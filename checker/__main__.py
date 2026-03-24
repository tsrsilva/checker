# SPDX-FileCopyrightText: 2026 Thiago S. R. Silva, Diego S. Porto
# SPDX-License-Identifier: MIT

# checker/__main__.py
import argparse
from .main import resolve_paths, generate_report

def main():
    parser = argparse.ArgumentParser(description="GBIF species taxon checker")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--input-file", default=None, help="Input taxa file path")
    parser.add_argument("--output-file", default=None, help="Output report file path")

    args = parser.parse_args()

    try:
        input_file_path, output_file_path = resolve_paths(
            config_path=args.config,
            input_file=args.input_file,
            output_file=args.output_file,
        )

        generate_report(str(input_file_path), str(output_file_path))
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()