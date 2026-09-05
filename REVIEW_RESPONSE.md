# Response to the supplied AIM-PROBABILITY-0002 review

Version 0.1.0-candidate, 5 September 2026. This is an original response matrix, not a reproduction of the review. The user clarified that the audit-ZIP link denotes the original bundle, not an additional supplied implementation. This successor does not claim to ship or personally replay a separate reviewer implementation. Reviewer-reported and producer-observed checks remain distinct.

| Item | Action and location | Closure evidence |
|---|---|---|
| R1, decimal displays | Corrected nats and bits in PROOF Section 1 and README; exact formula unchanged | High-precision Decimal diagnostic; certificate constants unchanged |
| R2, attribution | Attribute only the recorded constant to Montúfar Section 9 item 10; maximizers are a question there | Primary PDF, page 37, item 10 |
| R3, proof-to-code map | Added PROOF Section 9, separating executable obligations from analytic bridges | Seven-row obligation table |
| R4, independence label | Standalone/separately-implemented wording, explicit producer-coordinated provenance | verify.py docstring and PROOF Section 9 |
| R5, bibliography and prior art | Boundary decomposition, Alexandr–Hoşten Proposition 2, disjoint-support mixture comparison | PROOF Sources and NOVELTY revision-date audit |
| R6, tree statistics | Verifier reconstructs root and depth counts | 52 roots; maximum depth 20 in verification.json |
| S1, executable use | witness.py, exact channel/symmetry/leaf trace, worked example | test_witness.py; examples/channel-witness.json |
| S2, broader transfer | R(n,2^(n-m)k)<=R(m,k), hence R(n,2^(n-2))<=c | Complete proof in PROOF Section 7.2; 50 four-/five-bit implementation diagnostics |
| S3, four-star goal | Assessed, not claimed achieved | NOVELTY: classical transfer, no higher-dimensional sharpness, external assessment or impact |

The six original certificate files retain identical bytes. The original reviewed ZIP is preserved unchanged with SHA-256 `c9031bc194d6e165f563e3a67bd3658c7b419667b44d3e21233eb81ae5b19e66`. The successor does not overwrite that archive.

Producer diagnostics initially found a precision-context error in the new Decimal equality test. The context was corrected; the issue did not affect the exact verifier, certificate data or mathematical constant. Diagnostic tolerances are expressly excluded from proof decisions.

The supplied review is not treated as authenticated external specialist review, independent-person reconstruction, formal verification or journal peer review. Internal editorial reports are separately recorded at their frozen target hashes.
