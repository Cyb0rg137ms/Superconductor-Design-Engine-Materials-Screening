# Limitations

* **No materials prediction.** Nothing in this repository computes λ, ω_log or μ* from a crystal
  structure. Allen-Dynes/McMillan only map those three numbers to T_c. Any "candidate" T_c is only as
  good as its inputs, and the v1 inputs are unsourced.
* **Candidate database = hypotheses.** The 8 v1 entries (CaH12 at 8 GPa, YH9 at 5 GPa, C6Li, K3C60,
  BiSb, NdNiO2, metastable metallic H, …) carry v1's `tc_predicted` and `confidence` values. These are
  not supported by any calculation here and several contradict the literature (e.g. no ambient-
  or low-pressure room-temperature superconductor is established). They are labelled
  `status = "unverified hypothesis (v1, unsourced)"`.
* **`evaluate_clathrate` is a toy heuristic** (λ and ω_log come from ad-hoc scaling rules).
* **1-D chain BCS model.** Mean-field, s-wave, constant coupling over the whole band (no Debye cut-off),
  one dimension. With g ≈ 1–5 eV the gaps and T_c are in eV / thousands of K. These are model units
  that illustrate the gap equation; they say nothing about real materials. The strong-coupling rise
  of 2Δ0/k_BT_c in this model is a property of the band-wide coupling, not Eliashberg physics.
* **Weak coupling below grid resolution.** For g ≲ 0.6 eV (t = 1 eV) Δ0 is smaller than the k-grid
  energy spacing near E_F and the solver returns 0. Increase `n_k` to resolve it.
* **Allen-Dynes** is a fit to Eliashberg solutions for λ ≲ 3 and is less accurate for λ > 3.

## Roadmap
* α²F(ω) input → λ, ω_log, ω̄2 (so Allen-Dynes inputs can come from DFPT output files).
* Isotropic Eliashberg solver on the imaginary axis as a cross-check of Allen-Dynes.
* 2-D/3-D lattices and a Debye-window coupling.
