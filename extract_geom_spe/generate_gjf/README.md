# generate_gjf

Batch-generates a series of Gaussian input files (.gjf) from a single
template by substituting checkpoint file names across a numbered range.

## Usage
1. Edit the script to set your template file name and number range:
```python
template_file = "197s.gjf"   # your template
for n in range(197, 222, 2): # start, end, step
```
2. Run:
```bash
python generate_gjf.py
```

## Output
```
Created 197s.gjf
Created 199s.gjf
Created 201s.gjf
...
```
