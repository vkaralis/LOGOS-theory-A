# Numerical validation

The release is executed in a new Python 3.12 virtual environment with individually
installed pinned dependencies and no inherited site packages. Local execution is
on macOS arm64. Linux execution is configured in CI but has not been run locally.
`reference_results/environment.json` records the actual Python and numerical
library versions; README commands and requirements-lock.txt reproduce the setup.

Seven unittest checks cover fixed candidate initial states and DOP853/Radau
agreement, the concavity null, finite exact-dose mass balance and tail, matched
palbociclib amount and ANC nadirs, constrained reduced restart (including
infeasibility and zero rebound), deterministic synthetic generation and versions.
`python scripts/verify_outputs.py results` checks the complete release outputs.

Selected fixed-model anchors:

| Calculation | Result |
|---|---:|
| A-PER-REFINED J | 0.080905389814 |
| A-PER-REFINED peak injury | 0.188070550584 |
| Constant input one J | -0.032715501025 |
| Stationary constant-family upper bound | 0.073717155071 |
| Finite equal-dose cycle J | 0.0552361206 |
| Finite constant-family upper bound | approximately 0.050307 |
| Fixed feasible / fixed feasible strict cases | 25 / 22 of 32 |
| Grid selected feasible / selected strict cases | 29 / 24 of 32 |
| Principal-cap phase gain / retained cells | 425 / 15 |
| Tight-cap phase restoration / no safe sampled cells | 242 / 198 |
| Principal / tight nonpositive overlays | 200 / 101 |

Fresh local optimizer outputs can change in their last digits across platforms;
check frozen candidates and endpoints using stated tolerances. Midpoint refinement
errors are regenerated against the current independent affine-map integration,
so they reflect that implementation's initialization accuracy. Approximate
screening classifications remain separate from continuously checked witnesses.

The original source computations have been separated from real-data processing.
Synthetic subject-held-out predictions cannot confirm observed-data associations,
causal recovery benefit or a clinical policy. No external reviewer reproduction,
GitHub CI result, DOI or clinical validation is claimed.
