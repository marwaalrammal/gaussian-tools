# gaussian-tools
Python scripts for Gaussian calculations and quantum chemistry

# gaussian-geom-extractor
A Python tool for computational chemists that extracts the final optimized geometry 
from Gaussian constrained optimization log files and automatically generates 
Single Point Energy (SPE) input files (.gjf).

## What It Does
- Parses Gaussian `.log` files and finds the **last Input orientation block**
- Extracts atomic coordinates and charge automatically
- Generates ready-to-submit **Gaussian SPE input files** (`.gjf`)
- Supports batch processing of multiple log files at once
## Requirements
- Python 3.6+
- No external libraries needed — uses only Python standard library

## Usage
```bash
# Process all log files in current directory
python extract_geom_spe.py *.log

# Process specific files
python extract_geom_spe.py 197.log 200.log
```

## Output
One `.gjf` file per log file:
```
200.log → 200_MC.gjf
```

## Settings
Edit these variables at the top of the script before running:
| Setting | Default | Description |
|---|---|---|
| `CHARGE` | 0 | Molecular charge |
| `MULTIPLICITY` | 3 | Spin multiplicity (3 = triplet) |
| `METHOD` | ub3lyp | DFT functional |
| `BASIS` | genecp | Basis set keyword |
| `MEM` | 48GB | Memory allocation |
| `NPROC` | 8 | Number of processors |

## Supported Elements
H, B, C, N, O, F, P, S, Cl, Fe, Co, Ni, Cu, Zn, Br, I

## Author
**Marwa Al Rammal**  
Computational Chemist  
GitHub: [@marwaalrammal](https://github.com/marwaalrammal)

## Citation
If you use this tool in your research, please cite:
> Al Rammal, M. (2026). gaussian-geom-extractor. Zenodo.

## License
MIT License — see [LICENSE] for details.
