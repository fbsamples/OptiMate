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



# Import libraries
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.targetingsearch import TargetingSearch
from time import time
from time import sleep
import pandas as pd
import numpy as np
import json
import requests
from datetime import datetime, timedelta
from time import sleep
import plotly.graph_objects as go


#---------------------------------------START INPUT SECTION-----------------------------------------#



#---------------------------------------------INPUT 01----------------------------------------------#

# Include your own access token instead of xxxxxx
access_token = 'xxxxxx'
api = FacebookAdsApi.init(
    access_token = access_token,
)


# Set the Ad Account on which you want to have the predictions. Replace the xxxxxx with your own Account ID
ad_account_id = 'act_xxxxxxx'


# Initiatie the API call on the defined Ad Account
ad_account = AdAccount(
    fbid = ad_account_id,
    api = api,
)

# Choose an index to be added to your CSV output files
ad_account_index = '01'

# Choose a name to be added to your CSV output files
advertiser_name = 'xxx'

# Write the directory where you want to save all the OUTPUTS
save_directory = 'C:/Users/username/Desktop/' # this is just an example on PC

# Make sure you are using the latest API version
# You can double check on: https://developers.facebook.com/docs/graph-api/guides/versioning
api_version = 'v14.0'


# Define the audience you want to have the predictions on

# Budget in whole units, not cents and using the same currency your ad account is configured
# This will be your reference budget set as your business as usual
budget = 350000

# Input the country for the ads delivery
# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web
countries = [['MX']]

# Input all the campaing specs for your prediction
# Input the minimum and maximum ages

ages = [[18,65]]

# Input the genders. 2-for female, 1-for male
gender_list = [[1,2]]

# IMPORTANT: WE RECOMMEND NOT TO CHANGE expected_reacg PARAMETER. PREDICTION STILL WILL PROVIDE VALUES FOR DIFFERENT BUDGETS AND REACH LEVELS
# If need to change, it must be >200000 as this is a requirement to have Reach and Frequency predictions on this same Buying type
expected_reach = 200000 # Integer. Recommended to leave fixed on 200000 

# When using interest-behavior based audiences, make sure that you have already save the audience in the 
# same AdAccount in Ads Manager you are using for the Reach&Frequency predictions
# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction
# ONLY for interests or behaviors audience
# If you ARE NOT using interests, leave audience_name = 'None'
audience_name = 'None' # Add your own Audience name

# This example covers different days, frequency caps and objectives combinations
# Furthermore, it can be customized according to your needs
# Just keep in mind that the combinations of all parameters does not exceed around 70-80 calls per hour
# Otherwise rate limits will show an error
# IF more than 70-80 combinations are needed, you can use a time.sleep()

# Define the amount of days for your Campaign predictions
camp_days = [28] 

# Set different objectives to siulate
# Different objectives are: 'BRAND_AWARENESS', 'REACH', 'LINK_CLICKS', 'POST_ENGAGEMENT' AND 'VIDEO_VIEWS'
camp_objectives = [
    'REACH',
    'BRAND_AWARENESS',
    'LINK_CLICKS',
    'POST_ENGAGEMENT',
    'VIDEO_VIEWS',
]

# Frequency caps
# Needs the maximum number of times your ad will be shown to a person during a specifyed time period
# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days
maximum_caps = [2]
every_x_days = 7

# Days before the campaign begins
# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on
# Minimum and default value is 1
days_prior_start = 7



#----------------------------------------END INPUT SECTION--------------------------------------#



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

       
    # Filter by name only the audience you included in the input section
    audiences_list = [audience_name] # SET YOUR OWN AUDIENCE NAME

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

    
# Make a call to the Ad Account to know the currency it is set up,
# Depending on this, the predictions will be in cents or not

# More information about Currencies
# https://developers.facebook.com/docs/marketing-api/currencies

fields_01 = [
    'currency',
    'account_id',
    'name',    
]


account_info = AdAccount(ad_account_id).api_get(
    fields = fields_01,

    )

acc_currency = account_info['currency']
acc_id = account_info['account_id']
acc_name = account_info['name']

# Almost all country currencies are in cents, except for: 
# Chilean Peso, Colombian Peso, Costa Rican Colon, Hungarian Forint, Iceland Krona,
# Indonesian Rupiah, Japanese Yen, Korean Won, Paraguayan Guarani, Taiwan Dollar and Vietnamese Dong
# For additional information visit: https://developers.facebook.com/docs/marketing-api/currencies
# Transform the currency your account is set up, if it is in cents, it will tranform to whole currency units
 # If it is in whole units, it will keep the same

if (acc_currency in ['CLP', 'COP', 'CRC', 'HUF', 'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']):
    
    divider = 1
else:
    
    divider = 100


# Fetch today's date to make a call for different timeframes until finds ads where FanPage and Instagram
# Account ID can be fetched
# This is needed to avoid passing the rate limit

# Last day for fetching insights is always 'today'
until_date = datetime.now()

# First try will begin fetching ads from past 7 days. If no information is fetched, will try adding more days
init_days = 7

# Define an empty dataframe where insights will be stored
df_insights = pd.DataFrame()
# Condition will be satistyed once df_insights is not empty and ads can be fetched
while df_insights.empty:
    try:
        # Convert init_days to timedelta
        days = timedelta(init_days)
        since_date = until_date - days

        # Dates must be in string format YYYY-MM-DD
        since_date_str = str(since_date)[0:10]
        until_date_str = str(until_date)[0:10]

        # Make a call to fetch a subset of adsets to match the Account to the Facebook Page and Instagram Account

        fields = [
            'ad_id',
        ]

        params = {
            'level': 'ad', # different levels are: account, campaign, adset and ad
            'time_range': {'since':since_date_str,'until':until_date_str}, 
            }

        insights = AdAccount(ad_account_id).get_insights(
            fields=fields,
            params=params,
            )

        df_insights = pd.DataFrame.from_dict(insights)

    except:
         pass

    # Add more days while df_insights is empty
    init_days = init_days + 7
    

print(df_insights)


# Get adcreatives and tacking specs to fetch IG Account and FB Page IDs respectively

df_adcreatives = pd.DataFrame()
df_ads_pages = pd.DataFrame()

fields_tracking = [
    'adcreatives',
    'tracking_specs',
]

count_01 = 0
for ad in df_insights['ad_id']:
    ads_specs = Ad(ad).api_get(
    fields = fields_tracking)
    
    df_adcreatives.loc[count_01, 'adcreative_id'] = ads_specs['adcreatives']['data'][0]['id']
    
    count_02 = 0
    for spec in ads_specs['tracking_specs']:
        a = str(spec)
        if 'page' in a:
            idx = count_02
            
            df_ads_pages.loc[count_01, 'page_id'] = ads_specs['tracking_specs'][count_02]['page'][0]
            
        count_02 = count_02 + 1
        
    
    
    
    count_01 = count_01 + 1


print(df_adcreatives)


print(df_ads_pages)


# Create a dataframe to store the Instagram IDs for the Account
df_creative_ig = pd.DataFrame()


# Define the Instagram fields that is needed for the prediction
fields_creatives = [
    'instagram_user_id',
]

# Loop on all the adcreatives during the past 3 months
count_03 = 0
for creative in df_adcreatives['adcreative_id']:
    creative_ig = AdCreative(creative).api_get(
    fields = fields_creatives)
    
    try: 
        df_creative_ig.loc[count_03, 'instagram_id'] = creative_ig['instagram_user_id']
    except: 
        df_creative_ig.loc[count_03, 'instagram_id'] = float('nan')
    
    count_03 = count_03 + 1
    
# Remove rows with NaNs
df_creative_ig = df_creative_ig.dropna()

# Reset index
df_creative_ig = df_creative_ig.reset_index(drop = True)
    
# For making the predictions, it is only needed one Facebook page ID and one Instagram ID related to the Ad Account
# It can be used any of the previous Page ID and Instagram ID from the previous calls
fb_ig_ids = [int(df_ads_pages.loc[0, 'page_id']), int(df_creative_ig.loc[0, 'instagram_id'])] 


print(df_creative_ig)


# Define the closest match function

def closest(lst, budget): 
      
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-budget))] 


######------------------ESTIMATING REACH & FREQUENCY CURVES SIMULATIONS------------------#####

# We define this constant to compute the number of days each campaign should last
secs_per_day = 60 * 60 * 24

# Transform the days before the campaign starts to secs

days_prior_start_sec = days_prior_start * secs_per_day

df_append_sim = pd.DataFrame()

count = 0
now_time = int(time())

