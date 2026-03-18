#!/usr/bin/env python3
"""Generate publication-quality GovCon Weekly Intelligence newsletter (v2)."""

import json, html, os
from datetime import datetime, date

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "corrected_all.json")
OUT_FILE = os.path.join(os.path.dirname(__file__), "output", "report_2026-03-18_v2.html")

with open(DATA_FILE) as f:
    data = json.load(f)

def e(text):
    """Escape HTML."""
    return html.escape(str(text)) if text else ""

def fmt_money(val):
    """Format raw number as $XXM or $X.XB."""
    if val is None:
        return ""
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"${val/1_000_000:.0f}M"
    return f"${val:,.0f}"

def urgency_dot(u):
    colors = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}
    return colors.get(u, "#6B7280")

def winnability_color(w):
    colors = {"high": "#10B981", "medium": "#F59E0B", "low": "#EF4444"}
    return colors.get(w, "#6B7280")

def priority_style(p):
    styles = {
        "urgent": ("URGENT", "#EF4444", "#FEF2F2"),
        "this_week": ("THIS WEEK", "#F59E0B", "#FFFBEB"),
        "this_month": ("THIS MONTH", "#3B82F6", "#EFF6FF"),
    }
    return styles.get(p, ("", "#6B7280", "#F9FAFB"))

# Compute totals for KPI bar
recompetes = data["sections"]["recompete_alerts"]["items"]
awards = data["sections"]["new_awards"]["items"]
options = data["sections"]["option_exercises"]["items"]
funding = data["sections"]["funding_actions"]["items"]
actions = data["action_items"]
doge = data["doge_tracker"]

total_recompete_value = sum(i.get("current_value_raw", 0) for i in recompetes)
total_award_value = sum(i.get("award_value_raw", 0) for i in awards)
total_option_value = sum(i.get("option_value_raw", 0) for i in options)
total_funding_value = sum(i.get("modification_value_raw", 0) for i in funding)
urgent_actions = sum(1 for a in actions if a["priority"] == "urgent")

# --- HTML GENERATION ---
H = []

H.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light">
<title>GovCon Weekly Intelligence — {e(data['report_subtitle'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<style>
/* === RESET & BASE === */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --navy: #0F172A;
  --navy-deep: #070E1A;
  --navy-mid: #1E293B;
  --navy-light: #334155;
  --gold: #C9A227;
  --gold-light: #E8D48B;
  --gold-dim: rgba(201, 162, 39, 0.12);
  --gold-glow: rgba(201, 162, 39, 0.06);
  --white: #FFFFFF;
  --off-white: #F8FAFC;
  --gray-50: #F9FAFB;
  --gray-100: #F1F5F9;
  --gray-200: #E2E8F0;
  --gray-300: #CBD5E1;
  --gray-400: #94A3B8;
  --gray-500: #64748B;
  --gray-600: #475569;
  --gray-700: #334155;
  --red: #EF4444;
  --red-dim: #FEF2F2;
  --red-border: #FECACA;
  --green: #10B981;
  --green-dim: #ECFDF5;
  --green-border: #A7F3D0;
  --blue: #3B82F6;
  --blue-dim: #EFF6FF;
  --blue-border: #BFDBFE;
  --purple: #8B5CF6;
  --purple-dim: #F5F3FF;
  --purple-border: #C4B5FD;
  --amber: #F59E0B;
  --amber-dim: #FFFBEB;
  --amber-border: #FDE68A;
  --font-display: 'Playfair Display', Georgia, 'Times New Roman', serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
  --radius: 8px;
  --radius-lg: 12px;
}}

body {{
  font-family: var(--font-body);
  color: var(--navy);
  background: var(--gray-50);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

/* === WRAPPER === */
.wrapper {{
  max-width: 680px;
  margin: 0 auto;
  background: var(--white);
  box-shadow: 0 0 0 1px var(--gray-200), var(--shadow-lg);
}}

@media (min-width: 720px) {{
  .wrapper {{ margin: 24px auto; border-radius: var(--radius-lg); overflow: hidden; }}
}}

/* === HEADER === */
.header {{
  background: var(--navy-deep);
  background-image:
    radial-gradient(ellipse at 30% 0%, rgba(201,162,39,0.08) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 100%, rgba(59,130,246,0.06) 0%, transparent 50%);
  padding: 40px 32px 32px;
  text-align: center;
  position: relative;
  overflow: hidden;
}}

.header::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--gold));
}}

.header-flag {{
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--gold);
  border: 1px solid rgba(201,162,39,0.3);
  padding: 4px 14px;
  border-radius: 2px;
  margin-bottom: 16px;
  opacity: 0;
  animation: fadeDown 0.6s ease forwards 0.2s;
}}

.header-title {{
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 800;
  color: var(--white);
  letter-spacing: -0.5px;
  margin-bottom: 6px;
  opacity: 0;
  animation: fadeDown 0.6s ease forwards 0.35s;
}}

.header-subtitle {{
  font-size: 14px;
  color: var(--gray-400);
  font-weight: 400;
  opacity: 0;
  animation: fadeDown 0.6s ease forwards 0.45s;
}}

