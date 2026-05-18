#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Batch-generates a series of Gaussian input files (.gjf) from a single template   #
#            by substituting checkpoint file names across a numbered range.                    #
#                                                                                               #
#   Input:                                                                                      #
#       1. A template Gaussian input file (.gjf)                                                #
#                                                                                               #
#   Output:                                                                                     #
#       1. One .gjf file per number in the specified range                                      #
#          e.g. 197s.gjf, 199s.gjf, 201s.gjf ...                                              #
#                                                                                               #
#   Settings (edit before running):                                                             #
#       template_file : name of your template .gjf file                                        #
#       range()       : start, end, step for file numbering                                    #
#                                                                                               #
#   Usage:                                                                                      #
#       python generate_gjf.py                                                                  #
#                                                                                               #
#   Citation:                                                                                   #
#   If you use this script in your research, please cite:                                       #
#   Al Rammal, Marwa (2026). gaussian-tools. Zenodo.                                           #
#   https://doi.org/10.5281/zenodo.20275969                                                    #
#                                                                                               #
#   History:                                                                                    #
#   2026/05/15, Marwa Al Rammal, NCSU                                                          #
#   Reference: https://github.com/marwaalrammal/gaussian-tools                                 #
#                                                                                               #
#################################################################################################

import os

# ─────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────
template_file = "197s.gjf"   # Your template file
# range(start, end, step) — end is not included
file_range    = range(197, 222, 2)
# ─────────────────────────────────────────────

with open(template_file, "r") as f:
    template = f.read()

for n in file_range:
    filename = f"{n}s.gjf"
    content  = template.replace("197s.chk", f"{n}s.chk")
    with open(filename, "w") as f:
        f.write(content)
    print(f"Created {filename}")

print("\n─────────────────────────────────────────────────────────")
print("If you use this script in your research, please cite:")
print("Al Rammal, Marwa (2026). gaussian-tools. Zenodo.")
print("https://doi.org/10.5281/zenodo.20275969")
print("─────────────────────────────────────────────────────────\n")
