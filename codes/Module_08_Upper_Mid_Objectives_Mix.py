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
import math
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d

# This module gets predictions for two Reach & Frequency Objectives to 
# identify the mix that best bring results in terms of reach, weekly frequency or CPMs

#---------------------------------------START INPUT SECTION-----------------------------------------#

#---------------------------------------------INPUT 01----------------------------------------------#

# Include your own access token instead of xxxxxx
access_token = 'xxxxx'
api = FacebookAdsApi.init(
    access_token = access_token,
)


# Set the Ad Account on which you want to have the predictions. Replace the xxxxxx with your own Account ID
ad_account_id = 'act_xxxxx'


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
api_version = 'v15.0'

#---------------------------------------------INPUT 02----------------------------------------------#

# Budget in whole units, not cents and using the same currency your ad account is configured
# This will be your reference budget set as your business as usual
budget = 30000

# Input the country for the ads delivery
# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web
# ONLY USE ONE COUNTRY AT ONCE: LIST OF 1 ELEMENT ONLY
country = ['MX']

# Input all the campaing specs for your prediction
# Input the minimum and maximum ages
# In Meta Ads Platforms, minimum available is 13 years old and maximum is 65, which stands for people 65+ years old
age = [18,65]

# Input the genders. 2-for female, 1-for male
gender = [1,2]

# When using interest-behavior based audiences, make sure that you have already saved the audience in the 
# same AdAccount in Ads Manager you are using for the Reach&Frequency predictions
# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction
# ONLY for interests or behaviors audience
# If you ARE NOT using interests, leave audience_name = 'None'
audience_name = 'None' # Add your own Audience name

# Define the amount of days for your Campaign predictions
camp_days = 28

# Set different objectives to siulate
# Different objectives are: 'BRAND_AWARENESS', 'REACH', 'LINK_CLICKS', 'POST_ENGAGEMENT' AND 'VIDEO_VIEWS'
# USE ONLY TWO OBJECTIVES AT ONCE: LIST OF 2 ELEMENTS ONLY
# IDEALLY TO TEST 1 UPPER FUNNNEL OBJECTIVE (REACH OR BRAND_AWARENESS) VERSUS 1 MID FUNNEL OBJECTIVE (LINK_CLICKS,
# POST_ENGAGEMENT OR VIDEO_VIEWS)
camp_objectives = [
    #'REACH',
    'BRAND_AWARENESS',
    'LINK_CLICKS',
    #'POST_ENGAGEMENT',
    #'VIDEO_VIEWS',
]

# Frequency caps
# Needs the maximum number of times your ad will be shown to a person during a specifyed time period
# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days
maximum_cap = 2
every_x_days = 7

# Days before the campaign begins
# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on
# Minimum and default value is 1
days_prior_start = 1

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

# Define the closest match function

def closest(lst, budget): 
      
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-budget))] 

######------------------ESTIMATING REACH & FREQUENCY CURVES SIMULATIONS------------------#####

# IMPORTANT: WE RECOMMEND NOT TO CHANGE expected_reach PARAMETER. PREDICTION STILL WILL PROVIDE VALUES FOR DIFFERENT BUDGETS AND REACH LEVELS
# If need to change, it must be >200000 as this is a requirement to have Reach and Frequency predictions on this same Buying type
expected_reach = 200000 # Integer. Recommended to leave fixed on 200000 

# We define this constant to compute the number of days each campaign should last
secs_per_day = 60 * 60 * 24

# Transform the days before the campaign starts to secs

days_prior_start_sec = days_prior_start * secs_per_day

df_append_sim = pd.DataFrame()

now_time = int(time())

# THIS MODULE ONLY PERFORMS COMBINATIONS OF TWO DIFFERENT OBJECTIVES
# IF YOU HAVE LESS THAN 2 OR GREATER THAN 2 OBJECTIVES THE MODULE WON'S RUN

