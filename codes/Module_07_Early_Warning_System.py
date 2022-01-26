#Copyright (c) Facebook, Inc. and its affiliates.
#All rights reserved.

#This source code is licensed under the license found in the
#LICENSE file in the root directory of this source tree.

#------------------------START Module_07_Early_Warning_System-------------------------------------#

#--------------------------------------START INPUT SECTION----------------------------------------#

# Import Python libraries
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountactivity import AdAccountActivity
from facebook_business.adobjects.currency import Currency
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from datetime import datetime, date, timedelta
import pandas as pd 
import numpy as np

# Include your own access token instead of xxxxxx
access_token = 'xxxxxxx'

# Initiate the Facebook Business API with the access token
FacebookAdsApi.init(access_token=access_token)

# Write a list with all the Ad Account IDs you want to include
ad_account_ids = ['act_xxxxxxx',
                  'act_xxxxxxx',
                  'act_xxxxxxx',
                  'act_xxxxxxx',
                  ]

# Define the dates you want to make the call on to fetch historical data
# Historical data has to be ferched only the first time
# Next calls can be updated on a daily basis

since_date = '2021-10-01'
until_date = '2021-12-31'

# Write the directory where you want to save all the OUTPUTS
save_directory = 'C:/Users/username/Desktop/' # this is just an example on PC

#--------------------------------------END INPUT SECTION----------------------------------------#

# Extract the currency info on each AdAccount
fields_accounts = [
    'account_id',
    'account_name',
    'account_currency'
    ]

# Leva 'level': 'account' fixed
params_accounts = {
    'level': 'account', # Different levels are: account, campaign, adset and ad
    'time_range': {'since': since_date, 'until': until_date},
}


# Create an empty dataframe where the campaign metrics will be stored

append_info_accounts = pd.DataFrame()

# Make the API call for pulling the information related to Accounts info

for accounts in ad_account_ids:
    
    # API Account call
    accounts_info = AdAccount(accounts).get_insights(
        fields = fields_accounts,
        params = params_accounts,
        
        )
    
    
    # Convert each call object into a dataframe
    df_accounts_info = pd.DataFrame.from_dict(accounts_info)
        
    # Append each dataframe for storing all Accounts into a one single dataframe
    append_info_accounts = append_info_accounts.append(df_accounts_info).reset_index(drop = True)
    
# Almost all country currencies are in cents, except for: 
# Chilean Peso, Colombian Peso, Costa Rican Colon, Hungarian Forint, Iceland Krona,
# Indonesian Rupiah, Japanese Yen, Korean Won, Paraguayan Guarani, Taiwan Dollar and Vietnamese Dong
# For additional information visit: https://developers.facebook.com/docs/marketing-api/currencies

# Extract the currency info from the AdAccount as different currencies have different cents configurations

count = 0

for currency in append_info_accounts['account_currency']:
    
    # Transform the currency your account is set up, if it is in cents, it will tranform to whole currency units
    # If it is in whole units, it will keep the same
    
    if (currency in ['CLP', 'COP', 'CRC', 'HUF', 'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']):

        append_info_accounts.loc[count, 'currency_divisor'] = 1

    else:

        append_info_accounts.loc[count, 'currency_divisor'] = 100
        
    count = count + 1
    
append_info_accounts = append_info_accounts.drop(['date_start', 'date_stop'], axis=1)    
append_info_accounts = append_info_accounts.drop_duplicates()

#--------------------START FETCHING DATA AT CAMPAIGN LEVEL----------------------#

# Specify the fields you want to fetch at campaign level

fields_campaigns = [
    'account_id',
    'id', 
    'name', 
    'buying_type',
    'objective',
    'lifetime_budget',
    'daily_budget',
    'start_time',
    'stop_time'
]


# Create an empty dataframe where the campaign metrics will be stored

append_metrics_campaigns = pd.DataFrame()

# Make the API call for pulling the information related to insights and campaigns specs

