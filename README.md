# tda_distance

**WIP: a Python library for topological data analysis on financial data.**

This project started with a question: how does the structure of relationships between stocks change around a market crash?

I built an S&P 500 analysis pipeline that converts stock-return correlations into distances, computes persistent homology, and creates interactive Mapper graphs. I’m now working toward turning that pipeline into a reusable library for financial TDA.

## Research motivation

Individual price charts show how each stock moves. I wanted to investigate how stocks move relative to one another, and whether topology could help describe the structure of those relationships.

The current approach treats each stock as a point whose relationships to other stocks are determined by its recent returns. Persistent homology examines connected components and loops across distance thresholds. Mapper provides a complementary visualization of overlapping clusters.

The research is exploratory. A topological feature is something to investigate; its presence alone does not establish an economic explanation or a trading signal.

## Current implementation

The pipeline:

1. Loads an S&P 500 ticker list and historical market data, using local caches when available.
2. Calculates daily returns and filters assets with missing return observations.
3. Selects a historical window before the analysis date.
4. Converts Pearson correlations into a distance matrix.
5. Uses Ripser to compute persistent homology in dimensions 0 and 1.
6. Exports a persistence diagram, an interactive Mapper graph, and the distance matrix.

The code also includes command-line configuration, logging, and tests for configuration, data handling, and selected error cases.

## From correlations to distances

For stocks (i) and (j), the pipeline uses:

$$
d(i,j) = \sqrt{2(1-\rho\_{ij})}
$$

where (\rho\_{ij}) is the Pearson correlation between their returns within the selected window.

This maps correlation to a distance between 0 and 2:

- Correlation of **1** gives distance **0**.
- Correlation of **0** gives distance **√2**.
- Correlation of **−1** gives distance **2**.

The construction corresponds to Euclidean distance between centered, unit-normalized return vectors. It gives the analysis a geometric representation of how assets move together.

## Two views of market structure

### Persistent homology

Ripser takes the distance matrix and computes:

- **H₀:** connected components and the thresholds at which they merge.
- **H₁:** loops and the thresholds over which they persist.

The results are saved as persistence diagrams.

### Mapper

The visualization uses a two-dimensional multidimensional-scaling projection as its lens, an overlapping cover, and DBSCAN clustering with correlation distance.

The resulting HTML graph can be explored using ticker tooltips. Mapper and persistent homology are separate analyses; loops in a Mapper graph should not automatically be interpreted as the H₁ features in a persistence diagram.

## Running the pipeline

Use Python 3.10 or later. From the repository root, install the dependencies:

```bash
pip install -r requirements.txt
```

Run an analysis with an explicit date range and lookback:

```bash
python main.py run --start-date 2018-01-01 --end-date 2020-03-01 --crash-eve-date 2020-02-19 --lookback 40
```

The lookback counts rows of trading observations. The selected window excludes the resolved analysis-date row; non-trading dates are resolved to the preceding available observation.

Other commands:

```bash
# Load or download the market data
python main.py download --start-date 2018-01-01 --end-date 2020-03-01

# Check whether expected output files exist
python main.py report --crash-eve-date 2020-02-19

# See available options
python main.py --help

# Run the tests
python -m unittest discover -s tests
```

The optional `--config` argument currently accepts **JSON**. YAML configuration loading is not implemented.

## Outputs

By default, the pipeline writes:

- Persistence diagrams and interactive HTML graphs to `outputs/figures/`.
- A labeled distance matrix to `data/processed/distance_matrix.csv`.
- Logs to `outputs/logs/`.

The default distance-matrix file is overwritten on subsequent runs.

## Current limitations

- **Historical universe selection:** the ticker source uses current S&P 500 membership rather than point-in-time constituents, introducing survivorship and selection bias into historical analysis.
- **Data preparation:** the download path uses unadjusted closing prices. Corporate actions and missing-data filtering can affect the resulting relationships.
- **Cache coverage:** existing caches are reused without automatically downloading missing dates. Check coverage before changing the analysis period.
- **Parameter sensitivity:** lookback length, the Mapper cover, and clustering settings can change the output. Systematic sensitivity analysis is still needed.
- **Interpretation:** the project does not yet establish that its topological features predict market outcomes.

## Direction of development

The next stage is to separate the S&P 500 example from the underlying analysis tools and build a reusable library.

Planned work includes:

- Support for user-provided financial datasets.
- A documented Python API for distance construction and topological analysis.
- Rolling-window comparisons across market conditions.
- Configurable Mapper and clustering parameters.
- Stronger data validation, cache handling, and mathematical tests.
- Comparisons with simpler correlation and clustering baselines.

