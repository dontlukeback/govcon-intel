# GovCon Intel: Automated Growth Setup

## Overview

This folder contains automation tools to drive subscriber growth WITHOUT manual content creation.

Every week when the pipeline runs, it now ALSO generates ready-to-post social content across 4 platforms.

## What's Been Built

### 1. Auto-Growth Playbook (`auto-growth.md`)
**Comprehensive guide covering:**
- Substack Notes strategy (why manual posting is better than API)
- Recommendation network tactics (how to get cross-recommended)
- Substack SEO optimization (publication settings + per-post)
- Cross-posting strategies (LinkedIn, Twitter, Reddit)
- Referral program setup
- Paid acquisition (Substack Boost, LinkedIn ads)
- 90-day priority roadmap

**Key Finding:** Substack Notes API doesn't officially exist. Reverse-engineered endpoints are risky (TOS violation, account suspension). **Recommendation: Post Notes manually via UI (5 min/week).**

---

### 2. Weekly Auto-Content Generator (`weekly-auto-content.py`)
**Generates 14 pieces of content from awards data:**
- 5 LinkedIn posts (data insights, winner spotlights, market signals)
- 3 Twitter threads (7 tweets each)
- 1 Reddit post (r/governmentcontracting format)
- 5 Substack Notes (500 char limit, engagement hooks)

**All content saved to:** `output/social/` for copy-paste distribution.

**Run weekly:**
```bash
cd ~/Personal/govcon-intel
python3 marketing/weekly-auto-content.py
```

**Output:** 14 text files ready to post (just replace `[LINK]` with newsletter URL).

---

### 3. Substack Notes Poster (`post_note.py`)
**Educational tool demonstrating reverse-engineered API.**

⚠️ **DO NOT USE IN PRODUCTION**
- No official API
- Risk of account suspension
- Unsupported endpoints may break

**Recommended alternative:** Use Zapier to trigger Slack reminder when newsletter publishes → manually post 3-5 Notes via Substack UI.

**If you want to experiment (at your own risk):**
```bash
# Get your substack.sid cookie (from browser DevTools)
export SUBSTACK_SID='your-cookie-value'

# Generate and preview Notes
python3 post_note.py
# Choose option 1: Copy-paste to UI (RECOMMENDED)
# Choose option 2: Attempt API post (RISKY)
# Choose option 3: Save to files
```

---

## Quick Start: Weekly Workflow

### Step 1: Run the Pipeline
```bash
cd ~/Personal/govcon-intel
./generate.sh  # Pulls data, enriches, generates newsletter
```

### Step 2: Generate Social Content
```bash
python3 marketing/weekly-auto-content.py
```

This creates:
```
output/social/
├── linkedin_01_weekly_summary.txt
├── linkedin_02_winner_spotlight.txt
├── linkedin_03_market_signal.txt
├── linkedin_04_vertical_trend.txt
├── linkedin_05_recompete_signal.txt
├── twitter_thread_01.txt
├── twitter_thread_02.txt
├── twitter_thread_03.txt
├── reddit_post.txt
├── substack_note_01_data_hook.txt
├── substack_note_02_hot_take.txt
├── substack_note_03_lesson.txt
├── substack_note_04_signal.txt
└── substack_note_05_question.txt
```

### Step 3: Distribute (15 Minutes)
1. **LinkedIn** (2 posts): Copy `linkedin_01_weekly_summary.txt` + `linkedin_03_market_signal.txt`
   - Replace `[LINK]` with newsletter URL
   - Post Monday 8am ET, Thursday 10am ET

2. **Substack Notes** (3-5 notes): Copy `substack_note_*.txt`
   - Post to https://substack.com/notes/new
   - Space out: Mon, Tue, Wed, Thu, Fri

3. **Twitter** (1 thread): Copy `twitter_thread_01.txt`
   - Thread via Twitter UI (or use Typefully for scheduling)
   - Post Tuesday 9am ET

4. **Reddit** (1 post): Copy `reddit_post.txt`
   - Post to r/governmentcontracting
   - Wednesday 10am ET (highest engagement time)

**Total time:** 10-15 minutes per week

---

## Automation Opportunities

### Zero-Code (Zapier/Make.com)

**Zap 1: Auto-Reminder**
- Trigger: New post published on Substack RSS
- Action: Send Slack message "Newsletter published! Post 3 Notes + LinkedIn today"