for country in countries:

    for gender in gender_list:

        for age in ages:

            for objective in camp_objectives:

                for frequency_cap in maximum_caps:

                    for days in camp_days:

                        df_append_sim.loc[count, 'budget'] = budget
                        df_append_sim.loc[count, 'country'] = country
                        df_append_sim.loc[count, 'gender'] = ' '.join([str(elem) for elem in gender])
                        df_append_sim.loc[count, 'age_min'] = age[0]
                        df_append_sim.loc[count, 'age_max'] = age[1]
                        df_append_sim.loc[count, 'days'] = days
                        df_append_sim.loc[count, 'frequency_cap'] = str(frequency_cap) + ' times every ' + str(every_x_days) + ' days'
                        df_append_sim.loc[count, 'objective'] = objective
                        df_append_sim.loc[count, 'included_interests'] = str(inc_inter_behav)
                        df_append_sim.loc[count, 'excluded_interests'] = str(exc_inter_behav)


                        # Convert campaign days duration to weeks
                        weeks = days / 7


                        # Case when running POST_ENGAGEMENT, as this objective has restrictions on some placements
                        if objective == 'POST_ENGAGEMENT':


                            prediction = ad_account.create_reach_frequency_prediction(
                                params={
                                    'start_time': (now_time) + days_prior_start_sec,
                                    'end_time': min((now_time + days_prior_start_sec + (days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                                    'objective': objective, # set the campaign objective
                                    'frequency_cap': frequency_cap,
                                    'interval_frequency_cap_reset_period': (every_x_days * 24),
                                    'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                                    #'budget': budget, 
                                    'reach': expected_reach,
                                    'destination_ids': fb_ig_ids, 
                                    'target_spec': {
                                        'age_min': age[0], # mininum age in years
                                        'age_max': age[1], # maximum age in years
                                        'genders': gender, # 2-for female, 1-for male
                                        'geo_locations': {
                                            'countries': country,
                                        },

                                        'flexible_spec': inc_inter_behav,
                                        'exclusions': exc_inter_behav,

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

                                        'publisher_platforms': [
                                            'facebook',
                                            'instagram',
                                            'audience_network',

                                        ],

                                        'facebook_positions': [
                                            'feed',
                                            'instant_article',
                                            'marketplace',
                                            'video_feeds',
                                            'story',
                                            'instream_video',

                                        ],

                                        'instagram_positions': [
                                            'stream',
                                            'story',
                                            'explore',
                                            'reels',
                                        ],

                                        'audience_network_positions': [
                                            'classic',
                                            'instream_video',
                                        ],

                                        'device_platforms': [
                                            'mobile',
                                            'desktop',
                                        ],
                                    },
                                },
                            )

                        # Case when running LINK_CLICKS, as this objective has restrictions on some placements

                        elif objective == 'LINK_CLICKS': 

                            prediction = ad_account.create_reach_frequency_prediction(
                                params={
                                    'start_time': (now_time) + days_prior_start_sec,
                                    'end_time': min((now_time + days_prior_start_sec + (days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                                    'objective': objective, # set the campaign objective
                                    'frequency_cap': frequency_cap,
                                    'interval_frequency_cap_reset_period': (every_x_days * 24),
                                    'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                                    #'budget': budget, 
                                    'reach': expected_reach,
                                    'destination_ids': fb_ig_ids, 
                                    'target_spec': {
                                        'age_min': age[0], # mininum age in years
                                        'age_max': age[1], # maximum age in years
                                        'genders': gender, # 2-for female, 1-for male
                                        'geo_locations': {
                                            'countries': country,
                                        },

                                        'flexible_spec': inc_inter_behav,
                                        'exclusions': exc_inter_behav,

                                        'publisher_platforms': [
                                            'facebook',
                                            'instagram',
                                            #'audience_network',

                                        ],

                                        'facebook_positions': [
                                            'feed',
                                            'instant_article',
                                            'marketplace',
                                            'video_feeds',
                                            'story',
                                            'instream_video',

                                        ],

                                        'instagram_positions': [
                                            'stream',
                                            'story',
                                            'explore',
                                            'reels',
                                        ],

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

                            # Case when running REACH objective


                        elif objective == 'REACH':

                            prediction = ad_account.create_reach_frequency_prediction(
                                params={
                                    'start_time': (now_time) + days_prior_start_sec,
                                    'end_time': min((now_time + days_prior_start_sec + (days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                                    'objective': objective, # set the campaign objective
                                    'frequency_cap': frequency_cap,
                                    'interval_frequency_cap_reset_period': (every_x_days * 24),
                                    'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                                    #'budget': budget, 
                                    'reach': expected_reach,
                                    'destination_ids': fb_ig_ids, 
                                    'target_spec': {
                                        'age_min': age[0], # mininum age in years
                                        'age_max': age[1], # maximum age in years
                                        'genders': gender, # 2-for female, 1-for male
                                        'geo_locations': {
                                            'countries': country,
                                        },

                                        'flexible_spec': inc_inter_behav,
                                        'exclusions': exc_inter_behav,

                                        'publisher_platforms': [
                                            'facebook',
                                            'instagram',
                                            'audience_network',

                                        ],

                                        'facebook_positions': [
                                            'feed',
                                            'instant_article',
                                            'marketplace',
                                            'video_feeds',
                                            'story',
                                            'instream_video',

                                        ],

                                        'instagram_positions': [
                                            'stream',
                                            'story',
                                            'explore',
                                            'reels',
                                        ],

                                        'audience_network_positions': [
                                            'classic',
                                            'instream_video',
                                        ],

                                        'device_platforms': [
                                            'mobile',
                                            'desktop',
                                        ],
                                    },
                                },
                            )

                        # Case when running BRAND_AWARENESS objective

                        elif objective == 'BRAND_AWARENESS':


                            prediction = ad_account.create_reach_frequency_prediction(
                                params={
                                    'start_time': (now_time) + days_prior_start_sec,
                                    'end_time': min((now_time + days_prior_start_sec + (days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                                    'objective': objective, # set the campaign objective
                                    'frequency_cap': frequency_cap,
                                    'interval_frequency_cap_reset_period': (every_x_days * 24),
                                    'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                                    #'budget': budget, 
                                    'reach': expected_reach,
                                    'destination_ids': fb_ig_ids, 
                                    'target_spec': {
                                        'age_min': age[0], # mininum age in years
                                        'age_max': age[1], # maximum age in years
                                        'genders': gender, # 2-for female, 1-for male
                                        'geo_locations': {
                                            'countries': country,
                                        },

                                        'flexible_spec': inc_inter_behav,
                                        'exclusions': exc_inter_behav,

                                        'publisher_platforms': [
                                            'facebook',
                                            'instagram',
                                            'audience_network',

                                        ],

                                        'facebook_positions': [
                                            'feed',
                                            'instant_article',
                                            'marketplace',
                                            'video_feeds',
                                            'story',
                                            'instream_video',

                                        ],

                                        'instagram_positions': [
                                            'stream',
                                            'story',
                                            'explore',
                                            'reels',
                                        ],

                                        'audience_network_positions': [
                                            'classic',
                                            'instream_video',
                                        ],


                                        'device_platforms': [
                                            'mobile',
                                            'desktop',
                                        ],
                                    },
                                },
                            )

                        # Case when running VIDEO_VIEWS objective

                        elif objective == 'VIDEO_VIEWS':

                            prediction = ad_account.create_reach_frequency_prediction(
                                params={
                                    'start_time': (now_time) + days_prior_start_sec,
                                    'end_time': min((now_time + days_prior_start_sec + (days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                                    'objective': objective, # set the campaign objective
                                    'frequency_cap': frequency_cap,
                                    'interval_frequency_cap_reset_period': (every_x_days * 24),
                                    'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                                    #'budget': budget, 
                                    'reach': expected_reach,
                                    'destination_ids': fb_ig_ids, 
                                    'target_spec': {
                                        'age_min': age[0], # mininum age in years
                                        'age_max': age[1], # maximum age in years
                                        'genders': gender, # 2-for female, 1-for male
                                        'geo_locations': {
                                            'countries': country,
                                        },

                                        'flexible_spec': inc_inter_behav,
                                        'exclusions': exc_inter_behav,

                                        'publisher_platforms': [
                                            'facebook',
                                            'instagram',
                                            'audience_network',

                                        ],

                                        'facebook_positions': [
                                            'feed',
                                            'instant_article',
                                            'marketplace',
                                            'video_feeds',
                                            'story',
                                            'instream_video',

                                        ],

                                        'instagram_positions': [
                                            'stream',
                                            'story',
                                            'explore',
                                            'reels',
                                        ],

                                        'audience_network_positions': [
                                            'classic',
                                            'instream_video',
                                        ],

                                        'device_platforms': [
                                            'mobile',
                                            'desktop',
                                        ],
                                    },
                                },
                            )

                        # Once the call is made, we need to create a function to identify when the prediction call has ended
                        prediction

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

                            sleep(20)

                        # When the prediction is complete, fetch the fields we need to plot the curves
                        results = prediction.api_get(
                            fields=[
                                'curve_budget_reach',
                                'placement_breakdown',
                                'external_budget',
                                'external_reach',
                                'external_impression',
                                'audience_size_lower_bound',
                                'audience_size_upper_bound',
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

                        # Convert the JSON data to a DataFrame
                        df = pd.DataFrame(
                            data = response.json()['curve_budget_reach'],
                        )



                        clean_df = df[['budget', 'impression', 'reach', 'conversion']]


                        clean_df['frequency'] = clean_df.impression / clean_df.reach
                        clean_df['budget'] = clean_df.budget / divider
                        clean_df['weekly_freq'] = clean_df.frequency / ((int(df_append_sim.at[count, 'days']))/7)
                        max_reach = clean_df['reach'].max()

                        # matching the real spent values to the budget, reach and frequency on the estimation
                        lst = clean_df['budget'].tolist()
                        #budget = budget


                        # Closest budget for BAU
                        closest_budget_bau = closest(lst, budget)

                        # Fetch two rows for interpolate the budget values

                        if budget > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_bau]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_bau = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_bau = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_bau >= budget:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_bau]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_bau = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_bau = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_bau]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_bau = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_bau = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_bau'] = closest_upper_row_bau.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_bau'] = closest_lower_row_bau.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_bau'] = closest_upper_row_bau.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_bau'] = closest_lower_row_bau.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_bau'] = closest_upper_row_bau.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_bau'] = closest_lower_row_bau.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_bau'] = closest_upper_row_bau.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_bau'] = closest_lower_row_bau.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_bau'] = closest_upper_row_bau.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_bau'] = closest_lower_row_bau.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_bau'] = closest_upper_row_bau.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_bau'] = closest_lower_row_bau.loc[0, 'weekly_freq']


                        #Interpolating values for BAU

                        df_append_sim.loc[count, 'rf_impression_bau_pred'] = (((closest_upper_row_bau.loc[0, 'impression'] - closest_lower_row_bau.loc[0, 'impression']) / (closest_upper_row_bau.loc[0, 'budget'] - closest_lower_row_bau.loc[0, 'budget'])) * (budget-closest_lower_row_bau.loc[0, 'budget'])) + closest_lower_row_bau.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_bau_pred'] = (((closest_upper_row_bau.loc[0, 'reach'] - closest_lower_row_bau.loc[0, 'reach']) / (closest_upper_row_bau.loc[0, 'budget'] - closest_lower_row_bau.loc[0, 'budget'])) * (budget-closest_lower_row_bau.loc[0, 'budget'])) + closest_lower_row_bau.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_bau_pred'] = (((closest_upper_row_bau.loc[0, 'conversion'] - closest_lower_row_bau.loc[0, 'conversion']) / (closest_upper_row_bau.loc[0, 'budget'] - closest_lower_row_bau.loc[0, 'budget'])) * (budget-closest_lower_row_bau.loc[0, 'budget'])) + closest_lower_row_bau.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_bau_pred'] = (((closest_upper_row_bau.loc[0, 'frequency'] - closest_lower_row_bau.loc[0, 'frequency']) / (closest_upper_row_bau.loc[0, 'budget'] - closest_lower_row_bau.loc[0, 'budget'])) * (budget-closest_lower_row_bau.loc[0, 'budget'])) + closest_lower_row_bau.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_bau_pred'] = (((closest_upper_row_bau.loc[0, 'weekly_freq'] - closest_lower_row_bau.loc[0, 'weekly_freq']) / (closest_upper_row_bau.loc[0, 'budget'] - closest_lower_row_bau.loc[0, 'budget'])) * (budget-closest_lower_row_bau.loc[0, 'budget'])) + closest_lower_row_bau.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_bau_pred'] = budget / df_append_sim.loc[count, 'rf_impression_bau_pred'] * 1000



                    ############------------------Simulations for +10 budget scenario------------------###################

                        budget_10 = df_append_sim.at[count, 'budget'] * 1.1
                        df_append_sim.loc[count, 'budget_10'] = budget_10


                        # Closest budget for +10 budget
                        closest_budget_10 = closest(lst, budget_10)

                        # Fetch two rows for interpolate the budget values

                        if budget_10 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_10]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_10 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_10 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_10 >= budget_10:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_10]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_10 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_10 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_10]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_10 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_10 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_10'] = closest_upper_row_10.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_10'] = closest_lower_row_10.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_10'] = closest_upper_row_10.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_10'] = closest_lower_row_10.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_10'] = closest_upper_row_10.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_10'] = closest_lower_row_10.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_10'] = closest_upper_row_10.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_10'] = closest_lower_row_10.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_10'] = closest_upper_row_10.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_10'] = closest_lower_row_10.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_10'] = closest_upper_row_10.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_10'] = closest_lower_row_10.loc[0, 'weekly_freq']


                        #Interpolating values for +10 budget

                        df_append_sim.loc[count, 'rf_impression_10_pred'] = (((closest_upper_row_10.loc[0, 'impression'] - closest_lower_row_10.loc[0, 'impression']) / (closest_upper_row_10.loc[0, 'budget'] - closest_lower_row_10.loc[0, 'budget'])) * (budget_10-closest_lower_row_10.loc[0, 'budget'])) + closest_lower_row_10.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_10_pred'] = (((closest_upper_row_10.loc[0, 'reach'] - closest_lower_row_10.loc[0, 'reach']) / (closest_upper_row_10.loc[0, 'budget'] - closest_lower_row_10.loc[0, 'budget'])) * (budget_10-closest_lower_row_10.loc[0, 'budget'])) + closest_lower_row_10.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_10_pred'] = (((closest_upper_row_10.loc[0, 'conversion'] - closest_lower_row_10.loc[0, 'conversion']) / (closest_upper_row_10.loc[0, 'budget'] - closest_lower_row_10.loc[0, 'budget'])) * (budget_10-closest_lower_row_10.loc[0, 'budget'])) + closest_lower_row_10.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_10_pred'] = (((closest_upper_row_10.loc[0, 'frequency'] - closest_lower_row_10.loc[0, 'frequency']) / (closest_upper_row_10.loc[0, 'budget'] - closest_lower_row_10.loc[0, 'budget'])) * (budget_10-closest_lower_row_10.loc[0, 'budget'])) + closest_lower_row_10.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_10_pred'] = (((closest_upper_row_10.loc[0, 'weekly_freq'] - closest_lower_row_10.loc[0, 'weekly_freq']) / (closest_upper_row_10.loc[0, 'budget'] - closest_lower_row_10.loc[0, 'budget'])) * (budget_10-closest_lower_row_10.loc[0, 'budget'])) + closest_lower_row_10.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_10_pred'] = budget_10 / df_append_sim.loc[count, 'rf_impression_10_pred'] * 1000


                        ############------------------Simulations for +_15 budget scenario------------------###################

                        budget_15 = df_append_sim.at[count, 'budget'] * 1.15
                        df_append_sim.loc[count, 'budget_15'] = budget_15


                        # Closest budget for +_15 budget
                        closest_budget_15 = closest(lst, budget_15)

                        # Fetch two rows for interpolate the budget values

                        if budget_15 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_15]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_15 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_15 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_15 >= budget_15:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_15]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_15 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_15 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_15]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_15 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_15 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_15'] = closest_upper_row_15.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_15'] = closest_lower_row_15.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_15'] = closest_upper_row_15.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_15'] = closest_lower_row_15.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_15'] = closest_upper_row_15.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_15'] = closest_lower_row_15.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_15'] = closest_upper_row_15.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_15'] = closest_lower_row_15.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_15'] = closest_upper_row_15.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_15'] = closest_lower_row_15.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_15'] = closest_upper_row_15.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_15'] = closest_lower_row_15.loc[0, 'weekly_freq']


                        #Interpolating values for +_15 budget

                        df_append_sim.loc[count, 'rf_impression_15_pred'] = (((closest_upper_row_15.loc[0, 'impression'] - closest_lower_row_15.loc[0, 'impression']) / (closest_upper_row_15.loc[0, 'budget'] - closest_lower_row_15.loc[0, 'budget'])) * (budget_15-closest_lower_row_15.loc[0, 'budget'])) + closest_lower_row_15.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_15_pred'] = (((closest_upper_row_15.loc[0, 'reach'] - closest_lower_row_15.loc[0, 'reach']) / (closest_upper_row_15.loc[0, 'budget'] - closest_lower_row_15.loc[0, 'budget'])) * (budget_15-closest_lower_row_15.loc[0, 'budget'])) + closest_lower_row_15.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_15_pred'] = (((closest_upper_row_15.loc[0, 'conversion'] - closest_lower_row_15.loc[0, 'conversion']) / (closest_upper_row_15.loc[0, 'budget'] - closest_lower_row_15.loc[0, 'budget'])) * (budget_15-closest_lower_row_15.loc[0, 'budget'])) + closest_lower_row_15.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_15_pred'] = (((closest_upper_row_15.loc[0, 'frequency'] - closest_lower_row_15.loc[0, 'frequency']) / (closest_upper_row_15.loc[0, 'budget'] - closest_lower_row_15.loc[0, 'budget'])) * (budget_15-closest_lower_row_15.loc[0, 'budget'])) + closest_lower_row_15.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_15_pred'] = (((closest_upper_row_15.loc[0, 'weekly_freq'] - closest_lower_row_15.loc[0, 'weekly_freq']) / (closest_upper_row_15.loc[0, 'budget'] - closest_lower_row_15.loc[0, 'budget'])) * (budget_15-closest_lower_row_15.loc[0, 'budget'])) + closest_lower_row_15.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_15_pred'] = budget_15 / df_append_sim.loc[count, 'rf_impression_15_pred'] * 1000


                        ############------------------Simulations for +20 budget scenario------------------###################

                        budget_20 = df_append_sim.at[count, 'budget'] * 1.2


                        # Closest budget for +20 budget
                        closest_budget_20 = closest(lst, budget_20)
                        df_append_sim.loc[count, 'budget_20'] = budget_20

                        # Fetch two rows for interpolate the budget values

                        if budget_20 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_20]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_20 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_20 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_20 >= budget_20:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_20]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_20 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_20 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_20]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_20 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_20 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_20'] = closest_upper_row_20.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_20'] = closest_lower_row_20.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_20'] = closest_upper_row_20.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_20'] = closest_lower_row_20.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_20'] = closest_upper_row_20.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_20'] = closest_lower_row_20.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_20'] = closest_upper_row_20.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_20'] = closest_lower_row_20.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_20'] = closest_upper_row_20.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_20'] = closest_lower_row_20.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_20'] = closest_upper_row_20.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_20'] = closest_lower_row_20.loc[0, 'weekly_freq']


                        #Interpolating values for +20 budget

                        df_append_sim.loc[count, 'rf_impression_20_pred'] = (((closest_upper_row_20.loc[0, 'impression'] - closest_lower_row_20.loc[0, 'impression']) / (closest_upper_row_20.loc[0, 'budget'] - closest_lower_row_20.loc[0, 'budget'])) * (budget_20-closest_lower_row_20.loc[0, 'budget'])) + closest_lower_row_20.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_20_pred'] = (((closest_upper_row_20.loc[0, 'reach'] - closest_lower_row_20.loc[0, 'reach']) / (closest_upper_row_20.loc[0, 'budget'] - closest_lower_row_20.loc[0, 'budget'])) * (budget_20-closest_lower_row_20.loc[0, 'budget'])) + closest_lower_row_20.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_20_pred'] = (((closest_upper_row_20.loc[0, 'conversion'] - closest_lower_row_20.loc[0, 'conversion']) / (closest_upper_row_20.loc[0, 'budget'] - closest_lower_row_20.loc[0, 'budget'])) * (budget_20-closest_lower_row_20.loc[0, 'budget'])) + closest_lower_row_20.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_20_pred'] = (((closest_upper_row_20.loc[0, 'frequency'] - closest_lower_row_20.loc[0, 'frequency']) / (closest_upper_row_20.loc[0, 'budget'] - closest_lower_row_20.loc[0, 'budget'])) * (budget_20-closest_lower_row_20.loc[0, 'budget'])) + closest_lower_row_20.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_20_pred'] = (((closest_upper_row_20.loc[0, 'weekly_freq'] - closest_lower_row_20.loc[0, 'weekly_freq']) / (closest_upper_row_20.loc[0, 'budget'] - closest_lower_row_20.loc[0, 'budget'])) * (budget_20-closest_lower_row_20.loc[0, 'budget'])) + closest_lower_row_20.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_20_pred'] = budget_20 / df_append_sim.loc[count, 'rf_impression_20_pred'] * 1000


                        ############------------------Simulations for +_25 budget scenario------------------###################

                        budget_25 = df_append_sim.at[count, 'budget'] * 1.25
                        df_append_sim.loc[count, 'budget_25'] = budget_25


                        # Closest budget for +_25 budget
                        closest_budget_25 = closest(lst, budget_25)

                        # Fetch two rows for interpolate the budget values

                        if budget_25 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_25]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_25 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_25 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_25 >= budget_25:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_25]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_25 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_25 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_25]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_25 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_25 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_25'] = closest_upper_row_25.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_25'] = closest_lower_row_25.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_25'] = closest_upper_row_25.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_25'] = closest_lower_row_25.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_25'] = closest_upper_row_25.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_25'] = closest_lower_row_25.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_25'] = closest_upper_row_25.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_25'] = closest_lower_row_25.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_25'] = closest_upper_row_25.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_25'] = closest_lower_row_25.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_25'] = closest_upper_row_25.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_25'] = closest_lower_row_25.loc[0, 'weekly_freq']


                        #Interpolating values for +_25 budget

                        df_append_sim.loc[count, 'rf_impression_25_pred'] = (((closest_upper_row_25.loc[0, 'impression'] - closest_lower_row_25.loc[0, 'impression']) / (closest_upper_row_25.loc[0, 'budget'] - closest_lower_row_25.loc[0, 'budget'])) * (budget_25-closest_lower_row_25.loc[0, 'budget'])) + closest_lower_row_25.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_25_pred'] = (((closest_upper_row_25.loc[0, 'reach'] - closest_lower_row_25.loc[0, 'reach']) / (closest_upper_row_25.loc[0, 'budget'] - closest_lower_row_25.loc[0, 'budget'])) * (budget_25-closest_lower_row_25.loc[0, 'budget'])) + closest_lower_row_25.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_25_pred'] = (((closest_upper_row_25.loc[0, 'conversion'] - closest_lower_row_25.loc[0, 'conversion']) / (closest_upper_row_25.loc[0, 'budget'] - closest_lower_row_25.loc[0, 'budget'])) * (budget_25-closest_lower_row_25.loc[0, 'budget'])) + closest_lower_row_25.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_25_pred'] = (((closest_upper_row_25.loc[0, 'frequency'] - closest_lower_row_25.loc[0, 'frequency']) / (closest_upper_row_25.loc[0, 'budget'] - closest_lower_row_25.loc[0, 'budget'])) * (budget_25-closest_lower_row_25.loc[0, 'budget'])) + closest_lower_row_25.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_25_pred'] = (((closest_upper_row_25.loc[0, 'weekly_freq'] - closest_lower_row_25.loc[0, 'weekly_freq']) / (closest_upper_row_25.loc[0, 'budget'] - closest_lower_row_25.loc[0, 'budget'])) * (budget_25-closest_lower_row_25.loc[0, 'budget'])) + closest_lower_row_25.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_25_pred'] = budget_25 / df_append_sim.loc[count, 'rf_impression_25_pred'] * 1000



                        ############------------------Simulations for +30 budget scenario------------------###################

                        budget_30 = df_append_sim.at[count, 'budget'] * 1.3


                        # Closest budget for +30 budget
                        closest_budget_30 = closest(lst, budget_30)
                        df_append_sim.loc[count, 'budget_30'] = budget_30

                        # Fetch two rows for interpolate the budget values

                        if budget_30 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_30]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_30 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_30 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_30 >= budget_30:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_30]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_30 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_30 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_30]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_30 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_30 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_30'] = closest_upper_row_30.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_30'] = closest_lower_row_30.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_30'] = closest_upper_row_30.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_30'] = closest_lower_row_30.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_30'] = closest_upper_row_30.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_30'] = closest_lower_row_30.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_30'] = closest_upper_row_30.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_30'] = closest_lower_row_30.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_30'] = closest_upper_row_30.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_30'] = closest_lower_row_30.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_30'] = closest_upper_row_30.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_30'] = closest_lower_row_30.loc[0, 'weekly_freq']


                        #Interpolating values for +30 budget

                        df_append_sim.loc[count, 'rf_impression_30_pred'] = (((closest_upper_row_30.loc[0, 'impression'] - closest_lower_row_30.loc[0, 'impression']) / (closest_upper_row_30.loc[0, 'budget'] - closest_lower_row_30.loc[0, 'budget'])) * (budget_30-closest_lower_row_30.loc[0, 'budget'])) + closest_lower_row_30.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_30_pred'] = (((closest_upper_row_30.loc[0, 'reach'] - closest_lower_row_30.loc[0, 'reach']) / (closest_upper_row_30.loc[0, 'budget'] - closest_lower_row_30.loc[0, 'budget'])) * (budget_30-closest_lower_row_30.loc[0, 'budget'])) + closest_lower_row_30.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_30_pred'] = (((closest_upper_row_30.loc[0, 'conversion'] - closest_lower_row_30.loc[0, 'conversion']) / (closest_upper_row_30.loc[0, 'budget'] - closest_lower_row_30.loc[0, 'budget'])) * (budget_30-closest_lower_row_30.loc[0, 'budget'])) + closest_lower_row_30.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_30_pred'] = (((closest_upper_row_30.loc[0, 'frequency'] - closest_lower_row_30.loc[0, 'frequency']) / (closest_upper_row_30.loc[0, 'budget'] - closest_lower_row_30.loc[0, 'budget'])) * (budget_30-closest_lower_row_30.loc[0, 'budget'])) + closest_lower_row_30.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_30_pred'] = (((closest_upper_row_30.loc[0, 'weekly_freq'] - closest_lower_row_30.loc[0, 'weekly_freq']) / (closest_upper_row_30.loc[0, 'budget'] - closest_lower_row_30.loc[0, 'budget'])) * (budget_30-closest_lower_row_30.loc[0, 'budget'])) + closest_lower_row_30.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_30_pred'] = budget_30 / df_append_sim.loc[count, 'rf_impression_30_pred'] * 1000

                        ############------------------Simulations for +_35 budget scenario------------------###################

                        budget_35 = df_append_sim.at[count, 'budget'] * 1.35
                        df_append_sim.loc[count, 'budget_35'] = budget_35


                        # Closest budget for +_35 budget
                        closest_budget_35 = closest(lst, budget_35)

                        # Fetch two rows for interpolate the budget values

                        if budget_35 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_35]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_35 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_35 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_35 >= budget_35:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_35]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_35 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_35 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_35]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_35 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_35 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_35'] = closest_upper_row_35.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_35'] = closest_lower_row_35.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_35'] = closest_upper_row_35.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_35'] = closest_lower_row_35.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_35'] = closest_upper_row_35.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_35'] = closest_lower_row_35.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_35'] = closest_upper_row_35.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_35'] = closest_lower_row_35.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_35'] = closest_upper_row_35.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_35'] = closest_lower_row_35.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_35'] = closest_upper_row_35.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_35'] = closest_lower_row_35.loc[0, 'weekly_freq']


                        #Interpolating values for +_35 budget

                        df_append_sim.loc[count, 'rf_impression_35_pred'] = (((closest_upper_row_35.loc[0, 'impression'] - closest_lower_row_35.loc[0, 'impression']) / (closest_upper_row_35.loc[0, 'budget'] - closest_lower_row_35.loc[0, 'budget'])) * (budget_35-closest_lower_row_35.loc[0, 'budget'])) + closest_lower_row_35.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_35_pred'] = (((closest_upper_row_35.loc[0, 'reach'] - closest_lower_row_35.loc[0, 'reach']) / (closest_upper_row_35.loc[0, 'budget'] - closest_lower_row_35.loc[0, 'budget'])) * (budget_35-closest_lower_row_35.loc[0, 'budget'])) + closest_lower_row_35.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_35_pred'] = (((closest_upper_row_35.loc[0, 'conversion'] - closest_lower_row_35.loc[0, 'conversion']) / (closest_upper_row_35.loc[0, 'budget'] - closest_lower_row_35.loc[0, 'budget'])) * (budget_35-closest_lower_row_35.loc[0, 'budget'])) + closest_lower_row_35.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_35_pred'] = (((closest_upper_row_35.loc[0, 'frequency'] - closest_lower_row_35.loc[0, 'frequency']) / (closest_upper_row_35.loc[0, 'budget'] - closest_lower_row_35.loc[0, 'budget'])) * (budget_35-closest_lower_row_35.loc[0, 'budget'])) + closest_lower_row_35.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_35_pred'] = (((closest_upper_row_35.loc[0, 'weekly_freq'] - closest_lower_row_35.loc[0, 'weekly_freq']) / (closest_upper_row_35.loc[0, 'budget'] - closest_lower_row_35.loc[0, 'budget'])) * (budget_35-closest_lower_row_35.loc[0, 'budget'])) + closest_lower_row_35.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_35_pred'] = budget_35 / df_append_sim.loc[count, 'rf_impression_35_pred'] * 1000


                        ############------------------Simulations for +40 budget scenario------------------###################

                        budget_40 = df_append_sim.at[count, 'budget'] * 1.4


                        # Closest budget for +40 budget
                        closest_budget_40 = closest(lst, budget_40)
                        df_append_sim.loc[count, 'budget_40'] = budget_40

                        # Fetch two rows for interpolate the budget values

                        if budget_40 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_40]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_40 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_40 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_40 >= budget_40:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_40]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_40 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_40 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_40]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_40 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_40 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_40'] = closest_upper_row_40.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_40'] = closest_lower_row_40.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_40'] = closest_upper_row_40.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_40'] = closest_lower_row_40.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_40'] = closest_upper_row_40.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_40'] = closest_lower_row_40.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_40'] = closest_upper_row_40.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_40'] = closest_lower_row_40.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_40'] = closest_upper_row_40.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_40'] = closest_lower_row_40.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_40'] = closest_upper_row_40.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_40'] = closest_lower_row_40.loc[0, 'weekly_freq']


                        #Interpolating values for +40 budget

                        df_append_sim.loc[count, 'rf_impression_40_pred'] = (((closest_upper_row_40.loc[0, 'impression'] - closest_lower_row_40.loc[0, 'impression']) / (closest_upper_row_40.loc[0, 'budget'] - closest_lower_row_40.loc[0, 'budget'])) * (budget_40-closest_lower_row_40.loc[0, 'budget'])) + closest_lower_row_40.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_40_pred'] = (((closest_upper_row_40.loc[0, 'reach'] - closest_lower_row_40.loc[0, 'reach']) / (closest_upper_row_40.loc[0, 'budget'] - closest_lower_row_40.loc[0, 'budget'])) * (budget_40-closest_lower_row_40.loc[0, 'budget'])) + closest_lower_row_40.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_40_pred'] = (((closest_upper_row_40.loc[0, 'conversion'] - closest_lower_row_40.loc[0, 'conversion']) / (closest_upper_row_40.loc[0, 'budget'] - closest_lower_row_40.loc[0, 'budget'])) * (budget_40-closest_lower_row_40.loc[0, 'budget'])) + closest_lower_row_40.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_40_pred'] = (((closest_upper_row_40.loc[0, 'frequency'] - closest_lower_row_40.loc[0, 'frequency']) / (closest_upper_row_40.loc[0, 'budget'] - closest_lower_row_40.loc[0, 'budget'])) * (budget_40-closest_lower_row_40.loc[0, 'budget'])) + closest_lower_row_40.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_40_pred'] = (((closest_upper_row_40.loc[0, 'weekly_freq'] - closest_lower_row_40.loc[0, 'weekly_freq']) / (closest_upper_row_40.loc[0, 'budget'] - closest_lower_row_40.loc[0, 'budget'])) * (budget_40-closest_lower_row_40.loc[0, 'budget'])) + closest_lower_row_40.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_40_pred'] = budget_40 / df_append_sim.loc[count, 'rf_impression_40_pred'] * 1000


                            ############------------------Simulations for +_45 budget scenario------------------###################

                        budget_45 = df_append_sim.at[count, 'budget'] * 1.45
                        df_append_sim.loc[count, 'budget_45'] = budget_45


                        # Closest budget for +_45 budget
                        closest_budget_45 = closest(lst, budget_45)

                        # Fetch two rows for interpolate the budget values


                        if budget_45 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_45]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_45 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_45 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()


                        elif closest_budget_45 >= budget_45:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_45]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_45 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_45 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_45]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_45 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_45 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_45'] = closest_upper_row_45.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_45'] = closest_lower_row_45.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_45'] = closest_upper_row_45.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_45'] = closest_lower_row_45.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_45'] = closest_upper_row_45.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_45'] = closest_lower_row_45.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_45'] = closest_upper_row_45.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_45'] = closest_lower_row_45.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_45'] = closest_upper_row_45.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_45'] = closest_lower_row_45.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_45'] = closest_upper_row_45.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_45'] = closest_lower_row_45.loc[0, 'weekly_freq']


                        #Interpolating values for +_45 budget

                        df_append_sim.loc[count, 'rf_impression_45_pred'] = (((closest_upper_row_45.loc[0, 'impression'] - closest_lower_row_45.loc[0, 'impression']) / (closest_upper_row_45.loc[0, 'budget'] - closest_lower_row_45.loc[0, 'budget'])) * (budget_45-closest_lower_row_45.loc[0, 'budget'])) + closest_lower_row_45.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_45_pred'] = (((closest_upper_row_45.loc[0, 'reach'] - closest_lower_row_45.loc[0, 'reach']) / (closest_upper_row_45.loc[0, 'budget'] - closest_lower_row_45.loc[0, 'budget'])) * (budget_45-closest_lower_row_45.loc[0, 'budget'])) + closest_lower_row_45.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_45_pred'] = (((closest_upper_row_45.loc[0, 'conversion'] - closest_lower_row_45.loc[0, 'conversion']) / (closest_upper_row_45.loc[0, 'budget'] - closest_lower_row_45.loc[0, 'budget'])) * (budget_45-closest_lower_row_45.loc[0, 'budget'])) + closest_lower_row_45.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_45_pred'] = (((closest_upper_row_45.loc[0, 'frequency'] - closest_lower_row_45.loc[0, 'frequency']) / (closest_upper_row_45.loc[0, 'budget'] - closest_lower_row_45.loc[0, 'budget'])) * (budget_45-closest_lower_row_45.loc[0, 'budget'])) + closest_lower_row_45.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_45_pred'] = (((closest_upper_row_45.loc[0, 'weekly_freq'] - closest_lower_row_45.loc[0, 'weekly_freq']) / (closest_upper_row_45.loc[0, 'budget'] - closest_lower_row_45.loc[0, 'budget'])) * (budget_45-closest_lower_row_45.loc[0, 'budget'])) + closest_lower_row_45.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_45_pred'] = budget_45 / df_append_sim.loc[count, 'rf_impression_45_pred'] * 1000




                        ############------------------Simulations for +50 budget scenario------------------###################

                        budget_50 = df_append_sim.at[count, 'budget'] * 1.5


                        # Closest budget for +50 budget
                        closest_budget_50 = closest(lst, budget_50)
                        df_append_sim.loc[count, 'budget_50'] = budget_50

                        # Fetch two rows for interpolate the budget values

                        if budget_50 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_50]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_50 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_50 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_50 >= budget_50:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_50]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_50 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_50 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_50]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_50 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_50 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_50'] = closest_upper_row_50.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_50'] = closest_lower_row_50.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_50'] = closest_upper_row_50.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_50'] = closest_lower_row_50.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_50'] = closest_upper_row_50.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_50'] = closest_lower_row_50.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_50'] = closest_upper_row_50.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_50'] = closest_lower_row_50.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_50'] = closest_upper_row_50.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_50'] = closest_lower_row_50.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_50'] = closest_upper_row_50.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_50'] = closest_lower_row_50.loc[0, 'weekly_freq']


                        #Interpolating values for +50 budget

                        df_append_sim.loc[count, 'rf_impression_50_pred'] = (((closest_upper_row_50.loc[0, 'impression'] - closest_lower_row_50.loc[0, 'impression']) / (closest_upper_row_50.loc[0, 'budget'] - closest_lower_row_50.loc[0, 'budget'])) * (budget_50-closest_lower_row_50.loc[0, 'budget'])) + closest_lower_row_50.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_50_pred'] = (((closest_upper_row_50.loc[0, 'reach'] - closest_lower_row_50.loc[0, 'reach']) / (closest_upper_row_50.loc[0, 'budget'] - closest_lower_row_50.loc[0, 'budget'])) * (budget_50-closest_lower_row_50.loc[0, 'budget'])) + closest_lower_row_50.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_50_pred'] = (((closest_upper_row_50.loc[0, 'conversion'] - closest_lower_row_50.loc[0, 'conversion']) / (closest_upper_row_50.loc[0, 'budget'] - closest_lower_row_50.loc[0, 'budget'])) * (budget_50-closest_lower_row_50.loc[0, 'budget'])) + closest_lower_row_50.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_50_pred'] = (((closest_upper_row_50.loc[0, 'frequency'] - closest_lower_row_50.loc[0, 'frequency']) / (closest_upper_row_50.loc[0, 'budget'] - closest_lower_row_50.loc[0, 'budget'])) * (budget_50-closest_lower_row_50.loc[0, 'budget'])) + closest_lower_row_50.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_50_pred'] = (((closest_upper_row_50.loc[0, 'weekly_freq'] - closest_lower_row_50.loc[0, 'weekly_freq']) / (closest_upper_row_50.loc[0, 'budget'] - closest_lower_row_50.loc[0, 'budget'])) * (budget_50-closest_lower_row_50.loc[0, 'budget'])) + closest_lower_row_50.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_50_pred'] = budget_50 / df_append_sim.loc[count, 'rf_impression_50_pred'] * 1000





                        ############------------------Simulations for +55 budget scenario------------------###################

                        budget_55 = df_append_sim.at[count, 'budget'] * 1.55


                        # Closest budget for +55 budget
                        closest_budget_55 = closest(lst, budget_55)
                        df_append_sim.loc[count, 'budget_55'] = budget_55

                        # Fetch two rows for interpolate the budget values

                        if budget_55 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_55]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_55 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_55 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_55 >= budget_55:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_55]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_55 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_55 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_55]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_55 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_55 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_55'] = closest_upper_row_55.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_55'] = closest_lower_row_55.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_55'] = closest_upper_row_55.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_55'] = closest_lower_row_55.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_55'] = closest_upper_row_55.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_55'] = closest_lower_row_55.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_55'] = closest_upper_row_55.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_55'] = closest_lower_row_55.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_55'] = closest_upper_row_55.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_55'] = closest_lower_row_55.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_55'] = closest_upper_row_55.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_55'] = closest_lower_row_55.loc[0, 'weekly_freq']


                        #Interpolating values for +55 budget

                        df_append_sim.loc[count, 'rf_impression_55_pred'] = (((closest_upper_row_55.loc[0, 'impression'] - closest_lower_row_55.loc[0, 'impression']) / (closest_upper_row_55.loc[0, 'budget'] - closest_lower_row_55.loc[0, 'budget'])) * (budget_55-closest_lower_row_55.loc[0, 'budget'])) + closest_lower_row_55.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_55_pred'] = (((closest_upper_row_55.loc[0, 'reach'] - closest_lower_row_55.loc[0, 'reach']) / (closest_upper_row_55.loc[0, 'budget'] - closest_lower_row_55.loc[0, 'budget'])) * (budget_55-closest_lower_row_55.loc[0, 'budget'])) + closest_lower_row_55.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_55_pred'] = (((closest_upper_row_55.loc[0, 'conversion'] - closest_lower_row_55.loc[0, 'conversion']) / (closest_upper_row_55.loc[0, 'budget'] - closest_lower_row_55.loc[0, 'budget'])) * (budget_55-closest_lower_row_55.loc[0, 'budget'])) + closest_lower_row_55.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_55_pred'] = (((closest_upper_row_55.loc[0, 'frequency'] - closest_lower_row_55.loc[0, 'frequency']) / (closest_upper_row_55.loc[0, 'budget'] - closest_lower_row_55.loc[0, 'budget'])) * (budget_55-closest_lower_row_55.loc[0, 'budget'])) + closest_lower_row_55.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_55_pred'] = (((closest_upper_row_55.loc[0, 'weekly_freq'] - closest_lower_row_55.loc[0, 'weekly_freq']) / (closest_upper_row_55.loc[0, 'budget'] - closest_lower_row_55.loc[0, 'budget'])) * (budget_55-closest_lower_row_55.loc[0, 'budget'])) + closest_lower_row_55.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_55_pred'] = budget_55 / df_append_sim.loc[count, 'rf_impression_55_pred'] * 1000





                        ############------------------Simulations for +60 budget scenario------------------###################

                        budget_60 = df_append_sim.at[count, 'budget'] * 1.6


                        # Closest budget for +60 budget
                        closest_budget_60 = closest(lst, budget_60)
                        df_append_sim.loc[count, 'budget_60'] = budget_60

                        # Fetch two rows for interpolate the budget values

                        if budget_60 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_60]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_60 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_60 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_60 >= budget_60:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_60]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_60 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_60 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_60]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_60 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_60 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_60'] = closest_upper_row_60.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_60'] = closest_lower_row_60.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_60'] = closest_upper_row_60.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_60'] = closest_lower_row_60.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_60'] = closest_upper_row_60.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_60'] = closest_lower_row_60.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_60'] = closest_upper_row_60.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_60'] = closest_lower_row_60.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_60'] = closest_upper_row_60.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_60'] = closest_lower_row_60.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_60'] = closest_upper_row_60.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_60'] = closest_lower_row_60.loc[0, 'weekly_freq']


                        #Interpolating values for +60 budget

                        df_append_sim.loc[count, 'rf_impression_60_pred'] = (((closest_upper_row_60.loc[0, 'impression'] - closest_lower_row_60.loc[0, 'impression']) / (closest_upper_row_60.loc[0, 'budget'] - closest_lower_row_60.loc[0, 'budget'])) * (budget_60-closest_lower_row_60.loc[0, 'budget'])) + closest_lower_row_60.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_60_pred'] = (((closest_upper_row_60.loc[0, 'reach'] - closest_lower_row_60.loc[0, 'reach']) / (closest_upper_row_60.loc[0, 'budget'] - closest_lower_row_60.loc[0, 'budget'])) * (budget_60-closest_lower_row_60.loc[0, 'budget'])) + closest_lower_row_60.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_60_pred'] = (((closest_upper_row_60.loc[0, 'conversion'] - closest_lower_row_60.loc[0, 'conversion']) / (closest_upper_row_60.loc[0, 'budget'] - closest_lower_row_60.loc[0, 'budget'])) * (budget_60-closest_lower_row_60.loc[0, 'budget'])) + closest_lower_row_60.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_60_pred'] = (((closest_upper_row_60.loc[0, 'frequency'] - closest_lower_row_60.loc[0, 'frequency']) / (closest_upper_row_60.loc[0, 'budget'] - closest_lower_row_60.loc[0, 'budget'])) * (budget_60-closest_lower_row_60.loc[0, 'budget'])) + closest_lower_row_60.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_60_pred'] = (((closest_upper_row_60.loc[0, 'weekly_freq'] - closest_lower_row_60.loc[0, 'weekly_freq']) / (closest_upper_row_60.loc[0, 'budget'] - closest_lower_row_60.loc[0, 'budget'])) * (budget_60-closest_lower_row_60.loc[0, 'budget'])) + closest_lower_row_60.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_60_pred'] = budget_60 / df_append_sim.loc[count, 'rf_impression_60_pred'] * 1000





                        ############------------------Simulations for +65 budget scenario------------------###################

                        budget_65 = df_append_sim.at[count, 'budget'] * 1.65


                        # Closest budget for +65 budget
                        closest_budget_65 = closest(lst, budget_65)
                        df_append_sim.loc[count, 'budget_65'] = budget_65

                        # Fetch two rows for interpolate the budget values

                        if budget_65 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_65]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_65 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_65 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_65 >= budget_65:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_65]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_65 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_65 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_65]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_65 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_65 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_65'] = closest_upper_row_65.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_65'] = closest_lower_row_65.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_65'] = closest_upper_row_65.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_65'] = closest_lower_row_65.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_65'] = closest_upper_row_65.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_65'] = closest_lower_row_65.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_65'] = closest_upper_row_65.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_65'] = closest_lower_row_65.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_65'] = closest_upper_row_65.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_65'] = closest_lower_row_65.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_65'] = closest_upper_row_65.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_65'] = closest_lower_row_65.loc[0, 'weekly_freq']


                        #Interpolating values for +65 budget

                        df_append_sim.loc[count, 'rf_impression_65_pred'] = (((closest_upper_row_65.loc[0, 'impression'] - closest_lower_row_65.loc[0, 'impression']) / (closest_upper_row_65.loc[0, 'budget'] - closest_lower_row_65.loc[0, 'budget'])) * (budget_65-closest_lower_row_65.loc[0, 'budget'])) + closest_lower_row_65.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_65_pred'] = (((closest_upper_row_65.loc[0, 'reach'] - closest_lower_row_65.loc[0, 'reach']) / (closest_upper_row_65.loc[0, 'budget'] - closest_lower_row_65.loc[0, 'budget'])) * (budget_65-closest_lower_row_65.loc[0, 'budget'])) + closest_lower_row_65.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_65_pred'] = (((closest_upper_row_65.loc[0, 'conversion'] - closest_lower_row_65.loc[0, 'conversion']) / (closest_upper_row_65.loc[0, 'budget'] - closest_lower_row_65.loc[0, 'budget'])) * (budget_65-closest_lower_row_65.loc[0, 'budget'])) + closest_lower_row_65.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_65_pred'] = (((closest_upper_row_65.loc[0, 'frequency'] - closest_lower_row_65.loc[0, 'frequency']) / (closest_upper_row_65.loc[0, 'budget'] - closest_lower_row_65.loc[0, 'budget'])) * (budget_65-closest_lower_row_65.loc[0, 'budget'])) + closest_lower_row_65.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_65_pred'] = (((closest_upper_row_65.loc[0, 'weekly_freq'] - closest_lower_row_65.loc[0, 'weekly_freq']) / (closest_upper_row_65.loc[0, 'budget'] - closest_lower_row_65.loc[0, 'budget'])) * (budget_65-closest_lower_row_65.loc[0, 'budget'])) + closest_lower_row_65.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_65_pred'] = budget_65 / df_append_sim.loc[count, 'rf_impression_65_pred'] * 1000



                        ############------------------Simulations for +70 budget scenario------------------###################

                        budget_70 = df_append_sim.at[count, 'budget'] * 1.7


                        # Closest budget for +70 budget
                        closest_budget_70 = closest(lst, budget_70)
                        df_append_sim.loc[count, 'budget_70'] = budget_70

                        # Fetch two rows for interpolate the budget values

                        if budget_70 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_70]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_70 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_70 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_70 >= budget_70:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_70]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_70 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_70 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_70]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_70 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_70 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_70'] = closest_upper_row_70.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_70'] = closest_lower_row_70.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_70'] = closest_upper_row_70.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_70'] = closest_lower_row_70.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_70'] = closest_upper_row_70.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_70'] = closest_lower_row_70.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_70'] = closest_upper_row_70.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_70'] = closest_lower_row_70.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_70'] = closest_upper_row_70.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_70'] = closest_lower_row_70.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_70'] = closest_upper_row_70.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_70'] = closest_lower_row_70.loc[0, 'weekly_freq']


                        #Interpolating values for +70 budget

                        df_append_sim.loc[count, 'rf_impression_70_pred'] = (((closest_upper_row_70.loc[0, 'impression'] - closest_lower_row_70.loc[0, 'impression']) / (closest_upper_row_70.loc[0, 'budget'] - closest_lower_row_70.loc[0, 'budget'])) * (budget_70-closest_lower_row_70.loc[0, 'budget'])) + closest_lower_row_70.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_70_pred'] = (((closest_upper_row_70.loc[0, 'reach'] - closest_lower_row_70.loc[0, 'reach']) / (closest_upper_row_70.loc[0, 'budget'] - closest_lower_row_70.loc[0, 'budget'])) * (budget_70-closest_lower_row_70.loc[0, 'budget'])) + closest_lower_row_70.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_70_pred'] = (((closest_upper_row_70.loc[0, 'conversion'] - closest_lower_row_70.loc[0, 'conversion']) / (closest_upper_row_70.loc[0, 'budget'] - closest_lower_row_70.loc[0, 'budget'])) * (budget_70-closest_lower_row_70.loc[0, 'budget'])) + closest_lower_row_70.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_70_pred'] = (((closest_upper_row_70.loc[0, 'frequency'] - closest_lower_row_70.loc[0, 'frequency']) / (closest_upper_row_70.loc[0, 'budget'] - closest_lower_row_70.loc[0, 'budget'])) * (budget_70-closest_lower_row_70.loc[0, 'budget'])) + closest_lower_row_70.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_70_pred'] = (((closest_upper_row_70.loc[0, 'weekly_freq'] - closest_lower_row_70.loc[0, 'weekly_freq']) / (closest_upper_row_70.loc[0, 'budget'] - closest_lower_row_70.loc[0, 'budget'])) * (budget_70-closest_lower_row_70.loc[0, 'budget'])) + closest_lower_row_70.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_70_pred'] = budget_70 / df_append_sim.loc[count, 'rf_impression_70_pred'] * 1000



                        ############------------------Simulations for +75 budget scenario------------------###################

                        budget_75 = df_append_sim.at[count, 'budget'] * 1.75


                        # Closest budget for +75 budget
                        closest_budget_75 = closest(lst, budget_75)
                        df_append_sim.loc[count, 'budget_75'] = budget_75

                        # Fetch two rows for interpolate the budget values

                        if budget_75 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_75]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_75 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_75 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_75 >= budget_75:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_75]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_75 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_75 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_75]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_75 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_75 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_75'] = closest_upper_row_75.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_75'] = closest_lower_row_75.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_75'] = closest_upper_row_75.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_75'] = closest_lower_row_75.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_75'] = closest_upper_row_75.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_75'] = closest_lower_row_75.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_75'] = closest_upper_row_75.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_75'] = closest_lower_row_75.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_75'] = closest_upper_row_75.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_75'] = closest_lower_row_75.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_75'] = closest_upper_row_75.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_75'] = closest_lower_row_75.loc[0, 'weekly_freq']


                        #Interpolating values for +70 budget

                        df_append_sim.loc[count, 'rf_impression_75_pred'] = (((closest_upper_row_75.loc[0, 'impression'] - closest_lower_row_75.loc[0, 'impression']) / (closest_upper_row_75.loc[0, 'budget'] - closest_lower_row_75.loc[0, 'budget'])) * (budget_75-closest_lower_row_75.loc[0, 'budget'])) + closest_lower_row_75.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_75_pred'] = (((closest_upper_row_75.loc[0, 'reach'] - closest_lower_row_75.loc[0, 'reach']) / (closest_upper_row_75.loc[0, 'budget'] - closest_lower_row_75.loc[0, 'budget'])) * (budget_75-closest_lower_row_75.loc[0, 'budget'])) + closest_lower_row_75.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_75_pred'] = (((closest_upper_row_75.loc[0, 'conversion'] - closest_lower_row_75.loc[0, 'conversion']) / (closest_upper_row_75.loc[0, 'budget'] - closest_lower_row_75.loc[0, 'budget'])) * (budget_75-closest_lower_row_75.loc[0, 'budget'])) + closest_lower_row_75.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_75_pred'] = (((closest_upper_row_75.loc[0, 'frequency'] - closest_lower_row_75.loc[0, 'frequency']) / (closest_upper_row_75.loc[0, 'budget'] - closest_lower_row_75.loc[0, 'budget'])) * (budget_75-closest_lower_row_75.loc[0, 'budget'])) + closest_lower_row_75.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_75_pred'] = (((closest_upper_row_75.loc[0, 'weekly_freq'] - closest_lower_row_75.loc[0, 'weekly_freq']) / (closest_upper_row_75.loc[0, 'budget'] - closest_lower_row_75.loc[0, 'budget'])) * (budget_75-closest_lower_row_75.loc[0, 'budget'])) + closest_lower_row_75.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_75_pred'] = budget_75 / df_append_sim.loc[count, 'rf_impression_75_pred'] * 1000





                        ############------------------Simulations for +80 budget scenario------------------###################

                        budget_80 = df_append_sim.at[count, 'budget'] * 1.8


                        # Closest budget for +80 budget
                        closest_budget_80 = closest(lst, budget_80)
                        df_append_sim.loc[count, 'budget_80'] = budget_80

                        # Fetch two rows for interpolate the budget values

                        if budget_80 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_80]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_80 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_80 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_80 >= budget_80:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_80]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_80 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_80 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_80]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_80 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_80 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_80'] = closest_upper_row_80.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_80'] = closest_lower_row_80.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_80'] = closest_upper_row_80.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_80'] = closest_lower_row_80.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_80'] = closest_upper_row_80.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_80'] = closest_lower_row_80.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_80'] = closest_upper_row_80.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_80'] = closest_lower_row_80.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_80'] = closest_upper_row_80.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_80'] = closest_lower_row_80.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_80'] = closest_upper_row_80.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_80'] = closest_lower_row_80.loc[0, 'weekly_freq']


                        #Interpolating values for +80 budget

                        df_append_sim.loc[count, 'rf_impression_80_pred'] = (((closest_upper_row_80.loc[0, 'impression'] - closest_lower_row_80.loc[0, 'impression']) / (closest_upper_row_80.loc[0, 'budget'] - closest_lower_row_80.loc[0, 'budget'])) * (budget_80-closest_lower_row_80.loc[0, 'budget'])) + closest_lower_row_80.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_80_pred'] = (((closest_upper_row_80.loc[0, 'reach'] - closest_lower_row_80.loc[0, 'reach']) / (closest_upper_row_80.loc[0, 'budget'] - closest_lower_row_80.loc[0, 'budget'])) * (budget_80-closest_lower_row_80.loc[0, 'budget'])) + closest_lower_row_80.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_80_pred'] = (((closest_upper_row_80.loc[0, 'conversion'] - closest_lower_row_80.loc[0, 'conversion']) / (closest_upper_row_80.loc[0, 'budget'] - closest_lower_row_80.loc[0, 'budget'])) * (budget_80-closest_lower_row_80.loc[0, 'budget'])) + closest_lower_row_80.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_80_pred'] = (((closest_upper_row_80.loc[0, 'frequency'] - closest_lower_row_80.loc[0, 'frequency']) / (closest_upper_row_80.loc[0, 'budget'] - closest_lower_row_80.loc[0, 'budget'])) * (budget_80-closest_lower_row_80.loc[0, 'budget'])) + closest_lower_row_80.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_80_pred'] = (((closest_upper_row_80.loc[0, 'weekly_freq'] - closest_lower_row_80.loc[0, 'weekly_freq']) / (closest_upper_row_80.loc[0, 'budget'] - closest_lower_row_80.loc[0, 'budget'])) * (budget_80-closest_lower_row_80.loc[0, 'budget'])) + closest_lower_row_80.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_80_pred'] = budget_80 / df_append_sim.loc[count, 'rf_impression_80_pred'] * 1000



                        ############------------------Simulations for +85 budget scenario------------------###################

                        budget_85 = df_append_sim.at[count, 'budget'] * 1.85


                        # Closest budget for +85 budget
                        closest_budget_85 = closest(lst, budget_85)
                        df_append_sim.loc[count, 'budget_85'] = budget_85

                        # Fetch two rows for interpolate the budget values

                        if budget_85 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_85]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_85 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_85 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_85 >= budget_85:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_85]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_85 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_85 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_85]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_85 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_85 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_85'] = closest_upper_row_85.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_85'] = closest_lower_row_85.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_85'] = closest_upper_row_85.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_85'] = closest_lower_row_85.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_85'] = closest_upper_row_85.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_85'] = closest_lower_row_85.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_85'] = closest_upper_row_85.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_85'] = closest_lower_row_85.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_85'] = closest_upper_row_85.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_85'] = closest_lower_row_85.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_85'] = closest_upper_row_85.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_85'] = closest_lower_row_85.loc[0, 'weekly_freq']


                        #Interpolating values for +85 budget

                        df_append_sim.loc[count, 'rf_impression_85_pred'] = (((closest_upper_row_85.loc[0, 'impression'] - closest_lower_row_85.loc[0, 'impression']) / (closest_upper_row_85.loc[0, 'budget'] - closest_lower_row_85.loc[0, 'budget'])) * (budget_85-closest_lower_row_85.loc[0, 'budget'])) + closest_lower_row_85.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_85_pred'] = (((closest_upper_row_85.loc[0, 'reach'] - closest_lower_row_85.loc[0, 'reach']) / (closest_upper_row_85.loc[0, 'budget'] - closest_lower_row_85.loc[0, 'budget'])) * (budget_85-closest_lower_row_85.loc[0, 'budget'])) + closest_lower_row_85.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_85_pred'] = (((closest_upper_row_85.loc[0, 'conversion'] - closest_lower_row_85.loc[0, 'conversion']) / (closest_upper_row_85.loc[0, 'budget'] - closest_lower_row_85.loc[0, 'budget'])) * (budget_85-closest_lower_row_85.loc[0, 'budget'])) + closest_lower_row_85.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_85_pred'] = (((closest_upper_row_85.loc[0, 'frequency'] - closest_lower_row_85.loc[0, 'frequency']) / (closest_upper_row_85.loc[0, 'budget'] - closest_lower_row_85.loc[0, 'budget'])) * (budget_85-closest_lower_row_85.loc[0, 'budget'])) + closest_lower_row_85.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_85_pred'] = (((closest_upper_row_85.loc[0, 'weekly_freq'] - closest_lower_row_85.loc[0, 'weekly_freq']) / (closest_upper_row_85.loc[0, 'budget'] - closest_lower_row_85.loc[0, 'budget'])) * (budget_85-closest_lower_row_85.loc[0, 'budget'])) + closest_lower_row_85.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_85_pred'] = budget_85 / df_append_sim.loc[count, 'rf_impression_85_pred'] * 1000


                        ############------------------Simulations for +_90 budget scenario------------------###################

                        budget_90 = df_append_sim.at[count, 'budget'] * 1.90


                        # Closest budget for +_90 budget
                        closest_budget_90 = closest(lst, budget_90)
                        df_append_sim.loc[count, 'budget_90'] = budget_90

                        # Fetch two rows for interpolate the budget values

                        if budget_90 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_90]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_90 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_90 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_90 >= budget_90:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_90]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_90 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_90 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_90]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_90 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_90 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_90'] = closest_upper_row_90.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_90'] = closest_lower_row_90.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_90'] = closest_upper_row_90.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_90'] = closest_lower_row_90.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_90'] = closest_upper_row_90.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_90'] = closest_lower_row_90.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_90'] = closest_upper_row_90.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_90'] = closest_lower_row_90.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_90'] = closest_upper_row_90.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_90'] = closest_lower_row_90.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_90'] = closest_upper_row_90.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_90'] = closest_lower_row_90.loc[0, 'weekly_freq']


                        #Interpolating values for +_90 budget

                        df_append_sim.loc[count, 'rf_impression_90_pred'] = (((closest_upper_row_90.loc[0, 'impression'] - closest_lower_row_90.loc[0, 'impression']) / (closest_upper_row_90.loc[0, 'budget'] - closest_lower_row_90.loc[0, 'budget'])) * (budget_90-closest_lower_row_90.loc[0, 'budget'])) + closest_lower_row_90.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_90_pred'] = (((closest_upper_row_90.loc[0, 'reach'] - closest_lower_row_90.loc[0, 'reach']) / (closest_upper_row_90.loc[0, 'budget'] - closest_lower_row_90.loc[0, 'budget'])) * (budget_90-closest_lower_row_90.loc[0, 'budget'])) + closest_lower_row_90.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_90_pred'] = (((closest_upper_row_90.loc[0, 'conversion'] - closest_lower_row_90.loc[0, 'conversion']) / (closest_upper_row_90.loc[0, 'budget'] - closest_lower_row_90.loc[0, 'budget'])) * (budget_90-closest_lower_row_90.loc[0, 'budget'])) + closest_lower_row_90.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_90_pred'] = (((closest_upper_row_90.loc[0, 'frequency'] - closest_lower_row_90.loc[0, 'frequency']) / (closest_upper_row_90.loc[0, 'budget'] - closest_lower_row_90.loc[0, 'budget'])) * (budget_90-closest_lower_row_90.loc[0, 'budget'])) + closest_lower_row_90.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_90_pred'] = (((closest_upper_row_90.loc[0, 'weekly_freq'] - closest_lower_row_90.loc[0, 'weekly_freq']) / (closest_upper_row_90.loc[0, 'budget'] - closest_lower_row_90.loc[0, 'budget'])) * (budget_90-closest_lower_row_90.loc[0, 'budget'])) + closest_lower_row_90.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_90_pred'] = budget_90 / df_append_sim.loc[count, 'rf_impression_90_pred'] * 1000


                        ############------------------Simulations for +_95 budget scenario------------------###################

                        budget_95 = df_append_sim.at[count, 'budget'] * 1.95


                        # Closest budget for +_95 budget
                        closest_budget_95 = closest(lst, budget_95)
                        df_append_sim.loc[count, 'budget_95'] = budget_95

                        # Fetch two rows for interpolate the budget values

                        if budget_95 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_95]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_95 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_95 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_95 >= budget_95:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_95]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_95 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_95 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_95]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_95 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_95 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_95'] = closest_upper_row_95.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_95'] = closest_lower_row_95.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_95'] = closest_upper_row_95.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_95'] = closest_lower_row_95.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_95'] = closest_upper_row_95.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_95'] = closest_lower_row_95.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_95'] = closest_upper_row_95.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_95'] = closest_lower_row_95.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_95'] = closest_upper_row_95.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_95'] = closest_lower_row_95.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_95'] = closest_upper_row_95.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_95'] = closest_lower_row_95.loc[0, 'weekly_freq']


                        #Interpolating values for +_95 budget

                        df_append_sim.loc[count, 'rf_impression_95_pred'] = (((closest_upper_row_95.loc[0, 'impression'] - closest_lower_row_95.loc[0, 'impression']) / (closest_upper_row_95.loc[0, 'budget'] - closest_lower_row_95.loc[0, 'budget'])) * (budget_95-closest_lower_row_95.loc[0, 'budget'])) + closest_lower_row_95.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_95_pred'] = (((closest_upper_row_95.loc[0, 'reach'] - closest_lower_row_95.loc[0, 'reach']) / (closest_upper_row_95.loc[0, 'budget'] - closest_lower_row_95.loc[0, 'budget'])) * (budget_95-closest_lower_row_95.loc[0, 'budget'])) + closest_lower_row_95.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_95_pred'] = (((closest_upper_row_95.loc[0, 'conversion'] - closest_lower_row_95.loc[0, 'conversion']) / (closest_upper_row_95.loc[0, 'budget'] - closest_lower_row_95.loc[0, 'budget'])) * (budget_95-closest_lower_row_95.loc[0, 'budget'])) + closest_lower_row_95.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_95_pred'] = (((closest_upper_row_95.loc[0, 'frequency'] - closest_lower_row_95.loc[0, 'frequency']) / (closest_upper_row_95.loc[0, 'budget'] - closest_lower_row_95.loc[0, 'budget'])) * (budget_95-closest_lower_row_95.loc[0, 'budget'])) + closest_lower_row_95.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_95_pred'] = (((closest_upper_row_95.loc[0, 'weekly_freq'] - closest_lower_row_95.loc[0, 'weekly_freq']) / (closest_upper_row_95.loc[0, 'budget'] - closest_lower_row_95.loc[0, 'budget'])) * (budget_95-closest_lower_row_95.loc[0, 'budget'])) + closest_lower_row_95.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_95_pred'] = budget_95 / df_append_sim.loc[count, 'rf_impression_95_pred'] * 1000


                        ############------------------Simulations for +_100 budget scenario------------------###################

                        budget_100 = df_append_sim.at[count, 'budget'] * 2


                        # Closest budget for +_100 budget
                        closest_budget_100 = closest(lst, budget_100)
                        df_append_sim.loc[count, 'budget_100'] = budget_100

                        # Fetch two rows for interpolate the budget values

                        if budget_100 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_100]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_100 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_100 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_100 >= budget_100:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_100]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_100 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_100 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_100]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_100 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_100 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_100'] = closest_upper_row_100.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_100'] = closest_lower_row_100.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_100'] = closest_upper_row_100.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_100'] = closest_lower_row_100.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_100'] = closest_upper_row_100.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_100'] = closest_lower_row_100.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_100'] = closest_upper_row_100.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_100'] = closest_lower_row_100.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_100'] = closest_upper_row_100.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_100'] = closest_lower_row_100.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_100'] = closest_upper_row_100.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_100'] = closest_lower_row_100.loc[0, 'weekly_freq']


                        #Interpolating values for +_100 budget

                        df_append_sim.loc[count, 'rf_impression_100_pred'] = (((closest_upper_row_100.loc[0, 'impression'] - closest_lower_row_100.loc[0, 'impression']) / (closest_upper_row_100.loc[0, 'budget'] - closest_lower_row_100.loc[0, 'budget'])) * (budget_100-closest_lower_row_100.loc[0, 'budget'])) + closest_lower_row_100.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_100_pred'] = (((closest_upper_row_100.loc[0, 'reach'] - closest_lower_row_100.loc[0, 'reach']) / (closest_upper_row_100.loc[0, 'budget'] - closest_lower_row_100.loc[0, 'budget'])) * (budget_100-closest_lower_row_100.loc[0, 'budget'])) + closest_lower_row_100.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_100_pred'] = (((closest_upper_row_100.loc[0, 'conversion'] - closest_lower_row_100.loc[0, 'conversion']) / (closest_upper_row_100.loc[0, 'budget'] - closest_lower_row_100.loc[0, 'budget'])) * (budget_100-closest_lower_row_100.loc[0, 'budget'])) + closest_lower_row_100.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_100_pred'] = (((closest_upper_row_100.loc[0, 'frequency'] - closest_lower_row_100.loc[0, 'frequency']) / (closest_upper_row_100.loc[0, 'budget'] - closest_lower_row_100.loc[0, 'budget'])) * (budget_100-closest_lower_row_100.loc[0, 'budget'])) + closest_lower_row_100.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_100_pred'] = (((closest_upper_row_100.loc[0, 'weekly_freq'] - closest_lower_row_100.loc[0, 'weekly_freq']) / (closest_upper_row_100.loc[0, 'budget'] - closest_lower_row_100.loc[0, 'budget'])) * (budget_100-closest_lower_row_100.loc[0, 'budget'])) + closest_lower_row_100.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_100_pred'] = budget_100 / df_append_sim.loc[count, 'rf_impression_100_pred'] * 1000


                        ############------------------Simulations for +_105 budget scenario------------------###################

                        budget_105 = df_append_sim.at[count, 'budget'] * 2.05


                        # Closest budget for +_105 budget
                        closest_budget_105 = closest(lst, budget_105)
                        df_append_sim.loc[count, 'budget_105'] = budget_105

                        # Fetch two rows for interpolate the budget values

                        if budget_105 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_105]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_105 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_105 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_105 >= budget_105:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_105]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_105 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_105 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_105]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_105 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_105 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_105'] = closest_upper_row_105.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_105'] = closest_lower_row_105.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_105'] = closest_upper_row_105.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_105'] = closest_lower_row_105.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_105'] = closest_upper_row_105.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_105'] = closest_lower_row_105.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_105'] = closest_upper_row_105.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_105'] = closest_lower_row_105.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_105'] = closest_upper_row_105.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_105'] = closest_lower_row_105.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_105'] = closest_upper_row_105.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_105'] = closest_lower_row_105.loc[0, 'weekly_freq']


                        #Interpolating values for +_105 budget

                        df_append_sim.loc[count, 'rf_impression_105_pred'] = (((closest_upper_row_105.loc[0, 'impression'] - closest_lower_row_105.loc[0, 'impression']) / (closest_upper_row_105.loc[0, 'budget'] - closest_lower_row_105.loc[0, 'budget'])) * (budget_105-closest_lower_row_105.loc[0, 'budget'])) + closest_lower_row_105.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_105_pred'] = (((closest_upper_row_105.loc[0, 'reach'] - closest_lower_row_105.loc[0, 'reach']) / (closest_upper_row_105.loc[0, 'budget'] - closest_lower_row_105.loc[0, 'budget'])) * (budget_105-closest_lower_row_105.loc[0, 'budget'])) + closest_lower_row_105.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_105_pred'] = (((closest_upper_row_105.loc[0, 'conversion'] - closest_lower_row_105.loc[0, 'conversion']) / (closest_upper_row_105.loc[0, 'budget'] - closest_lower_row_105.loc[0, 'budget'])) * (budget_105-closest_lower_row_105.loc[0, 'budget'])) + closest_lower_row_105.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_105_pred'] = (((closest_upper_row_105.loc[0, 'frequency'] - closest_lower_row_105.loc[0, 'frequency']) / (closest_upper_row_105.loc[0, 'budget'] - closest_lower_row_105.loc[0, 'budget'])) * (budget_105-closest_lower_row_105.loc[0, 'budget'])) + closest_lower_row_105.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_105_pred'] = (((closest_upper_row_105.loc[0, 'weekly_freq'] - closest_lower_row_105.loc[0, 'weekly_freq']) / (closest_upper_row_105.loc[0, 'budget'] - closest_lower_row_105.loc[0, 'budget'])) * (budget_105-closest_lower_row_105.loc[0, 'budget'])) + closest_lower_row_105.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_105_pred'] = budget_105 / df_append_sim.loc[count, 'rf_impression_105_pred'] * 1000


                        ############------------------Simulations for +_110 budget scenario------------------###################

                        budget_110 = df_append_sim.at[count, 'budget'] * 2.1


                        # Closest budget for +_110 budget
                        closest_budget_110 = closest(lst, budget_110)
                        df_append_sim.loc[count, 'budget_110'] = budget_110

                        # Fetch two rows for interpolate the budget values

                        if budget_110 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_110]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_110 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_110 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_110 >= budget_110:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_110]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_110 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_110 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_110]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_110 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_110 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_110'] = closest_upper_row_110.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_110'] = closest_lower_row_110.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_110'] = closest_upper_row_110.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_110'] = closest_lower_row_110.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_110'] = closest_upper_row_110.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_110'] = closest_lower_row_110.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_110'] = closest_upper_row_110.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_110'] = closest_lower_row_110.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_110'] = closest_upper_row_110.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_110'] = closest_lower_row_110.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_110'] = closest_upper_row_110.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_110'] = closest_lower_row_110.loc[0, 'weekly_freq']


                        #Interpolating values for +_110 budget

                        df_append_sim.loc[count, 'rf_impression_110_pred'] = (((closest_upper_row_110.loc[0, 'impression'] - closest_lower_row_110.loc[0, 'impression']) / (closest_upper_row_110.loc[0, 'budget'] - closest_lower_row_110.loc[0, 'budget'])) * (budget_110-closest_lower_row_110.loc[0, 'budget'])) + closest_lower_row_110.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_110_pred'] = (((closest_upper_row_110.loc[0, 'reach'] - closest_lower_row_110.loc[0, 'reach']) / (closest_upper_row_110.loc[0, 'budget'] - closest_lower_row_110.loc[0, 'budget'])) * (budget_110-closest_lower_row_110.loc[0, 'budget'])) + closest_lower_row_110.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_110_pred'] = (((closest_upper_row_110.loc[0, 'conversion'] - closest_lower_row_110.loc[0, 'conversion']) / (closest_upper_row_110.loc[0, 'budget'] - closest_lower_row_110.loc[0, 'budget'])) * (budget_110-closest_lower_row_110.loc[0, 'budget'])) + closest_lower_row_110.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_110_pred'] = (((closest_upper_row_110.loc[0, 'frequency'] - closest_lower_row_110.loc[0, 'frequency']) / (closest_upper_row_110.loc[0, 'budget'] - closest_lower_row_110.loc[0, 'budget'])) * (budget_110-closest_lower_row_110.loc[0, 'budget'])) + closest_lower_row_110.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_110_pred'] = (((closest_upper_row_110.loc[0, 'weekly_freq'] - closest_lower_row_110.loc[0, 'weekly_freq']) / (closest_upper_row_110.loc[0, 'budget'] - closest_lower_row_110.loc[0, 'budget'])) * (budget_110-closest_lower_row_110.loc[0, 'budget'])) + closest_lower_row_110.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_110_pred'] = budget_110 / df_append_sim.loc[count, 'rf_impression_110_pred'] * 1000


                        ############------------------Simulations for +_115 budget scenario------------------###################

                        budget_115 = df_append_sim.at[count, 'budget'] * 2.15


                        # Closest budget for +_115 budget
                        closest_budget_115 = closest(lst, budget_115)
                        df_append_sim.loc[count, 'budget_115'] = budget_115

                        # Fetch two rows for interpolate the budget values

                        if budget_115 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_115]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_115 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_115 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_115 >= budget_115:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_115]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_115 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_115 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_115]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_115 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_115 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_115'] = closest_upper_row_115.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_115'] = closest_lower_row_115.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_115'] = closest_upper_row_115.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_115'] = closest_lower_row_115.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_115'] = closest_upper_row_115.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_115'] = closest_lower_row_115.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_115'] = closest_upper_row_115.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_115'] = closest_lower_row_115.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_115'] = closest_upper_row_115.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_115'] = closest_lower_row_115.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_115'] = closest_upper_row_115.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_115'] = closest_lower_row_115.loc[0, 'weekly_freq']


                        #Interpolating values for +_115 budget

                        df_append_sim.loc[count, 'rf_impression_115_pred'] = (((closest_upper_row_115.loc[0, 'impression'] - closest_lower_row_115.loc[0, 'impression']) / (closest_upper_row_115.loc[0, 'budget'] - closest_lower_row_115.loc[0, 'budget'])) * (budget_115-closest_lower_row_115.loc[0, 'budget'])) + closest_lower_row_115.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_115_pred'] = (((closest_upper_row_115.loc[0, 'reach'] - closest_lower_row_115.loc[0, 'reach']) / (closest_upper_row_115.loc[0, 'budget'] - closest_lower_row_115.loc[0, 'budget'])) * (budget_115-closest_lower_row_115.loc[0, 'budget'])) + closest_lower_row_115.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_115_pred'] = (((closest_upper_row_115.loc[0, 'conversion'] - closest_lower_row_115.loc[0, 'conversion']) / (closest_upper_row_115.loc[0, 'budget'] - closest_lower_row_115.loc[0, 'budget'])) * (budget_115-closest_lower_row_115.loc[0, 'budget'])) + closest_lower_row_115.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_115_pred'] = (((closest_upper_row_115.loc[0, 'frequency'] - closest_lower_row_115.loc[0, 'frequency']) / (closest_upper_row_115.loc[0, 'budget'] - closest_lower_row_115.loc[0, 'budget'])) * (budget_115-closest_lower_row_115.loc[0, 'budget'])) + closest_lower_row_115.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_115_pred'] = (((closest_upper_row_115.loc[0, 'weekly_freq'] - closest_lower_row_115.loc[0, 'weekly_freq']) / (closest_upper_row_115.loc[0, 'budget'] - closest_lower_row_115.loc[0, 'budget'])) * (budget_115-closest_lower_row_115.loc[0, 'budget'])) + closest_lower_row_115.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_115_pred'] = budget_115 / df_append_sim.loc[count, 'rf_impression_115_pred'] * 1000


                        ############------------------Simulations for +_120 budget scenario------------------###################

                        budget_120 = df_append_sim.at[count, 'budget'] * 2.2


                        # Closest budget for +_120 budget
                        closest_budget_120 = closest(lst, budget_120)
                        df_append_sim.loc[count, 'budget_120'] = budget_120

                        # Fetch two rows for interpolate the budget values

                        if budget_120 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_120]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_120 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_120 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_120 >= budget_120:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_120]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_120 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_120 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_120]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_120 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_120 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_120'] = closest_upper_row_120.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_120'] = closest_lower_row_120.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_120'] = closest_upper_row_120.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_120'] = closest_lower_row_120.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_120'] = closest_upper_row_120.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_120'] = closest_lower_row_120.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_120'] = closest_upper_row_120.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_120'] = closest_lower_row_120.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_120'] = closest_upper_row_120.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_120'] = closest_lower_row_120.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_120'] = closest_upper_row_120.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_120'] = closest_lower_row_120.loc[0, 'weekly_freq']


                        #Interpolating values for +_120 budget

                        df_append_sim.loc[count, 'rf_impression_120_pred'] = (((closest_upper_row_120.loc[0, 'impression'] - closest_lower_row_120.loc[0, 'impression']) / (closest_upper_row_120.loc[0, 'budget'] - closest_lower_row_120.loc[0, 'budget'])) * (budget_120-closest_lower_row_120.loc[0, 'budget'])) + closest_lower_row_120.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_120_pred'] = (((closest_upper_row_120.loc[0, 'reach'] - closest_lower_row_120.loc[0, 'reach']) / (closest_upper_row_120.loc[0, 'budget'] - closest_lower_row_120.loc[0, 'budget'])) * (budget_120-closest_lower_row_120.loc[0, 'budget'])) + closest_lower_row_120.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_120_pred'] = (((closest_upper_row_120.loc[0, 'conversion'] - closest_lower_row_120.loc[0, 'conversion']) / (closest_upper_row_120.loc[0, 'budget'] - closest_lower_row_120.loc[0, 'budget'])) * (budget_120-closest_lower_row_120.loc[0, 'budget'])) + closest_lower_row_120.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_120_pred'] = (((closest_upper_row_120.loc[0, 'frequency'] - closest_lower_row_120.loc[0, 'frequency']) / (closest_upper_row_120.loc[0, 'budget'] - closest_lower_row_120.loc[0, 'budget'])) * (budget_120-closest_lower_row_120.loc[0, 'budget'])) + closest_lower_row_120.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_120_pred'] = (((closest_upper_row_120.loc[0, 'weekly_freq'] - closest_lower_row_120.loc[0, 'weekly_freq']) / (closest_upper_row_120.loc[0, 'budget'] - closest_lower_row_120.loc[0, 'budget'])) * (budget_120-closest_lower_row_120.loc[0, 'budget'])) + closest_lower_row_120.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_120_pred'] = budget_120 / df_append_sim.loc[count, 'rf_impression_120_pred'] * 1000


                        ############------------------Simulations for +_125 budget scenario------------------###################

                        budget_125 = df_append_sim.at[count, 'budget'] * 2.25


                        # Closest budget for +_125 budget
                        closest_budget_125 = closest(lst, budget_125)
                        df_append_sim.loc[count, 'budget_125'] = budget_125

                        # Fetch two rows for interpolate the budget values

                        if budget_125 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_125]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_125 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_125 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_125 >= budget_125:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_125]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_125 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_125 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_125]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_125 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_125 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_125'] = closest_upper_row_125.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_125'] = closest_lower_row_125.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_125'] = closest_upper_row_125.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_125'] = closest_lower_row_125.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_125'] = closest_upper_row_125.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_125'] = closest_lower_row_125.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_125'] = closest_upper_row_125.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_125'] = closest_lower_row_125.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_125'] = closest_upper_row_125.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_125'] = closest_lower_row_125.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_125'] = closest_upper_row_125.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_125'] = closest_lower_row_125.loc[0, 'weekly_freq']


                        #Interpolating values for +_125 budget

                        df_append_sim.loc[count, 'rf_impression_125_pred'] = (((closest_upper_row_125.loc[0, 'impression'] - closest_lower_row_125.loc[0, 'impression']) / (closest_upper_row_125.loc[0, 'budget'] - closest_lower_row_125.loc[0, 'budget'])) * (budget_125-closest_lower_row_125.loc[0, 'budget'])) + closest_lower_row_125.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_125_pred'] = (((closest_upper_row_125.loc[0, 'reach'] - closest_lower_row_125.loc[0, 'reach']) / (closest_upper_row_125.loc[0, 'budget'] - closest_lower_row_125.loc[0, 'budget'])) * (budget_125-closest_lower_row_125.loc[0, 'budget'])) + closest_lower_row_125.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_125_pred'] = (((closest_upper_row_125.loc[0, 'conversion'] - closest_lower_row_125.loc[0, 'conversion']) / (closest_upper_row_125.loc[0, 'budget'] - closest_lower_row_125.loc[0, 'budget'])) * (budget_125-closest_lower_row_125.loc[0, 'budget'])) + closest_lower_row_125.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_125_pred'] = (((closest_upper_row_125.loc[0, 'frequency'] - closest_lower_row_125.loc[0, 'frequency']) / (closest_upper_row_125.loc[0, 'budget'] - closest_lower_row_125.loc[0, 'budget'])) * (budget_125-closest_lower_row_125.loc[0, 'budget'])) + closest_lower_row_125.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_125_pred'] = (((closest_upper_row_125.loc[0, 'weekly_freq'] - closest_lower_row_125.loc[0, 'weekly_freq']) / (closest_upper_row_125.loc[0, 'budget'] - closest_lower_row_125.loc[0, 'budget'])) * (budget_125-closest_lower_row_125.loc[0, 'budget'])) + closest_lower_row_125.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_125_pred'] = budget_125 / df_append_sim.loc[count, 'rf_impression_125_pred'] * 1000


                        ############------------------Simulations for +_130 budget scenario------------------###################

                        budget_130 = df_append_sim.at[count, 'budget'] * 2.3


                        # Closest budget for +_130 budget
                        closest_budget_130 = closest(lst, budget_130)
                        df_append_sim.loc[count, 'budget_130'] = budget_130

                        # Fetch two rows for interpolate the budget values

                        if budget_130 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_130]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_130 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_130 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_130 >= budget_130:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_130]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_130 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_130 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_130]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_130 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_130 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_130'] = closest_upper_row_130.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_130'] = closest_lower_row_130.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_130'] = closest_upper_row_130.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_130'] = closest_lower_row_130.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_130'] = closest_upper_row_130.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_130'] = closest_lower_row_130.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_130'] = closest_upper_row_130.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_130'] = closest_lower_row_130.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_130'] = closest_upper_row_130.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_130'] = closest_lower_row_130.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_130'] = closest_upper_row_130.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_130'] = closest_lower_row_130.loc[0, 'weekly_freq']


                        #Interpolating values for +_130 budget

                        df_append_sim.loc[count, 'rf_impression_130_pred'] = (((closest_upper_row_130.loc[0, 'impression'] - closest_lower_row_130.loc[0, 'impression']) / (closest_upper_row_130.loc[0, 'budget'] - closest_lower_row_130.loc[0, 'budget'])) * (budget_130-closest_lower_row_130.loc[0, 'budget'])) + closest_lower_row_130.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_130_pred'] = (((closest_upper_row_130.loc[0, 'reach'] - closest_lower_row_130.loc[0, 'reach']) / (closest_upper_row_130.loc[0, 'budget'] - closest_lower_row_130.loc[0, 'budget'])) * (budget_130-closest_lower_row_130.loc[0, 'budget'])) + closest_lower_row_130.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_130_pred'] = (((closest_upper_row_130.loc[0, 'conversion'] - closest_lower_row_130.loc[0, 'conversion']) / (closest_upper_row_130.loc[0, 'budget'] - closest_lower_row_130.loc[0, 'budget'])) * (budget_130-closest_lower_row_130.loc[0, 'budget'])) + closest_lower_row_130.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_130_pred'] = (((closest_upper_row_130.loc[0, 'frequency'] - closest_lower_row_130.loc[0, 'frequency']) / (closest_upper_row_130.loc[0, 'budget'] - closest_lower_row_130.loc[0, 'budget'])) * (budget_130-closest_lower_row_130.loc[0, 'budget'])) + closest_lower_row_130.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_130_pred'] = (((closest_upper_row_130.loc[0, 'weekly_freq'] - closest_lower_row_130.loc[0, 'weekly_freq']) / (closest_upper_row_130.loc[0, 'budget'] - closest_lower_row_130.loc[0, 'budget'])) * (budget_130-closest_lower_row_130.loc[0, 'budget'])) + closest_lower_row_130.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_130_pred'] = budget_130 / df_append_sim.loc[count, 'rf_impression_130_pred'] * 1000


                        ############------------------Simulations for +_135 budget scenario------------------###################

                        budget_135 = df_append_sim.at[count, 'budget'] * 2.35


                        # Closest budget for +_135 budget
                        closest_budget_135 = closest(lst, budget_135)
                        df_append_sim.loc[count, 'budget_135'] = budget_135

                        # Fetch two rows for interpolate the budget values

                        if budget_135 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_135]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_135 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_135 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_135 >= budget_135:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_135]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_135 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_135 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_135]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_135 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_135 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_135'] = closest_upper_row_135.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_135'] = closest_lower_row_135.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_135'] = closest_upper_row_135.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_135'] = closest_lower_row_135.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_135'] = closest_upper_row_135.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_135'] = closest_lower_row_135.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_135'] = closest_upper_row_135.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_135'] = closest_lower_row_135.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_135'] = closest_upper_row_135.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_135'] = closest_lower_row_135.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_135'] = closest_upper_row_135.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_135'] = closest_lower_row_135.loc[0, 'weekly_freq']


                        #Interpolating values for +_135 budget

                        df_append_sim.loc[count, 'rf_impression_135_pred'] = (((closest_upper_row_135.loc[0, 'impression'] - closest_lower_row_135.loc[0, 'impression']) / (closest_upper_row_135.loc[0, 'budget'] - closest_lower_row_135.loc[0, 'budget'])) * (budget_135-closest_lower_row_135.loc[0, 'budget'])) + closest_lower_row_135.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_135_pred'] = (((closest_upper_row_135.loc[0, 'reach'] - closest_lower_row_135.loc[0, 'reach']) / (closest_upper_row_135.loc[0, 'budget'] - closest_lower_row_135.loc[0, 'budget'])) * (budget_135-closest_lower_row_135.loc[0, 'budget'])) + closest_lower_row_135.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_135_pred'] = (((closest_upper_row_135.loc[0, 'conversion'] - closest_lower_row_135.loc[0, 'conversion']) / (closest_upper_row_135.loc[0, 'budget'] - closest_lower_row_135.loc[0, 'budget'])) * (budget_135-closest_lower_row_135.loc[0, 'budget'])) + closest_lower_row_135.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_135_pred'] = (((closest_upper_row_135.loc[0, 'frequency'] - closest_lower_row_135.loc[0, 'frequency']) / (closest_upper_row_135.loc[0, 'budget'] - closest_lower_row_135.loc[0, 'budget'])) * (budget_135-closest_lower_row_135.loc[0, 'budget'])) + closest_lower_row_135.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_135_pred'] = (((closest_upper_row_135.loc[0, 'weekly_freq'] - closest_lower_row_135.loc[0, 'weekly_freq']) / (closest_upper_row_135.loc[0, 'budget'] - closest_lower_row_135.loc[0, 'budget'])) * (budget_135-closest_lower_row_135.loc[0, 'budget'])) + closest_lower_row_135.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_135_pred'] = budget_135 / df_append_sim.loc[count, 'rf_impression_135_pred'] * 1000


                        ############------------------Simulations for +_140 budget scenario------------------###################

                        budget_140 = df_append_sim.at[count, 'budget'] * 2.4


                        # Closest budget for +_140 budget
                        closest_budget_140 = closest(lst, budget_140)
                        df_append_sim.loc[count, 'budget_140'] = budget_140

                        # Fetch two rows for interpolate the budget values

                        if budget_140 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_140]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_140 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_140 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_140 >= budget_140:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_140]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_140 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_140 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_140]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_140 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_140 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_140'] = closest_upper_row_140.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_140'] = closest_lower_row_140.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_140'] = closest_upper_row_140.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_140'] = closest_lower_row_140.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_140'] = closest_upper_row_140.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_140'] = closest_lower_row_140.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_140'] = closest_upper_row_140.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_140'] = closest_lower_row_140.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_140'] = closest_upper_row_140.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_140'] = closest_lower_row_140.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_140'] = closest_upper_row_140.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_140'] = closest_lower_row_140.loc[0, 'weekly_freq']


                        #Interpolating values for +_140 budget

                        df_append_sim.loc[count, 'rf_impression_140_pred'] = (((closest_upper_row_140.loc[0, 'impression'] - closest_lower_row_140.loc[0, 'impression']) / (closest_upper_row_140.loc[0, 'budget'] - closest_lower_row_140.loc[0, 'budget'])) * (budget_140-closest_lower_row_140.loc[0, 'budget'])) + closest_lower_row_140.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_140_pred'] = (((closest_upper_row_140.loc[0, 'reach'] - closest_lower_row_140.loc[0, 'reach']) / (closest_upper_row_140.loc[0, 'budget'] - closest_lower_row_140.loc[0, 'budget'])) * (budget_140-closest_lower_row_140.loc[0, 'budget'])) + closest_lower_row_140.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_140_pred'] = (((closest_upper_row_140.loc[0, 'conversion'] - closest_lower_row_140.loc[0, 'conversion']) / (closest_upper_row_140.loc[0, 'budget'] - closest_lower_row_140.loc[0, 'budget'])) * (budget_140-closest_lower_row_140.loc[0, 'budget'])) + closest_lower_row_140.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_140_pred'] = (((closest_upper_row_140.loc[0, 'frequency'] - closest_lower_row_140.loc[0, 'frequency']) / (closest_upper_row_140.loc[0, 'budget'] - closest_lower_row_140.loc[0, 'budget'])) * (budget_140-closest_lower_row_140.loc[0, 'budget'])) + closest_lower_row_140.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_140_pred'] = (((closest_upper_row_140.loc[0, 'weekly_freq'] - closest_lower_row_140.loc[0, 'weekly_freq']) / (closest_upper_row_140.loc[0, 'budget'] - closest_lower_row_140.loc[0, 'budget'])) * (budget_140-closest_lower_row_140.loc[0, 'budget'])) + closest_lower_row_140.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_140_pred'] = budget_140 / df_append_sim.loc[count, 'rf_impression_140_pred'] * 1000


                        ############------------------Simulations for +_145 budget scenario------------------###################

                        budget_145 = df_append_sim.at[count, 'budget'] * 2.45


                        # Closest budget for +_145 budget
                        closest_budget_145 = closest(lst, budget_145)
                        df_append_sim.loc[count, 'budget_145'] = budget_145

                        # Fetch two rows for interpolate the budget values

                        if budget_145 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_145]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_145 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_145 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_145 >= budget_145:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_145]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_145 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_145 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_145]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_145 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_145 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_145'] = closest_upper_row_145.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_145'] = closest_lower_row_145.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_145'] = closest_upper_row_145.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_145'] = closest_lower_row_145.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_145'] = closest_upper_row_145.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_145'] = closest_lower_row_145.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_145'] = closest_upper_row_145.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_145'] = closest_lower_row_145.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_145'] = closest_upper_row_145.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_145'] = closest_lower_row_145.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_145'] = closest_upper_row_145.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_145'] = closest_lower_row_145.loc[0, 'weekly_freq']


                        #Interpolating values for +_145 budget

                        df_append_sim.loc[count, 'rf_impression_145_pred'] = (((closest_upper_row_145.loc[0, 'impression'] - closest_lower_row_145.loc[0, 'impression']) / (closest_upper_row_145.loc[0, 'budget'] - closest_lower_row_145.loc[0, 'budget'])) * (budget_145-closest_lower_row_145.loc[0, 'budget'])) + closest_lower_row_145.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_145_pred'] = (((closest_upper_row_145.loc[0, 'reach'] - closest_lower_row_145.loc[0, 'reach']) / (closest_upper_row_145.loc[0, 'budget'] - closest_lower_row_145.loc[0, 'budget'])) * (budget_145-closest_lower_row_145.loc[0, 'budget'])) + closest_lower_row_145.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_145_pred'] = (((closest_upper_row_145.loc[0, 'conversion'] - closest_lower_row_145.loc[0, 'conversion']) / (closest_upper_row_145.loc[0, 'budget'] - closest_lower_row_145.loc[0, 'budget'])) * (budget_145-closest_lower_row_145.loc[0, 'budget'])) + closest_lower_row_145.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_145_pred'] = (((closest_upper_row_145.loc[0, 'frequency'] - closest_lower_row_145.loc[0, 'frequency']) / (closest_upper_row_145.loc[0, 'budget'] - closest_lower_row_145.loc[0, 'budget'])) * (budget_145-closest_lower_row_145.loc[0, 'budget'])) + closest_lower_row_145.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_145_pred'] = (((closest_upper_row_145.loc[0, 'weekly_freq'] - closest_lower_row_145.loc[0, 'weekly_freq']) / (closest_upper_row_145.loc[0, 'budget'] - closest_lower_row_145.loc[0, 'budget'])) * (budget_145-closest_lower_row_145.loc[0, 'budget'])) + closest_lower_row_145.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_145_pred'] = budget_145 / df_append_sim.loc[count, 'rf_impression_145_pred'] * 1000


                        ############------------------Simulations for +_150 budget scenario------------------###################

                        budget_150 = df_append_sim.at[count, 'budget'] * 2.5


                        # Closest budget for +_150 budget
                        closest_budget_150 = closest(lst, budget_150)
                        df_append_sim.loc[count, 'budget_150'] = budget_150

                        # Fetch two rows for interpolate the budget values

                        if budget_150 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_150]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_150 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_150 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_150 >= budget_150:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_150]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_150 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_150 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_150]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_150 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_150 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_150'] = closest_upper_row_150.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_150'] = closest_lower_row_150.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_150'] = closest_upper_row_150.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_150'] = closest_lower_row_150.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_150'] = closest_upper_row_150.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_150'] = closest_lower_row_150.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_150'] = closest_upper_row_150.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_150'] = closest_lower_row_150.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_150'] = closest_upper_row_150.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_150'] = closest_lower_row_150.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_150'] = closest_upper_row_150.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_150'] = closest_lower_row_150.loc[0, 'weekly_freq']


                        #Interpolating values for +_150 budget

                        df_append_sim.loc[count, 'rf_impression_150_pred'] = (((closest_upper_row_150.loc[0, 'impression'] - closest_lower_row_150.loc[0, 'impression']) / (closest_upper_row_150.loc[0, 'budget'] - closest_lower_row_150.loc[0, 'budget'])) * (budget_150-closest_lower_row_150.loc[0, 'budget'])) + closest_lower_row_150.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_150_pred'] = (((closest_upper_row_150.loc[0, 'reach'] - closest_lower_row_150.loc[0, 'reach']) / (closest_upper_row_150.loc[0, 'budget'] - closest_lower_row_150.loc[0, 'budget'])) * (budget_150-closest_lower_row_150.loc[0, 'budget'])) + closest_lower_row_150.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_150_pred'] = (((closest_upper_row_150.loc[0, 'conversion'] - closest_lower_row_150.loc[0, 'conversion']) / (closest_upper_row_150.loc[0, 'budget'] - closest_lower_row_150.loc[0, 'budget'])) * (budget_150-closest_lower_row_150.loc[0, 'budget'])) + closest_lower_row_150.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_150_pred'] = (((closest_upper_row_150.loc[0, 'frequency'] - closest_lower_row_150.loc[0, 'frequency']) / (closest_upper_row_150.loc[0, 'budget'] - closest_lower_row_150.loc[0, 'budget'])) * (budget_150-closest_lower_row_150.loc[0, 'budget'])) + closest_lower_row_150.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_150_pred'] = (((closest_upper_row_150.loc[0, 'weekly_freq'] - closest_lower_row_150.loc[0, 'weekly_freq']) / (closest_upper_row_150.loc[0, 'budget'] - closest_lower_row_150.loc[0, 'budget'])) * (budget_150-closest_lower_row_150.loc[0, 'budget'])) + closest_lower_row_150.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_150_pred'] = budget_150 / df_append_sim.loc[count, 'rf_impression_150_pred'] * 1000


                                        ############------------------Simulations for +_155 budget scenario------------------###################

                        budget_155 = df_append_sim.at[count, 'budget'] * 2.55


                        # Closest budget for +_155 budget
                        closest_budget_155 = closest(lst, budget_155)
                        df_append_sim.loc[count, 'budget_155'] = budget_155

                        # Fetch two rows for interpolate the budget values

                        if budget_155 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_155]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_155 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_155 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_155 >= budget_155:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_155]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_155 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_155 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_155]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_155 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_155 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_155'] = closest_upper_row_155.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_155'] = closest_lower_row_155.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_155'] = closest_upper_row_155.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_155'] = closest_lower_row_155.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_155'] = closest_upper_row_155.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_155'] = closest_lower_row_155.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_155'] = closest_upper_row_155.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_155'] = closest_lower_row_155.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_155'] = closest_upper_row_155.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_155'] = closest_lower_row_155.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_155'] = closest_upper_row_155.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_155'] = closest_lower_row_155.loc[0, 'weekly_freq']


                        #Interpolating values for +_155 budget

                        df_append_sim.loc[count, 'rf_impression_155_pred'] = (((closest_upper_row_155.loc[0, 'impression'] - closest_lower_row_155.loc[0, 'impression']) / (closest_upper_row_155.loc[0, 'budget'] - closest_lower_row_155.loc[0, 'budget'])) * (budget_155-closest_lower_row_155.loc[0, 'budget'])) + closest_lower_row_155.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_155_pred'] = (((closest_upper_row_155.loc[0, 'reach'] - closest_lower_row_155.loc[0, 'reach']) / (closest_upper_row_155.loc[0, 'budget'] - closest_lower_row_155.loc[0, 'budget'])) * (budget_155-closest_lower_row_155.loc[0, 'budget'])) + closest_lower_row_155.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_155_pred'] = (((closest_upper_row_155.loc[0, 'conversion'] - closest_lower_row_155.loc[0, 'conversion']) / (closest_upper_row_155.loc[0, 'budget'] - closest_lower_row_155.loc[0, 'budget'])) * (budget_155-closest_lower_row_155.loc[0, 'budget'])) + closest_lower_row_155.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_155_pred'] = (((closest_upper_row_155.loc[0, 'frequency'] - closest_lower_row_155.loc[0, 'frequency']) / (closest_upper_row_155.loc[0, 'budget'] - closest_lower_row_155.loc[0, 'budget'])) * (budget_155-closest_lower_row_155.loc[0, 'budget'])) + closest_lower_row_155.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_155_pred'] = (((closest_upper_row_155.loc[0, 'weekly_freq'] - closest_lower_row_155.loc[0, 'weekly_freq']) / (closest_upper_row_155.loc[0, 'budget'] - closest_lower_row_155.loc[0, 'budget'])) * (budget_155-closest_lower_row_155.loc[0, 'budget'])) + closest_lower_row_155.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_155_pred'] = budget_155 / df_append_sim.loc[count, 'rf_impression_155_pred'] * 1000


                        ############------------------Simulations for +_160 budget scenario------------------###################

                        budget_160 = df_append_sim.at[count, 'budget'] * 2.6


                        # Closest budget for +_160 budget
                        closest_budget_160 = closest(lst, budget_160)
                        df_append_sim.loc[count, 'budget_160'] = budget_160

                        # Fetch two rows for interpolate the budget values

                        if budget_160 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_160]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_160 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_160 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_160 >= budget_160:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_160]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_160 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_160 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_160]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_160 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_160 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_160'] = closest_upper_row_160.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_160'] = closest_lower_row_160.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_160'] = closest_upper_row_160.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_160'] = closest_lower_row_160.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_160'] = closest_upper_row_160.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_160'] = closest_lower_row_160.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_160'] = closest_upper_row_160.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_160'] = closest_lower_row_160.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_160'] = closest_upper_row_160.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_160'] = closest_lower_row_160.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_160'] = closest_upper_row_160.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_160'] = closest_lower_row_160.loc[0, 'weekly_freq']


                        #Interpolating values for +_160 budget

                        df_append_sim.loc[count, 'rf_impression_160_pred'] = (((closest_upper_row_160.loc[0, 'impression'] - closest_lower_row_160.loc[0, 'impression']) / (closest_upper_row_160.loc[0, 'budget'] - closest_lower_row_160.loc[0, 'budget'])) * (budget_160-closest_lower_row_160.loc[0, 'budget'])) + closest_lower_row_160.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_160_pred'] = (((closest_upper_row_160.loc[0, 'reach'] - closest_lower_row_160.loc[0, 'reach']) / (closest_upper_row_160.loc[0, 'budget'] - closest_lower_row_160.loc[0, 'budget'])) * (budget_160-closest_lower_row_160.loc[0, 'budget'])) + closest_lower_row_160.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_160_pred'] = (((closest_upper_row_160.loc[0, 'conversion'] - closest_lower_row_160.loc[0, 'conversion']) / (closest_upper_row_160.loc[0, 'budget'] - closest_lower_row_160.loc[0, 'budget'])) * (budget_160-closest_lower_row_160.loc[0, 'budget'])) + closest_lower_row_160.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_160_pred'] = (((closest_upper_row_160.loc[0, 'frequency'] - closest_lower_row_160.loc[0, 'frequency']) / (closest_upper_row_160.loc[0, 'budget'] - closest_lower_row_160.loc[0, 'budget'])) * (budget_160-closest_lower_row_160.loc[0, 'budget'])) + closest_lower_row_160.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_160_pred'] = (((closest_upper_row_160.loc[0, 'weekly_freq'] - closest_lower_row_160.loc[0, 'weekly_freq']) / (closest_upper_row_160.loc[0, 'budget'] - closest_lower_row_160.loc[0, 'budget'])) * (budget_160-closest_lower_row_160.loc[0, 'budget'])) + closest_lower_row_160.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_160_pred'] = budget_160 / df_append_sim.loc[count, 'rf_impression_160_pred'] * 1000


                        ############------------------Simulations for +_165 budget scenario------------------###################

                        budget_165 = df_append_sim.at[count, 'budget'] * 2.65


                        # Closest budget for +_165 budget
                        closest_budget_165 = closest(lst, budget_165)
                        df_append_sim.loc[count, 'budget_165'] = budget_165

                        # Fetch two rows for interpolate the budget values

                        if budget_165 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_165]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_165 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_165 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_165 >= budget_165:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_165]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_165 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_165 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_165]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_165 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_165 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_165'] = closest_upper_row_165.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_165'] = closest_lower_row_165.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_165'] = closest_upper_row_165.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_165'] = closest_lower_row_165.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_165'] = closest_upper_row_165.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_165'] = closest_lower_row_165.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_165'] = closest_upper_row_165.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_165'] = closest_lower_row_165.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_165'] = closest_upper_row_165.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_165'] = closest_lower_row_165.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_165'] = closest_upper_row_165.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_165'] = closest_lower_row_165.loc[0, 'weekly_freq']


                        #Interpolating values for +_165 budget

                        df_append_sim.loc[count, 'rf_impression_165_pred'] = (((closest_upper_row_165.loc[0, 'impression'] - closest_lower_row_165.loc[0, 'impression']) / (closest_upper_row_165.loc[0, 'budget'] - closest_lower_row_165.loc[0, 'budget'])) * (budget_165-closest_lower_row_165.loc[0, 'budget'])) + closest_lower_row_165.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_165_pred'] = (((closest_upper_row_165.loc[0, 'reach'] - closest_lower_row_165.loc[0, 'reach']) / (closest_upper_row_165.loc[0, 'budget'] - closest_lower_row_165.loc[0, 'budget'])) * (budget_165-closest_lower_row_165.loc[0, 'budget'])) + closest_lower_row_165.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_165_pred'] = (((closest_upper_row_165.loc[0, 'conversion'] - closest_lower_row_165.loc[0, 'conversion']) / (closest_upper_row_165.loc[0, 'budget'] - closest_lower_row_165.loc[0, 'budget'])) * (budget_165-closest_lower_row_165.loc[0, 'budget'])) + closest_lower_row_165.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_165_pred'] = (((closest_upper_row_165.loc[0, 'frequency'] - closest_lower_row_165.loc[0, 'frequency']) / (closest_upper_row_165.loc[0, 'budget'] - closest_lower_row_165.loc[0, 'budget'])) * (budget_165-closest_lower_row_165.loc[0, 'budget'])) + closest_lower_row_165.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_165_pred'] = (((closest_upper_row_165.loc[0, 'weekly_freq'] - closest_lower_row_165.loc[0, 'weekly_freq']) / (closest_upper_row_165.loc[0, 'budget'] - closest_lower_row_165.loc[0, 'budget'])) * (budget_165-closest_lower_row_165.loc[0, 'budget'])) + closest_lower_row_165.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_165_pred'] = budget_165 / df_append_sim.loc[count, 'rf_impression_165_pred'] * 1000


                        ############------------------Simulations for +_170 budget scenario------------------###################

                        budget_170 = df_append_sim.at[count, 'budget'] * 2.70

                        # Closest budget for +_170 budget
                        closest_budget_170 = closest(lst, budget_170)
                        df_append_sim.loc[count, 'budget_170'] = budget_170

                        # Fetch two rows for interpolate the budget values

                        if budget_170 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_170]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_170 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_170 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_170 >= budget_170:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_170]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_170 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_170 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_170]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_170 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_170 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_170'] = closest_upper_row_170.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_170'] = closest_lower_row_170.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_170'] = closest_upper_row_170.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_170'] = closest_lower_row_170.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_170'] = closest_upper_row_170.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_170'] = closest_lower_row_170.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_170'] = closest_upper_row_170.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_170'] = closest_lower_row_170.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_170'] = closest_upper_row_170.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_170'] = closest_lower_row_170.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_170'] = closest_upper_row_170.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_170'] = closest_lower_row_170.loc[0, 'weekly_freq']


                        #Interpolating values for +_170 budget

                        df_append_sim.loc[count, 'rf_impression_170_pred'] = (((closest_upper_row_170.loc[0, 'impression'] - closest_lower_row_170.loc[0, 'impression']) / (closest_upper_row_170.loc[0, 'budget'] - closest_lower_row_170.loc[0, 'budget'])) * (budget_170-closest_lower_row_170.loc[0, 'budget'])) + closest_lower_row_170.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_170_pred'] = (((closest_upper_row_170.loc[0, 'reach'] - closest_lower_row_170.loc[0, 'reach']) / (closest_upper_row_170.loc[0, 'budget'] - closest_lower_row_170.loc[0, 'budget'])) * (budget_170-closest_lower_row_170.loc[0, 'budget'])) + closest_lower_row_170.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_170_pred'] = (((closest_upper_row_170.loc[0, 'conversion'] - closest_lower_row_170.loc[0, 'conversion']) / (closest_upper_row_170.loc[0, 'budget'] - closest_lower_row_170.loc[0, 'budget'])) * (budget_170-closest_lower_row_170.loc[0, 'budget'])) + closest_lower_row_170.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_170_pred'] = (((closest_upper_row_170.loc[0, 'frequency'] - closest_lower_row_170.loc[0, 'frequency']) / (closest_upper_row_170.loc[0, 'budget'] - closest_lower_row_170.loc[0, 'budget'])) * (budget_170-closest_lower_row_170.loc[0, 'budget'])) + closest_lower_row_170.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_170_pred'] = (((closest_upper_row_170.loc[0, 'weekly_freq'] - closest_lower_row_170.loc[0, 'weekly_freq']) / (closest_upper_row_170.loc[0, 'budget'] - closest_lower_row_170.loc[0, 'budget'])) * (budget_170-closest_lower_row_170.loc[0, 'budget'])) + closest_lower_row_170.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_170_pred'] = budget_170 / df_append_sim.loc[count, 'rf_impression_170_pred'] * 1000


                        ############------------------Simulations for +_175 budget scenario------------------###################

                        budget_175 = df_append_sim.at[count, 'budget'] * 2.75

                        # Closest budget for +_175 budget
                        closest_budget_175 = closest(lst, budget_175)
                        df_append_sim.loc[count, 'budget_175'] = budget_175

                        # Fetch two rows for interpolate the budget values

                        if budget_175 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_175]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_175 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_175 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_175 >= budget_175:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_175]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_175 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_175 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_175]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_175 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_175 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_175'] = closest_upper_row_175.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_175'] = closest_lower_row_175.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_175'] = closest_upper_row_175.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_175'] = closest_lower_row_175.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_175'] = closest_upper_row_175.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_175'] = closest_lower_row_175.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_175'] = closest_upper_row_175.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_175'] = closest_lower_row_175.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_175'] = closest_upper_row_175.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_175'] = closest_lower_row_175.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_175'] = closest_upper_row_175.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_175'] = closest_lower_row_175.loc[0, 'weekly_freq']


                        #Interpolating values for +_175 budget

                        df_append_sim.loc[count, 'rf_impression_175_pred'] = (((closest_upper_row_175.loc[0, 'impression'] - closest_lower_row_175.loc[0, 'impression']) / (closest_upper_row_175.loc[0, 'budget'] - closest_lower_row_175.loc[0, 'budget'])) * (budget_175-closest_lower_row_175.loc[0, 'budget'])) + closest_lower_row_175.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_175_pred'] = (((closest_upper_row_175.loc[0, 'reach'] - closest_lower_row_175.loc[0, 'reach']) / (closest_upper_row_175.loc[0, 'budget'] - closest_lower_row_175.loc[0, 'budget'])) * (budget_175-closest_lower_row_175.loc[0, 'budget'])) + closest_lower_row_175.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_175_pred'] = (((closest_upper_row_175.loc[0, 'conversion'] - closest_lower_row_175.loc[0, 'conversion']) / (closest_upper_row_175.loc[0, 'budget'] - closest_lower_row_175.loc[0, 'budget'])) * (budget_175-closest_lower_row_175.loc[0, 'budget'])) + closest_lower_row_175.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_175_pred'] = (((closest_upper_row_175.loc[0, 'frequency'] - closest_lower_row_175.loc[0, 'frequency']) / (closest_upper_row_175.loc[0, 'budget'] - closest_lower_row_175.loc[0, 'budget'])) * (budget_175-closest_lower_row_175.loc[0, 'budget'])) + closest_lower_row_175.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_175_pred'] = (((closest_upper_row_175.loc[0, 'weekly_freq'] - closest_lower_row_175.loc[0, 'weekly_freq']) / (closest_upper_row_175.loc[0, 'budget'] - closest_lower_row_175.loc[0, 'budget'])) * (budget_175-closest_lower_row_175.loc[0, 'budget'])) + closest_lower_row_175.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_175_pred'] = budget_175 / df_append_sim.loc[count, 'rf_impression_175_pred'] * 1000





                        ############------------------Simulations for +_180 budget scenario------------------###################

                        budget_180 = df_append_sim.at[count, 'budget'] * 2.8

                        # Closest budget for +_180 budget
                        closest_budget_180 = closest(lst, budget_180)
                        df_append_sim.loc[count, 'budget_180'] = budget_180

                        # Fetch two rows for interpolate the budget values

                        if budget_180 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_180]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_180 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_180 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_180 >= budget_180:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_180]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_180 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_180 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_180]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_180 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_180 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_180'] = closest_upper_row_180.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_180'] = closest_lower_row_180.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_180'] = closest_upper_row_180.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_180'] = closest_lower_row_180.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_180'] = closest_upper_row_180.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_180'] = closest_lower_row_180.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_180'] = closest_upper_row_180.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_180'] = closest_lower_row_180.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_180'] = closest_upper_row_180.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_180'] = closest_lower_row_180.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_180'] = closest_upper_row_180.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_180'] = closest_lower_row_180.loc[0, 'weekly_freq']


                        #Interpolating values for +_180 budget

                        df_append_sim.loc[count, 'rf_impression_180_pred'] = (((closest_upper_row_180.loc[0, 'impression'] - closest_lower_row_180.loc[0, 'impression']) / (closest_upper_row_180.loc[0, 'budget'] - closest_lower_row_180.loc[0, 'budget'])) * (budget_180-closest_lower_row_180.loc[0, 'budget'])) + closest_lower_row_180.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_180_pred'] = (((closest_upper_row_180.loc[0, 'reach'] - closest_lower_row_180.loc[0, 'reach']) / (closest_upper_row_180.loc[0, 'budget'] - closest_lower_row_180.loc[0, 'budget'])) * (budget_180-closest_lower_row_180.loc[0, 'budget'])) + closest_lower_row_180.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_180_pred'] = (((closest_upper_row_180.loc[0, 'conversion'] - closest_lower_row_180.loc[0, 'conversion']) / (closest_upper_row_180.loc[0, 'budget'] - closest_lower_row_180.loc[0, 'budget'])) * (budget_180-closest_lower_row_180.loc[0, 'budget'])) + closest_lower_row_180.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_180_pred'] = (((closest_upper_row_180.loc[0, 'frequency'] - closest_lower_row_180.loc[0, 'frequency']) / (closest_upper_row_180.loc[0, 'budget'] - closest_lower_row_180.loc[0, 'budget'])) * (budget_180-closest_lower_row_180.loc[0, 'budget'])) + closest_lower_row_180.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_180_pred'] = (((closest_upper_row_180.loc[0, 'weekly_freq'] - closest_lower_row_180.loc[0, 'weekly_freq']) / (closest_upper_row_180.loc[0, 'budget'] - closest_lower_row_180.loc[0, 'budget'])) * (budget_180-closest_lower_row_180.loc[0, 'budget'])) + closest_lower_row_180.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_180_pred'] = budget_180 / df_append_sim.loc[count, 'rf_impression_180_pred'] * 1000



                        ############------------------Simulations for +_185 budget scenario------------------###################

                        budget_185 = df_append_sim.at[count, 'budget'] * 2.85

                        # Closest budget for +_185 budget
                        closest_budget_185 = closest(lst, budget_185)
                        df_append_sim.loc[count, 'budget_185'] = budget_185

                        # Fetch two rows for interpolate the budget values

                        if budget_185 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_185]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_185 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_185 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_185 >= budget_185:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_185]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_185 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_185 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_185]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_185 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_185 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_185'] = closest_upper_row_185.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_185'] = closest_lower_row_185.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_185'] = closest_upper_row_185.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_185'] = closest_lower_row_185.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_185'] = closest_upper_row_185.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_185'] = closest_lower_row_185.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_185'] = closest_upper_row_185.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_185'] = closest_lower_row_185.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_185'] = closest_upper_row_185.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_185'] = closest_lower_row_185.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_185'] = closest_upper_row_185.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_185'] = closest_lower_row_185.loc[0, 'weekly_freq']


                        #Interpolating values for +_185 budget

                        df_append_sim.loc[count, 'rf_impression_185_pred'] = (((closest_upper_row_185.loc[0, 'impression'] - closest_lower_row_185.loc[0, 'impression']) / (closest_upper_row_185.loc[0, 'budget'] - closest_lower_row_185.loc[0, 'budget'])) * (budget_185-closest_lower_row_185.loc[0, 'budget'])) + closest_lower_row_185.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_185_pred'] = (((closest_upper_row_185.loc[0, 'reach'] - closest_lower_row_185.loc[0, 'reach']) / (closest_upper_row_185.loc[0, 'budget'] - closest_lower_row_185.loc[0, 'budget'])) * (budget_185-closest_lower_row_185.loc[0, 'budget'])) + closest_lower_row_185.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_185_pred'] = (((closest_upper_row_185.loc[0, 'conversion'] - closest_lower_row_185.loc[0, 'conversion']) / (closest_upper_row_185.loc[0, 'budget'] - closest_lower_row_185.loc[0, 'budget'])) * (budget_185-closest_lower_row_185.loc[0, 'budget'])) + closest_lower_row_185.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_185_pred'] = (((closest_upper_row_185.loc[0, 'frequency'] - closest_lower_row_185.loc[0, 'frequency']) / (closest_upper_row_185.loc[0, 'budget'] - closest_lower_row_185.loc[0, 'budget'])) * (budget_185-closest_lower_row_185.loc[0, 'budget'])) + closest_lower_row_185.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_185_pred'] = (((closest_upper_row_185.loc[0, 'weekly_freq'] - closest_lower_row_185.loc[0, 'weekly_freq']) / (closest_upper_row_185.loc[0, 'budget'] - closest_lower_row_185.loc[0, 'budget'])) * (budget_185-closest_lower_row_185.loc[0, 'budget'])) + closest_lower_row_185.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_185_pred'] = budget_185 / df_append_sim.loc[count, 'rf_impression_185_pred'] * 1000



                        ############------------------Simulations for +_190 budget scenario------------------###################

                        budget_190 = df_append_sim.at[count, 'budget'] * 2.9

                        # Closest budget for +_190 budget
                        closest_budget_190 = closest(lst, budget_190)
                        df_append_sim.loc[count, 'budget_190'] = budget_190

                        # Fetch two rows for interpolate the budget values

                        if budget_190 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_190]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_190 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_190 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_190 >= budget_190:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_190]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_190 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_190 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_190]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_190 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_190 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_190'] = closest_upper_row_190.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_190'] = closest_lower_row_190.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_190'] = closest_upper_row_190.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_190'] = closest_lower_row_190.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_190'] = closest_upper_row_190.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_190'] = closest_lower_row_190.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_190'] = closest_upper_row_190.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_190'] = closest_lower_row_190.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_190'] = closest_upper_row_190.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_190'] = closest_lower_row_190.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_190'] = closest_upper_row_190.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_190'] = closest_lower_row_190.loc[0, 'weekly_freq']


                        #Interpolating values for +_190 budget

                        df_append_sim.loc[count, 'rf_impression_190_pred'] = (((closest_upper_row_190.loc[0, 'impression'] - closest_lower_row_190.loc[0, 'impression']) / (closest_upper_row_190.loc[0, 'budget'] - closest_lower_row_190.loc[0, 'budget'])) * (budget_190-closest_lower_row_190.loc[0, 'budget'])) + closest_lower_row_190.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_190_pred'] = (((closest_upper_row_190.loc[0, 'reach'] - closest_lower_row_190.loc[0, 'reach']) / (closest_upper_row_190.loc[0, 'budget'] - closest_lower_row_190.loc[0, 'budget'])) * (budget_190-closest_lower_row_190.loc[0, 'budget'])) + closest_lower_row_190.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_190_pred'] = (((closest_upper_row_190.loc[0, 'conversion'] - closest_lower_row_190.loc[0, 'conversion']) / (closest_upper_row_190.loc[0, 'budget'] - closest_lower_row_190.loc[0, 'budget'])) * (budget_190-closest_lower_row_190.loc[0, 'budget'])) + closest_lower_row_190.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_190_pred'] = (((closest_upper_row_190.loc[0, 'frequency'] - closest_lower_row_190.loc[0, 'frequency']) / (closest_upper_row_190.loc[0, 'budget'] - closest_lower_row_190.loc[0, 'budget'])) * (budget_190-closest_lower_row_190.loc[0, 'budget'])) + closest_lower_row_190.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_190_pred'] = (((closest_upper_row_190.loc[0, 'weekly_freq'] - closest_lower_row_190.loc[0, 'weekly_freq']) / (closest_upper_row_190.loc[0, 'budget'] - closest_lower_row_190.loc[0, 'budget'])) * (budget_190-closest_lower_row_190.loc[0, 'budget'])) + closest_lower_row_190.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_190_pred'] = budget_190 / df_append_sim.loc[count, 'rf_impression_190_pred'] * 1000



                        ############------------------Simulations for +_195 budget scenario------------------###################

                        budget_195 = df_append_sim.at[count, 'budget'] * 2.95

                        # Closest budget for +_195 budget
                        closest_budget_195 = closest(lst, budget_195)
                        df_append_sim.loc[count, 'budget_195'] = budget_195

                        # Fetch two rows for interpolate the budget values

                        if budget_195 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_195]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_195 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_195 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_195 >= budget_195:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_195]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_195 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_195 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_195]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_195 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_195 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_195'] = closest_upper_row_195.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_195'] = closest_lower_row_195.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_195'] = closest_upper_row_195.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_195'] = closest_lower_row_195.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_195'] = closest_upper_row_195.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_195'] = closest_lower_row_195.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_195'] = closest_upper_row_195.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_195'] = closest_lower_row_195.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_195'] = closest_upper_row_195.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_195'] = closest_lower_row_195.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_195'] = closest_upper_row_195.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_195'] = closest_lower_row_195.loc[0, 'weekly_freq']


                        #Interpolating values for +_195 budget

                        df_append_sim.loc[count, 'rf_impression_195_pred'] = (((closest_upper_row_195.loc[0, 'impression'] - closest_lower_row_195.loc[0, 'impression']) / (closest_upper_row_195.loc[0, 'budget'] - closest_lower_row_195.loc[0, 'budget'])) * (budget_195-closest_lower_row_195.loc[0, 'budget'])) + closest_lower_row_195.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_195_pred'] = (((closest_upper_row_195.loc[0, 'reach'] - closest_lower_row_195.loc[0, 'reach']) / (closest_upper_row_195.loc[0, 'budget'] - closest_lower_row_195.loc[0, 'budget'])) * (budget_195-closest_lower_row_195.loc[0, 'budget'])) + closest_lower_row_195.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_195_pred'] = (((closest_upper_row_195.loc[0, 'conversion'] - closest_lower_row_195.loc[0, 'conversion']) / (closest_upper_row_195.loc[0, 'budget'] - closest_lower_row_195.loc[0, 'budget'])) * (budget_195-closest_lower_row_195.loc[0, 'budget'])) + closest_lower_row_195.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_195_pred'] = (((closest_upper_row_195.loc[0, 'frequency'] - closest_lower_row_195.loc[0, 'frequency']) / (closest_upper_row_195.loc[0, 'budget'] - closest_lower_row_195.loc[0, 'budget'])) * (budget_195-closest_lower_row_195.loc[0, 'budget'])) + closest_lower_row_195.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_195_pred'] = (((closest_upper_row_195.loc[0, 'weekly_freq'] - closest_lower_row_195.loc[0, 'weekly_freq']) / (closest_upper_row_195.loc[0, 'budget'] - closest_lower_row_195.loc[0, 'budget'])) * (budget_195-closest_lower_row_195.loc[0, 'budget'])) + closest_lower_row_195.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_195_pred'] = budget_195 / df_append_sim.loc[count, 'rf_impression_195_pred'] * 1000



                        ############------------------Simulations for +_200 budget scenario------------------###################

                        budget_200 = df_append_sim.at[count, 'budget'] * 3

                        # Closest budget for +_200 budget
                        closest_budget_200 = closest(lst, budget_200)
                        df_append_sim.loc[count, 'budget_200'] = budget_200

                        # Fetch two rows for interpolate the budget values

                        if budget_200 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_200]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_200 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_200 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_200 >= budget_200:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_200]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_200 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_200 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_200]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_200 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_200 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_200'] = closest_upper_row_200.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_200'] = closest_lower_row_200.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_200'] = closest_upper_row_200.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_200'] = closest_lower_row_200.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_200'] = closest_upper_row_200.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_200'] = closest_lower_row_200.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_200'] = closest_upper_row_200.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_200'] = closest_lower_row_200.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_200'] = closest_upper_row_200.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_200'] = closest_lower_row_200.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_200'] = closest_upper_row_200.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_200'] = closest_lower_row_200.loc[0, 'weekly_freq']


                        #Interpolating values for +_200 budget

                        df_append_sim.loc[count, 'rf_impression_200_pred'] = (((closest_upper_row_200.loc[0, 'impression'] - closest_lower_row_200.loc[0, 'impression']) / (closest_upper_row_200.loc[0, 'budget'] - closest_lower_row_200.loc[0, 'budget'])) * (budget_200-closest_lower_row_200.loc[0, 'budget'])) + closest_lower_row_200.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_200_pred'] = (((closest_upper_row_200.loc[0, 'reach'] - closest_lower_row_200.loc[0, 'reach']) / (closest_upper_row_200.loc[0, 'budget'] - closest_lower_row_200.loc[0, 'budget'])) * (budget_200-closest_lower_row_200.loc[0, 'budget'])) + closest_lower_row_200.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_200_pred'] = (((closest_upper_row_200.loc[0, 'conversion'] - closest_lower_row_200.loc[0, 'conversion']) / (closest_upper_row_200.loc[0, 'budget'] - closest_lower_row_200.loc[0, 'budget'])) * (budget_200-closest_lower_row_200.loc[0, 'budget'])) + closest_lower_row_200.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_200_pred'] = (((closest_upper_row_200.loc[0, 'frequency'] - closest_lower_row_200.loc[0, 'frequency']) / (closest_upper_row_200.loc[0, 'budget'] - closest_lower_row_200.loc[0, 'budget'])) * (budget_200-closest_lower_row_200.loc[0, 'budget'])) + closest_lower_row_200.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_200_pred'] = (((closest_upper_row_200.loc[0, 'weekly_freq'] - closest_lower_row_200.loc[0, 'weekly_freq']) / (closest_upper_row_200.loc[0, 'budget'] - closest_lower_row_200.loc[0, 'budget'])) * (budget_200-closest_lower_row_200.loc[0, 'budget'])) + closest_lower_row_200.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_200_pred'] = budget_200 / df_append_sim.loc[count, 'rf_impression_200_pred'] * 1000


                        ############------------------Simulations for +_210 budget scenario------------------###################

                        budget_210 = df_append_sim.at[count, 'budget'] * 3.1

                        # Closest budget for +_210 budget
                        closest_budget_210 = closest(lst, budget_210)
                        df_append_sim.loc[count, 'budget_210'] = budget_210

                        # Fetch two rows for interpolate the budget values

                        if budget_210 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_210]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_210 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_210 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_210 >= budget_210:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_210]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_210 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_210 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_210]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_210 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_210 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_210'] = closest_upper_row_210.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_210'] = closest_lower_row_210.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_210'] = closest_upper_row_210.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_210'] = closest_lower_row_210.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_210'] = closest_upper_row_210.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_210'] = closest_lower_row_210.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_210'] = closest_upper_row_210.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_210'] = closest_lower_row_210.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_210'] = closest_upper_row_210.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_210'] = closest_lower_row_210.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_210'] = closest_upper_row_210.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_210'] = closest_lower_row_210.loc[0, 'weekly_freq']


                        #Interpolating values for +_210 budget

                        df_append_sim.loc[count, 'rf_impression_210_pred'] = (((closest_upper_row_210.loc[0, 'impression'] - closest_lower_row_210.loc[0, 'impression']) / (closest_upper_row_210.loc[0, 'budget'] - closest_lower_row_210.loc[0, 'budget'])) * (budget_210-closest_lower_row_210.loc[0, 'budget'])) + closest_lower_row_210.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_210_pred'] = (((closest_upper_row_210.loc[0, 'reach'] - closest_lower_row_210.loc[0, 'reach']) / (closest_upper_row_210.loc[0, 'budget'] - closest_lower_row_210.loc[0, 'budget'])) * (budget_210-closest_lower_row_210.loc[0, 'budget'])) + closest_lower_row_210.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_210_pred'] = (((closest_upper_row_210.loc[0, 'conversion'] - closest_lower_row_210.loc[0, 'conversion']) / (closest_upper_row_210.loc[0, 'budget'] - closest_lower_row_210.loc[0, 'budget'])) * (budget_210-closest_lower_row_210.loc[0, 'budget'])) + closest_lower_row_210.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_210_pred'] = (((closest_upper_row_210.loc[0, 'frequency'] - closest_lower_row_210.loc[0, 'frequency']) / (closest_upper_row_210.loc[0, 'budget'] - closest_lower_row_210.loc[0, 'budget'])) * (budget_210-closest_lower_row_210.loc[0, 'budget'])) + closest_lower_row_210.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_210_pred'] = (((closest_upper_row_210.loc[0, 'weekly_freq'] - closest_lower_row_210.loc[0, 'weekly_freq']) / (closest_upper_row_210.loc[0, 'budget'] - closest_lower_row_210.loc[0, 'budget'])) * (budget_210-closest_lower_row_210.loc[0, 'budget'])) + closest_lower_row_210.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_210_pred'] = budget_210 / df_append_sim.loc[count, 'rf_impression_210_pred'] * 1000





                        ############------------------Simulations for +_220 budget scenario------------------###################

                        budget_220 = df_append_sim.at[count, 'budget'] * 3.2

                        # Closest budget for +_220 budget
                        closest_budget_220 = closest(lst, budget_220)
                        df_append_sim.loc[count, 'budget_220'] = budget_220

                        # Fetch two rows for interpolate the budget values

                        if budget_220 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_220]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_220 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_220 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_220 >= budget_220:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_220]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_220 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_220 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_220]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_220 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_220 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_220'] = closest_upper_row_220.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_220'] = closest_lower_row_220.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_220'] = closest_upper_row_220.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_220'] = closest_lower_row_220.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_220'] = closest_upper_row_220.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_220'] = closest_lower_row_220.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_220'] = closest_upper_row_220.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_220'] = closest_lower_row_220.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_220'] = closest_upper_row_220.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_220'] = closest_lower_row_220.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_220'] = closest_upper_row_220.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_220'] = closest_lower_row_220.loc[0, 'weekly_freq']


                        #Interpolating values for +_220 budget

                        df_append_sim.loc[count, 'rf_impression_220_pred'] = (((closest_upper_row_220.loc[0, 'impression'] - closest_lower_row_220.loc[0, 'impression']) / (closest_upper_row_220.loc[0, 'budget'] - closest_lower_row_220.loc[0, 'budget'])) * (budget_220-closest_lower_row_220.loc[0, 'budget'])) + closest_lower_row_220.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_220_pred'] = (((closest_upper_row_220.loc[0, 'reach'] - closest_lower_row_220.loc[0, 'reach']) / (closest_upper_row_220.loc[0, 'budget'] - closest_lower_row_220.loc[0, 'budget'])) * (budget_220-closest_lower_row_220.loc[0, 'budget'])) + closest_lower_row_220.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_220_pred'] = (((closest_upper_row_220.loc[0, 'conversion'] - closest_lower_row_220.loc[0, 'conversion']) / (closest_upper_row_220.loc[0, 'budget'] - closest_lower_row_220.loc[0, 'budget'])) * (budget_220-closest_lower_row_220.loc[0, 'budget'])) + closest_lower_row_220.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_220_pred'] = (((closest_upper_row_220.loc[0, 'frequency'] - closest_lower_row_220.loc[0, 'frequency']) / (closest_upper_row_220.loc[0, 'budget'] - closest_lower_row_220.loc[0, 'budget'])) * (budget_220-closest_lower_row_220.loc[0, 'budget'])) + closest_lower_row_220.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_220_pred'] = (((closest_upper_row_220.loc[0, 'weekly_freq'] - closest_lower_row_220.loc[0, 'weekly_freq']) / (closest_upper_row_220.loc[0, 'budget'] - closest_lower_row_220.loc[0, 'budget'])) * (budget_220-closest_lower_row_220.loc[0, 'budget'])) + closest_lower_row_220.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_220_pred'] = budget_220 / df_append_sim.loc[count, 'rf_impression_220_pred'] * 1000



                        ############------------------Simulations for +_230 budget scenario------------------###################

                        budget_230 = df_append_sim.at[count, 'budget'] * 3.3

                        # Closest budget for +_230 budget
                        closest_budget_230 = closest(lst, budget_230)
                        df_append_sim.loc[count, 'budget_230'] = budget_230

                        # Fetch two rows for interpolate the budget values

                        if budget_230 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_230]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_230 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_230 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_230 >= budget_230:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_230]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_230 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_230 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_230]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_230 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_230 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_230'] = closest_upper_row_230.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_230'] = closest_lower_row_230.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_230'] = closest_upper_row_230.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_230'] = closest_lower_row_230.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_230'] = closest_upper_row_230.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_230'] = closest_lower_row_230.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_230'] = closest_upper_row_230.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_230'] = closest_lower_row_230.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_230'] = closest_upper_row_230.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_230'] = closest_lower_row_230.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_230'] = closest_upper_row_230.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_230'] = closest_lower_row_230.loc[0, 'weekly_freq']


                        #Interpolating values for +_230 budget

                        df_append_sim.loc[count, 'rf_impression_230_pred'] = (((closest_upper_row_230.loc[0, 'impression'] - closest_lower_row_230.loc[0, 'impression']) / (closest_upper_row_230.loc[0, 'budget'] - closest_lower_row_230.loc[0, 'budget'])) * (budget_230-closest_lower_row_230.loc[0, 'budget'])) + closest_lower_row_230.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_230_pred'] = (((closest_upper_row_230.loc[0, 'reach'] - closest_lower_row_230.loc[0, 'reach']) / (closest_upper_row_230.loc[0, 'budget'] - closest_lower_row_230.loc[0, 'budget'])) * (budget_230-closest_lower_row_230.loc[0, 'budget'])) + closest_lower_row_230.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_230_pred'] = (((closest_upper_row_230.loc[0, 'conversion'] - closest_lower_row_230.loc[0, 'conversion']) / (closest_upper_row_230.loc[0, 'budget'] - closest_lower_row_230.loc[0, 'budget'])) * (budget_230-closest_lower_row_230.loc[0, 'budget'])) + closest_lower_row_230.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_230_pred'] = (((closest_upper_row_230.loc[0, 'frequency'] - closest_lower_row_230.loc[0, 'frequency']) / (closest_upper_row_230.loc[0, 'budget'] - closest_lower_row_230.loc[0, 'budget'])) * (budget_230-closest_lower_row_230.loc[0, 'budget'])) + closest_lower_row_230.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_230_pred'] = (((closest_upper_row_230.loc[0, 'weekly_freq'] - closest_lower_row_230.loc[0, 'weekly_freq']) / (closest_upper_row_230.loc[0, 'budget'] - closest_lower_row_230.loc[0, 'budget'])) * (budget_230-closest_lower_row_230.loc[0, 'budget'])) + closest_lower_row_230.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_230_pred'] = budget_230 / df_append_sim.loc[count, 'rf_impression_230_pred'] * 1000



                        ############------------------Simulations for +_240 budget scenario------------------###################

                        budget_240 = df_append_sim.at[count, 'budget'] * 3.4

                        # Closest budget for +_240 budget
                        closest_budget_240 = closest(lst, budget_240)
                        df_append_sim.loc[count, 'budget_240'] = budget_240

                        # Fetch two rows for interpolate the budget values

                        if budget_240 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_240]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_240 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_240 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_240 >= budget_240:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_240]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_240 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_240 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_240]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_240 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_240 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_240'] = closest_upper_row_240.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_240'] = closest_lower_row_240.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_240'] = closest_upper_row_240.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_240'] = closest_lower_row_240.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_240'] = closest_upper_row_240.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_240'] = closest_lower_row_240.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_240'] = closest_upper_row_240.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_240'] = closest_lower_row_240.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_240'] = closest_upper_row_240.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_240'] = closest_lower_row_240.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_240'] = closest_upper_row_240.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_240'] = closest_lower_row_240.loc[0, 'weekly_freq']


                        #Interpolating values for +_240 budget

                        df_append_sim.loc[count, 'rf_impression_240_pred'] = (((closest_upper_row_240.loc[0, 'impression'] - closest_lower_row_240.loc[0, 'impression']) / (closest_upper_row_240.loc[0, 'budget'] - closest_lower_row_240.loc[0, 'budget'])) * (budget_240-closest_lower_row_240.loc[0, 'budget'])) + closest_lower_row_240.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_240_pred'] = (((closest_upper_row_240.loc[0, 'reach'] - closest_lower_row_240.loc[0, 'reach']) / (closest_upper_row_240.loc[0, 'budget'] - closest_lower_row_240.loc[0, 'budget'])) * (budget_240-closest_lower_row_240.loc[0, 'budget'])) + closest_lower_row_240.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_240_pred'] = (((closest_upper_row_240.loc[0, 'conversion'] - closest_lower_row_240.loc[0, 'conversion']) / (closest_upper_row_240.loc[0, 'budget'] - closest_lower_row_240.loc[0, 'budget'])) * (budget_240-closest_lower_row_240.loc[0, 'budget'])) + closest_lower_row_240.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_240_pred'] = (((closest_upper_row_240.loc[0, 'frequency'] - closest_lower_row_240.loc[0, 'frequency']) / (closest_upper_row_240.loc[0, 'budget'] - closest_lower_row_240.loc[0, 'budget'])) * (budget_240-closest_lower_row_240.loc[0, 'budget'])) + closest_lower_row_240.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_240_pred'] = (((closest_upper_row_240.loc[0, 'weekly_freq'] - closest_lower_row_240.loc[0, 'weekly_freq']) / (closest_upper_row_240.loc[0, 'budget'] - closest_lower_row_240.loc[0, 'budget'])) * (budget_240-closest_lower_row_240.loc[0, 'budget'])) + closest_lower_row_240.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_240_pred'] = budget_240 / df_append_sim.loc[count, 'rf_impression_240_pred'] * 1000



                        ############------------------Simulations for +_250 budget scenario------------------###################

                        budget_250 = df_append_sim.at[count, 'budget'] * 3.5

                        # Closest budget for +_250 budget
                        closest_budget_250 = closest(lst, budget_250)
                        df_append_sim.loc[count, 'budget_250'] = budget_250

                        # Fetch two rows for interpolate the budget values

                        if budget_250 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_250]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_250 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_250 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_250 >= budget_250:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_250]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_250 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_250 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_250]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_250 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_250 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_250'] = closest_upper_row_250.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_250'] = closest_lower_row_250.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_250'] = closest_upper_row_250.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_250'] = closest_lower_row_250.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_250'] = closest_upper_row_250.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_250'] = closest_lower_row_250.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_250'] = closest_upper_row_250.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_250'] = closest_lower_row_250.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_250'] = closest_upper_row_250.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_250'] = closest_lower_row_250.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_250'] = closest_upper_row_250.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_250'] = closest_lower_row_250.loc[0, 'weekly_freq']


                        #Interpolating values for +_250 budget

                        df_append_sim.loc[count, 'rf_impression_250_pred'] = (((closest_upper_row_250.loc[0, 'impression'] - closest_lower_row_250.loc[0, 'impression']) / (closest_upper_row_250.loc[0, 'budget'] - closest_lower_row_250.loc[0, 'budget'])) * (budget_250-closest_lower_row_250.loc[0, 'budget'])) + closest_lower_row_250.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_250_pred'] = (((closest_upper_row_250.loc[0, 'reach'] - closest_lower_row_250.loc[0, 'reach']) / (closest_upper_row_250.loc[0, 'budget'] - closest_lower_row_250.loc[0, 'budget'])) * (budget_250-closest_lower_row_250.loc[0, 'budget'])) + closest_lower_row_250.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_250_pred'] = (((closest_upper_row_250.loc[0, 'conversion'] - closest_lower_row_250.loc[0, 'conversion']) / (closest_upper_row_250.loc[0, 'budget'] - closest_lower_row_250.loc[0, 'budget'])) * (budget_250-closest_lower_row_250.loc[0, 'budget'])) + closest_lower_row_250.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_250_pred'] = (((closest_upper_row_250.loc[0, 'frequency'] - closest_lower_row_250.loc[0, 'frequency']) / (closest_upper_row_250.loc[0, 'budget'] - closest_lower_row_250.loc[0, 'budget'])) * (budget_250-closest_lower_row_250.loc[0, 'budget'])) + closest_lower_row_250.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_250_pred'] = (((closest_upper_row_250.loc[0, 'weekly_freq'] - closest_lower_row_250.loc[0, 'weekly_freq']) / (closest_upper_row_250.loc[0, 'budget'] - closest_lower_row_250.loc[0, 'budget'])) * (budget_250-closest_lower_row_250.loc[0, 'budget'])) + closest_lower_row_250.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_250_pred'] = budget_250 / df_append_sim.loc[count, 'rf_impression_250_pred'] * 1000





                        ############------------------Simulations for +_260 budget scenario------------------###################

                        budget_260 = df_append_sim.at[count, 'budget'] * 3.6

                        # Closest budget for +_260 budget
                        closest_budget_260 = closest(lst, budget_260)
                        df_append_sim.loc[count, 'budget_260'] = budget_260

                        # Fetch two rows for interpolate the budget values

                        if budget_260 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_260]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_260 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_260 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_260 >= budget_260:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_260]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_260 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_260 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_260]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_260 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_260 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_260'] = closest_upper_row_260.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_260'] = closest_lower_row_260.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_260'] = closest_upper_row_260.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_260'] = closest_lower_row_260.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_260'] = closest_upper_row_260.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_260'] = closest_lower_row_260.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_260'] = closest_upper_row_260.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_260'] = closest_lower_row_260.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_260'] = closest_upper_row_260.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_260'] = closest_lower_row_260.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_260'] = closest_upper_row_260.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_260'] = closest_lower_row_260.loc[0, 'weekly_freq']


                        #Interpolating values for +_260 budget

                        df_append_sim.loc[count, 'rf_impression_260_pred'] = (((closest_upper_row_260.loc[0, 'impression'] - closest_lower_row_260.loc[0, 'impression']) / (closest_upper_row_260.loc[0, 'budget'] - closest_lower_row_260.loc[0, 'budget'])) * (budget_260-closest_lower_row_260.loc[0, 'budget'])) + closest_lower_row_260.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_260_pred'] = (((closest_upper_row_260.loc[0, 'reach'] - closest_lower_row_260.loc[0, 'reach']) / (closest_upper_row_260.loc[0, 'budget'] - closest_lower_row_260.loc[0, 'budget'])) * (budget_260-closest_lower_row_260.loc[0, 'budget'])) + closest_lower_row_260.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_260_pred'] = (((closest_upper_row_260.loc[0, 'conversion'] - closest_lower_row_260.loc[0, 'conversion']) / (closest_upper_row_260.loc[0, 'budget'] - closest_lower_row_260.loc[0, 'budget'])) * (budget_260-closest_lower_row_260.loc[0, 'budget'])) + closest_lower_row_260.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_260_pred'] = (((closest_upper_row_260.loc[0, 'frequency'] - closest_lower_row_260.loc[0, 'frequency']) / (closest_upper_row_260.loc[0, 'budget'] - closest_lower_row_260.loc[0, 'budget'])) * (budget_260-closest_lower_row_260.loc[0, 'budget'])) + closest_lower_row_260.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_260_pred'] = (((closest_upper_row_260.loc[0, 'weekly_freq'] - closest_lower_row_260.loc[0, 'weekly_freq']) / (closest_upper_row_260.loc[0, 'budget'] - closest_lower_row_260.loc[0, 'budget'])) * (budget_260-closest_lower_row_260.loc[0, 'budget'])) + closest_lower_row_260.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_260_pred'] = budget_260 / df_append_sim.loc[count, 'rf_impression_260_pred'] * 1000





                        ############------------------Simulations for +_270 budget scenario------------------###################

                        budget_270 = df_append_sim.at[count, 'budget'] * 3.7

                        # Closest budget for +_270 budget
                        closest_budget_270 = closest(lst, budget_270)
                        df_append_sim.loc[count, 'budget_270'] = budget_270

                        # Fetch two rows for interpolate the budget values

                        if budget_270 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_270]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_270 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_270 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_270 >= budget_270:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_270]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_270 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_270 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_270]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_270 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_270 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_270'] = closest_upper_row_270.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_270'] = closest_lower_row_270.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_270'] = closest_upper_row_270.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_270'] = closest_lower_row_270.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_270'] = closest_upper_row_270.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_270'] = closest_lower_row_270.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_270'] = closest_upper_row_270.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_270'] = closest_lower_row_270.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_270'] = closest_upper_row_270.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_270'] = closest_lower_row_270.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_270'] = closest_upper_row_270.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_270'] = closest_lower_row_270.loc[0, 'weekly_freq']


                        #Interpolating values for +_270 budget

                        df_append_sim.loc[count, 'rf_impression_270_pred'] = (((closest_upper_row_270.loc[0, 'impression'] - closest_lower_row_270.loc[0, 'impression']) / (closest_upper_row_270.loc[0, 'budget'] - closest_lower_row_270.loc[0, 'budget'])) * (budget_270-closest_lower_row_270.loc[0, 'budget'])) + closest_lower_row_270.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_270_pred'] = (((closest_upper_row_270.loc[0, 'reach'] - closest_lower_row_270.loc[0, 'reach']) / (closest_upper_row_270.loc[0, 'budget'] - closest_lower_row_270.loc[0, 'budget'])) * (budget_270-closest_lower_row_270.loc[0, 'budget'])) + closest_lower_row_270.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_270_pred'] = (((closest_upper_row_270.loc[0, 'conversion'] - closest_lower_row_270.loc[0, 'conversion']) / (closest_upper_row_270.loc[0, 'budget'] - closest_lower_row_270.loc[0, 'budget'])) * (budget_270-closest_lower_row_270.loc[0, 'budget'])) + closest_lower_row_270.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_270_pred'] = (((closest_upper_row_270.loc[0, 'frequency'] - closest_lower_row_270.loc[0, 'frequency']) / (closest_upper_row_270.loc[0, 'budget'] - closest_lower_row_270.loc[0, 'budget'])) * (budget_270-closest_lower_row_270.loc[0, 'budget'])) + closest_lower_row_270.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_270_pred'] = (((closest_upper_row_270.loc[0, 'weekly_freq'] - closest_lower_row_270.loc[0, 'weekly_freq']) / (closest_upper_row_270.loc[0, 'budget'] - closest_lower_row_270.loc[0, 'budget'])) * (budget_270-closest_lower_row_270.loc[0, 'budget'])) + closest_lower_row_270.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_270_pred'] = budget_270 / df_append_sim.loc[count, 'rf_impression_270_pred'] * 1000





                        ############------------------Simulations for +_280 budget scenario------------------###################

                        budget_280 = df_append_sim.at[count, 'budget'] * 3.8

                        # Closest budget for +_280 budget
                        closest_budget_280 = closest(lst, budget_280)
                        df_append_sim.loc[count, 'budget_280'] = budget_280

                        # Fetch two rows for interpolate the budget values

                        if budget_280 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_280]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_280 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_280 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_280 >= budget_280:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_280]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_280 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_280 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_280]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_280 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_280 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_280'] = closest_upper_row_280.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_280'] = closest_lower_row_280.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_280'] = closest_upper_row_280.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_280'] = closest_lower_row_280.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_280'] = closest_upper_row_280.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_280'] = closest_lower_row_280.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_280'] = closest_upper_row_280.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_280'] = closest_lower_row_280.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_280'] = closest_upper_row_280.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_280'] = closest_lower_row_280.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_280'] = closest_upper_row_280.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_280'] = closest_lower_row_280.loc[0, 'weekly_freq']


                        #Interpolating values for +_280 budget

                        df_append_sim.loc[count, 'rf_impression_280_pred'] = (((closest_upper_row_280.loc[0, 'impression'] - closest_lower_row_280.loc[0, 'impression']) / (closest_upper_row_280.loc[0, 'budget'] - closest_lower_row_280.loc[0, 'budget'])) * (budget_280-closest_lower_row_280.loc[0, 'budget'])) + closest_lower_row_280.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_280_pred'] = (((closest_upper_row_280.loc[0, 'reach'] - closest_lower_row_280.loc[0, 'reach']) / (closest_upper_row_280.loc[0, 'budget'] - closest_lower_row_280.loc[0, 'budget'])) * (budget_280-closest_lower_row_280.loc[0, 'budget'])) + closest_lower_row_280.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_280_pred'] = (((closest_upper_row_280.loc[0, 'conversion'] - closest_lower_row_280.loc[0, 'conversion']) / (closest_upper_row_280.loc[0, 'budget'] - closest_lower_row_280.loc[0, 'budget'])) * (budget_280-closest_lower_row_280.loc[0, 'budget'])) + closest_lower_row_280.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_280_pred'] = (((closest_upper_row_280.loc[0, 'frequency'] - closest_lower_row_280.loc[0, 'frequency']) / (closest_upper_row_280.loc[0, 'budget'] - closest_lower_row_280.loc[0, 'budget'])) * (budget_280-closest_lower_row_280.loc[0, 'budget'])) + closest_lower_row_280.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_280_pred'] = (((closest_upper_row_280.loc[0, 'weekly_freq'] - closest_lower_row_280.loc[0, 'weekly_freq']) / (closest_upper_row_280.loc[0, 'budget'] - closest_lower_row_280.loc[0, 'budget'])) * (budget_280-closest_lower_row_280.loc[0, 'budget'])) + closest_lower_row_280.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_280_pred'] = budget_280 / df_append_sim.loc[count, 'rf_impression_280_pred'] * 1000





                        ############------------------Simulations for +_290 budget scenario------------------###################

                        budget_290 = df_append_sim.at[count, 'budget'] * 3.9

                        # Closest budget for +_290 budget
                        closest_budget_290 = closest(lst, budget_290)
                        df_append_sim.loc[count, 'budget_290'] = budget_290

                        # Fetch two rows for interpolate the budget values

                        if budget_290 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_290]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_290 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_290 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_290 >= budget_290:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_290]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_290 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_290 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_290]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_290 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_290 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_290'] = closest_upper_row_290.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_290'] = closest_lower_row_290.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_290'] = closest_upper_row_290.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_290'] = closest_lower_row_290.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_290'] = closest_upper_row_290.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_290'] = closest_lower_row_290.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_290'] = closest_upper_row_290.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lower_conversion_290'] = closest_lower_row_290.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_290'] = closest_upper_row_290.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_290'] = closest_lower_row_290.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_290'] = closest_upper_row_290.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_290'] = closest_lower_row_290.loc[0, 'weekly_freq']


                        #Interpolating values for +_290 budget

                        df_append_sim.loc[count, 'rf_impression_290_pred'] = (((closest_upper_row_290.loc[0, 'impression'] - closest_lower_row_290.loc[0, 'impression']) / (closest_upper_row_290.loc[0, 'budget'] - closest_lower_row_290.loc[0, 'budget'])) * (budget_290-closest_lower_row_290.loc[0, 'budget'])) + closest_lower_row_290.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_290_pred'] = (((closest_upper_row_290.loc[0, 'reach'] - closest_lower_row_290.loc[0, 'reach']) / (closest_upper_row_290.loc[0, 'budget'] - closest_lower_row_290.loc[0, 'budget'])) * (budget_290-closest_lower_row_290.loc[0, 'budget'])) + closest_lower_row_290.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_290_pred'] = (((closest_upper_row_290.loc[0, 'conversion'] - closest_lower_row_290.loc[0, 'conversion']) / (closest_upper_row_290.loc[0, 'budget'] - closest_lower_row_290.loc[0, 'budget'])) * (budget_290-closest_lower_row_290.loc[0, 'budget'])) + closest_lower_row_290.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_290_pred'] = (((closest_upper_row_290.loc[0, 'frequency'] - closest_lower_row_290.loc[0, 'frequency']) / (closest_upper_row_290.loc[0, 'budget'] - closest_lower_row_290.loc[0, 'budget'])) * (budget_290-closest_lower_row_290.loc[0, 'budget'])) + closest_lower_row_290.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_290_pred'] = (((closest_upper_row_290.loc[0, 'weekly_freq'] - closest_lower_row_290.loc[0, 'weekly_freq']) / (closest_upper_row_290.loc[0, 'budget'] - closest_lower_row_290.loc[0, 'budget'])) * (budget_290-closest_lower_row_290.loc[0, 'budget'])) + closest_lower_row_290.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_290_pred'] = budget_290 / df_append_sim.loc[count, 'rf_impression_290_pred'] * 1000





                        ############------------------Simulations for +_300 budget scenario------------------###################

                        budget_300 = df_append_sim.at[count, 'budget'] * 4

                        # Closest budget for +_300 budget
                        closest_budget_300 = closest(lst, budget_300)
                        df_append_sim.loc[count, 'budget_300'] = budget_300

                        # Fetch two rows for interpolate the budget values

                        if budget_300 > max(clean_df['budget']):

                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_300]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_300 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_300 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        elif closest_budget_300 >= budget_300:
                            closest_upper_index = (clean_df[clean_df['budget'] == closest_budget_300]).index.to_list()[0]
                            closest_lower_index = closest_upper_index - 1

                            closest_upper_row_300 = (clean_df.filter(like = str(closest_upper_index), axis=0)).reset_index()
                            closest_lower_row_300 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        else:

                            closest_lower_index = (clean_df[clean_df['budget'] == closest_budget_300]).index.to_list()[0]
                            closest_upper_index = closest_lower_index + 1

                            closest_upper_row_300 = clean_df.filter(like = str(closest_upper_index), axis=0).reset_index()
                            closest_lower_row_300 = clean_df.filter(like = str(closest_lower_index), axis=0).reset_index()

                        df_append_sim.loc[count, 'closest_upper_budget_300'] = closest_upper_row_300.loc[0, 'budget']
                        df_append_sim.loc[count, 'closest_lower_budget_300'] = closest_lower_row_300.loc[0, 'budget']

                        df_append_sim.loc[count, 'closest_upper_impression_300'] = closest_upper_row_300.loc[0, 'impression']
                        df_append_sim.loc[count, 'closest_lower_impression_300'] = closest_lower_row_300.loc[0, 'impression']

                        df_append_sim.loc[count, 'closest_upper_reach_300'] = closest_upper_row_300.loc[0, 'reach']
                        df_append_sim.loc[count, 'closest_lower_reach_300'] = closest_lower_row_300.loc[0, 'reach']

                        df_append_sim.loc[count, 'closest_upper_conversion_300'] = closest_upper_row_300.loc[0, 'conversion']
                        df_append_sim.loc[count, 'closest_lowerowr_conversion_300'] = closest_lower_row_300.loc[0, 'conversion']


                        df_append_sim.loc[count, 'closest_upper_frequency_300'] = closest_upper_row_300.loc[0, 'frequency']
                        df_append_sim.loc[count, 'closest_lower_frequency_300'] = closest_lower_row_300.loc[0, 'frequency']

                        df_append_sim.loc[count, 'closest_upper_weekly_freq_300'] = closest_upper_row_300.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'closest_lower_weekly_freq_300'] = closest_lower_row_300.loc[0, 'weekly_freq']


                        #Interpolating values for +_300 budget

                        df_append_sim.loc[count, 'rf_impression_300_pred'] = (((closest_upper_row_300.loc[0, 'impression'] - closest_lower_row_300.loc[0, 'impression']) / (closest_upper_row_300.loc[0, 'budget'] - closest_lower_row_300.loc[0, 'budget'])) * (budget_300-closest_lower_row_300.loc[0, 'budget'])) + closest_lower_row_300.loc[0, 'impression']
                        df_append_sim.loc[count, 'rf_reach_300_pred'] = (((closest_upper_row_300.loc[0, 'reach'] - closest_lower_row_300.loc[0, 'reach']) / (closest_upper_row_300.loc[0, 'budget'] - closest_lower_row_300.loc[0, 'budget'])) * (budget_300-closest_lower_row_300.loc[0, 'budget'])) + closest_lower_row_300.loc[0, 'reach']
                        df_append_sim.loc[count, 'rf_conversion_300_pred'] = (((closest_upper_row_300.loc[0, 'conversion'] - closest_lower_row_300.loc[0, 'conversion']) / (closest_upper_row_300.loc[0, 'budget'] - closest_lower_row_300.loc[0, 'budget'])) * (budget_300-closest_lower_row_300.loc[0, 'budget'])) + closest_lower_row_300.loc[0, 'conversion']
                        df_append_sim.loc[count, 'rf_frequency_300_pred'] = (((closest_upper_row_300.loc[0, 'frequency'] - closest_lower_row_300.loc[0, 'frequency']) / (closest_upper_row_300.loc[0, 'budget'] - closest_lower_row_300.loc[0, 'budget'])) * (budget_300-closest_lower_row_300.loc[0, 'budget'])) + closest_lower_row_300.loc[0, 'frequency']
                        df_append_sim.loc[count, 'rf_weekly_freq_300_pred'] = (((closest_upper_row_300.loc[0, 'weekly_freq'] - closest_lower_row_300.loc[0, 'weekly_freq']) / (closest_upper_row_300.loc[0, 'budget'] - closest_lower_row_300.loc[0, 'budget'])) * (budget_300-closest_lower_row_300.loc[0, 'budget'])) + closest_lower_row_300.loc[0, 'weekly_freq']
                        df_append_sim.loc[count, 'rf_cpm_300_pred'] = budget_300 / df_append_sim.loc[count, 'rf_impression_300_pred'] * 1000

                        print(count)



                        count = count + 1

