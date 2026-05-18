#!/usr/bin/env python3
#################################################################################################
#                                                                                               #
#   Program: Tracks a TD-DFT excited state (root N) across a Gaussian geometry optimization   #
#            and detects root flips using cosine similarity of CI transition fingerprints.     #
#                                                                                               #
#   Input:                                                                                      #
#       1. Gaussian TD-DFT geometry optimization log file (.log)                               #
#                                                                                               #
#   Output:                                                                                     #
#       1. Std-out: step-by-step table of energy (eV), oscillator strength (f),               #
#          spin contamination <S²>, dominant transition, and similarity to previous step       #
#       2. FLIP warning when another state matches the previous target better                  #
#       3. Final recommendation: CONTINUE / RESTART                                            #
#       4. Optional CSV file with full tracking data (--csv flag)                              #
#                                                                                               #
#   Usage:                                                                                      #
#       python track_root.py opt_6.log              # track root 6 (default)                  #
#       python track_root.py opt_6.log --root 4     # track a different root                  #
#       python track_root.py opt_6.log --csv        # also write a CSV file                   #
#       python track_root.py opt_6.log --verbose    # print all states each step              #
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

import re
import sys
import math
import argparse
import csv as _csv

# ── regex ────────────────────────────────────────────────────────────────────
RE_TD_HEADER  = re.compile(r"Excitation energies and oscillator strengths")
RE_ES_HEADER  = re.compile(
    r"Excited State\s+(\d+):\s+\S+\s+([\d.]+)\s+eV\s+[\d.]+\s+nm"
    r"\s+f=([\d.]+)\s+<S\*\*2>=([\d.]+)"
)
RE_TRANSITION = re.compile(
    r"^\s+(\d+)([AB])\s*(->|<-)\s*(\d+)([AB])\s+(-?[\d.]+)"
)
RE_TARGET_MARKER = re.compile(r"This state for optimization")
RE_CONV_LINE  = re.compile(
    r"Maximum Force\s+([\d.]+)\s+([\d.]+)\s+(YES|NO)"
)
RE_GRAD_BLOCK = re.compile(r"GradGradGradGrad")


# ── helpers ──────────────────────────────────────────────────────────────────
def cosine(a: dict, b: dict) -> float:
    """
    |Cosine| similarity between two {key: float} sparse vectors.
    Absolute value is used because TD-DFT CI eigenvectors have an arbitrary
    overall sign — multiplying all coefficients by -1 gives the same state,
    but would make a naive dot product negative.
    """
    if not a or not b:
        return 0.0
    dot  = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in set(a) | set(b))
    na   = math.sqrt(sum(v * v for v in a.values()))
    nb   = math.sqrt(sum(v * v for v in b.values()))
    return abs(dot / (na * nb)) if (na and nb) else 0.0


def dominant(state: dict):
    """Return (from_orb, from_spin, to_orb, to_spin) with largest |coeff|."""
    tr = state["transitions"]
    if not tr:
        return None
    return max(tr, key=lambda k: abs(tr[k]))


def fmt_pair(pair) -> str:
    if pair is None:
        return "—"
    fo, fs, to, ts = pair
    return f"{fo}{fs}→{to}{ts}"


# ── parser ───────────────────────────────────────────────────────────────────
def parse_log(path: str):
    """
    Returns a list of steps.  Each step is a dict:
        {
          "step_n": int,
          "max_force": float | None,
          "conv_force": bool | None,
          "states": { root_int: state_dict, ... }
        }
    state_dict keys: root, eV, f, s2, transitions{}, is_target
    """
    steps      = []
    cur_block  = None   # dict being built for the current TD block
    cur_state  = None   # state dict being built
    step_count = 0
    conv_info  = {}     # maps step_count → (max_force, converged?)

    with open(path) as fh:
        for line in fh:

            # Count gradient (optimization) blocks to number steps
            if RE_GRAD_BLOCK.search(line):
                step_count += 1
                continue

            # Capture convergence info
            mc = RE_CONV_LINE.search(line)
            if mc:
                conv_info[step_count] = (float(mc.group(1)), mc.group(3) == "YES")
                continue

            # New TD-DFT block
            if RE_TD_HEADER.search(line):
                if cur_block:
                    steps.append(cur_block)
                cur_block  = {"step_n": len(steps) + 1,
                              "max_force": None, "conv_force": None,
                              "states": {}}
                cur_state  = None
                continue

            if cur_block is None:
                continue

            # Excited State header line
            mh = RE_ES_HEADER.search(line)
            if mh:
                cur_state = {
                    "root":        int(mh.group(1)),
                    "eV":          float(mh.group(2)),
                    "f":           float(mh.group(3)),
                    "s2":          float(mh.group(4)),
                    "transitions": {},
                    "is_target":   False,
                }
                cur_block["states"][cur_state["root"]] = cur_state
                continue

            # Transition line
            if cur_state is not None:
                mt = RE_TRANSITION.match(line)
                if mt:
                    fo, fs = int(mt.group(1)), mt.group(2)
                    direction = mt.group(3)
                    to, ts = int(mt.group(4)), mt.group(5)
                    coeff  = float(mt.group(6))
                    # normalise direction so key is always (occupied→virtual)
                    key = (fo, fs, to, ts) if direction == "->" else (to, ts, fo, fs)
                    cur_state["transitions"][key] = coeff
                    continue

            # Target marker
            if cur_state is not None and RE_TARGET_MARKER.search(line):
                cur_state["is_target"] = True

    # flush last block
    if cur_block and cur_block["states"]:
        steps.append(cur_block)

    # attach convergence info
    for i, step in enumerate(steps):
        key = i + 1           # grad blocks roughly align with TD blocks
        if key in conv_info:
            step["max_force"], step["conv_force"] = conv_info[key]

    return steps


