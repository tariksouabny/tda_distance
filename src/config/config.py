import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PipelineConfig:
    crash_eve_date: str = "2020-04-19"
    lookback: int = 40
    start_date: str = "2018-01-01"
    end_date: str = "2020-03-01"
    output_dir: str = "outputs/figures"
    log_dir: str = "outputs/logs"
    show_plots: bool = False
    data_cache_path: str = "data/raw/sp500_raw_prices.csv"
    ticker_cache_path: str = "data/external/sp500_tickers.csv"
    distance_matrix_path: str = "data/processed/distance_matrix.csv"


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged.get(key), value)
        else:
            merged[key] = value
    return merged


def load_config(config_path: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> PipelineConfig:
    default_config = {
        "pipeline": {
            "crash_eve_date": "2020-04-19",
            "lookback": 40,
            "start_date": "2018-01-01",
            "end_date": "2020-03-01",
            "output_dir": "outputs/figures",
            "log_dir": "outputs/logs",
            "show_plots": False,
            "data_cache_path": "data/raw/sp500_raw_prices.csv",
            "ticker_cache_path": "data/external/sp500_tickers.csv",
            "distance_matrix_path": "data/processed/distance_matrix.csv",
        }
    }

    config_data = default_config
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as handle:
            config_data = _deep_merge(default_config, json.load(handle))

    if overrides:
        normalized_overrides = dict(overrides)
        if "pipeline" not in normalized_overrides and any(key in normalized_overrides for key in ["crash_eve_date", "lookback", "start_date", "end_date", "output_dir", "log_dir", "show_plots", "data_cache_path", "ticker_cache_path", "distance_matrix_path"]):
            normalized_overrides = {"pipeline": normalized_overrides}
        config_data = _deep_merge(config_data, normalized_overrides)

    pipeline_cfg = config_data.get("pipeline", {})
    return PipelineConfig(
        crash_eve_date=pipeline_cfg.get("crash_eve_date", "2020-04-19"),
        lookback=int(pipeline_cfg.get("lookback", 40)),
        start_date=pipeline_cfg.get("start_date", "2018-01-01"),
        end_date=pipeline_cfg.get("end_date", "2020-03-01"),
        output_dir=pipeline_cfg.get("output_dir", "outputs/figures"),
        log_dir=pipeline_cfg.get("log_dir", "outputs/logs"),
        show_plots=bool(pipeline_cfg.get("show_plots", False)),
        data_cache_path=pipeline_cfg.get("data_cache_path", "data/raw/sp500_raw_prices.csv"),
        ticker_cache_path=pipeline_cfg.get("ticker_cache_path", "data/external/sp500_tickers.csv"),
        distance_matrix_path=pipeline_cfg.get("distance_matrix_path", "data/processed/distance_matrix.csv"),
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the S&P 500 TDA pipeline")
    parser.add_argument("command", nargs="?", default="run", choices=["download", "run", "report"], help="Pipeline action to execute")
    parser.add_argument("--config", default=None, help="Path to a JSON configuration file")
    parser.add_argument("--crash-eve-date", default=None, help="Date for the analysis window")
    parser.add_argument("--lookback", type=int, default=None, help="Number of days to use for the lookback window")
    parser.add_argument("--start-date", default=None, help="Start date for the data download")
    parser.add_argument("--end-date", default=None, help="End date for the data download")
    parser.add_argument("--output-dir", default=None, help="Directory where generated figures are stored")
    parser.add_argument("--log-dir", default=None, help="Directory where logs are stored")
    parser.add_argument("--show-plots", action="store_true", help="Display plots while the pipeline runs")
    return parser


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)
