# vibrational-mode-coefficients

Decomposes the geometric distortion between a ground state (GS) and an 
excited state (3MC) into contributions from normal mode vectors by solving:

**v₃MC = v_GS + Σ(cᵢ × aᵢ)**

where cᵢ are the vibrational coefficients and aᵢ are the normal mode 
displacement vectors extracted from a Gaussian frequency calculation.

## Requirements
```bash
pip install numpy pandas openpyxl
```

## Workflow

### Step 1 — Prepare your XYZ files
Prepare two structure files:
- `GS.xyz` — ground state geometry
- `excited_state.xyz` — excited state geometry (e.g. 3MC)

See `example/1.xyz` (GS) and `example/2.xyz` (excited state) for reference.

---

### Step 2 — Align structures (Kabsch algorithm)
```bash
python align_kabsch.py 2.xyz 1.xyz
```
**Output:** `shifted.2.xyz` — excited state geometry aligned onto GS frame

> ⚠️ align_kabsch.py is NOT authored by Marwa Al Rammal.
> Original author: Grace (2019), based on code by Dr. L.P. Wang, UC Davis.
> Distributed under BSD 3-Clause License.
> Source: https://github.com/leeping/forcebalance
> See THIRD_PARTY_LICENSES.md for full license text.

---

### Step 3 — Extract vibrational modes from Gaussian log
Edit `extract_vibrationalmodes.py` to set your log file name and atom/mode count:
```python
log_filename = "1.log"
num_atoms = 61
num_modes = 177
```
Then run:
```bash
python extract_vibrationalmodes.py
```
**Output:** `cartesian_displacements.xlsx`

See `example/cartesian_displacements.xlsx` for reference.

---

### Step 4 — Reshape vibrational mode data
```bash
python rearrange_vibrationalmodes.py
```
**Output:** `reshaped_modes.xlsx`

See `example/reshaped_modes.xlsx` for reference.

---

### Step 5 — Extract and compare coordinates
Edit `extract_coordinates.py` to set your file names:
```python
gs_file = "1.xyz"
shifted_file = "shifted.2.xyz"
```
Then run:
```bash
python extract_coordinates.py
```
**Output:** `coordinates_comparison.xlsx`

See `example/coordinates_comparison.xlsx` for reference.

---

### Step 6 — Build Mode_Delta.xlsx (manual Excel step)
1. Open `coordinates_comparison.xlsx`
2. Add a column `Delta = shifted - GS` for each atom and direction
3. Open `reshaped_modes.xlsx` and copy all mode columns
4. Paste modes + Delta column into a new file
5. Save as `Mode_Delta.xlsx`

See `example/Mode_Delta.xlsx` for reference.

---

### Step 7 — Solve for vibrational coefficients
```bash
python solving_matrix.py
```
**Output:** `mode_solution_steps.xlsx` with sheets:
- `M_Transpose` — transpose of mode matrix
- `M_T_M` — M^T × M
- `M_T_M_Inverse` — (M^T M)⁻¹
- `Pseudo_Inverse` — Moore-Penrose pseudoinverse
- `Coefficients` — **cᵢ values for each normal mode**

See `example/mode_solution_steps.xlsx` for reference.

---

## Example Files
The `example/` folder contains a complete working dataset:

| File | Description |
|---|---|
| `1.xyz` | Ground state geometry (61 atoms) |
| `2.xyz` | Excited state geometry (3MC) |
| `1.log` | Gaussian frequency log file |
| `cartesian_displacements.xlsx` | Output of Step 3 |
| `reshaped_modes.xlsx` | Output of Step 4 |
| `coordinates_comparison.xlsx` | Output of Step 5 |
| `Mode_Delta.xlsx` | Input for Step 7 |
| `mode_solution_steps.xlsx` | Final coefficients |

---

## Author
**Marwa Al Rammal**  
Computational Chemist, NCSU  

## Third-Party Code
`align_kabsch.py` — written by Grace (2019), based on code by Dr. L.P. Wang (UC Davis).  
Reference: https://github.com/leeping/forcebalance

## Citation
If you use this workflow in your research, please cite:
> Al Rammal, Marwa (2026). gaussian-tools. Zenodo. [https://doi.org/10.5281/zenodo.20213932](https://doi.org/10.5281/zenodo.20276209)
