# Publishing to Substack — Step-by-Step

After running `./prepare_publish.sh`, your newsletter content is on the clipboard and the Substack editor is open.

## Steps

1. **Paste content** — Click inside the Substack editor body, then Cmd+V. Substack will interpret the markdown formatting automatically (headings, bold, lists, blockquotes, horizontal rules).

2. **Set title** — Use the week's lead story. Format: `GovCon Weekly: [Lead Headline] — Week of [Date]`
   - Example: `GovCon Weekly: DoD Drops $2.1B in Cyber — Week of Mar 17`

3. **Set subtitle** — One-line summary of the top 2-3 themes.
   - Example: `Nuclear cleanup surges, USAID contracts orphaned, small business goals slip`

4. **Fix tables** — Substack does not render markdown tables natively. Two options:
   - **Option A (quick):** Leave as pipe-separated text. It reads fine.
   - **Option B (polished):** Screenshot the tables from the HTML version (`output/report_YYYY-MM-DD_v2.html`) and insert as images.

5. **Add charts** — Drag chart images from `assets/` into the post at the appropriate sections:
   - `obligations_by_agency.png` — after the Procurement Pulse section
   - `top_awards_bar.png` — after Who Won This Week
   - `set_aside_goals.png` — after Small Business section
   - Other charts as relevant

6. **Preview** — Click "Preview" in the top right. Check:
   - Headings render correctly (H2 for section headers, H3 for sub-stories)
   - Bold text appears bold
   - Lists are properly formatted
   - No raw markdown artifacts visible

7. **Settings** before publishing:
   - **Section:** Newsletter (default)
   - **Audience:** Everyone (free edition) or Paid subscribers
   - **Email:** Send to subscribers (toggle ON)
   - **Social preview:** Add a 1-2 sentence hook for the email subject line

8. **Publish** — Hit "Publish" (or "Schedule" if you want to send at a specific time, e.g., Tuesday 7am ET).

## Quick Reference

```bash
# Full run: generate + copy + open browser
./prepare_publish.sh

# Already generated today — just copy and open
./prepare_publish.sh --skip-gen

# Custom date range
./prepare_publish.sh --days 14
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Pipeline fails on data pull | Check USAspending API status, re-run |
| Charts fail | Run `python3 create_charts.py` manually, check matplotlib is installed |
| Clipboard empty | Run `cat output/substack_YYYY-MM-DD.md \| pbcopy` manually |
| Formatting looks wrong after paste | Substack sometimes needs a page refresh before paste. Try Cmd+A, Delete, then re-paste |
| Tables render as raw text | Expected — see step 4 above |
