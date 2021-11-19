#Copyright (c) Facebook, Inc. and its affiliates.
#All rights reserved.

#This source code is licensed under the license found in the
#LICENSE file in the root directory of this source tree.

#------------------------START Module_03_Interest_Optimization-------------------------#

# Import libraries
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adasyncrequest import AdAsyncRequest
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.targetingsearch import TargetingSearch
import matplotlib.pyplot as plt
import waterfall_chart
from IPython.display import display
import pandas as pd 
import numpy as np 
import datetime 
import time
from itertools import chain

#---------------------------------------START INPUT SECTION-----------------------------------------#

#---------------------------------------------INPUT 01----------------------------------------------#

# Include your own access token instead of xxxxxx
access_token = 'xxxxxxx'
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

#---------------------------------------END INPUT 01----------------------------------------------#

# RUN THIS SECTION BEFORE GOING TO INPUT 02
fields_audiences = [
    'name',
    'targeting',
]

saved_audiences = AdAccount(ad_account_id).get_saved_audiences(
    fields = fields_audiences
)

df_saved_audiences = pd.DataFrame(saved_audiences)

# Export the df_saved_audiences to the defined save_directory
export_csv = df_saved_audiences.to_csv(r'' + save_directory + 'Saved_audiences.csv', header=True, index = None)


print(df_saved_audiences)

#---------------------------------------START INPUT 02----------------------------------------------#

# Once you have printed you saved audiences, filter only the audiences you are interested for the optimization
# Just keep in mind that the higher the number of audiences, rate limits will reached faster

# Filter by name only those audiences that you want to optimize on interests
audiences_list = ['Audience_03', # SET YOUR OWN AUDIENCE NAME
                  'Audience_03', # SET YOUR OWN AUDIENCE NAME
                  'Audience_03', # SET YOUR OWN AUDIENCE NAME
                 ]

df_saved_audiences_filter = df_saved_audiences[df_saved_audiences['name'].isin(audiences_list)].reset_index( drop = True)

#---------------------------------------END INPUT 02----------------------------------------------#

# Extract the targeting specs for each filtered audience

append_audiences = pd.DataFrame()

count = 0
for name in df_saved_audiences_filter['name']:
    
    audiences = pd.DataFrame(df_saved_audiences_filter['targeting'][count]['flexible_spec'][0]['interests']).reset_index(drop = True)
    audiences['audience_name'] = name
    audiences['age_min'] = df_saved_audiences_filter['targeting'][count]['age_min']
    audiences['age_max'] = df_saved_audiences_filter['targeting'][count]['age_max']
    audiences['genders'] = df_saved_audiences_filter['targeting'][count]['genders'][0]
    audiences['countries'] = df_saved_audiences_filter['targeting'][0]['geo_locations']['countries'][0]
    append_audiences = append_audiences.append(audiences)
        
    count = count + 1

# Rename column names
append_audiences = append_audiences.rename(columns = {'id': 'interest_id', 
                                                      'name': 'interest_name'
                                                      })
# Reset index
append_audiences = append_audiences.reset_index(drop = True)

# Create a for loop for defining a ranking with the interests with higher user levels
# and call just the individual reach for each interest

count = 0
for interests in append_audiences['interest_id']:
    
    fields = [
    ]
    
    params = {
      'targeting_spec': {'geo_locations':{'countries':[append_audiences.loc[count, 'countries']]},
                         'genders':[int(append_audiences.loc[count, 'genders'])],
                         'age_max':int(append_audiences.loc[count, 'age_max']),
                         'age_min':int(append_audiences.loc[count, 'age_min']), 
                         'flexible_spec': [
                             {
                                 'interests': [int(interests)],
                             },
                             
                             
                         ],
                         #'exclusions': {
                         #    'interests': [
                         #        {'id': 6002971095994, # This is just an example
                         #        },
                         #    ],
                         #},
                         }
    }
    
    # Make the call to fetch reach estimations
    reach_estimate = AdAccount(ad_account_id).get_reach_estimate (
        fields=fields,
        params=params,
        )
    
    append_audiences.loc[count, 'ind_reach'] = int(reach_estimate[0]['users'])
    
    count = count + 1
    
# Rank the dataframe by name and individual reach
append_audiences = append_audiences.sort_values(by = ['audience_name', 'ind_reach'], ascending = False)

# Reset dataframe index
append_audiences = append_audiences.reset_index(drop = True)

# Convert interest_id column to numeric
append_audiences['interest_id'] = pd.to_numeric(append_audiences['interest_id'])