/* === HERO STAT === */
.hero-stat {{
  background: var(--navy);
  background-image: linear-gradient(135deg, var(--navy-deep) 0%, var(--navy) 50%, var(--navy-mid) 100%);
  padding: 28px 32px;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  position: relative;
}}

.hero-stat-label {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 8px;
}}

.hero-stat-number {{
  font-family: var(--font-display);
  font-size: 56px;
  font-weight: 900;
  color: var(--white);
  letter-spacing: -2px;
  line-height: 1;
  margin-bottom: 8px;
  opacity: 0;
  animation: countPop 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards 0.5s;
}}

.hero-stat-context {{
  font-size: 13px;
  color: var(--gray-400);
  max-width: 480px;
  margin: 0 auto;
  line-height: 1.5;
}}

/* === KPI BAR === */
.kpi-bar {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-bottom: 1px solid var(--gray-200);
  background: var(--gray-50);
}}

.kpi-item {{
  padding: 16px 12px;
  text-align: center;
  border-right: 1px solid var(--gray-200);
  opacity: 0;
  animation: fadeUp 0.5s ease forwards;
}}
.kpi-item:last-child {{ border-right: none; }}
.kpi-item:nth-child(1) {{ animation-delay: 0.6s; }}
.kpi-item:nth-child(2) {{ animation-delay: 0.7s; }}
.kpi-item:nth-child(3) {{ animation-delay: 0.8s; }}
.kpi-item:nth-child(4) {{ animation-delay: 0.9s; }}

.kpi-number {{
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 700;
  color: var(--navy);
  letter-spacing: -0.5px;
}}

.kpi-label {{
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--gray-500);
  margin-top: 2px;
}}

/* === TABLE OF CONTENTS === */
.toc {{
  padding: 20px 32px;
  border-bottom: 1px solid var(--gray-200);
  background: var(--white);
}}

.toc-title {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gray-400);
  margin-bottom: 12px;
}}

.toc-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 24px;
}}

.toc-item {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--gray-600);
  text-decoration: none;
  padding: 4px 0;
  transition: color 0.15s;
}}
.toc-item:hover {{ color: var(--navy); }}

.toc-num {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--gold);
  min-width: 20px;
}}

.toc-dot {{
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}}

/* === SECTION LAYOUT === */
.section {{
  padding: 0 32px 32px;
}}

.section-header {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 28px 0 8px;
  margin-bottom: 4px;
}}

.section-num {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--gold);
  background: var(--gold-dim);
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 1px;
}}

.section-title {{
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.3px;
}}

.section-subtitle {{
  font-size: 13px;
  color: var(--gray-500);
  margin-bottom: 20px;
  padding-left: 0;
}}

/* === DIVIDER === */
.divider {{
  height: 1px;
  background: var(--gray-200);
  margin: 0 32px;
}}

.divider-gold {{
  height: 2px;
  background: linear-gradient(90deg, var(--gold-dim), var(--gold), var(--gold-dim));
  margin: 0;
}}

/* === CARD BASE === */
.card {{
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 16px;
  position: relative;
  transition: box-shadow 0.2s;
}}
.card:hover {{ box-shadow: var(--shadow-md); }}

.card-red {{ border-left: 4px solid var(--red); }}
.card-green {{ border-left: 4px solid var(--green); }}
.card-blue {{ border-left: 4px solid var(--blue); }}
.card-purple {{ border-left: 4px solid var(--purple); }}
.card-amber {{ border-left: 4px solid var(--amber); }}

.card-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}}

.card-title {{
  font-size: 16px;
  font-weight: 700;
  color: var(--navy);
  line-height: 1.3;
}}

.card-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 12px;
  color: var(--gray-500);
  margin-bottom: 12px;
}}

.card-meta-item {{
  display: flex;
  align-items: center;
  gap: 4px;
}}

.card-meta strong {{
  color: var(--gray-700);
  font-weight: 600;
}}

.card-body {{
  font-size: 14px;
  color: var(--gray-600);
  line-height: 1.7;
  margin-bottom: 16px;
}}

/* === BADGES === */
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 3px;
  white-space: nowrap;
  flex-shrink: 0;
}}

.badge-urgent {{
  background: var(--red);
  color: white;
}}

.badge-days {{
  background: var(--red-dim);
  color: var(--red);
  border: 1px solid var(--red-border);
}}

.badge-days-medium {{
  background: var(--amber-dim);
  color: #92400E;
  border: 1px solid var(--amber-border);
}}

.badge-winnability-high {{
  background: var(--green-dim);
  color: #065F46;
  border: 1px solid var(--green-border);
}}
.badge-winnability-medium {{
  background: var(--amber-dim);
  color: #92400E;
  border: 1px solid var(--amber-border);
}}
.badge-winnability-low {{
  background: var(--red-dim);
  color: #991B1B;
  border: 1px solid var(--red-border);
}}

.badge-value {{
  background: var(--navy);
  color: var(--gold-light);
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 4px;
}}

.badge-set-aside {{
  background: var(--purple-dim);
  color: #5B21B6;
  border: 1px solid var(--purple-border);
}}

.badge-fno {{
  background: var(--gray-100);
  color: var(--gray-600);
  border: 1px solid var(--gray-300);
}}

