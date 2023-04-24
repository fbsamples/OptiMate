import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Covers different use cases',
    Svg: require('@site/static/img/OptiMate_use_cases.svg').default,
    description: (
      <>
        Built to cover most common industry needs when planning
        branding campaigns at Meta. Use it to improve your campaign outcomes
        by leveraging on different objectives, campaign duration, audiences and
        frequency controls.

      </>
    ),
  },
  {
    title: 'Optimize Meta Ads results',
    Svg: require('@site/static/img/OptiMate_simulations.svg').default,
    description: (
      <>
        Run hundreds of campaign predictions instead of simulating manually.
        Having a full map of possibilities will allow you to take better decisions
        based on accurate data, using Meta's real time predictions for Reach & Frequency campaings.
      </>
    ),
  },
  {
    title: 'Test & Learn with experimental design',
    Svg: require('@site/static/img/OptiMate_testing.svg').default,
    description: (
      <>
        Go beyond and complement media results with Meta Brand Lift tests
        to measure impact on brand outcomes. Using experimental design to truly measure
        incremental results will provide more robust insights to take better media decisons.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
