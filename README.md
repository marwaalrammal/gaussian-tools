# gaussian-tools

A collection of Python utilities for computational chemists working with
Gaussian quantum chemistry calculations.

## Tools

### 1. `extract_geom_spe` — Geometry Extractor & SPE Generator
Extracts the final optimized geometry from Gaussian constrained optimization
log files and generates ready-to-submit Single Point Energy (SPE) input files.

### 2. `track_root` — TD-DFT Root Tracker
Monitors excited state character across a TD-DFT geometry optimization.
Detects root flips using cosine similarity and recommends whether to
continue or restart the calculation.

### 3. `generate_gjf` — Batch GJF Generator
Generates a series of Gaussian input files from a template by substituting
checkpoint file names across a numbered range.

## Requirements
- Python 3.6+
- No external libraries needed

## Author
**Marwa Al Rammal**  
Computational Chemist  
GitHub: [@marwaalrammal](https://github.com/marwaalrammal)

## Citation
If you use any of these tools in your research, please cite:
> Al Rammal, M. (2026). gaussian-tools. Zenodo. *DOI: 10.5281/zenodo.20213932*

## License
MIT License