df_append_sim


# Melt budget to have an easier way to read the data
df_budget = pd.melt(df_append_sim, id_vars = ['country','gender','age_min','age_max', 'days', 
                                              'frequency_cap', 'objective', 'included_interests', 'excluded_interests'],
              value_vars = ['budget','budget_10','budget_15','budget_20','budget_25','budget_30','budget_35',
                            'budget_40','budget_45','budget_50','budget_55','budget_60','budget_65','budget_70',
                            'budget_75','budget_80','budget_85','budget_90','budget_95','budget_100','budget_105',
                            'budget_110','budget_115','budget_120','budget_125','budget_130','budget_135',
                            'budget_140','budget_145','budget_150','budget_155','budget_160','budget_165',
                            'budget_170','budget_175','budget_180','budget_185','budget_190','budget_195',
                            'budget_200','budget_210','budget_220','budget_230','budget_240','budget_250',
                            'budget_260','budget_270','budget_280','budget_290','budget_300'],
                         var_name='Scenario_budget', value_name='Budget')


# Melt impressions to have an easier way to read the data
df_impressions = pd.melt(df_append_sim, id_vars = ['country','gender','age_min','age_max', 'days', 
                                              'frequency_cap', 'objective', 'included_interests', 'excluded_interests'],
              value_vars = ['rf_impression_bau_pred','rf_impression_10_pred','rf_impression_15_pred',
                            'rf_impression_20_pred','rf_impression_25_pred','rf_impression_30_pred',
                            'rf_impression_35_pred','rf_impression_40_pred','rf_impression_45_pred',
                            'rf_impression_50_pred','rf_impression_55_pred','rf_impression_60_pred',
                            'rf_impression_65_pred','rf_impression_70_pred','rf_impression_75_pred',
                            'rf_impression_80_pred','rf_impression_85_pred','rf_impression_90_pred',
                            'rf_impression_95_pred','rf_impression_100_pred','rf_impression_105_pred',
                            'rf_impression_110_pred','rf_impression_115_pred','rf_impression_120_pred',
                            'rf_impression_125_pred','rf_impression_130_pred','rf_impression_135_pred',
                            'rf_impression_140_pred','rf_impression_145_pred','rf_impression_150_pred',
                            'rf_impression_155_pred','rf_impression_160_pred','rf_impression_165_pred',
                            'rf_impression_170_pred','rf_impression_175_pred','rf_impression_180_pred',
                            'rf_impression_185_pred','rf_impression_190_pred','rf_impression_195_pred',
                            'rf_impression_200_pred','rf_impression_210_pred','rf_impression_220_pred',
                            'rf_impression_230_pred','rf_impression_240_pred','rf_impression_250_pred',
                            'rf_impression_260_pred','rf_impression_270_pred','rf_impression_280_pred',
                            'rf_impression_290_pred','rf_impression_300_pred'],
                         var_name='Scenario_imp', value_name='Impressions')

