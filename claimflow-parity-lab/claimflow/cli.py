"""Command-line interface for ClaimFlow Parity Lab."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

from claimflow.metrics import drift_table, group_denial_rates, intervention_backlog, metric_summary
from claimflow.parity import parity_table
from claimflow.report import render_insights, write_bar_svg, write_heatmap_svg
from claimflow.synthetic import GeneratorConfig, write_claimflows
from claimflow.validate import require_valid, validate_claimflows


ROOT = Path.cwd()
DATA_PATH = ROOT / "data" / "claimflow_events.csv"
REPORTS = ROOT / "reports"


def _load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Run generate first.")
    return pd.read_csv(path)


def cmd_generate(args: argparse.Namespace) -> None:
    config = GeneratorConfig(patients=args.patients, days=args.days, seed=args.seed)
    df = write_claimflows(DATA_PATH, config)
    print(f"generated {len(df):,} synthetic workflows -> {DATA_PATH}")


def cmd_validate(_: argparse.Namespace) -> None:
    df = _load_data()
    result = validate_claimflows(df)
    if result.passed:
        print("validation passed")
        return
    for error in result.errors:
        print(f"validation error: {error}")
    raise SystemExit(1)


def cmd_analyze(_: argparse.Namespace) -> None:
    df = _load_data()
    require_valid(df)
    REPORTS.mkdir(exist_ok=True)
    rates = group_denial_rates(df, ["payer", "service_line"])
    summary = metric_summary(df)
    drift = drift_table(df, ["payer", "service_line"])
    parity = parity_table(df, ["patient_segment", "payer", "service_line"])
    backlog = intervention_backlog(df)
    summary.to_csv(REPORTS / "metric_summary.csv", index=False)
    rates.to_csv(REPORTS / "denial_rates.csv", index=False)
    drift.to_csv(REPORTS / "drift_table.csv", index=False)
    parity.to_csv(REPORTS / "parity_table.csv", index=False)
    backlog.to_csv(REPORTS / "intervention_backlog.csv", index=False)
    write_heatmap_svg(REPORTS / "figures" / "denial_heatmap.svg", rates)
    write_bar_svg(REPORTS / "figures" / "drift_bars.svg", drift)
    print(f"analysis written -> {REPORTS}")


def cmd_report(_: argparse.Namespace) -> None:
    needed = ["metric_summary.csv", "drift_table.csv", "parity_table.csv", "intervention_backlog.csv"]
    missing = [name for name in needed if not (REPORTS / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing report inputs: {', '.join(missing)}. Run analyze first.")
    render_insights(
        REPORTS / "INSIGHTS.md",
        pd.read_csv(REPORTS / "metric_summary.csv"),
        pd.read_csv(REPORTS / "drift_table.csv"),
        pd.read_csv(REPORTS / "parity_table.csv"),
        pd.read_csv(REPORTS / "intervention_backlog.csv"),
    )
    print(f"report written -> {REPORTS / 'INSIGHTS.md'}")


def cmd_demo(args: argparse.Namespace) -> None:
    cmd_generate(args)
    cmd_validate(args)
    cmd_analyze(args)
    cmd_report(args)


def cmd_clean(_: argparse.Namespace) -> None:
    if DATA_PATH.exists():
        DATA_PATH.unlink()
    if REPORTS.exists():
        for path in REPORTS.glob("*.csv"):
            path.unlink()
        if (REPORTS / "INSIGHTS.md").exists():
            (REPORTS / "INSIGHTS.md").unlink()
        figures = REPORTS / "figures"
        if figures.exists():
            shutil.rmtree(figures)
            figures.mkdir(parents=True, exist_ok=True)
    print("generated artifacts removed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic prior-auth and claims-denial parity analytics.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["generate", "demo"]:
        p = sub.add_parser(name)
        p.add_argument("--patients", type=int, default=5000)
        p.add_argument("--days", type=int, default=180)
        p.add_argument("--seed", type=int, default=42)
        p.set_defaults(func=cmd_generate if name == "generate" else cmd_demo)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("analyze").set_defaults(func=cmd_analyze)
    sub.add_parser("report").set_defaults(func=cmd_report)
    sub.add_parser("clean").set_defaults(func=cmd_clean)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
