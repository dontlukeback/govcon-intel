# GovCon Weekly Intelligence: Newsletter Design Specification

## Overview

This specification transforms the GovCon Weekly newsletter from a plain text dump into a premium intelligence product that looks like Bloomberg Terminal meets defense intel briefing. All recommendations work within Substack's native capabilities.

---

## Visual Identity

### Color Palette
- **Navy Primary**: `#0A1628` (backgrounds, headers)
- **Gold Accent**: `#C5A44E` (highlights, numbers, CTAs)
- **White**: `#FFFFFF` (body text)
- **Gray Muted**: `#8899AA` (metadata, labels)
- **Alert Red**: `#FF6B6B` (warnings, urgent items)

### Typography Hierarchy
Substack uses system fonts. Set hierarchy through size and weight:

1. **Newsletter Title (H1)**: 36-42px, Bold
2. **Section Headers (H2)**: 28-32px, Bold
3. **Subsection Headers (H3)**: 20-24px, Semibold
4. **Body Text**: 16-18px, Regular, 1.6 line height
5. **Metadata/Captions**: 14px, Regular, muted color
6. **Pull Quotes**: 20-24px, Medium weight

---

## Substack Native Features: What Works

### ✅ Supported Features

1. **Images**: Upload SVGs, PNGs, JPGs
   - Full-width images
   - Inline images with captions
   - Image alignment (left, center, right)

2. **Headings**: H1, H2, H3, H4
   - Use Substack's heading buttons in the editor
   - Creates clean hierarchy

3. **Blockquotes**: Native blockquote styling
   - Use for key insights, warnings, action items
   - Substack adds left border automatically

4. **Horizontal Rules**: `---` creates dividers
   - Use between major sections
   - Can replace with SVG dividers for brand consistency

5. **Tables**: Markdown-style tables
   - Great for rankings, comparisons
   - Auto-formats in email

6. **Lists**: Bulleted and numbered
   - Clean, email-compatible rendering

7. **Bold/Italic**: Standard emphasis

8. **Links**: Inline and button CTAs
   - Substack has a "Subscribe" button widget
   - Custom buttons via their editor

9. **Code Blocks**: For NAICS codes, contract numbers

### ❌ Limited/Not Supported

- Custom CSS (no inline styles)
- Custom fonts (uses system fonts)
- Multi-column layouts (single column only)
- Background colors on text (use images for cards)
- Custom HTML (sanitized in emails)

**Solution**: Use SVG images for branded elements (stats cards, headers, dividers)

---

## Newsletter Structure: Before vs. After

### BEFORE (Current)
```
# Title
*metadata*
---
**Intro paragraph**
## Section
Content
---
```

Problems:
- No visual hierarchy
- Metadata looks like an afterthought
- No branding
- Sections blur together
- Key numbers lost in text
- No visual "stops" for scanning

### AFTER (Recommended)

```
[HEADER IMAGE: newsletter-header.svg]

> **Quick Snapshot**: 1,173 awards | $8.7B value | 547 cyber | 7 SB set-asides

[STATS CARD IMAGE: quick-stats-card.svg]

---

## 📋 Executive Summary

[2-3 sentence bold paragraph highlighting the week's most important signal]

**This week's action**: [One specific, time-bound recommendation]

---

[SECTION DIVIDER IMAGE]

## 🎯 Recompete Watch

[Intro paragraph explaining why this matters]

### 1. Contract Name
**Agency** | Incumbent: Company | $XXM | XX days to expiration

> **Timeline pressure: HIGH/MEDIUM/LOW**

[2-3 paragraphs with analysis]

**Who should pursue**: [Target audience]

**This week**: [Specific action item]

[Repeat for each recompete]

---

[SECTION DIVIDER IMAGE]

## 📊 Agency Signals

[Intro: "What this week's spending tells us..."]

- **Agency Name**: $XXM in activity. [Key insight + implication]
- **Agency Name**: [Pattern detected]. [Strategic meaning]
- **Hottest NAICS**: [Code] ([Category]) up +XX% week-over-week

> **Action**: [Strategic recommendation based on signals]

---

[SECTION DIVIDER IMAGE]

## 🏆 Contractor Power Rankings

| Rank | Contractor | Activity | Key Move |
|------|-----------|----------|----------|
| 1 | Company | $XXM | Contract won at Agency |
| ... | ... | ... | ... |

> **Market Intel**: [Key insight from rankings]

---

[SECTION DIVIDER IMAGE]

## 🔧 Small Business Corner

[Analysis of SB opportunities]

**Target Opportunities for Subcontractors:**

- **Contract Name** ($XXM, Prime): [Specific capabilities needed]
- **Contract Name** ($XXM, Prime): [Specific capabilities needed]

> **Action**: Pick ONE. Find the prime's SB liaison. Send a 1-page brief. Do this by Friday.

---

[SECTION DIVIDER IMAGE]

## 📈 Trend Analysis

### Trend Name: Insight Headline
[3-4 paragraphs of analysis]

**Forward look**: [Prediction with timeline]

> **Strategic Implication**: [What this means for your pipeline]

[Repeat for 2-3 trends]

---

[SECTION DIVIDER IMAGE]

## ✅ This Week's Action Items

> **Prioritized by time-sensitivity**

### URGENT (XX days)
1. [Action item with specific NAICS, agency, deadline]
2. [Action item]

### THIS WEEK
3. [Action item]
4. [Action item]

### THIS MONTH
5. [Action item]
6. [Action item]

---

*GovCon Weekly Intelligence tracks 1,000+ federal contract awards every week across 9 IT verticals. Data sourced from USAspending.gov and FPDS. Published every Monday.*

**Questions?** Reply to this email. We read everything.

[Subscribe button]
```