# Melt reach to have an easier way to read the data
df_reach = pd.melt(df_append_sim, id_vars = ['country','gender','age_min','age_max', 'days', 
                                              'frequency_cap', 'objective', 'included_interests', 'excluded_interests'],
              value_vars = ['rf_reach_bau_pred','rf_reach_10_pred','rf_reach_15_pred',
                            'rf_reach_20_pred','rf_reach_25_pred','rf_reach_30_pred',
                            'rf_reach_35_pred','rf_reach_40_pred','rf_reach_45_pred',
                            'rf_reach_50_pred','rf_reach_55_pred','rf_reach_60_pred',
                            'rf_reach_65_pred','rf_reach_70_pred','rf_reach_75_pred',
                            'rf_reach_80_pred','rf_reach_85_pred','rf_reach_90_pred',
                            'rf_reach_95_pred','rf_reach_100_pred','rf_reach_105_pred',
                            'rf_reach_110_pred','rf_reach_115_pred','rf_reach_120_pred',
                            'rf_reach_125_pred','rf_reach_130_pred','rf_reach_135_pred',
                            'rf_reach_140_pred','rf_reach_145_pred','rf_reach_150_pred',
                            'rf_reach_155_pred','rf_reach_160_pred','rf_reach_165_pred',
                            'rf_reach_170_pred','rf_reach_175_pred','rf_reach_180_pred',
                            'rf_reach_185_pred','rf_reach_190_pred','rf_reach_195_pred',
                            'rf_reach_200_pred','rf_reach_210_pred','rf_reach_220_pred',
                            'rf_reach_230_pred','rf_reach_240_pred','rf_reach_250_pred',
                            'rf_reach_260_pred','rf_reach_270_pred','rf_reach_280_pred',
                            'rf_reach_290_pred','rf_reach_300_pred'],
                         var_name='Scenario_reach', value_name='Reach')

