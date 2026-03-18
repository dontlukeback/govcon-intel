# GovCon Weekly Intelligence -- Newsletter Design Guide

**Based on:** Research across Litmus, Mailchimp, Campaign Monitor, Smashing Magazine, Email on Acid, Can I Email, Good Email Code, Really Good Emails, and analysis of Morning Brew, CB Insights, Benedict Evans, Stratechery, and intelligence brief formats.

**Current template reviewed:** `output/report_2026-03-18.html`

---

## Executive Assessment of Current Template

The existing template is already strong. It uses table-based layout, inline CSS, proper preheader text, a clean color system, and good visual hierarchy. The recommendations below are refinements, not a rebuild.

**What's working well:**
- Table-based layout (correct for email)
- Inline CSS throughout (Gmail compatible)
- Navy/gold brand palette conveys authority
- Color-coded left borders for urgency tiers (red/amber/green/blue) -- excellent
- Stat banner at the top (four KPIs) -- readers love this
- "Signal of the Week" callout box -- strong pattern

**What needs improvement:**
- Missing dark mode support (meta tags + color-scheme)
- Missing Outlook VML conditional comments for DPI scaling
- No accessibility attributes (role, aria-label, lang duplication)
- Font stack could be more resilient
- Mobile padding needs tightening (32px side padding is generous on 320px screens)
- CTA button is not "bulletproof" (will break in Outlook)
- No section dividers/numbering -- readers lose their place in long emails
- Missing "table of contents" jump links at top
- Preheader spacing hack missing (inbox may pull body content)

---

## 1. Color Palette

### Primary Colors

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| **Navy (Primary)** | Deep navy | `#0F172A` | Header, footer, dark panels, Market Pulse section |
| **Gold (Accent)** | Warm gold | `#C9A227` | Brand accent, gold bar separator, trending indicators, labels |
| **White** | Clean white | `#FFFFFF` | Main content background |
| **Light gray** | Page background | `#F1F5F9` | Email body background (outside content area) |

### Semantic Colors (Urgency/Status System)

| Status | Color | Hex | When to Use |
|--------|-------|-----|-------------|
| **Urgent/Action Required** | Red | `#DC2626` | Recompetes <120 days, deadline alerts |
| **Watch** | Amber | `#D97706` | Recompetes 120-180 days, caution signals |
| **Positive/Awarded** | Green | `#16A34A` | New awards, positive trends, growth indicators |
| **Informational** | Blue | `#2563EB` | Option exercises, neutral data, links |
| **Muted** | Slate | `#64748B` | Secondary text, metadata, dates |

### Color Psychology Rationale

- **Navy blue** = trust, authority, stability, expertise. The #1 color used by defense contractors, financial services, and intelligence agencies. Conveys "we take this seriously." Used by Deloitte, McKinsey, Gartner, Jane's Defence.
- **Gold** = premium, exclusive, intelligence. Distinguishes from generic blue-and-white B2B emails. Signals "this is worth paying for." Used by Bloomberg, The Information, premium financial newsletters.
- **Red for urgency** = universally understood. The "days remaining" badges in red create genuine urgency without being spammy.
- **White space** = professionalism. Dense-but-clean signals "analyst report" not "marketing email."

### Dark Mode Considerations

Add to `<head>`:
```html
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<style>
  :root { color-scheme: light dark; }
  @media (prefers-color-scheme: dark) {
    .body-bg { background-color: #1a1a2e !important; }
    .content-bg { background-color: #16213e !important; }
    .text-primary { color: #e2e8f0 !important; }
    .text-secondary { color: #94a3b8 !important; }
    .gold-accent { color: #d4af37 !important; }
  }
</style>
```

**Client support (2025-2026):** Apple Mail, Gmail (all platforms), Outlook.com, Outlook iOS/Android, Yahoo, Samsung Email all support `color-scheme`. Windows Outlook desktop (2003-2019) does NOT -- it ignores dark mode entirely (which is fine; it renders the light version).

