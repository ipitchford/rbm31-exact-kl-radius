# Devil's Advocate: frozen RBM(3,1) submission

The strongest counterargument is that a finite collection of successful approximations cannot establish the claimed global radius for a nonconvex mixture model, and that even a valid upper bound would not establish that parity supplies the only maximizers. Different vertex witnesses cannot generally be averaged while retaining two product components; an inverse channel may also preserve divergence unless its equality condition is explicitly excluded. If either defect were present, the global theorem and the advertised constructive interface would fail despite a successful certificate replay. The frozen submission addresses both objections: each leaf uses one common feasible witness, and the last channel from a parity target strictly merges unequal likelihood ratios. I found no surviving instance of this counterargument in the manuscript or implementation.

## Target, scope, and review limitations

- Date: 5 September 2026.
- Frozen archive: `rbm31-stage1-review-frozen.zip`.
- Archive SHA-256, checked directly: `28b6d736b7bfd7bbabcb0892a3bb25fa873674362e6a90028b04829e71f923e1`.
- Reviewed extraction: `rbm31-exact-kl-radius (fresh extraction)`.
- Manuscript body SHA-256: `9226acdf9c56af217ea99fec60f082db9cb8b94ffc48ed8bcaa1562ca80db4a0`.
- `verify.py` SHA-256: `161b4affd17127e9a19d1a9d635cd11baa713bc182b881fae30f3ea4aeae8dbd`.
- `witness.py` SHA-256: `4c5c063dc0670ea53cef08076ff542fa8be16458fa4378fc48d2cd66884d7a51`.

Scope: semantic quantifiers, support boundaries, relaxation direction, exact arithmetic, equality cases, the constructive parameter transformations, and the higher-dimensional conditioning claim. I read the complete manuscript body, the exact verifier, the witness interface and its tests, and the relevant proof text. I did not read other reviewer reports or the submission's previous review-response document. I did not edit the submission. This report is the only file written by this review.

Confidence is high in the specific algebraic and semantic resolutions below, and moderate in overall correctness under this bounded review. This is producer-coordinated, model-mediated internal editorial scrutiny. It is not unaffiliated specialist review, independent reimplementation, formal verification, or an exhaustive novelty assessment. Running the supplied checker inside a diagnostic does not change that status.

## Adversarial findings and resolutions

1. **Finite tests versus the universal quantifier — resolved.** `PROOF.md` Sections 4.1–5, especially lines 229–253 and 313–321, prescribe complete initial simplices and both children of every midpoint split. `verify.py:294–336` reconstructs these vertices, rejects missing or unreachable nodes, and checks every vertex against the leaf's single witness. First-argument convexity of `D(p || q)` with that fixed witness covers all real weights. Neither convexity of the mixture model nor convexity of its minimum-divergence function is assumed. This is a genuine finite certificate for continuous coverage, conditional on the audited checker and analytic bridge.

2. **A necessary cone condition used in the wrong direction — resolved.** `PROOF.md:80–96` proves that the mixture model is included in the union of oriented supermodular cones. Minimizing over that larger set gives a lower bound on the model's minimum, which is the required direction. The positive explicit mixture supplies the matching upper bound at parity. The KKT sign in `verify.py:184–190` is consistent with the supporting-plane argument: for a normalized positive table in the standard cone,

   `D(u_E || q) - c = D(q* || q) + a sum_i L_i log(q) >= 0`.

   The equality and boundary argument can therefore be checked directly. A zero entry makes the first term diverge along an interior approximation because every entry of `q*` is positive; the second term remains nonnegative. The finitely many orientations allow a fixed-orientation subsequence if necessary. No sufficiency characterization at zero entries is needed.

