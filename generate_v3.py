#!/usr/bin/env python3
"""Generate publication-quality GovCon Weekly Intelligence newsletter (v3)."""

import json, html, os
from datetime import datetime, date

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "corrected_all.json")
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "report_2026-03-18_v2.html")

with open(DATA_FILE) as f:
    data = json.load(f)

def e(text):
    return html.escape(str(text)) if text else ""

def fmt_money(val):
    if val is None: return ""
    if isinstance(val, str):
        val = val.replace("$","").replace(",","").replace("B","e9").replace("M","e6")
        try: val = float(val)
        except: return val
    if val >= 1_000_000_000: return f"${val/1_000_000_000:.1f}B"
    if val >= 1_000_000: return f"${val/1_000_000:.0f}M"
    return f"${val:,.0f}"

def urgency_dot(u):
    return {"high":"#EF4444","medium":"#F59E0B","low":"#10B981"}.get(u,"#6B7280")

def winnability_color(w):
    return {"high":"#10B981","medium":"#F59E0B","low":"#EF4444"}.get(w,"#6B7280")

def priority_style(p):
    return {
        "urgent": ("URGENT","#EF4444","#FEF2F2"),
        "this_week": ("THIS WEEK","#F59E0B","#FFFBEB"),
        "this_month": ("THIS MONTH","#3B82F6","#EFF6FF"),
    }.get(p, ("","#6B7280","#F9FAFB"))

def bar_color(val):
    if val >= 70: return "#10B981"
    if val >= 50: return "#F59E0B"
    return "#EF4444"

# ── Aliases ──
recompetes = data["sections"]["recompete_alerts"]["items"]
awards = data["sections"]["new_awards"]["items"]
options = data["sections"]["option_exercises"]["items"]
funding = data["sections"]["funding_actions"]["items"]
actions = data["action_items"]
doge = data["doge_tracker"]
notable = data["notable"]
market = data["market_pulse"]
otw = data["one_to_watch"]
health = data["govcon_health_index"]
wired = data["is_it_wired"]
bridge = data["bridge_watch"]
setaside = data["set_aside_spotlight"]
protest = data["protest_report"]
calendar = data["calendar"]

total_award_value = sum(a.get("award_value_raw",0) for a in awards)
urgent_count = sum(1 for a in actions if a["priority"]=="urgent")
report_date = data["report_date"]
report_title = data["report_title"]
report_subtitle = data["report_subtitle"]

H = []

# ════════════════════════════════════════════════════════════
# HTML Head + CSS
# ════════════════════════════════════════════════════════════
H.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(report_title)} | {e(report_subtitle)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --navy:#0F172A;--navy-light:#1E293B;--navy-mid:#334155;
  --gold:#C9A227;--gold-light:#E8D48B;--gold-dim:rgba(201,162,39,0.08);
  --white:#FFF;--off-white:#F8FAFC;
  --g50:#F9FAFB;--g100:#F3F4F6;--g200:#E5E7EB;--g300:#D1D5DB;
  --g400:#9CA3AF;--g500:#6B7280;--g600:#4B5563;--g700:#374151;--g800:#1F2937;
  --red:#DC2626;--red-lt:#FEF2F2;--red-bd:#FECACA;
  --green:#059669;--green-lt:#ECFDF5;--green-bd:#A7F3D0;
  --blue:#2563EB;--blue-lt:#EFF6FF;--blue-bd:#BFDBFE;
  --purple:#7C3AED;--purple-lt:#F5F3FF;--purple-bd:#DDD6FE;
  --amber:#D97706;--amber-lt:#FFFBEB;--amber-bd:#FDE68A;
  --fd:'Playfair Display',Georgia,serif;
  --fb:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
  --fm:'JetBrains Mono','SF Mono',Consolas,monospace;
}}
body{{background:var(--g50);color:var(--g800);font-family:var(--fb);font-size:15px;line-height:1.7;-webkit-font-smoothing:antialiased}}
.w{{max-width:680px;margin:0 auto;background:var(--white);box-shadow:0 1px 3px rgba(0,0,0,.06),0 8px 40px rgba(0,0,0,.04)}}
.c{{padding:0 32px}}
@media(max-width:700px){{.c{{padding:0 16px}}}}

/* Header */
.hdr{{background:var(--navy);padding:28px 32px 24px;text-align:center}}
.hdr-badge{{display:inline-block;font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:var(--gold);border:1px solid rgba(201,162,39,.3);padding:4px 14px;border-radius:3px;margin-bottom:14px}}
.hdr h1{{font-family:var(--fd);font-size:28px;font-weight:700;color:var(--white);letter-spacing:-.3px;margin-bottom:4px}}
.hdr .sub{{font-size:13px;color:var(--g400)}}
.hdr .gl{{width:60px;height:2px;background:var(--gold);margin:14px auto 0}}

/* Section dividers */
.sd{{display:flex;align-items:center;gap:14px;margin:36px 0 20px;padding-top:8px}}
.sn{{font-family:var(--fm);font-size:11px;font-weight:700;color:var(--gold);background:var(--gold-dim);border:1px solid rgba(201,162,39,.15);width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;flex-shrink:0}}
.sl{{font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g500)}}
.sln{{flex:1;height:1px;background:var(--g200)}}
.st{{font-family:var(--fd);font-size:22px;font-weight:700;color:var(--navy);margin-bottom:4px;letter-spacing:-.2px}}
.ss{{font-size:13px;color:var(--g500);margin-bottom:16px;line-height:1.5}}

/* Health gauge */
.hg{{background:var(--navy);border-radius:12px;padding:28px;margin-bottom:16px;text-align:center;position:relative;overflow:hidden}}
.hg::before{{content:'';position:absolute;top:-40%;left:50%;transform:translateX(-50%);width:200%;height:80%;background:radial-gradient(ellipse,rgba(201,162,39,.08) 0%,transparent 60%)}}
.hs{{font-family:var(--fd);font-size:72px;font-weight:800;color:var(--gold);line-height:1;position:relative}}
.hc{{font-family:var(--fm);font-size:14px;font-weight:600;position:relative}}
.hl{{font-family:var(--fm);font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:var(--g400);margin-top:8px;position:relative}}