if len(camp_objectives)==2:

    for objective in camp_objectives:

        # Case when running POST_ENGAGEMENT, as this objective has restrictions on some placements
        if objective == 'POST_ENGAGEMENT':


            prediction = ad_account.create_reach_frequency_prediction(
                params={
                    'start_time': (now_time) + days_prior_start_sec,
                    'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                    'objective': objective, # set the campaign objective
                    'frequency_cap': maximum_cap,
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
                            'search',
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
                    'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                    'objective': objective, # set the campaign objective
                    'frequency_cap': maximum_cap,
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
                            'search',
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
                    'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                    'objective': objective, # set the campaign objective
                    'frequency_cap': maximum_cap,
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
                            'search',
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
                    'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                    'objective': objective, # set the campaign objective
                    'frequency_cap': maximum_cap,
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
                            'search',
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
                    'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                    'objective': objective, # set the campaign objective
                    'frequency_cap': maximum_cap,
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
                            'search',
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


        # Save only relevant data
        clean_df = df[['budget', 'impression', 'reach']]

        # Transforming budget to whole units according to currency
        clean_df['budget'] = clean_df['budget'] /  divider

        # Add objective colums and add useful metrics
        clean_df['objective'] = objective
        clean_df['weeks'] = camp_days / 7
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_freq'] = clean_df.frequency / clean_df['weeks']


        # Append new data 
        df_append_sim = df_append_sim.append(clean_df)

    df_append_sim = df_append_sim.reset_index(drop = True)
    
else:
    print('You have selected ' + str(len(camp_objectives)) + ' campaign objective(s). You have to select exactly 2 objectives')
    
# Create two arrays (independent variables) with the budgets for the objective 1 and objective 2
x_obj_1 = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[0]]['budget'].to_numpy()
x_obj_2 = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[1]]['budget'].to_numpy()

# Create two arrays (dependent variables) with the budgets for different metrics for Objective 1

y_obj_1_reach = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[0]]['reach'].to_numpy()
y_obj_1_impression = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[0]]['impression'].to_numpy()
y_obj_1_frequency = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[0]]['frequency'].to_numpy()
y_obj_1_weekly_freq = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[0]]['weekly_freq'].to_numpy()

# Create two arrays (dependent variables) with the budgets for different metrics for Objective 2
y_obj_2_reach = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[1]]['reach'].to_numpy()
y_obj_2_impression = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[1]]['impression'].to_numpy()
y_obj_2_frequency = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[1]]['frequency'].to_numpy()
y_obj_2_weekly_freq = df_append_sim[df_append_sim['objective'] == df_append_sim.objective.unique()[1]]['weekly_freq'].to_numpy()


# Create the function to interpolate data for Objective 1
f_obj_1_reach = interp1d(x_obj_1, y_obj_1_reach)
f_obj_1_impression = interp1d(x_obj_1, y_obj_1_impression)
f_obj_1_frequency = interp1d(x_obj_1, y_obj_1_frequency)
f_obj_1_weekly_freq = interp1d(x_obj_1, y_obj_1_weekly_freq)

# Create the function to interpolate data for Objective 2
f_obj_2_reach = interp1d(x_obj_2, y_obj_2_reach)
f_obj_2_impression = interp1d(x_obj_2, y_obj_2_impression)
f_obj_2_frequency = interp1d(x_obj_2, y_obj_2_frequency)
f_obj_2_weekly_freq = interp1d(x_obj_2, y_obj_2_weekly_freq)

# Create two lists of different values to be interpolated taking the budget as the reference
obj_1_budget_lst = []
obj_2_budget_lst = []

for i in range(0,101):
    obj_1_budget_lst.append(budget * (i / 100))

for j in range(100,-1, -1):
    obj_2_budget_lst.append(budget * (j / 100))

# Create DataFrames to store interpolated data
df_obj_1_interpolated = pd.DataFrame()
df_obj_2_interpolated = pd.DataFrame()

# Build each dataframe with the interpolated data
df_obj_1_interpolated['budget'] = pd.Series(obj_1_budget_lst)

count_1 = 0
for budget_obj_1 in obj_1_budget_lst:
    
    if budget_obj_1 < x_obj_1.min():
        df_obj_1_interpolated.loc[count_1, 'reach'] = 0
        df_obj_1_interpolated.loc[count_1, 'impression'] = 0
        df_obj_1_interpolated.loc[count_1, 'frequency'] = 0
        df_obj_1_interpolated.loc[count_1, 'weekly_freq'] = 0
        df_obj_1_interpolated.loc[count_1, 'cpm'] = 0
    else:
        df_obj_1_interpolated.loc[count_1, 'reach'] = f_obj_1_reach(budget_obj_1)
        df_obj_1_interpolated.loc[count_1, 'impression'] = f_obj_1_impression(budget_obj_1)
        df_obj_1_interpolated.loc[count_1, 'frequency'] = f_obj_1_frequency(budget_obj_1)
        df_obj_1_interpolated.loc[count_1, 'weekly_freq'] = f_obj_1_weekly_freq(budget_obj_1)
        df_obj_1_interpolated.loc[count_1, 'cpm'] = (df_obj_1_interpolated.loc[count_1,'budget'] / df_obj_1_interpolated.loc[count_1,'impression']) * 1000
        
    count_1 = count_1 + 1
    
    
