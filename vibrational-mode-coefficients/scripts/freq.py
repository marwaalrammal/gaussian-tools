#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Extracts vibrational frequencies and IR intensities from a Gaussian log file      #
#            and prints them to the terminal.                                                   #
#                                                                                               #
#   Input:                                                                                      #
#       1. Gaussian frequency log file (.log)                                                   #
#                                                                                               #
#   Output:                                                                                     #
#       1. Std-out: frequency (cm-1)   IR intensity (km/mol)                                   #
#          To save output: python freq.py > frequencies.txt                                     #
#                                                                                               #
#   Settings (edit before running):                                                             #
#       output : name of your Gaussian log file                                                 #
#                                                                                               #
#   Usage:                                                                                      #
#       python freq.py                                                                          #
#                                                                                               #
#   History:                                                                                    #
#   Marwa Al Rammal, NCSU                                                                      #
#   Reference: https://github.com/marwaalrammal/gaussian-tools                                 #
#                                                                                               #
#################################################################################################

import re

# ─────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────
output = "1.log"   # Replace with your Gaussian log file
# ─────────────────────────────────────────────

# Extract frequencies
with open(output, 'r') as infile:
    frequencies = []
    for lines in infile:
        if 'Frequencies' in lines:
            for i in re.findall(r"\d+\.\d+", lines):
                frequencies.append(i)

# Extract IR intensities
with open(output, 'r') as infile:
    intensities = []
    for linesi in infile:
        if 'IR Inten' in linesi:
            for j in re.findall(r"\d+\.\d+", linesi):
                intensities.append(j)

frequencies = [float(i) for i in frequencies]
intensities = [float(i) for i in intensities]
nvib        = len(frequencies)

print(f"{'Frequency (cm-1)':>20}  {'IR Intensity (km/mol)':>22}")
print("-" * 45)
for item in range(nvib):
    print(f"{frequencies[item]:>20.4f}  {intensities[item]:>22.4f}")