/* === CALLOUT BOXES === */
.callout {{
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
  font-size: 13px;
  line-height: 1.7;
}}

.callout-label {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}}

.callout-green {{
  background: var(--green-dim);
  border: 1px solid var(--green-border);
  color: #065F46;
}}
.callout-green .callout-label {{ color: var(--green); }}

.callout-red {{
  background: var(--red-dim);
  border: 1px solid var(--red-border);
  color: #991B1B;
}}
.callout-red .callout-label {{ color: var(--red); }}

.callout-blue {{
  background: var(--blue-dim);
  border: 1px solid var(--blue-border);
  color: #1E40AF;
}}
.callout-blue .callout-label {{ color: var(--blue); }}

.callout-amber {{
  background: var(--amber-dim);
  border: 1px solid var(--amber-border);
  color: #92400E;
}}
.callout-amber .callout-label {{ color: var(--amber); }}

.callout-navy {{
  background: var(--navy);
  border: 1px solid var(--navy-light);
  color: var(--gray-300);
}}
.callout-navy .callout-label {{ color: var(--gold); }}

/* === FACTORS LIST === */
.factors {{
  list-style: none;
  padding: 0;
  margin: 8px 0;
}}

.factors li {{
  position: relative;
  padding: 6px 0 6px 20px;
  font-size: 13px;
  color: var(--gray-600);
  line-height: 1.55;
  border-bottom: 1px solid var(--gray-100);
}}
.factors li:last-child {{ border-bottom: none; }}

.factors li::before {{
  content: '';
  position: absolute;
  left: 4px;
  top: 14px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--gold);
}}

/* === WHO SHOULD PURSUE === */
.pursue-list {{
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
}}

.pursue-list li {{
  position: relative;
  padding: 8px 0 8px 28px;
  font-size: 13px;
  color: var(--gray-700);
  line-height: 1.55;
}}

.pursue-list li::before {{
  content: '\\2192';
  position: absolute;
  left: 6px;
  top: 8px;
  color: var(--gold);
  font-weight: 700;
}}

/* === DOGE TRACKER === */
.doge-panel {{
  background: var(--navy);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 16px;
}}

.doge-agency {{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}}
.doge-agency:last-child {{ margin-bottom: 0; }}

.doge-agency-name {{
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 4px;
}}

.doge-action {{
  font-size: 13px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 6px;
}}

.doge-impact {{
  font-size: 13px;
  color: var(--gray-400);
  line-height: 1.6;
  margin-bottom: 8px;
}}

.doge-status {{
  font-size: 12px;
  font-style: italic;
  color: var(--amber);
  line-height: 1.5;
}}

.doge-status-growing {{
  color: var(--green);
}}

/* === COURT RULINGS === */
.court-card {{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-left: 3px solid var(--amber);
  border-radius: 6px;
  padding: 14px 16px;
  margin-bottom: 10px;
}}

.court-case {{
  font-size: 13px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 4px;
}}

.court-ruling {{
  font-size: 12px;
  color: var(--gray-400);
  margin-bottom: 6px;
}}

.court-impact {{
  font-size: 12px;
  color: var(--gray-300);
  font-style: italic;
  line-height: 1.5;
}}

/* === CONTRACTOR IMPACT === */
.contractor-row {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-top: 12px;
}}

.contractor-card {{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  padding: 14px 16px;
}}

.contractor-name {{
  font-size: 13px;
  font-weight: 700;
  color: var(--white);
}}

.contractor-exposure {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--red);
  margin: 2px 0 6px;
}}

.contractor-status {{
  font-size: 12px;
  color: var(--gray-400);
  line-height: 1.5;
}}

.contractor-signal {{
  font-size: 12px;
  color: var(--gold);
  font-weight: 600;
  margin-top: 6px;
}}

/* === MARKET PULSE === */
.pulse-panel {{
  background: var(--navy);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 16px;
}}

.pulse-headline {{
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
}}

.pulse-total {{
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 900;
  color: var(--white);
}}

.pulse-change {{
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--green);
}}

.pulse-subtitle {{
  font-size: 11px;
  color: var(--gray-400);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}}

.pulse-grid {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin: 16px 0;
}}

.pulse-row {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 16px;
  background: rgba(255,255,255,0.04);
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.06);
}}

.pulse-agency-name {{
  font-size: 14px;
  font-weight: 700;
  color: var(--white);
}}

.pulse-amount {{
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--gold);
  white-space: nowrap;
}}

.pulse-trend {{
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 4px;
  line-height: 1.5;
}}

.naics-tag {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 8px;
  width: 100%;
}}

.naics-code {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--gold);
  background: var(--gold-dim);
  padding: 2px 8px;
  border-radius: 3px;
  white-space: nowrap;
}}

.naics-desc {{
  font-size: 13px;
  color: var(--white);
  font-weight: 600;
}}

.naics-change {{
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--green);
  margin-left: auto;
  white-space: nowrap;
}}

.naics-insight {{
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 4px;
  line-height: 1.5;
}}

/* === ACTION ITEMS === */
.action-card {{
  display: flex;
  gap: 14px;
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius);
  margin-bottom: 10px;
}}
.action-card:hover {{ box-shadow: var(--shadow-sm); }}