/* Health bars */
.hb{{display:flex;align-items:center;gap:10px;margin-bottom:10px;font-size:13px}}
.hb-l{{width:140px;flex-shrink:0;font-weight:500;color:var(--g700)}}
.hb-t{{flex:1;height:8px;background:var(--g100);border-radius:4px;overflow:hidden}}
.hb-f{{height:100%;border-radius:4px}}
.hb-v{{width:32px;text-align:right;font-family:var(--fm);font-size:12px;font-weight:600}}

/* Hero stat */
.hero{{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-light) 100%);border-radius:12px;padding:32px;text-align:center;margin:24px 0;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:0;right:0;width:200px;height:200px;background:radial-gradient(circle,rgba(201,162,39,.1) 0%,transparent 70%)}}
.hero .num{{font-family:var(--fd);font-size:56px;font-weight:800;color:var(--gold);line-height:1;letter-spacing:-2px;position:relative}}
.hero .lbl{{font-family:var(--fm);font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:var(--gold-light);margin-top:8px;position:relative}}
.hero .ctx{{font-size:14px;color:rgba(255,255,255,.7);margin-top:14px;line-height:1.6;max-width:500px;margin-left:auto;margin-right:auto;position:relative}}

/* KPI bar */
.kpi{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--g200);border:1px solid var(--g200);border-radius:10px;overflow:hidden;margin-bottom:28px}}
.kpi-i{{background:var(--white);padding:16px 12px;text-align:center}}
.kpi-v{{font-family:var(--fd);font-size:22px;font-weight:700;color:var(--navy)}}
.kpi-l{{font-family:var(--fm);font-size:9px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--g400);margin-top:2px}}

/* TOC */
.toc{{background:var(--off-white);border:1px solid var(--g200);border-radius:10px;padding:20px 24px;margin-bottom:28px}}
.toc-t{{font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g400);margin-bottom:12px}}
.toc-g{{display:grid;grid-template-columns:1fr 1fr;gap:6px 24px}}
.toc-i{{font-size:13px;color:var(--g600);display:flex;align-items:center;gap:8px;text-decoration:none;padding:3px 0}}
.toc-i:hover{{color:var(--navy)}}
.toc-n{{font-family:var(--fm);font-size:10px;font-weight:600;color:var(--gold);width:20px}}

/* Cards */
.cd{{border:1px solid var(--g200);border-radius:10px;padding:20px;margin-bottom:16px;background:var(--white);transition:box-shadow .2s}}
.cd:hover{{box-shadow:0 2px 8px rgba(0,0,0,.04)}}
.cd-r{{border-left:4px solid var(--red)}}
.cd-g{{border-left:4px solid var(--green)}}
.cd-b{{border-left:4px solid var(--blue)}}
.cd-p{{border-left:4px solid var(--purple)}}
.cd-a{{border-left:4px solid var(--amber)}}
.cd-gd{{border-left:4px solid var(--gold)}}
.cd-h{{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:10px}}
.cd-t{{font-family:var(--fd);font-size:17px;font-weight:700;color:var(--navy);line-height:1.3}}
.cd-ag{{font-family:var(--fm);font-size:11px;font-weight:500;color:var(--g500);margin-top:2px}}

/* Badges */
.bg{{font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:.5px;padding:3px 10px;border-radius:4px;white-space:nowrap;display:inline-flex;align-items:center;gap:4px}}
.bg-u{{background:var(--red-lt);color:var(--red);border:1px solid var(--red-bd)}}
.bg-m{{background:var(--amber-lt);color:var(--amber);border:1px solid var(--amber-bd)}}
.bg-l{{background:var(--green-lt);color:var(--green);border:1px solid var(--green-bd)}}
.bg-hw{{background:var(--green-lt);color:var(--green);border:1px solid var(--green-bd)}}
.bg-mw{{background:var(--amber-lt);color:var(--amber);border:1px solid var(--amber-bd)}}
.bg-lw{{background:var(--red-lt);color:var(--red);border:1px solid var(--red-bd)}}
.bg-d{{background:var(--navy);color:var(--gold);font-size:11px;font-weight:700;padding:4px 10px}}
.bg-n{{background:var(--blue-lt);color:var(--blue);border:1px solid var(--blue-bd)}}

/* Meta row */
.mr{{display:flex;flex-wrap:wrap;gap:6px 16px;margin:8px 0}}
.mi{{font-size:12px;color:var(--g500)}}
.mi strong{{color:var(--g700);font-weight:600}}

/* Callouts */
.co{{padding:14px 16px;border-radius:8px;margin:12px 0;font-size:13px;line-height:1.6}}
.co-l{{font-family:var(--fm);font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px}}
.co-g{{background:var(--green-lt);border:1px solid var(--green-bd)}}.co-g .co-l{{color:var(--green)}}
.co-r{{background:var(--red-lt);border:1px solid var(--red-bd)}}.co-r .co-l{{color:var(--red)}}
.co-b{{background:var(--blue-lt);border:1px solid var(--blue-bd)}}.co-b .co-l{{color:var(--blue)}}
.co-a{{background:var(--amber-lt);border:1px solid var(--amber-bd)}}.co-a .co-l{{color:var(--amber)}}
.co-p{{background:var(--purple-lt);border:1px solid var(--purple-bd)}}.co-p .co-l{{color:var(--purple)}}
.co-n{{background:rgba(15,23,42,.04);border:1px solid rgba(15,23,42,.1)}}.co-n .co-l{{color:var(--navy)}}

/* Collapsible */
details.ex{{margin:8px 0;border:1px solid var(--g200);border-radius:8px;overflow:hidden}}
details.ex summary{{padding:10px 14px;font-family:var(--fm);font-size:11px;font-weight:600;color:var(--g600);cursor:pointer;list-style:none;background:var(--g50);display:flex;align-items:center;gap:6px;transition:background .15s}}
details.ex summary:hover{{background:var(--g100)}}
details.ex summary::-webkit-details-marker{{display:none}}
details.ex summary::before{{content:'\\25B8';font-size:10px;color:var(--g400);transition:transform .15s}}
details.ex[open] summary::before{{transform:rotate(90deg)}}
details.ex .xb{{padding:12px 14px;font-size:13px;line-height:1.6;color:var(--g600);border-top:1px solid var(--g200)}}

/* Wired cards */
.wc{{background:var(--navy);border-radius:10px;padding:20px;margin-bottom:16px;color:var(--white)}}
.wsd{{display:flex;align-items:center;gap:16px;margin-bottom:14px}}
.wsc{{width:64px;height:64px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:var(--fd);font-size:28px;font-weight:800;flex-shrink:0}}
.wsr{{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:12px}}
.wsr:last-child{{border-bottom:none}}