---

## Image Placement Strategy

### 1. Header (Top)
**File**: `newsletter-header.svg`
**Placement**: First element in newsletter
**Purpose**: Immediate brand recognition, professionalism

### 2. Quick Stats Card (Below intro)
**File**: `quick-stats-card.svg`
**Placement**: After 2-3 sentence intro, before first section
**Purpose**: Scannable snapshot, shareable on LinkedIn

### 3. Section Dividers (Between major sections)
**File**: `section-divider.svg`
**Placement**: Between each major section (after `---`)
**Purpose**: Visual breathing room, clear section breaks

### 4. Optional: Custom Cards for Special Callouts
**Future assets to create**:
- Urgency indicator cards (HIGH/MEDIUM/LOW)
- "New This Week" badges
- "Incumbent Risk" warning cards
- Timeline visualizations for recompetes

---

## Substack Editor Workflow

### Step 1: Upload Images
1. Click "+" in editor → "Image"
2. Upload SVGs first (header, divider, stats card)
3. Set image width to "Full width" for header and stats
4. Set dividers to "Center" alignment

### Step 2: Apply Text Hierarchy
1. Newsletter title: H1
2. Section titles: H2 (with emoji for visual differentiation)
3. Subsections: H3
4. Use bold for key terms, companies, numbers
5. Use blockquotes (>) for action items and key insights

### Step 3: Use Blockquotes Strategically
Blockquotes create visual weight. Use for:
- Timeline pressure indicators
- Action items
- Strategic implications
- Market intel insights

### Step 4: Table Formatting
Create tables in Markdown:
```
| Rank | Contractor | Activity | Key Move |
|------|-----------|----------|----------|
| 1 | GDIT | $1.2B | Won JADC2 |
```
Substack will auto-format with clean borders.

### Step 5: Add Visual Breaks
- Use `---` for horizontal rules between sections
- Insert section-divider.svg for branded breaks
- Add blank lines generously (Substack collapses excess anyway)

---

## Typography Recommendations

### Heading Sizes (in Substack editor)
- **Newsletter title**: "Heading 1" (largest)
- **Section headers**: "Heading 2"
- **Subsection headers**: "Heading 3"
- **Contract/Agency names**: "Heading 4" OR bold body text

### Emphasis Patterns
- **Bold**: Company names, contract names, key numbers, deadlines
- *Italic*: Metadata, data sources, tangential context
- `Code`: NAICS codes, contract IDs, specific references

### Line Spacing
Substack auto-handles this, but group related content:
- Keep analysis paragraphs tight (no blank lines between)
- Add blank line BEFORE new topic
- Double blank line before major sections

---

## Content Layout Patterns

### Pattern 1: Recompete Entries
```
### 1. Contract Name (Descriptive)
**Agency** | Incumbent: Company | $XXM | XX days to expiration

> **Timeline pressure: HIGH**

[Analysis paragraph 1: What's happening]

[Analysis paragraph 2: Why it matters]

**Who should pursue**: [Specific guidance]

**This week**: [Concrete action]
```

### Pattern 2: Agency Signals
```
- **Agency Name**: $XXM in activity. [Insight]. [Implication].
```
Keep to one line per agency for scannability.

### Pattern 3: Trend Analysis
```
### Trend Name: Clear Insight Headline
[Opening: What we're seeing]

[Context: Why it's happening]

[Data: Quantify the trend]

**Forward look**: [Prediction]

> **Strategic Implication**: [What to do]
```

### Pattern 4: Action Items
```
### URGENT (XX days)
1. [Action] — [Specific details: NAICS, agency, artifact to create]
```
Use numbered lists for sequential actions, bullets for parallel options.

---

## Visual Hierarchy Through Color (Via Images)

Since Substack doesn't support colored text, use SVG cards for:

1. **Stats/Numbers**: Gold text on navy background
2. **Warnings**: Red accent for urgency indicators
3. **Action Items**: Could create action-item cards with checkboxes

**Future Asset Ideas**:
- `urgency-high.svg`: Red badge saying "HIGH - XX DAYS"
- `new-this-week.svg`: Gold badge for new signals
- `sb-opportunity.svg`: Green badge for small business set-asides

---

## Email Compatibility Notes

Substack handles email rendering automatically, but follow these rules:

### ✅ Email-Safe Practices
- SVG images (Substack converts to PNG for email)
- Tables (render cleanly in all email clients)
- Horizontal rules (standard HTML `<hr>`)
- Blockquotes (standard email styling)
- Bold/italic (universally supported)

### ⚠️ Email Limitations
- No custom fonts (falls back to system fonts)
- No JavaScript (not applicable here)
- Limited CSS (Substack handles this)

**Bottom line**: Everything in this spec is email-safe.

---

## Before/After Comparison

### Current Newsletter (Plain Text)
- ❌ No visual identity
- ❌ Metadata feels tacked on
- ❌ Sections blur together
- ❌ Key numbers buried in text
- ❌ No scanning stops
- ❌ Looks like internal email, not product

### Redesigned Newsletter (Premium Intel)
- ✅ Branded header establishes tone immediately
- ✅ Stats card makes numbers screenshot-worthy
- ✅ Clear visual hierarchy guides eye
- ✅ Blockquotes elevate action items
- ✅ Section dividers create breathing room
- ✅ Looks like Bloomberg/Axios/premium intelligence

---

## Implementation Checklist

### Phase 1: Core Branding (DONE)
- [x] Header image created
- [x] Section divider created
- [x] Quick stats card created
- [ ] Upload to Substack media library

### Phase 2: Content Restructuring (NEXT)
- [ ] Add header image to newsletter template
- [ ] Reformat intro with stats card
- [ ] Convert plain bullets to blockquote action items
- [ ] Add section dividers between major sections
- [ ] Apply heading hierarchy (H2 for sections, H3 for subsections)
- [ ] Use blockquotes for timeline pressure, actions, implications

### Phase 3: Polish (AFTER FIRST REDESIGNED ISSUE)
- [ ] Create urgency indicator badges (HIGH/MEDIUM/LOW)
- [ ] Create "New This Week" badges for fresh signals
- [ ] Create SB opportunity cards
- [ ] A/B test subject lines with new visual format
- [ ] Track open rates and link clicks

### Phase 4: Advanced (FUTURE)
- [ ] Timeline visualization for recompetes (Gantt-style SVG)
- [ ] Interactive table of contents (if Substack adds support)
- [ ] Animated stat cards (if moving to web-first format)
- [ ] Dark mode optimization

---

## Style Guide Quick Reference

| Element | Formatting | Example |
|---------|-----------|---------|
| Section header | H2 + emoji | `## 🎯 Recompete Watch` |
| Subsection | H3 | `### 1. Contract Name` |
| Agency/Company | Bold | `**DISA**` or `**Leidos**` |
| Contract value | Bold | `**$487M**` |
| NAICS code | Code | `NAICS 541512` |
| Timeline pressure | Blockquote + bold | `> **Timeline pressure: HIGH**` |
| Action item | Blockquote | `> **Action**: Do this thing` |
| Data source | Italic | `*Data: USAspending.gov*` |
| Key numbers in prose | Bold | `up **+28%** week-over-week` |

---

## Emojis for Section Differentiation

Since we can't use colored headers, emojis add visual differentiation:

- 📋 Executive Summary
- 🎯 Recompete Watch
- 📊 Agency Signals
- 🏆 Contractor Power Rankings
- 🔧 Small Business Corner
- 📈 Trend Analysis
- ✅ Action Items

**Alternative**: Use bracketed labels like `[RECOMPETE]` or `[ACTION]` if emojis feel too casual.

---

## Success Metrics

Track these before/after redesign:

1. **Open rate**: Should increase with professional header
2. **Read time**: Should stabilize (visual hierarchy aids scanning)
3. **Link clicks**: Should increase on SAM.gov alerts, FOIA requests
4. **Forwards**: Should increase (more shareable with branding)
5. **Screenshot shares**: New metric — track LinkedIn shares of stats card
6. **Reply rate**: Should stay same or increase (implies engagement)

---

## Next Newsletter: Implementation Plan

1. **Upload assets** to Substack media library:
   - `newsletter-header.svg`
   - `section-divider.svg`
   - `quick-stats-card.svg`

2. **Restructure content** using this template:
   - Insert header at top
   - Move stats into card format
   - Add section dividers
   - Convert key insights to blockquotes
   - Apply heading hierarchy

3. **Preview** in Substack's email preview mode

4. **Test send** to internal email first

5. **Publish** and monitor metrics

---

## Long-Term Evolution

### Month 2-3: Refine
- Create additional SVG assets based on content patterns
- Optimize image file sizes for email load time
- A/B test different intro formats

### Month 4-6: Expand
- Add "Chart of the Week" (visualization of key trend)
- Create downloadable PDF version with enhanced visuals
- Experiment with Substack's audio feature for weekly briefing

### Month 7+: Advanced Features
- Interactive elements if Substack adds support
- Video briefings for major events
- Subscriber-only deep dives with premium formatting

---

## Contact for Design Questions

All assets are version-controlled in `/Users/luke/Personal/govcon-intel/assets/`.

Update this spec as we learn what resonates with readers. The goal: premium intelligence product that commands attention and drives action.