.action-priority {{
  flex-shrink: 0;
  width: 4px;
  border-radius: 2px;
  min-height: 40px;
}}

.action-content {{
  flex: 1;
  min-width: 0;
}}

.action-title {{
  font-size: 14px;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: 4px;
}}

.action-context {{
  font-size: 13px;
  color: var(--gray-500);
  line-height: 1.55;
}}

.action-deadline {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--red);
  margin-top: 6px;
}}

/* === ONE TO WATCH === */
.watch-panel {{
  background: linear-gradient(135deg, var(--navy-deep) 0%, var(--navy) 60%, #1a2744 100%);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 16px;
  border: 1px solid rgba(201,162,39,0.15);
  position: relative;
  overflow: hidden;
}}

.watch-panel::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}}

.watch-flag {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 12px;
}}

.watch-headline {{
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 800;
  color: var(--white);
  margin-bottom: 8px;
  line-height: 1.3;
}}

.watch-meta {{
  font-size: 13px;
  color: var(--gray-400);
  margin-bottom: 16px;
}}

.watch-meta strong {{
  color: var(--gold);
}}

.watch-body {{
  font-size: 14px;
  color: var(--gray-300);
  line-height: 1.7;
  margin-bottom: 16px;
}}

.watch-why {{
  background: rgba(201,162,39,0.08);
  border: 1px solid rgba(201,162,39,0.15);
  border-radius: 6px;
  padding: 14px 16px;
  margin-bottom: 16px;
}}

.watch-why-label {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 6px;
}}

.watch-why-text {{
  font-size: 13px;
  color: var(--gray-300);
  line-height: 1.6;
}}

.watch-actions {{
  list-style: none;
  padding: 0;
}}

.watch-actions li {{
  position: relative;
  padding: 8px 0 8px 24px;
  font-size: 13px;
  color: var(--gray-300);
  line-height: 1.55;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.watch-actions li:last-child {{ border-bottom: none; }}

.watch-actions li::before {{
  content: '';
  position: absolute;
  left: 6px;
  top: 16px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--gold);
}}

/* === CTA === */
.cta-block {{
  background: var(--navy);
  padding: 32px;
  text-align: center;
}}

.cta-headline {{
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  color: var(--white);
  margin-bottom: 8px;
}}

.cta-body {{
  font-size: 14px;
  color: var(--gray-400);
  margin-bottom: 20px;
  max-width: 420px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}}

.cta-button {{
  display: inline-block;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 700;
  color: var(--navy-deep);
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  padding: 14px 32px;
  border-radius: 6px;
  text-decoration: none;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(201,162,39,0.3);
  transition: transform 0.15s, box-shadow 0.15s;
}}
.cta-button:hover {{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(201,162,39,0.4);
}}

.cta-price {{
  font-size: 12px;
  color: var(--gray-500);
  margin-top: 12px;
}}

/* === FEEDBACK === */
.feedback {{
  padding: 20px 32px;
  text-align: center;
  border-top: 1px solid var(--gray-200);
  background: var(--gray-50);
}}

.feedback-question {{
  font-size: 13px;
  color: var(--gray-500);
  margin-bottom: 12px;
}}

.feedback-buttons {{
  display: flex;
  justify-content: center;
  gap: 16px;
}}

.feedback-btn {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-600);
  background: var(--white);
  border: 1px solid var(--gray-200);
  text-decoration: none;
  transition: all 0.15s;
}}
.feedback-btn:hover {{
  border-color: var(--gold);
  color: var(--navy);
}}

/* === FOOTER === */
.footer {{
  padding: 24px 32px;
  text-align: center;
  background: var(--navy-deep);
  color: var(--gray-500);
  font-size: 11px;
  line-height: 1.8;
}}

.footer a {{
  color: var(--gold);
  text-decoration: none;
}}

/* === DETAILS/EXPAND === */
details {{
  margin: 8px 0;
}}
details summary {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--gray-500);
  cursor: pointer;
  padding: 6px 0;
  user-select: none;
  list-style: none;
}}
details summary::before {{
  content: '\\25B6  ';
  font-size: 9px;
  transition: transform 0.2s;
  display: inline-block;
}}
details[open] summary::before {{
  transform: rotate(90deg);
}}

