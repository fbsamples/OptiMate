# Planning Excellence Toolkit

Pre-built sample codes in Python that allows to take advantage of the Facebook's Reach & Frequency API to compare different strategies when planning campaigns for branding purposes.

## Examples

Use case Module 01: When planning campaigns under Reach & Frequency buying type, it is possible to fetch predictions on reach (people), frequency and CPMs, given specific campaign parameters such as: audience, dates, budget, placements and frequency control caps.

Using Module 01, it is possible to compare 5 different objectives: Reach, Brand Awareness, Video Views, Link clicks and Engagement. The code provides different charts showing predicted metrics under specific budgets on the following variables: Reach (number of people), Reach % (percentage of the potential audience), Total frequency (during the specified period), Weekly frequency (Total frequency divided by the number of weeks of the campaign) and Cost Per Mille (CPM). In addition, a CSV file is exported to have all the Reach & Frequency curves data in detail for further analysis.

## Example for Reach (people):

![](https://github.com/fbsamples/Planning_Excellence_Toolkit/blob/main/images/M01_Reach_people.PNG)

## Example for Total frequency:

![](https://github.com/fbsamples/Planning_Excellence_Toolkit/blob/main/images/M01_Total_frequency.PNG)

## Example for Cost Per Mille (CPM):

![](https://github.com/fbsamples/Planning_Excellence_Toolkit/blob/main/images/M01_CPM.PNG)



## Requirements
Sample codes in Python works with any operative system that is able to work on Python.

## Installing Facebook_business

Before you use any Module from this Toolkit, it is needed to install the latest version of the Facebook_business SDK in Python. You can refer to the following documentation to install the Python SDK and complete all the pre-requisites specified in the facebook-python-business-sdk/README.md file:

https://github.com/facebook/facebook-python-business-sdk

IMPORTANT: It is highly recommended to uninstall any other previous version of the Facebook_business. It can be done via pip:

*pip uninstall Facebook_business

## How Planning Excellence Toolkit works

Different use cases are covered in different Modules. Each module runs a specific code with an expected outcome. Take a look at each Module use case description in the DOCUMENTATION.txt file to choose the one that best fits your needs.

Once a specific module is selected, you need to add your own Ad Account ID and Access Token credentials to make the calls.

## Full documentation

Read the full documentation on the DOCUMENTATION.txt file

## Join the fbsamples community
* Website: https://github.com/fbsamples

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License
Planning Excellence Toolkit is licensed under the LICENSE file in this repository.
