"""
generate_instances.py — Reproducible Instance Generator
========================================================
Generates instance files S2–S7 for the computational experiments
(Section 5, Table 9) using fixed seed=42 and the exact topology
parameters from the paper's pipeline.

Paper : A Cyber-Physical Manufacturing Execution Architecture
        Integrating ERP Transaction Automation and
        Autonomous Decision-Making
Authors: Omkar Vishwas Patil, Kushal Bhandari, Omid Fatahi Valilai
Journal: Journal of Manufacturing Systems (JMS), Elsevier

Usage:
    python generate_instances.py

Output files are written to the instances/ directory.
Instance S1 and S1_disruption are hand-crafted (not generated)
and correspond to the SAP case study in Section 4.
"""

import random
from pathlib import Path

# Topology parameters for each scenario
# (n_plants, n_hubs, n_dests, n_ships, tight_cap)
TOPOLOGY = {
    "s2": (3,  3,  3,  5,  False),
    "s3": (4,  5,  4,  10, False),
    "s4": (5,  8,  7,  20, False),
    "s5": (5,  8,  7,  20, True),
    "s6": (7,  11, 10, 30, False),
    "s7": (7,  11, 10, 30, True),
}

# Arc cost and capacity ranges (from paper Section 5.1)
COST_PLANT_HUB  = (8,  25)
COST_HUB_DEST   = (5,  20)
CAP_NORMAL      = (15, 40)
CAP_TIGHT       = (10, 20)
QTY_RANGE       = (3,  12)
SEED            = 42


def generate_instance(n_plants: int, n_hubs: int, n_dests: int,
                      n_ships: int, tight_cap: bool = False,
                      seed: int = SEED) -> str:
    """
    Generate an ASP instance file using fixed random seed.
    Two-tier topology: plants -> hubs -> destinations (full bipartite).
    """
    rng = random.Random(seed)

    plants = [f"p{i+1}" for i in range(n_plants)]
    hubs   = [f"h{i+1}" for i in range(n_hubs)]
    dests  = [f"d{i+1}" for i in range(n_dests)]
    all_n  = plants + hubs + dests

    cap_range = CAP_TIGHT if tight_cap else CAP_NORMAL
    cap_label = "tight" if tight_cap else "normal"

    n_arcs = n_plants * n_hubs + n_hubs * n_dests
    n_nodes = n_plants + n_hubs + n_dests

    lines = [
        f"% Generated instance (seed={seed}, topology: "
        f"{n_plants}p+{n_hubs}h+{n_dests}d={n_nodes}n, "
        f"{n_arcs} arcs, {n_ships} ships, {cap_label} capacity)",
        f"% Corresponds to computational experiments in Section 5.",
        "",
    ]

    # Nodes
    lines += [f"node({v})." for v in all_n] + [""]

    # Plant -> hub arcs
    lines.append("% Plant-to-hub arcs")
    for p in plants:
        for h in hubs:
            c   = rng.randint(*COST_PLANT_HUB)
            cap = rng.randint(*cap_range)
            lines.append(f"edge({p},{h}). cost({p},{h},{c}). cap({p},{h},{cap}).")
    lines.append("")

    # Hub -> dest arcs
    lines.append("% Hub-to-destination arcs")
    for h in hubs:
        for d in dests:
            c   = rng.randint(*COST_HUB_DEST)
            cap = rng.randint(*cap_range)
            lines.append(f"edge({h},{d}). cost({h},{d},{c}). cap({h},{d},{cap}).")
    lines.append("")

    # Shipment requests
    lines.append("% Shipment requests")
    for i in range(n_ships):
        o = rng.choice(plants)
        d = rng.choice(dests)
        while o == d:
            d = rng.choice(dests)
        q = rng.randint(*QTY_RANGE)
        lines.append(f"ship(k{i+1},{o},{d},{q}).")

    return "\n".join(lines) + "\n"


def main() -> None:
    out_dir = Path("instances")
    out_dir.mkdir(exist_ok=True)

    print(f"Generating instances with seed={SEED}...")
    print(f"{'Scenario':<10} {'Nodes':>6} {'Arcs':>6} {'Ships':>6} {'Cap':>8}  Output")
    print("-" * 60)

    for sid, (np, nh, nd, ns, tight) in TOPOLOGY.items():
        n_nodes = np + nh + nd
        n_arcs  = np * nh + nh * nd
        cap_label = "tight" if tight else "normal"
        content = generate_instance(np, nh, nd, ns, tight, SEED)
        out_path = out_dir / f"instance_{sid}.lp"
        out_path.write_text(content)
        print(f"{sid.upper():<10} {n_nodes:>6} {n_arcs:>6} {ns:>6} {cap_label:>8}  {out_path}")

    print(f"\nDone. Instance files written to {out_dir}/")
    print("Run verify_all.py to confirm solver results.")


if __name__ == "__main__":
    main()