# This section runs each pair, triples,... and so on for all the interests
# ranking the combinations that generate the higher reach levels 

df_interest_optim = pd.DataFrame(columns = ['interest_id', 'interest_name', 'ind_reach', 'interest_ids', 'interest_names','joint_reach'])

count_03 = 0
for audience in append_audiences['audience_name'].unique():
    
    # Clone the df_interests dataframe and use this new one to develope all the estimations
    df_interests_order = append_audiences[:][append_audiences[:]['audience_name'] == audience]
    
    df_interests_order = df_interests_order.reset_index(drop = True)
    
    # Convert the series interests to a list
    interest_list_ids = df_interests_order['interest_id'].to_list()
    
    # Create empty list to store the interests combinations
    ranked_interest_list = []
    ranked_interest_names_list = []
    
    # Run a loop to explore different interest combinations

    count_02 = 0
    for i in range(0, len(interest_list_ids)):
        
        temp_df = pd.DataFrame(columns = ['interest_ids', 'interest_names','interest_try', 'interest_name', 'ind_reach', 'joint_reach'])
        count_01 = 0

        for interests in df_interests_order['interest_id']:
            
            # This considers always the ranked list to be combined with the rest of interests
            interests_cum_list = ranked_interest_list[:]
            interests_names_cum_list = ranked_interest_names_list[:]

            # Append the new interests to be combined
            interests_cum_list.append(int(interests))
            interests_names_cum_list.append(df_interests_order.loc[count_01,'interest_name'])

            # Leave this variable empty
            fields = [
                ]

            # Params are extracted from df_interests_order dataframe
            params = {
                'targeting_spec': {'geo_locations':{'countries':[df_interests_order.loc[count_01, 'countries']]},
                                   'genders':[int(df_interests_order.loc[count_01, 'genders'])],
                                   'age_max':int(df_interests_order.loc[count_01, 'age_max']),
                                   'age_min':int(df_interests_order.loc[count_01, 'age_min']), 
                                   'flexible_spec': [
                                       {
                                           'interests':interests_cum_list,
                                           }
                                       ],
                                   #'exclusions': {
                                   #    'interests': [
                                   #        {'id': 6002971095994,
                                   #        },
                                   #    ],
                                   #},
                                   }
                }

            # Make the call for each interest combination
            reach_estimate = AdAccount(ad_account_id).get_reach_estimate (
                fields=fields,
                params=params,
                )

            # Create a temporary dataframe where the reach estimates will be storer for each combination
            temp_df.loc[count_01, 'interest_ids'] = interests_cum_list
            temp_df.loc[count_01, 'interest_names'] = interests_names_cum_list
            temp_df.loc[count_01, 'interest_try'] = int(interests)
            temp_df.loc[count_01, 'interest_name'] = df_interests_order.loc[count_01, 'interest_name']
            temp_df.loc[count_01, 'ind_reach'] = df_interests_order.loc[count_01, 'ind_reach']
            temp_df.loc[count_01, 'joint_reach'] = reach_estimate[0]['users']

            count_01 = count_01 + 1

        # Identifying the index with the maximum joint_reach, so we can identify the interest list
        # and filter the dataframe where we will be iterating the next raking

        max_index = (temp_df[temp_df['joint_reach'] == max(temp_df['joint_reach'])].index.values)[0]
        ranked_interest_list = temp_df.loc[max_index, 'interest_ids']
        ranked_interest_names_list = temp_df.loc[max_index, 'interest_names']
        max_reach_interest = temp_df.loc[max_index, 'interest_try']

        # Saving the optimized ranked order and reach results in a different dataframe

        df_interest_optim.loc[(count_02 + count_03), 'audience_name'] = audience
        df_interest_optim.loc[(count_02 + count_03), 'interest_id'] = temp_df.loc[max_index, 'interest_try']
        df_interest_optim.loc[(count_02 + count_03), 'interest_name'] = temp_df.loc[max_index, 'interest_name']
        df_interest_optim.loc[(count_02 + count_03), 'ind_reach'] = int(temp_df.loc[max_index, 'ind_reach'])
        df_interest_optim.loc[(count_02 + count_03), 'interest_ids'] =  ranked_interest_list
        df_interest_optim.loc[(count_02 + count_03), 'interest_names'] = ranked_interest_names_list
        df_interest_optim.loc[(count_02 + count_03), 'joint_reach'] = temp_df.loc[max_index, 'joint_reach']
        
        # Excluding from the dataframe the interest with the maximum reach
        # so it is ready for the next loop
        df_interests_order = df_interests_order[df_interests_order['interest_id'] != max_reach_interest]
        df_interests_order = df_interests_order.reset_index(drop = True)
        
        count_02 = count_02 + 1
    
    
    count_03 = count_03 + count_02