/* Bridge */
.bc{{border:2px dashed var(--amber-bd);background:var(--amber-lt);border-radius:10px;padding:18px;margin-bottom:14px}}

/* Market panel */
.mp{{background:var(--navy);border-radius:12px;padding:24px;margin:16px 0;color:var(--white)}}
.mp h3{{font-family:var(--fd);font-size:18px;color:var(--gold);margin-bottom:16px}}
.mp-r{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px}}
.mp-r:last-child{{border-bottom:none}}

/* Action items */
.ai{{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid var(--g100)}}
.ai:last-child{{border-bottom:none}}

/* Calendar */
.ci{{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--g100);font-size:13px}}
.ci:last-child{{border-bottom:none}}

/* Protest stats */
.ps{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--g200);border:1px solid var(--g200);border-radius:10px;overflow:hidden;margin-bottom:16px}}
.ps-i{{background:var(--white);padding:14px;text-align:center}}
.ps-v{{font-family:var(--fd);font-size:24px;font-weight:700;color:var(--navy)}}
.ps-l{{font-family:var(--fm);font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--g400);margin-top:2px}}

/* Set-aside table */
.sat{{width:100%;border-collapse:collapse;font-size:13px;margin:12px 0}}
.sat th{{font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--g400);text-align:left;padding:8px 10px;border-bottom:2px solid var(--g200)}}
.sat td{{padding:10px;border-bottom:1px solid var(--g100);vertical-align:top}}
.sat td.nm{{text-align:right;font-family:var(--fm);font-weight:600}}

