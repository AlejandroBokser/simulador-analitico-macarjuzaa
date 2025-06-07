#!/usr/bin/env python3
"""Export daily simulation data to CSV."""
from export_to_csv import main as export_main
import sys

if __name__ == "__main__":
    price_file = sys.argv[1] if len(sys.argv) > 1 else "btcdata.csv"
    config_file = sys.argv[2] if len(sys.argv) > 2 else "config.json"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "output.csv"
    export_main(price_file=price_file, config_file=config_file, output_file=output_file, weekly=False)
