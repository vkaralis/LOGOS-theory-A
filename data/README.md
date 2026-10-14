# Data provenance and license

`synthetic_restart_panel.csv` contains 144 independently generated toy episodes
from 48 fictitious subjects prefixed SYN-. Seed: 20261012. No source records,
source fitted coefficients, patient identifiers, or resampled real observations
are used. Each row includes `is_synthetic=True`. ANC is expressed in G/L, dose
in arbitrary illustrative mg/m² and gap/time in days; the toy equation and
ranges are software examples, not estimated pharmacological relationships.

`synthetic_metadata.json` records generation settings. Regenerate with
`logos-reproduce`, or from Python:

```python
from logos_recovery.synthetic import run
run('data')
```

`candidate_benchmarks.json` contains deterministic simulated normalized model
reference values and initial states. It contains no observations. Four candidate
identities are deliberately retained separately.

The repository MIT license applies to these data and simulation outputs.