for accounts in ad_account_ids:
    
    # Campaigns call
    campaigns_metrics = AdAccount(accounts).get_campaigns(
        fields = fields_campaigns,
        )
    
    # Convert each call object into a dataframe
    df_campaigns_metrics = pd.DataFrame.from_dict(campaigns_metrics)
        
    # Append each dataframe for storing all Accounts into a one single dataframe
    append_metrics_campaigns = append_metrics_campaigns.append(df_campaigns_metrics).reset_index(drop = True)
    

# Rename the columns to facilitate names identification
append_metrics_campaigns = append_metrics_campaigns.rename(columns =
                                                           {'id': 'campaign_id', 
                                                            'name': 'campaign_name', 'daily_budget': 'campaign_daily_budget', 
                                                            'lifetime_budget': 'campaign_lifetime_budget'
                                                            })

# Create new dates columns in UTC datetime
append_metrics_campaigns['start_time_utc'] = pd.to_datetime(append_metrics_campaigns['start_time'], utc = True)
append_metrics_campaigns['stop_time_utc'] = pd.to_datetime(append_metrics_campaigns['stop_time'], utc = True)

# Filter only the campaigns you are interested on reading according to the initial range dates you specified
append_metrics_campaigns_filter = append_metrics_campaigns[(append_metrics_campaigns['start_time_utc'] >= pd.to_datetime(since_date, utc = True)) &
                                  (append_metrics_campaigns['start_time_utc'] <= pd.to_datetime(until_date, utc = True))
                                  ].reset_index(drop = True)

# Add the Account currency info to the append_metrics_campaigns_filter dataframe
df_campaigns = pd.merge(append_metrics_campaigns_filter, append_info_accounts, on = 'account_id', how = 'left')

# Convert string budgets to float budgets if the campaign has values for that column

if 'campaign_daily_budget' in df_campaigns.columns:
    df_campaigns['campaign_daily_budget'] = df_campaigns['campaign_daily_budget'].astype(float)
else:
    df_campaigns['campaign_daily_budget'] =float('nan')
    
if 'campaign_lifetime_budget' in df_campaigns.columns:
    df_campaigns['campaign_lifetime_budget'] = df_campaigns['campaign_lifetime_budget'].astype(float)
else: 
    df_campaigns['campaign_lifetime_budget'] =float('nan')

# Convert the currency cents to whole units (in those cases that applies)
df_campaigns['campaign_daily_budget_curr'] = df_campaigns['campaign_daily_budget'] / df_campaigns['currency_divisor']
df_campaigns['campaign_lifetime_budget_curr'] = df_campaigns['campaign_lifetime_budget'] / df_campaigns['currency_divisor']

# Keep only campaigns with budget greater than zero
df_campaigns = (df_campaigns[(df_campaigns['campaign_daily_budget']>0) | (df_campaigns['campaign_lifetime_budget']>0)]).reset_index(drop = True)

# Creating a new variable to separate the kind of budget set-up: lifetime or daily
count = 0

for campaigns in df_campaigns['campaign_id']:
    
    if df_campaigns.loc[count, 'campaign_daily_budget'] > 0:
        df_campaigns.loc[count, 'campaign_budget_setup'] = "Daily budget"
    
    elif df_campaigns.loc[count, 'campaign_lifetime_budget'] > 0:
        df_campaigns.loc[count, 'campaign_budget_setup'] = "Lifetime budget"
    
    count = count + 1
    
df_campaigns = df_campaigns.drop(['campaign_daily_budget', 'campaign_lifetime_budget'], axis=1) 

# Export data in case deeper analysis is needed
#export_csv = df_campaigns.to_csv(r'' + save_directory + 'Campaigns_Budget_Setup.csv', header=True, index = None)

# Create two basic stats summaries to calculate the outliers based on standard deviations
stats_daily_camp = df_campaigns.groupby('account_id', as_index = False).agg({'campaign_daily_budget_curr':['mean', 'std']})
stats_lifetime_camp = df_campaigns.groupby('account_id', as_index = False).agg({'campaign_lifetime_budget_curr':['mean', 'std']})


# Rename column names, as the group by changes it
stats_daily_camp.columns = ["_".join((j,k)) for j,k in stats_daily_camp.columns]
stats_lifetime_camp.columns = ["_".join((j,k)) for j,k in stats_lifetime_camp.columns]

