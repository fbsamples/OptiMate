"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[128],{3905:(e,n,t)=>{t.d(n,{Zo:()=>c,kt:()=>h});var a=t(7294);function r(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function o(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);n&&(a=a.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,a)}return t}function i(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?o(Object(t),!0).forEach((function(n){r(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):o(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function s(e,n){if(null==e)return{};var t,a,r=function(e,n){if(null==e)return{};var t,a,r={},o=Object.keys(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||(r[t]=e[t]);return r}(e,n);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(r[t]=e[t])}return r}var u=a.createContext({}),d=function(e){var n=a.useContext(u),t=n;return e&&(t="function"==typeof e?e(n):i(i({},n),e)),t},c=function(e){var n=d(e.components);return a.createElement(u.Provider,{value:n},e.children)},m="mdxType",l={inlineCode:"code",wrapper:function(e){var n=e.children;return a.createElement(a.Fragment,{},n)}},p=a.forwardRef((function(e,n){var t=e.components,r=e.mdxType,o=e.originalType,u=e.parentName,c=s(e,["components","mdxType","originalType","parentName"]),m=d(t),p=r,h=m["".concat(u,".").concat(p)]||m[p]||l[p]||o;return t?a.createElement(h,i(i({ref:n},c),{},{components:t})):a.createElement(h,i({ref:n},c))}));function h(e,n){var t=arguments,r=n&&n.mdxType;if("string"==typeof e||r){var o=t.length,i=new Array(o);i[0]=p;var s={};for(var u in n)hasOwnProperty.call(n,u)&&(s[u]=n[u]);s.originalType=e,s[m]="string"==typeof e?e:r,i[1]=s;for(var d=2;d<o;d++)i[d]=t[d];return a.createElement.apply(null,i)}return a.createElement.apply(null,t)}p.displayName="MDXCreateElement"},3953:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>u,contentTitle:()=>i,default:()=>l,frontMatter:()=>o,metadata:()=>s,toc:()=>d});var a=t(7462),r=(t(7294),t(3905));const o={sidebar_position:3},i="Main input Parameters",s={unversionedId:"GettingStarted/Input parameters",id:"GettingStarted/Input parameters",title:"Main input Parameters",description:"Must have parameters",source:"@site/docs/GettingStarted/Input parameters.md",sourceDirName:"GettingStarted",slug:"/GettingStarted/Input parameters",permalink:"/OptiMate/docs/GettingStarted/Input parameters",draft:!1,editUrl:"https://github.com/fbsamples/OptiMate/docs/GettingStarted/Input parameters.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"Use cases",permalink:"/OptiMate/docs/GettingStarted/Usage"},next:{title:"Outcomes",permalink:"/OptiMate/docs/GettingStarted/Outcomes"}},u={},d=[{value:"Must have parameters",id:"must-have-parameters",level:2}],c={toc:d},m="wrapper";function l(e){let{components:n,...t}=e;return(0,r.kt)(m,(0,a.Z)({},c,t,{components:n,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"main-input-parameters"},"Main input Parameters"),(0,r.kt)("h2",{id:"must-have-parameters"},"Must have parameters"),(0,r.kt)("p",null,"In most of the modules you will need to input the following parameters. It's important to make sure you have permissions to access at least one Meta Ad Account, so you can fetch predictions and get insights."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"#---------------------------------------------INPUT SECTION----------------------------------------------#\n# Include your own access token instead of xxxxxx\naccess_token = 'xxxxxx'\n\n# Make sure you are using the latest API version\n# You can double check on: https://developers.facebook.com/docs/graph-api/guides/versioning\napi_version = 'v15.0'\n\n# Initiate the Facebook Business API with the access token\napi = FacebookAdsApi.init(\n    access_token = access_token,\n    api_version = api_version,\n)\n\n# Set the Ad Account on which you want to have the predictions. Replace the xxxxxx with your own Account ID\nad_account_id = 'act_xxxxxx'\n\n# Write the directory where you want to save all the OUTPUTS\nsave_directory = 'C:/Users/username/Desktop/' # this is just an example on PC\n\n")),(0,r.kt)("h1",{id:"parameters-for-modules-1-2-4-5-and-9"},"Parameters for Modules 1, 2, 4, 5 and 9"),(0,r.kt)("p",null,"Use Reach & Frequency predictions to bring results depending on different objectives, audiences, campaign duration and frequency control caps. In these Modules you will need to input specific campaign parameters to have a specific prediction on that. Depending on each Module some inputs are predefined (by design) and some others can be customized:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"# Specify the objective you want to test\n# Available Objectives are: BRAND_AWARENESS, LINK_CLICKS, POST_ENGAGEMENT, REACH and VIDEO_VIEWS\nobjective = 'REACH'\n\n# Input the minimum and maximum ages\n# In Meta Ads Platforms, minimum available is 13 years old and maximum is 65, which stands for people 65+ years old\nage_min = 18\nage_max = 65\n\n# Input the genders in a list. 2-for female, 1-for male\ngender_list = [1,2]\n\n# Input the county for the ads delivery\ncountries = ['MX'] # Write your country acronym\n\n# Define the amount of days for your Campaign predictions\ncamp_days = 28 # The maximum days that the prediction can be done is 90 within a 6 months window from now\n\n# Frequency caps\n# Needs the maximum number of times your ad will be shown to a person during a specifyed time period\n# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days\nfrequency_cap = 2\nevery_x_days = 7\n\n# When using interest-behavior based audiences, make sure that you have already saved the audience in the same AdAccount in Ads Manager you are using for the Reach&Frequency predictions\n# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction\n# ONLY for interests or behaviors audiences\n# If you ARE NOT using interests/behaviors, leave audience_name = 'None'\naudience_name = 'None'\n\n# Days before the campaign begins\n# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on\n# Minimum and default value is 1\ndays_prior_start = 1\n\n")),(0,r.kt)("h1",{id:"parameters-for-module-3"},"Parameters for Module 3"),(0,r.kt)("p",null,"In addition to the must have parameters, for Module 3 it's only needed the name of the audience you need to optimize. To that end it's very important thar first you create the audience by following:"),(0,r.kt)("ol",null,(0,r.kt)("li",{parentName:"ol"},"Go to Ads Manager>>Audiences section"),(0,r.kt)("li",{parentName:"ol"},"Click on Create Audience>>Saved Audience"),(0,r.kt)("li",{parentName:"ol"},"Define demographics and desired interest-behaviors and 'Name your audience'\nNote: this Module only works with Saved Audiences, not for Custom Audiences nor LookAlike Audiences")),(0,r.kt)("h1",{id:"filter-by-name-only-those-audiences-that-you-want-to-optimize-on-interests"},"Filter by name only those audiences that you want to optimize on interests"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"# Example for a Saved Audience named 'Saved_Audience_Name'\naudiences_list = ['Saved_Audience_Name', # SET YOUR OWN AUDIENCE NAME\n                 ]\n\n")),(0,r.kt)("h1",{id:"parameters-for-module-6"},"Parameters for Module 6"),(0,r.kt)("p",null,"Very similar to Modules 1, 2, 4, 5 and 9 but in this case as this is the most robust module we can define different parameters at once to perform several combinations. Instead of having single value parameters, we can work with lists and a defined reference budget:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"# Budget in whole units, not cents and using the same currency your ad account is configured\n# This will be your reference budget set as your business as usual\nbudget = 100000\n\n# Input the country for the ads delivery\n# Write your country acronym. If not sure about your country, search about Country Postal Abbreviations on the web\ncountries = [['MX']]\n\n# Input all the campaing specs for your prediction\n# Input the minimum and maximum ages\n# In Meta Ads Platforms, minimum available is 13 years old and maximum is 65, which stands for people 65+ years old\n\nages = [[25,50], [25,65]]\n\n# Input the genders. 2-for female, 1-for male\ngender_list = [[1,2]]\n\n# When using interest-behavior based audiences, make sure that you have already save the audience in the\n# same AdAccount in Ads Manager you are using for the Reach&Frequency predictions\n# Once the audience is saved, you can use EXACTLY the same name as an input for the prediction\n# ONLY for interests or behaviors audience\n# If you ARE NOT using interests, leave audience_name = 'None'\naudience_name = 'None' # Add your own Audience name\n\n# This example covers different days, frequency caps and objectives combinations\n# Furthermore, it can be customized according to your needs\n# Just keep in mind that the combinations of all parameters does not exceed around 70-80 calls per hour\n# Otherwise rate limits will show an error\n# IF more than 70-80 combinations are needed, you can use a time.sleep()\n\n# Define the amount of days for your Campaign predictions\ncamp_days = [28, 35, 42]\n\n# Set different objectives to siulate\n# Different objectives are: 'BRAND_AWARENESS', 'REACH', 'LINK_CLICKS', 'POST_ENGAGEMENT' AND 'VIDEO_VIEWS'\ncamp_objectives = [\n    'REACH',\n    'BRAND_AWARENESS',\n]\n\n# Frequency caps\n# Needs the maximum number of times your ad will be shown to a person during a specifyed time period\n# Example: maximump_cap = 2 and every_x_days = 7 means that your ad won't be shown more than 2 times every 7 days\nmaximum_caps = [3, 4, 5]\nevery_x_days = 7\n\n# Days before the campaign begins\n# When 1, means that the campaign will begin tomorrow, 7 means that the campaign will begin in one week, and so on\n# Minimum and default value is 1\ndays_prior_start = 1\n\n")),(0,r.kt)("h1",{id:"parameters-for-module-7"},"Parameters for Module 7"),(0,r.kt)("p",null,"As this Module performs a confidence intervals analysis, it's needed to define a time frame. Besides this input and the must have credentials the rest of the analysis is performed by the code itself."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"# Define the dates you want to make the call on to fetch historical data\n# Historical data has to be fetched only the first time\n# Next calls can be updated on a daily/weekly basis\n\nsince_date = '2023-01-01'\nuntil_date = '2023-03-31'\n\n# Write the directory where you want to save all the OUTPUTS\nsave_directory = 'C:/Users/username/Desktop/' # this is just an example on PC\n\n")),(0,r.kt)("h1",{id:"parameters-for-module-8"},"Parameters for Module 8"),(0,r.kt)("p",null,"Inputs for this Module are very similar to the ones in the Modules 1, 2, 4, 5 and 9 but in addition we need to specify two parameters:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"# Budget in whole units, not cents and using the same currency your ad account is configured\n# This will be your reference budget set as your business as usual\nbudget = 30000\n\n# Set different objectives to simulate\n# Different objectives are: 'BRAND_AWARENESS', 'REACH', 'LINK_CLICKS', 'POST_ENGAGEMENT' AND 'VIDEO_VIEWS'\n# USE ONLY TWO OBJECTIVES AT ONCE: LIST OF 2 ELEMENTS ONLY\n# IDEALLY TO TEST 1 UPPER FUNNNEL OBJECTIVE (REACH OR BRAND_AWARENESS) VERSUS 1 MID FUNNEL OBJECTIVE (LINK_CLICKS,\n# POST_ENGAGEMENT OR VIDEO_VIEWS)\ncamp_objectives = [\n    #'REACH',\n    'BRAND_AWARENESS',\n    'LINK_CLICKS',\n    #'POST_ENGAGEMENT',\n    #'VIDEO_VIEWS',\n]\n\n")))}l.isMDXComponent=!0}}]);