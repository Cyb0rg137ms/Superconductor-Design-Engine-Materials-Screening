# Superconductor-Design-ML — Architecture & Technical Reference

> **Full Project Name:** Superconductor-Design-ML — Materials Discovery Engine
> **Category:** Computational Materials Science / Physics-Guided ML
> **Language:** Python 3.9+, NumPy
> **Test Coverage:** 4/4 unit tests passing ✅

---

## 1. Architecture Overview

```
03_superconductor_design/
├── materials/
│   ├── database.py     # Stoichiometry candidate registry
│   ├── designer.py     # Allen-Dynes Tc calculator & clathrate evaluator
│   ├── visualizer.py   # ASCII histogram & terminal plotting engine
│   └── __init__.py
├── tests/
│   └── test_materials.py
├── run_search.py       # End-to-end screening pipeline
└── README.md
```

### Component Interaction

```
┌──────────────────────────────────────────────────────────────┐
│              SUPERCONDUCTOR DESIGN PIPELINE                  │
│                                                              │
│  CandidateDatabase ──► Filter by pressure/temp constraints   │
│          │                                                   │
│          ▼                                                   │
│  SuperconductorDesigner                                      │
│    ├── compute_allen_dynes_tc(λ, μ*, θ_log)                 │
│    └── evaluate_clathrate(H_count, metal_mass)              │
│          │                                                   │
│          ▼                                                   │
│  ScreeningVisualizer                                         │
│    ├── ASCII Tc histogram                                    │
│    └── Top-N candidate ranking table                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Framework

### 2.1 Allen-Dynes Modification of the McMillan Formula

The critical temperature `Tc` (in Kelvin) for a conventional superconductor is:

```
Tc = (θ_log / 1.2)  ×  exp( -1.04 × (1 + λ)  /  (λ - μ* × (1 + 0.62λ)) )
     ×  f1  ×  f2

Parameters:
  λ       = electron-phonon coupling constant  (dimensionless, typically 0.3 – 3.0)
  μ*      = Coulomb pseudopotential  (screened electron-electron repulsion, ~0.1 – 0.15)
  θ_log   = logarithmic average phonon frequency  (in Kelvin)
  f1, f2  = strong-coupling correction factors (see below)
```

### 2.2 Strong-Coupling Correction Factor f1

When λ > 1.5, the weak-coupling McMillan formula becomes inaccurate.
The `f1` factor corrects for this:

```
f1 = ( 1  +  (λ / (2.46 × (1 + 3.8μ*)))^(3/2) )^(1/3)

When λ is small: f1 ≈ 1.0  (no correction needed)
When λ is large: f1 > 1.0  (boosts Tc prediction)
```

### 2.3 Shape Correction Factor f2

`f2` accounts for the shape of the phonon spectrum (not just its average):

```
f2 = 1  +  (√2 - 1) × λ^2
              ─────────────────────────────────────────────────────
              λ^2  +  (1.82 × (1 + 6.3μ*) × (θ_2 / θ_log))^2

θ_2  = second moment of the phonon spectrum  (captures spectral width)
```

### 2.4 Clathrate Lattice Estimation

Hydrogen clathrate cages (e.g., H64M stoichiometry) have very light hydrogen atoms
that produce high-frequency phonon modes. The effective coupling estimate:

```
λ_eff  ≈  N(EF) × <I²>  /  (M_H × <ω²>)

N(EF)  = electronic density of states at the Fermi level
<I²>   = mean-square electron-phonon matrix element
M_H    = hydrogen atomic mass  (light → high ω → large λ_eff)
<ω²>   = mean-square phonon frequency
```

Higher hydrogen count N_H → softer cage phonons → larger λ_eff → higher Tc.

---

## 3. Workflow

```
Load candidate database (stoichiometry records with λ, μ*, θ_log)
        │
        ▼
Apply filters:  pressure range, structural stability criteria
        │
        ▼
For each candidate material:
    Compute f1  (strong-coupling correction)
    Compute f2  (spectral shape correction)
    Compute Tc  = (θ_log / 1.2) × exp(...) × f1 × f2
        │
        ▼
Is Tc > target threshold (e.g., 77 K, room-temperature)?
    Yes → add to high-Tc candidate list
    No  → discard
        │
        ▼
Sort candidates by Tc (highest first)
        │
        ▼
Render ASCII histogram + top-N ranking table
```

---

## 4. System Design

| Component | Module | Role |
|-----------|--------|------|
| **Data Layer** | `database.py` | Curated stoichiometry records with physical parameters |
| **Physics Engine** | `designer.py` | Allen-Dynes Tc calculation, clathrate evaluation |
| **Visualization** | `visualizer.py` | Terminal-based histogram plotting, ranking display |
| **Pipeline** | `run_search.py` | Orchestrates screening from raw database to final output |
| **Tests** | `test_materials.py` | Formula accuracy, database loading, filtering logic |

---

## 5. Key Advantages

| Advantage | Description |
|-----------|-------------|
| **Physics-grounded** | Implements Allen-Dynes equations exactly as in Phys. Rev. B 12, 905 (1975) |
| **Strong-coupling corrections** | Handles high-λ materials beyond McMillan validity range |
| **Modular database** | Easy to extend with new stoichiometry entries |
| **Zero ML black-box** | Fully interpretable physics equations — every parameter has physical meaning |
| **Fast screening** | Evaluates thousands of candidates in milliseconds |

---

## 6. Test Results

```
tests/test_materials.py::test_database_loading      PASSED
tests/test_materials.py::test_database_filtering    PASSED
tests/test_materials.py::test_allen_dynes_math      PASSED
tests/test_materials.py::test_clathrate_evaluation  PASSED
────────────────────────────────────────────────────
4 passed in 0.03s
```

---

## 7. Quick Start

```bash
pip install -e .
pytest tests/
python run_search.py
```

<div align="center">
  <a href="https://q.com"><img src="../../assets/https_q_com.png" width="80" /></a>
</div>
