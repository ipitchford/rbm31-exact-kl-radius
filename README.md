# AIM-PROBABILITY-0002: full-scope proof candidate

The claimed exact maximum forward-KL error of RBM(3,1), equivalently a mixture of two three-bit Bernoulli products, is

\[
-\tfrac34\log(2\sqrt3-3)=0.575738814443071397195567796635\ldots\text{ nats}.
\]

The only maximizing targets are the two uniform parity distributions.

Start with [paper.pdf](paper.pdf) or [PROOF.md](PROOF.md). The manuscript contains the analytic argument, finite computer-assisted lemma, proof-to-checker map, constructive interface and conditioning extension. [verification.json](verification.json) records producer replay of 52 roots, maximum depth 20, 16,600 covering simplices and 93,792 vertex conditions. This is an anonymous AI-assisted unrefereed theorem candidate, not a peer-reviewed result.

## Replay

Python 3.10 or later; no third-party packages are required for verification.

```sh
python3 verify.py --out replay.json
python3 test_verify.py
python3 test_witness.py
```

Expected: six cover `PASS` records, overall `PASS`, 13 verifier tests and five constructive-interface tests. A normal replay takes a few seconds on the development machine. The optional output `replay.json` is new local output and is not part of the frozen manifest.

The verifier checks exact model membership from mixture parameters, support-orbit completeness, complete recursive subdivision trees, the parity KKT identities, and rigorous logarithm bounds. It uses no search scores. Tests include false equality, deleted branches, unreachable nodes, illegal parameters, and a damaged lower-bound certificate.

## Contents

- `PROOF.md`: complete proof, including all equality cases and computer-assistance boundary.
- `verify.py`: standalone exact certificate checker.
- `test_verify.py`: adversarial and cross-implementation diagnostics.
- `certificates/*.json`: six exact convex-cover trees; no floating-point parameters or scores.
- `verification.json`: local exact-replay receipt with certificate hashes.
- `NOVELTY.md`: attribution, prior searches, exact target and the historical screening boundary.
- `scout.py`, `cover_scout.py`, `freeze_certificates.py`: optional discovery/rebuild code.
- `MANIFEST.sha256`: hashes of the shipped files other than itself.

To rerun discovery, install NumPy and SciPy in an isolated environment, then use `cover_scout.py` for each support, with output names `cover-two-scout.json`, `cover-three-scout.json`, `cover-four-scout.json`, `cover-parity-scout.json`, `cover-five-scout.json`, and `cover-six-scout.json`. Run `freeze_certificates.py`, then verify the resulting files. Discovery reproducibility is separate from replay of the frozen exact certificate.

## Assurance and attribution

The constant was already conjectured in Montúfar's 2018 review and attributed there to discussions with Johannes Rauh. That passage asks for maximizers but does not explicitly identify parity. The proposed proof does not claim priority for the expression. The checker was implemented separately from search in the same producer-coordinated workflow; this is not independent-person validation. Internal model review is not external specialist or journal peer review. See `REVIEW_RESPONSE.md` and `NOVELTY.md` for the exact attribution and assurance boundaries.

## Constructive use and bounded stretch

```sh
python3 witness.py 3/16 1/16 0 1/4 0 1/4 3/16 1/16 --out query.json
```

The returned exact two-product mixture has error at most the theorem constant. It is a certified feasible witness, not a generally optimal projection. Parameter arrays are least-significant-bit first. The interface verifies the entire certificate first.

For n bits it conditions on n-3 high bits and returns at most 2^(n-2) product components with the same error bound. The guarantee is about product mixtures, not arbitrary larger RBMs; sharpness beyond three bits is not claimed. The extension demonstrates a scoped infinite-family consequence, not a four-star rating or measured practical impact.

This implementation is intended for small explicit probability tables: its input has 2^n entries, and reconstructing the full output from C components costs O(n * 2^n * C) arithmetic operations, up to O(n * 4^n) at the stated component budget, before exact-arithmetic operand costs. Reuse one `Oracle` instance to amortize certificate verification across queries.
