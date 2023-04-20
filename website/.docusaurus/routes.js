import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/OptiMate/blog',
    component: ComponentCreator('/OptiMate/blog', '44c'),
    exact: true
  },
  {
    path: '/OptiMate/blog/archive',
    component: ComponentCreator('/OptiMate/blog/archive', 'b11'),
    exact: true
  },
  {
    path: '/OptiMate/blog/first-blog-post',
    component: ComponentCreator('/OptiMate/blog/first-blog-post', '90a'),
    exact: true
  },
  {
    path: '/OptiMate/blog/long-blog-post',
    component: ComponentCreator('/OptiMate/blog/long-blog-post', '786'),
    exact: true
  },
  {
    path: '/OptiMate/blog/mdx-blog-post',
    component: ComponentCreator('/OptiMate/blog/mdx-blog-post', 'ae3'),
    exact: true
  },
  {
    path: '/OptiMate/blog/tags',
    component: ComponentCreator('/OptiMate/blog/tags', 'e2b'),
    exact: true
  },
  {
    path: '/OptiMate/blog/tags/docusaurus',
    component: ComponentCreator('/OptiMate/blog/tags/docusaurus', '0a2'),
    exact: true
  },
  {
    path: '/OptiMate/blog/tags/facebook',
    component: ComponentCreator('/OptiMate/blog/tags/facebook', '837'),
    exact: true
  },
  {
    path: '/OptiMate/blog/tags/hello',
    component: ComponentCreator('/OptiMate/blog/tags/hello', '299'),
    exact: true
  },
  {
    path: '/OptiMate/blog/tags/hola',
    component: ComponentCreator('/OptiMate/blog/tags/hola', '51b'),
    exact: true
  },
  {
    path: '/OptiMate/blog/welcome',
    component: ComponentCreator('/OptiMate/blog/welcome', 'e1b'),
    exact: true
  },
  {
    path: '/OptiMate/markdown-page',
    component: ComponentCreator('/OptiMate/markdown-page', '318'),
    exact: true
  },
  {
    path: '/OptiMate/my-markdown-page',
    component: ComponentCreator('/OptiMate/my-markdown-page', '8b3'),
    exact: true
  },
  {
    path: '/OptiMate/my-react-page',
    component: ComponentCreator('/OptiMate/my-react-page', '012'),
    exact: true
  },
  {
    path: '/OptiMate/docs',
    component: ComponentCreator('/OptiMate/docs', '536'),
    routes: [
      {
        path: '/OptiMate/docs/FAQs',
        component: ComponentCreator('/OptiMate/docs/FAQs', '49d'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/OptiMate/docs/GettingStarted/Input parameters',
        component: ComponentCreator('/OptiMate/docs/GettingStarted/Input parameters', '389'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/OptiMate/docs/GettingStarted/Outcomes',
        component: ComponentCreator('/OptiMate/docs/GettingStarted/Outcomes', 'a15'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/OptiMate/docs/GettingStarted/Prerequisites',
        component: ComponentCreator('/OptiMate/docs/GettingStarted/Prerequisites', '340'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/OptiMate/docs/GettingStarted/Test & Learn',
        component: ComponentCreator('/OptiMate/docs/GettingStarted/Test & Learn', '3b2'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/OptiMate/docs/GettingStarted/Usage',
        component: ComponentCreator('/OptiMate/docs/GettingStarted/Usage', 'cd7'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/OptiMate/docs/intro',
        component: ComponentCreator('/OptiMate/docs/intro', '36a'),
        exact: true,
        sidebar: "tutorialSidebar"
      }
    ]
  },
  {
    path: '/OptiMate/',
    component: ComponentCreator('/OptiMate/', 'b37'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
