"""Report rendering for ClaimFlow Parity Lab."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_bar_svg(path: Path, drift: pd.DataFrame, label_col: str = "payer") -> None:
    """Write a small SVG bar chart for top drift cohorts."""

    top = drift.head(8).copy()
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 320
    max_delta = max(top["drift_delta"].max(), 0.01)
    rows = []
    for i, row in top.iterrows():
        label_parts = [str(row.get(col, "")) for col in ["payer", "service_line"] if col in row]
        label = " / ".join(label_parts)
        bar_width = int((row["drift_delta"] / max_delta) * 520)
        y = 42 + i * 32
        rows.append(f'<text x="20" y="{y + 17}" font-size="13">{label}</text>')
        rows.append(f'<rect x="280" y="{y}" width="{bar_width}" height="20" fill="#1f77b4" />')
        rows.append(f'<text x="{290 + bar_width}" y="{y + 15}" font-size="12">{_pct(row["drift_delta"])}</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="20" y="25" font-size="18" font-weight="700">Top denial-rate drift cohorts</text>{"".join(rows)}</svg>'
    path.write_text(svg, encoding="utf-8")


def write_heatmap_svg(path: Path, rates: pd.DataFrame) -> None:
    """Write a compact payer x service-line denial heatmap."""

    pivot = rates.pivot_table(index="payer", columns="service_line", values="denial_rate", fill_value=0)
    cell_w, cell_h = 118, 42
    width = 180 + cell_w * len(pivot.columns)
    height = 80 + cell_h * len(pivot.index)
    max_rate = max(float(pivot.max().max()), 0.01)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/>']
    parts.append('<text x="20" y="28" font-size="18" font-weight="700">Denial-rate heatmap</text>')
    for c, col in enumerate(pivot.columns):
        parts.append(f'<text x="{170 + c * cell_w}" y="58" font-size="11" transform="rotate(-20 {170 + c * cell_w},58)">{col}</text>')
    for r, idx in enumerate(pivot.index):
        y = 70 + r * cell_h
        parts.append(f'<text x="20" y="{y + 26}" font-size="13">{idx}</text>')
        for c, col in enumerate(pivot.columns):
            value = float(pivot.loc[idx, col])
            intensity = int(245 - (value / max_rate) * 165)
            color = f"rgb({intensity},{intensity + 20},245)"
            x = 150 + c * cell_w
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 4}" height="{cell_h - 4}" fill="{color}" stroke="#ffffff"/>')
            parts.append(f'<text x="{x + 22}" y="{y + 24}" font-size="12">{_pct(value)}</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def render_insights(
    path: Path,
    summary: pd.DataFrame,
    drift: pd.DataFrame,
    parity: pd.DataFrame,
    backlog: pd.DataFrame,
) -> None:
    """Render the executive Markdown report."""

    values = dict(zip(summary["metric"], summary["value"]))
    top_drift = drift.iloc[0]
    top_parity = parity.iloc[0]
    top_backlog = backlog.iloc[0]
    body = f"""# ClaimFlow Parity Lab - Executive Insights

Synthetic data only. This report summarizes a generated prior-authorization and claims workflow dataset.

## Headline Metrics

- Claim volume: {int(values["claim_volume"]):,}
- Denial rate: {_pct(float(values["denial_rate"]))}
- Avoidable denial share: {_pct(float(values["avoidable_denial_share"]))}
- Appeal rate: {_pct(float(values["appeal_rate"]))}
- Overturn rate: {_pct(float(values["overturn_rate"]))}
- Median cycle time: {float(values["median_cycle_days"]):.0f} days
- Denied reimbursement at risk: ${float(values["denied_reimbursement_at_risk"]):,.0f}

## Biggest Drift Signal

The largest recent denial-rate increase is `{top_drift.get("payer")}` / `{top_drift.get("service_line")}` with a drift delta of {_pct(float(top_drift["drift_delta"]))}. This is the cohort to inspect first for policy changes, staffing gaps, or documentation friction.

## Largest Access-Parity Gap

The largest estimated excess-denial value appears in `{top_parity.get("patient_segment")}` / `{top_parity.get("payer")}` / `{top_parity.get("service_line")}`. The model estimates ${float(top_parity["estimated_excess_value"]):,.0f} in excess value versus the population-average denial rate.

## Recommended First Bet

**{top_backlog["intervention"]}**

- Denial reason: `{top_backlog["denial_reason"]}`
- Avoidable denials: {int(top_backlog["avoidable_denials"]):,}
- Reimbursement at risk: ${float(top_backlog["reimbursement_at_risk"]):,.0f}
- Impact score: {float(top_backlog["impact_score"]):,.0f}

## Artifacts

- `reports/metric_summary.csv`
- `reports/drift_table.csv`
- `reports/parity_table.csv`
- `reports/intervention_backlog.csv`
- `reports/figures/denial_heatmap.svg`
- `reports/figures/drift_bars.svg`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
