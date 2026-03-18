#!/usr/bin/env python3
"""
GovCon Weekly Intelligence -- HTML Newsletter Generator v4
Research-informed, intelligence-dense newsletter worth paying for.
"""

import json
import os
import sys
import argparse
import html as html_module
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"


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


def urgency_color(u):
    return {"high": "#DC2626", "medium": "#D97706"}.get(u, "#6B7280")


def urgency_bg(u):
    return {"high": "#FEF2F2", "medium": "#FFFBEB"}.get(u, "#F9FAFB")


def priority_color(p):
    return {"urgent": "#DC2626", "this_week": "#D97706", "this_month": "#2563EB"}.get(p, "#64748B")


def priority_label(p):
    return {"urgent": "URGENT", "this_week": "THIS WEEK", "this_month": "THIS MONTH"}.get(p, p.upper())


def winnability_badge(score):
    m = {
        "high": ("#059669", "#ECFDF5", "HIGH WINNABILITY"),
        "medium": ("#D97706", "#FFFBEB", "MEDIUM WINNABILITY"),
        "low": ("#DC2626", "#FEF2F2", "LOW WINNABILITY"),
    }
    color, bg, label = m.get(score, ("#64748B", "#F9FAFB", "UNRATED"))
    return f'<span style="display:inline-block;background:{bg};color:{color};font-size:10px;font-weight:700;padding:2px 8px;border-radius:3px;border:1px solid {color};letter-spacing:0.5px;">{label}</span>'


# ────────────────────────────────────────────────────────────────
# Reusable HTML building blocks
# ────────────────────────────────────────────────────────────────

def _head():
    return f"""<!DOCTYPE html>
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
<noscript><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
<![endif]-->
<style>
  :root {{ color-scheme: light dark; }}
  @media (prefers-color-scheme: dark) {{
    .body-bg {{ background-color: #0B1120 !important; }}
    .card-bg {{ background-color: #1E293B !important; }}
    .tp {{ color: #F1F5F9 !important; }}
    .ts {{ color: #94A3B8 !important; }}
  }}
  @media only screen and (max-width: 620px) {{
    .cp {{ padding-left: 16px !important; padding-right: 16px !important; }}
    .stat-cell {{ display: block !important; width: 100% !important; border-right: none !important; border-bottom: 1px solid #E2E8F0 !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:{FONT};color:#1E293B;line-height:1.6;-webkit-font-smoothing:antialiased;">"""


def _preheader(text):
    spacer = "&#8199;&#65279;&#847; " * 30
    return f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{esc(text)} {spacer}</div>'


def _open_wrapper(subtitle):
    return f"""<div role="article" aria-roledescription="email" aria-label="GovCon Weekly Intelligence - {esc(subtitle)}" lang="en">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;" class="body-bg">
<tr><td align="center" style="padding:24px 16px;">
<!--[if mso]><table role="presentation" cellspacing="0" cellpadding="0" border="0" width="620"><tr><td><![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;">"""


def _close_wrapper():
    return """</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table></div></body></html>"""


def _divider():
    return '<tr><td style="background:#FFFFFF;padding:0 32px;" class="cp card-bg"><div style="border-top:1px solid #E2E8F0;"></div></td></tr>'


def _section_label(num, title):
    return f'<div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">{num} / {esc(title)}</div>'


# ────────────────────────────────────────────────────────────────
# Main generator
# ────────────────────────────────────────────────────────────────

