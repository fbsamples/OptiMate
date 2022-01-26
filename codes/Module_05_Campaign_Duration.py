#Copyright (c) Facebook, Inc. and its affiliates.
#All rights reserved.

#This source code is licensed under the license found in the
#LICENSE file in the root directory of this source tree.

# Import libraries
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from time import time
from time import sleep
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import requests
import matplotlib.pyplot as plt
from tqdm import tqdm

#---------------------------------------START INPUT SECTION-----------------------------------------#

#---------------------------------------------INPUT 01----------------------------------------------#

# Include your own access token instead of xxxxxx
access_token = 'xxxxxx'
api = FacebookAdsApi.init(
    access_token = access_token,
)

# Set the Ad Account on which you want to have the predictions. Replace the xxxxxx with your own Account ID
ad_account_id = 'act_xxxxxxx'

# Choose an index to be added to your CSV output files
ad_account_index = 'xx'

# Choose a name to be added to your CSV output files
advertiser_name = 'xxx'

# Write the directory where you want to save all the OUTPUTS
save_directory = 'C:/Users/user_name/Desktop/' # this is just an example on PC

# Make sure you are using the latest API version
# You can double check on: https://developers.facebook.com/docs/graph-api/guides/versioning
api_version = 'v11.0'

# Define the Audience specs you want to use for your prediction
# Depending on the Audience definition you will be able to have a higher or lower reach results

# Set the objective
# Different objectives are: 'BRAND_AWARENESS', 'REACH', 'LINK_CLICKS', 'POST_ENGAGEMENT' AND 'VIDEO_VIEWS'
objective = 'BRAND_AWARENESS'


# Input all the campaing specs for your prediction
# Input the minimum and maximum ages
age_min = 18
age_max = 65

# Input the genders. 2-for female, 1-for male
gender = [1,2]

# Add a label to better identify the gender spec
gender_str = 'Female-Male' 

# Input the country for the ads delivery
# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web
countries = ['MX'] 


# IMPORTANT: WE RECOMMEND NOT TO CHANGE expected_reacg PARAMETER. PREDICTION STILL WILL PROVIDE VALUES FOR DIFFERENT BUDGETS AND REACH LEVELS
# If need to change, it must be >200000 as this is a requirement to have Reach and Frequency predictions on this same Buying type
expected_reach = 200000 # Integer. Recommended to leave fixed on 200000 

# Define the amount of days for your Campaign predictions
campaign_days = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84 ] # The maximum days that the prediction can be done is 89 within a 6 months window from now

weekly_freq_cap = 2 # Weekly frequency caps list

# Create a list with your interest IDs
# You can use the Targeting_Interest_Search.py code to find your specific Interest IDs
# Leave empty if not using interest targeting
interest_list = [
    #{
    #    'id':'6003161475030', # Ex. Comedy Movies
    #    'id':'6003223339834', # Ex. Culture
    #    }
    ]

# Define the size of each currency increment for interpolating curves
# Example: having a currency in USD, a 100 increment means that starting from the lowest budget value, let's say 12,000 USD
# we'll have: 12000 USD, 12100 USD, 12200 USD, 12300 USD, 12400 USD and so on until reaching the max budget value for each curve
# IMPORTANT: the lower the currency_incr, the higher the amount of time for interpolating values
currency_incr = 100000 #integer

#---------------------------------------END INPUT SECTION-----------------------------------------#

# We define this constant to compute the number of days each campaign should last
secs_per_day = 60 * 60 * 24

# Initiatie the API call on the defined Ad Account

ad_account = AdAccount(
    fbid = ad_account_id,
    api = api,
)

# Make a call to the Ad Account to know the currency it is set up,
# Depending on this, the predictions will be in cents or not

# More information about Currencies
# https://developers.facebook.com/docs/marketing-api/currencies

#insights_accounts = pd.DataFrame()

fields_01 = [
    'account_currency',
    'account_id',
    'account_name',    
]

# It does not matter the 'since' and 'until' dates as long as the period within the Account is active is covered
# It is used then, 'today' date to make sure it is an active account
params_01 = {
    'level': 'account', # different levels are: account, campaign, adset and ad
    'time_range': { 'since': str(pd.to_datetime('today'))[0:10], 'until': str(pd.to_datetime('today'))[0:10] },
}


insights = AdAccount(ad_account_id).get_insights(
    fields = fields_01,
    params = params_01,
    )