# Melt frequency to have an easier way to read the data
df_frequency = pd.melt(df_append_sim, id_vars = ['country','gender','age_min','age_max', 'days', 
                                              'frequency_cap', 'objective', 'included_interests', 'excluded_interests'],
              value_vars = ['rf_frequency_bau_pred','rf_frequency_10_pred','rf_frequency_15_pred',
                            'rf_frequency_20_pred','rf_frequency_25_pred','rf_frequency_30_pred',
                            'rf_frequency_35_pred','rf_frequency_40_pred','rf_frequency_45_pred',
                            'rf_frequency_50_pred','rf_frequency_55_pred','rf_frequency_60_pred',
                            'rf_frequency_65_pred','rf_frequency_70_pred','rf_frequency_75_pred',
                            'rf_frequency_80_pred','rf_frequency_85_pred','rf_frequency_90_pred',
                            'rf_frequency_95_pred','rf_frequency_100_pred','rf_frequency_105_pred',
                            'rf_frequency_110_pred','rf_frequency_115_pred','rf_frequency_120_pred',
                            'rf_frequency_125_pred','rf_frequency_130_pred','rf_frequency_135_pred',
                            'rf_frequency_140_pred','rf_frequency_145_pred','rf_frequency_150_pred',
                            'rf_frequency_155_pred','rf_frequency_160_pred','rf_frequency_165_pred',
                            'rf_frequency_170_pred','rf_frequency_175_pred','rf_frequency_180_pred',
                            'rf_frequency_185_pred','rf_frequency_190_pred','rf_frequency_195_pred',
                            'rf_frequency_200_pred','rf_frequency_210_pred','rf_frequency_220_pred',
                            'rf_frequency_230_pred','rf_frequency_240_pred','rf_frequency_250_pred',
                            'rf_frequency_260_pred','rf_frequency_270_pred','rf_frequency_280_pred',
                            'rf_frequency_290_pred','rf_frequency_300_pred'],
                         var_name='Scenario_frequency', value_name='Frequency')

