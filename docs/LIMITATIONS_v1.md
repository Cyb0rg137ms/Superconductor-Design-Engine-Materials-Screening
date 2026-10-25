"""
LIMITATIONS.md — Superconductor Design Engine
=============================================

# Known Limitations and Future Work

## Physics Approximations (BCS / Allen-Dynes)

### 1. Weak-Coupling BCS Approximations
Our self-consistent gap solver assumes weak-coupling BCS theory:
- Good for traditional superconductors (like lead, aluminium) where $\lambda < 0.5$.
- Fails for modern high-$T_c$ superconductors (e.g. cuprates, iron pnictides, or dense hydrides) where strong-coupling effects and non-phonon mechanisms dominate.
- Fails to model retardation effects (frequency dependence of the electron-phonon interaction).

To solve this, a production-grade materials simulator must solve the full **Eliashberg equations** on the imaginary frequency axis.

### 2. Allen-Dynes Empirical Bounds
The Allen-Dynes equation is an empirical correction to McMillan's formula:
- It works well up to $\lambda \approx 1.5$.
- For extremely strong coupling ($\lambda > 2$, as found in dense hydrogen clathrates at megabar pressures), it underestimates $T_c$.
- It assumes a single average phonon frequency ($\omega_{\text{log}}$) and does not capture structural instability ( imaginary phonon frequencies).

---

## Materials search & Optimization

### 1. Bayesian Optimization in Discrete Spaces
Our composer search uses a continuous Gaussian Process surrogate. However:
- Material composition spaces are highly discrete and structured (chemical formulas must satisfy valency rules, charge neutrality, and thermodynamic stability).
- Simple GP searches can propose unphysical combinations (e.g., $H_{3.14}S_{0.86}$).
- Production models use discrete search spaces constrained by crystal structure prediction (USPEX, CALYPSO).
"""
