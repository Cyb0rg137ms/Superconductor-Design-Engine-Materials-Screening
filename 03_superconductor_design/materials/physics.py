"""
physics.py
==========
BCS (Bardeen-Cooper-Schrieffer) mean-field Hamiltonian solver for superconductor design.
"""

from __future__ import annotations

import math
from typing import List, Tuple


def tight_binding_dispersion(
    k: float,
    hopping_t: float,
    lattice_a: float = 1.0,
) -> float:
    return -2.0 * hopping_t * math.cos(k * lattice_a)


def bcs_quasiparticle_energy(
    epsilon_k: float,
    mu: float,
    delta: float,
) -> float:
    xi_k = epsilon_k - mu
    return math.sqrt(xi_k * xi_k + delta * delta)


def bcs_gap_equation(
    delta: float,
    hopping_t: float,
    mu: float,
    coupling_g: float,
    n_k: int = 1000,
    temperature: float = 0.0,
    kB: float = 8.617e-5,
) -> float:
    rhs = 0.0
    for i in range(n_k):
        k = math.pi * (2 * i + 1 - n_k) / n_k
        eps_k = tight_binding_dispersion(k, hopping_t)
        E_k = bcs_quasiparticle_energy(eps_k, mu, delta)

        if E_k < 1e-12:
            continue

        if temperature < 1e-9:
            tanh_factor = 1.0
        else:
            arg = E_k / (2.0 * kB * temperature)
            tanh_factor = math.tanh(min(arg, 300.0))

        rhs += delta * tanh_factor / (2.0 * E_k)

    return (coupling_g / n_k) * rhs


def solve_gap_self_consistent(
    hopping_t: float,
    mu: float,
    coupling_g: float,
    delta_init: float = 0.1,
    n_k: int = 500,
    temperature: float = 0.0,
    max_iter: int = 200,
    tol: float = 1e-6,
) -> Tuple[float, bool, int]:
    alpha = 0.3
    delta = delta_init

    for i in range(max_iter):
        rhs = bcs_gap_equation(delta, hopping_t, mu, coupling_g, n_k, temperature)
        delta_new = (1 - alpha) * delta + alpha * rhs

        if abs(delta_new - delta) < tol:
            return delta_new, True, i + 1

        delta = delta_new

    return delta, False, max_iter


def density_of_states(
    hopping_t: float,
    mu: float,
    delta: float,
    n_energies: int = 200,
    energy_range: Tuple[float, float] = (-3.0, 3.0),
    broadening: float = 0.05,
    n_k: int = 500,
) -> Tuple[List[float], List[float]]:
    E_min, E_max = energy_range
    dE = (E_max - E_min) / n_energies
    energies = [E_min + (i + 0.5) * dE for i in range(n_energies)]
    dos = [0.0] * n_energies

    for ki in range(n_k):
        k = math.pi * (2 * ki + 1 - n_k) / n_k
        eps_k = tight_binding_dispersion(k, hopping_t)
        E_k = bcs_quasiparticle_energy(eps_k, mu, delta)
        xi_k = eps_k - mu

        if E_k < 1e-12:
            u2 = 0.5
            v2 = 0.5
        else:
            u2 = 0.5 * (1.0 + xi_k / E_k)
            v2 = 0.5 * (1.0 - xi_k / E_k)

        for j, E in enumerate(energies):
            lorentz_p = broadening / (math.pi * ((E - E_k) ** 2 + broadening ** 2))
            lorentz_h = broadening / (math.pi * ((E + E_k) ** 2 + broadening ** 2))
            dos[j] += (u2 * lorentz_p + v2 * lorentz_h) / n_k

    return energies, dos


def coherence_length(
    hopping_t: float,
    mu: float,
    delta: float,
    hbar: float = 6.582e-16,
    n_k: int = 100,
) -> float:
    if delta < 1e-10:
        return float("inf")

    v_F_sum = 0.0
    v_F_count = 0
    dk = math.pi / n_k

    for i in range(n_k):
        k = -math.pi / 2 + (i + 0.5) * dk
        eps_k = tight_binding_dispersion(k, hopping_t)
        if abs(eps_k - mu) < 4 * delta:
            v_F = abs(2.0 * hopping_t * math.sin(k))
            v_F_sum += v_F
            v_F_count += 1

    if v_F_count == 0:
        return float("inf")

    v_F_avg = v_F_sum / v_F_count
    return v_F_avg / (math.pi * delta)