/* OTW + CTA */
.otw{{background:linear-gradient(135deg,#1a1a2e 0%,var(--navy) 100%);border-radius:12px;padding:28px;color:var(--white);margin:16px 0}}
.otw h3{{font-family:var(--fd);font-size:20px;color:var(--gold);margin-bottom:4px}}
.cta{{background:var(--gold);border-radius:12px;padding:28px;text-align:center;margin:28px 0}}
.cta h3{{font-family:var(--fd);font-size:22px;color:var(--navy);margin-bottom:6px}}
.cta-b{{display:inline-block;background:var(--navy);color:var(--gold);font-family:var(--fm);font-size:12px;font-weight:600;letter-spacing:1px;text-transform:uppercase;padding:12px 32px;border-radius:6px;text-decoration:none}}

/* Feedback + Footer */
.fb-row{{display:flex;justify-content:center;gap:24px;padding:20px 0;border-top:1px solid var(--g200);border-bottom:1px solid var(--g200);margin:20px 0}}
.fb-btn{{font-size:13px;color:var(--g500);text-decoration:none;display:flex;align-items:center;gap:6px;padding:6px 14px;border:1px solid var(--g200);border-radius:6px;transition:all .15s}}
.fb-btn:hover{{background:var(--g50);color:var(--navy);border-color:var(--g300)}}
.ftr{{background:var(--navy);padding:24px 32px;text-align:center}}
.ftr p{{font-size:12px;color:var(--g400);line-height:1.6}}
.ftr .gld{{color:var(--gold)}}

/* Lists */
.il{{list-style:none;padding:0;margin:8px 0}}
.il li{{padding:4px 0 4px 16px;position:relative;font-size:13px;line-height:1.6;color:var(--g600)}}
.il li::before{{content:'\\203A';position:absolute;left:0;color:var(--gold);font-weight:700;font-size:16px}}

@media(max-width:500px){{
  .kpi{{grid-template-columns:repeat(2,1fr)}}
  .toc-g{{grid-template-columns:1fr}}
  .ps{{grid-template-columns:1fr}}
  .wsd{{flex-direction:column;text-align:center}}
  .cd-h{{flex-direction:column}}
}}
</style>
</head>
<body>
<div class="w">
""")

# ── HEADER ──
H.append(f"""
<div class="hdr">
  <div class="hdr-badge">Premium Intelligence Brief</div>
  <h1>{e(report_title)}</h1>
  <div class="sub">{e(report_subtitle)} &middot; {e(report_date)}</div>
  <div class="gl"></div>
</div>
<div class="c">
""")

# ════════════════════════════════════════════════════════════
# 01 - GovCon Health Index
# ════════════════════════════════════════════════════════════
score = health.get("current_score", health.get("score", 62))
prev = health.get("previous_score", 68)
change = health.get("change", score - prev)
chg_icon = "&#9660;" if change < 0 else "&#9650;"
chg_color = "#EF4444" if change < 0 else "#10B981"

H.append(f"""
<div class="sd"><span class="sn">01</span><span class="sl">GovCon Health Index</span><span class="sln"></span></div>
<div class="hg">
  <div class="hs">{score}</div>
  <div class="hc" style="color:{chg_color};">{chg_icon} {abs(change)} from {prev}</div>
  <div class="hl">Federal Procurement Health &middot; March 2026</div>
</div>
<p style="font-size:14px;color:var(--g600);margin-bottom:16px;line-height:1.6;">{e(health.get('interpretation',''))}</p>
""")

for comp in health.get("components", []):
    val = comp.get("score", comp.get("value", 50))
    c = bar_color(val)
    w = comp.get("weight", "")
    H.append(f"""<div class="hb">
  <span class="hb-l">{e(comp['name'])} <span style="color:var(--g400);font-size:11px;">({e(w)})</span></span>
  <div class="hb-t"><div class="hb-f" style="width:{val}%;background:{c};"></div></div>
  <span class="hb-v" style="color:{c};">{val}</span>
</div>""")

H.append('<details class="ex" style="margin-top:12px;"><summary>Component Details</summary><div class="xb">')
for comp in health.get("components", []):
    H.append(f"<p style='margin-bottom:8px;'><strong>{e(comp['name'])}:</strong> {e(comp.get('detail',''))}</p>")
H.append("</div></details>")

# ════════════════════════════════════════════════════════════
# 02 - Number of the Week
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s02"><span class="sn">02</span><span class="sl">Number of the Week</span><span class="sln"></span></div>
<div class="hero">
  <div class="num">{e(notable['key_stat'])}</div>
  <div class="lbl">{e(notable['key_stat_label'])}</div>
  <div class="ctx">{e(notable['summary'])}</div>
</div>
""")

# ── KPI Bar ──
H.append(f"""
<div class="kpi">
  <div class="kpi-i"><div class="kpi-v">{len(recompetes)}</div><div class="kpi-l">Recompetes</div></div>
  <div class="kpi-i"><div class="kpi-v">{fmt_money(total_award_value)}</div><div class="kpi-l">Awarded</div></div>
  <div class="kpi-i"><div class="kpi-v">{len(doge['agencies_affected'])}</div><div class="kpi-l">DOGE Agencies</div></div>
  <div class="kpi-i"><div class="kpi-v" style="color:var(--red);">{urgent_count}</div><div class="kpi-l">Urgent Actions</div></div>
</div>
""")

# ── TOC ──
toc_items = [
    ("01","Health Index"),("02","Number of the Week"),("03","DOGE Tracker"),
    ("04","Is It Wired?"),("05","Bridge Watch"),("06","Recompete Alerts"),
    ("07","New Awards"),("08","Option Exercises"),("09","Funding Actions"),
    ("10","Set-Aside Spotlight"),("11","Protest Report"),("12","Market Pulse"),
    ("13","Action Items"),("14","Calendar"),("15","One to Watch")
]
H.append('<div class="toc"><div class="toc-t">In This Issue</div><div class="toc-g">')
for num, label in toc_items:
    H.append(f'<a class="toc-i" href="#s{num}"><span class="toc-n">{num}</span> {label}</a>')
H.append('</div></div>')

# ════════════════════════════════════════════════════════════
# 03 - DOGE Tracker
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s03"><span class="sn">03</span><span class="sl">DOGE Tracker</span><span class="sln"></span></div>
<div class="st">DOGE Disruption Monitor</div>
<div class="ss">{e(doge['headline'])}</div>
""")

for ag in doge["agencies_affected"]:
    is_growing = "GROWING" in ag.get("action","")
    dot_color = "#10B981" if is_growing else "#EF4444"
    H.append(f"""<div class="cd" style="padding:16px;margin-bottom:12px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
    <span style="width:8px;height:8px;border-radius:50%;background:{dot_color};display:inline-block;"></span>
    <strong style="font-size:14px;color:var(--navy);">{e(ag['agency'])}</strong>
    <span style="font-family:var(--fm);font-size:11px;color:var(--g500);">{e(ag['action'])}</span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin-bottom:6px;">{e(ag['impact'])}</p>
  <p style="font-size:12px;color:var(--g500);font-style:italic;">{e(ag['status'])}</p>
</div>""")

# Court rulings
H.append('<div style="margin-top:16px;"><div style="font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g400);margin-bottom:10px;">Court Rulings</div>')
for cr in doge.get("court_rulings",[]):
    H.append(f"""<div class="co co-n" style="margin-bottom:10px;">
  <div class="co-l">{e(cr['case'])}</div>
  <p style="font-size:13px;margin-bottom:4px;"><strong>{e(cr['ruling'])}</strong></p>
  <p style="font-size:12px;color:var(--g500);">{e(cr['practical_impact'])}</p>
</div>""")
H.append('</div>')

# Contractor impact
H.append('<div style="margin-top:16px;"><div style="font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g400);margin-bottom:10px;">Contractor Impact</div>')
for ci in doge.get("contractor_impact",[]):
    H.append(f"""<div class="cd cd-r" style="padding:14px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:6px;">
    <strong style="color:var(--navy);">{e(ci['contractor'])}</strong>
    <span class="bg bg-u">{e(ci['exposure'])}</span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin-bottom:4px;">{e(ci['status'])}</p>
  <p style="font-size:12px;color:var(--g500);font-weight:500;">{e(ci['signal'])}</p>
</div>""")
H.append('</div>')

# Outlook
H.append(f"""<div class="co co-a" style="margin-top:16px;">
  <div class="co-l">Outlook</div>
  <p style="font-size:13px;">{e(doge['outlook'])}</p>
</div>""")

# ════════════════════════════════════════════════════════════
# 04 - Is It Wired?
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s04"><span class="sn">04</span><span class="sl">Is It Wired?</span><span class="sln"></span></div>
<div class="st">&ldquo;Is It Wired?&rdquo; Scorecard</div>
<div class="ss">{e(wired.get('subtitle', wired.get('intro', '')))}</div>
""")

if wired.get("methodology_note"):
    H.append(f'<p style="font-size:12px;color:var(--g500);margin-bottom:16px;font-style:italic;">{e(wired["methodology_note"])}</p>')

for item in wired.get("items", []):
    sc = item.get("wired_score", 50)
    verdict = item.get("verdict", "")
    if sc >= 70: ring_bg="rgba(239,68,68,.2)"; ring_border="#EF4444"
    elif sc >= 50: ring_bg="rgba(245,158,11,.2)"; ring_border="#F59E0B"
    else: ring_bg="rgba(16,185,129,.2)"; ring_border="#10B981"

    verdict_color = ring_border
    est_val = item.get("estimated_value", "")
    posted = item.get("posted_date", "")
    deadline = item.get("response_deadline", "")

    H.append(f"""<div class="wc">
  <div class="wsd">
    <div class="wsc" style="background:{ring_bg};border:3px solid {ring_border};color:{ring_border};">{sc}</div>
    <div>
      <div style="font-family:var(--fd);font-size:17px;font-weight:700;">{e(item.get('solicitation',''))}</div>
      <div style="font-family:var(--fm);font-size:11px;color:var(--g400);margin-top:2px;">{e(item.get('agency',''))}</div>
      <div style="font-family:var(--fm);font-size:11px;font-weight:700;color:{verdict_color};margin-top:4px;">{e(verdict)}</div>
    </div>
  </div>""")

    if est_val or posted or deadline:
        H.append(f'<div class="mr" style="margin-bottom:10px;">')
        if est_val: H.append(f'<span class="mi" style="color:var(--g400);"><strong style="color:var(--g300);">Est. Value:</strong> {e(est_val)}</span>')
        if posted: H.append(f'<span class="mi" style="color:var(--g400);"><strong style="color:var(--g300);">Posted:</strong> {e(posted)}</span>')
        if deadline: H.append(f'<span class="mi" style="color:var(--g400);"><strong style="color:var(--g300);">Deadline:</strong> {e(deadline)}</span>')
        H.append('</div>')

    for sig in item.get("signals", []):
        finding = sig.get("finding", sig.get("value", ""))
        red_flag = sig.get("red_flag", False)
        impact = sig.get("score_impact", "")
        flag_indicator = '<span style="color:#EF4444;">&#9679;</span>' if red_flag else '<span style="color:#10B981;">&#9679;</span>'
        H.append(f"""  <div class="wsr">
    <span style="color:var(--g400);">{flag_indicator} {e(sig.get('signal',''))}</span>
    <span style="color:var(--g300);font-weight:500;">{e(finding)}</span>
  </div>""")

    exception = item.get("exception", item.get("bottom_line", ""))
    if exception:
        H.append(f"""  <div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,.08);font-size:13px;color:var(--g300);line-height:1.6;">
    <strong style="color:var(--gold);">Bottom Line:</strong> {e(exception)}
  </div>""")

    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 05 - Bridge Watch
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s05"><span class="sn">05</span><span class="sl">Bridge Watch</span><span class="sln"></span></div>
<div class="st">Bridge Contract Watch</div>
<div class="ss">{e(bridge.get('subtitle', bridge.get('intro', '')))}</div>
""")

for b in bridge.get("items", []):
    ws = b.get("wired_score", 50)
    if ws >= 60: ws_label="LEANING WIRED"; ws_color="#EF4444"
    elif ws >= 40: ws_label="TOSS-UP"; ws_color="#F59E0B"
    else: ws_label="WIDE OPEN"; ws_color="#10B981"

    bridge_val = b.get("bridge_value", "")
    bridge_per = b.get("bridge_period", b.get("bridge_duration", ""))
    pred_val = b.get("predecessor_value", b.get("original_contract_value", ""))
    recomp = b.get("recompete_signal", b.get("recompete_timeline", ""))
    action = b.get("what_to_do", b.get("opportunity", ""))

    H.append(f"""<div class="bc">
  <div class="cd-h">
    <div>
      <div class="cd-t" style="font-size:16px;">{e(b.get('contract_name',''))}</div>
      <div class="cd-ag">{e(b.get('agency',''))} &middot; Incumbent: {e(b.get('incumbent',''))}</div>
    </div>
    <span class="bg bg-d">{e(bridge_per)}</span>
  </div>
  <div class="mr">
    <span class="mi"><strong>Bridge:</strong> {e(bridge_val)}</span>
    <span class="mi"><strong>Original:</strong> {e(pred_val)}</span>
    <span class="mi"><strong>Wired Score:</strong> <span style="color:{ws_color};font-weight:600;">{ws}/100 ({ws_label})</span></span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin:8px 0;"><strong>Recompete Signal:</strong> {e(recomp)}</p>""")

    if action:
        H.append(f"""<div class="co co-g" style="margin-top:10px;">
    <div class="co-l">What To Do</div>
    <p style="font-size:13px;">{e(action)}</p>
  </div>""")

    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 06 - Recompete Alerts
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s06"><span class="sn">06</span><span class="sl">Recompete Alerts</span><span class="sln"></span></div>
<div class="st">{e(data['sections']['recompete_alerts']['title'])}</div>
<div class="ss">{e(data['sections']['recompete_alerts']['subtitle'])}</div>
""")

for r in recompetes:
    win = r.get("winnability_score","").lower()
    win_cls = {"high":"bg-hw","medium":"bg-mw","low":"bg-lw"}.get(win,"bg-mw")
    days = r.get("days_remaining","?")

    H.append(f"""<div class="cd cd-r">
  <div class="cd-h">
    <div><div class="cd-t">{e(r['contract_name'])}</div><div class="cd-ag">{e(r['agency'])}</div></div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;">
      <span class="bg bg-d">{days}d</span>
      <span class="bg {win_cls}">{win.upper()} WIN</span>
    </div>
  </div>
  <div class="mr">
    <span class="mi"><strong>Incumbent:</strong> {e(r['incumbent'])}</span>
    <span class="mi"><strong>Value:</strong> {e(r['current_value'])}</span>
    <span class="mi"><strong>NAICS:</strong> {e(r['naics'])}</span>
    <span class="mi"><strong>Set-Aside:</strong> {e(r['set_aside'])}</span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin:8px 0;">{e(r['notable_detail'])}</p>
  <p style="font-size:12px;color:var(--g500);margin-bottom:6px;"><strong>Status:</strong> {e(r['solicitation_status'])}</p>""")

    if r.get("winnability_factors"):
        H.append('<details class="ex"><summary>Winnability Analysis</summary><div class="xb"><ul class="il">')
        for f in r["winnability_factors"]: H.append(f"<li>{e(f)}</li>")
        H.append("</ul></div></details>")
    if r.get("protest_history"):
        H.append(f'<details class="ex"><summary>Protest History</summary><div class="xb"><p>{e(r["protest_history"])}</p></div></details>')
    if r.get("who_should_pursue"):
        H.append('<details class="ex"><summary>Who Should Pursue</summary><div class="xb"><ul class="il">')
        for w in r["who_should_pursue"]: H.append(f"<li>{e(w)}</li>")
        H.append("</ul></div></details>")
    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 07 - New Awards
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s07"><span class="sn">07</span><span class="sl">New Awards</span><span class="sln"></span></div>
<div class="st">{e(data['sections']['new_awards']['title'])}</div>
<div class="ss">{e(data['sections']['new_awards']['subtitle'])}</div>
""")

