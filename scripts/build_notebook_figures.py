#!/usr/bin/env python3
"""Generate lightweight SVG figures for the explainer notebook."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
FIG_DIR = ROOT / "notebooks" / "figures"
SITE_FIG_DIR = ROOT / "site" / "notebooks" / "figures"


def load(name: str):
    return json.loads((SITE_DATA / name).read_text())


def write(name: str, svg: str) -> None:
    for fig_dir in [FIG_DIR, SITE_FIG_DIR]:
        fig_dir.mkdir(parents=True, exist_ok=True)
        (fig_dir / name).write_text(svg, encoding="utf-8")


def axis_label(text: str, x: float, y: float, anchor: str = "middle") -> str:
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="label">{text}</text>'


def chart_style() -> str:
    return """
    <style>
      .bg { fill: #fffdf8; }
      .axis { stroke: #d8d0c2; stroke-width: 1; }
      .grid { stroke: #eee7da; stroke-width: 1; }
      .label { fill: #62706c; font: 12px system-ui, sans-serif; }
      .title { fill: #17201d; font: 700 18px system-ui, sans-serif; }
      .note { fill: #7a5d2a; font: 700 12px system-ui, sans-serif; }
    </style>
    """


def annual_svg() -> str:
    data = load("annual_reports.json")
    width, height = 900, 440
    left, right, top, bottom = 62, 24, 42, 48
    xs = [d["year"] for d in data]
    ys = [d["reports"] for d in data]
    min_x, max_x = min(xs), max(xs)
    max_y = max(ys)

    def sx(x):
        return left + (x - min_x) / (max_x - min_x) * (width - left - right)

    def sy(y):
        return height - bottom - y / max_y * (height - top - bottom)

    points = " ".join(f"{sx(d['year']):.1f},{sy(d['reports']):.1f}" for d in data)
    ticks = []
    for year in [1910, 1930, 1950, 1970, 1990, 2010]:
        ticks.append(f'<line x1="{sx(year):.1f}" y1="{top}" x2="{sx(year):.1f}" y2="{height-bottom}" class="grid"/>')
        ticks.append(axis_label(str(year), sx(year), height - 18))
    for value in [0, 2500, 5000, 7500]:
        y = sy(value)
        ticks.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="grid"/>')
        ticks.append(axis_label(str(value), 48, y + 4, "end"))

    band_x = sx(1995)
    band_w = sx(2005) - sx(1995)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
      {chart_style()}
      <rect width="{width}" height="{height}" class="bg"/>
      <text x="{left}" y="26" class="title">Reports by year</text>
      {"".join(ticks)}
      <rect x="{band_x:.1f}" y="{top}" width="{band_w:.1f}" height="{height-top-bottom}" fill="#f2d49c" opacity="0.45"/>
      <text x="{band_x + 8:.1f}" y="{top + 22}" class="note">online reporting era</text>
      <line x1="{band_x:.1f}" y1="{top}" x2="{band_x:.1f}" y2="{height-bottom}" stroke="#8d6b2f" stroke-width="2" stroke-dasharray="4 4"/>
      <text x="{band_x + 8:.1f}" y="{height - bottom - 10}" class="note">1995 split</text>
      <polyline points="{points}" fill="none" stroke="#d65d47" stroke-width="3"/>
      <line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>
      <line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>
    </svg>"""


def annual_annotated_svg() -> str:
    """Static version of the website's annotated annual plot."""
    data = load("annual_reports.json")
    width, height = 900, 440
    left, right, top, bottom = 62, 24, 42, 48
    xs = [d["year"] for d in data]
    ys = [d["reports"] for d in data]
    min_x, max_x = min(xs), max(xs)
    max_y = max(ys) if ys else 1

    def sx(x):
        return left + (x - min_x) / (max_x - min_x) * (width - left - right)

    def sy(y):
        return height - bottom - y / max_y * (height - top - bottom)

    points = " ".join(f"{sx(d['year']):.1f},{sy(d['reports']):.1f}" for d in data)
    fill_points = f"{sx(min_x):.1f},{sy(0):.1f} " + points + f" {sx(max_x):.1f},{sy(0):.1f}"

    def vline(year, color, dash=None, label=None, label_y=0.92):
        x = sx(year)
        style = f'stroke:{color};stroke-width:2;'
        if dash:
            style += f'stroke-dasharray:{dash};'
        out = [f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height-bottom}" style="{style}"/>']
        if label:
            y = top + (height - top - bottom) * label_y
            out.append(
                f'<text x="{x + 8:.1f}" y="{y:.1f}" text-anchor="start" class="note" fill="{color}">{label}</text>'
            )
        return "".join(out)

    ticks = []
    for year in [1910, 1930, 1950, 1970, 1990, 2010]:
        ticks.append(f'<line x1="{sx(year):.1f}" y1="{top}" x2="{sx(year):.1f}" y2="{height-bottom}" class="grid"/>')
        ticks.append(axis_label(str(year), sx(year), height - 18))
    for value in [0, 2500, 5000, 7500]:
        y = sy(value)
        ticks.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="grid"/>')
        ticks.append(axis_label(str(value), 48, y + 4, "end"))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
      {chart_style()}
      <rect width="{width}" height="{height}" class="bg"/>
      <text x="{left}" y="26" class="title">Annual reports (annotated)</text>
      {"".join(ticks)}
      <polygon points="{fill_points}" fill="rgba(63, 111, 159, 0.16)" stroke="none"/>
      <polyline points="{points}" fill="none" stroke="#3f6f9f" stroke-width="3"/>
      {vline(1982, "#d99a2b", "2 6", "E.T.", label_y=0.25)}
      {vline(1993.7, "#17201d", None, "The X-Files", label_y=0.12)}
      {vline(1995, "#d65d47", "6 5", "1995 split", label_y=0.32)}
      <line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>
      <line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>
    </svg>"""


def shapes_svg() -> str:
    data = load("shape_counts.json")[:10]
    width, height = 900, 440
    left, right, top, bottom = 112, 28, 42, 36
    max_v = max(d["reports"] for d in data)
    bar_h = (height - top - bottom) / len(data)
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Top reported shapes</text>']
    for i, d in enumerate(data):
        y = top + i * bar_h + 4
        w = d["reports"] / max_v * (width - left - right)
        parts.append(axis_label(d["shape"], left - 12, y + bar_h * 0.55, "end"))
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h-8:.1f}" rx="3" fill="#117c78"/>')
        parts.append(axis_label(f"{d['reports']:,}", left + w + 8, y + bar_h * 0.55, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def shape_groups_svg() -> str:
    data = load("shape_counts.json")
    counts = {d["shape"]: d["reports"] for d in data}
    total = sum(counts.values())
    groups = [
        ("lights / flashes", ["light", "fireball", "flash"], "#d65d47"),
        ("round forms", ["circle", "sphere", "disk", "oval", "egg"], "#117c78"),
        ("uncertain labels", ["unknown", "other", "changing", "formation", "teardrop"], "#8d6b2f"),
        ("structured forms", ["triangle", "rectangle", "diamond", "chevron", "cylinder", "cigar", "cross", "cone"], "#3f6f9f"),
    ]
    rows = []
    for label, shapes, color in groups:
        reports = sum(counts.get(shape, 0) for shape in shapes)
        rows.append((label, reports, reports / total, color))
    rows.sort(key=lambda row: row[1], reverse=True)

    width, height = 900, 270
    left, right, top = 70, 70, 78
    bar_w, bar_h = width - left - right, 36
    parts = [
        chart_style(),
        f'<rect width="{width}" height="{height}" class="bg"/>',
        f'<text x="{left}" y="30" class="title">Shape labels grouped by visual impression</text>',
        axis_label("Broad analytical grouping of reported labels, not proof of physical object type.", left, 54, "start"),
    ]
    x = left
    for label, reports, share, color in rows:
        w = share * bar_w
        parts.append(f'<rect x="{x:.1f}" y="{top}" width="{w:.1f}" height="{bar_h}" fill="{color}"/>')
        if w > 95:
            parts.append(f'<text x="{x + w / 2:.1f}" y="{top + 23}" text-anchor="middle" fill="#fffdf8" font="700 12px system-ui, sans-serif">{share:.1%}</text>')
        x += w
    parts.append(f'<rect x="{left}" y="{top}" width="{bar_w}" height="{bar_h}" fill="none" stroke="#d8d0c2"/>')

    legend_y = top + 70
    for i, (label, reports, share, color) in enumerate(rows):
        col = i % 2
        row = i // 2
        lx = left + col * 390
        ly = legend_y + row * 44
        parts.append(f'<rect x="{lx}" y="{ly}" width="13" height="13" rx="3" fill="{color}"/>')
        parts.append(axis_label(label, lx + 22, ly + 12, "start"))
        parts.append(axis_label(f"{reports:,} reports ({share:.1%})", lx + 22, ly + 31, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def heatmap_svg() -> str:
    data = load("month_hour.json")
    width, height = 900, 470
    left, right, top, bottom = 54, 28, 42, 42
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    inner_w, inner_h = width - left - right, height - top - bottom
    cell_w, cell_h = inner_w / 24, inner_h / 12
    max_v = max(d["reports"] for d in data)

    def color(value):
        t = math.sqrt(value / max_v) if max_v else 0
        r = int(255 * t + 255 * (1 - t))
        g = int(245 * (1 - t) + 98 * t)
        b = int(205 * (1 - t) + 53 * t)
        return f"rgb({r},{g},{b})"

    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Reports by month and hour</text>']
    for d in data:
        x = left + d["hour"] * cell_w
        y = top + (d["month"] - 1) * cell_h
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w-1:.1f}" height="{cell_h-1:.1f}" fill="{color(d["reports"])}"/>')
    for i, month in enumerate(months):
        parts.append(axis_label(month, left - 10, top + i * cell_h + cell_h * 0.65, "end"))
    for hour in [0, 6, 12, 18, 23]:
        parts.append(axis_label(f"{hour}:00", left + hour * cell_w, height - 16))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def state_bars_svg(mode: str = "reports") -> str:
    """Static version of state ranking (top 12)."""
    rows = load("state_counts.json")
    if mode not in {"reports", "reports_per_million"}:
        raise ValueError("mode must be reports or reports_per_million")
    rows = sorted(rows, key=lambda d: float(d[mode]), reverse=True)[:12]
    width, height = 900, 460
    left, right, top, bottom = 120, 40, 42, 40
    max_v = max(float(d[mode]) for d in rows) if rows else 1.0
    bar_h = (height - top - bottom) / max(1, len(rows))
    title = "US states: raw reports" if mode == "reports" else "US states: reports per million"
    fill = "#3f6f9f" if mode == "reports" else "#d65d47"
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">{title}</text>']
    for i, d in enumerate(rows):
        y = top + i * bar_h + 4
        value = float(d[mode])
        w = value / max_v * (width - left - right)
        parts.append(axis_label(str(d["state"]), left - 12, y + bar_h * 0.55, "end"))
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h-8:.1f}" rx="3" fill="{fill}"/>')
        label = f"{int(value):,}" if mode == "reports" else f"{value:.0f}"
        parts.append(axis_label(label, left + w + 8, y + bar_h * 0.55, "start"))
    note = "Static snapshot; website includes the choropleth + toggle." if mode == "reports" else "Per-capita view (per million residents)."
    parts.append(axis_label(note, left, height - 14, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def area51_svg() -> str:
    area51 = load("area51_summary.json")
    rows = [
        ("Area 51 region", int(area51["nearby_reports"]), "nearby bounding region"),
        ("Las Vegas", int(area51["las_vegas_reports"]), "city reports"),
        ("Nevada", int(area51["nevada_reports"]), "all state reports"),
    ]
    width, height = 900, 320
    left, right, top, bottom = 170, 50, 42, 40
    max_v = max(v for _, v, _ in rows) if rows else 1
    bar_h = (height - top - bottom) / len(rows)
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Area 51 vs nearby reporting</text>']
    for i, (label, value, note) in enumerate(rows):
        y = top + i * bar_h + 6
        w = value / max_v * (width - left - right)
        parts.append(axis_label(label, left - 12, y + bar_h * 0.55, "end"))
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h-12:.1f}" rx="3" fill="#d99a2b"/>')
        parts.append(axis_label(f"{value:,}", left + w + 8, y + bar_h * 0.55, "start"))
        parts.append(axis_label(note, left + 8, y + bar_h * 0.55, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def duration_boxplot_svg() -> str:
    """Quantile box summaries on a log x-axis (static)."""
    rows = load("duration_by_shape.json")[:14]
    width, height = 900, 520
    left, right, top, bottom = 140, 40, 42, 54
    x_min, x_max = 1.0, 86400.0

    def sx(v):
        v = max(x_min, min(x_max, float(v)))
        return left + (math.log10(v) - math.log10(x_min)) / (math.log10(x_max) - math.log10(x_min)) * (width - left - right)

    row_h = (height - top - bottom) / max(1, len(rows))
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Duration distribution by shape (log scale)</text>']
    ticks = [(1, "1s"), (10, "10s"), (60, "1m"), (600, "10m"), (3600, "1h"), (21600, "6h"), (86400, "24h")]
    for v, label in ticks:
        x = sx(v)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height-bottom}" class="grid"/>')
        parts.append(axis_label(label, x, height - 18))

    for i, d in enumerate(rows):
        y_mid = top + i * row_h + row_h * 0.55
        parts.append(axis_label(d["shape"], left - 12, y_mid, "end"))
        x0, x1 = sx(d["p05"]), sx(d["p95"])
        q1, q3 = sx(d["p25"]), sx(d["p75"])
        med = sx(d["median"])
        parts.append(f'<line x1="{x0:.1f}" y1="{y_mid:.1f}" x2="{x1:.1f}" y2="{y_mid:.1f}" stroke="#8d6b2f" stroke-width="2"/>')
        box_y = y_mid - row_h * 0.22
        box_h = row_h * 0.44
        parts.append(f'<rect x="{q1:.1f}" y="{box_y:.1f}" width="{(q3-q1):.1f}" height="{box_h:.1f}" fill="rgba(141,107,47,0.22)" stroke="#8d6b2f"/>')
        parts.append(f'<line x1="{med:.1f}" y1="{box_y:.1f}" x2="{med:.1f}" y2="{(box_y+box_h):.1f}" stroke="#8d6b2f" stroke-width="2"/>')

    parts.append(axis_label("box = p25–p75, whiskers = p05–p95", left, height - 14, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def country_bars_svg() -> str:
    rows = load("country_counts.json")[:6]
    width, height = 900, 380
    left, right, top, bottom = 180, 50, 42, 40
    max_v = max(d["reports"] for d in rows) if rows else 1
    bar_h = (height - top - bottom) / len(rows)
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Country report counts (top)</text>']
    for i, d in enumerate(rows):
        y = top + i * bar_h + 6
        w = d["reports"] / max_v * (width - left - right)
        parts.append(axis_label(d["country"], left - 12, y + bar_h * 0.55, "end"))
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h-12:.1f}" rx="3" fill="#3f6f9f"/>')
        parts.append(axis_label(f"{d['reports']:,}", left + w + 8, y + bar_h * 0.55, "start"))
    parts.append(axis_label("This reflects reporting pipeline reach, not a balanced global survey.", left, height - 14, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def word_cloud_svg() -> str:
    words = load("summary.json")["top_words"][:28]
    width, height = 900, 420
    left = 42
    max_count = max(w["count"] for w in words) if words else 1

    def font_size(c):
        t = math.sqrt(c / max_count)
        return 16 + t * 36

    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Common words in report comments</text>']
    cx, cy = width * 0.52, height * 0.56
    palette = ["#117c78", "#d65d47", "#d99a2b", "#3f6f9f", "#8d6b2f", "#17201d"]
    for i, w in enumerate(words):
        angle = i * 2.399963
        radius = math.sqrt(i) * 14
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        size = font_size(w["count"])
        color = palette[i % len(palette)]
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'fill="{color}" font-size="{size:.1f}" font-family="system-ui, sans-serif">{w["word"]}</text>'
        )
    parts.append(axis_label("A vocabulary of observation (light, bright, moving, colors) more than certainty.", left, height - 14, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def hotspot_decade_svg(decade: int = 2000) -> str:
    """Static decade snapshot of hotspot bins (proxy for the slider view)."""
    rows = [d for d in load("hex_decade_bins.json") if int(d["decade"]) == int(decade)]
    rows = sorted(rows, key=lambda d: int(d["reports"]), reverse=True)[:500]
    width, height = 900, 520
    left, right, top, bottom = 28, 28, 42, 42
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Hotspot decade snapshot: {decade}s</text>']
    if not rows:
        parts.append(axis_label("No data for this decade.", left, top + 40, "start"))
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'

    lons = [float(d["lon"]) for d in rows]
    lats = [float(d["lat"]) for d in rows]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    max_reports = max(int(d["reports"]) for d in rows)

    def sx(lon):
        return left + (lon - min_lon) / (max_lon - min_lon + 1e-9) * (width - left - right)

    def sy(lat):
        return height - bottom - (lat - min_lat) / (max_lat - min_lat + 1e-9) * (height - top - bottom)

    for d in rows:
        r = 2.0 + math.sqrt(int(d["reports"]) / max_reports) * 12.0
        parts.append(
            f'<circle cx="{sx(float(d["lon"])):.1f}" cy="{sy(float(d["lat"])):.1f}" r="{r:.1f}" '
            f'fill="#117c78" fill-opacity="0.42" stroke="#17201d" stroke-width="0.3"/>'
        )

    parts.append(axis_label("Static proxy for the slider view (each dot is one spatial bin).", left, height - 14, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def hotspots_svg() -> str:
    data = load("hotspots.json")[:12]
    width, height = 900, 430
    left, right, top, bottom = 64, 28, 42, 52
    max_reports = max(d["total_reports"] for d in data)
    max_years = max(d["active_years"] for d in data)
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Persistent hotspot bins: total reports vs active years</text>']
    for d in data:
        x = left + d["total_reports"] / max_reports * (width - left - right)
        y = height - bottom - d["active_years"] / max_years * (height - top - bottom)
        r = 5 + math.sqrt(d["total_reports"]) * 0.8
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#d65d47" fill-opacity="0.58" stroke="#7b2f23"/>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>')
    parts.append(axis_label("total reports in bin", width / 2, height - 12))
    parts.append(axis_label("active years", 18, height / 2, "middle"))
    parts.append(axis_label("Each point is one high-persistence spatial bin.", left + 8, height - bottom - 10, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def city_hotspots_svg() -> str:
    data = load("city_counts.json")[:12]
    width, height = 900, 440
    left, right, top, bottom = 132, 36, 42, 36
    max_v = max(d["reports"] for d in data)
    bar_h = (height - top - bottom) / len(data)
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Top US city hotspots</text>']
    for i, d in enumerate(data):
        y = top + i * bar_h + 4
        w = d["reports"] / max_v * (width - left - right)
        label = f'{d["city"]}, {d["state"]}'
        parts.append(axis_label(label, left - 12, y + bar_h * 0.55, "end"))
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h-8:.1f}" rx="3" fill="#d65d47"/>')
        parts.append(axis_label(f"{d['reports']:,}", left + w + 8, y + bar_h * 0.55, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def duration_by_shape_svg() -> str:
    data = load("duration_by_shape.json")[:16]
    width, height = 900, 470
    left, right, top, bottom = 112, 36, 42, 42
    max_v = max(d["median"] for d in data)
    bar_h = (height - top - bottom) / len(data)

    def minutes(seconds):
        return f"{seconds / 60:.0f}m"

    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', f'<text x="{left}" y="26" class="title">Median duration by common shape</text>']
    for i, d in enumerate(data):
        y = top + i * bar_h + 4
        w = d["median"] / max_v * (width - left - right)
        parts.append(axis_label(d["shape"], left - 12, y + bar_h * 0.55, "end"))
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h-8:.1f}" rx="3" fill="#8d6b2f"/>')
        parts.append(axis_label(minutes(d["median"]), left + w + 8, y + bar_h * 0.55, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def era_comparison_svg() -> str:
    data = load("duration_by_era_shape.json")
    width, height = 900, 320
    left, top = 70, 62
    card_w, card_h = 360, 190
    parts = [chart_style(), f'<rect width="{width}" height="{height}" class="bg"/>', '<text x="70" y="30" class="title">Before and after the web</text>']
    for i, d in enumerate(data):
        x = left + i * (card_w + 70)
        parts.append(f'<rect x="{x}" y="{top}" width="{card_w}" height="{card_h}" rx="8" fill="#fffdf8" stroke="#d8d0c2"/>')
        parts.append(axis_label(d["label"], x + 18, top + 30, "start"))
        parts.append(f'<text x="{x + 18}" y="{top + 76}" fill="#17201d" font="700 34px system-ui, sans-serif">{d["reports"]:,}</text>')
        parts.append(axis_label("reports", x + 18, top + 98, "start"))
        parts.append(axis_label(f'Median duration: {d["median"] / 60:.0f}m', x + 18, top + 132, "start"))
        parts.append(axis_label(f'Top shape: {d["top_shape"]} ({d["top_shape_share"]:.1%})', x + 18, top + 158, "start"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def main() -> None:
    write("annual_reports.svg", annual_svg())
    write("annual_annotated.svg", annual_annotated_svg())
    write("shape_counts.svg", shapes_svg())
    write("shape_groups.svg", shape_groups_svg())
    write("month_hour_heatmap.svg", heatmap_svg())
    write("hotspot_persistence.svg", hotspots_svg())
    write("hotspot_decade_2000.svg", hotspot_decade_svg(2000))
    write("city_hotspots.svg", city_hotspots_svg())
    write("state_bars_reports.svg", state_bars_svg("reports"))
    write("state_bars_per_million.svg", state_bars_svg("reports_per_million"))
    write("area51_comparison.svg", area51_svg())
    write("duration_by_shape.svg", duration_by_shape_svg())
    write("duration_boxplot.svg", duration_boxplot_svg())
    write("era_comparison.svg", era_comparison_svg())
    write("country_bars.svg", country_bars_svg())
    write("word_cloud.svg", word_cloud_svg())
    print(f"Wrote notebook figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
