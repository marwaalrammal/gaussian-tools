#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Extracts the final optimized geometry from Gaussian constrained optimization      #
#            log files and generates Single Point Energy (SPE) input files (.gjf).             #
#                                                                                               #
#   Input:                                                                                      #
#       1. One or more Gaussian log files (.log)                                                #
#                                                                                               #
#   Output:                                                                                     #
#       1. One .gjf SPE input file per log file                                                 #
#          e.g. 200.log -> 200_MC.gjf                                                          #
#                                                                                               #
#   Settings (edit before running):                                                             #
#       CHARGE       : molecular charge                                                         #
#       MULTIPLICITY : target multiplicity for SPE (3 for triplet)                             #
#       METHOD       : DFT functional                                                           #
#       BASIS        : basis set keyword                                                        #
#       EXTRAS       : additional route keywords                                                #
#       MEM / NPROC  : memory and processor resources                                          #
#                                                                                               #
#   Usage:                                                                                      #
#       python extract_geom_spe.py *.log           # process all log files                     #
#       python extract_geom_spe.py 197.log 200.log # process specific files                    #
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

import sys
import os
import glob

# ─────────────────────────────────────────────
# USER SETTINGS — edit these as needed
# ─────────────────────────────────────────────
CHARGE        = 0
MULTIPLICITY  = 3          # triplet SPE

METHOD        = "ub3lyp"
BASIS         = "genecp"
EXTRAS        = ("empiricaldispersion=gd2 "
                 "scrf=(solvent=acetonitrile,pcm) "
                 "integral=grid=ultrafine "
                 "guess=read"
                 "pseudo=read scf=xqc symmetry=none")

MEM           = "48GB"
NPROC         = 8
CHK_SUFFIX    = "_spe"
GJF_SUFFIX    = "_MC"
# ─────────────────────────────────────────────

ATOMIC_NUM_TO_SYMBOL = {
    1: "H",  5: "B",  6: "C",  7: "N",  8: "O",
    9: "F", 15: "P", 16: "S", 17: "Cl", 26: "Fe",
    27: "Co", 28: "Ni", 29: "Cu", 30: "Zn",
    35: "Br", 53: "I",
}

BASIS_SECTION = """\
H N C B 0
6-311G*
****
Fe 0
SDD
****

Fe 0
SDD

""" + "\n" * 10

ROUTE = f"#p {METHOD}/{BASIS} {EXTRAS}"


def parse_last_input_orientation(log_path):
    atoms = []
    in_block = False
    header_lines = 0

    with open(log_path, "r") as f:
        for line in f:
            if "Input orientation:" in line:
                atoms = []
                in_block = True
                header_lines = 0
                continue
            if in_block:
                if header_lines < 4:
                    header_lines += 1
                    continue
                stripped = line.strip()
                if stripped.startswith("---") or stripped == "":
                    in_block = False
                    continue
                parts = stripped.split()
                if len(parts) >= 6:
                    try:
                        atomic_num = int(parts[1])
                        x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
                        symbol = ATOMIC_NUM_TO_SYMBOL.get(atomic_num, f"X{atomic_num}")
                        atoms.append((symbol, x, y, z))
                    except ValueError:
                        in_block = False
    return atoms


def get_charge_from_log(log_path):
    with open(log_path, "r") as f:
        for line in f:
            if "Charge =" in line and "Multiplicity =" in line:
                parts = line.split()
                try:
                    charge = int(parts[parts.index("=") + 1])
                    return charge
                except (ValueError, IndexError):
                    pass
    return CHARGE


def write_spe_input(atoms, log_path, charge):
    base     = os.path.splitext(os.path.basename(log_path))[0]
    out_name = f"{base}{GJF_SUFFIX}.gjf"
    out_path = os.path.join(os.path.dirname(log_path), out_name)
    title    = f"SPE triplet | from {base}.log"

    with open(out_path, "w") as f:
        f.write(f"%chk={base}{CHK_SUFFIX}.chk\n")
        f.write(f"%mem={MEM}\n")
        f.write(f"%nprocshared={NPROC}\n")
        f.write(f"{ROUTE}\n\n")
        f.write(f"{title}\n\n")
        f.write(f"{charge} {MULTIPLICITY}\n")
        for sym, x, y, z in atoms:
            f.write(f" {sym:<4s}  {x:>14.8f}  {y:>14.8f}  {z:>14.8f}\n")
        f.write("\n")
        f.write(BASIS_SECTION)
        f.write("\n")
    return out_path


def process_log(log_path):
    print(f"\nProcessing: {log_path}")
    atoms = parse_last_input_orientation(log_path)
    if not atoms:
        print(f"  [ERROR] No 'Input orientation' block found in {log_path}!")
        return
    charge = get_charge_from_log(log_path)
    print(f"  Found {len(atoms)} atoms | Charge = {charge} → SPE multiplicity = {MULTIPLICITY}")
    out = write_spe_input(atoms, log_path, charge)
    print(f"  Written: {out}")


if __name__ == "__main__":
    targets = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            targets.extend(glob.glob(arg))
    else:
        targets = glob.glob("*.log")

    if not targets:
        print("No log files found. Usage: python extract_geom_spe.py *.log")
        sys.exit(1)

    targets.sort()
    print(f"Found {len(targets)} log file(s) to process.")

    for log in targets:
        process_log(log)

    print("\nDone! Check the generated .gjf files before submitting.")
    print("\n─────────────────────────────────────────────────────────")
    print("If you use this script in your research, please cite:")
    print("Al Rammal, Marwa (2026). gaussian-tools. Zenodo.")
    print("https://doi.org/10.5281/zenodo.20275969")
    print("─────────────────────────────────────────────────────────\n")
