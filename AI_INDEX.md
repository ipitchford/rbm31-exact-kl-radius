# AI index — rbm31-exact-kl-radius

## Identity and version

Documentation addendum: 2026-09-24. Indexes [source commit ec82819b1349](https://github.com/ipitchford/rbm31-exact-kl-radius/tree/ec82819b13493d12430338b309d81f08d6a4db09) and candidate tag `v0.1.0-candidate`. This index was added after that release: it is **not** part of the original tag, DOI archive or frozen manifest. Existing release files and checksums remain unchanged. For historical manifest/allow-list checks, use a clean checkout of that tag, not this documentation-enriched branch. The addendum is authenticated by Git history.

[Release identity and DOI](README.md) · [Evidence Press context](https://evidencepress.org/releases/rbm31-exact-kl-radius/)

## Exact scope

The candidate gives the exact maximum forward-KL approximation error for RBM(3,1), equivalently a mixture of two three-bit Bernoulli products: −(3/4) log(2√3−3) nats. Only the two uniform parity targets attain it. The larger-bit constructive extension concerns product mixtures, not arbitrary larger RBMs.

The linked manuscript and claim register control all hypotheses and quantifiers; this index is a navigation aid, not a substitute proof.

## Claim and evidence map

- [PROOF.md](PROOF.md) — Exact statement, proof, equality cases and computational bridge.
- [CLAIMS.json](CLAIMS.json) — Claim register.
- [verification.json](verification.json) — Producer replay receipt.
- [NOVELTY.md](NOVELTY.md) — Prior art and attribution.
- [ENVIRONMENT.md](ENVIRONMENT.md) — Environment.
- [LICENSE.md](LICENSE.md) — Original prose and data terms.
- [LICENSE-CODE](LICENSE-CODE) — Code terms.

## Reproduce

From the indexed release root, after inspecting the commands and installing the documented environment:

```sh
python3 verify.py --out /tmp/rbm31-replay.json
python3 test_verify.py
python3 test_witness.py
```

Python 3.10+, standard library. Expected six cover PASS records and overall PASS, 13 verifier tests and five witness tests. These are recorded expectations, not a fresh replay performed for this index.

## Trust boundary and safe reuse

The constant predates this proposed proof. Search and checker separation inside the producer workflow is not unaffiliated validation. No peer review is asserted.

No new mathematical validation, formalisation, independent reproduction or novelty audit was performed for this documentation repair. Preserve the anonymous attribution and existing citation metadata. Distinguish producer checks, finite formal results, universal written arguments and external review. Before downstream reuse, match the exact statement and dependency scope and check subsequent corrections; a DOI or successful command alone is not proof of correctness.

## Licence and provenance

Use the rights/provenance sources linked above and [README](README.md); cited and third-party material retains its own terms. This new index is dedicated under CC0-1.0, without changing any existing licence or attribution.

