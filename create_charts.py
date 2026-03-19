#!/usr/bin/env python3
"""
GovCon Intel Newsletter Charts
Generates premium dark-themed charts from award data.
"""

import json
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Theme ---
BG = '#0A1628'
GOLD = '#C5A44E'
GOLD_LIGHT = '#D4B96A'
WHITE = '#FFFFFF'
GRAY = '#8899AA'
GRID = '#1A2A3E'

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'govcon_awards_2026-03-18.json')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

DPI = 150
WIDTH_PX, HEIGHT_PX = 800, 400
FIGSIZE = (WIDTH_PX / DPI, HEIGHT_PX / DPI)
FIGSIZE_WIDE = (900 / DPI, HEIGHT_PX / DPI)  # wider for charts with long labels


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def fmt_dollars(val):
    """Format dollar value compactly."""
    if val >= 1_000_000_000:
        return f'${val / 1_000_000_000:.1f}B'
    if val >= 1_000_000:
        return f'${val / 1_000_000:.0f}M'
    if val >= 1_000:
        return f'${val / 1_000:.0f}K'
    return f'${val:.0f}'


def style_ax(ax, title):
    """Apply shared dark theme to axes."""
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    ax.set_title(title, color=WHITE, fontsize=10, fontweight='bold', pad=12, loc='left')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID)
    ax.spines['left'].set_color(GRID)
    ax.xaxis.set_visible(False)


def shorten_name(name, max_len=30):
    """Truncate long names for chart labels."""
    name = name.title()
    if len(name) <= max_len:
        return name
    return name[:max_len - 1].rstrip() + '...'


def chart_top_agencies(data):
    """Horizontal bar: top 10 agencies by total award value."""
    totals = defaultdict(float)
    for d in data:
        totals[d['awarding_agency']] += d['award_amount']

    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:10]
    top.reverse()  # bottom-to-top for horizontal bar

    labels = [shorten_name(a.replace('Department of ', 'Dept. ').replace('Administration', 'Admin.'), 26) for a, _ in top]
    values = [v for _, v in top]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    bars = ax.barh(labels, values, color=GOLD, height=0.65, edgecolor='none')
    style_ax(ax, 'TOP AGENCIES BY TOTAL AWARD VALUE')

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.015, bar.get_y() + bar.get_height() / 2,
                fmt_dollars(val), va='center', ha='left', color=GOLD_LIGHT, fontsize=7.5, fontweight='bold')

    ax.set_xlim(0, max(values) * 1.22)
    ax.tick_params(axis='y', colors=WHITE)
    fig.subplots_adjust(left=0.30, right=0.95, top=0.88, bottom=0.05)
    fig.savefig(os.path.join(ASSETS_DIR, 'chart_top_agencies.png'), dpi=DPI, facecolor=BG)
    plt.close(fig)
    print('  -> chart_top_agencies.png')


def chart_vertical_breakdown(data):
    """Horizontal bar: count and value per vertical."""
    counts = defaultdict(int)
    values = defaultdict(float)
    for d in data:
        for v in (d.get('verticals') or []):
            counts[v] += 1
            values[v] += d['award_amount']

    # Sort by value descending
    verticals = sorted(values.keys(), key=lambda v: values[v], reverse=True)
    verticals.reverse()  # bottom-to-top

    vals = [values[v] for v in verticals]
    cnts = [counts[v] for v in verticals]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    bars = ax.barh(verticals, vals, color=GOLD, height=0.6, edgecolor='none')
    style_ax(ax, 'AWARD VALUE BY VERTICAL')

    for bar, val, cnt in zip(bars, vals, cnts):
        award_word = 'award' if cnt == 1 else 'awards'
        label = f'{fmt_dollars(val)}  ({cnt} {award_word})'
        ax.text(bar.get_width() + max(vals) * 0.015, bar.get_y() + bar.get_height() / 2,
                label, va='center', ha='left', color=GOLD_LIGHT, fontsize=7.5, fontweight='bold')

    ax.set_xlim(0, max(vals) * 1.35)
    ax.tick_params(axis='y', colors=WHITE)
    fig.subplots_adjust(left=0.22, right=0.95, top=0.88, bottom=0.05)
    fig.savefig(os.path.join(ASSETS_DIR, 'chart_verticals.png'), dpi=DPI, facecolor=BG)
    plt.close(fig)
    print('  -> chart_verticals.png')


def chart_top_contractors(data):
    """Horizontal bar: top 10 contractors by total award value."""
    totals = defaultdict(float)
    for d in data:
        totals[d['recipient_name']] += d['award_amount']

    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:10]
    top.reverse()

    labels = [shorten_name(name, 32) for name, _ in top]
    values = [v for _, v in top]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    bars = ax.barh(labels, values, color=GOLD, height=0.65, edgecolor='none')
    style_ax(ax, 'TOP CONTRACTORS BY TOTAL AWARD VALUE')

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.015, bar.get_y() + bar.get_height() / 2,
                fmt_dollars(val), va='center', ha='left', color=GOLD_LIGHT, fontsize=7.5, fontweight='bold')

    ax.set_xlim(0, max(values) * 1.22)
    ax.tick_params(axis='y', colors=WHITE)
    fig.subplots_adjust(left=0.35, right=0.95, top=0.88, bottom=0.05)
    fig.savefig(os.path.join(ASSETS_DIR, 'chart_top_contractors.png'), dpi=DPI, facecolor=BG)
    plt.close(fig)
    print('  -> chart_top_contractors.png')


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    data = load_data()
    print(f'Loaded {len(data)} awards. Generating charts...')

    chart_top_agencies(data)
    chart_vertical_breakdown(data)
    chart_top_contractors(data)

    print('Done. Charts saved to assets/')


if __name__ == '__main__':
    main()
