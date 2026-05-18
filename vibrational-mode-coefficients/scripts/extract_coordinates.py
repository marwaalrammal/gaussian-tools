#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Extracts atomic coordinates from two XYZ files (ground state and aligned           #
#            excited state) and saves them side by side in an Excel file.                      #
#                                                                                               #
#   Input:                                                                                      #
#       1. GS XYZ file      : ground state structure (.xyz)                                    #
#       2. Shifted XYZ file : Kabsch-aligned excited state structure (.xyz)                    #
#                                                                                               #
#   Output:                                                                                     #
#       1. coordinates_comparison.xlsx                                                          #
#          Columns: Atom | Direction | GS | Shifted                                            #
#          (three rows per atom: X, Y, Z)                                                      #
#                                                                                               #
#   Settings (edit before running):                                                             #
#       gs_file      : your ground state XYZ file                                              #
#       shifted_file : Kabsch-aligned XYZ file (output of align_kabsch.py)                     #
#       output_excel : name for the output Excel file                                           #
#                                                                                               #
#   Usage:                                                                                      #
#       python extract_coordinates.py                                                           #
#                                                                                               #
#   History:                                                                                    #
#   2025/03/06, Marwa Al Rammal, NCSU                                                          #
#   Reference: https://github.com/marwaalrammal/gaussian-tools                                 #
#                                                                                               #
#################################################################################################

import pandas as pd


def parse_xyz(file_path):
    """Reads an XYZ file and extracts atomic positions."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    atom_data = []
    for line in lines[2:]:  # Skip first two header lines
        parts = line.split()
        if len(parts) == 4:
            atom_data.append([parts[0], float(parts[1]),
                               float(parts[2]), float(parts[3])])
    return atom_data


def create_excel(gs_file, shifted_file, output_excel):
    """Extracts positions from two XYZ files and creates an Excel comparison file."""
    gs_atoms      = parse_xyz(gs_file)
    shifted_atoms = parse_xyz(shifted_file)

    if len(gs_atoms) != len(shifted_atoms):
        raise ValueError("Mismatch in number of atoms between GS and Shifted files.")

    reshaped_data = []
    for (gs_atom, gs_x, gs_y, gs_z), (_, sh_x, sh_y, sh_z) in zip(gs_atoms, shifted_atoms):
        reshaped_data.append([gs_atom, "X", gs_x, sh_x])
        reshaped_data.append([gs_atom, "Y", gs_y, sh_y])
        reshaped_data.append([gs_atom, "Z", gs_z, sh_z])

    df = pd.DataFrame(reshaped_data, columns=["Atom", "Direction", "GS", "Shifted"])
    df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"Excel file saved: {output_excel}")


# ─────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────
gs_file      = "1.xyz"
shifted_file = "shifted.2.xyz"
output_excel = "coordinates_comparison.xlsx"
# ─────────────────────────────────────────────

create_excel(gs_file, shifted_file, output_excel)
