# Marketing Automation

Automated subscriber growth tools for GovCon Weekly Intelligence.

## What's Here

### Strategic Guides
- **`auto-growth.md`** (288 lines) — Complete playbook for Substack growth
  - Why Substack Notes API doesn't exist (and what to do instead)
  - Platform-native growth levers (recommendations, SEO, cross-posting)
  - 90-day roadmap to 500 subscribers without paid ads

- **`AUTOMATION-SETUP.md`** (237 lines) — Quick start guide
  - Weekly workflow (15 min/week)
  - Zapier automation ideas
  - Growth metrics to track

### Tools
- **`weekly-auto-content.py`** (399 lines) — Content generator
  - Input: `output/data_YYYY-MM-DD.json` (awards data)
  - Output: 14 ready-to-post pieces of content
    - 5 LinkedIn posts
    - 3 Twitter threads
    - 1 Reddit post
    - 5 Substack Notes
  - Usage: `python3 marketing/weekly-auto-content.py`

- **`../post_note.py`** (311 lines) — Notes API demo (educational only)
  - ⚠️ DO NOT USE IN PRODUCTION
  - Demonstrates reverse-engineered Substack API
  - Risk of account suspension
  - **Recommendation:** Post Notes manually via UI

## Quick Start

### 1. Generate Weekly Content
```bash
cd ~/Personal/govcon-intel
python3 marketing/weekly-auto-content.py
```

Output saved to `output/social/`:
- `linkedin_01_weekly_summary.txt` through `linkedin_05_recompete_signal.txt`
- `twitter_thread_01.txt` through `twitter_thread_03.txt`
- `reddit_post.txt`
- `substack_note_01_data_hook.txt` through `substack_note_05_question.txt`

### 2. Distribute (15 Minutes)
1. **LinkedIn** (2 posts/week): Copy files, replace `[LINK]`, post Mon/Thu 8am
2. **Substack Notes** (3-5/week): Copy files, post to https://substack.com/notes/new
3. **Twitter** (1 thread/week): Copy file, thread via UI, post Tue 9am
4. **Reddit** (1 post/week): Copy file, post to r/governmentcontracting, Wed 10am

### 3. Track Results
- Substack Dashboard → Stats → Referrers (which platform drives subscribers)
- Use UTM parameters: `?utm_source=linkedin&utm_medium=post1`

## Key Findings from Research

### Substack Notes API Status
**Does NOT exist officially.**
- Reverse-engineered endpoints documented at github.com/can3p/substack-api-notes
- Only supports drafts (`POST /api/v1/drafts`), NOT Notes
- Attempting to post Notes via undocumented API = TOS violation risk

**Recommendation:** Manual posting via UI takes 5 min/week. Not worth automation risk.

### Highest-ROI Growth Levers
1. **Recommendation Network** (30-60% of new subs) — Outreach to 10 adjacent publications for cross-recommendations
2. **Substack Notes** (10-50 subs per viral Note) — Post 3-5x/week, use engagement hooks
3. **LinkedIn Cross-Posting** (organic reach + backlinks) — 2x/week, data-driven posts
4. **Referral Program** (10-15% refer 1+ people) — Set milestones: 3/10/25 referrals = rewards
5. **SEO** (passive discovery) — Optimize publication description, use long-tail keywords in titles

### What NOT to Do
- ❌ Don't build a Notes API integration (unsupported, risky)
- ❌ Don't spam Reddit/LinkedIn (1-2 quality posts/week beats 10 low-effort posts)
- ❌ Don't pay for ads before testing organic channels (test Notes + recommendations first)
- ❌ Don't automate without manual review (generated content needs human editing)

## Growth Roadmap: 90 Days to 500 Subscribers

### Month 1: Foundation (Current)
- [x] Build content generator ✅
- [x] Document growth playbook ✅
- [ ] Optimize Substack SEO (custom domain, description)
- [ ] Set up referral program (Dashboard → Settings → Referrals)
- [ ] Post 3-5 Notes/week manually
- [ ] Test LinkedIn cross-posting (2x/week)

### Month 2: Distribution
- [ ] Outreach to 10 publications (cross-recommendation pitches)
- [ ] Create 1 lead magnet (Recompete Calendar spreadsheet)
- [ ] Reddit seeding (2-3 posts/month)
- [ ] Zapier automation (Slack reminder when newsletter publishes)

### Month 3: Scale
- [ ] Test Substack Boost ($500 budget, measure CAC vs LTV)
- [ ] A/B test paywall placement + subject lines
- [ ] Guest post on 2 GovCon blogs (backlinks)
- [ ] Launch paid subscriber onboarding sequence

## Files in This Directory

| File | Lines | Purpose |
|------|-------|---------|
| `auto-growth.md` | 288 | Complete growth strategy guide |
| `AUTOMATION-SETUP.md` | 237 | Quick start + weekly workflow |
| `weekly-auto-content.py` | 399 | Auto-generate 14 pieces of social content |
| `README.md` | This file | Marketing automation overview |
| `channels.md` | — | Original marketing channels doc |
| `content-calendar.md` | — | Original content calendar |
| `social-posts.md` | — | Original social post ideas |
| `strategy.md` | — | Original marketing strategy |

## Integration with Pipeline

The content generator is designed to run AFTER the data pipeline:

```bash
# Full workflow
./generate.sh                           # Step 1-4: Pull data, enrich, generate newsletters
python3 marketing/weekly-auto-content.py  # Step 5: Generate social content
```

The script reads from `output/data_YYYY-MM-DD.json` (latest awards file) and generates ready-to-post content in `output/social/`.

## Support

For questions or issues:
1. Read `auto-growth.md` sections 1-5 (covers 80% of questions)
2. Check `AUTOMATION-SETUP.md` FAQ section
3. Review generated content examples in `output/social/`

## Next Steps

1. **Run the generator:** `python3 marketing/weekly-auto-content.py`
2. **Review output:** Check `output/social/` files for quality
3. **Post 3 items this week:** 1 LinkedIn + 2 Notes (test engagement)
4. **Read auto-growth.md:** Sections 1-3 (Notes + Recommendations + SEO)
5. **Set up referral program:** Dashboard → Settings → Referrals

**Goal:** 50 new subscribers this month via organic channels (no ads).
