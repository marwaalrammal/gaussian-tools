#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Reshapes Cartesian displacement data from horizontal to vertical format.           #
#            Each atom gets three rows (X, Y, Z) with one column per vibrational mode.         #
#                                                                                               #
#   Input:                                                                                      #
#       1. cartesian_displacements.xlsx (output of extract_vibrationalmodes.py)                 #
#                                                                                               #
#   Output:                                                                                     #
#       1. reshaped_modes.xlsx                                                                  #
#          Rows: atom + direction (X/Y/Z) | Columns: Mode_1 ... Mode_N                         #
#                                                                                               #
#   Settings (edit before running):                                                             #
#       input_excel  : path to cartesian_displacements.xlsx                                    #
#       output_excel : name for the reshaped output file                                        #
#       num_atoms    : number of atoms in your molecule                                         #
#       num_modes    : number of vibrational modes                                              #
#                                                                                               #
#   Usage:                                                                                      #
#       python rearrange_vibrationalmodes.py                                                    #
#                                                                                               #
#   History:                                                                                    #
#   2025/03/05, Marwa Al Rammal, NCSU                                                          #
#   Reference: https://github.com/marwaalrammal/gaussian-tools                                 #
#                                                                                               #
#################################################################################################

import pandas as pd


def reshape_and_save_to_excel(input_file, output_file, num_atoms=61, num_modes=177):
    df    = pd.read_excel(input_file, engine='openpyxl')
    atoms = df["Atom"].values

    reshaped_data = []
    for i in range(num_atoms):
        atom = atoms[i]
        for axis_index, axis in enumerate(["X", "Y", "Z"]):
            row = [atom, axis]
            for mode in range(num_modes):
                row.append(df.iloc[i, 1 + mode * 3 + axis_index])
            reshaped_data.append(row)

    columns     = ["Atom", "Direction"] + [f"Mode_{i+1}" for i in range(num_modes)]
    reshaped_df = pd.DataFrame(reshaped_data, columns=columns)
    reshaped_df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Reshaped data saved to {output_file}")


# ─────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────
input_excel  = "cartesian_displacements.xlsx"
output_excel = "reshaped_modes.xlsx"
num_atoms    = 61
num_modes    = 177
# ─────────────────────────────────────────────

reshape_and_save_to_excel(input_excel, output_excel, num_atoms, num_modes)