3. **Support reduction losing valid targets or creating new maximizers — resolved.** The slice-inclusion hypothesis guarantees every ratio entering the minimum is positive and finite. The subtraction removes at least one positive cell, creates none, and preserves total mass. Empty-slice cases are handled before the ratio is taken (`witness.py:91–109`). For equality classification, strict convexity excludes nonvertex points, and the exact equality exception excludes every nonparity vertex. At the last reverse step from parity, each merged binary fiber contains one zero target probability and one positive target probability, while the comparison distribution is positive on both. Positive finite `tau` therefore makes the log-sum inequality strict (`PROOF.md:327–334`). Earlier channels cannot undo that strict upper bound. The argument does not claim a uniform positive gap away from the two maximizers.

4. **Floating arithmetic disguised as exact evidence — resolved.** `verify.py:37–83` rounds each nonnegative fixed-point operation outward and adds the stated series-tail bound. Negative range-reduction exponents reverse the interval endpoints correctly. The quadratic-field enclosure and the sign of the negative factor defining `c` are handled consistently at lines 139–147. Witness parameters are checked as integers over a positive integer denominator before the table is reconstructed. Positive target mass over a zero witness entry is rejected. The parity exception is an exact vector-and-parity identity, not a tolerance (`verify.py:250–291`). Display floats and the Decimal comparisons in interface tests are outside the proof decisions.

5. **A correct cover but an incorrect returned mixture — resolved in inspected code and targeted probes.** The barycentric branch convention in `witness.py:141–155` matches the checker's child convention. Reversal of the certificate's parameter order at line 164 correctly converts most-significant-bit order to the interface's least-significant-bit order. The inverse permutation and complement at lines 165–170 are consistent with the forward state map. For a Bernoulli parameter `t`, the recorded channel updates it to `t/(1+tau)` when source is 1 and `(tau+t)/(1+tau)` when source is 0, exactly as implemented at line 181. The interface supplies a feasible approximation; the manuscript explicitly declines general optimal-projection or RBM-training claims.

6. **Higher-dimensional model substitution or ignored zero contexts — resolved.** The conditioning proof in `PROOF.md:355–380` retains the context weights and appends deterministic coordinates to each local component. Zero-mass contexts are omitted. The KL identity is a weighted sum over disjoint contexts, and the component budget is `2^(n-m) k`; the implementation follows this at `witness.py:187–203`. Closed parameters permit the deterministic context bits. The corollary requires at least `2^(n-2)` product components and does not identify these models with general larger RBMs. It establishes neither sharpness beyond three bits nor a dimension-independent component budget. The text states those limitations explicitly.

## Targeted execution evidence

A separate in-memory diagnostic completed successfully after `Oracle()` verified the six frozen covers. It examined 296 targets:

- 48 channel images: both parity targets, all three axes, both channel directions, and `tau` in `{10^-30, 1/3, 1, 10^30}`. Every returned witness had strictly subconstant divergence at 150-digit Decimal precision.
- 56 point masses across three, four, and five bits. Returned distributions matched these targets exactly in the quadratic-field representation, exercising deterministic coordinates and omitted zero contexts.
- 192 cube-symmetry cases: all 48 permutations/complements applied to four targets, including parity, a uniform target, and two strongly unbalanced boundary-support targets with weight ratio `10^30`. All returned mixtures met the numerical bound diagnostic.

The diagnostic printed `PASS` with `adversarial_targets: 296` and exited successfully. Bytecode generation was disabled, and no query files were written. The high-precision KL comparisons are diagnostics, not exact inequality certificates or evidence for the all-real/all-dimensional quantifiers. Their value is in challenging channel direction, bit order, boundary handling, and symmetry reversal; the theorem still rests on the exact cover and analytic proof.

## Severity and recommendation

- **Critical:** none identified. No unresolved Critical finding prevents acceptance.
- **Major:** none identified within the stated scope.
- **Minor:** no required revision identified. Existing warnings about rational executable inputs, feasible rather than optimal witnesses, exponential component budget, and producer-side assurance are appropriately explicit.

**Recommendation: Accept**, within this role's scope, for publication as an unrefereed computer-assisted theorem candidate. This recommendation does not by itself clear the other editorial roles, package integrity, attribution, rendering, or release checks, and does not upgrade any external-validation assurance field.
