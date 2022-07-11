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


#------------------------START Module_01_Massive_Reach_Right_Objective----------------------------#


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


#---------------------------------------------INPUT 01----------------------------------------------#
# Include your own access token instead of xxxxxx
access_token = 'xxxxxxx'

# Make sure you are using the latest API version
# You can double check on: https://developers.facebook.com/docs/graph-api/guides/versioning
api_version = 'v14.0'

# Initiate the Facebook Business API with the access token
api = FacebookAdsApi.init(
    access_token = access_token,
    api_version = api_version,
)

# Set the Ad Account on which you want to have the predictions. Replace the xxxxxx with your own Account ID
ad_account_id = 'act_xxxxxxx'

# Write the directory where you want to save all the OUTPUTS
save_directory = 'C:/Users/username/Desktop/' # this is just an example on PC


#---------------------------------------------INPUT 02----------------------------------------------#

# Input all the campaing specs for your prediction
# Input the minimum and maximum ages
age_min = 18
age_max = 65

# Input the genders. 2-for female, 1-for male
gender_list = [1,2]

# Input the country for the ads delivery
# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web
countries = ['MX'] 


# IMPORTANT: WE RECOMMEND NOT TO CHANGE expected_reacg PARAMETER. PREDICTION STILL WILL PROVIDE VALUES FOR DIFFERENT BUDGETS AND REACH LEVELS
# If need to change, it must be >200000 as this is a requirement to have Reach and Frequency predictions on this same Buying type
expected_reach = 200000 # Integer. Recommended to leave fixed on 200000 

# Define the amount of days for your Campaign predictions
camp_days = 28 # The maximum days that the prediction can be done is 89 within a 6 months window from now

# Frequency caps
# Needs the maximum number of times your ad will be shown to a person during a specifyed time period
# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days
frequency_cap = 2
every_x_days = 7

# When using interest-behavior based audiences, make sure that you have already save the audience in the 
# same AdAccount in Ads Manager you are using for the Reach&Frequency predictions
# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction
# ONLY for interests or behaviors audience
# If you ARE NOT using interests, leave audience_name = 'None'
audience_name = 'None'

# Days before the campaign begins
# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on
# Minimum and default value is 1
days_prior_start = 7

# Define the size of each currency increment for interpolating curves
# Example: having a currency in USD, a 100 increment means that starting from the lowest budget value, let's say 12,000 USD
# we'll have: 12000 USD, 12100 USD, 12200 USD, 12300 USD, 12400 USD and so on until reaching the max budget value for each curve
# IMPORTANT: the lower the currency_incr, the higher the amount of time for interpolating values
currency_incr = 10000 # Integer


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


# IMPORTANT: This code only works if you ARE ABOUT TO CONSIDER ONE OF THE FOLLOWING OBJETIVES
# FOR YOUR CAMPAIGN: REACH, BRAND_AWARENESS, VIDEO_VIEWS, POST_ENGAGEMENT or LINK_CLICKS (TRAFFIC)

# Define the list of objectives availables for this module.
# This 5 objectives are used because the approach of the Planning Excellence Toolkit
# is focused on Branding campaigns

objectives_list = ['REACH', 'BRAND_AWARENESS', 'VIDEO_VIEWS', 'POST_ENGAGEMENT', 'LINK_CLICKS']



# Create a variable that contains the amount of seconds for one day. This will be used on the Campaign Dates
secs_per_day = 60 * 60 * 24

# Transform the days before the campaign starts to secs
days_prior_start_sec = days_prior_start * secs_per_day

# Convert campaign days duration to weeks
weeks = days / 7


# Compute the Unix time for 'now'. This will be used on the dates
now_time = int(time())

# Create a DataFrame and a list that will be used to append and store data from the predictions

append_clean_df = pd.DataFrame()
lst_min_budgets = []

