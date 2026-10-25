"""Compare McMillan vs Allen-Dynes over a λ sweep and solve one BCS chain.

Run: python examples/compare_formulas.py
"""

import numpy as np

from scdesign import KB_EV, Chain, allen_dynes_tc, mcmillan_tc, solve_gap, solve_tc

lam = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
for ratio in (1.0, 1.5):
    ad = allen_dynes_tc(1000.0, lam, 0.1, ratio)
    print(
        f"ω_log=1000 K, μ*=0.1, ω2/ω_log={ratio}: "
        + "  ".join(f"λ={x}:{t:.0f}K" for x, t in zip(lam, ad, strict=True))
    )
print(
    "McMillan:", "  ".join(f"λ={x}:{t:.0f}K" for x, t in zip(lam, mcmillan_tc(1000.0, lam, 0.1), strict=True))
)

chain = Chain(hopping_t=1.0, mu=0.0, coupling_g=1.0, n_k=20000)
d0, tc = solve_gap(chain), solve_tc(chain)
print(f"1-D chain g=1 eV: Δ0={d0:.5f} eV, T_c={tc:.2f} K, 2Δ0/kT_c={2 * d0 / (KB_EV * tc):.4f}")