def generate_html(data):
    notable = data.get("notable", {})
    doge = data.get("doge_tracker", {})
    sections = data.get("sections", {})
    pulse = data.get("market_pulse", {})
    action_items = data.get("action_items", [])
    one_to_watch = data.get("one_to_watch", {})
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
    h.append(_head())
    h.append(_preheader(notable.get("headline", "This week in federal contracting")))
    h.append(_open_wrapper(subtitle))

    # ── HEADER ──
    h.append(f"""
<tr><td style="background:#0F172A;padding:28px 32px;border-radius:12px 12px 0 0;" class="cp">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td><div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">Intelligence Brief</div>
    <div style="font-size:24px;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px;">GovCon Weekly</div></td>
    <td style="text-align:right;vertical-align:bottom;"><div style="font-size:13px;color:#94A3B8;">{esc(subtitle)}</div></td>
  </tr></table>
</td></tr>
<tr><td style="height:3px;background:#C9A227;font-size:0;line-height:0;">&nbsp;</td></tr>""")

    # ── NUMBER OF THE WEEK ──
    key_stat = notable.get("key_stat", "")
    if key_stat:
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:28px 32px 0;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="text-align:center;padding:16px 0;">
    <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;">Number of the Week</div>
    <div style="font-size:48px;font-weight:900;color:#0F172A;letter-spacing:-2px;line-height:1;" class="tp">{esc(key_stat)}</div>
    <div style="font-size:14px;font-weight:600;color:#64748B;margin-top:8px;" class="ts">{esc(notable.get('key_stat_label', ''))}</div>
  </td></tr></table>
</td></tr>""")

    # ── SIGNAL OF THE WEEK ──
    h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#FEFCE8;border-left:4px solid #C9A227;border-radius:0 8px 8px 0;">
  <tr><td style="padding:20px 24px;">
    <div style="font-size:11px;font-weight:700;color:#92400E;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">&#9670; Signal of the Week</div>
    <div style="font-size:20px;font-weight:800;color:#1E293B;line-height:1.3;margin-bottom:10px;" class="tp">{esc(notable.get('headline', ''))}</div>
    <div style="font-size:14px;color:#475569;line-height:1.7;" class="ts">{esc(notable.get('summary', ''))}</div>
  </td></tr></table>
</td></tr>""")

    # ── KPI DASHBOARD ──
    stats = [
        ("Recompetes", fmt_money(recompete_total), "#DC2626", len(recompetes)),
        ("Awarded", fmt_money(awards_total), "#16A34A", len(new_awards)),
        ("Renewed", fmt_money(options_total), "#2563EB", len(options)),
        ("Funding", fmt_money(funding_total), "#64748B", len(funding)),
    ]
    h.append('<tr><td style="background:#FFFFFF;padding:0 32px 20px;" class="cp card-bg">')
    h.append('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;"><tr>')
    for i, (label, value, color, count) in enumerate(stats):
        bdr = 'border-right:1px solid #E2E8F0;' if i < 3 else ''
        h.append(f'<td style="width:25%;padding:14px 8px;text-align:center;{bdr}" class="stat-cell"><div style="font-size:22px;font-weight:800;color:{color};letter-spacing:-0.5px;">{value}</div><div style="font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.5px;margin-top:3px;">{label} ({count})</div></td>')
    h.append("</tr></table></td></tr>")

    # ── TABLE OF CONTENTS ──
    sec_num = 0
    toc = []
    if doge:
        sec_num += 1; toc.append(f'<strong style="color:#EF4444;">0{sec_num}</strong>&nbsp; DOGE Tracker &mdash; {len(doge.get("agencies_affected",[]))} agencies affected')
    sec_recompete = sec_num + 1 if recompetes else 0
    if recompetes:
        sec_num += 1; toc.append(f'<strong style="color:#DC2626;">0{sec_num}</strong>&nbsp; Recompete Alerts ({len(recompetes)}) &mdash; {fmt_money(recompete_total)} at risk')
    if new_awards:
        sec_num += 1; toc.append(f'<strong style="color:#16A34A;">0{sec_num}</strong>&nbsp; New Awards ({len(new_awards)}) &mdash; {fmt_money(awards_total)}')
    if options:
        sec_num += 1; toc.append(f'<strong style="color:#2563EB;">0{sec_num}</strong>&nbsp; Option Exercises ({len(options)}) &mdash; {fmt_money(options_total)}')
    if funding:
        sec_num += 1; toc.append(f'<strong style="color:#7C3AED;">0{sec_num}</strong>&nbsp; Funding Actions ({len(funding)}) &mdash; {fmt_money(funding_total)}')
    sec_num += 1; toc.append(f'<strong style="color:#C9A227;">0{sec_num}</strong>&nbsp; Market Pulse + Action Items')
    if one_to_watch:
        sec_num += 1; toc.append(f'<strong style="color:#0F172A;">0{sec_num}</strong>&nbsp; One to Watch &mdash; {esc(one_to_watch.get("headline","")[:50])}...')

    h.append(f"""
<tr><td style="background:#FFFFFF;padding:0 32px 20px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F8FAFC;border-radius:8px;border:1px solid #E2E8F0;">
  <tr><td style="padding:14px 20px;">
    <div style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">In This Brief</div>
    <div style="font-size:13px;line-height:2;color:#1E293B;" class="tp">{'<br>'.join(toc)}</div>
  </td></tr></table>
</td></tr>""")

    # ════════════════════════════════════════════════════════════
    # 01 — DOGE TRACKER
    # ════════════════════════════════════════════════════════════
    cur_sec = 0
    if doge:
        cur_sec += 1
        h.append(_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 12px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'DOGE Tracker')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;margin-bottom:8px;" class="tp">Federal Restructuring &amp; Budget Impact</div>
  <div style="font-size:14px;color:#475569;line-height:1.7;margin-bottom:16px;padding:14px;background:#FEF2F2;border-left:4px solid #EF4444;border-radius:0 6px 6px 0;" class="ts">{esc(doge.get('headline', ''))}</div>
