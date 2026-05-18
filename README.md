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

### 4. `vibrational-mode-coefficients` — Vibrational Mode Decomposition
Decomposes the geometric distortion between a ground state and an excited
state into normal mode contributions by solving:

**v₃MC = v_GS + Σ(cᵢ × aᵢ)**

Includes a full step-by-step workflow with example files for a 61-atom
transition metal complex.

## Requirements
- Python 3.6+
- `numpy`, `pandas`, `openpyxl` required for vibrational-mode-coefficients
- No external libraries needed for other tools

## Author
**Marwa Al Rammal**  
Computational Chemist  
ORCID: [0000-0001-8607-8420](https://orcid.org/0000-0001-8607-8420)  
GitHub: [@marwaalrammal](https://github.com/marwaalrammal)

## Citation
If you use any of these tools in your research, please cite:
> Al Rammal, Marwa (2026). gaussian-tools. Zenodo. https://doi.org/10.5281/zenodo.20276209

## License
BSD 2-Clause License — see [LICENSE](LICENSE) for details.
