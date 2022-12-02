# Copyright 2022 Facebook, Inc.

# You are hereby granted a non-exclusive, worldwide, royalty-free license to
# use, copy, modify, and distribute this software in source code or binary
# form for use in connection with the web services and APIs provided by
# Facebook.

# As with any software that integrates with the Facebook platform, your use
# of this software is subject to the Facebook Developer Principles and
# Policies [http://developers.facebook.com/policy/]. This copyright notice
# shall be included in all copies or substantial portions of the software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


#Copyright (c) Facebook, Inc. and its affiliates.
#All rights reserved.

#This source code is licensed under the license found in the
#LICENSE file in the root directory of this source tree.

#------------------------START Module_09_Video_Views_InStream_StandAlone----------------------------#

#--------------------------------------START INPUT SECTION----------------------------------------#

# Import Python libraries
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.targetingsearch import TargetingSearch
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adaccount import AdAccount
from time import time
from time import sleep
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import numpy as np
import json
import requests
from scipy.interpolate import interp1d

#---------------------------------------------INPUT 01----------------------------------------------#
# Include your own access token instead of xxxxxx
access_token = 'xxxxxx'

# Make sure you are using the latest API version
# You can double check on: https://developers.facebook.com/docs/graph-api/guides/versioning
api_version = 'v15.0'

# Initiate the Facebook Business API with the access token
api = FacebookAdsApi.init(
    access_token = access_token,
    api_version = api_version,
)

# Set the Ad Account on which you want to have the predictions. Replace the xxxxxx with your own Account ID
ad_account_id = 'act_xxxxxx'

# Write the directory where you want to save all the OUTPUTS
save_directory = 'C:/Users/username/Desktop/' # this is just an example on PC


#---------------------------------------------INPUT 02----------------------------------------------#

# Input all the campaign specs for your prediction
# Input the minimum and maximum ages
# In Meta Ads Platforms, minimum available is 13 years old and maximum is 65, which stands for people 65+ years old
age_min = 18
age_max = 65 

# Input the genders in a list. 2-for female, 1-for male
gender_list = [1,2]

# Input the country for the ads delivery
# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web
countries = ['MX'] 

# Define the amount of days for your Campaign predictions
camp_days = 28 # The maximum days that the prediction can be done is 90 within a 6 months window from now

# Frequency caps
# Needs the maximum number of times your ad will be shown to a person during a specifyed time period
# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days
frequency_cap = 2
every_x_days = 7

# When using interest-behavior based audiences, make sure that you have already saved the audience in the 
# same AdAccount in Ads Manager you are using for the Reach&Frequency predictions
# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction
# ONLY for interests or behaviors audience
# If you ARE NOT using interests/behaviors, leave audience_name = 'None'
audience_name = 'None'

# Days before the campaign begins
# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on
# Minimum and default value is 1
days_prior_start = 1

#--------------------------------------END INPUT SECTION----------------------------------------#

#-------------------------------------START REACH AND FREQUENCY PREDICTIONS---------------------#

# Initiatie the API call on the defined Ad Account
ad_account = AdAccount(
    fbid = ad_account_id,
    api = api,
)

# This section fetches targeting specs when working with Interest-behavior based audiences

if audience_name == 'None':
    inc_inter_behav = []
    exc_inter_behav = []
    exc_inter_behav_str = []

else:    
    fields_audiences = [
        'name',
        'targeting',
        ]
    
    saved_audiences = AdAccount(ad_account_id).get_saved_audiences(
        fields = fields_audiences
        )
    
    df_saved_audiences = pd.DataFrame(saved_audiences)

       
    # Filter by name, only the audience you included in the input section
    audiences_list = [audience_name] 

    df_saved_audiences_filter = df_saved_audiences[df_saved_audiences['name'].isin(audiences_list)].reset_index( drop = True)

    try:
        # Save the interests and behavior specs to be INCLUDED in a list
        inc_inter_behav = df_saved_audiences_filter['targeting'][0]['flexible_spec']
    except:
        # Save the interests and behavior specs to be INCLUDED in a list
        inc_inter_behav = []

    try:
        # Save the interests and behavior specs to be EXCLUDED in a list
        exc_inter_behav = df_saved_audiences_filter['targeting'][0]['exclusions']
        
    except:
        # Save the interests and behavior specs to be EXCLUDED in a list
        exc_inter_behav = []

# Make a call to the Ad Account to know the currency it is configured
# Depending on this, predictions will be displayed in cents or not