</td></tr>""")

        # Agency impacts
        for ag in doge.get("agencies_affected", []):
            action = ag.get("action", "")
            is_growing = "growing" in action.lower() or "absorbing" in action.lower()
            dot_color = "#16A34A" if is_growing else "#DC2626"
            h.append(f"""
<tr><td style="background:#FFFFFF;padding:0 32px 10px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-radius:6px;">
  <tr><td style="padding:14px 16px;">
    <div style="font-size:14px;font-weight:700;color:#1E293B;" class="tp"><span style="color:{dot_color};">&#9679;</span> {esc(ag.get('agency',''))}: {esc(action)}</div>
    <div style="font-size:13px;color:#475569;margin-top:6px;line-height:1.6;" class="ts">{esc(ag.get('impact',''))}</div>
    <div style="font-size:12px;color:#64748B;margin-top:6px;font-style:italic;" class="ts"><strong>Status:</strong> {esc(ag.get('status',''))}</div>
  </td></tr></table>
</td></tr>""")

        # Court rulings
        rulings = doge.get("court_rulings", [])
        if rulings:
            h.append('<tr><td style="background:#FFFFFF;padding:8px 32px 4px;" class="cp card-bg"><div style="font-size:12px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;">Court Rulings to Watch</div></td></tr>')
            for cr in rulings:
                h.append(f"""
<tr><td style="background:#FFFFFF;padding:4px 32px 10px;" class="cp card-bg">
  <div style="font-size:13px;color:#1E293B;line-height:1.6;padding:10px 14px;background:#F8FAFC;border-radius:6px;border-left:3px solid #6366F1;" class="tp">
    <strong>{esc(cr.get('case',''))}</strong>: {esc(cr.get('ruling',''))}<br>
    <span style="color:#64748B;">{esc(cr.get('practical_impact',''))}</span>
  </div>
</td></tr>""")

        # Contractor impact
        contractors = doge.get("contractor_impact", [])
        if contractors:
            h.append('<tr><td style="background:#FFFFFF;padding:8px 32px 4px;" class="cp card-bg"><div style="font-size:12px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;">Contractor Exposure</div></td></tr>')
            for ci in contractors:
                h.append(f"""
<tr><td style="background:#FFFFFF;padding:4px 32px 10px;" class="cp card-bg">
  <div style="font-size:13px;line-height:1.6;padding:10px 14px;background:#FEF2F2;border-radius:6px;">
    <strong style="color:#1E293B;">{esc(ci.get('contractor',''))}</strong> &mdash; {esc(ci.get('exposure',''))}<br>
    <span style="color:#475569;">{esc(ci.get('status',''))}</span><br>
    <strong style="color:#DC2626;">&#9654; {esc(ci.get('signal',''))}</strong>
  </div>
</td></tr>""")

        # Outlook
        outlook = doge.get("outlook", "")
        if outlook:
            h.append(f"""
