"""``scdesign`` command line: tc, gap, screen, bench."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from scdesign.allen_dynes import allen_dynes_tc, mcmillan_tc
from scdesign.bcs import KB_EV, Chain, coherence_length, solve_gap, solve_tc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="scdesign", description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tc", help="McMillan / Allen-Dynes T_c from λ, ω_log, μ*")
    t.add_argument("--lam", type=float, required=True)
    t.add_argument("--omega-log", type=float, required=True, help="K")
    t.add_argument("--mu", type=float, default=0.1)
    t.add_argument("--omega2-ratio", type=float, default=1.0)
    g = sub.add_parser("gap", help="self-consistent BCS gap and T_c on a 1-D chain")
    g.add_argument("--g", type=float, default=2.0, help="coupling (eV)")
    g.add_argument("--t", type=float, default=1.0, help="hopping (eV)")
    g.add_argument("--mu", type=float, default=0.0, help="chemical potential (eV)")
    g.add_argument("--n-k", type=int, default=20000)
    g.add_argument("--temperature", type=float, default=0.0, help="K")
    s = sub.add_parser("screen", help="v1 candidate list (unverified hypotheses) filtered by pressure/T_c")
    s.add_argument("--max-pressure", type=float, default=10.0)
    s.add_argument("--min-tc", type=float, default=270.0)
    b = sub.add_parser("bench", help="validation + timing benchmarks")
    b.add_argument("--out", type=Path, default=Path("docs/assets"))
    b.add_argument("--quick", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING)

    if a.cmd == "tc":
        out = {
            "mcmillan_k": float(mcmillan_tc(a.omega_log, a.lam, a.mu)),
            "allen_dynes_k": float(allen_dynes_tc(a.omega_log, a.lam, a.mu, a.omega2_ratio)),
        }
        print(json.dumps(out, indent=2))
    elif a.cmd == "gap":
        c = Chain(a.t, a.mu, a.g, a.n_k)
        d0, tc = solve_gap(c, a.temperature), solve_tc(c)
        out = {"delta_ev": d0, "tc_k": tc, "coherence_length_sites": coherence_length(c, d0)}
        if tc > 0 and a.temperature == 0:
            out["ratio_2delta_over_kTc"] = 2 * d0 / (KB_EV * tc)
        print(json.dumps(out, indent=2))
    elif a.cmd == "screen":
        from materials.database import DISCLAIMER, MaterialsDatabase

        db = MaterialsDatabase()
        hits = [m for m in db.filter_by_pressure(a.max_pressure) if m["tc_predicted"] >= a.min_tc]
        print(json.dumps({"disclaimer": DISCLAIMER, "candidates": hits}, indent=2))
    else:
        from scdesign.benchmarks import run

        res = run(a.out, quick=a.quick)
        for r in res["ratio_vs_g"]:
            print(
                f"g={r['g']:<5} Δ0={r['delta0_ev']:.5f} eV  Tc={r['tc_k']:9.2f} K  2Δ0/kTc={r['ratio']:.4f}"
            )
        print(f"BCS limit {res['bcs_ratio_target']:.4f}")
        for r in res["allen_dynes"]:
            print(
                f"{r['name']:<16} v1 claimed {r['v1_claimed']:6.1f}  v1 code {r['v1_code']:7.2f}  "
                f"McMillan {r['mcmillan']:7.2f}  Allen-Dynes {r['allen_dynes']:7.2f}  exp {r['exp_tc']:6.1f} K"
            )
        for r in res["timing"]:
            print(r)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