# More information about Currencies
# https://developers.facebook.com/docs/marketing-api/currencies

# Define fields for currency info
fields_01 = [
    'currency',
    'account_id',
    'name',    
]

# Make the currency call to the AdAccount
account_info = AdAccount(ad_account_id).api_get(
    fields = fields_01,

    )

# Save the information in separated variables
acc_currency = account_info['currency']
acc_id = account_info['account_id']
acc_name = account_info['name']

# Almost all country currencies are in cents, except for: 
# Chilean Peso, Colombian Peso, Costa Rican Colon, Hungarian Forint, Iceland Krona,
# Indonesian Rupiah, Japanese Yen, Korean Won, Paraguayan Guarani, Taiwan Dollar and Vietnamese Dong
# For additional information visit: https://developers.facebook.com/docs/marketing-api/currencies
# Transform the currency your AdAccount is set up, if it is in cents, it will tranform to whole currency units
 # If it is in whole units, it will keep the same

if (acc_currency in ['CLP', 'COP', 'CRC', 'HUF', 'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']):
    
    divisor = 1
else:
    
    divisor = 100

# Fetch today's date to make a call for different timeframes until finds ads where FanPage and Instagram
# within the AdAccount ID can be fetched
# This is needed to avoid passing rate limits

# Last day for fetching insights is always 'today'
until_date = datetime.now()

# First try will begin fetching ads from past 7 days. If no information is fetched, will try adding more days
init_days = 7

# Define an empty dataframe where insights will be stored
df_insights = pd.DataFrame()

# Condition will be satisfyed once df_insights is not empty and ads can be fetched
while df_insights.empty:
    try:
        # Convert init_days to timedelta
        days = timedelta(init_days)
        since_date = until_date - days

        # Dates must be in string format 'YYYY-MM-DD'
        since_date_str = str(since_date)[0:10]
        until_date_str = str(until_date)[0:10]

        # Make a call to fetch a subset of adsets to match the AdAccount to the Facebook Page and Instagram Account
        fields = [
            'ad_id',
            ]
        
        params = {
            'level': 'ad', # different levels are: account, campaign, adset and ad
            'time_range': {'since':since_date_str,'until':until_date_str}, 
            }

        insights = AdAccount(ad_account_id).get_insights(
            fields = fields,
            params = params,
            )

        df_insights = pd.DataFrame.from_dict(insights)

    except:
         pass

    # Add more days while df_insights is empty
    init_days = init_days + 7
    

# Get adcreatives and tacking specs to fetch IG Account and FB Page IDs respectively
df_adcreatives = pd.DataFrame()
df_ads_pages = pd.DataFrame()

# Define fields for adcreatives call
fields_tracking = [
    'adcreatives',
    'tracking_specs',
]

# Make the API call to the Ad
count_01 = 0
for ad in df_insights['ad_id']:
    ads_specs = Ad(ad).api_get(
        fields = fields_tracking
        )
    
    df_adcreatives.loc[count_01, 'adcreative_id'] = ads_specs['adcreatives']['data'][0]['id']
    
    count_02 = 0
    for spec in ads_specs['tracking_specs']:
        a = str(spec)
        if 'page' in a:
            idx = count_02
            
            df_ads_pages.loc[count_01, 'page_id'] = ads_specs['tracking_specs'][count_02]['page'][0]
            
        count_02 = count_02 + 1
    
    count_01 = count_01 + 1

# For making predictions, it is only needed one Facebook page ID and one Instagram ID related to the AdAccount
# It can be used any of the previous Page ID and Instagram ID from the previous calls
# WHEN USING VIDEO VIEWS IN STREAM STAND ALONE, IT'S ONLY NEEDED THE FACEBOOK PAGE ID
fb_ig_ids = [int(df_ads_pages.loc[0, 'page_id'])] 

# IMPORTANT: This code only works if you ARE ABOUT TO CONSIDER ONE OF THE FOLLOWING OBJETIVES
# FOR YOUR CAMPAIGN: REACH, BRAND_AWARENESS, VIDEO_VIEWS, POST_ENGAGEMENT or LINK_CLICKS (TRAFFIC)

# Define the list of objectives availables for this module.
# These 5 objectives are used because of the approach of OptiMate for Branding campaigns (upper-mid funnel objectives)
objectives_list = ['VIDEO_VIEWS']

# Create a variable that contains the amount of seconds for one day. This will be used in the Campaign Dates
secs_per_day = 60 * 60 * 24