<tr><td style="background:#FFFFFF;padding:8px 32px 16px;" class="cp card-bg">
  <div style="font-size:13px;color:#475569;line-height:1.7;padding:14px;background:#0F172A;border-radius:6px;color:#E2E8F0;">
    <strong style="color:#C9A227;">&#9654; Outlook:</strong> {esc(outlook)}
  </div>
</td></tr>""")

    # ════════════════════════════════════════════════════════════
    # 02 — RECOMPETE ALERTS (with winnability + who should pursue)
    # ════════════════════════════════════════════════════════════
    if recompetes:
        cur_sec += 1
        h.append(_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 12px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'Recompete Alerts')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">Contracts Expiring &mdash; Capture Starts Now</div>
  <div style="font-size:13px;color:#64748B;margin-top:4px;" class="ts">These agencies still need the work done. If you&rsquo;re in the right NAICS with past performance, start shaping.</div>
</td></tr>""")

        for r in recompetes:
            uc = urgency_color(r.get("urgency", ""))
            ubg = urgency_bg(r.get("urgency", ""))
            days = r.get("days_remaining", "?")
            u_label = "URGENT" if r.get("urgency") == "high" else "WATCH"
            wb = winnability_badge(r.get("winnability_score", ""))
            tenure = r.get("incumbent_tenure_years", "")
            tenure_str = f" &middot; {tenure}yr incumbent" if tenure else ""

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:4px 32px 16px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid {uc};border-radius:0 8px 8px 0;">
  <tr><td style="padding:20px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td><span style="display:inline-block;background:{uc};color:#FFF;font-size:10px;font-weight:800;padding:3px 10px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px;">{u_label} &middot; {days}d</span>&nbsp;{wb}</td>
      <td style="text-align:right;"><span style="font-size:22px;font-weight:800;color:{uc};">{esc(r.get('current_value','?'))}</span></td>
    </tr></table>
    <div style="font-size:16px;font-weight:700;color:#1E293B;margin-top:12px;" class="tp">{esc(r.get('contract_name',''))}</div>
    <div style="font-size:13px;color:#64748B;margin-top:4px;" class="ts">{esc(r.get('agency',''))} &middot; Incumbent: <strong>{esc(r.get('incumbent','?'))}</strong>{tenure_str}<br>NAICS {esc(r.get('naics','?'))} &middot; {esc(r.get('set_aside',''))} &middot; <em>{esc(r.get('solicitation_status','?'))}</em></div>""")

            # Intel
            h.append(f"""    <div style="font-size:13px;color:#475569;margin-top:12px;padding:12px 14px;background:{ubg};border-radius:6px;line-height:1.6;">
      <strong style="color:{uc};">&#9654; Intel:</strong> {esc(r.get('notable_detail',''))}
    </div>""")

            # Winnability factors
            factors = r.get("winnability_factors", [])
            if factors:
                h.append('<div style="margin-top:10px;padding:12px 14px;background:#F8FAFC;border-radius:6px;border:1px solid #E2E8F0;">')
                h.append('<div style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Winnability Analysis</div>')
                for wf in factors:
                    h.append(f'<div style="font-size:12px;color:#475569;line-height:1.6;padding:3px 0 3px 12px;border-left:2px solid #C9A227;">{esc(wf)}</div>')
                h.append('</div>')

            # Who should pursue
            wsp = r.get("who_should_pursue", [])
            if wsp:
                h.append('<div style="margin-top:10px;padding:12px 14px;background:#EFF6FF;border-radius:6px;">')
                h.append('<div style="font-size:11px;font-weight:700;color:#2563EB;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Who Should Pursue</div>')
                for w in wsp:
                    h.append(f'<div style="font-size:12px;color:#475569;line-height:1.6;margin-bottom:4px;">&#8227; {esc(w)}</div>')
                h.append('</div>')

            # Protest history
            protest = r.get("protest_history", "")
            if protest:
                h.append(f'<div style="font-size:12px;color:#64748B;margin-top:8px;font-style:italic;">&#9888; <strong>Protest History:</strong> {esc(protest)}</div>')

            h.append("</td></tr></table></td></tr>")

    # ════════════════════════════════════════════════════════════
    # 03 — NEW AWARDS (with why they won + market signal)
    # ════════════════════════════════════════════════════════════
    if new_awards:
        cur_sec += 1
        h.append(_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 12px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'New Awards')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">Who Won, Why They Won, and What It Means</div>
</td></tr>""")

        for a in new_awards:
            comps = a.get("competitors_known", [])
            comp_str = ", ".join(esc(c) for c in comps) if comps else "Not disclosed"

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:4px 32px 16px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid #16A34A;border-radius:0 8px 8px 0;">
  <tr><td style="padding:20px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td><span style="display:inline-block;background:#16A34A;color:#FFF;font-size:10px;font-weight:800;padding:3px 10px;border-radius:3px;text-transform:uppercase;">Awarded {esc(a.get('award_date',''))}</span></td>
      <td style="text-align:right;"><span style="font-size:22px;font-weight:800;color:#16A34A;">{esc(a.get('award_value','?'))}</span></td>
    </tr></table>
    <div style="font-size:16px;font-weight:700;color:#1E293B;margin-top:12px;" class="tp">{esc(a.get('contract_name',''))}</div>
    <div style="font-size:13px;color:#64748B;margin-top:4px;" class="ts">{esc(a.get('agency',''))} &middot; Winner: <strong style="color:#16A34A;">{esc(a.get('awardee','?'))}</strong><br>NAICS {esc(a.get('naics','?'))} &middot; {esc(a.get('set_aside',''))} &middot; {esc(a.get('period_of_performance',''))}<br>Also competed: {comp_str}</div>""")

            # Why they won
            why = a.get("why_they_won", "")
            if why:
                h.append(f'<div style="font-size:13px;color:#475569;margin-top:12px;padding:12px 14px;background:#F0FDF4;border-radius:6px;line-height:1.6;"><strong style="color:#16A34A;">&#9654; Why They Won:</strong> {esc(why)}</div>')

            # What losers should do
            losers = a.get("what_losers_should_do", "")
            if losers:
                h.append(f'<div style="font-size:13px;color:#475569;margin-top:8px;padding:12px 14px;background:#FEF2F2;border-radius:6px;line-height:1.6;"><strong style="color:#DC2626;">&#9654; If You Lost:</strong> {esc(losers)}</div>')

            # Market signal
            sig = a.get("market_signal", "")
            if sig:
                h.append(f'<div style="font-size:13px;color:#475569;margin-top:8px;padding:12px 14px;background:#FFFBEB;border-radius:6px;line-height:1.6;"><strong style="color:#D97706;">&#9654; Market Signal:</strong> {esc(sig)}</div>')

            h.append("</td></tr></table></td></tr>")

    # ════════════════════════════════════════════════════════════
    # 04 — OPTION EXERCISES (with recompete signals)
    # ════════════════════════════════════════════════════════════
    if options:
        cur_sec += 1
        h.append(_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 12px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'Option Exercises')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">Renewals &amp; Recompete Signals</div>
</td></tr>""")

        for o in options:
            opt_year = o.get("option_year", "")
            is_final = "final" in opt_year.lower() or "5 of 5" in opt_year.lower() or "4 of 4" in opt_year.lower()
            if not is_final and opt_year:
                parts = opt_year.lower().replace("option year", "").strip().split(" of ")
                if len(parts) == 2:
                    try:
                        is_final = int(parts[0].strip()) >= int(parts[1].strip()) - 1
                    except ValueError:
                        pass

            final_badge = ' <span style="display:inline-block;background:#DC2626;color:#FFF;font-size:10px;font-weight:700;padding:2px 8px;border-radius:3px;">RECOMPETE COMING</span>' if is_final else ''

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:4px 32px 12px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:0 8px 8px 0;">
  <tr><td style="padding:16px 20px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td><div style="font-size:15px;font-weight:700;color:#1E293B;" class="tp">{esc(o.get('contract_name',''))}</div>
      <div style="font-size:13px;color:#64748B;margin-top:3px;" class="ts">{esc(o.get('agency',''))} &middot; <strong>{esc(o.get('contractor',''))}</strong> &middot; {esc(opt_year)}{final_badge}</div></td>
      <td style="text-align:right;vertical-align:top;"><span style="font-size:18px;font-weight:800;color:#2563EB;">{esc(o.get('option_value','?'))}</span></td>
    </tr></table>""")

            detail = o.get("notable_detail", "")
            if detail:
                h.append(f'<div style="font-size:13px;color:#475569;margin-top:10px;padding:10px 14px;background:#EFF6FF;border-radius:6px;line-height:1.6;"><strong style="color:#2563EB;">&#9654; Intel:</strong> {esc(detail)}</div>')

            recomp_sig = o.get("recompete_signal", "")
            if recomp_sig:
                h.append(f'<div style="font-size:13px;color:#475569;margin-top:8px;padding:10px 14px;background:#FFFBEB;border-radius:6px;line-height:1.6;"><strong style="color:#D97706;">&#9654; Recompete Signal:</strong> {esc(recomp_sig)}</div>')

            wsw = o.get("who_should_watch", [])
            if wsw:
                h.append('<div style="margin-top:8px;padding:10px 14px;background:#F8FAFC;border-radius:6px;">')
                h.append('<div style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Who Should Watch</div>')
                for w in wsw:
                    h.append(f'<div style="font-size:12px;color:#475569;line-height:1.5;margin-bottom:3px;">&#8227; {esc(w)}</div>')
                h.append('</div>')

            h.append("</td></tr></table></td></tr>")

    # ════════════════════════════════════════════════════════════
    # 05 — FUNDING ACTIONS
    # ════════════════════════════════════════════════════════════
    if funding:
        cur_sec += 1
        h.append(_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 12px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'Funding Actions')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">Follow the Money</div>
</td></tr>""")

        for fi in funding:
            action = fi.get("action_type", "")
            ac = "#7C3AED" if "ceiling" in action.lower() else "#0891B2" if "task order" in action.lower() else "#64748B"

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:4px 32px 12px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #E2E8F0;border-left:4px solid {ac};border-radius:0 8px 8px 0;">
  <tr><td style="padding:16px 20px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td><span style="display:inline-block;background:{ac};color:#FFF;font-size:10px;font-weight:800;padding:2px 8px;border-radius:3px;text-transform:uppercase;">{esc(action)}</span>
      <div style="font-size:15px;font-weight:700;color:#1E293B;margin-top:8px;" class="tp">{esc(fi.get('contract_name',''))}</div>
      <div style="font-size:13px;color:#64748B;margin-top:3px;" class="ts">{esc(fi.get('agency',''))} &middot; {esc(fi.get('contractor',''))}</div></td>
      <td style="text-align:right;vertical-align:top;"><span style="font-size:18px;font-weight:800;color:{ac};">{esc(fi.get('modification_value','?'))}</span>""")
            nc = fi.get("new_ceiling")
            if nc:
                h.append(f'<div style="font-size:11px;color:#64748B;margin-top:2px;">Ceiling: {esc(nc)}</div>')
            h.append("</td></tr></table>")

            intel = fi.get("intel_note", "") or fi.get("notable_detail", "")
            if intel:
                h.append(f'<div style="font-size:13px;color:#475569;margin-top:10px;padding:10px 14px;background:#F5F3FF;border-radius:6px;line-height:1.6;"><strong style="color:{ac};">&#9654; Intel:</strong> {esc(intel)}</div>')

            h.append("</td></tr></table></td></tr>")

    # ════════════════════════════════════════════════════════════
    # 06 — MARKET PULSE
    # ════════════════════════════════════════════════════════════
    cur_sec += 1
    top_agencies = pulse.get("top_agencies_by_spend", [])
    trending = pulse.get("trending_naics", [])

    h.append(_divider())
    h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 8px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'Market Pulse')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">Where the Money Is Going</div>
</td></tr>
<tr><td style="background:#FFFFFF;padding:4px 32px 20px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;border-radius:8px;border-top:3px solid #C9A227;">
  <tr><td style="padding:24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td><div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;">Total Obligations</div>
      <div style="font-size:40px;font-weight:900;color:#FFF;letter-spacing:-1.5px;margin-top:4px;line-height:1;">{esc(pulse.get('total_obligations_week',''))}</div></td>
      <td style="text-align:right;vertical-align:bottom;"><span style="display:inline-block;background:#16A34A;color:#FFF;font-size:14px;font-weight:700;padding:6px 14px;border-radius:6px;">{esc(pulse.get('yoy_change',''))} YoY</span></td>
    </tr></table>""")

    if top_agencies:
        h.append('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;border-top:1px solid #1E293B;padding-top:14px;">')
        h.append('<tr><td colspan="2" style="padding-bottom:8px;"><div style="font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;">Top Agencies</div></td></tr>')
        for ag in top_agencies:
            trend = ag.get("trend", "")
            h.append(f'<tr><td style="padding:6px 0;font-size:13px;color:#E2E8F0;">{esc(ag.get("agency",""))}</td><td style="padding:6px 0;text-align:right;font-size:15px;font-weight:700;color:#FFF;">{esc(ag.get("amount",""))}</td></tr>')
            if trend:
                h.append(f'<tr><td colspan="2" style="padding:0 0 8px 0;font-size:11px;color:#94A3B8;line-height:1.5;">{esc(trend)}</td></tr>')
        h.append("</table>")

    if trending:
        h.append('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;border-top:1px solid #1E293B;padding-top:14px;">')
        h.append('<tr><td colspan="2" style="padding-bottom:8px;"><div style="font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;">Trending NAICS</div></td></tr>')
        for t in trending:
            insight = t.get("insight", "")
            h.append(f'<tr><td style="padding:4px 0;font-size:13px;color:#E2E8F0;">{esc(t.get("code",""))} &mdash; {esc(t.get("description",""))}</td><td style="padding:4px 0;text-align:right;font-size:14px;font-weight:700;color:#C9A227;">{esc(t.get("change",""))}</td></tr>')
            if insight:
                h.append(f'<tr><td colspan="2" style="padding:0 0 6px 0;font-size:11px;color:#94A3B8;line-height:1.5;">{esc(insight)}</td></tr>')
        h.append("</table>")

    h.append("</td></tr></table></td></tr>")

    # ════════════════════════════════════════════════════════════
    # ACTION ITEMS — What to do this week
    # ════════════════════════════════════════════════════════════
    if action_items:
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:16px 32px 12px;" class="cp card-bg">
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">&#9889; What to Do This Week</div>
  <div style="font-size:13px;color:#64748B;margin-top:2px;" class="ts">Specific actions ranked by urgency. Don&rsquo;t just read &mdash; act.</div>
