"""
test_hamiltonian.py
===================
Tests for superconductor BCS Hamiltonian solver.
"""

import math
import pytest

from materials.physics import (
    tight_binding_dispersion,
    bcs_quasiparticle_energy,
    bcs_gap_equation,
    solve_gap_self_consistent,
    density_of_states,
    coherence_length,
)


def test_tight_binding_dispersion():
    eps = tight_binding_dispersion(k=0.0, hopping_t=1.0)
    assert abs(eps - (-2.0)) < 1e-10
    eps_pi = tight_binding_dispersion(k=math.pi, hopping_t=1.0)
    assert abs(eps_pi - 2.0) < 1e-10


def test_bcs_quasiparticle_energy():
    E = bcs_quasiparticle_energy(epsilon_k=1.0, mu=1.0, delta=0.3)
    assert abs(E - 0.3) < 1e-10
    E_zero = bcs_quasiparticle_energy(2.0, mu=0.5, delta=0.0)
    assert abs(E_zero - 1.5) < 1e-10


def test_solve_gap_self_consistent():
    gap, converged, _ = solve_gap_self_consistent(
        hopping_t=1.0, mu=0.0, coupling_g=1.5, n_k=200
    )
    assert converged
    assert gap > 0


def test_density_of_states():
    energies, dos = density_of_states(hopping_t=1.0, mu=0.0, delta=0.3, n_energies=50, n_k=100)
    assert len(energies) == 50
    assert len(dos) == 50
    assert all(d >= 0 for d in dos)


def test_coherence_length():
    xi = coherence_length(hopping_t=1.0, mu=0.0, delta=0.0)
    assert xi == float("inf")
    xi_pos = coherence_length(hopping_t=1.0, mu=0.0, delta=0.3)
    assert xi_pos > 0
