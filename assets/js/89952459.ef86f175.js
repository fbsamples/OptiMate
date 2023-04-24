"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[186],{3905:(e,t,n)=>{n.d(t,{Zo:()=>c,kt:()=>k});var a=n(7294);function s(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function r(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){s(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function i(e,t){if(null==e)return{};var n,a,s=function(e,t){if(null==e)return{};var n,a,s={},o=Object.keys(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||(s[n]=e[n]);return s}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(s[n]=e[n])}return s}var l=a.createContext({}),p=function(e){var t=a.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):r(r({},t),e)),n},c=function(e){var t=p(e.components);return a.createElement(l.Provider,{value:t},e.children)},u="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},h=a.forwardRef((function(e,t){var n=e.components,s=e.mdxType,o=e.originalType,l=e.parentName,c=i(e,["components","mdxType","originalType","parentName"]),u=p(n),h=s,k=u["".concat(l,".").concat(h)]||u[h]||d[h]||o;return n?a.createElement(k,r(r({ref:t},c),{},{components:n})):a.createElement(k,r({ref:t},c))}));function k(e,t){var n=arguments,s=t&&t.mdxType;if("string"==typeof e||s){var o=n.length,r=new Array(o);r[0]=h;var i={};for(var l in t)hasOwnProperty.call(t,l)&&(i[l]=t[l]);i.originalType=e,i[u]="string"==typeof e?e:s,r[1]=i;for(var p=2;p<o;p++)r[p]=n[p];return a.createElement.apply(null,r)}return a.createElement.apply(null,n)}h.displayName="MDXCreateElement"},3494:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>l,contentTitle:()=>r,default:()=>d,frontMatter:()=>o,metadata:()=>i,toc:()=>p});var a=n(7462),s=(n(7294),n(3905));const o={sidebar_position:1},r="Prerequisites",i={unversionedId:"GettingStarted/Prerequisites",id:"GettingStarted/Prerequisites",title:"Prerequisites",description:"Quick guide for installing the Meta Marketing API",source:"@site/docs/GettingStarted/Prerequisites.md",sourceDirName:"GettingStarted",slug:"/GettingStarted/Prerequisites",permalink:"/OptiMate/docs/GettingStarted/Prerequisites",draft:!1,editUrl:"https://github.com/fbsamples/OptiMate/docs/GettingStarted/Prerequisites.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1},sidebar:"tutorialSidebar",previous:{title:"Welcome to OptiMate",permalink:"/OptiMate/docs/intro"},next:{title:"Use cases",permalink:"/OptiMate/docs/GettingStarted/Usage"}},l={},p=[{value:"Quick guide for installing the Meta Marketing API",id:"quick-guide-for-installing-the-meta-marketing-api",level:2},{value:"1. Register an App on Facebook for Developers website",id:"1-register-an-app-on-facebook-for-developers-website",level:2},{value:"2. Link the App to a Business Manager",id:"2-link-the-app-to-a-business-manager",level:2},{value:"3. Create a System User on Business Manager",id:"3-create-a-system-user-on-business-manager",level:2},{value:"4. Generate Access Token",id:"4-generate-access-token",level:2},{value:"5. Install the Facebook SDK for Python",id:"5-install-the-facebook-sdk-for-python",level:2},{value:"Happy coding!",id:"happy-coding",level:2}],c={toc:p},u="wrapper";function d(e){let{components:t,...n}=e;return(0,s.kt)(u,(0,a.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,s.kt)("h1",{id:"prerequisites"},"Prerequisites"),(0,s.kt)("h2",{id:"quick-guide-for-installing-the-meta-marketing-api"},"Quick guide for installing the Meta Marketing API"),(0,s.kt)("p",null,"Important: These steps and sample codes assume that you are working with Python 3.0 or the most recent version. Furthermore, before following this guide it\u2019s important to have access to a Meta Business Manager Account and admin (or have permissions to manage) at least one Meta Ad Account."),(0,s.kt)("hr",null),(0,s.kt)("h2",{id:"1-register-an-app-on-facebook-for-developers-website"},"1. Register an App on Facebook for Developers website"),(0,s.kt)("p",null,"a.\tClick on the next ",(0,s.kt)("strong",{parentName:"p"},(0,s.kt)("a",{parentName:"strong",href:"https://developers.facebook.com/apps/"},"link"))," , click on \u2018My apps\u2019 and then click on \u2018Create app\u2019"),(0,s.kt)("p",null,"b.\tOn the \u2018Select an app type\u2019 step, select \u2018Business\u2019 app and click \u2018next\u2019"),(0,s.kt)("p",null,"c.\tGive a name to the new App, write an e-mail, select the \u2018App Purpose\u2019 (Yourself or Clients) according to your needs, select a Business Manager Account and click on \u2018Create App\u2019"),(0,s.kt)("p",null,"d.\tIf you are asked to re-enter your password, then complete the Security check"),(0,s.kt)("p",null,"e.\tAn App Dashboard will be displayed, copy the App ID and save it, you will use it later"),(0,s.kt)("p",null,"f.\tOn the left side tab, click on \u2018Roles>>Roles\u2019 and Add the Administrators, Developers or Testers or Analytics Users for your App, according to your needs"),(0,s.kt)("h2",{id:"2-link-the-app-to-a-business-manager"},"2. Link the App to a Business Manager"),(0,s.kt)("p",null,"Note: If you already connected your app to a Business Manager Account (Section I, step \u2018c\u2019), skip this section"),(0,s.kt)("p",null,"a.\tGo to Business Manager ",(0,s.kt)("strong",{parentName:"p"},(0,s.kt)("a",{parentName:"strong",href:"https://business.facebook.com/home"},"page"))," and click on the \u2018Business Settings\u2019  on the left tab"),(0,s.kt)("p",null,"b.\tClick on \u2018Accounts\u2019 on the left side of the page, and then click on \u2018Apps\u2019"),(0,s.kt)("p",null,"c.\tClick on \u2018Add>>Add an App\u2019 and paste the App ID you saved in previous steps. Then, click on \u2018Add App\u2019"),(0,s.kt)("h2",{id:"3-create-a-system-user-on-business-manager"},"3. Create a System User on Business Manager"),(0,s.kt)("p",null,"a.\tOn Business Settings, click on \u2018System Users>>Add\u2019"),(0,s.kt)("p",null,"b.\tAssign a Name to the System user (or use an existing one), select a role and click on \u2018Create System User\u2019. When having an existing System user, you will have to assign an \u2018Employee\u2019 role."),(0,s.kt)("p",null,"c.\tSelect the \u2018System User\u2019 you will be working on and then click on \u2018Add Assets\u2019"),(0,s.kt)("p",null,"d.\tOn the Select Asset Type section, click on Apps and click on the new App name you have recently created"),(0,s.kt)("p",null,"e.\tAssign the permissions you want to provide to the System user (Develop app, View insights, Test app or Manager App). Click on \u2018Save Changes\u2019"),(0,s.kt)("h2",{id:"4-generate-access-token"},"4. Generate Access Token"),(0,s.kt)("p",null,"a.\tOn the same System Users section, click on the Admin System user name and then click on \u2018Generate New Token\u2019, select the App name and select all the Scopes you need to access and then click on \u2018Generate Token\u2019. When starting to use the Facebook Marketing API, we suggest selecting the following permissions: business_management, read_insights, ads_read and ads_management"),(0,s.kt)("p",null,"b.\tIMPORTANT: Copy and save in a safe place the Access Token. Anyone who has this token will have access to the Ad Accounts or Business information."),(0,s.kt)("h2",{id:"5-install-the-facebook-sdk-for-python"},"5. Install the Facebook SDK for Python"),(0,s.kt)("p",null,"The Facebook_business package is compatible with Python versions 2 and 3."),(0,s.kt)("p",null,"\u2022\tThe easiest way to install the SDK is via the pip on the Python Terminal"),(0,s.kt)("p",null,"\u2022\tYou can install the pip on the Terminal with: ",(0,s.kt)("strong",{parentName:"p"},"easy_install pip")),(0,s.kt)("p",null,"a.\tOnce you have installed the pip, install Facebook_business: ",(0,s.kt)("strong",{parentName:"p"},"pip install Facebook_business")),(0,s.kt)("p",null,(0,s.kt)("strong",{parentName:"p"},"IMPORTANT"),": If you have already installed a previous version of Facebook_business, first uninstall it and then re-install. This is to make sure that you have the latest version"),(0,s.kt)("p",null,"b.\tOnce you have completed these prerequisites you will be able do download OptiMate ",(0,s.kt)("strong",{parentName:"p"},(0,s.kt)("a",{parentName:"strong",href:"https://github.com/fbsamples/OptiMate/tree/main/codes"},"sample codes"))," and start using them. Make sure to include your own Token and Ad Account credentials"),(0,s.kt)("p",null,"c.\tFollow each sample code instructions to fetch results for each Module according to your campaign needs. Take a look at the usage file to have a clear idea of the expected outcomes on each Module"),(0,s.kt)("p",null,"More Meta Marketing API info on: ",(0,s.kt)("a",{parentName:"p",href:"https://developers.facebook.com/docs/marketing-apis"},"https://developers.facebook.com/docs/marketing-apis")),(0,s.kt)("h2",{id:"happy-coding"},"Happy coding!"))}d.isMDXComponent=!0}}]);