</td></tr>""")

        for ai in action_items:
            pc = priority_color(ai.get("priority", ""))
            pl = priority_label(ai.get("priority", ""))
            deadline = ai.get("deadline", "")
            dl_str = f' &middot; Due {esc(deadline)}' if deadline else ""

            h.append(f"""
<tr><td style="background:#FFFFFF;padding:2px 32px 10px;" class="cp card-bg">
  <div style="padding:12px 14px;border-left:4px solid {pc};background:#F8FAFC;border-radius:0 6px 6px 0;">
    <div style="font-size:10px;font-weight:800;color:{pc};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">{pl}{dl_str}</div>
    <div style="font-size:14px;font-weight:700;color:#1E293B;line-height:1.4;" class="tp">{esc(ai.get('action',''))}</div>
    <div style="font-size:12px;color:#64748B;margin-top:4px;line-height:1.5;" class="ts">{esc(ai.get('context',''))}</div>
  </div>
</td></tr>""")

    # ════════════════════════════════════════════════════════════
    # ONE TO WATCH
    # ════════════════════════════════════════════════════════════
    if one_to_watch:
        cur_sec += 1
        h.append(_divider())
        h.append(f"""
<tr><td style="background:#FFFFFF;padding:20px 32px 12px;" class="cp card-bg">
  {_section_label(f'0{cur_sec}', 'One to Watch')}
  <div style="font-size:18px;font-weight:800;color:#1E293B;" class="tp">{esc(one_to_watch.get('headline',''))}</div>
  <div style="font-size:13px;color:#64748B;margin-top:4px;" class="ts">{esc(one_to_watch.get('agency',''))} &middot; Est. {esc(one_to_watch.get('estimated_value',''))}</div>
