"""Mean-field BCS on a 1-D tight-binding chain (energies in eV, temperatures in K), vectorised in NumPy.

Gap equation (s-wave, contact interaction g, all k in the Brillouin zone):

    1 = (g/N) Σ_k tanh(E_k / 2k_BT) / (2E_k),     E_k = sqrt(ξ_k² + Δ²),  ξ_k = −2t cos k − μ.

The right-hand side decreases monotonically in Δ and in T, so Δ(T) and T_c are found by
bisection, which is guaranteed to converge (the v1 fixed-point iteration with an absolute
tolerance reported "converged" at Δ ≈ 6e-6 eV for weak coupling while still drifting).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

KB_EV = 8.617333262e-5  # Boltzmann constant, eV/K
BCS_RATIO = 2.0 * np.pi / np.exp(np.euler_gamma)  # 2Δ0/(k_B T_c) = 3.5276 in weak coupling


@dataclass(frozen=True)
class Chain:
    hopping_t: float = 1.0
    mu: float = 0.0
    coupling_g: float = 2.0
    n_k: int = 20000

    def xi(self) -> NDArray[np.float64]:
        k = np.pi * (2 * np.arange(self.n_k) + 1 - self.n_k) / self.n_k  # midpoints, avoids k = ±π/2 exactly
        return -2.0 * self.hopping_t * np.cos(k) - self.mu


def _thermal(x: NDArray[np.float64], temperature: float) -> NDArray[np.float64]:
    """tanh(x / 2kT) / (2x), with the x→0 and T→0 limits handled."""
    ax = np.abs(x)
    if temperature <= 0:
        return 1.0 / (2.0 * np.maximum(ax, 1e-300))
    kt = KB_EV * temperature
    small = ax < 1e-12
    return np.where(small, 1.0 / (4.0 * kt), np.tanh(ax / (2.0 * kt)) / (2.0 * np.maximum(ax, 1e-300)))


def gap_rhs(chain: Chain, delta: float, temperature: float = 0.0) -> float:
    """(g/N) Σ tanh(E/2kT)/(2E); the gap equation is gap_rhs == 1."""
    e = np.sqrt(chain.xi() ** 2 + delta**2)
    return float(chain.coupling_g * _thermal(e, temperature).mean())


def solve_gap(chain: Chain, temperature: float = 0.0, iters: int = 200) -> float:
    """Self-consistent Δ(T) ≥ 0 in eV (0 if the normal state is the only solution)."""
    if gap_rhs(chain, 0.0, temperature) <= 1.0:
        return 0.0
    lo, hi = 0.0, chain.coupling_g  # rhs(g) ≤ 1/2
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if gap_rhs(chain, mid, temperature) > 1.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-14:
            break
    return 0.5 * (lo + hi)


def solve_tc(chain: Chain, iters: int = 200) -> float:
    """T_c in K: largest T with a non-zero gap (linearised gap equation = 1)."""
    if gap_rhs(chain, 0.0, 0.0) <= 1.0:
        return 0.0
    lo, hi = 0.0, chain.coupling_g / (4.0 * KB_EV)  # rhs(T) ≤ g/(4kT)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if gap_rhs(chain, 0.0, mid) > 1.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9 * max(hi, 1.0):
            break
    return 0.5 * (lo + hi)


def gap_curve(chain: Chain, temperatures: NDArray[np.float64]) -> NDArray[np.float64]:
    return np.array([solve_gap(chain, float(t)) for t in temperatures])


def bcs_universal_gap(t_reduced: NDArray[np.float64], n: int = 4000) -> NDArray[np.float64]:
    """Weak-coupling BCS Δ(T)/Δ(0) vs T/T_c (constant DOS, Debye cutoff → ∞).

    Uses ln(Δ0/Δ) = 2 Σ ∫_0^∞ dx f(E)/E form: ln(Δ0/Δ) = 2∫_0^∞ dξ (1/E) / (exp(E/kT)+1),
    with k T_c = Δ0 e^γ / π. Solved by bisection per temperature.
    """
    out = []
    x0 = 1e-8
    x = np.geomspace(x0, 80.0, n)  # ξ / Δ0, log grid resolves small Δ near T_c
    for tr in np.atleast_1d(t_reduced):
        if tr >= 1.0:
            out.append(0.0)
            continue
        if tr <= 0.0:
            out.append(1.0)
            continue
        kt = tr * np.exp(np.euler_gamma) / np.pi  # in units of Δ0

        def f(d: float, kt: float = kt) -> float:
            e = np.sqrt(x**2 + d**2)
            integ = 2.0 * np.trapezoid(1.0 / (e * (np.exp(np.minimum(e / kt, 700)) + 1.0)), x)
            integ += np.arcsinh(x0 / d)  # [0, x0]: f(E) ≈ 1/2
            return float(np.log(1.0 / d) - integ)

        lo, hi = 1e-7, 1.0  # f(lo) > 0 > ... f decreasing to f(1) = -integ < 0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        out.append(0.5 * (lo + hi))
    return np.array(out)


def density_of_states(
    chain: Chain, delta: float, energies: NDArray[np.float64], broadening: float = 0.05
) -> NDArray[np.float64]:
    """Lorentzian-broadened BCS quasiparticle DOS (per site, per spin)."""
    xi = chain.xi()
    e = np.sqrt(xi**2 + delta**2)
    safe = np.where(e > 1e-12, e, 1.0)
    u2 = np.where(e > 1e-12, 0.5 * (1 + xi / safe), 0.5)
    v2 = 1.0 - u2
    w = energies[:, None]
    lp = broadening / (np.pi * ((w - e[None, :]) ** 2 + broadening**2))
    lh = broadening / (np.pi * ((w + e[None, :]) ** 2 + broadening**2))
    return np.asarray((u2 * lp + v2 * lh).mean(axis=1))


def coherence_length(chain: Chain, delta: float) -> float:
    """Pippard/BCS ξ0 = ħ v_F / (π Δ) in lattice units (ħ v_F = 2t sin k_F · a)."""
    if delta <= 0:
        return float("inf")
    c = -chain.mu / (2.0 * chain.hopping_t)
    if abs(c) >= 1:
        return float("inf")  # no Fermi surface (band insulator)
    kf = np.arccos(-c) if chain.hopping_t > 0 else np.arccos(c)
    return float(2.0 * abs(chain.hopping_t) * np.sin(kf) / (np.pi * delta))