acc_currency = insights[0]['account_currency']
acc_id = insights[0]['account_id']
acc_name = insights[0]['account_name']

# Transform the budget_your_currency units to the ones the API will be using (usually in cents)

if (acc_currency in ['CLP', 'COP', 'CRC', 'HUF', 'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']):
    
    divider = 1
else:
    
    divider = 100

# Fetch past adsets results to have a valid list of Facebook Page IDs to work on the predictions

# Set only promoted_object field
fields = [
    'promoted_object'
]

# Fetch the Facebook Page IDs as one of them will be needed when using Facebook placements and positions (Feed, Story, Search, etc.)
objects = AdAccount(ad_account_id).get_ad_sets(
    fields = fields
    )
# Create a copy of objects
fb_promoted_object = objects[:]

# Create an empty DataFrame to store pages IDs

df_fb_page = pd.DataFrame()
count = 0

# Save valids page_id in a DataFrame
for pages in fb_promoted_object:
    try:
        df_fb_page.loc[count, 'id'] = pages['promoted_object']['page_id']
    except:
        df_fb_page.loc[count, 'id'] = float('nan')
    count = count + 1
    
# Exclude NaN values from the DataFrame
df_fb_page = df_fb_page.dropna()
df_fb_page = df_fb_page.reset_index(drop =True)

# Fetch Instagram Account IDs as one of them will be needed when using Instagram placements and positions (Feed, Story, Explore, etc.)
# Fetching the Instagram Account ID
ig_account = AdAccount(ad_account_id).get_instagram_accounts()

# Convert the JSON to a DataFrame
df_ig_account = pd.DataFrame.from_dict(ig_account)

# Exclude empty rows
df_ig_account = df_ig_account.dropna()

# Reset index
df_ig_account = df_ig_account.reset_index(drop =True)

# For making the predictions, it is only needed one Facebook page ID and one Instagram ID related to the Ad Account
# It can be used any of the previous Page ID and Instagram ID from the previous calls
fb_ig_ids = [int(df_fb_page.loc[0, 'id']), int(df_ig_account.loc[0, 'id'])] 

######------------------ESTIMATING REACH & FREQUENCY CURVES SIMULATIONS------------------#####

append_clean_df = pd.DataFrame()
lst_min_budgets = []
lst_end_dates = []

count = 0
now_time = int(time())

starts_camp_dates = now_time