# Build each dataframe with the interpolated data
df_obj_2_interpolated['budget'] = pd.Series(obj_2_budget_lst)


count_2 = 0
for budget_obj_2 in obj_2_budget_lst:
    
    if budget_obj_2 < x_obj_2.min():
        df_obj_2_interpolated.loc[count_2, 'reach'] = 0
        df_obj_2_interpolated.loc[count_2, 'impression'] = 0
        df_obj_2_interpolated.loc[count_2, 'frequency'] = 0
        df_obj_2_interpolated.loc[count_2, 'weekly_freq'] = 0
        df_obj_2_interpolated.loc[count_2, 'cpm'] = 0
    else:
        df_obj_2_interpolated.loc[count_2, 'reach'] = f_obj_2_reach(budget_obj_2)
        df_obj_2_interpolated.loc[count_2, 'impression'] = f_obj_2_impression(budget_obj_2)
        df_obj_2_interpolated.loc[count_2, 'frequency'] = f_obj_2_frequency(budget_obj_2)
        df_obj_2_interpolated.loc[count_2, 'weekly_freq'] = f_obj_2_weekly_freq(budget_obj_2)
        df_obj_2_interpolated.loc[count_2, 'cpm'] = (df_obj_2_interpolated.loc[count_2,'budget'] / df_obj_2_interpolated.loc[count_2,'impression']) * 1000
        
    count_2 = count_2 + 1
    
# Rename columns to avoid confusion between dataframes

df_obj_1_interpolated.columns = [
    'budget_obj_1',
    'reach_obj_1',
    'impression_obj_1',
    'frequency_obj_1',
    'weekly_freq_obj_1',
    'cpm_obj_1',
    ]

df_obj_2_interpolated.columns = [
    'budget_obj_2',
    'reach_obj_2',
    'impression_obj_2',
    'frequency_obj_2',
    'weekly_freq_obj_2',
    'cpm_obj_2',
    ]


# Join both dataframes
df_interpolated = df_obj_1_interpolated.join(df_obj_2_interpolated, how = 'left')

# Create weighting variables to compute weighted averages for frequency metric
df_interpolated['weight_reach_obj_1'] = df_interpolated['reach_obj_1'] / (df_interpolated['reach_obj_1'] + df_interpolated['reach_obj_2'])
df_interpolated['weight_reach_obj_2'] = df_interpolated['reach_obj_2'] / (df_interpolated['reach_obj_1'] + df_interpolated['reach_obj_2'])

# Compute 'summary' metrics
df_interpolated['total_budget'] = df_interpolated['budget_obj_1'] + df_interpolated['budget_obj_2']
df_interpolated['budget_pct_obj_1'] = df_interpolated['budget_obj_1'] / df_interpolated['total_budget']
df_interpolated['budget_pct_obj_2'] = df_interpolated['budget_obj_2'] / df_interpolated['total_budget']
df_interpolated['sum_reach_not_deduplicated'] = df_interpolated['reach_obj_1'] + df_interpolated['reach_obj_2']
df_interpolated['total_impressions'] = df_interpolated['impression_obj_1'] + df_interpolated['impression_obj_2']
df_interpolated['weighted_average_frequency'] = (df_interpolated['weight_reach_obj_1'] * df_interpolated['frequency_obj_1']) + (df_interpolated['weight_reach_obj_2'] * df_interpolated['frequency_obj_2'])
df_interpolated['weighted_average_weekly_freq'] = (df_interpolated['weight_reach_obj_1'] * df_interpolated['weekly_freq_obj_1']) + (df_interpolated['weight_reach_obj_2'] * df_interpolated['weekly_freq_obj_2'])
df_interpolated['total_cpm'] = (df_interpolated['total_budget'] / df_interpolated['total_impressions']) * 1000