# Melt weekly frequency to have an easier way to read the data
df_weekly_freq = pd.melt(df_append_sim, id_vars = ['country','gender','age_min','age_max', 'days', 
                                              'frequency_cap', 'objective', 'included_interests', 'excluded_interests'],
              value_vars = ['rf_weekly_freq_bau_pred','rf_weekly_freq_10_pred','rf_weekly_freq_15_pred',
                            'rf_weekly_freq_20_pred','rf_weekly_freq_25_pred','rf_weekly_freq_30_pred',
                            'rf_weekly_freq_35_pred','rf_weekly_freq_40_pred','rf_weekly_freq_45_pred',
                            'rf_weekly_freq_50_pred','rf_weekly_freq_55_pred','rf_weekly_freq_60_pred',
                            'rf_weekly_freq_65_pred','rf_weekly_freq_70_pred','rf_weekly_freq_75_pred',
                            'rf_weekly_freq_80_pred','rf_weekly_freq_85_pred','rf_weekly_freq_90_pred',
                            'rf_weekly_freq_95_pred','rf_weekly_freq_100_pred','rf_weekly_freq_105_pred',
                            'rf_weekly_freq_110_pred','rf_weekly_freq_115_pred','rf_weekly_freq_120_pred',
                            'rf_weekly_freq_125_pred','rf_weekly_freq_130_pred','rf_weekly_freq_135_pred',
                            'rf_weekly_freq_140_pred','rf_weekly_freq_145_pred','rf_weekly_freq_150_pred',
                            'rf_weekly_freq_155_pred','rf_weekly_freq_160_pred','rf_weekly_freq_165_pred',
                            'rf_weekly_freq_170_pred','rf_weekly_freq_175_pred','rf_weekly_freq_180_pred',
                            'rf_weekly_freq_185_pred','rf_weekly_freq_190_pred','rf_weekly_freq_195_pred',
                            'rf_weekly_freq_200_pred','rf_weekly_freq_210_pred','rf_weekly_freq_220_pred',
                            'rf_weekly_freq_230_pred','rf_weekly_freq_240_pred','rf_weekly_freq_250_pred',
                            'rf_weekly_freq_260_pred','rf_weekly_freq_270_pred','rf_weekly_freq_280_pred',
                            'rf_weekly_freq_290_pred','rf_weekly_freq_300_pred'],
                         var_name='Scenario_weekly_freq', value_name='Weekly frequency')