# ── analysis ─────────────────────────────────────────────────────────────────
def analyse(steps, target_root: int):
    results = []

    for i, step in enumerate(steps):
        states   = step["states"]
        target   = states.get(target_root)

        rec = {
            "step":         step["step_n"],
            "max_force":    step["max_force"],
            "conv_force":   step["conv_force"],
            "target_eV":    target["eV"]    if target else None,
            "target_f":     target["f"]     if target else None,
            "target_s2":    target["s2"]    if target else None,
            "dom_pair":     dominant(target) if target else None,
            "status":       "MISSING" if not target else "OK",
            "flip_to":      None,
            "flip_sim_new": None,   # similarity of best match to prev target
            "flip_sim_old": None,   # similarity of root N to prev target
            "all_sims":     {},
        }

        if target and i > 0:
            prev_target = steps[i - 1]["states"].get(target_root)
            if prev_target and prev_target["transitions"]:
                prev_fp = prev_target["transitions"]
                # Compare prev target fingerprint against EVERY state this step
                sims = {
                    r: cosine(prev_fp, s["transitions"])
                    for r, s in states.items()
                }
                rec["all_sims"] = sims

                best_root = max(sims, key=sims.get)
                best_sim  = sims[best_root]
                cur_sim   = sims.get(target_root, 0.0)

                rec["flip_sim_old"] = cur_sim

                # Flag a flip when a different root is a clearly better match
                if best_root != target_root and best_sim > cur_sim + 0.08:
                    rec["status"]       = "FLIP"
                    rec["flip_to"]      = best_root
                    rec["flip_sim_new"] = best_sim

        results.append(rec)

    return results


# ── reporting ─────────────────────────────────────────────────────────────────
HEADER = (
    f"{'Step':>5}  {'eV':>6}  {'f':>7}  {'S²':>5}  "
    f"{'Dominant transition':<22}  {'Sim↑prev':>8}  {'Status'}"
)

def print_report(results, target_root: int, verbose: bool = False):
    print(f"\nTracking root {target_root}\n")
    print(HEADER)
    print("─" * 90)

    flips   = []
    missing = []

    for r in results:
        if r["status"] == "MISSING":
            print(f"{r['step']:>5}  {'—':>6}  {'—':>7}  {'—':>5}  {'root missing':22}  {'—':>8}  MISSING")
            missing.append(r["step"])
            continue

        sim_str = f"{r['flip_sim_old']:.3f}" if r["flip_sim_old"] is not None else "  —  "
        flag    = ""

        if r["status"] == "FLIP":
            flag = f"  ⚠ FLIP → root {r['flip_to']}  (sim {r['flip_sim_new']:.3f} vs {r['flip_sim_old']:.3f})"
            flips.append(r)

        print(
            f"{r['step']:>5}  {r['target_eV']:>6.4f}  {r['target_f']:>7.4f}  "
            f"{r['target_s2']:>5.3f}  {fmt_pair(r['dom_pair']):<22}  "
            f"{sim_str:>8}  {r['status']}{flag}"
        )

        if verbose and r["all_sims"]:
            sorted_sims = sorted(r["all_sims"].items(), key=lambda x: -x[1])
            for root, sim in sorted_sims[:5]:
                marker = " ← tracked" if root == target_root else ""
                print(f"              sim(root {root:>2}) = {sim:.3f}{marker}")

    # ── summary ──────────────────────────────────────────────────────────────
    print("\n" + "═" * 90)
    print("SUMMARY")
    print("═" * 90)

    if missing:
        print(f"  ✗  Root {target_root} absent in step(s): {missing}")

    if not flips:
        print(f"  ✓  No root flips detected across {len(results)} steps.")
        _recommend_continue(results)
    else:
        print(f"  ⚠  {len(flips)} potential root flip(s):")
        for r in flips:
            print(
                f"     Step {r['step']:>3}: root {target_root} ↔ root {r['flip_to']}"
                f"  — similarity dropped to {r['flip_sim_old']:.3f},"
                f" root {r['flip_to']} has {r['flip_sim_new']:.3f}"
            )
        _recommend_restart(results, flips, target_root)

    # ── convergence note ─────────────────────────────────────────────────────
    last = results[-1]
    if last["max_force"] is not None:
        conv = "YES" if last["conv_force"] else "NO"
        print(f"\n  Last step max force = {last['max_force']:.6f}  (converged: {conv})")
        if not last["conv_force"]:
            print("  Optimization has NOT converged — see restart recommendation below.")

    print()