# Computing percentage reach and cumulative percentage reach

count_05 = 0

for audience in append_audiences['audience_name'].unique():
    
    # Clone the df_interests dataframe and use this new one to develope all the estimations
    df_interests_order = append_audiences[:][append_audiences[:]['audience_name'] == audience]
    
    # Reset index
    df_interests_order = df_interests_order.reset_index(drop = True)
    
    # Create variables to store cumulative and incremental results
    count_04 = 0
    cum_reach = 0
    inc_reach = 0
    pct_inc_reach = 0
    
    # Run a loop to compute each new variable for incremental and cumulative results
    for i in range(0, len(df_interests_order)):
                
        df_interest_optim.loc[count_04 + count_05, 'inc_reach'] = df_interest_optim.loc[count_04 + count_05, 'joint_reach'] - inc_reach
        df_interest_optim.loc[count_04 + count_05, 'pct_cum_joint_reach'] = round(((df_interest_optim.loc[count_04 + count_05, 'joint_reach']) / max(df_interest_optim[df_interest_optim['audience_name'] == audience]['joint_reach']) *100),1)
        df_interest_optim.loc[count_04 + count_05, 'pct_inc_reach'] = df_interest_optim.loc[count_04 + count_05, 'pct_cum_joint_reach'] - pct_inc_reach
        inc_reach = df_interest_optim.loc[count_04 + count_05, 'joint_reach']
        pct_inc_reach = df_interest_optim.loc[count_04 + count_05, 'pct_cum_joint_reach']
        count_04 = count_04 + 1
    
    count_05 = count_05 + count_04
    
    
# Create a new incremental reach variable in term of millions to make its reading easier
df_interest_optim['inc_reach_millions'] = df_interest_optim['inc_reach'] / 1000000

# Export the optimized table results to the defined save_directory
export_csv = df_interest_optim.to_csv(r'' + save_directory + ad_account_id + '.csv', header=True, index = None)

# Chart the optimized table results using waterfall charts

for audience in df_interest_optim['audience_name'].unique():
    
    # Clone the df_interests dataframe and use this new one to develope all the estimations
    df_interests_order = df_interest_optim[:][df_interest_optim[:]['audience_name'] == audience]
    
    df_interests_order = df_interests_order.reset_index(drop = True)
    
    # Plot the Reach and Frequency Curves

    %matplotlib inline
    plt.style.use('seaborn-whitegrid')
    display(df_interests_order[['interest_name', 'pct_inc_reach']])
    a = df_interests_order['interest_name'].to_list()
    b = df_interests_order['pct_inc_reach'].to_list()
    c = df_interests_order['inc_reach_millions'].to_list()
    
    # Chart in terms of Reach %

    waterfall_chart.plot(a, b, net_label='Total Reach', rotation_value = 90)

    plt.ylabel('Reach %')
    plt.title('Optimized Interests: ' + audience)
    plt.axis([-1, (len(a)+1), 0, 120])
    plt.grid(True, linestyle='--', which='major',
                       color='grey', alpha=0.25);
    
    # Save the chart for relative reach results
    plt.savefig(r'' + save_directory + '03_Optimized_Interests_' + audience + '_pct.pdf', bbox_inches =  'tight')
    
    # Chart in terms of Reach %

    waterfall_chart.plot(a, c, net_label='Total Reach', rotation_value=90)
    plt.ylabel('Reach millions')
    plt.title('Optimized Interests: ' + audience)
    plt.axis([-1, (len(a)+1), 0, (sum(c)*1.2)])
    plt.grid(True, linestyle='--', which='major',
                       color='grey', alpha=.25);
    
    # Save the chart for absolute reach results
    plt.savefig(r'' + save_directory + '03_Optimized_Interests_' + audience + '_abs.pdf', bbox_inches =  'tight')
    
#---------------------------END Module_03_Interest_Optimization-----------------------#

# Additional resources on :

# Reach & Frequency Fields

# https://developers.facebook.com/docs/marketing-api/reference/reach-frequency-prediction

# Currencies
# https://developers.facebook.com/docs/marketing-api/currencies

# Flexible Targeting documentation:

# https://developers.facebook.com/docs/marketing-api/audiences/reference/flexible-targeting
# https://developers.facebook.com/docs/marketing-api/audiences/reference/targeting-search#interests
# https://developers.facebook.com/docs/marketing-api/audiences/reference/basic-targeting#interests
