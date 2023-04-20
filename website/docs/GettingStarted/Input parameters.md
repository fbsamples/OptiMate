---
sidebar_position: 3
---
# Main input Parameters

## Must have parameters
In most of the modules you will need to input the following parameters. It's important to make sure you have permissions to access at least one Meta Ad Account, so you can fetch predictions and get insights.

``` python
#---------------------------------------------INPUT SECTION----------------------------------------------#
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

```

# Parameters for Modules 1, 2, 4, 5 and 9
Use Reach & Frequency predictions to bring results depending on different objectives, audiences, campaign duration and frequency control caps. In these Modules you will need to input specific campaign parameters to have a specific prediction on that. Depending on each Module some inputs are predefined (by design) and some others can be customized:
``` python
# Specify the objective you want to test
# Available Objectives are: BRAND_AWARENESS, LINK_CLICKS, POST_ENGAGEMENT, REACH and VIDEO_VIEWS
objective = 'REACH'

# Input the minimum and maximum ages
# In Meta Ads Platforms, minimum available is 13 years old and maximum is 65, which stands for people 65+ years old
age_min = 18
age_max = 65

# Input the genders in a list. 2-for female, 1-for male
gender_list = [1,2]

# Input the county for the ads delivery
countries = ['MX'] # Write your country acronym

# Define the amount of days for your Campaign predictions
camp_days = 28 # The maximum days that the prediction can be done is 90 within a 6 months window from now

# Frequency caps
# Needs the maximum number of times your ad will be shown to a person during a specifyed time period
# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days
frequency_cap = 2
every_x_days = 7

# When using interest-behavior based audiences, make sure that you have already saved the audience in the same AdAccount in Ads Manager you are using for the Reach&Frequency predictions
# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction
# ONLY for interests or behaviors audiences
# If you ARE NOT using interests/behaviors, leave audience_name = 'None'
audience_name = 'None'

# Days before the campaign begins
# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on
# Minimum and default value is 1
days_prior_start = 1

```

# Parameters for Module 3
In addition to the must have parameters, for Module 3 it's only needed the name of the audience you need to optimize. To that end it's very important thar first you create the audience by following:
1. Go to Ads Manager>>Audiences section
2. Click on Create Audience>>Saved Audience
3. Define demographics and desired interest-behaviors and 'Name your audience'
Note: this Module only works with Saved Audiences, not for Custom Audiences nor LookAlike Audiences

# Filter by name only those audiences that you want to optimize on interests

``` python
# Example for a Saved Audience named 'Saved_Audience_Name'
audiences_list = ['Saved_Audience_Name', # SET YOUR OWN AUDIENCE NAME
                 ]

```

# Parameters for Module 6
Very similar to Modules 1, 2, 4, 5 and 9 but in this case as this is the most robust module we can define different parameters at once to perform several combinations. Instead of having single value parameters, we can work with lists and a defined reference budget:

``` python
# Budget in whole units, not cents and using the same currency your ad account is configured
# This will be your reference budget set as your business as usual
budget = 100000

# Input the country for the ads delivery
# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web
countries = [['MX']]

# Input all the campaing specs for your prediction
# Input the minimum and maximum ages
# In Meta Ads Platforms, minimum available is 13 years old and maximum is 65, which stands for people 65+ years old

ages = [[25,50], [25,65]]

# Input the genders. 2-for female, 1-for male
gender_list = [[1,2]]

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
camp_days = [28, 35, 42]

# Set different objectives to siulate
# Different objectives are: 'BRAND_AWARENESS', 'REACH', 'LINK_CLICKS', 'POST_ENGAGEMENT' AND 'VIDEO_VIEWS'
camp_objectives = [
    'REACH',
    'BRAND_AWARENESS',
]

# Frequency caps
# Needs the maximum number of times your ad will be shown to a person during a specifyed time period
# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days
maximum_caps = [3, 4, 5]
every_x_days = 7

# Days before the campaign begins
# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on
# Minimum and default value is 1
days_prior_start = 1

```
# Parameters for Module 7
As this Module performs a confidence intervals analysis, it's needed to define a time frame. Besides this input and the must have credentials the rest of the analysis is performed by the code itself.

```python
# Define the dates you want to make the call on to fetch historical data
# Historical data has to be fetched only the first time
# Next calls can be updated on a daily/weekly basis

since_date = '2023-01-01'
until_date = '2023-03-31'

# Write the directory where you want to save all the OUTPUTS
save_directory = 'C:/Users/username/Desktop/' # this is just an example on PC

```
# Parameters for Module 8
Inputs for this Module are very similar to the ones in the Modules 1, 2, 4, 5 and 9 but in addition we need to specify two parameters:

``` python
# Budget in whole units, not cents and using the same currency your ad account is configured
# This will be your reference budget set as your business as usual
budget = 30000

# Set different objectives to simulate
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

```