# Add set-up metrics and compute some additional ones
df_interpolated['country'] = country[0]
df_interpolated['gender'] = ' '.join([str(elem) for elem in gender])

# Transform gender codes into readable strings
count = 0
for i in range(0,len(df_interpolated)):
   
    if df_interpolated.loc[count, 'gender'] == '1 2':
        df_interpolated.loc[count,'gender_str'] = 'Female-Male'
    elif df_interpolated.loc[count,'gender'] == '1':
        df_interpolated.loc[count,'gender_str'] = 'Male'
    elif df_interpolated.loc[count,'gender'] == '2':
        df_interpolated.loc[count,'gender_str'] = 'Female'
        
    count = count + 1

# Add set-up variables
df_interpolated['age_min'] = age[0]
df_interpolated['age_max'] = age[1]
df_interpolated['days'] = camp_days
df_interpolated['weeks'] = camp_days / 7
df_interpolated['frequency_cap'] = str(maximum_cap) + ' times every ' + str(every_x_days) + ' days'
df_interpolated['included_interests'] = str(inc_inter_behav)
df_interpolated['excluded_interests'] = str(exc_inter_behav)

# Rename columns to identify predictions for each objective
df_interpolated.columns = [
    'Budget for ' + df_append_sim.objective.unique()[0],
    'Reach for ' + df_append_sim.objective.unique()[0],
    'Impressions for '+ df_append_sim.objective.unique()[0],
    'Frequency for '+ df_append_sim.objective.unique()[0],
    'Weekly Frequency for '+ df_append_sim.objective.unique()[0],
    'CPM for '+ df_append_sim.objective.unique()[0],
    'Budget for'+ df_append_sim.objective.unique()[1],
    'Reach for '+ df_append_sim.objective.unique()[1],
    'Impressions for '+ df_append_sim.objective.unique()[1],
    'Frequency for'+ df_append_sim.objective.unique()[1],
    'Weekly Frequency for '+ df_append_sim.objective.unique()[1],
    'CPM for '+ df_append_sim.objective.unique()[1],
    '% Weight Reach for '+ df_append_sim.objective.unique()[0],
    '% Weight Reach for '+ df_append_sim.objective.unique()[1],
    'Total Budget',
    '% Budget for '+ df_append_sim.objective.unique()[0],
    '% Budget for  '+ df_append_sim.objective.unique()[1],
    'Sum of Reach (NOT deduplicated)',
    'Total Impressions',
    'Weighted Average Frequency',
    'Weighted Average Weekly Frequency',
    'Total CPM',
    'Country',
    'Gender',
    'Gender Label',
    'Age min',
    'Age max',
    'Campaign days',
    'Campaign weeks',
    'Frequency Caps',
    'Included interests',
    'Excluded interests',    
    ]

# Identify specs combinations that maximize reach, weekly frequency and minimize CPM
reach_optim = df_interpolated[(df_interpolated['Sum of Reach (NOT deduplicated)'] == df_interpolated['Sum of Reach (NOT deduplicated)'].max())]
weekly_freq_optim = df_interpolated[(df_interpolated['Weighted Average Weekly Frequency'] == df_interpolated['Weighted Average Weekly Frequency'].max())]
cpm_optim = df_interpolated[(df_interpolated['Total CPM'] == df_interpolated['Total CPM'].min())]

# Create a new dataframe and store all optims in it
df_optimized = pd.DataFrame()
df_optimized = df_optimized.append(reach_optim)
df_optimized = df_optimized.append(weekly_freq_optim)
df_optimized = df_optimized.append(cpm_optim)

# Reset index
df_optimized = df_optimized.reset_index(drop = True)

# Add a scenario column to identigy optimizations
df_optimized.loc[0, 'Scenario'] = 'Maximum Sum of Reach (NOT Deduplicated)'
df_optimized.loc[1, 'Scenario'] = 'Maximum Weighted Average Weekly Frequency'
df_optimized.loc[2, 'Scenario'] = 'Minimum Total CPM'

# Export both, full data and optimized scenarios
export_csv = df_interpolated.to_csv(r'' + save_directory + '/Module_08_Objectives_Mix_' + advertiser_name + '_' + ad_account_index + '.csv', header=True, index = None)
export_csv = df_optimized.to_csv(r'' + save_directory + '/Module_08_Objectives_Mix_Optimized_' + advertiser_name + '_' + ad_account_index + '.csv', header=True, index = None)