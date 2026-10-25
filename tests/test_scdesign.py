import json

import numpy as np
import pytest

from scdesign import (
    BCS_RATIO,
    KB_EV,
    Chain,
    allen_dynes_tc,
    bcs_universal_gap,
    coherence_length,
    density_of_states,
    mcmillan_tc,
    solve_gap,
    solve_tc,
    strong_coupling_factors,
)
from scdesign.bcs import gap_curve, gap_rhs
from scdesign.benchmarks import _v1_allen_dynes, allen_dynes_table, run
from scdesign.cli import main


def test_mcmillan_known_value():
    # direct evaluation of McMillan's formula (ω_log/1.2) exp(-1.04(1+λ)/(λ-μ*(1+0.62λ)))
    w, lam, mu = 58.0, 1.55, 0.13
    expected = w / 1.2 * np.exp(-1.04 * (1 + lam) / (lam - mu * (1 + 0.62 * lam)))
    assert mcmillan_tc(w, lam, mu) == pytest.approx(expected)


def test_allen_dynes_constants():
    f1, f2 = strong_coupling_factors(1.0, 0.1, 1.0)
    l1 = 2.46 * (1 + 3.8 * 0.1)
    assert f1 == pytest.approx((1 + (1.0 / l1) ** 1.5) ** (1 / 3))
    assert f2 == pytest.approx(1.0)  # ratio 1 -> no shape correction


def test_allen_dynes_ge_mcmillan_and_zero_cases():
    for lam in (0.5, 1.0, 2.0, 3.0):
        assert allen_dynes_tc(500, lam, 0.1) >= mcmillan_tc(500, lam, 0.1)
    assert allen_dynes_tc(500, 0.0, 0.1) == 0.0
    assert allen_dynes_tc(500, 0.1, 0.2) == 0.0


def test_allen_dynes_vectorized():
    lam = np.array([0.5, 1.0, 2.0])
    out = allen_dynes_tc(300.0, lam, 0.1)
    assert out.shape == (3,)
    assert np.all(np.diff(out) > 0)
    assert out[1] == pytest.approx(allen_dynes_tc(300.0, 1.0, 0.1))


def test_v1_formula_overestimates():
    rows = allen_dynes_table()
    for r in rows:
        assert r["v1_code"] > r["allen_dynes"]
    assert _v1_allen_dynes(58, 1.55, 0.13) == pytest.approx(8.89, abs=0.01)


def test_gap_rhs_vectorized_matches_v1_loop():
    from materials.physics import bcs_gap_equation

    c = Chain(1.0, 0.1, 2.0, 400)
    for T in (0.0, 300.0):
        # v1 returns Δ·(g/N)Σ tanh/2E; v2 returns the Δ-normalised sum (gap eq. == 1).
        # v1 uses k_B = 8.617e-5 (rounded), hence the loose tolerance at T > 0.
        v1 = bcs_gap_equation(0.3, 1.0, 0.1, 2.0, 400, T) / 0.3
        assert gap_rhs(c, 0.3, T) == pytest.approx(v1, rel=1e-4 if T else 1e-10)


def test_gap_is_self_consistent_and_ratio_bcs():
    c = Chain(coupling_g=1.0, n_k=20000)
    d = solve_gap(c)
    assert gap_rhs(c, d) == pytest.approx(1.0, rel=1e-6)
    tc = solve_tc(c)
    assert 2 * d / (KB_EV * tc) == pytest.approx(BCS_RATIO, rel=2e-3)


def test_gap_vanishes_above_tc_and_monotone():
    c = Chain(coupling_g=2.0, n_k=4000)
    tc = solve_tc(c)
    assert solve_gap(c, 1.05 * tc) == 0.0
    curve = gap_curve(c, np.linspace(0, 0.95 * tc, 8))
    assert np.all(np.diff(curve) <= 1e-12) and curve[-1] > 0


def test_universal_gap_limits():
    tr = np.array([0.05, 0.99])
    v = bcs_universal_gap(tr)
    assert v[0] == pytest.approx(1.0, abs=1e-4)
    assert v[1] == pytest.approx(1.7367 * np.sqrt(0.01), rel=0.02)  # Ginzburg-Landau limit


def test_dos_and_coherence():
    c = Chain(coupling_g=2.0, n_k=2000)
    e = np.linspace(-3, 3, 301)
    rho = density_of_states(c, 0.3, e, broadening=0.02)
    assert e.shape == rho.shape == (301,)
    assert rho[np.argmin(abs(e))] < 0.2 * rho.max()  # gap at E=0
    assert coherence_length(c, 0.0) == float("inf")
    assert coherence_length(c, 0.3) > coherence_length(c, 0.6)


def test_bench_quick_writes_artifacts(tmp_path):
    res = run(tmp_path, quick=True)
    assert (tmp_path / "bench.json").exists()
    assert (tmp_path / "bcs_validation.png").stat().st_size > 1000
    assert json.loads((tmp_path / "bench.json").read_text())["allen_dynes"][0]["name"] == "Pb"
    assert abs(res["ratio_vs_g"][0]["ratio"] - BCS_RATIO) < 0.01


def test_cli(capsys, tmp_path):
    assert main(["tc", "--lam", "1.55", "--omega-log", "58", "--mu", "0.13"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["allen_dynes_k"] == pytest.approx(6.76, abs=0.01)
    assert main(["gap", "--g", "1.0", "--n-k", "4000"]) == 0
    assert "ratio_2delta_over_kTc" in json.loads(capsys.readouterr().out)
    assert main(["screen", "--max-pressure", "10", "--min-tc", "270"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert "hypothes" in out["disclaimer"]
    assert all(c["status"].startswith("unverified") for c in out["candidates"])
    assert main(["bench", "--quick", "--out", str(tmp_path)]) == 0


def test_run_search_prints_disclaimer(capsys, tmp_path, monkeypatch):
    import run_search

    monkeypatch.chdir(tmp_path)
    run_search.run_materials_screening()
    out = capsys.readouterr().out
    assert "unverified" in out and "toy heuristic" in out


def test_v1_compat_designer_uses_fixed_formula():
    from materials.designer import calculate_allen_dynes_tc

    assert calculate_allen_dynes_tc(58, 1.55, 0.13) == pytest.approx(allen_dynes_tc(58, 1.55, 0.13, 1.2))


def test_example_runs():
    import runpy

    runpy.run_path("examples/compare_formulas.py")
