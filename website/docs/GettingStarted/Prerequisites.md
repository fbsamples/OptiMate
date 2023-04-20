---
sidebar_position: 1
---

# Prerequisites
## Quick guide for installing the Meta Marketing API

Important: These steps and sample codes assume that you are working with Python 3.0 or the most recent version. Furthermore, before following this guide it’s important to have access to a Meta Business Manager Account and admin (or have permissions to manage) at least one Meta Ad Account.

---

## 1. Register an App on Facebook for Developers website

a.	Click on the next **[link](https://developers.facebook.com/apps/)** , click on ‘My apps’ and then click on ‘Create app’

b.	On the ‘Select an app type’ step, select ‘Business’ app and click ‘next’

c.	Give a name to the new App, write an e-mail, select the ‘App Purpose’ (Yourself or Clients) according to your needs, select a Business Manager Account and click on ‘Create App’

d.	If you are asked to re-enter your password, then complete the Security check

e.	An App Dashboard will be displayed, copy the App ID and save it, you will use it later

f.	On the left side tab, click on ‘Roles>>Roles’ and Add the Administrators, Developers or Testers or Analytics Users for your App, according to your needs

## 2. Link the App to a Business Manager

Note: If you already connected your app to a Business Manager Account (Section I, step ‘c’), skip this section

a.	Go to Business Manager **[page](https://business.facebook.com/home)** and click on the ‘Business Settings’  on the left tab

b.	Click on ‘Accounts’ on the left side of the page, and then click on ‘Apps’

c.	Click on ‘Add>>Add an App’ and paste the App ID you saved in previous steps. Then, click on ‘Add App’

## 3. Create a System User on Business Manager

a.	On Business Settings, click on ‘System Users>>Add’

b.	Assign a Name to the System user (or use an existing one), select a role and click on ‘Create System User’. When having an existing System user, you will have to assign an ‘Employee’ role.

c.	Select the ‘System User’ you will be working on and then click on ‘Add Assets’

d.	On the Select Asset Type section, click on Apps and click on the new App name you have recently created

e.	Assign the permissions you want to provide to the System user (Develop app, View insights, Test app or Manager App). Click on ‘Save Changes’

## 4. Generate Access Token

a.	On the same System Users section, click on the Admin System user name and then click on ‘Generate New Token’, select the App name and select all the Scopes you need to access and then click on ‘Generate Token’. When starting to use the Facebook Marketing API, we suggest selecting the following permissions: business_management, read_insights, ads_read and ads_management

b.	IMPORTANT: Copy and save in a safe place the Access Token. Anyone who has this token will have access to the Ad Accounts or Business information.

## 5. Install the Facebook SDK for Python

The Facebook_business package is compatible with Python versions 2 and 3.

•	The easiest way to install the SDK is via the pip on the Python Terminal

•	You can install the pip on the Terminal with: **easy_install pip**

a.	Once you have installed the pip, install Facebook_business: **pip install Facebook_business**

**IMPORTANT**: If you have already installed a previous version of Facebook_business, first uninstall it and then re-install. This is to make sure that you have the latest version

b.	Once you have completed these prerequisites you will be able do download OptiMate **[sample codes](https://github.com/fbsamples/OptiMate/tree/main/codes)** and start using them. Make sure to include your own Token and Ad Account credentials

c.	Follow each sample code instructions to fetch results for each Module according to your campaign needs. Take a look at the usage file to have a clear idea of the expected outcomes on each Module

More Meta Marketing API info on: https://developers.facebook.com/docs/marketing-apis

## Happy coding!
