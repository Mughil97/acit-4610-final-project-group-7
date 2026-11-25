"""Load the OR-Library portfolio benchmark datasets.

Each dataset contains asset mean returns, standard deviations,
and pairwise correlations.

The covariance matrix is constructed from these statistics
according to Portfolio 2026, Problem 2, page 9.
"""

from dataclasses import dataclass, field
from pathlib import Path


# Locate the data directory relative to this Python file.
# This allows the datasets to be loaded independently of
# the current working directory.
DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass
class Portfolio:
    """Store the statistical information for one asset.

    Attributes:
        profit: Expected mean return of the asset (r_i).
        risk: Standard deviation of the asset return (s_i).
        correlations: Correlations between this asset
            and all other assets (row i of matrix C).
        covariances: Covariances between this asset
            and all other assets (row i of matrix Sigma).

    A complete portfolio dataset is represented by a list
    of these asset objects.
    """

    profit: float
    risk: float

    correlations: list[float] = field(default_factory=list)
    covariances: list[float] = field(default_factory=list)


def construct_covariance_matrix(
    portfolio: list[Portfolio],
) -> list[list[float]]:
    """Construct the symmetric covariance matrix.

    Required assignment formula:

        Sigma[i][j] = s_i * s_j * C[i][j]

    where:
        s_i and s_j are asset standard deviations.
        C[i][j] is the correlation between the two assets.

    The diagonal contains each asset's individual variance.
    Off-diagonal elements describe how asset returns vary
    together.

    Covariance depends only on the dataset, not on the
    candidate portfolio weights.
    """

    n = len(portfolio)
    covariance = [[0.0] * n for _ in range(n)]

    for i in range(n):

        # An asset has a correlation of 1 with itself.
        covariance[i][i] = portfolio[i].risk ** 2

        for j in range(i + 1, n):

            # Calculate covariance between assets i and j.
            value = (
                portfolio[i].risk
                * portfolio[j].risk
                * portfolio[i].correlations[j]
            )

            # Covariance is symmetric:
            # Sigma[i][j] = Sigma[j][i].
            covariance[i][j] = value
            covariance[j][i] = value

    return covariance


def read_portfolio_data(file_path: str) -> list[Portfolio]:
    """Load one portfolio benchmark dataset.

    OR-Library file structure:
        First line: number of assets.
        Next n lines: mean return and standard deviation.
        Remaining lines: asset indices and correlations.

    The original asset indices start at 1, whereas Python
    list indices start at 0.
    """

    with open(file_path) as f:

        # Number of assets in this benchmark.
        n = int(f.readline())

        data: list[Portfolio] = []

        # Read the expected return and standard deviation
        # of every asset.
        for _ in range(n):
            value = f.readline().split()

            profit = float(value[0])
            risk = float(value[1])

            data.append(
                Portfolio(profit, risk, [0.0] * n)
            )

        # Construct the symmetric correlation matrix.
        for line in f:
            value = line.split()

            if not value:
                continue

            # Convert 1-based indices to Python indices.
            i = int(value[0]) - 1
            j = int(value[1]) - 1

            corr = float(value[2])

            data[i].correlations[j] = corr
            data[j].correlations[i] = corr

    # Construct covariance once after loading the dataset.
    # It can then be reused during objective evaluations.
    covariance = construct_covariance_matrix(data)

    for i, asset in enumerate(data):
        asset.covariances = covariance[i]

    return data


# All five benchmark datasets required by the assignment.
datafiles = {
    "port1": str(DATA_DIR / "port1.txt"),
    "port2": str(DATA_DIR / "port2.txt"),
    "port3": str(DATA_DIR / "port3.txt"),
    "port4": str(DATA_DIR / "port4.txt"),
    "port5": str(DATA_DIR / "port5.txt"),
}


# Load the original benchmark datasets.
# Asset counts: 31, 85, 89, 98 and 225 respectively.
portfolio1, portfolio2, portfolio3, portfolio4, portfolio5 = (
    read_portfolio_data(datafiles["port1"]),
    read_portfolio_data(datafiles["port2"]),
    read_portfolio_data(datafiles["port3"]),
    read_portfolio_data(datafiles["port4"]),
    read_portfolio_data(datafiles["port5"]),
)
