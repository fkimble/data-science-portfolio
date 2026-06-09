"""Report rendering for CareRoute Equity Lab."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_wait_drift_svg(path: Path, drift: pd.DataFrame) -> None:
    """Write an SVG bar chart for wait-time drift."""

    top = drift.sort_values(["wait_drift_days", "leakage_drift_delta"], ascending=[False, False]).head(8)
    width, height = 940, 320
    max_delta = max(float(top["wait_drift_days"].max()), 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/>']
    parts.append('<text x="20" y="28" font-size="18" font-weight="700">Top referral wait-time drift cohorts</text>')
    for i, row in top.iterrows():
        label = " / ".join([str(row.get(col, "")) for col in ["patient_segment", "specialty", "region"] if col in row])
        y = 46 + len(parts) % 1000
        y = 48 + list(top.index).index(i) * 32
        bar_width = int((float(row["wait_drift_days"]) / max_delta) * 500)
        parts.append(f'<text x="20" y="{y + 16}" font-size="12">{label}</text>')
        parts.append(f'<rect x="350" y="{y}" width="{bar_width}" height="20" fill="#2a6f97" />')
        parts.append(f'<text x="{360 + bar_width}" y="{y + 15}" font-size="12">{float(row["wait_drift_days"]):.1f} days</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def write_leakage_heatmap_svg(path: Path, rates: pd.DataFrame) -> None:
    """Write a specialty x patient-segment leakage heatmap."""

    pivot = rates.pivot_table(index="specialty", columns="patient_segment", values="leakage_rate", fill_value=0)
    cell_w, cell_h = 120, 38
    width = 190 + cell_w * len(pivot.columns)
    height = 82 + cell_h * len(pivot.index)
    max_rate = max(float(pivot.max().max()), 0.01)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/>']
    parts.append('<text x="20" y="28" font-size="18" font-weight="700">Referral leakage by specialty and segment</text>')
    for c, col in enumerate(pivot.columns):
        parts.append(f'<text x="{170 + c * cell_w}" y="58" font-size="12">{col}</text>')
    for r, idx in enumerate(pivot.index):
        y = 70 + r * cell_h
        parts.append(f'<text x="20" y="{y + 23}" font-size="12">{idx}</text>')
        for c, col in enumerate(pivot.columns):
            value = float(pivot.loc[idx, col])
            intensity = int(245 - (value / max_rate) * 170)
            color = f"rgb(245,{intensity},{intensity})"
            x = 150 + c * cell_w
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 4}" height="{cell_h - 4}" fill="{color}" stroke="#ffffff"/>')
            parts.append(f'<text x="{x + 28}" y="{y + 22}" font-size="12">{_pct(value)}</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def render_insights(path: Path, summary: pd.DataFrame, drift: pd.DataFrame, equity: pd.DataFrame, backlog: pd.DataFrame) -> None:
    """Render an executive Markdown report."""

    values = dict(zip(summary["metric"], summary["value"]))
    stable_drift = drift[drift["referrals_recent"].ge(30)]
    top_drift = (stable_drift if not stable_drift.empty else drift).iloc[0]
    top_equity = equity.iloc[0]
    top_backlog = backlog.iloc[0]
    body = f"""# CareRoute Equity Lab - Executive Insights

Synthetic data only. This report summarizes specialty-referral access, leakage, and wait-time patterns.

## Headline Metrics

- Referral volume: {int(values["referral_volume"]):,}
- Completion rate: {_pct(float(values["completion_rate"]))}
- Referral leakage rate: {_pct(float(values["leakage_rate"]))}
- No-show rate: {_pct(float(values["no_show_rate"]))}
- Median wait days: {float(values["median_wait_days"]):.0f}
- Long-wait share: {_pct(float(values["long_wait_share"]))}
- Deferred visit value: ${float(values["deferred_visit_value"]):,.0f}

## Biggest Drift Signal

The largest leakage drift is `{top_drift.get("patient_segment")}` / `{top_drift.get("specialty")}` with a leakage delta of {_pct(float(top_drift["leakage_drift_delta"]))} and wait drift of {float(top_drift["wait_drift_days"]):.1f} days.

## Largest Equity Gap

The largest estimated excess leakage value appears in `{top_equity.get("patient_segment")}` / `{top_equity.get("payer")}` / `{top_equity.get("specialty")}`. The model estimates ${float(top_equity["estimated_excess_value"]):,.0f} in excess leaked referral value versus the portfolio-average leakage rate.

## Recommended First Bet

**{top_backlog["intervention"]}**

- Target issue: `{top_backlog["target_issue"]}`
- Affected referrals: {int(top_backlog["affected_referrals"]):,}
- Expected visit value at risk: ${float(top_backlog["expected_visit_value_at_risk"]):,.0f}
- Impact score: {float(top_backlog["impact_score"]):,.0f}

## Artifacts

- `reports/metric_summary.csv`
- `reports/access_rates.csv`
- `reports/drift_table.csv`
- `reports/equity_gap_table.csv`
- `reports/intervention_backlog.csv`
- `reports/figures/leakage_heatmap.svg`
- `reports/figures/wait_drift_bars.svg`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
