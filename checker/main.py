import argparse
import json
import re
from pathlib import Path

import requests
import yaml
from tqdm import tqdm

GBIF_API_BASE = "https://api.gbif.org/v1/species/match"
GBIF_SEARCH_BASE = "https://api.gbif.org/v1/species/search"


def load_config(config_path="configs/config.yaml"):
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}

    input_dir = Path(config.get("input", {}).get("data_dir", "data"))
    output_dir = Path(config.get("output", {}).get("base_dir", "outputs"))

    return input_dir, output_dir


def resolve_base_dirs(config_path="configs/config.yaml"):
    input_dir, output_dir = load_config(config_path)

    if not input_dir.is_absolute():
        input_dir = Path.cwd() / input_dir
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return input_dir, output_dir


def resolve_input_files(config_path="configs/config.yaml", input_file=None):
    input_dir, output_dir = resolve_base_dirs(config_path)

    if input_file:
        input_path = Path(input_file)
        if not input_path.is_absolute():
            input_path = input_dir / input_path
        if not input_path.exists():
            raise FileNotFoundError(f"Input path not found: {input_path}")

        if input_path.is_dir():
            input_files = sorted(path for path in input_path.rglob("*.txt") if path.is_file())
        else:
            input_files = [input_path]
    else:
        input_files = sorted(path for path in input_dir.rglob("*.txt") if path.is_file())

    if not input_files:
        raise FileNotFoundError(f"No input .txt files found in {input_dir}")

    return input_dir, output_dir, input_files


def resolve_output_path(output_dir, input_dir, input_path, output_file=None):
    if output_file:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = output_dir / output_path
    else:
        relative_parent = input_path.relative_to(input_dir).parent
        output_path = output_dir / relative_parent / f"{input_path.stem}_output_report.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def read_input_species(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines() if line.strip()]


def extract_genus(name):
    cleaned = name.replace("_", " ").strip()
    # Remove morphospecies markers like sp., cf., aff.
    cleaned = re.sub(r"\b(sp|cf|aff)\b\.?\d*", "", cleaned, flags=re.IGNORECASE).strip()
    # Return first capitalized word
    match = re.match(r"^([A-Z][a-zA-Z-]+)", cleaned)
    return match.group(1) if match else None


def search_gbif_genus(name, kingdom_filter="Animalia"):
    """Search GBIF for a genus and pick the first match in the desired kingdom."""
    try:
        response = requests.get(
            GBIF_SEARCH_BASE,
            params={"q": name, "rank": "GENUS", "limit": 50}
        )
        data = response.json()
        results = data.get("results", [])

        if not results:
            return None

        # Filter by exact rank GENUS
        results = [r for r in results if r.get("rank") == "GENUS"]

        # Filter by kingdom if provided
        if kingdom_filter:
            results = [r for r in results if r.get("kingdom") == kingdom_filter]

        if not results:
            return None

        # Pick the first match
        best = results[0]
        usage_key = best.get("key")
        valid_name = best.get("canonicalName") or best.get("scientificName")

        return {
            "valid_species_name": best.get("scientificName"),
            "ID": usage_key,
            "match_level": "genus"
        }

    except Exception as e:
        print(f"[ERROR] search_gbif_genus failed for '{name}': {e}")
        return None


def gbif_lookup(name):
    response = requests.get(GBIF_API_BASE, params={"name": name})
    data = response.json()

    print(f"\n[DEBUG] GBIF lookup for '{name}':")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Direct match case
    if data.get("matchType") in ("EXACT", "HIGHERRANK") or data.get("confidence", 0) >= 90:
        usage_key = data.get("usageKey")
        valid_name = data.get("canonicalName") or data.get("scientificName")

        return {
            "valid_species_name": data.get("scientificName"),
            "ID": usage_key,
            "match_level": "genus" if data.get("rank") == "GENUS" else "species"
        }

    # Any case with no match — fall back to genus search
    if data.get("matchType") == "NONE":
        genus = extract_genus(name)
        if genus:
            print(f"[DEBUG] No exact match for '{name}', searching manually for genus '{genus}'...")
            return search_gbif_genus(genus)

    return None

def query_gbif_species(species_name):
    try:
        # Try full name first
        match_data = gbif_lookup(species_name)
        if match_data:
            result = {
                "input_species_name": species_name,
                **match_data
            }
        else:
            # Fallback: try just genus
            genus = extract_genus(species_name)
            if genus:
                genus_match = gbif_lookup(genus)
                if genus_match:
                    genus_match["match_level"] = "genus"
                    result = {
                        "input_species_name": species_name,
                        **genus_match
                    }
                else:
                    # No match found
                    result = {
                        "input_species_name": species_name,
                        "valid_species_name": None,
                        "ID": None,
                        "match_level": None
                    }
            else:
                # No match found
                result = {
                    "input_species_name": species_name,
                    "valid_species_name": None,
                    "ID": None,
                    "match_level": None
                }

        return result

    except Exception as e:
        return {
            "input_species_name": species_name,
            "valid_species_name": None,
            "ID": None,
            "match_level": None,
            "error": str(e)
        }


def generate_report(input_file, output_file):
    species_list = read_input_species(input_file)
    report = []

    for species in tqdm(species_list, desc="Checking species"):
        result = query_gbif_species(species)
        report.append(result)

    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(report, out, indent=2, ensure_ascii=False)

    print(f"\n✅ Report saved to: {output_file}")


def generate_reports(config_path="configs/config.yaml", input_file=None, output_file=None):
    input_dir, output_dir, input_files = resolve_input_files(config_path, input_file)

    if output_file and len(input_files) > 1:
        raise ValueError("--output-file can only be used when processing a single input file")

    for input_path in input_files:
        output_path = resolve_output_path(output_dir, input_dir, input_path, output_file)
        print(f"Processing {input_path} -> {output_path}")
        generate_report(str(input_path), str(output_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GBIF species taxon checker")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--input-file", default=None, help="Input taxa file or directory path relative to the configured input directory")
    parser.add_argument("--output-file", default=None, help="Output report file path relative to the configured output directory for single-file runs")

    args = parser.parse_args()

    generate_reports(
        config_path=args.config,
        input_file=args.input_file,
        output_file=args.output_file,
    )
