# Tax Report

[![CI/CD Pipeline](https://github.com/tsrsilva/checker/actions/workflows/release.yml/badge.svg)](https://github.com/tsrsilva/checker/actions)

A Python tool that automatically matches a list of species with the GBIF backbone taxonomy, producing nested text outputs.

---

## Installation for development

Clone this repository and install dependencies locally:

```bash
git clone https://github.com/tsrsilva/checker.git
cd checker
pip install -r requirements.txt
```

### Configuration
The pipeline is configured via a YAML file located in ```configs/```. 

Example ```configs/config.yaml```:

```yaml
input:
  data_dir: "data"

output:
  base_dir: "outputs"
```

This file controls where input data are read from and where outputs are written.

## Usage

For most collaborators, the easiest way to run the tool is using Docker. This ensures consistent dependencies and paths, without requiring local Python setup.

### Option 1: Using Docker Compose (recommended)

```bash
docker compose build
docker compose run --rm checker
```

This will:

- Build the Docker image
- Run the container
- Automatically: 
    - Parse all ```.txt``` files in ```data/``` 
- Generate name matching reports in:
    - ```outputs```

No extra volume mounts or Docker commands are required.

### Option 2: Building the Docker image manually

```bash
docker build -t checker .
docker run --rm checker
```

Using Option 1 or 2 is recommended to avoid manual volume mounts and ensure consistent input/output paths.

### Option 3: Running locally without Docker (not recommended)

If you prefer to run natively on Python:

```bash
python checker/main.py
```

- Ensure all dependencies from ```requirements.txt``` are installed (or from ```environment.yml``` if using conda)
- Make sure the ```data/``` and ```outputs/``` directories exist in the project root
- Outputs will be saved according to the paths defined in configs/config.yaml

## Output overview

### JSON outputs

- Nested species name match:
    - Input species name
    - Valid species name
    - Species GBIF ID
    - Match level (e.g. genus, species)

## Project structure

```graphql
root/
├── checker/                # Main Python package with source code
├── data/                   # Input species list (.txt)
├── configs/                # YAML configuration files
├── outputs/                # Generated JSON outputs
├── LICENSES/               # License file (MIT)
├── environment.yml         # Conda environment for development
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Orchestrates Docker services for reproducible runs
├── Dockerfile              # Container build definition
└── README.md               # Project documentation
```

## Example data

A minimal example data file can be found at ```data/examples/minimal.txt```. The file consists of ten bee species names.

## License

Licensed under the [MIT License](/LICENSES/MIT.txt)
© 2026 Thiago S. R. Silva, Diego S. Porto

## Funding

This tool was developed as part of the project “PhenoBees: a knowledgebase and integrative approach for studying the evolution of morphological traits in bees” funded by the Research Council of Finland (grant #362624).

## Authors
- [Thiago S. R. Silva](https://github.com/tsrsilva)
- [Diego S. Porto](https://github.com/diegosasso)