for days in campaign_days:

    lifetime_freq_control = int((days/7) * weekly_freq_cap)

    # Case when running POST_ENGAGEMENT, as this objective has restrictions on some placements
    if objective == 'POST_ENGAGEMENT':

        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + secs_per_day + (days * secs_per_day)), (now_time + secs_per_day + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': lifetime_freq_control, # define a frequency cap over all the campaign duration (lifetime frequency cap)
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, no needed when using 'prediction_mode': 0
                'reach': expected_reach,
                'destination_ids': fb_ig_ids, 
                'target_spec': {
                    'age_min': age_min, # mininum age in years
                    'age_max': age_max, # maximum age in years
                    'genders': gender, # 2-for female, 1-for male
                    'geo_locations': {
                        'countries': countries,
                    },

                    # When using Interest based Audiences, you need to specify the ID
                    # For fetching the right Interest ID, you can use the Targeting Search Library
                    #'interests': [
                    #    {
                    #        'id':'6003161475030', # Ex. Comedy Movies
                    #        'id':'6003223339834', # Ex. Culture
                    #   }
                    #],

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
        clean_df['gender'] = gender_str
        clean_df['age_min'] = age_min
        clean_df['age_max'] = age_max
        clean_df['days'] = days
        clean_df['weekly_frequency_cap'] = weekly_freq_cap
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Post Engagement'
        clean_df['reach_pct'] = clean_df['reach'] / clean_df['reach'].max()

        # Create a list to store the minimum budget for each objective    
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))


    # Case when running LINK_CLICKS, as this objective has restrictions on some placements

    elif objective == 'LINK_CLICKS': 

        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + secs_per_day + (days * secs_per_day)), (now_time + secs_per_day + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': lifetime_freq_control, # define a frequency cap over all the campaign duration (lifetime frequency cap)
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
                'reach': expected_reach,
                'destination_ids': fb_ig_ids, 
                'target_spec': {
                    'age_min': age_min, # mininum age in years
                    'age_max': age_max, # maximum age in years
                    'genders': gender, # 2-for female, 1-for male
                    'geo_locations': {
                        'countries': countries,
                    },

                    # When using Interest based Audiences, you need to specify the ID
                    # For fetching the right Interest ID, you can use the Targeting Search Library
                    #'interests': [
                    #    {
                    #        'id':'6003161475030', # Ex. Comedy Movies
                    #        'id':'6003223339834', # Ex. Culture
                    #   }
                    #],

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
        clean_df['gender'] = gender_str
        clean_df['age_min'] = age_min
        clean_df['age_max'] = age_max
        clean_df['days'] = days
        clean_df['weekly_frequency_cap'] = weekly_freq_cap
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Link Clicks'
        clean_df['reach_pct'] = clean_df['reach'] / clean_df['reach'].max()

        # Create a list to store the minimum budget for each objective
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))


    # Case when running REACH objective
    elif objective == 'REACH':


        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + secs_per_day + (days * secs_per_day)), (now_time + secs_per_day + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': lifetime_freq_control, # define a frequency cap over all the campaign duration (lifetime frequency cap)
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
                'reach': expected_reach,
                'destination_ids': fb_ig_ids, 
                'target_spec': {
                    'age_min': age_min, # mininum age in years
                    'age_max': age_max, # maximum age in years
                    'genders': gender, # 2-for female, 1-for male
                    'geo_locations': {
                        'countries': countries,
                    },

                    # When using Interest based Audiences, you need to specify the ID
                    # For fetching the right Interest ID, you can use the Targeting Search Library
                    #'interests': [
                    #    {
                    #        'id':'6003161475030', # Ex. Comedy Movies
                    #        'id':'6003223339834', # Ex. Culture
                    #   }
                    #],

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
        clean_df['gender'] = gender_str
        clean_df['age_min'] = age_min
        clean_df['age_max'] = age_max
        clean_df['days'] = days
        clean_df['weekly_frequency_cap'] = weekly_freq_cap
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Reach'
        clean_df['reach_pct'] = clean_df['reach'] / clean_df['reach'].max()

        # Create a list to store the minimum budget for each objective
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))

    # Case when running BRAND_AWARENESS objective

    elif objective == 'BRAND_AWARENESS':


        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + secs_per_day + (days * secs_per_day)), (now_time + secs_per_day + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': lifetime_freq_control, # define a frequency cap over all the campaign duration (lifetime frequency cap)
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
                'reach': expected_reach,
                'destination_ids': fb_ig_ids, 
                'target_spec': {
                    'age_min': age_min, # mininum age in years
                    'age_max': age_max, # maximum age in years
                    'genders': gender, # 2-for female, 1-for male
                    'geo_locations': {
                        'countries': countries,
                    },

                    # When using Interest based Audiences, you need to specify the ID
                    # For fetching the right Interest ID, you can use the Targeting Search Library
                    #'interests': [
                    #    {
                    #        'id':'6003161475030', # Ex. Comedy Movies
                    #        'id':'6003223339834', # Ex. Culture
                    #   }
                    #],

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
        clean_df['gender'] = gender_str
        clean_df['age_min'] = age_min
        clean_df['age_max'] = age_max
        clean_df['days'] = days
        clean_df['weekly_frequency_cap'] = weekly_freq_cap
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Brand Awareness'
        clean_df['reach_pct'] = clean_df['reach'] / clean_df['reach'].max()

        # Create a list to store the minimum budget for each objective
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))


    # Case when running VIDEO_VIEWS objective

    elif objective == 'VIDEO_VIEWS':


        prediction = ad_account.create_reach_frequency_prediction(
            params={
                'start_time': (now_time) + secs_per_day,
                'end_time': min((now_time + secs_per_day + (days * secs_per_day)), (now_time + secs_per_day + (89*secs_per_day))),
                'objective': objective, # set the campaign objective
                'frequency_cap': lifetime_freq_control, # define a frequency cap over all the campaign duration (lifetime frequency cap)
                'prediction_mode': 0, # predicion mode 1 is for predicting Reach by providing budget, prediction mode 0 is for predicting Budget given a specific Reach
                #'budget': budget, 
                'reach': expected_reach,
                'destination_ids': fb_ig_ids, 
                'target_spec': {
                    'age_min': age_min, # mininum age in years
                    'age_max': age_max, # maximum age in years
                    'genders': gender, # 2-for female, 1-for male
                    'geo_locations': {
                        'countries': countries,
                    },

                    # When using Interest based Audiences, you need to specify the ID
                    # For fetching the right Interest ID, you can use the Targeting Search Library
                    #'interests': [
                    #    {
                    #        'id':'6003161475030', # Ex. Comedy Movies
                    #        'id':'6003223339834', # Ex. Culture
                    #   }
                    #],

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
        clean_df['gender'] = gender_str
        clean_df['age_min'] = age_min
        clean_df['age_max'] = age_max
        clean_df['days'] = days
        clean_df['weekly_frequency_cap'] = weekly_freq_cap
        clean_df['frequency'] = clean_df.impression / clean_df.reach
        clean_df['weekly_frequency'] = clean_df.frequency / (days/7)
        clean_df['cpm'] = clean_df.budget / clean_df.impression * 1000
        clean_df['objective'] = 'Video Views'
        clean_df['reach_pct'] = clean_df['reach'] / clean_df['reach'].max()
        lst_min_budgets.append(int(clean_df.loc[0, 'budget']))

    append_clean_df = append_clean_df.append(clean_df)
append_clean_df = append_clean_df.reset_index(drop = True)
append_clean_df['days'] = append_clean_df['days'].astype(int)

# Defining the minimum budget to have al the curves comparison

min_budget = np.ceil(
    max(lst_min_budgets)
    )


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
        
# Create the closest match function to match the defined budget to the closest value on the Reach&Frequency prediction

def closest(lst, eval_budget): 
      
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-eval_budget))] 
    

