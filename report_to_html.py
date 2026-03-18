#!/usr/bin/env python3
"""
GovCon Weekly Intelligence -- HTML Newsletter Generator v3
Research-informed rebuild incorporating competitive analysis, audience personas,
newsletter design best practices, and r/GovernmentContracting insights.

Design principles:
- 3-tier visual hierarchy: Scan (8s) > Read (30s/section) > Deep (engaged)
- Gate analysis not data: free tier sees cards, paid sees Intel callouts
- Language matches audience: "capture", "pipeline", "left of the RFP"
- Authority palette: navy + gold + red urgency
- Table-based layout, inline CSS, Outlook-safe, dark mode ready
"""

import json
import os
import sys
import argparse
import html as html_module
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def esc(text):
    if not text:
        return ""
    return html_module.escape(str(text))


def fmt_money(val):
    if isinstance(val, str):
        return val
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"${val/1_000_000:.0f}M"
    if val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:,.0f}"


def urgency_color(urgency):
    return {"high": "#DC2626", "medium": "#D97706"}.get(urgency, "#6B7280")


def urgency_bg(urgency):
    return {"high": "#FEF2F2", "medium": "#FFFBEB"}.get(urgency, "#F9FAFB")


FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"


def generate_html(data):
    notable = data.get("notable", {})
    sections = data.get("sections", {})
    pulse = data.get("market_pulse", {})
    subtitle = data.get("report_subtitle", "Weekly Intelligence Brief")

    recompetes = sections.get("recompete_alerts", {}).get("items", [])
    new_awards = sections.get("new_awards", {}).get("items", [])
    options = sections.get("option_exercises", {}).get("items", [])
    funding = sections.get("funding_actions", {}).get("items", [])

    recompete_total = sum(r.get("current_value_raw", 0) for r in recompetes)
    awards_total = sum(a.get("award_value_raw", 0) for a in new_awards)
    options_total = sum(o.get("option_value_raw", 0) for o in options)
    funding_total = sum(f.get("modification_value_raw", 0) for f in funding)

    h = []

    # ================================================================
    # DOCUMENT HEAD — dark mode, Outlook fixes, accessibility
    # ================================================================
    h.append(f"""<!DOCTYPE html>
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
<style>
  :root {{ color-scheme: light dark; }}
  @media (prefers-color-scheme: dark) {{
    .body-bg {{ background-color: #0B1120 !important; }}
    .card-bg {{ background-color: #1E293B !important; }}
    .text-primary {{ color: #F1F5F9 !important; }}
    .text-secondary {{ color: #94A3B8 !important; }}
    .border-light {{ border-color: #334155 !important; }}
  }}
  @media only screen and (max-width: 620px) {{
    .content-pad {{ padding-left: 16px !important; padding-right: 16px !important; }}
    .mobile-full {{ width: 100% !important; }}
    .stat-cell {{ display: block !important; width: 100% !important; border-right: none !important; border-bottom: 1px solid #E2E8F0 !important; }}
    .mobile-hide {{ display: none !important; }}
    .mobile-stack {{ display: block !important; width: 100% !important; text-align: left !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:{FONT};color:#1E293B;line-height:1.6;-webkit-font-smoothing:antialiased;">""")

    # Preheader with spacing hack
    preheader = esc(notable.get("headline", "This week in federal contracting"))
    spacer = "&#8199;&#65279;&#847; " * 30
    h.append(f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{preheader} {spacer}</div>')

    # Accessibility wrapper
    h.append(f'<div role="article" aria-roledescription="email" aria-label="GovCon Weekly Intelligence - {esc(subtitle)}" lang="en" dir="ltr">')

    # Outer wrapper table
    h.append("""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;" class="body-bg">
<tr><td align="center" style="padding:24px 16px;">""")

    # Ghost table for Outlook max-width
    h.append("""<!--[if mso]>
<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="620"><tr><td>
<![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;">""")

    # ================================================================
    # HEADER — masthead + date
    # ================================================================
    h.append(f"""
<tr><td style="background:#0F172A;padding:28px 32px;border-radius:12px 12px 0 0;" class="content-pad">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">Intelligence Brief</div>
      <div style="font-size:24px;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px;">GovCon Weekly</div>
    </td>
    <td style="text-align:right;vertical-align:bottom;">
      <div style="font-size:13px;color:#94A3B8;">{esc(subtitle)}</div>
    </td>
  </tr>
  </table>
</td></tr>""")

    # Gold accent bar
    h.append('<tr><td style="height:3px;background:linear-gradient(90deg,#C9A227,#E8D48B);font-size:0;line-height:0;">&nbsp;</td></tr>')

    # ================================================================
    # NUMBER OF THE WEEK — big stat callout (CB Insights pattern)
    # ================================================================
    key_stat = notable.get("key_stat", "")
    key_stat_label = notable.get("key_stat_label", "")
    if key_stat:
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:28px 32px 0;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="text-align:center;padding:20px 0;">
      <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">Number of the Week</div>
      <div style="font-size:48px;font-weight:900;color:#0F172A;letter-spacing:-2px;line-height:1;" class="text-primary">{esc(key_stat)}</div>
      <div style="font-size:14px;font-weight:600;color:#64748B;margin-top:8px;" class="text-secondary">{esc(key_stat_label)}</div>
    </td>
  </tr>
  </table>
</td></tr>""")

    # ================================================================
    # SIGNAL OF THE WEEK — hero callout
    # ================================================================
    h.append(f"""
<tr><td style="background:#FFFFFF;padding:24px 32px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#FEFCE8;border-left:4px solid #C9A227;border-radius:0 8px 8px 0;">
  <tr><td style="padding:20px 24px;">
    <div style="font-size:11px;font-weight:700;color:#92400E;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">&#9670; Signal of the Week</div>
    <div style="font-size:20px;font-weight:800;color:#1E293B;line-height:1.3;margin-bottom:10px;" class="text-primary">{esc(notable.get('headline', ''))}</div>
    <div style="font-size:14px;color:#475569;line-height:1.7;" class="text-secondary">{esc(notable.get('summary', ''))}</div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # KPI DASHBOARD — 4-stat bar
    # ================================================================
    stats = [
        ("Recompetes at Risk", fmt_money(recompete_total), "#DC2626", len(recompetes)),
        ("Awarded", fmt_money(awards_total), "#16A34A", len(new_awards)),
        ("Options Renewed", fmt_money(options_total), "#2563EB", len(options)),
        ("Funding Mods", fmt_money(funding_total), "#64748B", len(funding)),
    ]
    h.append('<tr><td style="background:#FFFFFF;padding:0 32px 24px;" class="content-pad card-bg">')
    h.append('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;" class="border-light">')
    h.append("<tr>")
    for i, (label, value, color, count) in enumerate(stats):
        border = 'border-right:1px solid #E2E8F0;' if i < 3 else ''
        h.append(f"""<td style="width:25%;padding:16px 8px;text-align:center;{border}" class="stat-cell">
  <div style="font-size:22px;font-weight:800;color:{color};letter-spacing:-0.5px;">{value}</div>
  <div style="font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.5px;margin-top:4px;line-height:1.3;">{label}<br>({count} this week)</div>
</td>""")
    h.append("</tr></table></td></tr>")

    # ================================================================
    # TABLE OF CONTENTS — "In This Brief" (Morning Brew pattern)
    # ================================================================
    toc_items = []
    if recompetes:
        toc_items.append(f'<strong style="color:#DC2626;">01</strong>&nbsp; Recompete Alerts ({len(recompetes)}) &mdash; {fmt_money(recompete_total)} at risk')
    if new_awards:
        toc_items.append(f'<strong style="color:#16A34A;">02</strong>&nbsp; New Awards ({len(new_awards)}) &mdash; {fmt_money(awards_total)} awarded')
    if options:
        toc_items.append(f'<strong style="color:#2563EB;">03</strong>&nbsp; Option Exercises ({len(options)}) &mdash; {fmt_money(options_total)} renewed')
    if funding:
        toc_items.append(f'<strong style="color:#64748B;">04</strong>&nbsp; Funding Actions ({len(funding)}) &mdash; {fmt_money(funding_total)} in mods')
    toc_items.append('<strong style="color:#C9A227;">05</strong>&nbsp; Market Pulse &mdash; agency spend + trending NAICS')

    toc_html = "<br>".join(toc_items)
    h.append(f"""
<tr><td style="background:#FFFFFF;padding:0 32px 24px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F8FAFC;border-radius:8px;border:1px solid #E2E8F0;" class="border-light">
  <tr><td style="padding:16px 20px;">
    <div style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">In This Brief</div>
    <div style="font-size:13px;line-height:2;color:#1E293B;" class="text-primary">
      {toc_html}
    </div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # SECTION DIVIDER helper
    # ================================================================
    def section_divider():
        return '<tr><td style="background:#FFFFFF;padding:0 32px;" class="content-pad card-bg"><div style="border-top:1px solid #E2E8F0;"></div></td></tr>'

    # ================================================================
    # 01 — RECOMPETE ALERTS
    # ================================================================
    if recompetes:
        h.append(section_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 8px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">01 / Recompete Alerts</div>
      <div style="font-size:18px;font-weight:800;color:#1E293B;" class="text-primary">Contracts Expiring &mdash; The Work Still Needs to Get Done</div>
    </td>
    <td style="text-align:right;vertical-align:bottom;">
      <div style="font-size:12px;color:#DC2626;font-weight:700;">ACTION REQUIRED</div>
    </td>
  </tr>
  <tr><td colspan="2" style="padding-top:6px;"><div style="font-size:13px;color:#64748B;line-height:1.5;" class="text-secondary">These contracts are ending soon. The agencies still need the work performed. If you&rsquo;re in the right NAICS and have the past performance, now is when capture starts.</div></td></tr>
  </table>
</td></tr>""")

        for r in recompetes:
            uc = urgency_color(r.get("urgency", ""))
            ubg = urgency_bg(r.get("urgency", ""))
            days = r.get("days_remaining", "?")
            urgency_label = "URGENT" if r.get("urgency") == "high" else "WATCH"
            set_aside = r.get("set_aside", "N/A")

            # "Wired?" signal based on set-aside and status
            wired_signal = ""
            status = r.get("solicitation_status", "")
            if "sources sought" in status.lower():
                wired_signal = '<span style="display:inline-block;background:#DBEAFE;color:#1D4ED8;font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;margin-left:6px;">OPEN FIELD</span>'
            elif "draft rfp" in status.lower():
                wired_signal = '<span style="display:inline-block;background:#FEF3C7;color:#92400E;font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;margin-left:6px;">SHAPING WINDOW</span>'
            elif "market research" in status.lower():
                wired_signal = '<span style="display:inline-block;background:#D1FAE5;color:#065F46;font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;margin-left:6px;">EARLY &mdash; GET IN NOW</span>'

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:6px 32px 16px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid {uc};border-radius:0 8px 8px 0;" class="border-light">
  <tr><td style="padding:20px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <span style="display:inline-block;background:{uc};color:#FFF;font-size:10px;font-weight:800;padding:3px 10px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px;">{urgency_label} &middot; {days} days</span>
        {wired_signal}
      </td>
      <td style="text-align:right;">
        <span style="font-size:22px;font-weight:800;color:{uc};">{esc(r.get('current_value', '?'))}</span>
      </td>
    </tr>
    </table>
    <div style="font-size:16px;font-weight:700;color:#1E293B;margin-top:12px;line-height:1.3;" class="text-primary">{esc(r.get('contract_name', ''))}</div>
    <div style="font-size:13px;color:#64748B;margin-top:6px;line-height:1.5;" class="text-secondary">
      {esc(r.get('agency', ''))} &middot; Incumbent: <strong style="color:#1E293B;">{esc(r.get('incumbent', '?'))}</strong><br>
      NAICS {esc(r.get('naics', '?'))} &middot; {esc(set_aside)} &middot; <em>{esc(r.get('solicitation_status', '?'))}</em>
    </div>
    <div style="font-size:13px;color:#475569;margin-top:12px;padding:12px 14px;background:{ubg};border-radius:6px;line-height:1.6;">
      <strong style="color:{uc};">&#9654; Intel:</strong> {esc(r.get('notable_detail', ''))}
    </div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # 02 — NEW AWARDS
    # ================================================================
    if new_awards:
        h.append(section_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 8px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">02 / New Awards</div>
      <div style="font-size:18px;font-weight:800;color:#1E293B;" class="text-primary">Who Won What &mdash; And What It Means for Your Pipeline</div>
    </td>
    <td style="text-align:right;vertical-align:bottom;">
      <div style="font-size:12px;color:#16A34A;font-weight:700;">{fmt_money(awards_total)} THIS WEEK</div>
    </td>
  </tr>
  <tr><td colspan="2" style="padding-top:6px;"><div style="font-size:13px;color:#64748B;line-height:1.5;" class="text-secondary">Track winners, losers, and team compositions. Know what the competitive landscape looks like before your next gate review.</div></td></tr>
  </table>
</td></tr>""")

        for a in new_awards:
            competitors = a.get("competitors_known", [])
            comp_str = ", ".join(esc(c) for c in competitors) if competitors else "Not disclosed"

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:6px 32px 16px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid #16A34A;border-radius:0 8px 8px 0;" class="border-light">
  <tr><td style="padding:20px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <span style="display:inline-block;background:#16A34A;color:#FFF;font-size:10px;font-weight:800;padding:3px 10px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px;">Awarded {esc(a.get('award_date', ''))}</span>
      </td>
      <td style="text-align:right;">
        <span style="font-size:22px;font-weight:800;color:#16A34A;">{esc(a.get('award_value', '?'))}</span>
      </td>
    </tr>
    </table>
    <div style="font-size:16px;font-weight:700;color:#1E293B;margin-top:12px;line-height:1.3;" class="text-primary">{esc(a.get('contract_name', ''))}</div>
    <div style="font-size:13px;color:#64748B;margin-top:6px;line-height:1.5;" class="text-secondary">
      {esc(a.get('agency', ''))} &middot; Winner: <strong style="color:#16A34A;">{esc(a.get('awardee', '?'))}</strong><br>
      NAICS {esc(a.get('naics', '?'))} &middot; {esc(a.get('set_aside', ''))} &middot; {esc(a.get('period_of_performance', ''))}
    </div>
    <div style="font-size:13px;color:#64748B;margin-top:4px;" class="text-secondary">
      <strong>Also competed:</strong> {comp_str}
    </div>
    <div style="font-size:13px;color:#475569;margin-top:12px;padding:12px 14px;background:#F0FDF4;border-radius:6px;line-height:1.6;">
      <strong style="color:#16A34A;">&#9654; Intel:</strong> {esc(a.get('notable_detail', ''))}
    </div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # 03 — OPTION EXERCISES
    # ================================================================
    if options:
        h.append(section_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 8px;" class="content-pad card-bg">
  <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">03 / Option Exercises</div>
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="text-primary">Agency Confidence Signals &mdash; Who&rsquo;s Getting Renewed</div>
  <div style="font-size:13px;color:#64748B;margin-top:6px;line-height:1.5;" class="text-secondary">Option exercises mean the government is satisfied. Watch for final option years &mdash; that&rsquo;s where recompetes begin.</div>
</td></tr>""")

        for o in options:
            # Highlight final option year
            option_year = o.get("option_year", "")
            is_final = False
            if option_year:
                parts = option_year.lower().split(" of ")
                if len(parts) == 2:
                    try:
                        current = int(parts[0].replace("option year", "").strip())
                        total = int(parts[1].strip())
                        if current >= total - 1:
                            is_final = True
                    except ValueError:
                        pass

            final_badge = ""
            if is_final:
                final_badge = ' <span style="display:inline-block;background:#FEF2F2;color:#DC2626;font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;">FINAL YEAR &mdash; RECOMPETE COMING</span>'

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:6px 32px 12px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:0 8px 8px 0;" class="border-light">
  <tr><td style="padding:16px 20px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <div style="font-size:15px;font-weight:700;color:#1E293B;line-height:1.3;" class="text-primary">{esc(o.get('contract_name', ''))}</div>
        <div style="font-size:13px;color:#64748B;margin-top:4px;" class="text-secondary">{esc(o.get('agency', ''))} &middot; <strong>{esc(o.get('contractor', ''))}</strong> &middot; {esc(option_year)}{final_badge}</div>
      </td>
      <td style="text-align:right;vertical-align:top;">
        <span style="font-size:18px;font-weight:800;color:#2563EB;">{esc(o.get('option_value', '?'))}</span>
      </td>
    </tr>
    </table>
    <div style="font-size:13px;color:#475569;margin-top:10px;padding:10px 14px;background:#EFF6FF;border-radius:6px;line-height:1.6;">
      <strong style="color:#2563EB;">&#9654; Intel:</strong> {esc(o.get('notable_detail', ''))}
    </div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # 04 — FUNDING ACTIONS (table format)
    # ================================================================
    if funding:
        h.append(section_divider())
        h.append("""
<tr><td style="background:#FFFFFF;padding:20px 32px 8px;" class="content-pad card-bg">
  <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">04 / Funding Actions</div>
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="text-primary">Ceiling Increases, Mods &amp; New Task Orders</div>
  <div style="font-size:13px;color:#64748B;margin-top:6px;line-height:1.5;" class="text-secondary">Follow the money. Ceiling increases signal growing programs. New task orders reveal where agencies are spending now.</div>
</td></tr>""")

        for i, f_item in enumerate(funding):
            action = f_item.get("action_type", "")
            action_color = "#7C3AED" if "ceiling" in action.lower() else "#0891B2" if "task order" in action.lower() else "#64748B"

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:6px 32px 12px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid {action_color};border-radius:0 8px 8px 0;" class="border-light">
  <tr><td style="padding:16px 20px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <span style="display:inline-block;background:{action_color};color:#FFF;font-size:10px;font-weight:800;padding:2px 8px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px;">{esc(action)}</span>
        <div style="font-size:15px;font-weight:700;color:#1E293B;margin-top:8px;line-height:1.3;" class="text-primary">{esc(f_item.get('contract_name', ''))}</div>
        <div style="font-size:13px;color:#64748B;margin-top:4px;" class="text-secondary">{esc(f_item.get('agency', ''))} &middot; {esc(f_item.get('contractor', ''))}</div>
      </td>
      <td style="text-align:right;vertical-align:top;">
        <span style="font-size:18px;font-weight:800;color:{action_color};">{esc(f_item.get('modification_value', '?'))}</span>""")
            new_ceil = f_item.get("new_ceiling")
            if new_ceil:
                h.append(f'<div style="font-size:11px;color:#64748B;margin-top:2px;">New ceiling: {esc(new_ceil)}</div>')
            h.append("""      </td>
    </tr>
    </table>""")
            detail = f_item.get("notable_detail", "")
            if detail:
                h.append(f"""    <div style="font-size:13px;color:#475569;margin-top:10px;padding:10px 14px;background:#F5F3FF;border-radius:6px;line-height:1.6;">
      <strong style="color:{action_color};">&#9654; Intel:</strong> {esc(detail)}
    </div>""")
            h.append("  </td></tr>\n  </table>\n</td></tr>")

    # ================================================================
    # 05 — MARKET PULSE (dark panel)
    # ================================================================
    top_agencies = pulse.get("top_agencies_by_spend", [])
    trending = pulse.get("trending_naics", [])

    h.append(section_divider())
    h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 8px;" class="content-pad card-bg">
  <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">05 / Market Pulse</div>
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="text-primary">Where the Money Is Going</div>
</td></tr>
<tr><td style="background:#FFFFFF;padding:8px 32px 24px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;border-radius:8px;overflow:hidden;border-top:3px solid #C9A227;">
  <tr><td style="padding:28px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;">Total Obligations This Week</div>
        <div style="font-size:40px;font-weight:900;color:#FFFFFF;letter-spacing:-1.5px;margin-top:6px;line-height:1;">{esc(pulse.get('total_obligations_week', '?'))}</div>
      </td>
      <td style="text-align:right;vertical-align:bottom;">
        <span style="display:inline-block;background:#16A34A;color:#FFFFFF;font-size:14px;font-weight:700;padding:6px 14px;border-radius:6px;">{esc(pulse.get('yoy_change', '?'))} YoY</span>
      </td>
    </tr>
    </table>""")

    if top_agencies:
        h.append("""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:24px;border-top:1px solid #1E293B;padding-top:16px;">
    <tr><td colspan="2" style="padding-bottom:10px;"><div style="font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;">Top Agencies by Spend</div></td></tr>""")
        for ag in top_agencies:
            h.append(f"""    <tr>
      <td style="padding:7px 0;font-size:14px;color:#E2E8F0;">{esc(ag.get('agency', ''))}</td>
      <td style="padding:7px 0;text-align:right;font-size:15px;font-weight:700;color:#FFFFFF;">{esc(ag.get('amount', ''))}</td>
    </tr>""")
        h.append("</table>")

    if trending:
        h.append("""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;border-top:1px solid #1E293B;padding-top:16px;">
    <tr><td colspan="2" style="padding-bottom:10px;"><div style="font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;">Trending NAICS Codes</div></td></tr>""")
        for t in trending:
            h.append(f"""    <tr>
      <td style="padding:6px 0;font-size:13px;color:#E2E8F0;">{esc(t.get('code', ''))} &mdash; {esc(t.get('description', ''))}</td>
      <td style="padding:6px 0;text-align:right;font-size:14px;font-weight:700;color:#C9A227;">{esc(t.get('change', ''))}</td>
    </tr>""")
        h.append("</table>")

    h.append("</td></tr></table></td></tr>")

    # ================================================================
    # CTA BLOCK — research-informed copy
    # ================================================================
    h.append("""
<tr><td style="background:#FFFFFF;padding:8px 32px 28px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;border-radius:8px;overflow:hidden;">
  <tr><td style="padding:32px;text-align:center;">
    <div style="font-size:22px;font-weight:800;color:#FFFFFF;margin-bottom:8px;line-height:1.3;">Stop wasting $50K on proposals you can&rsquo;t win</div>
    <div style="font-size:14px;color:#94A3B8;margin-bottom:24px;line-height:1.6;">GovCon Weekly Pro gives you bid/no-bid intelligence, recompete alerts filtered to your NAICS codes, and competitor analysis &mdash; every Monday at 7am.</div>
    <!--[if mso]>
    <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="#" style="height:48px;v-text-anchor:middle;width:260px;" arcsize="13%" strokecolor="#C9A227" fillcolor="#C9A227">
    <w:anchorlock/>
    <center style="color:#0F172A;font-family:sans-serif;font-size:15px;font-weight:bold;">Get Pro Intelligence &rarr;</center>
    </v:roundrect>
    <![endif]-->
    <!--[if !mso]><!-->
    <a href="#" style="display:inline-block;background:#C9A227;color:#0F172A;font-size:15px;font-weight:800;padding:14px 36px;border-radius:6px;text-decoration:none;letter-spacing:0.3px;">Get Pro Intelligence &rarr;</a>
    <!--<![endif]-->
    <div style="font-size:12px;color:#64748B;margin-top:14px;">$249/year &middot; Cancel anytime &middot; 14-day free trial</div>
    <div style="font-size:11px;color:#475569;margin-top:8px;font-style:italic;">Saves BD teams 5+ hours/week in research. That&rsquo;s $7,500/year at $30/hr.</div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # FEEDBACK — "Was this useful?" (engagement signal)
    # ================================================================
    h.append("""
<tr><td style="background:#FFFFFF;padding:0 32px 24px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="text-align:center;">
  <tr><td style="padding:8px 0;">
    <div style="font-size:13px;color:#64748B;">Was this brief useful?&nbsp;&nbsp;
      <a href="#" style="text-decoration:none;font-size:18px;" title="Very useful">&#128077;</a>&nbsp;&nbsp;
      <a href="#" style="text-decoration:none;font-size:18px;" title="Not useful">&#128078;</a>&nbsp;&nbsp;
      <span style="color:#94A3B8;">&middot;</span>&nbsp;&nbsp;
      <a href="#" style="color:#2563EB;text-decoration:none;font-size:13px;font-weight:600;">Forward to a colleague</a>
    </div>
  </td></tr>
  </table>
</td></tr>""")

    # ================================================================
    # FOOTER
    # ================================================================
    h.append("""
<tr><td style="background:#FFFFFF;padding:20px 32px 24px;border-top:1px solid #E2E8F0;border-radius:0 0 12px 12px;" class="content-pad card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="text-align:center;">
    <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">GovCon Weekly Intelligence</div>
    <div style="font-size:12px;color:#94A3B8;line-height:2;">
      AI-powered federal contract analysis for BD professionals<br>
      Data: USAspending.gov &middot; FPDS-NG &middot; SAM.gov &middot; Agency budget documents<br>
      <a href="#" style="color:#2563EB;text-decoration:none;">Unsubscribe</a> &middot;
      <a href="#" style="color:#2563EB;text-decoration:none;">Manage Preferences</a> &middot;
      <a href="#" style="color:#2563EB;text-decoration:none;">View in Browser</a>
    </div>
  </td></tr>
  </table>
</td></tr>""")

    # Close ghost table + outer wrapper
    h.append("""
</table>
<!--[if mso]>
</td></tr></table>
<![endif]-->
</td></tr>
</table>
</div>
</body>
</html>""")

    return "\n".join(h)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(BASE_DIR / "data" / "corrected_all.json"))
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    html = generate_html(data)

    if args.output:
        out_path = args.output
    else:
        os.makedirs(BASE_DIR / "output", exist_ok=True)
        datestamp = data.get("report_date", datetime.now().strftime("%Y-%m-%d"))
        out_path = str(BASE_DIR / "output" / f"report_{datestamp}.html")

    with open(out_path, "w") as f:
        f.write(html)

    print(f"Saved: {out_path}", file=sys.stderr)
    return out_path


if __name__ == "__main__":
    main()
