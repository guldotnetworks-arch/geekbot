# geekbot

YouTube creator reference data and tooling.

## Data

### `data/rpm_benchmarks.json`

Verified YouTube RPM and CPM benchmark data aggregated from creator-facing sources.

**Sources cross-referenced:**
- [OutlierKit](https://outlierkit.com/blog/most-profitable-youtube-niches) — AI + human curated niche RPM data, updated monthly from creator-reported dashboards
- [Lenos (LenosTube)](https://www.lenostube.com/en/youtube-cpm-rpm-rates/) — Aggregated CPM/RPM rates by country and niche from creator report data
- [upGrowth](https://upgrowth.in/youtube-cpm-overview-highest-paying-niches/) — Industry research panel, CPM by country and niche
- [MilX](https://milx.app/en/trends/the-most-profitable-youtube-niches-in-2025) — Creator market analysis 2025
- [Influencer Marketing Hub](https://influencermarketinghub.com/youtube-shorts-rpm/) — YouTube Shorts RPM benchmarks

**What's in the file:**

| Section | Description |
|---|---|
| `rpm_by_niche` | RPM ranges for 19 niches, US long-form, with confidence ratings |
| `rpm_shorts` | YouTube Shorts RPM benchmarks (dramatically lower than long-form) |
| `cpm_by_country` | Advertiser CPM for 8 countries with Tier classification |
| `seasonal_multipliers` | Q1–Q4 relative RPM factors with real platform-wide CPM data points |
| `rpm_vs_cpm_explainer` | Definition of the CPM→RPM gap and the 45% YouTube cut |

**Methodology note:** No publicly available tool has direct access to YouTube's Analytics API for third-party channels. All figures are aggregated from creator-submitted dashboard data, public disclosures, and research panels. Values are benchmarks, not guarantees — your actual RPM will vary based on audience geography, watch time, ad-blocker rate, and content quality signals.