</td></tr>
<tr><td style="background:#FFFFFF;padding:0 32px 12px;" class="cp card-bg">
  <div style="font-size:14px;color:#475569;line-height:1.7;" class="ts">{esc(one_to_watch.get('description',''))}</div>
  <div style="font-size:13px;color:#475569;margin-top:12px;padding:14px;background:#FFFBEB;border-left:4px solid #C9A227;border-radius:0 6px 6px 0;line-height:1.6;">
    <strong style="color:#92400E;">Why It Matters:</strong> {esc(one_to_watch.get('why_it_matters',''))}
  </div>
</td></tr>""")

        actions = one_to_watch.get("what_to_do_now", [])
        if actions:
            h.append('<tr><td style="background:#FFFFFF;padding:0 32px 16px;" class="cp card-bg">')
            h.append('<div style="font-size:12px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Start Positioning Now</div>')
            for act in actions:
                h.append(f'<div style="font-size:13px;color:#475569;line-height:1.6;margin-bottom:6px;padding-left:14px;border-left:2px solid #C9A227;">&#8227; {esc(act)}</div>')
            h.append('</td></tr>')

    # ════════════════════════════════════════════════════════════
    # CTA
    # ════════════════════════════════════════════════════════════
    h.append(f"""
<tr><td style="background:#FFFFFF;padding:8px 32px 24px;" class="cp card-bg">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;border-radius:8px;">
  <tr><td style="padding:32px;text-align:center;">
    <div style="font-size:22px;font-weight:800;color:#FFF;margin-bottom:8px;">Stop wasting B&amp;P on proposals you can&rsquo;t win</div>
    <div style="font-size:14px;color:#94A3B8;margin-bottom:24px;line-height:1.6;">Get winnability scores, recompete alerts, and capture intelligence filtered to your NAICS codes &mdash; every Monday at 7am.</div>
    <!--[if mso]>
    <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="#" style="height:48px;v-text-anchor:middle;width:260px;" arcsize="13%" strokecolor="#C9A227" fillcolor="#C9A227">
    <w:anchorlock/><center style="color:#0F172A;font-family:sans-serif;font-size:15px;font-weight:bold;">Get Pro Intelligence &rarr;</center>
    </v:roundrect><![endif]-->
    <!--[if !mso]><!--><a href="#" style="display:inline-block;background:#C9A227;color:#0F172A;font-size:15px;font-weight:800;padding:14px 36px;border-radius:6px;text-decoration:none;">Get Pro Intelligence &rarr;</a><!--<![endif]-->
    <div style="font-size:12px;color:#64748B;margin-top:14px;">$249/year &middot; 14-day free trial &middot; Cancel anytime</div>
  </td></tr></table>
