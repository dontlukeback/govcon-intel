# Beehiiv Setup Guide -- GovCon Weekly Intelligence

Step-by-step instructions for setting up Beehiiv as the newsletter platform and connecting it to the landing page.

---

## 1. Account Setup

### Create Your Account

1. Go to [beehiiv.com](https://www.beehiiv.com)
2. Click **Get Started** (top-right corner)
3. Select the **Launch** plan (free tier -- 2,500 subscribers, unlimited sends)
4. Sign up with email or Google
5. Confirm your email address

### Configure Your Publication

1. After signup, you land on the onboarding wizard
2. **Publication name:** `GovCon Weekly Intelligence`
3. **Publication URL slug:** `govcon-weekly-intelligence` (auto-generated, leave as-is)
4. **Category:** Select **Business** > **Industry**
5. Complete the onboarding wizard (skip any optional steps for now)

### Configure Sender Settings

1. Click **Settings** in the left sidebar
2. Click **Publication Details** (under General)
3. Fill in:
   - **Publication name:** `GovCon Weekly Intelligence`
   - **Publication description:** `AI-powered weekly intelligence on federal contract recompetes, new awards, and competitor moves. Built for GovCon BD teams who want to stop missing opportunities and stop overpaying for stale intel.`
   - **Logo:** Upload the GC logo (gold square with "GC" text) if you have one exported, or skip for now
4. Click **Save**
5. Click **Sending** in the left sidebar (under Settings)
6. Configure:
   - **Default sender name:** `Luke @ GovCon Weekly Intelligence`
   - **Default from email:** Use your Beehiiv-provided address for now (e.g., `luke@govcon-weekly-intelligence.beehiiv.com`). You can connect a custom domain later (see Section 7)
   - **Default reply-to email:** `govconweekly@gmail.com`
7. Click **Save**

---

## 2. Get the Embed Code

### Navigate to the Embed Settings

1. Click **Grow** in the left sidebar
2. Click **Subscription Forms**
3. You will see the default subscription form. Click on it to edit, or click **Create New Form** if you want a dedicated one for the landing page
4. In the form editor, you can customize the form appearance (see next section)
5. Click the **Embed** tab at the top of the form editor

### Choose Embed Type

Beehiiv offers three embed types. Use **Inline Embed** (not popup or slide-in):

1. Select **Inline** as the embed type
2. You will see a code snippet that looks like this:

```html
<iframe src="https://embeds.beehiiv.com/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  data-test-id="beehiiv-embed"
  width="100%"
  height="320"
  frameborder="0"
  scrolling="no"
  style="border-radius: 4px; border: 2px solid #e5e7eb; margin: 0; background-color: transparent;">
</iframe>
```

3. Copy this entire snippet

### Customize Colors to Match Navy + Gold Theme

1. While still in the form editor, click the **Design** tab
2. Set the following colors to match the landing page CSS variables:
   - **Background color:** `transparent` (or `#0A1628` if transparent is not an option -- this is `--navy`)
   - **Text color:** `#FFFFFF` (white)
   - **Input background:** `rgba(255,255,255,0.08)` -- if only hex is supported, use `#1B2A40` (a close approximation)
   - **Input text color:** `#FFFFFF`
   - **Input border color:** `#2A3F5F` (subtle light border on dark)
   - **Button background:** `#C5A44E` (this is `--gold`)
   - **Button text color:** `#0A1628` (this is `--navy`)
   - **Button text:** `Subscribe Free`
   - **Placeholder text:** `Enter your work email`
3. Under **Layout**, set:
   - **Alignment:** Center
   - **Show name field:** Off (email only -- reduces friction)
4. Click **Save**
5. Go back to the **Embed** tab and re-copy the embed code (it updates with your design changes)

---

## 3. Add to Landing Page

### Replace the Hero Placeholder

1. Open `/Users/luke/Personal/govcon-intel/landing/index.html` in your editor

2. Find the first placeholder (around line 844-852):

```html
<!-- BEEHIIV EMBED CODE HERE -->
<div class="hero-form-placeholder" style="max-width: 480px; margin: 0 auto 20px;">
    <!-- Replace this entire div with your Beehiiv embed code. -->
    <!-- The form below is a placeholder that mirrors Beehiiv styling. -->
    <form class="hero-form" action="#" method="post">
        <input type="email" placeholder="Enter your work email" required>
        <button type="submit">Subscribe Free</button>
    </form>
</div>
```

3. Replace the **entire** `<div class="hero-form-placeholder" ...>...</div>` block (including the div itself) with:

```html
<!-- BEEHIIV EMBED -->
<div style="max-width: 480px; margin: 0 auto 20px;">
    <iframe src="https://embeds.beehiiv.com/YOUR-EMBED-ID-HERE"
        data-test-id="beehiiv-embed"
        width="100%"
        height="52"
        frameborder="0"
        scrolling="no"
        style="border-radius: 6px; border: none; margin: 0; background-color: transparent;">
    </iframe>
</div>
```

**Note:** Set `height="52"` for an email-only form (no name field). If Beehiiv renders taller, increase to `80` or `100`. You will fine-tune this in the testing step.

### Replace the Bottom CTA Placeholder

4. Find the second placeholder (around line 1074-1081):

```html
<!-- BEEHIIV EMBED CODE HERE -->
<div class="hero-form-placeholder">
    <!-- Replace this entire div with your Beehiiv embed code. -->
    <form class="hero-form" action="#" method="post">
        <input type="email" placeholder="Enter your work email" required>
        <button type="submit">Subscribe Free</button>
    </form>
</div>
```

5. Replace the **entire** `<div class="hero-form-placeholder">...</div>` block with the same iframe embed:

```html
<!-- BEEHIIV EMBED -->
<div style="max-width: 480px; margin: 0 auto;">
    <iframe src="https://embeds.beehiiv.com/YOUR-EMBED-ID-HERE"
        data-test-id="beehiiv-embed"
        width="100%"
        height="52"
        frameborder="0"
        scrolling="no"
        style="border-radius: 6px; border: none; margin: 0; background-color: transparent;">
    </iframe>
</div>
```

### Test Locally

6. Open the file in a browser:

```bash
open /Users/luke/Personal/govcon-intel/landing/index.html
```

7. Verify:
   - [ ] The hero embed renders with an email field and "Subscribe Free" button
   - [ ] The bottom CTA embed renders identically
   - [ ] Colors match the surrounding page (gold button on navy background)
   - [ ] The iframe has no scrollbars or extra whitespace (adjust `height` if needed)
   - [ ] Submit a test email address -- it should appear in your Beehiiv subscriber list
   - [ ] Resize the browser to mobile width (375px) -- the form should stack properly
   - [ ] Check that the `hero-trust` text ("Free weekly brief. No credit card required...") still displays below the hero embed

### Troubleshooting Common Issues

- **Iframe too tall / too short:** Adjust the `height` attribute. Start at `52`, try `80`, `100`, or `120` until it fits without scrollbars.
- **White background flashing inside iframe:** Add `background-color: transparent;` to the iframe style (already included above).
- **Form not submitting:** Make sure you are not blocking third-party cookies or iframes in your browser. Beehiiv embeds require cookies.
- **Double scrollbar:** Make sure `scrolling="no"` is set and `overflow: hidden` is on the iframe if needed.

---

## 4. Import the First Newsletter

### Create a New Post

1. In Beehiiv, click **Posts** in the left sidebar
2. Click **Create Post** (top-right)
3. Set:
   - **Subject line:** `GovCon Weekly Intel Brief -- Week of Mar 16-22, 2026`
   - **Preview text:** `4 recompetes worth $962M. DISA, Army, VA moves. What it means for your pipeline.`
   - **Audience:** All subscribers

### Paste the HTML Report

4. In the post editor, click the **</>** icon in the toolbar (or press `Cmd+Shift+E` on Mac) to switch to **HTML mode**
5. Open the report file and copy its contents:

```bash
cat /Users/luke/Personal/govcon-intel/output/report_2026-03-18.html | pbcopy
```

6. Paste the HTML into the Beehiiv HTML editor
7. Switch back to **Visual mode** to verify it rendered correctly

### Important: Clean Up the HTML

Beehiiv's editor may strip or reformat some HTML. Check for:

- **Inline styles:** Beehiiv handles most CSS inline. If your report uses `<style>` blocks, the styles may be lost. Convert any `<style>` CSS to inline styles before pasting.
- **Images:** If the report references local image paths, upload them to Beehiiv's media library and update the `src` attributes.
- **Tables:** Beehiiv supports HTML tables, but complex layouts may need simplification.

### Preview and Test

8. Click **Preview** (top-right of the editor)
9. Click **Desktop** and **Mobile** toggle to check both layouts
10. Click **Send Test Email** (under the Preview dropdown)
11. Enter your personal email address
12. Send the test

### QA Checklist

After receiving the test email, verify:

- [ ] Subject line and preview text display correctly in inbox
- [ ] Report renders properly in Gmail (open in browser + Gmail app)
- [ ] Report renders properly in Outlook (if accessible)
- [ ] All links work (SAM.gov links, FPDS links, etc.)
- [ ] No broken images
- [ ] Text is readable on mobile (no horizontal scrolling)
- [ ] The gold/navy color scheme is intact
- [ ] AI Analysis sections are clearly distinguished
- [ ] Footer contains Beehiiv unsubscribe link (auto-added)
- [ ] "From" name shows as "Luke @ GovCon Weekly Intelligence"
- [ ] Reply-to goes to `govconweekly@gmail.com`

### Schedule or Send

13. Once QA passes, either:
    - Click **Schedule** and pick a date/time (recommended: Monday 7:00 AM ET)
    - Click **Send Now** if you are ready to go live immediately
    - Click **Save as Draft** if you are not ready yet

---

## 5. Configure the Welcome Email

### Set Up the Automation

1. Click **Automations** in the left sidebar
2. Click **Create Automation** (top-right)
3. Name it: `Welcome Sequence`
4. **Trigger:** Select **New Subscriber**
   - Filter: **All subscribers** (or filter by specific tags if you segment later)

### Add Email 1: Welcome + First Report

5. Click **Add Step** > **Send Email**
6. Set **Delay:** `0 minutes` (send immediately on subscribe)
7. Click into the email to edit it:
   - **Subject:** `Your first GovCon intelligence report (+ what to expect)`
   - **Preview text:** `Here's what you missed this week in federal contracting`
8. Switch to the editor body. Because this is a plain-text style email, type or paste the following (from `marketing/email-welcome-sequence.md`, Email 1 body):

```
Hey {first_name},

Welcome to GovCon Weekly Intelligence.

You just signed up for the free tier, which means you'll get a monthly market overview. But I want to show you what the weekly Pro tier looks like, so here's this week's full report:

[LINK TO LATEST REPORT]

What's inside:
- 4 recompetes worth $962M (with days-to-expiration and incumbent analysis)
- Competitor tracking: who won what this week
- AI analysis: what these moves mean for your pipeline
- Action items: specific things you should do by Friday

This lands in Pro subscribers' inboxes every Monday @ 7am.

---

A few things to know:

Free tier: You'll get a monthly overview (next one comes April 15)
Pro tier: $149/mo for weekly reports + NAICS filtering + competitor tracking
Enterprise tier: $399/mo for unlimited NAICS codes + team access + API

No hard sell. Read the sample report. If it's useful, upgrade. If not, the monthly overview is still free.

---

Quick question: What NAICS codes do you bid on?

Reply to this email and I'll send you a custom filter of this week's report showing only contracts in your codes.

(This takes me 2 minutes and helps me understand what people actually need.)

Thanks for subscribing,
Luke

P.S. -- Want these reports every week? Upgrade to Pro: [LINK]
```

**Note on merge tags:** Beehiiv uses `{first_name}` as a merge tag. If the subscriber did not provide a first name (email-only form), it will be blank. To add a fallback, use `{first_name|default:"there"}` so it renders as "Hey there," when the name is unknown.

9. Replace `[LINK TO LATEST REPORT]` and `[LINK]` with actual URLs once you have published your first post. You can get the post's web URL from **Posts > Published > click the post > Copy Link**.
10. Click **Save**

### Add Email 2: Use Case (Day 3)

11. Click **Add Step** > **Delay** > Set to **3 days**
12. Click **Add Step** > **Send Email**
13. Paste the Email 2 content from `marketing/email-welcome-sequence.md`
    - **Subject:** `How a Reston firm caught a $12M recompete 3 months early`
    - **Preview text:** `Real story from a GovCon Weekly subscriber`
14. Click **Save**

### Add Email 3: Upgrade Offer (Day 7)

15. Click **Add Step** > **Delay** > Set to **4 days** (Day 3 + 4 = Day 7 total)
16. Click **Add Step** > **Send Email**
17. Paste the Email 3 content from `marketing/email-welcome-sequence.md`
    - **Subject:** `3 questions about upgrading to Pro (answered)`
    - **Preview text:** `Pro tier vs. Free tier -- what's the difference?`
18. Click **Save**

### Add Bonus Email: Re-engagement (Day 30)

19. Click **Add Step** > **Delay** > Set to **23 days** (Day 7 + 23 = Day 30 total)
20. Click **Add Step** > **Conditional Split**
    - Condition: **Has not opened** any email in the last 14 days
    - If **true** (inactive): Add a **Send Email** step with the Bonus re-engagement email from `marketing/email-welcome-sequence.md`
    - If **false** (active): End the automation (no action)
21. Click **Save**

### Activate the Automation

22. Toggle the automation to **Active** (top-right of the automation editor)
23. Test by subscribing with a fresh test email address
24. Verify Email 1 arrives within a few minutes

---

## 6. Configure the Referral Program

### Enable Referral Program

1. Click **Grow** in the left sidebar
2. Click **Referral Program**
3. Toggle **Enable Referral Program** to ON

### Configure Milestones

Set up milestone rewards relevant to the GovCon audience:

| Referrals | Reward | Why It Works |
|-----------|--------|--------------|
| **1 referral** | Access to the archived report library (all past weekly briefs) | Low bar, immediate value |
| **3 referrals** | Free month of Pro tier | Lets them experience the upgrade without paying |
| **5 referrals** | Custom NAICS filter report (personalized one-time report) | High-perceived-value, low cost to deliver |
| **10 referrals** | 30-minute strategy call with Luke (pipeline review) | Personal touch, builds relationship |
| **25 referrals** | 3 months of Pro tier free | Big reward for power referrers |

### Set Up Each Milestone

4. Click **Add Milestone**
5. For each milestone:
   - **Number of referrals:** Enter the number from the table above
   - **Reward type:** Select **Custom** (you will fulfill manually or via a tag-based automation)
   - **Reward description:** Enter the reward text (e.g., "Access to archived report library")
   - **Reward email:** Write a short congratulations email explaining how to claim the reward
6. Click **Save** after each milestone

### Configure the Referral Widget

7. Under **Referral Program > Widget**, customize:
   - **Headline:** `Share GovCon Weekly Intelligence`
   - **Description:** `Know a BD lead or capture manager who'd find this useful? Share your unique link.`
   - **CTA text:** `Copy Referral Link`
8. The referral widget auto-appears in every email footer. You can also embed it on a custom "thank you" page.

### How It Works for Subscribers

- Every subscriber gets a unique referral link (shown in email footer and on their subscriber profile page)
- When someone subscribes through that link, the referrer gets credit
- Beehiiv tracks referrals automatically and triggers milestone rewards
- You can view referral leaderboard at **Grow > Referral Program > Leaderboard**

---

## 7. DNS / Custom Domain (Optional)

Connecting a custom domain means emails come from `luke@govconweekly.com` instead of `luke@govcon-weekly-intelligence.beehiiv.com`, and your newsletter archive lives at `govconweekly.com/newsletter` (or a subdomain like `intel.govconweekly.com`).

### Custom Sending Domain (Email Authentication)

This makes your emails come from `@govconweekly.com` and significantly improves deliverability.

1. Click **Settings** in the left sidebar
2. Click **Sending** (under General)
3. Click **Custom Sending Domain**
4. Enter your domain: `govconweekly.com`
5. Beehiiv will provide three DNS records to add at your registrar (Namecheap, Cloudflare, GoDaddy, etc.):

| Type | Name/Host | Value | Purpose |
|------|-----------|-------|---------|
| **TXT** | `@` or `govconweekly.com` | `v=spf1 include:beehiiv.com ~all` | SPF -- authorizes Beehiiv to send on your behalf |
| **CNAME** | `em._domainkey` | `(provided by Beehiiv)` | DKIM -- email signature verification |
| **CNAME** | `return` | `(provided by Beehiiv)` | Return-path for bounce handling |

6. Log in to your domain registrar
7. Go to **DNS settings** for `govconweekly.com`
8. Add each record exactly as Beehiiv specifies (copy-paste the values)
9. Go back to Beehiiv and click **Verify**
10. DNS propagation takes 15 minutes to 48 hours. If verification fails, wait and try again.
11. Once verified, update your **Default from email** (Settings > Sending) to `luke@govconweekly.com`

### Custom Web Domain (Newsletter Archive)

This makes your Beehiiv-hosted newsletter archive accessible at a custom URL.

1. Click **Settings** in the left sidebar
2. Click **Website** (under General)
3. Click **Custom Domain**
4. Enter your desired domain or subdomain:
   - Option A: `govconweekly.com` (if the landing page is hosted elsewhere, like Netlify, this creates a conflict -- use a subdomain instead)
   - Option B (recommended): `newsletter.govconweekly.com` (keeps the landing page and newsletter separate)
5. Add the DNS record at your registrar:

| Type | Name/Host | Value |
|------|-----------|-------|
| **CNAME** | `newsletter` | `custom.beehiiv.com` |

6. Go back to Beehiiv and click **Verify**
7. SSL is provisioned automatically after verification

### Recommended Domain Architecture

| URL | Hosted On | Purpose |
|-----|-----------|---------|
| `govconweekly.com` | Netlify or Vercel (see DEPLOY.md) | Landing page (`index.html`) |
| `newsletter.govconweekly.com` | Beehiiv | Newsletter archive + subscriber portal |
| Emails from `luke@govconweekly.com` | Beehiiv (custom sending domain) | Newsletter delivery |

This keeps the landing page on a fast static host while letting Beehiiv handle email delivery and the newsletter archive.

---

## Quick Reference: File Locations

| File | Purpose |
|------|---------|
| `landing/index.html` | Landing page with two Beehiiv embed placeholders (lines 844 and 1074) |
| `marketing/email-welcome-sequence.md` | Full welcome email copy (4 emails + reply templates) |
| `output/report_2026-03-18.html` | First newsletter content to import into Beehiiv |
| `DEPLOY.md` | Landing page deployment instructions (Netlify / Vercel) |