def _recommend_continue(results):
    last = results[-1]
    if last["max_force"] and not last["conv_force"]:
        print(
            "\n  RECOMMENDATION — CONTINUE / IMPROVE CONVERGENCE\n"
            "  ─────────────────────────────────────────────────\n"
            "  The state character is stable. The optimization just needs more steps.\n"
            "  Suggested gjf changes:\n"
            "    opt=(recalcfc=5,maxstep=5)   ← recalculates the Hessian every 5 steps\n"
            "  Restart with:  geom=check guess=read  (reads geometry from .chk)\n"
        )
    else:
        print("\n  RECOMMENDATION — CONVERGED, no action needed.\n")


def _recommend_restart(results, flips, target_root):
    first_flip_step = flips[0]["step"]
    flip_to         = flips[0]["flip_to"]
    print(
        f"\n  RECOMMENDATION — RESTART CAREFULLY\n"
        f"  ────────────────────────────────────\n"
        f"  Root flip first occurred at step {first_flip_step}.\n"
        f"  The true LMCT state may now be at root {flip_to} (check its NTOs).\n"
        f"\n"
        f"  Option A — if root {flip_to} is the correct state:\n"
        f"    Change  TD=(NStates=10,root={flip_to})  and restart.\n"
        f"\n"
        f"  Option B — if you want to stay on root {target_root}:\n"
        f"    Restart from step {first_flip_step - 1} geometry (extract from log),\n"
        f"    add  opt=(recalcfc=5,maxstep=3)  to tighten the optimizer.\n"
        f"\n"
        f"  In both cases use  geom=check guess=read  to restart from the .chk file.\n"
    )


# ── CSV export ────────────────────────────────────────────────────────────────
def write_csv(results, target_root: int, log_path: str):
    out = log_path.rsplit(".", 1)[0] + f"_root{target_root}_tracking.csv"
    fields = ["step", "eV", "f", "s2", "dominant_transition",
              "sim_to_prev", "status", "flip_to", "flip_sim"]
    with open(out, "w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({
                "step":                 r["step"],
                "eV":                   r["target_eV"],
                "f":                    r["target_f"],
                "s2":                   r["target_s2"],
                "dominant_transition":  fmt_pair(r["dom_pair"]),
                "sim_to_prev":          r["flip_sim_old"],
                "status":               r["status"],
                "flip_to":              r["flip_to"],
                "flip_sim":             r["flip_sim_new"],
            })
    print(f"  CSV written → {out}")


# ── entry point ───────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Track a TD-DFT root across a Gaussian optimization log."
    )
    ap.add_argument("log",            help="Gaussian .log file")
    ap.add_argument("--root",  "-r",  type=int, default=6,
                    help="Root index to track (default: 6)")
    ap.add_argument("--csv",          action="store_true",
                    help="Export results to CSV")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Print cosine similarities for all states each step")
    args = ap.parse_args()

    print(f"Parsing {args.log} …")
    steps = parse_log(args.log)
    print(f"Found {len(steps)} TD-DFT block(s).")

    results = analyse(steps, args.root)
    print_report(results, args.root, verbose=args.verbose)

    if args.csv:
        write_csv(results, args.root, args.log)


if __name__ == "__main__":
    main()
    print("\n─────────────────────────────────────────────────────────")
    print("If you use this script in your research, please cite:")
    print("Al Rammal, Marwa (2026). gaussian-tools. Zenodo.")
    print("https://doi.org/10.5281/zenodo.20275969")
    print("─────────────────────────────────────────────────────────\n")
