# Architecture (v2)

```mermaid
flowchart LR
  subgraph scdesign [scdesign: validated core]
    AD[allen_dynes.py<br/>McMillan + Allen-Dynes, vectorised]
    BCS[bcs.py<br/>Chain, gap_rhs, solve_gap / solve_tc by bisection,<br/>universal BCS curve, DOS, coherence length]
    BEN[benchmarks.py<br/>validation + timing → bench.json, PNG]
    CLI[cli.py: tc · gap · screen · bench]
  end
  subgraph materials [materials: v1 API, kept for compatibility]
    DB[database.py<br/>v1 candidate list + DISCLAIMER]
    DE[designer.py<br/>calculate_allen_dynes_tc → AD<br/>evaluate_clathrate = toy heuristic]
    PH[physics.py<br/>v1 loop functions; solve_gap_self_consistent → BCS]
  end
  CLI --> AD & BCS & BEN & DB
  DE --> AD
  PH --> BCS
  RS[run_search.py] --> DB & DE
```

* **Gap equation.** `gap_rhs(chain, Δ, T) = (g/N) Σ_k tanh(E_k/2k_BT)/(2E_k)` is strictly decreasing
  in Δ, so the root of `gap_rhs = 1` is bracketed and found by bisection: guaranteed convergence, no
  mixing parameter, no false "converged" states (v1's fixed-point loop declared convergence at
  Δ ≈ 6·10⁻⁶ for g = 0.5 because its tolerance was absolute).
* **T_c** is the root of `gap_rhs(Δ→0, T) = 1`, also by bisection on a log-T bracket.
* **Universal curve** `bcs_universal_gap(T/T_c)` solves the weak-coupling BCS equation in reduced
  units on a logarithmic ξ grid with the analytic `asinh` contribution of `[0, x0]`, used as the
  reference in the validation plot.
