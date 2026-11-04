"""Download and validate OR-Library portfolio datasets.

Retrieves the five benchmark instances, checks their
structure, and validates the port1 numerical checkpoints.
"""
from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen
from ..src.portfolio import EXPECTED_SIZES,check_port1_checkpoint,load_portfolio

BASE = "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/"
DEST = Path(__file__).resolve().parents[1]/"data"/"or_library"


def main() -> None:
    DEST.mkdir(exist_ok=True,parents=True)
    for name,n in EXPECTED_SIZES.items():
        dest = DEST/f"{name}.txt"
        if dest.exists():
            print(f"Already present: {dest}")
        else:
            url = f"{BASE}{name}.txt"
            print(f"Downloading {url}")
            try:
                with urlopen(url,timeout=30) as response:
                    payload = response.read()
                temp = dest.with_suffix(".download")
                temp.write_bytes(payload)
                # Validate BEFORE moving into the official data directory.
                load_portfolio(temp,expected_n=n)
                temp.replace(dest)
            except Exception as exc:
                dest.with_suffix(".download").unlink(missing_ok=True)
                raise RuntimeError(f"Download failed for {name}; download it manually from {url}") from exc
        data=load_portfolio(dest,expected_n=n)
        if name == "port1":
            check_port1_checkpoint(data)
        print(f"Validated {name}: {data.n} assets and {data.n*(data.n+1)//2} correlations")


if __name__ == "__main__":
    main()
