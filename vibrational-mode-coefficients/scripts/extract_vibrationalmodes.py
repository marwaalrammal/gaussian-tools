#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Extracts Cartesian displacement vectors from a Gaussian frequency log file         #
#            and saves them to an Excel spreadsheet.                                            #
#                                                                                               #
#   Input:                                                                                      #
#       1. Gaussian frequency log file (.log)                                                   #
#                                                                                               #
#   Output:                                                                                     #
#       1. cartesian_displacements.xlsx                                                         #
#          Rows: atoms | Columns: Mode_freq_X, Mode_freq_Y, Mode_freq_Z                        #
#                                                                                               #
#   Settings (edit before running):                                                             #
#       log_filename : name of your Gaussian log file                                           #
#       num_atoms    : number of atoms in your molecule                                         #
#       num_modes    : number of vibrational modes (3N-6 for non-linear molecules)              #
#                                                                                               #
#   Usage:                                                                                      #
#       python extract_vibrationalmodes.py                                                      #
#                                                                                               #
#   History:                                                                                    #
#   2025/03/05, Marwa Al Rammal, NCSU                                                          #
#   Reference: https://github.com/marwaalrammal/gaussian-tools                                 #
#                                                                                               #
#################################################################################################

import re
import pandas as pd

def extract_cartesian_displacements(log_file, num_atoms=61, num_modes=177):
    with open(log_file, 'r') as file:
        lines = file.readlines()

    mode_frequencies = []
    atom_displacements = {i: [] for i in range(1, num_atoms + 1)}
    capture = False
    current_modes = []

    for i, line in enumerate(lines):
        if "Frequencies --" in line:
            current_modes = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            mode_frequencies.extend(current_modes)
            continue
        if "Atom  AN" in line:
            capture = True
            continue
        if capture:
            parts = line.split()
            if len(parts) < 4 or not parts[0].isdigit():
                continue
            atom_number = int(parts[0])
            displacements = parts[2:]
            if len(displacements) == len(current_modes) * 3:
                atom_displacements[atom_number].extend(displacements)

    mode_data = [[atom] + disps for atom, disps in atom_displacements.items()]
    return mode_frequencies, mode_data


def save_to_excel(mode_frequencies, mode_data, output_file, num_modes=177):
    expected_columns = num_modes * 3
    for row in mode_data:
        if len(row) - 1 != expected_columns:
            print(f"Error: Atom {row[0]} has {len(row)-1} columns instead of {expected_columns}")
            return
    columns = ["Atom"] + [f"Mode_{mode_frequencies[i]}_{axis}"
                          for i in range(num_modes) for axis in ["X", "Y", "Z"]]
    df = pd.DataFrame(mode_data, columns=columns)
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Cartesian displacement vectors saved to {output_file}")


# ─────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────
log_filename = "1.log"
output_excel = "cartesian_displacements.xlsx"
num_atoms    = 61
num_modes    = 177
# ─────────────────────────────────────────────

mode_frequencies, mode_data = extract_cartesian_displacements(log_filename, num_atoms, num_modes)
save_to_excel(mode_frequencies, mode_data, output_excel, num_modes)