</td></tr>""")

    # ── FEEDBACK + FOOTER ──
    h.append("""
<tr><td style="background:#FFFFFF;padding:0 32px 16px;" class="cp card-bg">
  <div style="text-align:center;font-size:13px;color:#64748B;">Was this brief useful?&nbsp;
    <a href="#" style="text-decoration:none;font-size:16px;">&#128077;</a>&nbsp;
    <a href="#" style="text-decoration:none;font-size:16px;">&#128078;</a>&nbsp;&nbsp;
    <a href="#" style="color:#2563EB;text-decoration:none;font-size:13px;font-weight:600;">Forward to a colleague</a></div>
</td></tr>
<tr><td style="background:#FFFFFF;padding:16px 32px 24px;border-top:1px solid #E2E8F0;border-radius:0 0 12px 12px;" class="cp card-bg">
  <div style="text-align:center;">
    <div style="font-size:11px;font-weight:700;color:#C9A227;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">GovCon Weekly Intelligence</div>
    <div style="font-size:12px;color:#94A3B8;line-height:2;">
      Intelligence-driven federal contract analysis for capture professionals<br>
      Data: USAspending &middot; FPDS &middot; SAM.gov &middot; Agency budgets &middot; Court filings<br>
      <a href="#" style="color:#2563EB;text-decoration:none;">Unsubscribe</a> &middot;
      <a href="#" style="color:#2563EB;text-decoration:none;">Preferences</a> &middot;
      <a href="#" style="color:#2563EB;text-decoration:none;">View in Browser</a></div>
  </div>
</td></tr>""")

    h.append(_close_wrapper())
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