for a in awards:
    H.append(f"""<div class="cd cd-g">
  <div class="cd-h">
    <div><div class="cd-t">{e(a['contract_name'])}</div><div class="cd-ag">{e(a['agency'])}</div></div>
    <span class="bg bg-n">{fmt_money(a.get('award_value_raw',0))}</span>
  </div>
  <div class="mr">
    <span class="mi"><strong>Awardee:</strong> {e(a['awardee'])}</span>
    <span class="mi"><strong>Period:</strong> {e(a['period_of_performance'])}</span>
    <span class="mi"><strong>NAICS:</strong> {e(a['naics'])}</span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin:8px 0;">{e(a['notable_detail'])}</p>""")

    if a.get("why_they_won"):
        H.append(f'<div class="co co-g"><div class="co-l">Why They Won</div><p style="font-size:13px;">{e(a["why_they_won"])}</p></div>')
    if a.get("what_losers_should_do"):
        H.append(f'<div class="co co-r"><div class="co-l">If You Lost</div><p style="font-size:13px;">{e(a["what_losers_should_do"])}</p></div>')
    if a.get("market_signal"):
        H.append(f'<div class="co co-b"><div class="co-l">Market Signal</div><p style="font-size:13px;">{e(a["market_signal"])}</p></div>')
    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 08 - Option Exercises
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s08"><span class="sn">08</span><span class="sl">Option Exercises</span><span class="sln"></span></div>
<div class="st">{e(data['sections']['option_exercises']['title'])}</div>
<div class="ss">{e(data['sections']['option_exercises']['subtitle'])}</div>
""")

for o in options:
    H.append(f"""<div class="cd cd-b">
  <div class="cd-h">
    <div><div class="cd-t">{e(o['contract_name'])}</div><div class="cd-ag">{e(o['agency'])} &middot; {e(o['contractor'])}</div></div>
    <span class="bg bg-m">{e(o['option_year'])}</span>
  </div>
  <div class="mr">
    <span class="mi"><strong>Option Value:</strong> {e(o['option_value'])}</span>
    <span class="mi"><strong>Base Contract:</strong> {e(o['base_contract_value'])}</span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin:8px 0;">{e(o['notable_detail'])}</p>""")

    if o.get("recompete_signal"):
        H.append(f'<div class="co co-b"><div class="co-l">Recompete Signal</div><p style="font-size:13px;">{e(o["recompete_signal"])}</p></div>')
    if o.get("who_should_watch"):
        H.append('<details class="ex"><summary>Who Should Watch</summary><div class="xb"><ul class="il">')
        for w in o["who_should_watch"]: H.append(f"<li>{e(w)}</li>")
        H.append("</ul></div></details>")
    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 09 - Funding Actions
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s09"><span class="sn">09</span><span class="sl">Funding Actions</span><span class="sln"></span></div>
<div class="st">{e(data['sections']['funding_actions']['title'])}</div>
<div class="ss">{e(data['sections']['funding_actions']['subtitle'])}</div>
""")

for fi in funding:
    tc = {"Ceiling Increase":("cd-p","var(--purple)"),"New Task Order":("cd-a","var(--amber)"),"Incremental Funding":("cd-b","var(--blue)")}.get(fi.get("action_type",""),("cd-b","var(--blue)"))
    H.append(f"""<div class="cd {tc[0]}">
  <div class="cd-h">
    <div><div class="cd-t" style="font-size:16px;">{e(fi['contract_name'])}</div><div class="cd-ag">{e(fi['agency'])} &middot; {e(fi['contractor'])}</div></div>
    <div style="text-align:right;">
      <span style="font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:{tc[1]};">{e(fi['action_type'])}</span>
      <div style="font-family:var(--fd);font-size:18px;font-weight:700;color:var(--navy);margin-top:2px;">{e(fi['modification_value'])}</div>
    </div>
  </div>""")
    if fi.get("new_ceiling"):
        H.append(f'<p style="font-size:12px;color:var(--g500);margin-bottom:6px;"><strong>New Ceiling:</strong> {e(fi["new_ceiling"])}</p>')
    H.append(f'<p style="font-size:13px;color:var(--g600);margin:6px 0;">{e(fi["notable_detail"])}</p>')
    if fi.get("intel_note"):
        H.append(f'<div class="co co-n"><div class="co-l">Intel Note</div><p style="font-size:13px;">{e(fi["intel_note"])}</p></div>')
    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 10 - Set-Aside Spotlight
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s10"><span class="sn">10</span><span class="sl">Set-Aside Spotlight</span><span class="sln"></span></div>
<div class="st">Set-Aside Spotlight</div>
<div class="ss">{e(setaside.get('subtitle', setaside.get('intro', '')))}</div>
""")

