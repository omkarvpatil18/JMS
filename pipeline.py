"""
pipeline.py — Encode-Solve-Decode Pipeline
===========================================
Implements Algorithm 2 from Section 3.3.3:

  1. Encode: load ERP-validated instance facts from a .lp file
  2. Solve:  invoke clingo 5.8.0 with opt-mode=opt
  3. Decode: extract use(K,I,J) atoms and reconstruct execution plan

Paper : A Cyber-Physical Manufacturing Execution Architecture
        Integrating ERP Transaction Automation and
        Autonomous Decision-Making
Authors: Omkar Vishwas Patil,  Omid Fatahi Valilai
Journal: Journal of Manufacturing Systems (JMS), Elsevier

NOTE — Scope of this implementation:
    This script implements the ASP decision layer (Algorithm 2).
    The ERP execution layer (Algorithm 1 — UiPath automation) is
    specified as a formal algorithm in Section 3.2 of the paper.
    Algorithm 1 has not been deployed as a runnable UiPath bot;
    this is disclosed as Limitation L1 in Section 7.2.

Requirements:
    pip install clingo

Usage:
    # Baseline scenario
    python pipeline.py instances/instance_s1.lp

    # Disruption scenario
    python pipeline.py instances/instance_s1_disruption.lp

    # Custom instance
    python pipeline.py my_instance.lp --time-limit 30
"""

import argparse
import json
import threading
import time
from pathlib import Path

import clingo


# ---------------------------------------------------------------------------
# Algorithm 2 — Encode–Solve–Decode pipeline
# ---------------------------------------------------------------------------

def encode(rules_file: str, instance_file: str) -> clingo.Control:
    """
    Encode step: load rule template + instance facts into clingo.
    Corresponds to Algorithm 2, lines 1–4.
    """
    ctl = clingo.Control(["--opt-mode=opt", "--stats"])
    ctl.load(rules_file)
    ctl.load(instance_file)
    ctl.ground([("base", [])])
    return ctl


def solve(ctl: clingo.Control, time_limit: int = 20) -> dict:
    """
    Solve step: invoke clingo and capture the cost-minimising stable model.
    Corresponds to Algorithm 2, lines 5–10.

    Returns a dictionary with:
      - best_cost:  the cost of the best stable model found
      - use_atoms:  list of use(K,I,J) atoms in the solution
      - status:     'Optimal' if proven optimal, 'Best found*' if time limit hit
      - atoms:      ground program atom count
      - rules_tr:   transformed rule count
      - gnd_ms:     grounding time in milliseconds
      - solve_ms:   solving time in milliseconds
      - total_ms:   total wall-clock time in milliseconds
    """
    best_cost = None
    use_atoms = []

    def on_model(model: clingo.Model) -> None:
        nonlocal best_cost, use_atoms
        best_cost = model.cost[0] if model.cost else None
        use_atoms = [str(a) for a in model.symbols(shown=True)]

    t0 = time.time()
    timer = threading.Timer(time_limit, ctl.interrupt)
    timer.start()
    result = ctl.solve(on_model=on_model)
    timer.cancel()
    total_ms = round((time.time() - t0) * 1000)

    stats = ctl.statistics
    atoms   = int(stats["problem"]["lp"]["atoms"])
    rules   = int(stats["problem"]["lp"]["rules_tr"])
    gnd_ms  = round(
        (stats["summary"]["times"]["total"] - stats["summary"]["times"]["solve"]) * 1000, 1
    )
    solve_ms = round(stats["summary"]["times"]["solve"] * 1000, 1)
    status   = "Optimal" if result.exhausted else "Best found*"

    return {
        "best_cost": best_cost,
        "use_atoms": use_atoms,
        "status":    status,
        "atoms":     atoms,
        "rules_tr":  rules,
        "gnd_ms":    gnd_ms,
        "solve_ms":  solve_ms,
        "total_ms":  total_ms,
    }