temp_df_02 = pd.DataFrame()
append_interpolated = pd.DataFrame()

for days in tqdm(append_clean_df['days'].unique()):

    temp_df_02 = append_clean_df[append_clean_df['days'] == days].reset_index(drop = True)
    
    
    
    # This section splits the different weekly frequency control caps to run the interpolations in chunks for each dataframe
    count =  0
    
    for i in range(0, len(df_all_curves)):
    
        # Split the code into two sections to consider NaNs when your simulated reach is higher that the
        # mamixum possible reach for each objective

        if df_all_curves.loc[count, 'budget'] < max(temp_df_02['budget']):
            
            
            if (closest(temp_df_02['budget'], df_all_curves.loc[count, 'budget'])) < df_all_curves.loc[count, 'budget']:

                df_all_curves.loc[count, 'closest_budget_inf'] = (closest(temp_df_02['budget'], df_all_curves.loc[count, 'budget']))
                inf_index = temp_df_02[temp_df_02['budget'] == df_all_curves.loc[count, 'closest_budget_inf']].index.values[0]
                df_all_curves.loc[count, 'closest_budget_sup'] = temp_df_02.loc[inf_index + 1, 'budget']

                df_all_curves.loc[count, 'closest_impressions_inf'] = temp_df_02.loc[inf_index, 'impression']
                df_all_curves.loc[count, 'closest_reach_inf'] = temp_df_02.loc[inf_index, 'reach']
                df_all_curves.loc[count, 'closest_reach_pct_inf'] = temp_df_02.loc[inf_index, 'reach_pct']
                df_all_curves.loc[count, 'closest_frequency_inf'] = temp_df_02.loc[inf_index, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_inf'] = temp_df_02.loc[inf_index, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_inf'] = temp_df_02.loc[inf_index, 'cpm']

                df_all_curves.loc[count, 'closest_impressions_sup'] = temp_df_02.loc[inf_index + 1, 'impression']
                df_all_curves.loc[count, 'closest_reach_sup'] = temp_df_02.loc[inf_index + 1, 'reach']
                df_all_curves.loc[count, 'closest_reach_pct_sup'] = temp_df_02.loc[inf_index + 1, 'reach_pct']
                df_all_curves.loc[count, 'closest_frequency_sup'] = temp_df_02.loc[inf_index + 1, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_sup'] = temp_df_02.loc[inf_index + 1, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_sup'] = temp_df_02.loc[inf_index + 1, 'cpm']
                

            else:

                df_all_curves.loc[count, 'closest_budget_sup'] = (closest(temp_df_02['budget'], df_all_curves.loc[count, 'budget']))
                sup_index = temp_df_02[temp_df_02['budget'] == df_all_curves.loc[count, 'closest_budget_sup']].index.values[0]
                df_all_curves.loc[count, 'closest_budget_inf'] = temp_df_02.loc[sup_index - 1, 'budget']

                df_all_curves.loc[count, 'closest_impressions_inf'] = temp_df_02.loc[sup_index, 'impression']
                df_all_curves.loc[count, 'closest_reach_inf'] = temp_df_02.loc[sup_index, 'reach']
                df_all_curves.loc[count, 'closest_reach_pct_inf'] = temp_df_02.loc[sup_index, 'reach_pct']
                df_all_curves.loc[count, 'closest_frequency_inf'] = temp_df_02.loc[sup_index, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_inf'] = temp_df_02.loc[sup_index, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_inf'] = temp_df_02.loc[sup_index, 'cpm']

                df_all_curves.loc[count, 'closest_impressions_sup'] = temp_df_02.loc[sup_index - 1, 'impression']
                df_all_curves.loc[count, 'closest_reach_sup'] = temp_df_02.loc[sup_index - 1, 'reach']
                df_all_curves.loc[count, 'closest_reach_pct_sup'] = temp_df_02.loc[sup_index - 1, 'reach_pct']
                df_all_curves.loc[count, 'closest_frequency_sup'] = temp_df_02.loc[sup_index - 1, 'frequency']
                df_all_curves.loc[count, 'closest_weekly_freq_sup'] = temp_df_02.loc[sup_index - 1, 'weekly_frequency']
                df_all_curves.loc[count, 'closest_cpm_sup'] = temp_df_02.loc[sup_index - 1, 'cpm']
                

            df_all_curves.loc[count, 'impressions_itp'] = (((df_all_curves.loc[count, 'closest_impressions_sup'] - df_all_curves.loc[count, 'closest_impressions_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_impressions_inf']
            df_all_curves.loc[count, 'reach_itp'] = (((df_all_curves.loc[count, 'closest_reach_sup'] - df_all_curves.loc[count, 'closest_reach_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_reach_inf']
            df_all_curves.loc[count, 'reach_pct_itp'] = (((df_all_curves.loc[count, 'closest_reach_pct_sup'] - df_all_curves.loc[count, 'closest_reach_pct_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_reach_pct_inf']
            df_all_curves.loc[count, 'frequency_itp'] = (((df_all_curves.loc[count, 'closest_frequency_sup'] - df_all_curves.loc[count, 'closest_frequency_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_frequency_inf']
            df_all_curves.loc[count, 'weekly_freq_itp'] = (((df_all_curves.loc[count, 'closest_weekly_freq_sup'] - df_all_curves.loc[count, 'closest_weekly_freq_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_weekly_freq_inf']
            df_all_curves.loc[count, 'cpm_itp'] = (((df_all_curves.loc[count, 'closest_cpm_sup'] - df_all_curves.loc[count, 'closest_cpm_inf']) / (df_all_curves.loc[count, 'closest_budget_sup'] - df_all_curves.loc[count, 'closest_budget_inf'])) * (df_all_curves.loc[count, 'budget'] - df_all_curves.loc[count, 'closest_budget_inf'])) + df_all_curves.loc[count, 'closest_cpm_inf']

            

        else:
            df_all_curves.loc[count, ['closest_budget_inf', 
                                      'closest_impressions_inf',
                                      'closest_reach_inf',
                                      'closest_reach_pct_inf',
                                      'closest_frequency_inf',
                                      'closest_weekly_freq_inf',
                                      'closest_cpm_inf',
                                      'closest_budget_sup',
                                      'closest_impressions_sup',
                                      'closest_reach_sup',
                                      'closest_reach_pct_sup',
                                      'closest_frequency_sup',
                                      'closest_weekly_freq_sup',
                                      'closest_cpm_sup',
                                      'impressions_itp',
                                      'reach_itp',
                                      'reach_pct_itp',
                                      'frequency_itp',
                                      'weekly_freq_itp',
                                      'cpm_itp',
                                      ]] = float('Nan')
            

        count = count + 1
    
    # Add the column name for the weekly frequency control cap and objective
    df_all_curves['weekly_frequency_cap'] = weekly_freq_cap
    df_all_curves['objective'] = objective
    df_all_curves['days'] = str(days) + 'Days'
    df_all_curves['weeks'] = days / 7
    
    
    # Append the dataframe to the previous one
    append_interpolated =  append_interpolated.append(df_all_curves)

# Keep relevant fields    
append_interpolated = append_interpolated[[
    'budget',
    'weekly_frequency_cap',
    'days',
    'weeks',
    'impressions_itp', 
    'reach_itp',
    'reach_pct_itp',
    'frequency_itp', 
    'weekly_freq_itp', 
    'cpm_itp',
    'objective',
    ]]

# Reshape the dataframe to un-stack it
pivot_interpolated = append_interpolated.pivot(index = 'budget', columns = 'days').reset_index('budget')

# Merge the column names after the pivoting
pivot_interpolated.columns = ['_'.join((j, str(k))) for j, k in pivot_interpolated]

# Choose the directory to save the data predictions
export_csv = pivot_interpolated.to_csv(r'' + save_directory + '/05_Campaign_Duration_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.csv', header=True, index = None)

# Plot the Reach and Frequency Curves for Weekly Frequency

%matplotlib inline
plt.style.use('seaborn-whitegrid')

fig, ax = plt.subplots()
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_7Days'], label = 'Campaign duration: 1 week', color = '#9e0142')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_14Days'], label = 'Campaign duration: 2 weeks', color = '#d53e4f')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_21Days'], label = 'Campaign duration: 3 weeks', color = '#f46d43')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_28Days'], label = 'Campaign duration: 4 weeks', color = '#fdae61')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_35Days'], label = 'Campaign duration: 5 weeks', color = '#fee08b')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_42Days'], label = 'Campaign duration: 6 weeks', color = '#ffffbf')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_49Days'], label = 'Campaign duration: 7 weeks', color = '#e6f598')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_56Days'], label = 'Campaign duration: 8 weeks', color = '#abdda4')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_63Days'], label = 'Campaign duration: 9 weeks', color = '#66c2a5')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_70Days'], label = 'Campaign duration: 10 weeks', color = '#3288bd')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_77Days'], label = 'Campaign duration: 11 weeks', color = '#5e4fa2')
ax.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['weekly_freq_itp_84Days'], label = 'Campaign duration: 12 weeks', color = '#312955')
leg = ax.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Weekly Frequency')
#plt.title('Campaign Duration: Weekly Frequency\n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));
plt.title('Campaign Duration \n Accoun ID: ' + str('0000000') + ' / Name: ' + str('XYZ'));

plt.savefig(r'' + save_directory + '/05_Campaign_Duration_WeeklyFreq_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Reach (people)
fig, bx = plt.subplots()
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_7Days'], label = 'Campaign duration: 1 week', color = '#9e0142')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_14Days'], label = 'Campaign duration: 2 weeks', color = '#d53e4f')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_21Days'], label = 'Campaign duration: 3 weeks', color = '#f46d43')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_28Days'], label = 'Campaign duration: 4 weeks', color = '#fdae61')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_35Days'], label = 'Campaign duration: 5 weeks', color = '#fee08b')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_42Days'], label = 'Campaign duration: 6 weeks', color = '#ffffbf')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_49Days'], label = 'Campaign duration: 7 weeks', color = '#e6f598')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_56Days'], label = 'Campaign duration: 8 weeks', color = '#abdda4')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_63Days'], label = 'Campaign duration: 9 weeks', color = '#66c2a5')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_70Days'], label = 'Campaign duration: 10 weeks', color = '#3288bd')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_77Days'], label = 'Campaign duration: 11 weeks', color = '#5e4fa2')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_itp_84Days'], label = 'Campaign duration: 12 weeks', color = '#312955')
leg = bx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Reach (Millions)')
#plt.title('Campaign Duration: Weekly Frequency\n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));
plt.title('Campaign Duration \n Accoun ID: ' + str('0000000') + ' / Name: ' + str('XYZ'));

plt.savefig(r'' + save_directory + '/05_Campaign_Duration_Reach_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


# Plot the Reach and Frequency Curves for Cost per mille (CPM)
fig, cx = plt.subplots()
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_7Days'], label = 'Campaign duration: 1 week', color = '#9e0142')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_14Days'], label = 'Campaign duration: 2 weeks', color = '#d53e4f')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_21Days'], label = 'Campaign duration: 3 weeks', color = '#f46d43')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_28Days'], label = 'Campaign duration: 4 weeks', color = '#fdae61')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_35Days'], label = 'Campaign duration: 5 weeks', color = '#fee08b')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_42Days'], label = 'Campaign duration: 6 weeks', color = '#ffffbf')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_49Days'], label = 'Campaign duration: 7 weeks', color = '#e6f598')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_56Days'], label = 'Campaign duration: 8 weeks', color = '#abdda4')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_63Days'], label = 'Campaign duration: 9 weeks', color = '#66c2a5')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_70Days'], label = 'Campaign duration: 10 weeks', color = '#3288bd')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_77Days'], label = 'Campaign duration: 11 weeks', color = '#5e4fa2')
cx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['cpm_itp_84Days'], label = 'Campaign duration: 12 weeks', color = '#312955')
leg = cx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('CPM (' + str(acc_currency) + ')')
#plt.title('Campaign Duration: Weekly Frequency\n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));
plt.title('Campaign Duration \n Accoun ID: ' + str('0000000') + ' / Name: ' + str('XYZ'));

plt.savefig(r'' + save_directory + '/05_Campaign_Duration_CPM_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Total frequency
fig, dx = plt.subplots()
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_7Days'], label = 'Campaign duration: 1 week', color = '#9e0142')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_14Days'], label = 'Campaign duration: 2 weeks', color = '#d53e4f')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_21Days'], label = 'Campaign duration: 3 weeks', color = '#f46d43')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_28Days'], label = 'Campaign duration: 4 weeks', color = '#fdae61')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_35Days'], label = 'Campaign duration: 5 weeks', color = '#fee08b')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_42Days'], label = 'Campaign duration: 6 weeks', color = '#ffffbf')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_49Days'], label = 'Campaign duration: 7 weeks', color = '#e6f598')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_56Days'], label = 'Campaign duration: 8 weeks', color = '#abdda4')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_63Days'], label = 'Campaign duration: 9 weeks', color = '#66c2a5')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_70Days'], label = 'Campaign duration: 10 weeks', color = '#3288bd')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_77Days'], label = 'Campaign duration: 11 weeks', color = '#5e4fa2')
dx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['frequency_itp_84Days'], label = 'Campaign duration: 12 weeks', color = '#312955')
leg = dx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Total frequency')
#plt.title('Campaign Duration: Weekly Frequency\n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));
plt.title('Campaign Duration \n Accoun ID: ' + str('0000000') + ' / Name: ' + str('XYZ'));

plt.savefig(r'' + save_directory + '/05_Campaign_Duration_TotalFreq_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')

# Plot the Reach and Frequency Curves for Reach % (on-target)
fig, bx = plt.subplots()
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_7Days'], label = 'Campaign duration: 1 week', color = '#9e0142')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_14Days'], label = 'Campaign duration: 2 weeks', color = '#d53e4f')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_21Days'], label = 'Campaign duration: 3 weeks', color = '#f46d43')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_28Days'], label = 'Campaign duration: 4 weeks', color = '#fdae61')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_35Days'], label = 'Campaign duration: 5 weeks', color = '#fee08b')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_42Days'], label = 'Campaign duration: 6 weeks', color = '#ffffbf')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_49Days'], label = 'Campaign duration: 7 weeks', color = '#e6f598')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_56Days'], label = 'Campaign duration: 8 weeks', color = '#abdda4')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_63Days'], label = 'Campaign duration: 9 weeks', color = '#66c2a5')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_70Days'], label = 'Campaign duration: 10 weeks', color = '#3288bd')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_77Days'], label = 'Campaign duration: 11 weeks', color = '#5e4fa2')
bx.plot(pivot_interpolated['budget_']/1000, pivot_interpolated['reach_pct_itp_84Days'], label = 'Campaign duration: 12 weeks', color = '#312955')
leg = bx.legend()
plt.xlabel('Budget '+ str(acc_currency) +' (Thousands)')
plt.ylabel('Reach % (on-target)')
#plt.title('Campaign Duration: Weekly Frequency\n Accoun ID: ' + str(acc_id) + ' / Name: ' + str(acc_name));
plt.title('Campaign Duration \n Accoun ID: ' + str('0000000') + ' / Name: ' + str('XYZ'));

plt.savefig(r'' + save_directory + '/05_Campaign_Duration_Reach_pct_' + str(acc_id) + '_' + datetime.today().strftime('%Y-%m-%d') + '.pdf')


#------------------------END Module_05_Campaign_Duration-----------------------------------------------#

# Additional resources on :

# Reach & Frequency Fields

# https://developers.facebook.com/docs/marketing-api/reference/reach-frequency-prediction

# Currencies
# https://developers.facebook.com/docs/marketing-api/currencies

# Platforms that cannot work with each Objective

# Audience Network cannot work with:
# 1. LINK_CLICKS
# 2. CONVERSIONS
