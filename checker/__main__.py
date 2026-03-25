# SPDX-FileCopyrightText: 2026 Thiago S. R. Silva, Diego S. Porto
# SPDX-License-Identifier: MIT

# checker/__main__.py
import argparse
from .main import generate_reports

def main():
    parser = argparse.ArgumentParser(description="GBIF species taxon checker")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--input-file", default=None, help="Input taxa file or directory path")
    parser.add_argument("--output-file", default=None, help="Output report file path for single-file runs")

    args = parser.parse_args()

    try:
        generate_reports(
            config_path=args.config,
            input_file=args.input_file,
            output_file=args.output_file,
        )
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()