gw = setaside["government_wide"]
gw_color = "#10B981" if "Meeting" in gw.get("status","") else "#F59E0B"
H.append(f"""<div class="co co-a" style="margin-bottom:16px;">
  <div class="co-l">Government-Wide Small Business Goal</div>
  <p style="font-size:14px;margin-bottom:4px;"><strong style="font-size:18px;">{e(gw.get('sb_actual',''))}</strong> actual vs <strong>{e(gw.get('sb_goal',''))}</strong> goal &mdash; <span style="color:{gw_color};font-weight:600;">{e(gw.get('status',''))}</span></p>
</div>""")

underperformers = setaside.get("underperforming_agencies", setaside.get("underperformers", []))
if underperformers:
    H.append("""<div style="font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g400);margin:16px 0 8px;">Agency Shortfalls</div>
<div style="overflow-x:auto;"><table class="sat">
<thead><tr><th>Agency</th><th>Category</th><th>Goal</th><th>Actual</th><th>Gap</th><th style="text-align:right;">$ Gap</th></tr></thead><tbody>""")
    for up in underperformers:
        gap_str = up.get("gap", "0")
        gap_val = float(gap_str.replace("pp","").replace("%","").strip()) if gap_str else 0
        bar_w = min(gap_val * 40, 100)
        H.append(f"""<tr>
  <td><strong>{e(up.get('agency',''))}</strong></td>
  <td>{e(up.get('category',''))}</td>
  <td class="nm">{e(up.get('goal',''))}</td>
  <td class="nm" style="color:var(--red);">{e(up.get('actual',''))}</td>
  <td><span style="display:inline-block;height:6px;border-radius:3px;background:var(--red);vertical-align:middle;margin-right:6px;width:{bar_w}px;"></span>{e(gap_str)}</td>
  <td class="nm" style="color:var(--red);font-weight:600;">{e(up.get('dollar_gap',''))}</td>
</tr>""")
    H.append("</tbody></table></div>")

    for up in underperformers:
        if up.get("action"):
            H.append(f'<details class="ex"><summary>{e(up.get("agency",""))} &mdash; {e(up.get("category",""))} Action</summary><div class="xb"><p>{e(up["action"])}</p></div></details>')

