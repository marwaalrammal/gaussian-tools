#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Solves for vibrational mode coefficients by least-squares matrix inversion.       #
#                                                                                               #
#   Solves: v_3MC = v_GS + sum(c_i * a_i)                                                     #
#   i.e.:   Delta = M * C                                                                      #
#   where:  M     = matrix of normal mode displacement vectors                                 #
#           Delta = coordinate difference vector (shifted - GS)                                #
#           C     = vibrational coefficients (solution)                                        #
#                                                                                               #
#   Solution via Moore-Penrose pseudoinverse:                                                   #
#           C = (M^T M)^-1 M^T * Delta                                                        #
#                                                                                               #
#   Input:                                                                                      #
#       1. Mode_Delta.xlsx                                                                      #
#          Columns: Atom | Direction | Mode_1 ... Mode_N | Delta                               #
#                                                                                               #
#   Output:                                                                                     #
#       1. mode_solution_steps.xlsx with sheets:                                               #
#          - M_Transpose    : M^T                                                              #
#          - M_T_M          : M^T * M                                                          #
#          - M_T_M_Inverse  : (M^T M)^-1                                                      #
#          - Pseudo_Inverse : M^+ = (M^T M)^-1 M^T                                            #
#          - Coefficients   : c_i values for each normal mode                                  #
#                                                                                               #
#   Usage:                                                                                      #
#       python solving_matrix.py                                                                #
#                                                                                               #
#   History:                                                                                    #
#   2025/03/06, Marwa Al Rammal, NCSU                                                          #
#   Reference: https://github.com/marwaalrammal/gaussian-tools                                 #
#                                                                                               #
#################################################################################################

import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────
file_path   = "Mode_Delta.xlsx"
output_file = "mode_solution_steps.xlsx"
# ─────────────────────────────────────────────

df = pd.read_excel(file_path, engine="openpyxl")
print("Available columns:", df.columns.tolist())

# Select Mode columns
mode_columns = [col for col in df.columns if col.startswith("Mode_") and col[5:].isdigit()]
mode_columns = sorted(mode_columns, key=lambda x: int(x.split("_")[1]))
M = df[mode_columns].values

# Select Delta column
delta_columns = [col for col in df.columns if "Delta" in col]
if not delta_columns:
    raise ValueError("Delta column not found. Check column names printed above.")
elif len(delta_columns) > 1:
    print(f"Multiple Delta columns found: {delta_columns}. Using the first one.")
Delta = df[delta_columns[0]].values.reshape(-1, 1)

# Compute matrices step by step
M_T      = M.T
MTM      = np.dot(M_T, M)
MTM_inv  = np.linalg.inv(MTM)
M_pseudo = np.dot(MTM_inv, M_T)
C        = np.dot(M_pseudo, Delta)

# Save all steps to Excel
df_MT      = pd.DataFrame(M_T,      columns=[f"Atom_{i+1}" for i in range(M_T.shape[1])])
df_MTM     = pd.DataFrame(MTM,      columns=[f"Mode_{i+1}" for i in range(MTM.shape[1])])
df_MTM_inv = pd.DataFrame(MTM_inv,  columns=[f"Mode_{i+1}" for i in range(MTM_inv.shape[1])])
df_pseudo  = pd.DataFrame(M_pseudo, columns=[f"Atom_{i+1}" for i in range(M_pseudo.shape[1])])
df_C       = pd.DataFrame(C,        columns=["Coefficient"])

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df_MT.to_excel(writer,      sheet_name="M_Transpose",    index=False)
    df_MTM.to_excel(writer,     sheet_name="M_T_M",          index=False)
    df_MTM_inv.to_excel(writer, sheet_name="M_T_M_Inverse",  index=False)
    df_pseudo.to_excel(writer,  sheet_name="Pseudo_Inverse",  index=False)
    df_C.to_excel(writer,       sheet_name="Coefficients",    index=False)

print(f"All matrices and coefficients saved to {output_file}")
