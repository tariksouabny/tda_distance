import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import persim
from ripser import ripser

from src.config import PipelineConfig, load_config, parse_args
from src.data.data_engine import get_data_df, get_sp500_tickers
from src.features.tda_math import get_distance_matrix
from src.utils.logger import get_logger
from src.visualization.visualization import generate_mapper_graph

logger = get_logger(__name__)


def build_overrides(args) -> dict:
    overrides = {}
    if args.crash_eve_date:
        overrides["pipeline"] = {"crash_eve_date": args.crash_eve_date}
    if args.lookback is not None:
        overrides.setdefault("pipeline", {})["lookback"] = args.lookback
    if args.start_date:
        overrides.setdefault("pipeline", {})["start_date"] = args.start_date
    if args.end_date:
        overrides.setdefault("pipeline", {})["end_date"] = args.end_date
    if args.output_dir:
        overrides.setdefault("pipeline", {})["output_dir"] = args.output_dir
    if args.log_dir:
        overrides.setdefault("pipeline", {})["log_dir"] = args.log_dir
    if args.show_plots:
        overrides.setdefault("pipeline", {})["show_plots"] = True
    return overrides


def resolve_config(args) -> PipelineConfig:
    overrides = build_overrides(args)
    return load_config(config_path=args.config, overrides=overrides)


def download_data(config: PipelineConfig):
    logger.info("Downloading market data and ticker cache...")
    universe = get_sp500_tickers(filepath=config.ticker_cache_path)
    get_data_df(
        universe,
        start_date=config.start_date,
        end_date=config.end_date,
        filepath=config.data_cache_path,
    )
    logger.info("Download step completed.")


def run_tda_pipeline(config: PipelineConfig | None = None):
    if config is None:
        config = resolve_config(parse_args())

    logger.info("--- Starting S&P 500 TDA Pipeline ---")
    crash_eve_date = config.crash_eve_date
    lookback = config.lookback

    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.log_dir, exist_ok=True)

    universe = get_sp500_tickers(filepath=config.ticker_cache_path)
    data_df = get_data_df(
        universe,
        start_date=config.start_date,
        end_date=config.end_date,
        filepath=config.data_cache_path,
    )
    valid_tickers = data_df.columns.tolist()

    logger.info(f"\nCalculating distance matrix for {crash_eve_date}...")
    distance_matrix = get_distance_matrix(
        data_df,
        target_date=crash_eve_date,
        lookback=lookback,
        save_path=config.distance_matrix_path,
    )

    logger.info("\nComputing Persistent Homology...")
    tda_results = ripser(distance_matrix, maxdim=1, distance_matrix=True)
    diagrams = tda_results["dgms"]

    logger.info("Plotting Persistence Diagram...")
    plt.figure(figsize=(8, 6))
    persim.plot_diagrams(diagrams, show=False)
    plt.title(f"S&P 500 Persistence Diagram: {crash_eve_date}")
    plt.savefig(os.path.join(config.output_dir, f"persistence_diagram_{crash_eve_date}.png"))
    if config.show_plots:
        plt.show(block=False)
        plt.pause(3)

    try:
        end_idx = data_df.index.get_indexer([pd.to_datetime(crash_eve_date)], method="ffill")[0]
    except KeyError:
        end_idx = len(data_df) - 1

    window_data = data_df.iloc[end_idx - lookback : end_idx]
    html_filename = os.path.join(config.output_dir, f"sp500_topology_{crash_eve_date}.html")
    generate_mapper_graph(window_data, distance_matrix, valid_tickers, output_filename=html_filename)
    plt.close("all")
    logger.info("\n--- Pipeline Complete! ---")


def generate_report(config: PipelineConfig):
    logger.info("Generating pipeline report...")
    output_files = [
        os.path.join(config.output_dir, f"persistence_diagram_{config.crash_eve_date}.png"),
        os.path.join(config.output_dir, f"sp500_topology_{config.crash_eve_date}.html"),
    ]

    print("Pipeline report")
    print(f"- Crash event date: {config.crash_eve_date}")
    print(f"- Lookback window: {config.lookback}")
    print(f"- Output directory: {config.output_dir}")
    print("- Generated files:")
    for file_path in output_files:
        exists = Path(file_path).exists()
        print(f"  - {file_path} [{'present' if exists else 'missing'}]")


def main():
    args = parse_args()
    config = resolve_config(args)

    if args.command == "download":
        download_data(config)
    elif args.command == "run":
        run_tda_pipeline(config)
    elif args.command == "report":
        generate_report(config)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()