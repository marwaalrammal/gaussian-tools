#Marwa Al Rammal 5 May 2026
# track_root

Tracks a TD-DFT excited state (root N) across a Gaussian geometry
optimization and detects root flips using cosine similarity of
CI transition fingerprints.

## What It Does
- Reports energy (eV), oscillator strength (f), and spin contamination <S²> at each step
- Shows the dominant orbital transition per step
- Detects root flips when another state better matches the previous step's character
- Recommends whether to CONTINUE or RESTART the calculation

## Usage
```bash
python track_root.py opt_6.log              # track root 6 (default)
python track_root.py opt_6.log --root 4     # track a different root
python track_root.py opt_6.log --csv        # export results to CSV
python track_root.py opt_6.log --verbose    # show all state similarities
```

## Output
```
Step    eV       f      S²    Dominant transition    Sim↑prev  Status
─────────────────────────────────────────────────────────────────────
   1  2.3451  0.0023  0.000  45A→46A               —         OK
   2  2.3210  0.0019  0.000  45A→46A               0.981     OK
   3  2.2987  0.0021  0.000  44A→46A               0.743     ⚠ FLIP → root 5
```

## Requirements
- Python 3.6+
- No external libraries needed
