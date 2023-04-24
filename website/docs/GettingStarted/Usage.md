---
sidebar_position: 2
---
# Use cases
The following steps will guide you through the whole process so you can start using OptiMate from the scratch.

OptiMate is a set of different codes/modules that aims to reproduce manual processes when planning and executing branding campaigns at Meta, so you can make it in a more automated way, driving efficiencies and identifying scenarios where you could improve results.

### Branding campaigns
OptiMate relies on the **[Meta Reach & Frequency buying type](https://www.facebook.com/business/help/885674161555708?id=842420845959022)**, which only considers the following campaign objectives: Reach, Brand Awareness, Engagement, Traffic and Video views that are commonly used for branding campaigns. Auction objectives are not considered in OptiMate nor Reach & Frequency predictions.

### Anticipating trade-offs between campaign parameters (Module 1, 2, 4, 5, 6)
When running Reach & Frequency predictions different parameters drive different reach, frequency and CPM results even when using the same budget. These parameters are being tested in different modules: Objectives (Module 1), Audience (Module 2), Frequency caps (Module 4), Campaign duration (Module 5) and Module 6 (the most robust) tests all these parameters at once, generating hundreds of simulations by combining different parameters at different budget levels.
![OptiMate Modules a](\img\OptiMate_Modules_a.png)


### Interest based audiences (Module 3)
When implementing branding campaings it is common that we have different ad creatives for different audiences. When those audiences are built using interests or behaviors it's possible to identify a set of interests/behaviors that are building reach in the most efficient way so we don't need to add more interest or behaviors. As a reference, in most of the cases there is no need to use more than 10 interests to have great reach levels.
![OptiMate Modules b](\img\OptiMate_Modules_b.png)

### Identify possible budget errors (Module 7)
This use case is not for planning campaigns but to track possible errors as soon as the campaign is being configured (no matter whether it is a Reach & Frequency or an Auction buying type). This module creates two dataframes, one for campaigns and one for adsets in order to identify budgets as outliers according to different confidence intervals.
![OptiMate Modules c](\img\OptiMate_Modules_c.png)

### Upper-mid funnel obejctives (Module 8)
When planning campaigns that will have a mix of upper (Reach, Brand Awareness) and mid funnel (Engagement, Traffic, Video views) objectives. This allows to identify the ideal mix of each objective to maximize reach/frequency or minimize CPMs.
![OptiMate Modules d](\img\OptiMate_Modules_d.png)


### In Stream video campaigns (Module 9)
For those campaigns where the main ad is a video format and we are aiming to maximize the probability of completed views using a Video views objective and the single In-stream video placement.
![OptiMate Modules e](\img\OptiMate_Modules_e.png)