# Create a for loop to make calls on each objective, as each one of them has specific placement specs to work on
for objective in objectives_list:

    print('Running: ' + objective + ' objective')
    # Make the predictions call for each OBJECTIVE
    
    # Case when running POST_ENGAGEMENT, as this objective has restrictions on some placements
    if objective == 'POST_ENGAGEMENT':
        
        
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

        # Convert the JSON data to a DataFrame
        df = pd.DataFrame(
            data = response.json()['curve_budget_reach'],
        )

        # Keep main metrics
        clean_df = df[['budget', 'impression', 'reach']]

        # Create some other fields that are relevant when analzing data curves
        clean_df['budget'] = clean_df.budget / divider 
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (camp_days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Post Engagement'
        clean_df['audience_name'] = audience_name
        
        
        # Create a list to store the minimum budget for each objective    
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))
        
        
    # Case when running LINK_CLICKS, as this objective has restrictions on some placements
    
    elif objective == 'LINK_CLICKS': 
        
        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': frequency_cap,
                'interval_frequency_cap_reset_period': (every_x_days * 24),
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
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
        clean_df['budget'] = clean_df.budget / divider 
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (camp_days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Link Clicks'
        clean_df['audience_name'] = audience_name
        
        
        # Create a list to store the minimum budget for each objective
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))

        
    # Case when running REACH objective
    elif objective == 'REACH':
        
    
        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': frequency_cap,
                'interval_frequency_cap_reset_period': (every_x_days * 24),
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
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
        clean_df['budget'] = clean_df.budget / divider 
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (camp_days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Reach'
        clean_df['audience_name'] = audience_name
        
        
        # Create a list to store the minimum budget for each objective
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))
        
    # Case when running BRAND_AWARENESS objective
        
    elif objective == 'BRAND_AWARENESS':
        
    
        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': frequency_cap,
                'interval_frequency_cap_reset_period': (every_x_days * 24),
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
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
        clean_df['budget'] = clean_df.budget / divider 
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (camp_days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Brand Awareness'
        clean_df['audience_name'] = audience_name
        
        # Create a list to store the minimum budget for each objective
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))

        
    # Case when running VIDEO_VIEWS objective
        
    elif objective == 'VIDEO_VIEWS':
        
    
        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + days_prior_start_sec + (camp_days * secs_per_day)), (now_time + days_prior_start_sec + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': frequency_cap,
                'interval_frequency_cap_reset_period': (every_x_days * 24),
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
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
        clean_df['budget'] = clean_df.budget / divider 
        clean_df['included_interests'] = str(inc_inter_behav)
        clean_df['excluded_interests'] = str(exc_inter_behav_str)

        
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (camp_days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Video Views'
        clean_df['audience_name'] = audience_name
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))
        
    append_clean_df = append_clean_df.append(clean_df)
        
append_clean_df = append_clean_df.reset_index(drop = True)
        

append_clean_df


# Define a minimum budget to have all the curves comparison
min_budget = np.ceil(
    max(lst_min_budgets)
    )

# Define a maximum budget to have all the curves comparison
max_budget = np.floor(
    max(append_clean_df['budget']
        )
    )

# Define the amount of steps/increments of currency_incr we'll have for the interpolations
n_steps = int(np.floor((max_budget - min_budget) / currency_incr))

# Create the dataframe where the standardized data will be stored
df_all_curves = pd.DataFrame()

# All curves will begin from the same minimum budget to have cross comparisons
cum_budget = min_budget


# Create the budget standardized field with the currency increments we have defined previously
count = 0
for i in range(0, n_steps):
        
        df_all_curves.loc[count, 'budget'] = cum_budget + currency_incr
        
        cum_budget = df_all_curves.loc[count, 'budget']
        count = count + 1
        


df_all_curves


# Create the closest match function to identify the closest values when interpolating each budget
def closest(lst, eval_budget): 
      
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-eval_budget))] 
    


# Create a DataFrame to save all the new fields and interpolated vales
temp_df_02 = pd.DataFrame()
append_interpolated = pd.DataFrame()