# Melt cpm to have an easier way to read the data
df_cpm = pd.melt(df_append_sim, id_vars = ['country','gender','age_min','age_max', 'days', 
                                              'frequency_cap', 'objective', 'included_interests', 'excluded_interests'],
              value_vars = ['rf_cpm_bau_pred','rf_cpm_10_pred','rf_cpm_15_pred',
                            'rf_cpm_20_pred','rf_cpm_25_pred','rf_cpm_30_pred',
                            'rf_cpm_35_pred','rf_cpm_40_pred','rf_cpm_45_pred',
                            'rf_cpm_50_pred','rf_cpm_55_pred','rf_cpm_60_pred',
                            'rf_cpm_65_pred','rf_cpm_70_pred','rf_cpm_75_pred',
                            'rf_cpm_80_pred','rf_cpm_85_pred','rf_cpm_90_pred',
                            'rf_cpm_95_pred','rf_cpm_100_pred','rf_cpm_105_pred',
                            'rf_cpm_110_pred','rf_cpm_115_pred','rf_cpm_120_pred',
                            'rf_cpm_125_pred','rf_cpm_130_pred','rf_cpm_135_pred',
                            'rf_cpm_140_pred','rf_cpm_145_pred','rf_cpm_150_pred',
                            'rf_cpm_155_pred','rf_cpm_160_pred','rf_cpm_165_pred',
                            'rf_cpm_170_pred','rf_cpm_175_pred','rf_cpm_180_pred',
                            'rf_cpm_185_pred','rf_cpm_190_pred','rf_cpm_195_pred',
                            'rf_cpm_200_pred','rf_cpm_210_pred','rf_cpm_220_pred',
                            'rf_cpm_230_pred','rf_cpm_240_pred','rf_cpm_250_pred',
                            'rf_cpm_260_pred','rf_cpm_270_pred','rf_cpm_280_pred',
                            'rf_cpm_290_pred','rf_cpm_300_pred'],
                         var_name='Scenario_cpm', value_name='CPM')


