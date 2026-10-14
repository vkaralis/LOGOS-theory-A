# Mathematical definitions

## Normalized exposure-gated model

Time is in recovery units. Input `u` is concentration-equivalent administration,
not a physical mass rate. For common bioavailability F, clearance CL and efficacy
scale KE, `u = F Uadm / (CL KE)`.

```text
C' = κ(u − C)
R' = r W(C)(1 − R) − α E(C) R
Z' = β E(C) − π WZ(C) Z
(log D)' = ρ(1 − E(C)) − η E(C) R
E(C) = C/(1+C)
W(C) = 1/[1+(C/χ)^n]
WZ(C) = 1/[1+(C/χZ)^2]
J = η <ER> − ρ <1−E>
```

| Parameter | Value | Meaning |
|---|---:|---|
| κ | 4 | Washout relative to restoration |
| α | 2 | Exposure-dependent responsiveness depletion |
| π | 0.7 | Injury repair |
| β | 0.2 | Injury formation |
| η | 1 | Responsiveness-dependent benefit |
| ρ | 0.08 | Disease rebound |
| χ | 0.35 | Restoration gate threshold |
| χZ | 1 | Repair gate threshold |
| n | 4 | Restoration gate exponent |
| r | 1 | Restoration multiplier |

The multiplier `r` in parameter perturbations is distinct from the dimensional
recovery rate used to define time and the rate in the reduced decision model.
The alternate restoration gate is `exp[-ln(2)(C/χ)^a]`, `a=n/[2ln(2)]`.
An optional first-order absorption layer uses `A'=12(u−A)`, `C'=κ(A−C)`.

A rectangle has period T, duty f, input 1/f on `[0,fT)` and zero on `[fT,T)`.
The mean input is exactly one. Analytic PK and affine one-cycle maps give each
regimen's own periodic states. Disease need not be periodic. Periodic mean C is
reported using the exact mass-balance identity, rather than sampled quadrature.

The primary grid is 45 geometric periods in [0.2,30] times 31 duties in [0.2,0.95].
The injury caps are 0.5 and 0.22. Screening uses 256 midpoint cells per segment;
selected candidates use split DOP853 integration with rtol 2e-11, atol 2e-13 and
step at most T/150. Endpoints, switches and derivative roots bracketed on 1,500
intervals per segment determine numerical peak injury. Radau checks use rtol 2e-12.
The bounded L-BFGS-B rerun is reported separately from the four frozen candidates.

## Null models

With R=1 and fixed mean exposure q, concavity of E gives
`J <= (η+ρ)E(q) − ρ`. For the separate linear recovery model
`R'=r(1−R)−aCR`, periodic positivity and mean C=q imply
`<CR> <= qr/(r+aq)`. The second result applies to a linear endpoint and does not
replace the canonical nonlinear model. A deterministic feedback trajectory adds
no information value when the common open-loop action class can reproduce it.

## Reduced conditional restart

```text
R(w) = 1 − (1−R0) exp(−rw)
Z(w) = Z0 exp(−pw)
D(w) = D0 exp(gw)
V(w) = B(1−R0)(1−exp(−rw)) − L D0(exp(gw)−1)
w* = log[B r(1−R0)/(L g D0)]/(r+g)
V'(w) = B r(1−R0)exp(−rw) − L g D0 exp(gw)
```

For strictly positive rates and costs, waiting has a positive unconstrained
window iff `B r(1−R0)>L g D0`. Otherwise immediate restart maximizes V.
Safety delay is `max(0,log(Z0/Zsafe)/p)` (zero for Z0=0); disease and horizon limits
bound the latest allowed wait. Project the optimum onto a nonempty feasible
interval. A forced safety delay can have negative V. This is a separate reduced
utility, not the value function of the full ODE.

Defaults: B=1, R0=0.2, L=0.15, D0=1, g=0.4; rates {0.5,1,2} have equal weights.
Ideal information and a single calendar wait share a fixed subsequent challenge.
Noisy information uses `Y=log(r)+Normal(0,σ²)` and waits in [0,6], with σ in
{0,0.25,0.5,1,2}. Posterior-optimal waits are integrated with 80 and 160
Gauss–Hermite nodes. Optional monitoring value is `max(0,information gain−cost)`.

## Finite comparisons and numerical bounds

Common initial state is C=0,R=1,Z=0,D=1. Administration stops at H=20;
outcomes are evaluated at 25. Exact-dose comparison: constant input one versus
12 cycles of T=20/12,f=0.2, both totaling 20. `JF=−log[D(25)/D(0)]/25`.
Residual exposure is `C(25)/κ`; integrated exposure equals
`amount−[C(25)−C(0)]/κ`. Injury is checked during treatment and follow-up.

The common-cap stationary comparison optimizes every constant input in [0,1]
under injury cap 0.22, against a fixed cycle. Realized amounts may differ.
A million-interval grid plus half-mesh times a derivative bound encloses
inter-grid variation. The finite constant-family comparison uses 4,096 intervals,
derivative bound 27.937143 and 1e-7 integration allowance; its upper bound relaxes
injury safety, hence covers safe constants too. These are conservative numerical
bounds with declared assumptions, not validated interval enclosures.

The stress test uses 32 unscrambled Sobol vectors over nine parameters ±20%,
and 63 screened rectangles. Contrary results and cases without a safe selected
rectangle remain reported; these are not population probabilities.

## Published-parameter safety illustration

The palbociclib model uses gut and central PK amounts in mg and five ANC pools
in G/L: proliferation, three transit pools and circulation. With time in days,
ka=0.187×24, elimination=57.09/1580×24, lag=0.658/24,
ktr=4/5.29, baseline=2.92, slope=0.0011 L/µg and feedback exponent=0.102.
Concentration is `1000 Central/1580` µg/L.

```text
Gut' = −ka Gut
Central' = ka Gut − kel Central
Prol' = ktr Prol[(1−slope C)(baseline/ANC)^gamma − 1]
T1' = ktr(Prol−T1)
T2' = ktr(T1−T2)
T3' = ktr(T2−T3)
ANC' = ktr(T3−ANC)
```

Doses enter the gut after the lag. Compare 125 mg on days 0–20 in each 28-day
cycle to hypothetical 93.75 mg daily over 168 days; both total 15,750 mg.
RK45 is split at dose events, rtol 2e-9, atol 1e-11, step at most 0.05 day.
Dense-output minimization finds interval nadirs; an independent solver repeats
this calculation. All PD pools start at baseline. Apparent PK parameters require
no extra bioavailability factor. No tumor response is modeled.