stats_daily_camp = stats_daily_camp.rename(columns = {'account_id_': 'account_id', 
                                                      })

stats_lifetime_camp = stats_lifetime_camp.rename(columns = {'account_id_': 'account_id', 
                                                      })

# Estimating confidence intervals at 95% for daily budget and lifetime budget: 1.96 values are fixed
stats_daily_camp['camp_daily_lower_bound_95'] = stats_daily_camp['campaign_daily_budget_curr_mean'] - (1.96 * stats_daily_camp['campaign_daily_budget_curr_std'])
stats_daily_camp['camp_daily_upper_bound_95'] = stats_daily_camp['campaign_daily_budget_curr_mean'] + (1.96 * stats_daily_camp['campaign_daily_budget_curr_std'])
stats_lifetime_camp['camp_lifetime_lower_bound_95'] = stats_lifetime_camp['campaign_lifetime_budget_curr_mean'] - (1.96 * stats_lifetime_camp['campaign_lifetime_budget_curr_std'])
stats_lifetime_camp['camp_lifetime_upper_bound_95'] = stats_lifetime_camp['campaign_lifetime_budget_curr_mean'] + (1.96 * stats_lifetime_camp['campaign_lifetime_budget_curr_std'])

# Estimating confidence intervals at 90% for daily budget and lifetime budget: 1.645 values are fixed
stats_daily_camp['camp_daily_lower_bound_90'] = stats_daily_camp['campaign_daily_budget_curr_mean'] - (1.645 * stats_daily_camp['campaign_daily_budget_curr_std'])
stats_daily_camp['camp_daily_upper_bound_90'] = stats_daily_camp['campaign_daily_budget_curr_mean'] + (1.645 * stats_daily_camp['campaign_daily_budget_curr_std'])
stats_lifetime_camp['camp_lifetime_lower_bound_90'] = stats_lifetime_camp['campaign_lifetime_budget_curr_mean'] - (1.645 * stats_lifetime_camp['campaign_lifetime_budget_curr_std'])
stats_lifetime_camp['camp_lifetime_upper_bound_90'] = stats_lifetime_camp['campaign_lifetime_budget_curr_mean'] + (1.645 * stats_lifetime_camp['campaign_lifetime_budget_curr_std'])


# Estimating confidence intervals at 80% for daily budget and lifetime budget: 1.282 values are fixed
stats_daily_camp['camp_daily_lower_bound_80'] = stats_daily_camp['campaign_daily_budget_curr_mean'] - (1.282 * stats_daily_camp['campaign_daily_budget_curr_std'])
stats_daily_camp['camp_daily_upper_bound_80'] = stats_daily_camp['campaign_daily_budget_curr_mean'] + (1.282 * stats_daily_camp['campaign_daily_budget_curr_std'])
stats_lifetime_camp['camp_lifetime_lower_bound_80'] = stats_lifetime_camp['campaign_lifetime_budget_curr_mean'] - (1.282 * stats_lifetime_camp['campaign_lifetime_budget_curr_std'])
stats_lifetime_camp['camp_lifetime_upper_bound_80'] = stats_lifetime_camp['campaign_lifetime_budget_curr_mean'] + (1.282 * stats_lifetime_camp['campaign_lifetime_budget_curr_std'])

# Merge df_campaigns with the stats dataframes
df_campaigns_stats = pd.merge(df_campaigns, stats_daily_camp, on = 'account_id', how = 'left')
df_campaigns_stats = pd.merge(df_campaigns_stats, stats_lifetime_camp, on = 'account_id', how = 'left')

# Creating outlier fields at 80%, 90% and 95% confidence levels