# Join all dataframes into a single one
df_melt = df_budget.join(df_impressions[['Scenario_imp', 'Impressions']])
df_melt = df_melt.join(df_reach[['Scenario_reach', 'Reach']])
df_melt = df_melt.join(df_frequency[['Scenario_frequency', 'Frequency']])
df_melt = df_melt.join(df_weekly_freq[['Scenario_weekly_freq', 'Weekly frequency']])
df_melt = df_melt.join(df_cpm[['Scenario_cpm', 'CPM']])
df_melt['Lower Reach Percentage'] = df_melt['Reach'] / results['audience_size_upper_bound']
df_melt['Upper Reach Percentage'] = df_melt['Reach'] / results['audience_size_lower_bound']

# Round values to ease reading
df_melt['Lower Reach Percentage'] = (round(((df_melt['Lower Reach Percentage'])*100),1)).astype(str) + '%'
df_melt['Upper Reach Percentage'] = (round(((df_melt['Upper Reach Percentage'])*100),1)).astype(str) + '%'

# Create a additional Reach (in millions) variable to ease reading
df_melt['Reach (millions)'] = round((df_melt['Reach'] / (1000000)),1)

# Adding Ad Account currency to identify CPM units
df_melt['account_currency'] = acc_currency

# Keep only relevant columns
df_melt_clean = df_melt[['country', 'account_currency', 'gender','age_min','age_max','days','frequency_cap','objective','included_interests',
                         'excluded_interests', 'Scenario_budget','Budget','Impressions','Reach', 'Reach (millions)',
                         'Lower Reach Percentage', 'Upper Reach Percentage','Frequency','Weekly frequency','CPM']]

# Rename columns to have an easier reading
df_melt_clean = df_melt_clean.rename(columns = {
    'country': 'Country', 'account_currency': 'Account currency', 'gender': 'Gender','age_min': 'Age min','age_max': 'Age max','days': 'Campaign days',
    'frequency_cap': 'Frequency cap','objective': 'Campaign objective','included_interests': 'Included interests/behaviors',
    'excluded_interests': 'Excluded interests/behaviors', 'Scenario_budget': 'Scenario budget'})

# Rename columns to have an easier reading
df_melt_clean['Scenario budget'] = df_melt_clean['Scenario budget'].replace(['budget','budget_10','budget_15','budget_20','budget_25','budget_30',
                                          'budget_35','budget_40','budget_45','budget_50','budget_55','budget_60',
                                          'budget_65','budget_70','budget_75','budget_80','budget_85','budget_90',
                                          'budget_95','budget_100','budget_105','budget_110','budget_115','budget_120',
                                          'budget_125','budget_130','budget_135','budget_140','budget_145',
                                          'budget_150','budget_155','budget_160','budget_165','budget_170',
                                          'budget_175','budget_180','budget_185','budget_190','budget_195',
                                          'budget_200','budget_210','budget_220','budget_230','budget_240',
                                          'budget_250','budget_260','budget_270','budget_280','budget_290','budget_300'],
                                         ['Business as usual','+10 pct','+15 pct','+20 pct','+25 pct','+30 pct','+35 pct','+40 pct',
                                          '+45 pct','+50 pct','+55 pct','+60 pct','+65 pct','+70 pct','+75 pct','+80 pct','+85 pct','+90 pct',
                                          '+95 pct','+100 pct','+105 pct','+110 pct','+115 pct','+120 pct','+125 pct','+130 pct','+135 pct',
                                          '+140 pct','+145 pct','+150 pct','+155 pct','+160 pct','+165 pct','+170 pct','+175 pct','+180 pct',
                                          '+185 pct','+190 pct','+195 pct','+200 pct','+210 pct','+220 pct','+230 pct','+240 pct','+250 pct',
                                          '+260 pct','+270 pct','+280 pct','+290 pct','+300 pct'])



# Rename columns to have an easier reading
df_melt_clean['Gender'] = df_melt_clean['Gender'].replace(['1 2','1','2'],
                                         ['Male, Female','Male', 'Female'])


df_melt_clean


# Filtering for only keeping the table with the reference budget
df_melt_clean_bau = df_melt_clean[(df_melt_clean['Budget'] == budget)].reset_index(drop = True)

# Identify specs combinations that maximize reach, weekly frequency and minimize CPM
reach_optim = df_melt_clean_bau[(df_melt_clean_bau['Reach'] == df_melt_clean_bau['Reach'].max())]
weekly_freq_optim = df_melt_clean_bau[(df_melt_clean_bau['Weekly frequency'] == df_melt_clean_bau['Weekly frequency'].max())]
cpm_optim = df_melt_clean_bau[(df_melt_clean_bau['CPM'] == df_melt_clean_bau['CPM'].min())]

# Create a new dataframe and store all optims in it
df_optimized = pd.DataFrame()
df_optimized = df_optimized.append(reach_optim)
df_optimized = df_optimized.append(weekly_freq_optim)
df_optimized = df_optimized.append(cpm_optim)

# Reset index
df_optimized = df_optimized.reset_index(drop = True)

# Add a scenario column to identigy optimizations

df_optimized.loc[0, 'Scenario'] = 'Maximum reach'
df_optimized.loc[1, 'Scenario'] = 'Maximum weekly frequency'
df_optimized.loc[2, 'Scenario'] = 'Minimum CPM'

# Create a table visualization
fig = go.Figure(data=[go.Table(
    header=dict(values=list(df_optimized.columns),
                fill_color='aquamarine',
                align='left'),
    cells=dict(values=[df_optimized['Country'], df_optimized['Account currency'], df_optimized['Gender'], 
                       df_optimized['Age min'], df_optimized['Age max'], df_optimized['Campaign days'], 
                       df_optimized['Frequency cap'], df_optimized['Campaign objective'], df_optimized['Included interests/behaviors'],
                       df_optimized['Excluded interests/behaviors'], df_optimized['Scenario budget'], df_optimized['Budget'],
                       df_optimized['Impressions'], df_optimized['Reach'], df_optimized['Reach (millions)'], df_optimized['Lower Reach Percentage'],
                       df_optimized['Upper Reach Percentage'], df_optimized['Frequency'], df_optimized['Weekly frequency'],
                       df_optimized['CPM'], df_optimized['Scenario']],
               fill_color='lavender',
               align='left'))
])

optim_table = fig.show()


print(df_optimized)


# Export the dataframes to CSV files
export_csv = df_melt_clean.to_csv(r'' + save_directory + '/06_KPI_Clean_' + advertiser_name + '_' + ad_account_index + '.csv', header=True, index = None)
export_csv = df_optimized.to_csv(r'' + save_directory + '/06_KPI_Optimized_' + advertiser_name + '_' + ad_account_index + '.csv', header=True, index = None)


# Additional resources on :

# Reach & Frequency Fields

# https://developers.facebook.com/docs/marketing-api/reference/reach-frequency-prediction
# https://developers.facebook.com/docs/marketing-api/reachandfrequency

# Currencies
# https://developers.facebook.com/docs/marketing-api/currencies

# Platforms that cannot work with each Objective

# Audience Network cannot work with:
# 1. LINK_CLICKS
# 2. CONVERSIONS