def decode(use_atoms: list[str]) -> dict[str, list[str]]:
    """
    Decode step: reconstruct per-shipment paths from use(K,I,J) atoms.
    Corresponds to Algorithm 2, lines 11–13.

    Returns a dict mapping shipment id -> ordered list of arc strings.
    """
    # Parse use(k,i,j) atoms
    arcs: dict[str, list[tuple[str, str]]] = {}
    for atom in use_atoms:
        # atom format: use(k1,p1,h1)
        inner = atom[4:-1]       # strip 'use(' and ')'
        parts = inner.split(",")
        if len(parts) != 3:
            continue
        k, i, j = parts
        arcs.setdefault(k, []).append((i, j))

    # Reconstruct ordered paths for each shipment
    paths: dict[str, list[str]] = {}
    for k, arc_list in arcs.items():
        # Build adjacency for this shipment
        adj: dict[str, str] = {i: j for i, j in arc_list}
        # Find source (node that is never a destination within this shipment)
        dests = {j for _, j in arc_list}
        sources = [i for i, _ in arc_list if i not in dests]
        if not sources:
            paths[k] = [f"{i}->{j}" for i, j in arc_list]
            continue
        node = sources[0]
        path = [node]
        visited = {node}
        while node in adj and adj[node] not in visited:
            node = adj[node]
            path.append(node)
            visited.add(node)
        paths[k] = [f"{path[n]}->{path[n+1]}" for n in range(len(path)-1)]

    return dict(sorted(paths.items()))


def run_pipeline(instance_file: str,
                 rules_file: str = "rules.lp",
                 time_limit: int = 20,
                 verbose: bool = True) -> dict:
    """
    Full encode–solve–decode pipeline for one instance.
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"  Encode–Solve–Decode Pipeline")
        print(f"  Instance : {instance_file}")
        print(f"  Rules    : {rules_file}")
        print(f"  Solver   : clingo {clingo.__version__}")
        print(f"  Time limit: {time_limit}s")
        print(f"{'='*60}")

    # 1. Encode
    ctl = encode(rules_file, instance_file)
    if verbose:
        print(f"\n  [Encode] Ground program ready.")

    # 2. Solve
    sol = solve(ctl, time_limit)
    if verbose:
        print(f"  [Solve]  Status   : {sol['status']}")
        print(f"           Cost     : {sol['best_cost']}")
        print(f"           Atoms    : {sol['atoms']}")
        print(f"           Rules(tr): {sol['rules_tr']}")
        print(f"           Gnd      : {sol['gnd_ms']} ms")
        print(f"           Solve    : {sol['solve_ms']} ms")
        print(f"           Total    : {sol['total_ms']} ms")

    # 3. Decode
    paths = decode(sol["use_atoms"])
    if verbose:
        print(f"\n  [Decode] Execution plan Π:")
        if paths:
            for shipment, arcs in paths.items():
                arc_str = " → ".join(
                    a.split("->")[0] for a in arcs
                ) + " → " + arcs[-1].split("->")[1]
                cost_note = ""
                print(f"    {shipment}: {arc_str}{cost_note}")
        else:
            print("    No feasible plan found.")

    result = {
        "instance":   instance_file,
        "rules":      rules_file,
        "status":     sol["status"],
        "cost":       sol["best_cost"],
        "paths":      paths,
        "use_atoms":  sol["use_atoms"],
        "stats": {
            "atoms":    sol["atoms"],
            "rules_tr": sol["rules_tr"],
            "gnd_ms":   sol["gnd_ms"],
            "solve_ms": sol["solve_ms"],
            "total_ms": sol["total_ms"],
        },
    }
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Encode–Solve–Decode pipeline for manufacturing execution planning."
    )
    parser.add_argument(
        "instance",
        help="Path to an ASP instance file (e.g. instances/instance_s1.lp)"
    )
    parser.add_argument(
        "--rules",
        default="rules.lp",
        help="Path to the ASP rule template (default: rules.lp)"
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=20,
        help="Solver time limit in seconds (default: 20)"
    )
    parser.add_argument(
        "--output-json",
        metavar="FILE",
        help="Write the full result to a JSON file"
    )
    args = parser.parse_args()

    if not Path(args.instance).exists():
        print(f"Error: instance file '{args.instance}' not found.")
        return
    if not Path(args.rules).exists():
        print(f"Error: rules file '{args.rules}' not found.")
        return

    result = run_pipeline(
        instance_file=args.instance,
        rules_file=args.rules,
        time_limit=args.time_limit,
        verbose=True,
    )

    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  Result written to {args.output_json}")


if __name__ == "__main__":
    main()