# Each intepolation on the standardized budgets will be run for each objective
for objective in tqdm(append_clean_df['objective'].unique()):

    temp_df_02 = append_clean_df[append_clean_df['objective'] == objective].reset_index(drop = True)
    
    # This section splits the different objectives to run the interpolations in chunks for each dataframe
    count =  0
    
    for i in range(0, len(df_all_curves)):
        
        # Split the code into two sections to consider NaNs when your simulated reach is higher that the
        # mamixum possible reach for each objective or lower than the minimum possible reach 

        if df_all_curves.loc[count, 'budget'] < max(temp_df_02['budget']):
            
            
            if (closest(temp_df_02['budget'], df_all_curves.loc[count, 'budget'])) < df_all_curves.loc[count, 'budget']:

                df_all_curves.loc[count, 'closest_budget_inf'] = (closest(temp_df_02['budget'], df_all_curves.loc[count, 'budget']))
                inf_index = temp_df_02[temp_df_02['budget'] == df_all_curves.loc[count, 'closest_budget_inf']].index.values[0]
                df_all_curves.loc[count, 'closest_budget_sup'] = temp_df_02.loc[inf_index + 1, 'budget']

                df_all_curves.loc[count, 'closest_impressions_inf'] = temp_df_02.loc[inf_index, 'impression']
                df_all_curves.loc[count, 'closest_reach_inf'] = temp_df_02.loc[inf_index, 'reach']
                df_all_curves.loc[count, 'closest_frequency_inf'] = temp_df_02.loc[inf_index, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_inf'] = temp_df_02.loc[inf_index, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_inf'] = temp_df_02.loc[inf_index, 'cpm']

                df_all_curves.loc[count, 'closest_impressions_sup'] = temp_df_02.loc[inf_index + 1, 'impression']
                df_all_curves.loc[count, 'closest_reach_sup'] = temp_df_02.loc[inf_index + 1, 'reach']
                df_all_curves.loc[count, 'closest_frequency_sup'] = temp_df_02.loc[inf_index + 1, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_sup'] = temp_df_02.loc[inf_index + 1, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_sup'] = temp_df_02.loc[inf_index + 1, 'cpm']
                

            else:

                df_all_curves.loc[count, 'closest_budget_sup'] = (closest(temp_df_02['budget'], df_all_curves.loc[count, 'budget']))
                sup_index = temp_df_02[temp_df_02['budget'] == df_all_curves.loc[count, 'closest_budget_sup']].index.values[0]
                df_all_curves.loc[count, 'closest_budget_inf'] = temp_df_02.loc[sup_index - 1, 'budget']

                df_all_curves.loc[count, 'closest_impressions_inf'] = temp_df_02.loc[sup_index, 'impression']
                df_all_curves.loc[count, 'closest_reach_inf'] = temp_df_02.loc[sup_index, 'reach']
                df_all_curves.loc[count, 'closest_frequency_inf'] = temp_df_02.loc[sup_index, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_inf'] = temp_df_02.loc[sup_index, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_inf'] = temp_df_02.loc[sup_index, 'cpm']

                df_all_curves.loc[count, 'closest_impressions_sup'] = temp_df_02.loc[sup_index - 1, 'impression']
                df_all_curves.loc[count, 'closest_reach_sup'] = temp_df_02.loc[sup_index - 1, 'reach']
                df_all_curves.loc[count, 'closest_frequency_sup'] = temp_df_02.loc[sup_index - 1, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_sup'] = temp_df_02.loc[sup_index - 1, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_sup'] = temp_df_02.loc[sup_index - 1, 'cpm']
                

            df_all_curves.loc[count, 'impressions_itp'] = (((df_all_curves.loc[count, 'closest_impressions_sup'] - df_all_curves.loc[count, 'closest_impressions_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_impressions_inf']
            df_all_curves.loc[count, 'reach_itp'] = (((df_all_curves.loc[count, 'closest_reach_sup'] - df_all_curves.loc[count, 'closest_reach_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_reach_inf']
            df_all_curves.loc[count, 'frequency_itp'] = (((df_all_curves.loc[count, 'closest_frequency_sup'] - df_all_curves.loc[count, 'closest_frequency_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_frequency_inf']
            df_all_curves.loc[count, 'weekly_freq_itp'] = (((df_all_curves.loc[count, 'closest_weekly_freq_sup'] - df_all_curves.loc[count, 'closest_weekly_freq_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_weekly_freq_inf']
            df_all_curves.loc[count, 'cpm_itp'] = (((df_all_curves.loc[count, 'closest_cpm_sup'] - df_all_curves.loc[count, 'closest_cpm_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_cpm_inf']

            
        # Case when the budgets are out of the predictions budget range for each field
        else:
            df_all_curves.loc[count, ['closest_budget_inf', 
                                      'closest_impressions_inf',
                                      'closest_reach_inf',
                                      'closest_frequency_inf',
                                      'closest_weekly_freq_inf',
                                      'closest_cpm_inf',
                                      'closest_budget_sup',
                                      'closest_impressions_sup',
                                      'closest_reach_sup',
                                      'closest_frequency_sup',
                                      'closest_weekly_freq_sup',
                                      'closest_cpm_sup',
                                      'impressions_itp',
                                      'reach_itp',
                                      'frequency_itp',
                                      'weekly_freq_itp',
                                      'cpm_itp',
                                      ]] = float('Nan')
            

        count = count + 1
    
    # Add the column name for the objective
    df_all_curves['objective'] = objective
    
    # Append the dataframe to the previous one
    append_interpolated =  append_interpolated.append(df_all_curves)
    
# Adding reach in percentage relative to estimated audience sizes
append_interpolated['reach_lower_bound_pct_ipt'] = append_interpolated['reach_itp'] / results['audience_size_upper_bound']
append_interpolated['reach_upper_bound_pct_ipt'] = append_interpolated['reach_itp'] / results['audience_size_lower_bound']


# Keep relevant fields
append_interpolated = append_interpolated[[
    'budget',
    'impressions_itp', 
    'reach_itp', 
    'reach_lower_bound_pct_ipt',
    'reach_upper_bound_pct_ipt',
    'frequency_itp', 
    'weekly_freq_itp', 
    'cpm_itp',
    'objective',
    ]]


# Reshape the dataframe to un-stack it
pivot_interpolated = append_interpolated.pivot(index = 'budget', columns = 'objective').reset_index('budget')


# Merge the column names after the pivoting
pivot_interpolated.columns = ['_'.join((j, k)) for j, k in pivot_interpolated]


# Save the predictions data in the save_directory
export_csv = pivot_interpolated.to_csv(r'' + save_directory + '01_Right_Objective_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.csv', header=True, index = None)


# Select a style for the charts
get_ipython().run_line_magic('matplotlib', 'inline')
plt.style.use('seaborn-whitegrid')

# Plot the Reach and Frequency Curves for Reach (people)
fig, ax = plt.subplots()
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_Reach']/1000000, label = 'Reach', color = '#8dd3c7')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_Brand Awareness']/1000000, label = 'Brand Awareness', color = '#fdb462')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_Link Clicks']/1000000, label = 'Link Clicks', color = '#80b1d3')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_Post Engagement']/1000000, label = 'Post Engagement', color = '#b3de69')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_Video Views']/1000000, label = 'Video Views', color = '#fb8072')
leg = ax.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Reach (Millions)')
plt.title('Optimizing with Right Objectives \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));
plt.title('Optimizing with Right Objectives');

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '01_Reach_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Total frequency
fig, bx = plt.subplots()
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_Reach'], label = 'Reach', color = '#8dd3c7')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_Brand Awareness'], label = 'Brand Awareness', color = '#fdb462')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_Link Clicks'], label = 'Link Clicks', color = '#80b1d3')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_Post Engagement'], label = 'Post Engagement', color = '#b3de69')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_Video Views'], label = 'Video Views', color = '#fb8072')
leg = bx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Total frequency')
plt.title('Optimizing with Right Objectives \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '01_Total_frequency_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Cost Per Mille (CPM)
fig, cx = plt.subplots()
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_Reach'], label = 'Reach', color = '#8dd3c7')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_Brand Awareness'], label = 'Brand Awareness', color = '#fdb462')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_Link Clicks'], label = 'Link Clicks', color = '#80b1d3')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_Post Engagement'], label = 'Post Engagement', color = '#b3de69')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_Video Views'], label = 'Video Views', color = '#fb8072')
leg = cx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('CPM (' + str(acc_currency) + ')')
plt.title('Optimizing with Right Objectives \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '01_CPM_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Weekly frequency
fig, dx = plt.subplots()
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_Reach'], label = 'Reach', color = '#8dd3c7')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_Brand Awareness'], label = 'Brand Awareness', color = '#fdb462')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_Link Clicks'], label = 'Link Clicks', color = '#80b1d3')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_Post Engagement'], label = 'Post Engagement', color = '#b3de69')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_Video Views'], label = 'Video Views', color = '#fb8072')
leg = dx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Weekly frequency')
plt.title('Optimizing with Right Objectives \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '01_Weekly_frequency_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Reach lower bound % (on-target)
fig, ex = plt.subplots()
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_lower_bound_pct_ipt_Reach']*100, label = 'Reach', color = '#8dd3c7')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_lower_bound_pct_ipt_Brand Awareness']*100, label = 'Brand Awareness', color = '#fdb462')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_lower_bound_pct_ipt_Link Clicks']*100, label = 'Link Clicks', color = '#80b1d3')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_lower_bound_pct_ipt_Post Engagement']*100, label = 'Post Engagement', color = '#b3de69')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_lower_bound_pct_ipt_Video Views']*100, label = 'Video Views', color = '#fb8072')
leg = ex.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Reach lower bound % (on-target)')
plt.title('Optimizing with Right Objectives \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '01_Reach_lower_pct_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Reach upper bound % (on-target)
fig, ex = plt.subplots()
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_upper_bound_pct_ipt_Reach']*100, label = 'Reach', color = '#8dd3c7')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_upper_bound_pct_ipt_Brand Awareness']*100, label = 'Brand Awareness', color = '#fdb462')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_upper_bound_pct_ipt_Link Clicks']*100, label = 'Link Clicks', color = '#80b1d3')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_upper_bound_pct_ipt_Post Engagement']*100, label = 'Post Engagement', color = '#b3de69')
ex.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_upper_bound_pct_ipt_Video Views']*100, label = 'Video Views', color = '#fb8072')
leg = ex.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Reach upper bound % (on-target)')
plt.title('Optimizing with Right Objectives \n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));

# Save the pdf in the save_directory
plt.savefig(r'' + save_directory + '01_Reach_upper_pct_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


#----------------------------------END REACH AND FREQUENCY PREDICTIONS--------------------------------#


# Additional resources on

# Reach & Frequency Fields: https://developers.facebook.com/docs/marketing-api/reference/reach-frequency-prediction
# Currencies: https://developers.facebook.com/docs/marketing-api/currencies

# Platforms that cannot work with the following objectives

# Audience Network cannot work with:
# 1. LINK_CLICKS
# 2. CONVERSIONS

# Messenger cannot work with any objective

