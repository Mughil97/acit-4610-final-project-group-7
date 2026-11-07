from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass
class Portfolio:
    profit: float
    risk: float
    correlations: list[float] = field(default_factory=list)


def read_portfolio_data(file_path: str) -> list[Portfolio]:
    with open(file_path) as f:
        n = int(f.readline())

        data: list[Portfolio] = []

        for _ in range(n):
            value = f.readline().split()
            profit = float(value[0])
            risk = float(value[1])
            data.append(Portfolio(profit, risk, [0.0] * n))

        for line in f:
            value = line.split()
            if not value:
                continue
            i = int(value[0]) - 1
            j = int(value[1]) - 1
            corr = float(value[2])
            data[i].correlations[j] = corr
            data[j].correlations[i] = corr

    return data


datafiles = {
    'port1': str(DATA_DIR / 'port1.txt'),
    'port2': str(DATA_DIR / 'port2.txt'),
    'port3': str(DATA_DIR / 'port3.txt'),
    'port4': str(DATA_DIR / 'port4.txt'),
    'port5': str(DATA_DIR / 'port5.txt'),
}


portfolio1, portfolio2, portfolio3, portfolio4, portfolio5 = (
    read_portfolio_data(datafiles['port1']),
    read_portfolio_data(datafiles['port2']),
    read_portfolio_data(datafiles['port3']),
    read_portfolio_data(datafiles['port4']),
    read_portfolio_data(datafiles['port5'])
)

