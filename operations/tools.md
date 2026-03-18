# Tool Stack

Recommended tools for running GovCon Intelligence as a one-person operation. Prioritizes free tiers and simplicity.

---

## Core Stack

### Newsletter Platform: Beehiiv
- **URL:** https://www.beehiiv.com/
- **Plan:** Launch (free) -- up to 2,500 subscribers
- **Why:** Built for newsletter businesses. Includes analytics, referral program, monetization tools, custom domains. Upgrades cleanly when you grow.
- **Key features on free tier:** Unlimited sends, basic analytics, custom domain support, web archive

### Landing Page: Beehiiv (built-in) or Netlify/Vercel
- **Primary:** Use Beehiiv's built-in subscribe page. It's good enough to start and avoids managing another tool.
- **If you want custom:** Netlify (https://netlify.com) or Vercel (https://vercel.com) -- both free for static sites. Drop an HTML landing page in the `landing/` directory and deploy.

### Data Source: USAspending API
- **URL:** https://api.usaspending.gov/
- **Cost:** Free, no API key required
- **Note:** Already integrated in `pipeline.py`

### Data Source (future): SAM.gov Entity API
- **URL:** https://open.gsa.gov/api/entity-api/
- **Cost:** Free, requires API key registration
- **Use:** Contractor enrichment (DUNS, cage codes, past performance)

### AI Layer (optional): Claude API
- **URL:** https://console.anthropic.com/
- **Cost:** Pay-per-use, ~$0.50-2.00 per newsletter generation depending on model and token usage
- **Use:** Narrative sections in `generate_insights.py`, trend commentary

---

## Analytics

### Beehiiv Analytics (built-in)
- Open rate, click rate, subscriber growth, geographic data
- Sufficient for the first 6-12 months

### Google Analytics (optional)
- **URL:** https://analytics.google.com/
- **Cost:** Free
- **Use:** Track landing page traffic sources, conversion rate. Add the GA tag to your landing page.
- **When to add:** When you start driving traffic from LinkedIn/social and want to know which channels convert

---

## Business Operations

### Email: Gmail / Google Workspace
- **Start with:** Free Gmail account (govconintel@gmail.com or similar)
- **Upgrade to:** Google Workspace ($7/mo) when you want @govconweekly.com email
- **Use:** Reader replies, partnership outreach, advertiser communication

### CRM: Google Sheets (start) or Notion (scale)
- **Start with:** A single Google Sheet with tabs:
  - `Subscribers` -- growth log (date, count, source)
  - `Metrics` -- weekly open rate, CTR, unsubscribes
  - `Prospects` -- potential advertisers/sponsors
  - `Content Ideas` -- topics, reader requests
- **Upgrade to:** Notion (free for personal use) when you need more structure
- **Upgrade to:** HubSpot free CRM when you have 10+ active sponsor conversations

### Domain Registrar
- **Options:** Namecheap, Cloudflare Registrar, Google Domains
- **Cost:** ~$10-15/year for a .com
- **Recommendation:** Cloudflare Registrar (at-cost pricing, good DNS)
- **Action:** Register your domain early, even before you need it. Point MX records to Gmail/Workspace.

### Social: LinkedIn (organic)
- **Cost:** Free
- **Strategy:** Post 2-3x/week with insights from the newsletter. Link to subscribe page.
- **Scheduling (optional):** Buffer free tier (https://buffer.com) -- 3 scheduled posts per channel

### Payments: Stripe
- **URL:** https://stripe.com/
- **Cost:** 2.9% + $0.30 per transaction (no monthly fee)
- **When:** Only set up when you're ready for a paid tier or sponsorship invoicing
- **Integration:** Beehiiv has built-in Stripe integration for paid subscriptions

---

## Monthly Cost Estimates by Stage

### Stage 1: Pre-launch / First 100 subscribers
| Item | Cost |
|------|------|
| Beehiiv (Launch plan) | $0 |
| Domain | ~$1/mo ($12/year) |
| USAspending API | $0 |
| Claude API (optional) | ~$2-8/mo |
| **Total** | **$1-9/mo** |

### Stage 2: Growth / 100-1,000 subscribers
| Item | Cost |
|------|------|
| Beehiiv (Launch plan) | $0 |
| Domain | ~$1/mo |
| Google Workspace (custom email) | $7/mo |
| Claude API | ~$8-15/mo |
| Buffer free tier | $0 |
| **Total** | **$16-23/mo** |

### Stage 3: Monetization / 1,000-2,500 subscribers
| Item | Cost |
|------|------|
| Beehiiv (Launch plan, still free) | $0 |
| Domain | ~$1/mo |
| Google Workspace | $7/mo |
| Claude API | ~$15-25/mo |
| Stripe (per-transaction only) | Variable |
| **Total** | **$23-33/mo** |

### Stage 4: Scale / 2,500+ subscribers
| Item | Cost |
|------|------|
| Beehiiv (Scale plan) | $49/mo |
| Domain | ~$1/mo |
| Google Workspace | $7/mo |
| Claude API | ~$25-40/mo |
| Buffer paid (optional) | $6/mo |
| **Total** | **$88-103/mo** |

At Stage 4 you should be generating revenue from sponsorships or paid tiers that more than covers these costs.

---

## Tools You Do NOT Need Yet

Avoid adding these until there's a clear reason:

- **Mailchimp/ConvertKit** -- Beehiiv does everything they do, and better for newsletters
- **WordPress** -- Overkill for a landing page. Static HTML or Beehiiv's page is fine.
- **Zapier/Make** -- Your pipeline is a bash script. That's simpler and more reliable than a no-code workflow.
- **Paid analytics** -- Beehiiv analytics + Google Analytics free tier is plenty
- **Design tools** -- Beehiiv templates are clean. Don't spend time on custom email design until 1,000+ subs.
- **Podcast hosting** -- Stay focused on the newsletter. Add formats later.
