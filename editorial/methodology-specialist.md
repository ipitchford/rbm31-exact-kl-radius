# Stage 1 methodology-specialist report

Date: 5 September 2026.

Recommendation: **Accept**, with one optional Minor testing-maintenance suggestion below. No Critical or Major methodological issue was identified in this bounded review.

## Target and review boundary

Reviewed frozen archive: `rbm31-stage1-review-frozen.zip`.

SHA-256, independently read back with `shasum -a 256`: `28b6d736b7bfd7bbabcb0892a3bb25fa873674362e6a90028b04829e71f923e1`.

Reviewed extraction: `rbm31-exact-kl-radius (fresh extraction)`.

Scope: `verify.py`, `witness.py`, their tests, the analytic proof and proof-to-checker map in `PROOF.md`, and the methodological claims and boundaries in `README.md`, `CLAIMS.json`, and `ENVIRONMENT.md`. I did not read another role's report, edit the submission, assess publication priority, or independently inspect every PDF page. The coordinating agent reported successful complete normal and optimized replay and tests; those reports are distinguished from the additional checks I executed below.

Confidence: high in the inspected certificate-checking and reconstruction semantics; moderately high in the mathematical bridge within the time available. This is a model-mediated, producer-coordinated internal editorial review. Neither its separate role nor the targeted alternative calculations constitute unaffiliated specialist review, independent reimplementation of the full proof, or formal verification.

## Findings and strengths

1. **The lower-bound certificate has the correct mathematical direction.** `verify.py:159–191` checks the proposed mixture decomposition, normalization, positivity, nine necessary polynomial inequalities, three active faces, and the positive-multiplier identity in exact quadratic arithmetic. `PROOF.md` Section 2 separately supplies the necessary model-to-cone inclusion, the convex supporting-plane argument, orientation coverage, and the boundary passage. A feasible parity witness alone would not establish the lower bound; the package includes the additional argument needed to exclude better mixtures. The equality and boundary-uniqueness argument is consistent with the supporting-plane remainder.

2. **The continuous upper bound is not confused with finite target sampling.** The six support classes are exhaustively reconstructed from all 255 nonempty supports. The reverse-channel formula decreases support and preserves the required model by data processing. The ordered-weight root formula covers the special parity and five-point simplices, while exact midpoint subdivision preserves each root's coverage. `verify_cover` requires both children, unique reached addresses, and equality of reached and supplied node sets. Consequently, accepted leaves cover the full real-weight simplices. The fixed common witness on each leaf permits convexity in the target argument; it does not require a convex model or a generally optimal witness.

3. **The arithmetic bounds are sound on inspection.** `verify.py:37–83` rounds the positive log-series terms outward, uses the stated geometric-tail bound, and reverses endpoints for negative range-reduction exponents. The square-root enclosure and negative coefficient in the constant's enclosure have the appropriate directions. `vertex_slack` takes an upper divergence bound and compares it strictly with a lower constant bound. Zero target terms are omitted, and a zero witness beneath positive target mass is rejected. Floating conversion at the end of the cover receipt is display-only.

4. **Equality exceptions are narrow and analytically justified.** The exception requires an exact uniform parity vector and a validated star atom of matching parity. Every other checked vertex must have positive certified slack. Strict convexity handles other points within a leaf, and the strict log-sum condition excludes a maximizer obtained by a nontrivial reverse-channel step from parity. The manuscript correctly distinguishes the smallest finite vertex margin from a nonexistent uniform gap for all nonmaximizers.

5. **The constructive coordinate conventions agree.** Certificate mixture parameters are expanded most-significant-bit first in `verify.py:265–267`; `witness.py:164` reverses each parameter triple for its explicitly documented least-significant-bit convention. Its inverse cube transformation, root and split barycentric updates, and reverse application of recorded channels have the required direction. Exact runtime checks verify target-to-leaf reconstruction and component feasibility. Conditioning on high-bit blocks preserves context masses and realizes the stated component budget; the all-dimensional conclusion rests on the analytic disjoint-context identity, not the finite tests.

6. **Proof arithmetic and diagnostics are separated explicitly.** The acceptance path in `verify.py` uses integers, fractions, and exact quadratic signs; removable Python assertions are not its rejection mechanism. Decimal logarithms and tolerance comparisons occur in test diagnostics, with comments and manuscript disclosures identifying their limited role. The test suite contains meaningful corruptions of branches, node addresses, lower-bound data, witness support, parameters, and equality cases.

## Additional methods executed

All additional controls ran with `python3 -B` against the extraction and made no submission changes.

- Rebuilt 246 logarithm enclosures using a direct exact rational truncated series and an argument-specific rational tail, with separately written range reduction. Every such enclosure lay inside the verifier's returned fixed-point enclosure. This checks implementation agreement without treating a Decimal logarithm as proof.
- Expanded an asymmetric rational two-product witness directly in certificate coordinate order, then checked reconstruction under all 48 cube symmetries.
- Compared component-level and independently accumulated probability-table channel actions in exact `Q(sqrt(3))` arithmetic for 24 combinations: three coordinates, both channel directions, and four positive rational channel parameters from `1/10^9` to `10^9`.
- Confirmed rejection of 11 additional malformed witness or split controls, including Boolean values in integer-only fields, illegal star atoms, zero denominators, repeated endpoints, and out-of-range endpoints.
- Instantiated the shipped oracle, which performs its full exact certificate replay, and checked one asymmetric rational target on each of the 255 nonempty supports. Independently expanded its traced certificate witness, inverted the symmetry at the table level, applied each recorded channel as an explicit table pushforward, and compared the result exactly with the returned component distribution. All passed. This corpus included 193 rational-witness cases, 62 exact representations, 50 nonidentity permutations, 168 nonzero flips, and 212 channel steps on witness-bearing traces. It did not exercise star-witness queries; the separate quadratic channel checks and inspected shipped parity tests cover that distinct path to a more limited extent.

## Issues and remedies

**Critical:** None found.

**Major:** None found.

**Minor, optional — preserve exact constructive regression identities.** The shipped `test_witness.py:27–33` checks output divergence with a clearly labeled Decimal diagnostic, while exact in-code checks establish reconstruction and feasibility. The additional table-level tests above strengthen detection of parameter-order, inverse-symmetry, and channel-composition regressions without relying on a transcendental tolerance. Suggested remedy: retain a compact exact regression covering an asymmetric rational witness under all 48 symmetries, at least one star witness, both channel directions, and a context lift. This is a maintenance improvement, not evidence of a failed current query or a required scientific revision.

## Decision

The inspected semantics support publication of this exact frozen target with its existing **unrefereed computer-assisted theorem candidate** status. The finite certificate and analytic bridge are clearly identified, the constructive interface is correctly limited to feasible approximation, and no load-bearing error was found. Acceptance here does not upgrade any unaffiliated review, independent reproduction, independent reimplementation, formal verification, or novelty assurance field.