count = 0
for campaigns in df_campaigns_stats['campaign_id']:
    
    # at 80%
    if pd.isnull(df_campaigns_stats.loc[count, 'campaign_daily_budget_curr']):
        if ((df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'] < df_campaigns_stats.loc[count, 'camp_lifetime_lower_bound_80']) | (df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'] > df_campaigns_stats.loc[count, 'camp_lifetime_upper_bound_80'])):
            df_campaigns_stats.loc[count, 'campaign_lifetime_oulier_80'] = 'Warning'
        
        else:
            df_campaigns_stats.loc[count, 'campaign_lifetime_oulier_80'] = '-'
            
    elif (pd.isnull(df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'])):
            
        if ((df_campaigns_stats.loc[count, 'campaign_daily_budget_curr'] < df_campaigns_stats.loc[count, 'camp_daily_lower_bound_80']) | (df_campaigns_stats.loc[count, 'campaign_daily_budget_curr'] > df_campaigns_stats.loc[count, 'camp_daily_upper_bound_80'])):
            df_campaigns_stats.loc[count, 'campaign_daily_oulier_80'] = 'Warning'
        else:
            df_campaigns_stats.loc[count, 'campaign_daily_oulier_80'] = '-'
            
    # at 90%
    
    if pd.isnull(df_campaigns_stats.loc[count, 'campaign_daily_budget_curr']):
        if ((df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'] < df_campaigns_stats.loc[count, 'camp_lifetime_lower_bound_90']) | (df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'] > df_campaigns_stats.loc[count, 'camp_lifetime_upper_bound_90'])):
            df_campaigns_stats.loc[count, 'campaign_lifetime_oulier_90'] = 'Warning'
        
        else:
            df_campaigns_stats.loc[count, 'campaign_lifetime_oulier_90'] = '-'
            
    elif (pd.isnull(df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'])):
            
        if ((df_campaigns_stats.loc[count, 'campaign_daily_budget_curr'] < df_campaigns_stats.loc[count, 'camp_daily_lower_bound_90']) | (df_campaigns_stats.loc[count, 'campaign_daily_budget_curr'] > df_campaigns_stats.loc[count, 'camp_daily_upper_bound_90'])):
            df_campaigns_stats.loc[count, 'campaign_daily_oulier_90'] = 'Warning'
        else:
            df_campaigns_stats.loc[count, 'campaign_daily_oulier_90'] = '-'
            
        
    # at 95%
    
    if pd.isnull(df_campaigns_stats.loc[count, 'campaign_daily_budget_curr']):
        
        if ((df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'] < df_campaigns_stats.loc[count, 'camp_lifetime_lower_bound_95']) | (df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'] > df_campaigns_stats.loc[count, 'camp_lifetime_upper_bound_95'])):
            df_campaigns_stats.loc[count, 'campaign_lifetime_oulier_95'] = 'Warning'
        else:
            df_campaigns_stats.loc[count, 'campaign_lifetime_oulier_95'] = '-'
            
    elif (pd.isnull(df_campaigns_stats.loc[count, 'campaign_lifetime_budget_curr'])):
            
        if ((df_campaigns_stats.loc[count, 'campaign_daily_budget_curr'] < df_campaigns_stats.loc[count, 'camp_daily_lower_bound_95']) | (df_campaigns_stats.loc[count, 'campaign_daily_budget_curr'] > df_campaigns_stats.loc[count, 'camp_daily_upper_bound_95'])):
            df_campaigns_stats.loc[count, 'campaign_daily_oulier_95'] = 'Warning'
        else:
            df_campaigns_stats.loc[count, 'campaign_daily_oulier_95'] = '-'
            
    count =  count + 1     

# Export the file with the confidence intervals for each campaign
export_csv = df_campaigns_stats.to_csv(r'' + save_directory + 'Campaigns_Confidence_Intervals.csv', header=True, index = None)

#--------------------ENDS FETCHING DATA AT CAMPAIGN LEVEL----------------------#

#--------------------STARTS FETCHING DATA AT AD SET LEVEL----------------------#

# Define fields and params
fields_adsets = [
    'account_id',
    'campaign_id',
    'id', 
    'name', 
    'lifetime_budget',
    'daily_budget',
    'start_time',
    'end_time'
]

params_adsets = {
    
    'filtering': [{'field':'campaign.delivery_info','operator':'IN','value': ["completed", "scheduled", "active"]}],
    
}

# Create an empty dataframe where the adsets metrics will be stored
append_metrics_adsets = pd.DataFrame()

# Make the API call for pulling the information related to insights and adsets specs
for accounts in ad_account_ids:
    
    # Ad Sets call
    adsets_metrics = AdAccount(accounts).get_ad_sets(
        fields = fields_adsets,
        params = params_adsets,
        )
    
    # Convert each call object into a dataframe
    df_adsets_metrics = pd.DataFrame.from_dict(adsets_metrics)
        
    # Append each dataframe for storing all Accounts into a one single dataframe
    append_metrics_adsets = append_metrics_adsets.append(df_adsets_metrics).reset_index(drop = True)


# Rename the columns to facilitate names identification
append_metrics_adsets = append_metrics_adsets.rename(columns = 
                                                           {'id': 'adset_id', 
                                                            'name': 'adset_name', 'daily_budget': 'adset_daily_budget', 
                                                            'lifetime_budget': 'adset_lifetime_budget'
                                                           })



    

# Replace zeros with NaN
append_metrics_adsets['adset_daily_budget'] = append_metrics_adsets['adset_daily_budget'].replace('0', float('nan'))
append_metrics_adsets['adset_lifetime_budget'] = append_metrics_adsets['adset_lifetime_budget'].replace('0', float('nan'))

# Create new dates columns in UTC datetime
append_metrics_adsets['start_time_utc'] = pd.to_datetime(append_metrics_adsets['start_time'], utc = True)
append_metrics_adsets['end_time_utc'] = pd.to_datetime(append_metrics_adsets['end_time'], utc = True)

# Filter only the Ad Sets you are interested on reading according to the initial range dates you specified
append_metrics_adsets_filter = append_metrics_adsets[(append_metrics_adsets['start_time_utc'] >= pd.to_datetime(since_date, utc = True)) &
                                  (append_metrics_adsets['start_time_utc'] <= pd.to_datetime(until_date, utc = True))
                                  ].reset_index(drop = True)


# Add the Account currency info to the append_metrics_adsets_filter dataframe
df_adsets = pd.merge(append_metrics_adsets_filter, append_info_accounts, on = 'account_id', how = 'left')

# Convert string budgets to float budgets if the adset has values for that column

if 'adset_daily_budget' in df_adsets.columns:
    df_adsets['adset_daily_budget'] = df_adsets['adset_daily_budget'].astype(float)
else:
    df_adsets['adset_daily_budget'] =float('nan')


if 'adset_lifetime_budget' in df_adsets.columns:
    df_adsets['adset_lifetime_budget'] = df_adsets['adset_lifetime_budget'].astype(float)
else:
    df_adsets['adset_lifetime_budget'] =float('nan')


# Convert the currency cents to whole units (in those cases that applies)
df_adsets['adset_daily_budget_curr'] = df_adsets['adset_daily_budget'] / df_adsets['currency_divisor']
df_adsets['adset_lifetime_budget_curr'] = df_adsets['adset_lifetime_budget'] / df_adsets['currency_divisor']

# Filtering adsets to keep only those with budget>0
df_adsets = (df_adsets[(df_adsets['adset_daily_budget']>0) | (df_adsets['adset_lifetime_budget']>0)]).reset_index(drop = True)

# Creating a new variable to separate the kind of budget set-up: lifetime or daily
count = 0

for adsets in df_adsets['adset_id']:
    
    if df_adsets.loc[count, 'adset_daily_budget'] > 0:
        df_adsets.loc[count, 'adset_budget_setup'] = "Daily budget"
    
    elif df_adsets.loc[count, 'adset_lifetime_budget'] > 0:
        df_adsets.loc[count, 'adset_budget_setup'] = "Lifetime budget"
    
    count = count + 1
    
df_adsets = df_adsets.drop(['adset_daily_budget', 'adset_lifetime_budget'], axis=1)    

# Export data in case deeper analysis is needed
#export_csv = df_adsets.to_csv(r'' + save_directory + 'AdSets_Budget_Setup.csv', header=True, index = None)

# Create two basic stats summaries to calculate the outliers based on standard deviations
stats_daily_adsets = df_adsets.groupby('account_id', as_index = False).agg({'adset_daily_budget_curr':['mean', 'std']})
stats_lifetime_adsets = df_adsets.groupby('account_id', as_index = False).agg({'adset_lifetime_budget_curr':['mean', 'std']})

# Rename the column names, as the group by changes it
stats_daily_adsets.columns = ["_".join((j,k)) for j,k in stats_daily_adsets.columns]
stats_lifetime_adsets.columns = ["_".join((j,k)) for j,k in stats_lifetime_adsets.columns]

stats_daily_adsets = stats_daily_adsets.rename(columns = {'account_id_': 'account_id', 
                                                      })

stats_lifetime_adsets = stats_lifetime_adsets.rename(columns = {'account_id_': 'account_id', 
                                                      })

# Estimating confidence intervals at 95% for daily budget and lifetime budget: 1.96 values are fixed
stats_daily_adsets['adset_daily_lower_bound_95'] = stats_daily_adsets['adset_daily_budget_curr_mean'] - (1.96 * stats_daily_adsets['adset_daily_budget_curr_std'])
stats_daily_adsets['adset_daily_upper_bound_95'] = stats_daily_adsets['adset_daily_budget_curr_mean'] + (1.96 * stats_daily_adsets['adset_daily_budget_curr_std'])
stats_lifetime_adsets['adset_lifetime_lower_bound_95'] = stats_lifetime_adsets['adset_lifetime_budget_curr_mean'] - (1.96 * stats_lifetime_adsets['adset_lifetime_budget_curr_std'])
stats_lifetime_adsets['adset_lifetime_upper_bound_95'] = stats_lifetime_adsets['adset_lifetime_budget_curr_mean'] + (1.96 * stats_lifetime_adsets['adset_lifetime_budget_curr_std'])

# Estimating confidence intervals at 90% for daily budget and lifetime budget: 1.645 values are fixed
stats_daily_adsets['adset_daily_lower_bound_90'] = stats_daily_adsets['adset_daily_budget_curr_mean'] - (1.645 * stats_daily_adsets['adset_daily_budget_curr_std'])
stats_daily_adsets['adset_daily_upper_bound_90'] = stats_daily_adsets['adset_daily_budget_curr_mean'] + (1.645 * stats_daily_adsets['adset_daily_budget_curr_std'])
stats_lifetime_adsets['adset_lifetime_lower_bound_90'] = stats_lifetime_adsets['adset_lifetime_budget_curr_mean'] - (1.645 * stats_lifetime_adsets['adset_lifetime_budget_curr_std'])
stats_lifetime_adsets['adset_lifetime_upper_bound_90'] = stats_lifetime_adsets['adset_lifetime_budget_curr_mean'] + (1.645 * stats_lifetime_adsets['adset_lifetime_budget_curr_std'])


# Estimating confidence intervals at 80% for daily budget and lifetime budget: 1.282 values are fixed
stats_daily_adsets['adset_daily_lower_bound_80'] = stats_daily_adsets['adset_daily_budget_curr_mean'] - (1.282 * stats_daily_adsets['adset_daily_budget_curr_std'])
stats_daily_adsets['adset_daily_upper_bound_80'] = stats_daily_adsets['adset_daily_budget_curr_mean'] + (1.282 * stats_daily_adsets['adset_daily_budget_curr_std'])
stats_lifetime_adsets['adset_lifetime_lower_bound_80'] = stats_lifetime_adsets['adset_lifetime_budget_curr_mean'] - (1.282 * stats_lifetime_adsets['adset_lifetime_budget_curr_std'])
stats_lifetime_adsets['adset_lifetime_upper_bound_80'] = stats_lifetime_adsets['adset_lifetime_budget_curr_mean'] + (1.282 * stats_lifetime_adsets['adset_lifetime_budget_curr_std'])

# Merge df_campaigns with the stats dataframes
df_adsets_stats = pd.merge(df_adsets, stats_daily_adsets, on = 'account_id', how = 'left')
df_adsets_stats = pd.merge(df_adsets_stats, stats_lifetime_adsets, on = 'account_id', how = 'left')

# Creating the outlier variables at 80%, 90% and 95% confidence levels
count = 0
for adsets in df_adsets_stats['adset_id']:
    
    
    # at 80%
    if (pd.isnull(df_adsets_stats.loc[count, 'adset_daily_budget_curr'])):
        if ((df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'] < df_adsets_stats.loc[count, 'adset_lifetime_lower_bound_80']) | (df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'] > df_adsets_stats.loc[count, 'adset_lifetime_upper_bound_80'])):
            df_adsets_stats.loc[count, 'adset_lifetime_oulier_80'] = 'Warning'
            
        else:
            df_adsets_stats.loc[count, 'adset_lifetime_oulier_80'] = '-'
            
            
    elif (pd.isnull(df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'])):
            
        if ((df_adsets_stats.loc[count, 'adset_daily_budget_curr'] < df_adsets_stats.loc[count, 'adset_daily_lower_bound_80']) | (df_adsets_stats.loc[count, 'adset_daily_budget_curr'] > df_adsets_stats.loc[count, 'adset_daily_upper_bound_80'])):
            df_adsets_stats.loc[count, 'adset_daily_oulier_80'] = 'Warning'
        else:
            df_adsets_stats.loc[count, 'adset_daily_oulier_80'] = '-'
        
        
            
    # at 90%
    
    if (pd.isnull(df_adsets_stats.loc[count, 'adset_daily_budget_curr'])):
        if ((df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'] < df_adsets_stats.loc[count, 'adset_lifetime_lower_bound_90']) | (df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'] > df_adsets_stats.loc[count, 'adset_lifetime_upper_bound_90'])):
            df_adsets_stats.loc[count, 'adset_lifetime_oulier_90'] = 'Warning'
        
        else:
            df_adsets_stats.loc[count, 'adset_lifetime_oulier_90'] = '-'
            
    elif (pd.isnull(df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'])):
            
        if ((df_adsets_stats.loc[count, 'adset_daily_budget_curr'] < df_adsets_stats.loc[count, 'adset_daily_lower_bound_90']) | (df_adsets_stats.loc[count, 'adset_daily_budget_curr'] > df_adsets_stats.loc[count, 'adset_daily_upper_bound_90'])):
            df_adsets_stats.loc[count, 'adset_daily_oulier_90'] = 'Warning'
        else:
            df_adsets_stats.loc[count, 'adset_daily_oulier_90'] = '-'
            
        
    # at 95%
    if (pd.isnull(df_adsets_stats.loc[count, 'adset_daily_budget_curr'])):
        
        if ((df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'] < df_adsets_stats.loc[count, 'adset_lifetime_lower_bound_95']) | (df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'] > df_adsets_stats.loc[count, 'adset_lifetime_upper_bound_95'])):
            df_adsets_stats.loc[count, 'adset_lifetime_oulier_95'] = 'Warning'
        else:
            df_adsets_stats.loc[count, 'adset_lifetime_oulier_95'] = '-'
            
    elif (pd.isnull(df_adsets_stats.loc[count, 'adset_lifetime_budget_curr'])):
            
        if ((df_adsets_stats.loc[count, 'adset_daily_budget_curr'] < df_adsets_stats.loc[count, 'adset_daily_lower_bound_95']) | (df_adsets_stats.loc[count, 'adset_daily_budget_curr'] > df_adsets_stats.loc[count, 'adset_daily_upper_bound_95'])):
            df_adsets_stats.loc[count, 'adset_daily_oulier_95'] = 'Warning'
        else:
            df_adsets_stats.loc[count, 'adset_daily_oulier_95'] = '-'
            
    count =  count + 1

# Export the file with the confidence intervals for each campaign
export_csv = df_adsets_stats.to_csv(r'' + save_directory + 'AdSets_Confidence_Intervals.csv', header=True, index = None)

#-----------------------------------ENDS FETCHING DATA AT AD SET LEVEL--------------------------------------------------#

#IMPORTANT: Once you have confidence intervals data for both, campaigns and adsets. Data can be shown in a Dashboard
# to track campaigns and adsets evolution.
# On the other hand, additional functions can be added to automatically send an e-mail notification to the people
# related to the AdAccount to make them aware of a possible overspend issue. 
# These funtions can be developed by each user of the module according to specific needs