/* === ANIMATIONS === */
@keyframes fadeDown {{
  from {{ opacity: 0; transform: translateY(-10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes countPop {{
  0% {{ opacity: 0; transform: scale(0.8); }}
  70% {{ transform: scale(1.02); }}
  100% {{ opacity: 1; transform: scale(1); }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* === RESPONSIVE === */
@media (max-width: 640px) {{
  .header {{ padding: 28px 20px 24px; }}
  .header-title {{ font-size: 26px; }}
  .hero-stat {{ padding: 20px; }}
  .hero-stat-number {{ font-size: 42px; }}
  .section {{ padding: 0 20px 24px; }}
  .divider {{ margin: 0 20px; }}
  .toc {{ padding: 16px 20px; }}
  .toc-grid {{ grid-template-columns: 1fr; }}
  .kpi-bar {{ grid-template-columns: repeat(2, 1fr); }}
  .kpi-item:nth-child(2) {{ border-right: none; }}
  .cta-block {{ padding: 24px 20px; }}
  .feedback {{ padding: 16px 20px; }}
  .pulse-headline {{ flex-direction: column; gap: 4px; }}
}}
</style>
</head>
<body>
""")

# === HEADER ===
H.append(f"""
<div class="wrapper">
  <!-- HEADER -->
  <div class="header">
    <div class="header-flag">Intelligence Brief</div>
    <div class="header-title">{e(data['report_title'])}</div>
    <div class="header-subtitle">{e(data['report_subtitle'])} &middot; March 18, 2026</div>
  </div>
""")

# === HERO STAT ===
notable = data["notable"]
H.append(f"""
  <!-- HERO STAT -->
  <div class="hero-stat">
    <div class="hero-stat-label">Number of the Week</div>
    <div class="hero-stat-number">{e(notable['key_stat'])}</div>
    <div class="hero-stat-context">{e(notable['key_stat_label'])}</div>
  </div>
""")

# === KPI BAR ===
H.append(f"""
  <!-- KPI BAR -->
  <div class="kpi-bar">
    <div class="kpi-item">
      <div class="kpi-number">{fmt_money(total_recompete_value)}</div>
      <div class="kpi-label">Recompetes</div>
    </div>
    <div class="kpi-item">
      <div class="kpi-number">{fmt_money(total_award_value)}</div>
      <div class="kpi-label">New Awards</div>
    </div>
    <div class="kpi-item">
      <div class="kpi-number">{fmt_money(total_funding_value)}</div>
      <div class="kpi-label">Funding Actions</div>
    </div>
    <div class="kpi-item">
      <div class="kpi-number" style="color: var(--red);">{urgent_actions}</div>
      <div class="kpi-label">Urgent Actions</div>
    </div>
  </div>
""")

# === TABLE OF CONTENTS ===
toc_items = [
    ("01", "DOGE Tracker", "#EF4444"),
    ("02", "Recompete Alerts", "#EF4444"),
    ("03", "New Awards", "#10B981"),
    ("04", "Option Exercises", "#3B82F6"),
    ("05", "Funding Actions", "#8B5CF6"),
    ("06", "Market Pulse", "#C9A227"),
    ("07", "Action Items", "#F59E0B"),
    ("08", "One to Watch", "#C9A227"),
]
H.append("""  <!-- TABLE OF CONTENTS -->
  <div class="toc">
    <div class="toc-title">In This Brief</div>
    <div class="toc-grid">
""")
for num, label, color in toc_items:
    H.append(f'      <a href="#section-{num}" class="toc-item"><span class="toc-num">{num}</span><span class="toc-dot" style="background:{color};"></span>{label}</a>\n')
H.append("""    </div>
  </div>
""")

# === HEADLINE INTEL ===
H.append(f"""
  <div class="section" style="padding-top: 24px;">
    <div class="callout callout-navy">
      <div class="callout-label">&#9733; Lead Intelligence</div>
      {e(notable['summary'])}
    </div>
  </div>
  <div class="divider"></div>
""")

# === SECTION 01: DOGE TRACKER ===
H.append(f"""
  <div class="section" id="section-01">
    <div class="section-header">
      <span class="section-num">01</span>
      <span class="section-title">DOGE Tracker</span>
    </div>
    <div class="section-subtitle">Agency disruptions, court rulings, and what it means for your contracts</div>

    <div class="callout callout-amber" style="margin-bottom: 16px;">
      <div class="callout-label">&#9888; Situation Overview</div>
      {e(doge['headline'])}
    </div>

    <div class="doge-panel">
      <div style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); margin-bottom: 14px;">Agencies Affected</div>
""")

for agency in doge["agencies_affected"]:
    growing = "GROWING" in agency.get("action", "")
    status_class = "doge-status-growing" if growing else ""
    H.append(f"""
      <div class="doge-agency">
        <div class="doge-agency-name">{e(agency['agency'])}</div>
        <div class="doge-action">{e(agency['action'])}</div>
        <div class="doge-impact">{e(agency['impact'])}</div>
        <div class="doge-status {status_class}">{e(agency['status'])}</div>
      </div>
""")

H.append("""
    </div>
""")

# Court Rulings
if doge.get("court_rulings"):
    H.append("""
    <div style="margin-top: 16px;">
      <div style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--gray-500); margin-bottom: 10px;">Court Rulings &amp; Legal Watch</div>
""")
    for ruling in doge["court_rulings"]:
        H.append(f"""
      <div class="court-card" style="background: var(--white); border: 1px solid var(--gray-200); border-left: 3px solid var(--amber);">
        <div class="court-case" style="color: var(--navy);">{e(ruling['case'])}</div>
        <div class="court-ruling" style="color: var(--gray-600);">{e(ruling['ruling'])}</div>
        <div class="court-impact" style="color: var(--gray-500);">{e(ruling['practical_impact'])}</div>
      </div>
""")
    H.append("    </div>\n")

# Contractor Impact
if doge.get("contractor_impact"):
    H.append("""
    <div style="margin-top: 16px;">
      <div style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--gray-500); margin-bottom: 10px;">Contractor Impact Watch</div>
      <div class="contractor-row">
""")
    for c in doge["contractor_impact"]:
        H.append(f"""
        <div class="contractor-card" style="background: var(--white); border: 1px solid var(--gray-200);">
          <div class="contractor-name" style="color: var(--navy);">{e(c['contractor'])}</div>
          <div class="contractor-exposure" style="color: var(--red);">Exposure: {e(c['exposure'])}</div>
          <div class="contractor-status" style="color: var(--gray-600);">{e(c['status'])}</div>
          <div class="contractor-signal" style="color: var(--gold);">{e(c['signal'])}</div>
        </div>
""")
    H.append("      </div>\n    </div>\n")

# DOGE Outlook
if doge.get("outlook"):
    H.append(f"""
    <div class="callout callout-navy" style="margin-top: 16px;">
      <div class="callout-label">&#128270; Outlook</div>
      {e(doge['outlook'])}
    </div>
""")

H.append("  </div>\n  <div class=\"divider\"></div>\n")

# === SECTION 02: RECOMPETE ALERTS ===
sec = data["sections"]["recompete_alerts"]
H.append(f"""
  <div class="section" id="section-02">
    <div class="section-header">
      <span class="section-num">02</span>
      <span class="section-title">{e(sec['title'])}</span>
    </div>
    <div class="section-subtitle">{e(sec['subtitle'])}</div>
""")

for item in sec["items"]:
    days = item.get("days_remaining", 0)
    days_class = "badge-days" if days <= 120 else "badge-days-medium"
    w = item.get("winnability_score", "").lower()
    w_class = f"badge-winnability-{w}" if w else ""
    sa = item.get("set_aside", "")
    sa_class = "badge-set-aside" if "Small" in sa else "badge-fno"

    H.append(f"""
    <div class="card card-red">
      <div class="card-header">
        <div class="card-title">{e(item['contract_name'])}</div>
        <span class="badge-value">{e(item.get('current_value', ''))}</span>
      </div>
      <div class="card-meta">
        <span class="card-meta-item"><strong>Agency:</strong> {e(item['agency'])}</span>
        <span class="card-meta-item"><strong>Incumbent:</strong> {e(item['incumbent'])}</span>
        <span class="card-meta-item"><strong>NAICS:</strong> {e(item.get('naics', ''))}</span>
      </div>
      <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
        <span class="badge {days_class}">{days}d remaining</span>
        <span class="badge {w_class}">Winnability: {w.upper()}</span>
        <span class="badge {sa_class}">{e(sa)}</span>
      </div>
      <div class="card-body">{e(item.get('notable_detail', ''))}</div>
""")

    # Solicitation status
    if item.get("solicitation_status"):
        H.append(f'      <div style="font-family: var(--font-mono); font-size: 11px; color: var(--blue); margin-bottom: 12px;">&#9654; {e(item["solicitation_status"])}</div>\n')

    # Winnability Factors
    if item.get("winnability_factors"):
        H.append('      <details>\n        <summary>Winnability Analysis</summary>\n        <ul class="factors">\n')
        for f in item["winnability_factors"]:
            H.append(f"          <li>{e(f)}</li>\n")
        H.append("        </ul>\n      </details>\n")

    # Protest History
    if item.get("protest_history"):
        H.append(f"""
      <div class="callout callout-amber" style="margin-top: 8px;">
        <div class="callout-label">&#9878; Protest History</div>
        {e(item['protest_history'])}
      </div>
""")

    # Who Should Pursue
    if item.get("who_should_pursue"):
        H.append('      <details>\n        <summary>Who Should Pursue This</summary>\n        <ul class="pursue-list">\n')
        for p in item["who_should_pursue"]:
            H.append(f"          <li>{e(p)}</li>\n")
        H.append("        </ul>\n      </details>\n")

    H.append("    </div>\n")

H.append("  </div>\n  <div class=\"divider\"></div>\n")

# === SECTION 03: NEW AWARDS ===
sec = data["sections"]["new_awards"]
H.append(f"""
  <div class="section" id="section-03">
    <div class="section-header">
      <span class="section-num">03</span>
      <span class="section-title">{e(sec['title'])}</span>
    </div>
    <div class="section-subtitle">{e(sec['subtitle'])}</div>
""")

for item in sec["items"]:
    competitors = item.get("competitors_known", [])
    comp_str = ", ".join(competitors) if competitors else "Not disclosed"

    H.append(f"""
    <div class="card card-green">
      <div class="card-header">
        <div class="card-title">{e(item['contract_name'])}</div>
        <span class="badge-value">{e(item.get('award_value', ''))}</span>
      </div>
      <div class="card-meta">
        <span class="card-meta-item"><strong>Agency:</strong> {e(item['agency'])}</span>
        <span class="card-meta-item"><strong>Awardee:</strong> {e(item['awardee'])}</span>
        <span class="card-meta-item"><strong>PoP:</strong> {e(item.get('period_of_performance', ''))}</span>
      </div>
      <div class="card-meta" style="margin-top: -4px;">
        <span class="card-meta-item"><strong>Also Competed:</strong> {e(comp_str)}</span>
      </div>
      <div class="card-body">{e(item.get('notable_detail', ''))}</div>
""")

    if item.get("why_they_won"):
        H.append(f"""
      <div class="callout callout-green">
        <div class="callout-label">&#10003; Why They Won</div>
        {e(item['why_they_won'])}
      </div>
""")

    if item.get("what_losers_should_do"):
        H.append(f"""
      <div class="callout callout-red">
        <div class="callout-label">&#10007; If You Lost</div>
        {e(item['what_losers_should_do'])}
      </div>
""")

    if item.get("market_signal"):
        H.append(f"""
      <div class="callout callout-blue">
        <div class="callout-label">&#9670; Market Signal</div>
        {e(item['market_signal'])}
      </div>
""")

    H.append("    </div>\n")

H.append("  </div>\n  <div class=\"divider\"></div>\n")

# === SECTION 04: OPTION EXERCISES ===
sec = data["sections"]["option_exercises"]
H.append(f"""
  <div class="section" id="section-04">
    <div class="section-header">
      <span class="section-num">04</span>
      <span class="section-title">{e(sec['title'])}</span>
    </div>
    <div class="section-subtitle">{e(sec['subtitle'])}</div>
""")

for item in sec["items"]:
    H.append(f"""
    <div class="card card-blue">
      <div class="card-header">
        <div class="card-title">{e(item['contract_name'])}</div>
        <span class="badge-value">{e(item.get('option_value', ''))}</span>
      </div>
      <div class="card-meta">
        <span class="card-meta-item"><strong>Agency:</strong> {e(item['agency'])}</span>
        <span class="card-meta-item"><strong>Contractor:</strong> {e(item['contractor'])}</span>
        <span class="card-meta-item"><strong>{e(item.get('option_year', ''))}</strong></span>
      </div>
      <div class="card-body">{e(item.get('notable_detail', ''))}</div>
""")

    if item.get("recompete_signal"):
        H.append(f"""
      <div class="callout callout-blue">
        <div class="callout-label">&#128161; Recompete Signal</div>
        {e(item['recompete_signal'])}
      </div>
""")

    if item.get("who_should_watch"):
        H.append('      <details>\n        <summary>Who Should Watch This</summary>\n        <ul class="pursue-list">\n')
        for w in item["who_should_watch"]:
            H.append(f"          <li>{e(w)}</li>\n")
        H.append("        </ul>\n      </details>\n")

    H.append("    </div>\n")

H.append("  </div>\n  <div class=\"divider\"></div>\n")

# === SECTION 05: FUNDING ACTIONS ===
sec = data["sections"]["funding_actions"]
H.append(f"""
  <div class="section" id="section-05">
    <div class="section-header">
      <span class="section-num">05</span>
      <span class="section-title">{e(sec['title'])}</span>
    </div>
    <div class="section-subtitle">{e(sec['subtitle'])}</div>
""")

for item in sec["items"]:
    action_type = item.get("action_type", "")
    H.append(f"""
    <div class="card card-purple">
      <div class="card-header">
        <div class="card-title">{e(item['contract_name'])}</div>
        <span class="badge-value">{e(item.get('modification_value', ''))}</span>
      </div>
      <div class="card-meta">
        <span class="card-meta-item"><strong>Type:</strong> {e(action_type)}</span>
        <span class="card-meta-item"><strong>Agency:</strong> {e(item['agency'])}</span>
        <span class="card-meta-item"><strong>Contractor:</strong> {e(item['contractor'])}</span>
""")
    if item.get("new_ceiling"):
        H.append(f'        <span class="card-meta-item"><strong>New Ceiling:</strong> {e(item["new_ceiling"])}</span>\n')
    H.append(f"""
      </div>
      <div class="card-body">{e(item.get('notable_detail', ''))}</div>
""")

    if item.get("intel_note"):
        H.append(f"""
      <div class="callout callout-navy">
        <div class="callout-label">&#128270; Intel Note</div>
        {e(item['intel_note'])}
      </div>
""")

    H.append("    </div>\n")

H.append("  </div>\n  <div class=\"divider\"></div>\n")

# === SECTION 06: MARKET PULSE ===
mp = data["market_pulse"]
H.append(f"""
  <div class="section" id="section-06">
    <div class="section-header">
      <span class="section-num">06</span>
      <span class="section-title">Market Pulse</span>
    </div>
    <div class="section-subtitle">Weekly spending trends, top agencies, and hot NAICS codes</div>

    <div class="pulse-panel">
      <div class="pulse-headline">
        <div>
          <div class="pulse-subtitle">Total Obligations This Week</div>
          <div class="pulse-total">{e(mp['total_obligations_week'])}</div>
        </div>
        <div class="pulse-change">{e(mp['yoy_change'])} YoY</div>
      </div>

      <div style="font-family: var(--font-mono); font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); margin-bottom: 10px;">Top Agencies by Spend</div>
      <div class="pulse-grid">
""")

for ag in mp.get("top_agencies_by_spend", []):
    H.append(f"""
        <div class="pulse-row">
          <div style="flex: 1;">
            <div class="pulse-agency-name">{e(ag['agency'])}</div>
            <div class="pulse-trend">{e(ag.get('trend', ''))}</div>
          </div>
          <div class="pulse-amount">{e(ag['amount'])}</div>
        </div>
""")

H.append("""
      </div>

      <div style="font-family: var(--font-mono); font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); margin: 20px 0 10px;">Trending NAICS Codes</div>
""")

for naics in mp.get("trending_naics", []):
    H.append(f"""
      <div class="naics-tag">
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="naics-code">{e(naics['code'])}</span>
            <span class="naics-desc">{e(naics['description'])}</span>
            <span class="naics-change">{e(naics['change'])}</span>
          </div>
          <div class="naics-insight">{e(naics.get('insight', ''))}</div>
        </div>
      </div>
""")

H.append("""
    </div>
  </div>
  <div class="divider"></div>
""")

# === SECTION 07: ACTION ITEMS ===
H.append("""
  <div class="section" id="section-07">
    <div class="section-header">
      <span class="section-num">07</span>
      <span class="section-title">Action Items</span>
    </div>
    <div class="section-subtitle">Priority-ranked actions for your BD team this week</div>
""")

for item in data["action_items"]:
    label, color, bg = priority_style(item["priority"])
    deadline_html = ""
    if item.get("deadline"):
        deadline_html = f'<div class="action-deadline">DEADLINE: {e(item["deadline"])}</div>'

    H.append(f"""
    <div class="action-card">
      <div class="action-priority" style="background: {color};"></div>
      <div class="action-content">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="badge" style="background: {bg}; color: {color}; border: 1px solid {color}33;">{label}</span>
        </div>
        <div class="action-title">{e(item['action'])}</div>
        <div class="action-context">{e(item['context'])}</div>
        {deadline_html}
      </div>
    </div>
""")

H.append("  </div>\n  <div class=\"divider\"></div>\n")

# === SECTION 08: ONE TO WATCH ===
otw = data["one_to_watch"]
H.append(f"""
  <div class="section" id="section-08">
    <div class="section-header">
      <span class="section-num">08</span>
      <span class="section-title">One to Watch</span>
    </div>
    <div class="section-subtitle">The opportunity smart BD teams should be tracking now</div>

    <div class="watch-panel">
      <div class="watch-flag">&#9733; Forward-Looking Intelligence</div>
      <div class="watch-headline">{e(otw['headline'])}</div>
      <div class="watch-meta"><strong>{e(otw['agency'])}</strong> &middot; Est. Value: <strong>{e(otw.get('estimated_value', ''))}</strong> &middot; {e(otw.get('timeline', ''))}</div>
      <div class="watch-body">{e(otw['description'])}</div>

      <div class="watch-why">
        <div class="watch-why-label">&#128161; Why It Matters</div>
        <div class="watch-why-text">{e(otw['why_it_matters'])}</div>
      </div>

      <div style="font-family: var(--font-mono); font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--gold); margin-bottom: 8px;">What to Do Now</div>
      <ul class="watch-actions">
""")

for action in otw.get("what_to_do_now", []):
    H.append(f"        <li>{e(action)}</li>\n")

H.append("""
      </ul>
    </div>
  </div>
""")

# === CTA ===
H.append("""
  <div class="divider-gold"></div>
  <div class="cta-block">
    <div class="cta-headline">Stop Wasting $50K on Proposals You Can't Win</div>
    <div class="cta-body">GovCon Weekly Intelligence gives you the bid/no-bid signals, incumbent analysis, and winnability scoring that enterprise platforms charge $8K+ for.</div>
    <a href="#" class="cta-button">Start Your Free Trial</a>
    <div class="cta-price">Pro: $29/mo ($249/yr) &middot; Insider: $79/mo ($699/yr) &middot; Cancel anytime</div>
    <div style="font-size: 11px; color: var(--gray-500); margin-top: 16px; font-style: italic;">Trusted by 2,400+ capture managers, BD leads, and GovCon advisors</div>
  </div>
""")

# === FEEDBACK ===
H.append("""
  <div class="feedback">
    <div class="feedback-question">How useful was this week's brief?</div>
    <div class="feedback-buttons">
      <a href="#" class="feedback-btn">&#128077; Useful</a>
      <a href="#" class="feedback-btn">&#128078; Not Useful</a>
      <a href="#" class="feedback-btn">&#128232; Forward to a Colleague</a>
    </div>
  </div>
""")

# === FOOTER ===
H.append("""
  <div class="footer">
    <strong style="color: #E2E8F0;">GovCon Weekly Intelligence</strong><br>
    Curated analysis for government contractors who compete to win.<br>
    <br>
    <span style="color: var(--gray-600); font-size: 10px;">Data current as of March 18, 2026 05:00 EST &middot; Sources: USAspending.gov, FPDS-NG, SAM.gov, Federal Register, court filings<br>
    Winnability scores computed from incumbent tenure, protest history, set-aside status, and competitive landscape analysis.</span><br>
    <br>
    <a href="#">Manage Preferences</a> &middot; <a href="#">Unsubscribe</a> &middot; <a href="#">View in Browser</a><br>
    &copy; 2026 GovCon Weekly Intelligence. All rights reserved.
  </div>

</div><!-- /wrapper -->
</body>
</html>
""")

# Write output
output = "".join(H)
with open(OUT_FILE, "w") as f:
    f.write(output)

print(f"Generated: {OUT_FILE}")
print(f"Size: {len(output):,} bytes, {output.count(chr(10)):,} lines")