# Transform the days before the campaign starts to secs
days_prior_start_sec = days_prior_start * secs_per_day

# Compute the Unix time for 'now'. This will be used on dates
now_time = int(time())

# Create a DataFrame and a list that will be used to append and store data from the predictions
append_clean_df = pd.DataFrame()
lst_min_budgets = []
lst_max_budgets = []

# IMPORTANT: WE RECOMMEND NOT TO CHANGE expected_reach PARAMETER. PREDICTION STILL WILL PROVIDE VALUES FOR DIFFERENT BUDGETS AND REACH LEVELS
# If need to change, it must be >200000 as this is a requirement to have Reach and Frequency predictions on this same Buying type
expected_reach = 200000 # Integer. Recommended to leave fixed on 200000 

# Create an emty data frame to save estimated audience sizes for each objective
df_audience_size = pd.DataFrame()

# Define a counter
count = 0

# Create a for loop to make calls on each objective, as each one of them has specific placement specs to work on
for objective in objectives_list:
        
    # Case when running VIDEO_VIEWS objective        
    if objective == 'VIDEO_VIEWS':
        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': frequency_cap,
                'interval_frequency_cap_reset_period': (every_x_days * 24),
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, no needed when using 'prediction_mode': 0
                'reach': expected_reach,
                'destination_ids': fb_ig_ids, 
                'target_spec': {
                    'age_min': age_min, # mininum age in years
                    'age_max': age_max, # maximum age in years
                    'genders': gender_list, # 2-for female, 1-for male
                    'geo_locations': {
                        'countries': countries,
                    },

                    'flexible_spec': inc_inter_behav,
                    'exclusions': exc_inter_behav,
                    #IMPORTANT: DO NOT ACTIVATE THIS SECTION IF YOU ALREADY DEFINED AN 'audience_name'
                    # IN THE INPUT SECTION OR IF YOU ARE NOT INTERESTED IN USING INTEREST-BASED AUDIENCES
                    # When using Interest based Audiences, you need to specify the ID
                    # For fetching the right Interest ID, you can use the Targeting Search Library
                    #'flexible_spec': [
                    #    {
                    #        # IMPORTANT: all the interests and behaviors you include within the
                    #        # same [brackets] works as an OR condition. If you want to apply an AND condition
                    #        # then open new curly brackets
                    #        'interests': [
                    #            6003349442621, # Entertainment
                    #            6004160395895, # Travel,
                    #            ],
                    #        'behaviors': [
                    #            6071631541183, # Engaged shoppers
                    #            ], 
                    #        },
                    #    
                    #    # Interests for AND condition
                    #    {
                    #        'interests': [
                    #            6003348604581, # Fashion accessories
                    #            ],
                    #        
                    #        'behaviors': [
                    #            6203619619383, # Friends of Soccer fans
                    #            ],
                    #        },
                    #    ],


                    #'exclusions': {
                    #    'interests': [
                    #        6003195797498, # Cuisine
                    #        6003409043877, # Alcoholic beverages
                    #        ],

                    #    'behaviors': [
                    #            6203619619383, # Friends of Soccer fans
                    #            ],
                    #    },
                    
                    # IMPORTANT: For VIDEO_VIEWS, 'audience_network' cannot be used as the only platform,
                    # it needs to be used with at least facebook-feed OR instagram-stream
                    'publisher_platforms': [
                        'facebook',
                        #'instagram',
                        #'audience_network', 
                    ],

                    'facebook_positions': [
                        #'feed',
                        #'instant_article',
                        #'marketplace',
                        #'video_feeds',
                        #'story',
                        'instream_video',
                    ],

                    #'instagram_positions': [
                    #    'stream',
                    #    'story',
                    #    'explore',
                    #    'reels',
                    #],

                    #'audience_network_positions': [
                    #    'classic',
                    #    'instream_video',
                    #],

                    'device_platforms': [
                        'mobile',
                        'desktop',
                    ],
                },
            },
        )

        # Once the call is made, we need to create a function to identify when the prediction call has ended
        def prediction_complete(prediction):
            prediction.api_get(
                fields=[
                    'status',
                    'prediction_progress',
                ],
            )

            return prediction['prediction_progress'] == 100 and prediction['status'] == 1

        # Function in case the predictions fails
        def prediction_fails(prediction):
            prediction.api_get(
                fields=[
                    'status',
                    'prediction_progress',
                ],
            )

            return prediction['status'] not in (1, 2, )

        # Up to 10 trials to attempt the call. Iif not, an error message is shown
        trials = 10
        while not prediction_complete(prediction):
            trials -= 1

            if not trials:
                raise SystemError('The prediction did not end on time.')

            if prediction_fails(prediction):
                raise SystemError('The prediction failed')

            sleep(10)

        # When the prediction is complete, fetch the fields we need to plot the curves
        results = prediction.api_get(
            fields=[
                'curve_budget_reach',
                'placement_breakdown',
                'external_budget',
                'external_reach',
                'external_impression',
                'audience_size_upper_bound',
                'audience_size_lower_bound',
            ],
        )
        
        # A prediction ID is needed to get the data on the API call
        prediction_id = results['id']

        # Call the API on the requested prediction_id
        response = requests.get(
            'https://graph.facebook.com/' + api_version + '/%s/' % str(prediction_id), # It's needed to upgrade the API version to the most recent one
            params={
                "fields": "curve_budget_reach",
                "access_token": access_token,
            },
        )

        # Create the JSON data to a DataFrame
        df = pd.DataFrame(
            data = response.json()['curve_budget_reach'],
        )

        # Keep main metrics
        clean_df = df[['budget', 'impression', 'reach']]

        # Create some other fields that are relevant when analzing curves data
        clean_df['budget'] = clean_df.budget / divisor 
        clean_df['included_interests'] = str(inc_inter_behav)
        clean_df['excluded_interests'] = str(exc_inter_behav_str)

        
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (camp_days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = objective
        clean_df['audience_name'] = audience_name
        lst_min_budgets.append(clean_df.loc[0, 'budget'])
        lst_max_budgets.append(clean_df.loc[(len(clean_df['budget'])-1), 'budget'])
        
    # Append predictions from each objective
    append_clean_df = append_clean_df.append(clean_df)
    
    # Save audience size to compute reach in %
    df_audience_size.loc[count, 'objective'] = objective
    df_audience_size.loc[count, 'audience_size_lower_bound'] = int(prediction['audience_size_lower_bound'])
    df_audience_size.loc[count, 'audience_size_upper_bound'] = int(prediction['audience_size_upper_bound'])
    
    count = count + 1
    
        
append_clean_df = append_clean_df.reset_index(drop = True)
        
#------------------- COMPUTATION FOR INTERPOLATION--------------------#

# Define a minimum budget to have all the curves comparison
min_budget = np.ceil(
    max(lst_min_budgets)
    )

# Define a maximum budget to have all the curves comparison
max_budget = np.floor(
    max(append_clean_df['budget']
        )
    )

# The size of the list to interpolate all values between min_budget and max_budget. 
# It's recommended to leave 1000 as default
n_steps = 1000

# Compute the increment size given n_steps
currency_incr = (max_budget - min_budget) / n_steps

# Create the dataframe where the standardized data will be stored
df_all_curves = pd.DataFrame()

# Create a list with the cummulative budgets for all objectives
# starting with the min_budget
lst_standard_budgets = []

# All curves will begin from the same minimum budget to have cross comparisons
cum_budget = min_budget

# Create the budget standardized field with the currency increments we have defined previously
for i in range(0, n_steps):        
        # Append cumulative budget values to the list
        lst_standard_budgets.append(cum_budget)
        
        # Add the currency_incr value to create new cumulative budgets
        cum_budget = cum_budget + currency_incr
        
# Create the dataframe where the standardized data will be stored
df_all_curves = pd.DataFrame()

# Define a temporary dataframe for each objective
temp_df = pd.DataFrame()

# Define a temporary dataframe for storing inteporlated values
temp_itp = pd.DataFrame()

# Apply the interpolation function depending on each objective

for itp_obj in append_clean_df['objective'].unique():
    
    # Filter data frame for each objective and store it temporary in temp_df
    temp_df = append_clean_df[append_clean_df['objective'] == itp_obj].reset_index(drop = True)
    
    # Create an array (for independent variable) with the budget levels for each objective
    x_budget = temp_df['budget'].to_numpy()

    # Create arrays (for dependent variables) with predicted metrics for each budget level
    y_reach = temp_df['reach'].to_numpy()
    y_impression = temp_df['impression'].to_numpy()
    
    # Create the function to interpolate data for each metric
    f_reach = interp1d(x_budget, y_reach, fill_value = float('nan'), bounds_error = False)
    f_impression = interp1d(x_budget, y_impression, fill_value = float('nan'), bounds_error = False)
    
    # Add interpolated values to the temp_itp data frame
    temp_itp['budget'] = pd.Series(lst_standard_budgets)
    temp_itp['reach'] = pd.Series(f_reach(lst_standard_budgets))
    temp_itp['impression'] = pd.Series(f_impression(lst_standard_budgets))
    temp_itp['objective'] = itp_obj
                                       
    # Append interpolated data into the new data frame
    df_all_curves = df_all_curves.append(temp_itp)
    
    print(itp_obj)
                  
# Reser index for the data frame
df_all_curves = df_all_curves.reset_index(drop = True)
    

# Add additional variables that are transformations of budget, reach and impressions

df_all_curves['frequency'] = df_all_curves['impression'] / df_all_curves['reach']
df_all_curves['weekly_frequency'] = df_all_curves['frequency'] / (camp_days/7)
df_all_curves['cpm'] = (df_all_curves['budget'] / df_all_curves['impression'])*1000

# Merge both data frames to compute reach in terms of percentage for upper and lower bounds
df_all_curves = pd.merge(df_all_curves, df_audience_size, on = 'objective')

# Computing percentage of reached people according to audience size per objective
df_all_curves['audience_pct_lower_bound'] = df_all_curves['reach'] / df_all_curves['audience_size_upper_bound']
df_all_curves['audience_pct_upper_bound'] = df_all_curves['reach'] / df_all_curves['audience_size_lower_bound']

# Reshape the dataframe to un-stack it
pivot_interpolated = df_all_curves.pivot(index = 'budget', columns = 'objective').reset_index('budget')

# Merge the column names after the pivoting
pivot_interpolated.columns = ['_'.join((j, k)) for j, k in pivot_interpolated]

# Save the predictions data in the save_directory
export_csv = pivot_interpolated.to_csv(r'' + save_directory + '09_Video_Views_InStream_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.csv', header=True, index = None)

# Select a style for the charts
%matplotlib inline
plt.style.use('seaborn-whitegrid')

# Plot the Reach and Frequency Curves for Reach (people)
fig, ax = plt.subplots()
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_VIDEO_VIEWS']/1000000, label = 'Video Views: InStream Video', color = '#fb8072')
leg = ax.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Reach (Millions)')
plt.title('Video Views InStream Stand Alone \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '09_Reach_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Total frequency
fig, bx = plt.subplots()
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_VIDEO_VIEWS'], label = 'Video Views: InStream Video', color = '#fb8072')
leg = bx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Total frequency')
plt.title('Video Views InStream Stand Alone \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '09_Total_frequency_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Cost Per Mille (CPM)
fig, cx = plt.subplots()
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_VIDEO_VIEWS'], label = 'Video Views: InStream Video', color = '#fb8072')
leg = cx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('CPM (' + str(acc_currency) + ')')
plt.title('Video Views InStream Stand Alone \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '09_CPM_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Weekly frequency
fig, dx = plt.subplots()
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_frequency_VIDEO_VIEWS'], label = 'Video Views: InStream Video', color = '#fb8072')
leg = dx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Weekly frequency')
plt.title('Video Views InStream Stand Alone \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '09_Weekly_frequency_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Weekly frequency
fig, ex = plt.subplots()
ex.plot(pivot_interpolated['budget_']/1000, (pivot_interpolated['audience_pct_lower_bound_VIDEO_VIEWS'] * 100), label = 'Video Views: InStream Video', color = '#fb8072')
leg = ex.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Lower Bound Reach % On-target')
plt.title('Video Views InStream Stand Alone \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '09_Lower_Bound_Reach_PCT_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Weekly frequency
fig, fx = plt.subplots()
fx.plot(pivot_interpolated['budget_']/1000, (pivot_interpolated['audience_pct_upper_bound_VIDEO_VIEWS'] * 100), label = 'Video Views: InStream Video', color = '#fb8072')
leg = fx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Upper Bound Reach % On-target')
plt.title('Video Views InStream Stand Alone \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '09_Upper_Bound_Reach_PCT_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

#----------------------------------END REACH AND FREQUENCY PREDICTIONS--------------------------------#

# Additional resources on

# Reach & Frequency Fields: https://developers.facebook.com/docs/marketing-api/reference/reach-frequency-prediction
# Currencies: https://developers.facebook.com/docs/marketing-api/currencies
# https://www.facebook.com/business/help/902459833240201?id=241532349736982

# Platforms that cannot work with the following objectives

# Audience Network cannot work with:
# 1. LINK_CLICKS
# 2. CONVERSIONS

# Messenger can't work with Reach & Frequency objectives