**Practical guidance:** Design for light mode first. Ensure logos/images have transparent backgrounds OR add a white padding border so they don't float on dark backgrounds. Use `background-color` on cells rather than relying on inherited white.

---

## 2. Typography

### Font Stack

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

This is already in the template and is the correct choice. It renders:
- **Apple devices:** San Francisco (clean, modern)
- **Windows:** Segoe UI (Microsoft's system font, looks professional)
- **Android:** Roboto (Google's system font)
- **Fallback:** Helvetica Neue > Arial

**Do NOT use web fonts** (Google Fonts, etc.) in this newsletter. They add load time, fail in Outlook, and the system font stack already looks professional across all clients.

### Type Scale

| Element | Size | Weight | Line Height | Letter Spacing | Current Status |
|---------|------|--------|-------------|----------------|----------------|
| **Masthead title** | 24px | 800 (extrabold) | 1.2 | -0.5px | Good as-is |
| **Section headers** | 18px | 800 | 1.3 | 0 | Good as-is |
| **Card titles** | 16px | 700 | 1.3 | 0 | Good as-is |
| **Body text** | 14px | 400 | 1.65 | 0 | Good as-is |
| **Metadata/labels** | 13px | 400-600 | 1.5 | 0 | Good as-is |
| **Category labels** | 11px | 700 | 1.2 | 1-2px | Uppercase, good |
| **Small/legal** | 12px | 400 | 1.6 | 0 | Good as-is |
| **KPI numbers** | 20-36px | 800-900 | 1.1 | -0.5 to -1px | Good as-is |

**Key principles:**
- Never go below 13px for body content (accessibility + mobile readability)
- Use weight contrast, not size contrast, for hierarchy within a section
- Negative letter-spacing on large numbers makes them feel "denser" and more authoritative
- Uppercase + wide letter-spacing on labels creates a clear visual tier break
- 1.6-1.65 line height for body text is ideal for scanning

### Hierarchy Pattern (from best intelligence newsletters)

The most effective data-heavy newsletters use a **3-tier visual hierarchy**:

1. **Tier 1 -- Scan layer:** Bold headlines, colored badges, large numbers. A reader skimming in 8 seconds gets the key takeaways.
2. **Tier 2 -- Read layer:** Card titles, metadata lines, one-sentence intel callouts. A reader spending 30 seconds per section gets actionable context.
3. **Tier 3 -- Deep layer:** Full analysis paragraphs, background context. Only engaged readers go here.

Your current template does this well with the badge + dollar amount + title + metadata + intel callout pattern. Maintain it.

---

## 3. Layout Structure

### Email Width

- **Max width: 620px** (current, correct)
- This is the sweet spot: wide enough for data tables, narrow enough for mobile
- Industry standard ranges from 580-640px; 600-620 is most common for data-heavy content

### Recommended Section Order

Based on research into Morning Brew, CB Insights, McKinsey briefs, and intelligence report formats:

```
1. HEADER (masthead + date)
2. GOLD SEPARATOR BAR (3px -- brand marker)
3. SIGNAL OF THE WEEK (hero callout)
4. KPI DASHBOARD (4-stat banner)
5. TABLE OF CONTENTS (new -- see below)
6. RECOMPETE ALERTS (highest urgency first)
7. NEW AWARDS
8. OPTION EXERCISES
9. FUNDING ACTIONS (table format)
10. MARKET PULSE (dark panel with trends)
11. UPGRADE CTA (for free tier) or FEEDBACK (for Pro)
12. FOOTER
```

### Add: Table of Contents

For a 3,000-5,000 word newsletter, readers need a map. Add after the KPI dashboard:

```html
<tr><td style="background:#FFFFFF;padding:0 32px 24px;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F8FAFC;border-radius:8px;">
  <tr><td style="padding:16px 20px;">
    <div style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">In This Brief</div>
    <div style="font-size:13px;line-height:2;color:#1E293B;">
      <strong style="color:#DC2626;">01</strong> Recompete Alerts (4) -- $961M at risk<br>
      <strong style="color:#16A34A;">02</strong> New Awards (4) -- $1.9B awarded<br>
      <strong style="color:#2563EB;">03</strong> Option Exercises (3) -- $261M renewed<br>
      <strong style="color:#64748B;">04</strong> Funding Actions (4) -- $2.7B in mods<br>
      <strong style="color:#C9A227;">05</strong> Market Pulse -- NAICS trends + agency spend
    </div>
  </td></tr>
  </table>
</td></tr>
```

**Why this works:** Morning Brew and CB Insights both use a "what's inside" block. It reduces perceived length, lets readers jump to their section, and increases time-on-email because readers commit to specific sections rather than abandoning a wall of content.

### Add: Section Numbering

Add a numbered label before each section header:

```html
<div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">01 / Recompete Alerts</div>
<div style="font-size:18px;font-weight:800;color:#1E293B;">Recompete Alerts</div>
```

This creates a wayfinding system. The reader always knows where they are in the report. Gartner and McKinsey briefs do this consistently.

### Mobile Responsiveness

The current template uses fixed 32px side padding. On a 320px-wide phone screen, that leaves only 256px for content. Recommendations:

```html
<!-- Add to <style> in head -->
<style>
  @media only screen and (max-width: 620px) {
    .content-padding { padding-left: 16px !important; padding-right: 16px !important; }
    .stat-cell { display: block !important; width: 50% !important; }
    .hide-mobile { display: none !important; }
    .stack-mobile { display: block !important; width: 100% !important; }
    .mobile-text-center { text-align: center !important; }
  }
</style>
```

**Key mobile patterns:**
- 4-column stat banner should become 2x2 grid on mobile
- Side padding should reduce from 32px to 16px
- Dollar amounts can reduce from 22px to 18px
- Data tables should stack or scroll horizontally

**Hybrid/spongy approach (no media query fallback):**
For clients that strip `<style>` blocks (older Gmail), use the fluid hybrid pattern:
```html
<div style="display:inline-block; width:100%; max-width:300px; vertical-align:top;">
  <!-- Column content -->
</div>
```
This lets columns stack naturally on narrow viewports without requiring media queries.

---

## 4. Section Design Patterns

### Pattern 1: Hero Callout (Signal of the Week)

Current implementation is excellent. The left-border + warm background + bold headline pattern is used by The Information, Stratechery (paid section callouts), and intelligence analyst reports.

**One enhancement:** Add a small icon or emoji before "Signal of the Week" to make it pop:

```
SIGNAL OF THE WEEK  (keep as uppercase label)
```

Or use a simple unicode character: `\u25CF` (filled circle) or `\u25B6` (play triangle) before the label for visual anchor.

### Pattern 2: Urgency Cards (Recompetes)

The color-coded left border + badge + dollar amount pattern is the strongest element of the current design. It mirrors how Bloomberg Terminal alerts work.

**Refinements:**
- Add a thin top border too (creates a more complete "card" feel)
- Consider adding a small "action" link at the bottom of each card: `Set SAM.gov Alert >>` as a text link (not a button)
- Group by urgency tier with a small divider: "URGENT" cards first, then "WATCH" cards

### Pattern 3: Data Tables (Funding Actions)

The current alternating-row table is clean. Enhancements:

- Add hover-state color for web view: `tr:hover { background: #f0f4ff; }`
- Right-align all dollar amounts (already done, good)
- Consider adding a small sparkline or trend arrow next to amounts when showing change over time
- Keep tables to 3-4 columns max for mobile compatibility

### Pattern 4: Dark Panel (Market Pulse)

The navy dark panel at the bottom is a strong visual break. This is the pattern CB Insights uses for their data callouts.

**Enhancements:**
- Add thin gold top border to the dark panel (brand consistency)
- Consider breaking the "Top Agencies" and "Trending NAICS" into two side-by-side columns on desktop, stacking on mobile

### Pattern 5: CTA Block

The current CTA block works but the button is not "bulletproof" for Outlook. Outlook doesn't support `border-radius` on `<a>` tags or padding-based buttons reliably.

**Bulletproof button pattern:**
```html
<!--[if mso]>
<v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="#" style="height:48px;v-text-anchor:middle;width:240px;" arcsize="13%" strokecolor="#C9A227" fillcolor="#C9A227">
<w:anchorlock/>
<center style="color:#0F172A;font-family:sans-serif;font-size:15px;font-weight:bold;">Start Free Trial</center>
</v:roundrect>
<![endif]-->
<!--[if !mso]><!-->
<a href="#" style="display:inline-block;background:#C9A227;color:#0F172A;font-size:15px;font-weight:800;padding:14px 32px;border-radius:6px;text-decoration:none;letter-spacing:0.3px;">Start Free Trial &rarr;</a>
<!--<![endif]-->
```

---

## 5. What Makes Readers Open and Read Weekly

### Subject Lines (Research-Backed)

Based on B2B newsletter benchmarks (industry avg open rate: 30%, target: 35%+):

**Patterns that work for data/intelligence newsletters:**

1. **Specific number + urgency:** `$890M in recompetes hitting in 60 days`
2. **Trend + "why":** `DoD cyber spend up 34% -- here's where it's going`
3. **Curiosity gap:** `The DISA contract nobody's tracking (yet)`
4. **Listicle:** `4 recompetes you need on your board this week`
5. **News angle:** `Scale AI just beat Palantir for NGA's biggest AI award`

**Patterns that DON'T work:**
- Generic dates: `GovCon Weekly: March 16-22` (no reason to open)
- All-caps urgency: `BREAKING: DOD AWARDS $1.2B` (spam filter bait)
- Vague value: `Your weekly government contracting update` (boring)

**Best practice:** A/B test subject lines. Send 20% of list two variants, wait 2 hours, send winning variant to remaining 80%.

### Preheader Text

The current preheader (`DoD Cyber Budget Surge: $2.1B in New Obligations This Quarter`) is good -- it extends the subject line rather than repeating it.

**Add the spacing hack** to prevent inbox clients from pulling body content:
```html
<div style="display:none;max-height:0;overflow:hidden;">
  DoD Cyber Budget Surge: $2.1B in New Obligations This Quarter
  &#8199;&#65279;&#847;&#8199;&#65279;&#847;&#8199;&#65279;&#847;
  <!-- repeat 50-100 times -->
</div>
```

### Reading Engagement (What Keeps Them Scrolling)

Research from Litmus: average email engagement is 8.97 seconds. For a 10-15 minute newsletter, you need structural hooks:

1. **Front-load value:** The KPI dashboard + Signal of the Week in the first scroll gives readers an immediate payoff. They've already gotten value before deciding to keep reading.

2. **Visual rhythm:** Alternate between card-style sections and table-style sections. Never have two identical layouts back-to-back. The current template does this well (cards > cards > compact cards > table > dark panel).

3. **Scannable intel boxes:** The colored background "Intel:" callouts inside each card are the #1 thing that keeps readers going. They can skip the metadata and just read the intel lines. This is the CB Insights model -- dense but scannable.

4. **Progressive disclosure:** Free tier shows 3 recompetes; Pro shows 6. The paywall creates a natural "there's more" incentive. Benedict Evans and Stratechery use this effectively.

5. **Consistent structure:** Readers develop a muscle memory. They know "scroll past the awards, I want the Market Pulse section." Consistency = habit = retention.

6. **One actionable item per section:** The PRD says "prescriptive, not descriptive." Every card should end with a specific action. This is what separates intelligence from information.

### Send Timing

- **Monday 7:00 AM EST** (current, correct for BD teams)
- BD managers check email first thing Monday to plan their week
- A/B test Tuesday 7 AM as an alternative (some B2B newsletters perform better Tuesday)
- Avoid Friday (low engagement) and Wednesday (meeting-heavy day)

---

## 6. Technical Email Rendering

### HTML Boilerplate

Add these to the `<head>`:

```html
<!DOCTYPE html>
<html lang="en" dir="ltr" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>GovCon Weekly Intelligence</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:AllowPNG/>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
```

### Client-Specific Notes

| Client | Market Share | Key Issues | Workaround |
|--------|-------------|------------|------------|
| **Apple Mail (macOS/iOS)** | 283/303 features | Near-perfect rendering | None needed |
| **Gmail (web)** | 152/303 features | Strips `<style>` in some contexts, no `background-image` | Inline all CSS, use `background-color` on cells |
| **Outlook (Windows)** | 59/303 features | Uses Word rendering engine. No `border-radius`, limited `padding`, no `max-width` | Use VML for rounded buttons, `<!--[if mso]>` ghost tables for layout |
| **Outlook (Mac)** | 175/303 features | Much better than Windows | Minor issues only |
| **Samsung Email** | 250/300 features | Good support | None needed |

### Universally Safe CSS Properties
- `margin`, `padding`, `border`, `width`, `height`
- `font-family`, `font-size`, `font-weight`, `color`, `text-align`
- `background-color` (NOT `background-image` universally)
- `line-height`, `letter-spacing`
- `text-transform`, `text-decoration`
- `vertical-align`
- `border-collapse`, `border-spacing`

### Properties to Avoid or Use Carefully
- `border-radius` -- Works everywhere EXCEPT Outlook Windows. Use it anyway (progressive enhancement) but don't rely on it for meaning.
- `max-width` -- Not supported in Outlook Windows. Use `<!--[if mso]>` ghost tables to enforce width.
- `flexbox`, `grid` -- Do not use in email. Period.
- `background-image` -- Unreliable. Use solid `background-color` instead.
- `position`, `float` -- Avoid. Use table cells for positioning.
- CSS animations -- Only for progressive enhancement in Apple Mail/iOS.

### Ghost Tables for Outlook

When you need `max-width` behavior (which Outlook ignores):

```html
<!--[if mso]>
<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="620">
<tr><td>
<![endif]-->
<div style="max-width:620px;margin:0 auto;">
  <!-- Content -->
</div>
<!--[if mso]>
</td></tr>
</table>
<![endif]-->
```

### Accessibility

Add to the main content wrapper:
```html
<div role="article" aria-roledescription="email" aria-label="GovCon Weekly Intelligence - Week of March 16-22, 2026" lang="en" dir="ltr" style="font-size:medium;font-size:max(16px,1rem);">
```

Duplicate `lang` attribute on `<html>`, the wrapper `<div>`, and key content sections (email clients strip outer elements unpredictably).

---

## 7. Patterns from Best-in-Class Newsletters

### Morning Brew
- **Lesson:** Numbered sections with a TOC at top. Readers know exactly what's inside before committing.
- **Adopt:** Add TOC block (recommended above). Number your sections.

### CB Insights
- **Lesson:** Data-heavy but scannable. Uses bold callout numbers, colored highlights, and irreverent commentary to keep dense data engaging.
- **Adopt:** Your "Intel:" callout boxes serve this purpose. Consider adding a weekly "number of the week" feature (e.g., `34% -- QoQ increase in DoD cyber spend`).

### Benedict Evans / Stratechery
- **Lesson:** Simple, text-forward design. Minimal images. The content IS the product. Premium feel comes from density of insight, not visual complexity.
- **Adopt:** Your current approach is already close. Don't over-design. The card layout with intel callouts is the right level of visual structure without becoming a marketing email.

### McKinsey / Gartner Briefs
- **Lesson:** Executive summary at top, then structured sections with clear headers. Footer always includes methodology note. Uses "implications" framing (what this means for you).
- **Adopt:** Your "So What" analysis pattern matches this. Consider adding a brief methodology note in footer: "Data: USAspending.gov, FPDS-NG, SAM.gov. AI analysis: Claude 3.5 Sonnet. Human-reviewed."

### The Information
- **Lesson:** Gold/navy premium palette. Paywall placement is strategic -- you get enough free to feel the value, then hit the gate at the "best part."
- **Adopt:** Your free/Pro tier split should gate the analysis (intel callouts), not the raw data. Free tier shows the recompete cards; Pro tier shows the "Intel:" analysis inside them.

### First Round Review
- **Lesson:** Long-form but with pull quotes and highlighted key sentences. Makes 3,000+ word emails feel manageable.
- **Adopt:** Consider bolding one key sentence per section as a "pull quote" equivalent for scanning.

---

## 8. Specific Improvements Checklist

### Must-Do (Before Launch)

- [ ] Add dark mode meta tags and `color-scheme` CSS
- [ ] Add Outlook VML namespace declarations and DPI fix
- [ ] Add `role="article"` and `aria-roledescription="email"` accessibility attributes
- [ ] Add preheader spacing hack (prevent body content bleed)
- [ ] Make CTA button bulletproof with VML fallback
- [ ] Add `role="presentation"` to all layout tables
- [ ] Reduce mobile padding from 32px to 16px via media query
- [ ] Add `lang="en"` to wrapper div (redundancy for client stripping)

### Should-Do (Week 1-2)

- [ ] Add Table of Contents section after KPI dashboard
- [ ] Add section numbering (`01 / Recompete Alerts`)
- [ ] Add ghost tables for Outlook max-width support
- [ ] A/B test subject line patterns
- [ ] Add action links at bottom of each recompete card (`Set SAM.gov Alert >>`)
- [ ] Test rendering in Litmus or Email on Acid across top 10 clients

### Nice-to-Have (Week 3-4)

- [ ] Add a "Number of the Week" feature between Signal of the Week and KPI dashboard
- [ ] Add pull-quote styling for key sentences (bold + left border)
- [ ] Add forward-to-friend tracking link in footer
- [ ] Add "Was this useful?" thumbs up/down at bottom (engagement signal)
- [ ] Add thin gold top border to Market Pulse dark panel
- [ ] Explore print-friendly CSS (`@media print` block)

---

## 9. Anti-Patterns to Avoid

1. **Don't add images.** The PRD says "no external images except header logo" -- this is correct. Images trigger spam filters, fail to load behind VPNs (your audience is GovCon/defense), and add load time. Text + structure is the right choice.

2. **Don't use gradient backgrounds.** They don't render in Outlook and add visual noise. Flat colors convey professionalism.

3. **Don't center-align body text.** Left-align everything except footer and CTA blocks. Centered body text is harder to read and looks like a marketing email.

4. **Don't use more than 2 fonts.** System font stack for everything. Weight and size create hierarchy, not font variety.

5. **Don't make the email wider than 620px.** Data tables tempt you to go wider. Resist. Use horizontal scrolling or condensed formatting for wide data.

6. **Don't use emoji in subject lines for this audience.** GovCon BD professionals expect formality. Emoji reduces perceived authority. (Exception: internal emoji like the fire emoji in the CB Insights style, used sparingly inside the body for personality, but even this is risky for a defense/intelligence audience.)

7. **Don't gate the raw data.** Gate the analysis. Free tier readers should see what recompetes exist; they pay for the "Intel:" insights and action items. This is the drug dealer model -- the data is the free sample, the insight is what you pay for.

---

## 10. Summary: The GovCon Newsletter Design Formula

```
AUTHORITY (navy + gold + dense data)
+ URGENCY (red badges + countdown days + action items)
+ STRUCTURE (numbered sections + TOC + consistent card pattern)
+ SCANNABILITY (3-tier hierarchy: skim > read > deep)
+ TECHNICAL SOUNDNESS (table layout + inline CSS + Outlook fallbacks + dark mode)
= A newsletter BD managers print out for Monday morning team meetings
```

The goal is not "beautiful email." The goal is **the email that BD managers forward to their CEO with the note "we need to subscribe to this."** Every design decision should serve that outcome.
