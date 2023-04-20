import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>

      <div className="padding-vert--xl">
          <div className="container">
            <div className="row">
              <div className={clsx('col col--6', styles.descriptionSection)}>
                <h2>Unlock the power of media planning for Meta Ads</h2>
                <p className={styles.descriptionSectionText}>OptiMate is a Meta open-source tool to
                fetch Reach & Frequency predictions for branding campaigns at scale. Predicting
                hundreds of campaign media outcomes (reach, frequency, CPM) to identify the one that
                best brings optimized results. Data can be used also as a hypothesis generator for
                Brand Lift Multi-cell studies at Meta to measure media impact on brand outcomes (ad recall, message, intent, etc.) </p>
              </div>
              <div className="col col--6">
                <iframe
                  width="100%"
                  height="400"
                  src="https://www.youtube.com/embed/aPiT25lhj_s"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                />
              </div>
            </div>
          </div>
        </div>
    </Layout>
  );
}