**Zap 2: LinkedIn Auto-Post** (requires LinkedIn Business page)
- Trigger: New post published on Substack RSS
- Action: Post first 3 paragraphs + link to LinkedIn

**Zap 3: New Subscriber → CRM**
- Trigger: New subscriber (via Substack webhook)
- Action: Add to Airtable with referral source

### Low-Code (Custom Scripts)

**Option A: Scheduled Social Posting**
```bash
# Add to crontab for Monday 8am
0 8 * * 1 cd ~/Personal/govcon-intel && python3 marketing/auto_post_linkedin.py
```

**Option B: Notion/Airtable Integration**
- Auto-populate content calendar in Notion
- Schedule posts via Buffer/Hootsuite API

---

## Growth Metrics to Track

### Week 1 Baseline
- [ ] Open rate: ___%
- [ ] Click rate: ___%
- [ ] Subscriber count: ___
- [ ] Free → Paid conversion: ___%

### Monthly Growth Targets
- [ ] +50 free subscribers/month (via Notes + LinkedIn)
- [ ] +10 paid subscribers/month (via paywall optimization)
- [ ] 5 cross-recommendations secured (outreach to adjacent publications)
- [ ] 100 LinkedIn followers (organic posting)

### Track in Substack Dashboard
- Dashboard → Stats → Overview (subscribers, open rate)
- Dashboard → Stats → Referrers (where subscribers come from)
- Dashboard → Stats → Posts (which content performs best)

---

## Priority Roadmap: Next 90 Days

### Month 1: Foundation
- [x] Build auto-content generator ✅
- [x] Document growth playbook ✅
- [ ] Optimize Substack SEO (publication description, custom domain)
- [ ] Set up referral program (3/10/25 referral milestones)
- [ ] Post 3-5 Notes per week manually
- [ ] Test LinkedIn cross-posting (2x/week)

### Month 2: Distribution
- [ ] Outreach to 10 adjacent publications (cross-recommendation pitches)
- [ ] Create 1 lead magnet (Recompete Calendar spreadsheet)
- [ ] Launch Reddit seeding (2-3 posts/month)
- [ ] Set up Zapier automation (Slack reminders)
- [ ] A/B test subject lines (data-first vs question hooks)

### Month 3: Scale
- [ ] Test Substack Boost ($500 budget, measure CAC)
- [ ] Launch paid subscriber onboarding sequence
- [ ] A/B test paywall placement (after section 3 vs section 5)
- [ ] Add LinkedIn auto-posting (if budget allows)
- [ ] Guest post on 2 GovCon blogs (backlinks for SEO)

---

## Files Reference

| File | Purpose | Usage |
|------|---------|-------|
| `auto-growth.md` | Strategy guide | Read once, reference as needed |
| `weekly-auto-content.py` | Content generator | Run weekly after pipeline |
| `post_note.py` | Notes API demo | Educational only (don't use in prod) |
| `AUTOMATION-SETUP.md` | This file | Setup + workflow guide |
| `output/social/` | Generated content | Copy-paste to platforms |

---

## FAQ

**Q: Why not automate everything with the API?**
A: Substack has no official API for Notes. Reverse-engineered endpoints are risky (TOS violation, account suspension). Manual posting takes 5 min/week — not worth the risk.

**Q: Can I use a social media scheduler like Buffer?**
A: Yes for Twitter/LinkedIn. Not for Substack Notes (no API support in Buffer/Hootsuite).

**Q: How do I get my substack.sid cookie?**
A: Don't. It's used for `post_note.py` demo only. For production, post manually via UI.

**Q: What if the content generator produces bad copy?**
A: Edit before posting. The script generates data-driven first drafts. Add your voice/insights before publishing.

**Q: How do I track which platform drives the most subscribers?**
A: Substack Dashboard → Stats → Referrers. Use UTM parameters in links (e.g., `?utm_source=linkedin&utm_medium=post1`).

---

## Next Steps

1. **Run the content generator** → Review output → Edit for voice
2. **Post 3 Notes + 2 LinkedIn posts this week** → Measure engagement
3. **Read `auto-growth.md` sections 1-3** → Optimize publication SEO
4. **Set up referral program** → Substack Dashboard → Settings → Referrals
5. **Outreach to 3 adjacent publications** → Pitch cross-recommendation

**Goal:** 500 free subscribers + 50 paid subscribers by Month 3 (without paid ads).
