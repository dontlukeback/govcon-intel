# Contractor Lookup Pages

**Purpose:** SEO moat + lead generation via public contractor lookup pages.

## Strategy

This is a two-pronged play:

1. **VALUE ADD**: Contractors can look up their own federal contract activity
2. **SEO PLAY**: People searching "[contractor name] federal contracts" land on our page with subscribe CTAs

## How It Works

Every week, the system:
1. Identifies top contractors by award value
2. Generates static HTML pages for each contractor
3. Shows agency breakdown, vertical breakdown, and top 5 awards
4. Includes 2x subscribe CTAs per page
5. Auto-updates sitemap for SEO

## Files

- `generate_contractor_pages.py` - Main generator script
- `update_sitemap.py` - Updates sitemap.xml with all contractor pages
- `landing/contractors/*.html` - Generated contractor pages

## Usage

### Generate Pages

```bash
# Generate top 20 contractors (default)
python3 generate_contractor_pages.py

# Generate top 50 contractors
python3 generate_contractor_pages.py --limit 50
```

### Update Sitemap

```bash
python3 update_sitemap.py
```

### Weekly Regeneration

Add to your weekly pipeline:

```bash
python3 generate_contractor_pages.py
python3 update_sitemap.py
git add landing/contractors/*.html landing/sitemap.xml
git commit -m "chore: regenerate contractor pages with latest data"
git push
```

## Generated Pages

Each contractor page includes:

- **Header**: Contractor name + total contracts/value
- **Stats Grid**: Total contracts, total value, agencies, verticals
- **CTA #1**: "Track [Contractor]'s Federal Activity" with subscribe button
- **Agency Breakdown**: Top agencies by contract value
- **Vertical Breakdown**: Top verticals (Cyber, Cloud, AI/ML, etc.)
- **Top 5 Awards**: Recent high-value contracts with descriptions
- **CTA #2**: "Want Weekly Updates?" with subscribe button
- **Footer**: Links back to home, privacy, terms
- **Analytics**: tracker.js included for conversion tracking

## SEO Optimization

Each page has:
- **Title**: "[Contractor Name] Federal Contracts | GovCon Weekly Intelligence"
- **Meta Description**: Contract count + total value + "See agencies, verticals, and recent awards"
- **Canonical URL**: Proper canonical tags
- **OG Tags**: Social sharing optimization
- **Sitemap**: Auto-included with priority 0.7, weekly changefreq

## Data Moat

As we accumulate more weeks of data:
- Pages get richer with historical trends
- More contractors qualify for pages
- Better SEO rankings from content freshness
- Harder for competitors to replicate

## Target Search Terms

- "[contractor name] federal contracts"
- "[contractor name] government contracts"
- "[contractor name] federal awards"
- "[contractor name] DOD contracts"
- "[contractor name] GSA schedule"

## Conversion Funnel

1. **Discovery**: Organic search → contractor page
2. **Value**: See their contract data (agencies, verticals, awards)
3. **CTA**: Subscribe to track their activity weekly
4. **Nurture**: Weekly newsletter with competitive intelligence
5. **Upsell**: Offer Pro tier for deeper analytics

## Current Stats

- **Pages Generated**: 20 (top contractors by value)
- **Total Sitemap URLs**: 30 (includes blog, static pages, etc.)
- **Analytics**: tracker.js monitors page views + CTA clicks
- **Deploy**: Netlify auto-deploys on push to main

## Next Steps

1. Deploy and monitor organic traffic
2. Track conversion rate (page view → subscribe click)
3. Submit sitemap to Google Search Console
4. Add more contractors as data grows (50? 100?)
5. A/B test CTA copy and placement
6. Add "competitor comparison" links between pages
