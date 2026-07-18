# Supplementary Repository

## A Cyber-Physical Manufacturing Execution Architecture Integrating ERP Transaction Automation and Autonomous Decision-Making

**Authors:** Omkar Vishwas Patil, Kushal Bhandari, Omid Fatahi Valilai  
**Journal:** Journal of Manufacturing Systems (JMS), Elsevier  
**Solver:** clingo 5.8.0 (Potsdam Answer Set Solving Collection)

---

## What is in this repository

This repository contains the ASP decision layer implementation and all instance files needed to reproduce the solver results reported in Sections 4 and 5 of the paper.

| File | Description |
|---|---|
| `rules.lp` | ASP rule template (Listing 1, Section 3.3.2) — stable across all planning cycles |
| `pipeline.py` | Encode–solve–decode pipeline (Algorithm 2, Section 3.3.3) |
| `verify_all.py` | Automated reproducibility verification script |
| `generate_instances.py` | Regenerates S2–S7 instance files from stated parameters |
| `instances/instance_s1.lp` | Baseline instance — SAP case study, Section 4 |
| `instances/instance_s1_disruption.lp` | Disruption variant — H1→D1 arc removed, Section 4.5 |
| `instances/instance_s1_greedy_comparison.lp` | Greedy comparison instance |
| `instances/instance_s2.lp` — `instance_s7.lp` | Computational experiment instances S2–S7, Section 5 |

---

## Important scope note

This repository covers the **ASP autonomous decision layer** (Algorithm 2).

The **ERP execution layer** (Algorithm 1 — UiPath automation pipeline) is specified as a formal algorithm in Section 3.2 of the paper. Algorithm 1 has not been deployed as a runnable UiPath bot against a live ERP system. The SAP S/4HANA screenshots in Section 4.1 of the paper confirm that the underlying ERP data model and transaction structure are executable in a real ERP environment, but these were produced through manual transaction execution in a non-production sandbox. This is disclosed as Limitation L1 in Section 7.2.

---

## Requirements

```bash
pip install clingo
```

Requires clingo 5.8.0. Results may differ with other versions due to internal solver heuristics.

---

## Reproducing the paper results

### Step 1 — Verify all solver results

```bash
python verify_all.py
```

This re-runs all scenarios from Sections 4 and 5 and reports PASS/FAIL for each. Expected output:

```
Scenario                                 Atoms  Rules   Cost Status         Result
------------------------------------------------------------------------
S1 (baseline, Section 4)                  144    240     65 Optimal          PASS ✓
S1 disruption (Section 4.5)               130    211     79 Optimal          PASS ✓
S2 (9 nodes, 5 ships)                     359    843     95 Optimal          PASS ✓
S3 (13 nodes, 10 ships)                  1103   3594   214* Best found*      PASS ✓
S4 (20 nodes, 20 ships, normal cap)      4344  12041   455* Best found*      PASS ✓
S5 (20 nodes, 20 ships, tight cap)       4334  12021   469* Best found*      PASS ✓
S6 (28 nodes, 30 ships, normal cap)     10616  27904   732* Best found*      PASS ✓
S7 (28 nodes, 30 ships, tight cap)      10580  27832   769* Best found*      PASS ✓
```

`*` Best-found costs (S3–S7) may vary slightly across hardware due to solver non-determinism at the time boundary. Atom/rule counts are deterministic and will always match.

### Step 2 — Run individual scenarios

```bash
# Baseline case study (Section 4)
python pipeline.py instances/instance_s1.lp

# Disruption scenario (Section 4.5)
python pipeline.py instances/instance_s1_disruption.lp

# Computational experiment S2
python pipeline.py instances/instance_s2.lp --time-limit 60

# Save result to JSON
python pipeline.py instances/instance_s1.lp --output-json result_s1.json
```

### Step 3 — Run the ASP solver directly

```bash
# Baseline (Section 4) — proven optimal
clingo rules.lp instances/instance_s1.lp --opt-mode=opt -n 1

# Disruption (Section 4.5) — proven optimal  
clingo rules.lp instances/instance_s1_disruption.lp --opt-mode=opt -n 1

# Larger instances — 20-second time limit
clingo rules.lp instances/instance_s3.lp --opt-mode=opt -n 1 --time-limit=20
```

### Step 4 — Regenerate S2–S7 instances

If you wish to verify the instance generation from the stated parameters:

```bash
python generate_instances.py
python verify_all.py
```

---

## Verified solver results

All results below were obtained using clingo 5.8.0 on the instance files in this repository.

| Scenario | Instance | Atoms | Rules (tr) | Cost | Status | Gnd (ms) | Total (ms) |
|---|---|---|---|---|---|---|---|
| S1 | instance_s1.lp | 144 | 240 | **65** | Optimal | 3.1 | 3 |
| S1_disruption | instance_s1_disruption.lp | 130 | 211 | **79** | Optimal | 2.1 | 2 |
| S2 | instance_s2.lp | 359 | 843 | 95 | Optimal | 3.2 | 2 |
| S3 | instance_s3.lp | 1103 | 3594 | 214* | Best found* | 7.1 | 20001 |
| S4 | instance_s4.lp | 4344 | 12041 | 455* | Best found* | 20.5 | 20005 |
| S5 | instance_s5.lp | 4334 | 12021 | 469* | Best found* | 21.6 | 20004 |
| S6 | instance_s6.lp | 10616 | 27904 | 732* | Best found* | 61.3 | 20004 |
| S7 | instance_s7.lp | 10580 | 27832 | 769* | Best found* | 56.5 | 20003 |

**Bold** = key results cited in the paper (Section 4): baseline cost 65, disruption cost 79.  
`*` = best-found within 20-second time limit; cost may vary slightly across hardware.

---

## Instance file format

Each instance file defines the manufacturing execution network as ASP facts:

```prolog
node(V).        % V is a node (plant, hub, or destination)
edge(I,J).      % directed transport lane (I,J) is available
cost(I,J,C).    % generalised transport cost C for lane (I,J)
cap(I,J,U).     % capacity U in tonnes for lane (I,J)
ship(K,O,D,Q).  % shipment K from origin O to destination D, quantity Q tonnes
```

The rule template `rules.lp` encodes the flow conservation constraints, capacity constraints, and cost objective that are stable across all instances. See Listing 1 and Section 3.3.2 of the paper.

---

## Solver configuration

All results in the paper used:

- Solver: `clingo 5.8.0`
- Mode: `--opt-mode=opt` (branch-and-bound to proven optimality)
- Time limit: 20 seconds for S3–S7; none for S1, S1_disruption, S2
- Seed: `--rand-freq=0` (default deterministic heuristic)

Extended solver configuration (multi-criteria objectives, soft constraints, infeasibility diagnostics) is documented in Appendix A of the paper.

---

## Citation

If you use this code or the instance files, please cite:

```
Patil, O.V., Bhandari, K., Fatahi Valilai, O. (2026).
A Cyber-Physical Manufacturing Execution Architecture Integrating
ERP Transaction Automation and Autonomous Decision-Making.
Journal of Manufacturing Systems. [in review]
```

---

## Contact

For questions about the ASP decision layer or instance files, please open a GitHub issue.  
For questions about the ERP execution layer specification (Algorithm 1), contact the corresponding author.