upcoming = setaside.get("upcoming_set_aside_opportunities", setaside.get("upcoming_set_asides", []))
if upcoming:
    H.append('<div style="font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g400);margin:20px 0 10px;">Upcoming Set-Aside Opportunities</div>')
    for opp in upcoming:
        sa_type = opp.get("set_aside", opp.get("type", ""))
        first_word = sa_type.split()[0] if sa_type else ""
        sc = {"HUBZone":("#7C3AED","var(--purple-lt)","var(--purple-bd)"),"WOSB":("#2563EB","var(--blue-lt)","var(--blue-bd)"),"SDB":("#D97706","var(--amber-lt)","var(--amber-bd)"),"SDVOSB":("#059669","var(--green-lt)","var(--green-bd)")}.get(first_word,("#6B7280","var(--g50)","var(--g200)"))
        timeline = opp.get("expected_date", opp.get("timeline", ""))
        naics = opp.get("naics", "")
        H.append(f"""<div class="cd" style="padding:14px;border-left:3px solid {sc[0]};">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
    <div>
      <div style="font-weight:600;font-size:14px;color:var(--navy);">{e(opp.get('title',''))}</div>
      <div style="font-family:var(--fm);font-size:11px;color:var(--g500);margin-top:2px;">{f'NAICS {e(naics)} &middot; ' if naics else ''}Est. {e(opp.get('est_value',''))}</div>
    </div>
    <span class="bg" style="background:{sc[1]};color:{sc[0]};border:1px solid {sc[2]};">{e(sa_type)}</span>
  </div>
  <p style="font-size:12px;color:var(--g500);margin-top:6px;">{e(timeline)}</p>
</div>""")

# ════════════════════════════════════════════════════════════
# 11 - Protest Report
# ════════════════════════════════════════════════════════════
ps = protest["week_stats"]
H.append(f"""
<div class="sd" id="s11"><span class="sn">11</span><span class="sl">Protest Report</span><span class="sln"></span></div>
<div class="st">GAO Protest Report</div>
<div class="ss">Weekly digest with BD implications -- not legal analysis.</div>

<div class="ps">
  <div class="ps-i"><div class="ps-v">{ps.get('filed','')}</div><div class="ps-l">Filed</div></div>
  <div class="ps-i"><div class="ps-v" style="color:var(--red);">{ps.get('sustained','')}</div><div class="ps-l">Sustained</div></div>
  <div class="ps-i"><div class="ps-v">{ps.get('sustain_rate','')}</div><div class="ps-l">Sustain Rate</div></div>
</div>
<p style="font-size:12px;color:var(--g500);margin-bottom:16px;text-align:center;">{ps.get('decided','')} decided &middot; {ps.get('denied','')} denied &middot; {ps.get('dismissed','')} dismissed</p>
""")

notable_decisions = protest.get("notable_decisions", protest.get("notable", []))
for pn in notable_decisions:
    outcome = pn.get("outcome", pn.get("status", ""))
    outcome_upper = outcome.upper() if outcome else ""
    if "SUSTAIN" in outcome_upper: stc = ("var(--red)","var(--red-lt)","var(--red-bd)")
    elif "DENIED" in outcome_upper or "DENI" in outcome_upper: stc = ("var(--green)","var(--green-lt)","var(--green-bd)")
    else: stc = ("var(--amber)","var(--amber-lt)","var(--amber-bd)")

    case_name = pn.get("case", "")
    value = pn.get("contract_value", pn.get("value", ""))
    summary = pn.get("grounds", pn.get("summary", ""))
    implication = pn.get("what_it_means", pn.get("bd_implication", ""))
    lesson = pn.get("lesson", pn.get("who_cares", ""))
    protester = pn.get("protester", "")
    awardee_name = pn.get("awardee", "")
    agency_name = pn.get("agency", "")

    H.append(f"""<div class="cd" style="border-left:4px solid {stc[0]};">
  <div class="cd-h">
    <div>
      <div class="cd-t" style="font-size:15px;">{e(case_name)}</div>
      <div class="cd-ag">{e(protester)}{f' v. {e(agency_name)}' if agency_name else ''}{f' &middot; Awardee: {e(awardee_name)}' if awardee_name else ''}{f' &middot; {e(value)}' if value else ''}</div>
    </div>
    <span class="bg" style="background:{stc[1]};color:{stc[0]};border:1px solid {stc[2]};">{e(outcome)}</span>
  </div>
  <p style="font-size:13px;color:var(--g600);margin:8px 0;">{e(summary)}</p>""")

    if implication:
        H.append(f'<div class="co co-n"><div class="co-l">BD Implication</div><p style="font-size:13px;">{e(implication)}</p></div>')
    if lesson:
        H.append(f'<p style="font-size:12px;color:var(--g500);margin-top:6px;"><strong>Lesson:</strong> {e(lesson)}</p>')
    H.append("</div>")

# ════════════════════════════════════════════════════════════
# 12 - Market Pulse
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s12"><span class="sn">12</span><span class="sl">Market Pulse</span><span class="sln"></span></div>
<div class="mp">
  <h3>Market Pulse</h3>
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:16px;">
    <div>
      <div style="font-family:var(--fd);font-size:32px;font-weight:700;color:var(--white);">{e(market['total_obligations_week'])}</div>
      <div style="font-family:var(--fm);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--g400);">Total Obligations This Week</div>
    </div>
    <div style="font-family:var(--fm);font-size:16px;font-weight:700;color:#10B981;">{e(market['yoy_change'])} YoY</div>
  </div>
  <div style="font-family:var(--fm);font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--gold);margin-bottom:8px;">Top Agencies by Spend</div>
""")

for ag in market["top_agencies_by_spend"]:
    H.append(f"""<div class="mp-r"><span style="color:var(--g300);font-weight:500;">{e(ag['agency'])}</span><span style="color:var(--gold);font-family:var(--fm);font-weight:600;">{e(ag['amount'])}</span></div>
<p style="font-size:11px;color:var(--g400);padding:0 0 8px;line-height:1.5;">{e(ag['trend'])}</p>""")

H.append('<div style="font-family:var(--fm);font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--gold);margin:16px 0 8px;">Trending NAICS Codes</div>')

for n in market["trending_naics"]:
    H.append(f"""<div class="mp-r"><span style="color:var(--g300);"><strong>{e(n['code'])}</strong> &mdash; {e(n['description'])}</span><span style="color:#10B981;font-family:var(--fm);font-weight:600;">{e(n['change'])}</span></div>
<p style="font-size:11px;color:var(--g400);padding:0 0 8px;line-height:1.5;">{e(n['insight'])}</p>""")

H.append("</div>")

# ════════════════════════════════════════════════════════════
# 13 - Action Items
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s13"><span class="sn">13</span><span class="sl">Action Items</span><span class="sln"></span></div>
<div class="st">Action Items</div>
<div class="ss">Priority-ranked tasks for your BD team this week.</div>
""")

