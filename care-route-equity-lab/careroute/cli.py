"""Command-line interface for CareRoute Equity Lab."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

from careroute.equity import equity_gap_table
from careroute.metrics import access_rates, drift_table, intervention_backlog, metric_summary
from careroute.report import render_insights, write_leakage_heatmap_svg, write_wait_drift_svg
from careroute.synthetic import GeneratorConfig, generate_referrals
from careroute.validate import require_valid, validate_referrals


ROOT = Path.cwd()
DATA_PATH = ROOT / "data" / "referral_routes.csv"
REPORTS = ROOT / "reports"


def _load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Run generate first.")
    return pd.read_csv(path)


def cmd_generate(args: argparse.Namespace) -> None:
    config = GeneratorConfig(referrals=args.referrals, days=args.days, seed=args.seed)
    df = generate_referrals(config)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"generated {len(df):,} synthetic referrals -> {DATA_PATH}")


def cmd_validate(_: argparse.Namespace) -> None:
    result = validate_referrals(_load_data())
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
    rates = access_rates(df, ["patient_segment", "specialty"])
    summary = metric_summary(df)
    drift = drift_table(df, ["patient_segment", "specialty"])
    equity = equity_gap_table(df, ["patient_segment", "payer", "specialty"])
    backlog = intervention_backlog(df)
    summary.to_csv(REPORTS / "metric_summary.csv", index=False)
    rates.to_csv(REPORTS / "access_rates.csv", index=False)
    drift.to_csv(REPORTS / "drift_table.csv", index=False)
    equity.to_csv(REPORTS / "equity_gap_table.csv", index=False)
    backlog.to_csv(REPORTS / "intervention_backlog.csv", index=False)
    write_leakage_heatmap_svg(REPORTS / "figures" / "leakage_heatmap.svg", rates)
    write_wait_drift_svg(REPORTS / "figures" / "wait_drift_bars.svg", drift)
    print(f"analysis written -> {REPORTS}")


def cmd_report(_: argparse.Namespace) -> None:
    needed = ["metric_summary.csv", "drift_table.csv", "equity_gap_table.csv", "intervention_backlog.csv"]
    missing = [name for name in needed if not (REPORTS / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing report inputs: {', '.join(missing)}. Run analyze first.")
    render_insights(
        REPORTS / "INSIGHTS.md",
        pd.read_csv(REPORTS / "metric_summary.csv"),
        pd.read_csv(REPORTS / "drift_table.csv"),
        pd.read_csv(REPORTS / "equity_gap_table.csv"),
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
    parser = argparse.ArgumentParser(description="Synthetic specialty-referral access and equity analytics.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["generate", "demo"]:
        p = sub.add_parser(name)
        p.add_argument("--referrals", type=int, default=6000)
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
