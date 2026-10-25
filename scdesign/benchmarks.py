"""Reproducible validation + timing benchmarks (``scdesign bench``)."""

from __future__ import annotations

import json
import logging
import platform
import time
from pathlib import Path
from typing import Any

import numpy as np

from scdesign.allen_dynes import allen_dynes_tc, mcmillan_tc
from scdesign.bcs import BCS_RATIO, KB_EV, Chain, bcs_universal_gap, gap_curve, gap_rhs, solve_gap, solve_tc

log = logging.getLogger(__name__)

# Inputs exactly as listed in v1's BENCHMARK_RESULTS.md (λ, ω_log, μ* there are unsourced);
# experimental T_c values are the commonly quoted ones.
V1_ALLEN_DYNES_CASES: list[dict[str, Any]] = [
    {"name": "Pb", "lam": 1.55, "omega_log": 58.0, "mu": 0.13, "v1_claimed": 7.1, "exp_tc": 7.2},
    {"name": "Nb", "lam": 1.04, "omega_log": 163.0, "mu": 0.13, "v1_claimed": 9.3, "exp_tc": 9.25},
    {
        "name": "H3S (150 GPa)",
        "lam": 2.20,
        "omega_log": 1100.0,
        "mu": 0.13,
        "v1_claimed": 191.0,
        "exp_tc": 203.0,
    },
    {
        "name": "LaH10 (170 GPa)",
        "lam": 2.50,
        "omega_log": 1250.0,
        "mu": 0.13,
        "v1_claimed": 242.0,
        "exp_tc": 250.0,
    },
]


def _v1_allen_dynes(w: float, lam: float, mu: float, ratio: float = 1.2) -> float:
    """The v1 formula, reproduced verbatim for comparison (wrong Λ1, Λ2 constants)."""
    den = lam - mu * (1.0 + 0.62 * lam)
    if lam <= 0 or den <= 0:
        return 0.0
    f1 = (1.0 + (lam / (1.01 * (1.0 + 2.0 * mu))) ** 1.5) ** (1.0 / 3.0)
    f2 = 1.0 + (ratio - 1.0) * lam**2 / (lam**2 + (1.61 * (1.0 + 2.0 * mu)) ** 2)
    return float(f1 * f2 * w / 1.20 * np.exp(-1.04 * (1.0 + lam) / den))


def allen_dynes_table() -> list[dict[str, Any]]:
    rows = []
    for c in V1_ALLEN_DYNES_CASES:
        rows.append(
            {
                **c,
                "v1_code": round(_v1_allen_dynes(c["omega_log"], c["lam"], c["mu"]), 2),
                "mcmillan": round(float(mcmillan_tc(c["omega_log"], c["lam"], c["mu"])), 2),
                "allen_dynes": round(float(allen_dynes_tc(c["omega_log"], c["lam"], c["mu"], 1.2)), 2),
            }
        )
    return rows


def ratio_vs_coupling(gs: list[float], n_k: int) -> list[dict[str, float]]:
    rows = []
    for g in gs:
        c = Chain(coupling_g=g, n_k=n_k)
        d0, tc = solve_gap(c), solve_tc(c)
        rows.append(
            {"g": g, "delta0_ev": d0, "tc_k": tc, "ratio": 2 * d0 / (KB_EV * tc) if tc else float("nan")}
        )
    return rows


def gap_curves(gs: list[float], n_k: int, points: int) -> dict[str, Any]:
    tr = np.linspace(0.0, 0.995, points)
    out: dict[str, Any] = {
        "t_reduced": tr.tolist(),
        "universal": bcs_universal_gap(tr).tolist(),
        "chains": {},
    }
    for g in gs:
        c = Chain(coupling_g=g, n_k=n_k)
        tc, d0 = solve_tc(c), solve_gap(c)
        out["chains"][str(g)] = (gap_curve(c, tr * tc) / d0).tolist()
    return out


def _time(fn: Any, repeats: int = 3) -> float:
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return float(np.median(ts) * 1e3)


def timing() -> list[dict[str, Any]]:
    from materials.physics import bcs_gap_equation

    rows = []
    for n_k in (500, 5000):
        c = Chain(coupling_g=2.0, n_k=n_k)
        rows.append(
            {
                "n_k": n_k,
                "rhs_v1_loop_ms": _time(lambda n_k=n_k: bcs_gap_equation(0.3, 1.0, 0.0, 2.0, n_k)),
                "rhs_numpy_ms": _time(lambda c=c: gap_rhs(c, 0.3)),
                "solve_gap_ms": _time(lambda c=c: solve_gap(c)),
                "solve_tc_ms": _time(lambda c=c: solve_tc(c)),
            }
        )
    return rows


def run(out_dir: Path | None = None, quick: bool = False) -> dict[str, Any]:
    n_k = 4000 if quick else 40000
    gs = [1.0, 1.5, 2.0, 3.0] if quick else [0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    res = {
        "machine": {"python": platform.python_version(), "platform": platform.platform()},
        "bcs_ratio_target": BCS_RATIO,
        "ratio_vs_g": ratio_vs_coupling(gs, n_k),
        "gap_curves": gap_curves([1.0, 3.0] if quick else [1.0, 2.0, 4.0], n_k, 12 if quick else 40),
        "allen_dynes": allen_dynes_table(),
        "timing": timing(),
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "bench.json").write_text(json.dumps(res, indent=2))
        _plot(res, out_dir / "bcs_validation.png")
    return res


def _plot(res: dict[str, Any], path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover
        log.warning("matplotlib missing; skipping plot")
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    gc = res["gap_curves"]
    a1.plot(gc["t_reduced"], gc["universal"], "k-", lw=2.5, label="BCS weak-coupling (universal)")
    for g, ys in gc["chains"].items():
        a1.plot(gc["t_reduced"], ys, "o", ms=3.5, label=f"1-D chain, g = {g} eV")
    a1.set(xlabel="T / T_c", ylabel="Δ(T) / Δ(0)", title="Self-consistent gap vs temperature")
    a1.legend(fontsize=8)
    rows = [r for r in res["ratio_vs_g"] if r["tc_k"] > 0]
    a2.plot([r["g"] for r in rows], [r["ratio"] for r in rows], "s-", label="computed 2Δ0 / k_B T_c")
    a2.axhline(res["bcs_ratio_target"], color="k", ls="--", label=f"BCS limit {res['bcs_ratio_target']:.4f}")
    a2.set(
        xlabel="coupling g (eV), t = 1 eV",
        ylabel="2Δ0 / k_B T_c",
        title="Gap ratio → BCS value at weak coupling",
    )
    a2.legend(fontsize=8)
    for ax in (a1, a2):
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