for ai in actions:
    plabel, pcolor, pbg = priority_style(ai["priority"])
    deadline_str = f' &middot; <strong>Due: {e(ai["deadline"])}</strong>' if ai.get("deadline") else ""
    H.append(f"""<div class="ai">
  <div style="flex-shrink:0;margin-top:2px;"><span class="bg" style="background:{pbg};color:{pcolor};border:1px solid {pcolor}22;font-size:9px;">{plabel}</span></div>
  <div style="flex:1;">
    <div style="font-weight:600;font-size:14px;color:var(--navy);margin-bottom:4px;">{e(ai['action'])}{deadline_str}</div>
    <p style="font-size:13px;color:var(--g600);line-height:1.5;">{e(ai['context'])}</p>
  </div>
</div>""")

# ════════════════════════════════════════════════════════════
# 14 - Calendar
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s14"><span class="sn">14</span><span class="sl">Calendar</span><span class="sln"></span></div>
<div class="st">What's Coming</div>
<div class="ss">Industry days, deadlines, regulatory changes, and data releases.</div>
""")

cal_type_styles = {
    "Industry Day":("#2563EB","var(--blue-lt)"),"Deadline":("#EF4444","var(--red-lt)"),
    "Court":("#7C3AED","var(--purple-lt)"),"Regulatory":("#D97706","var(--amber-lt)"),
    "System":("#6B7280","var(--g100)"),"Data":("#059669","var(--green-lt)"),
}

def render_cal_group(title, items):
    H.append(f'<div style="font-family:var(--fm);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--g400);margin:16px 0 8px;padding-top:8px;border-top:1px solid var(--g100);">{title}</div>')
    for item in items:
        ct = cal_type_styles.get(item.get("type",""), ("#6B7280","var(--g100)"))
        urg_d = urgency_dot(item.get("urgency","low"))
        event_name = item.get("title", item.get("event", ""))
        H.append(f"""<div class="ci">
  <span style="width:52px;flex-shrink:0;font-family:var(--fm);font-size:12px;font-weight:600;color:var(--navy);">{e(item.get('date',''))}</span>
  <span style="width:8px;height:8px;border-radius:50%;background:{urg_d};flex-shrink:0;margin-top:4px;"></span>
  <div style="flex:1;">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <span style="font-weight:600;color:var(--navy);font-size:13px;">{e(event_name)}</span>
      <span style="font-family:var(--fm);font-size:9px;font-weight:600;letter-spacing:.5px;padding:2px 6px;border-radius:3px;white-space:nowrap;background:{ct[1]};color:{ct[0]};">{e(item.get('type',''))}</span>
    </div>
    <p style="font-size:12px;color:var(--g500);margin-top:2px;">{e(item.get('detail',''))}</p>
  </div>
</div>""")

render_cal_group("This Week", calendar.get("this_week", []))
render_cal_group("Next Two Weeks", calendar.get("next_two_weeks", []))
render_cal_group("Looking Ahead", calendar.get("looking_ahead", []))

# ════════════════════════════════════════════════════════════
# 15 - One to Watch
# ════════════════════════════════════════════════════════════
H.append(f"""
<div class="sd" id="s15"><span class="sn">15</span><span class="sl">One to Watch</span><span class="sln"></span></div>
<div class="otw">
  <div style="font-family:var(--fm);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--gold-light);margin-bottom:8px;">Forward-Looking Intelligence</div>
  <h3>{e(otw['headline'])}</h3>
  <div style="font-family:var(--fm);font-size:11px;color:var(--g400);margin:4px 0 14px;">{e(otw['agency'])} &middot; Est. Value: {e(otw['estimated_value'])} &middot; Timeline: {e(otw['timeline'])}</div>
  <p style="font-size:14px;color:rgba(255,255,255,.8);line-height:1.7;margin-bottom:14px;">{e(otw['description'])}</p>
  <div style="background:rgba(201,162,39,.1);border:1px solid rgba(201,162,39,.2);border-radius:8px;padding:14px;margin-bottom:14px;">
    <div style="font-family:var(--fm);font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--gold);margin-bottom:6px;">Why It Matters</div>
    <p style="font-size:13px;color:rgba(255,255,255,.75);line-height:1.6;">{e(otw['why_it_matters'])}</p>
  </div>
  <div style="font-family:var(--fm);font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--gold);margin-bottom:8px;">What to Do Now</div>
  <ul class="il">
""")
for item in otw.get("what_to_do_now",[]):
    H.append(f'    <li style="color:rgba(255,255,255,.7);">{e(item)}</li>')
H.append("  </ul>\n</div>")

# ════════════════════════════════════════════════════════════
# CTA + Feedback + Footer
# ════════════════════════════════════════════════════════════
H.append("""
<div class="cta">
  <h3>Get the Full Intelligence Brief Every Week</h3>
  <p style="color:rgba(15,23,42,.7);font-size:14px;margin-bottom:16px;">Join 500+ GovCon professionals who start their Monday with actionable intelligence.</p>
  <a href="#" class="cta-b">Subscribe Now &rarr;</a>
  <p style="font-size:11px;color:rgba(15,23,42,.5);margin-top:12px;">Trusted by BD teams at 47 federal contractors</p>
</div>

<div class="fb-row">
  <a href="#" class="fb-btn">&#128077; Useful</a>
  <a href="#" class="fb-btn">&#128078; Not useful</a>
  <a href="#" class="fb-btn">&#128232; Forward to a colleague</a>
</div>
""")

H.append(f"""
</div><!-- /c -->
<div class="ftr">
  <p><span class="gld">{e(report_title)}</span></p>
  <p>Published {e(report_date)} &middot; Vol. 1, Issue 1</p>
  <p style="margin-top:8px;">Data sources: USAspending.gov, SAM.gov, GAO, Federal Register, SBA Scorecards</p>
  <p style="margin-top:4px;">Analysis powered by AI synthesis + editorial review. Data refreshed March 17, 2026.</p>
  <p style="margin-top:8px;font-size:11px;color:var(--g500);">
    This newsletter is for informational purposes only and does not constitute legal, financial, or procurement advice.<br>
    &copy; 2026 GovCon Weekly Intelligence. All rights reserved.
  </p>
</div>
</div><!-- /w -->
</body>
</html>""")

# ── Write output ──
output = "\n".join(H)
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, "w") as f:
    f.write(output)

print(f"Generated: {OUT_FILE}")
print(f"Size: {len(output):,} bytes, {output.count(chr(10)):,} lines")
