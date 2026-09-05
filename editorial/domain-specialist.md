# Stage-1 domain-specialist report

Review date: 5 September 2026. Role: algebraic statistics and information geometry. Recommendation: **Accept** within the declared unrefereed-candidate boundary. This is one internal editorial role recommendation, not the overall Stage-1 decision.

## Frozen target and review limits

- Archive: `rbm31-stage1-review-frozen.zip`.
- Archive SHA-256, checked during this review: `28b6d736b7bfd7bbabcb0892a3bb25fa873674362e6a90028b04829e71f923e1`.
- Reviewed extraction: `rbm31-exact-kl-radius (fresh extraction)`.
- `PROOF.md` SHA-256: `99eeeb6b9a93d338cd979520540b26a41ad6cdc85f5c84aa74dc9d478d2c288a`. The extracted manuscript hash matches the manuscript streamed directly from the frozen ZIP.
- `NOVELTY.md` SHA-256: `75a502c316e6e32aaec242b0b195cca4f9ab808f9d8f34280d3d72a3f9ac5c14`.
- `verify.py` SHA-256: `161b4affd17127e9a19d1a9d635cd11baa713bc182b881fae30f3ea4aeae8dbd`.

I read the manuscript and novelty note, checked the load-bearing analytic arguments, inspected the corresponding checker routines, and consulted the three primary antecedents discussed below. I did not read another role report or edit the submission. This report is the only file created by this review. I did not conduct a complete independent reconstruction of all certificate data, rerun the publication baseline, audit every executable-interface branch, or assess the rendered PDF.

Confidence is high in the analytic bridges examined, moderate in overall computer-assisted theorem correctness because the full finite certificate retains its declared checker and execution trust base, and limited on novelty and priority. This model-mediated review is producer-coordinated internal editorial scrutiny. It supplies no unaffiliated specialist review, independent-person reproduction, independent reimplementation, formal verification, or external journal acceptance. No personal domain credentials or external independence are asserted.

## Findings on the mathematical argument

### Model and lower bound

The definition in `PROOF.md:9–24` correctly uses the compact closure of the two-product mixture model. The distinction between a minimum over that closure and an infimum over finite RBM parameters matters here: the displayed optimum has a deterministic mixture component even though its probability table has full support. The manuscript preserves this distinction.

The necessary inclusion in the four oriented log-supermodular cones is sufficient for the lower-bound argument (`PROOF.md:70–96`). After coordinate complements make the component Bernoulli parameters ordered, their log-odds differences are nonnegative. Factoring one component gives a modular term plus a convex soft-plus term. For an arbitrary incomparable pair, the increments over the two disjoint coordinate differences are nonnegative, so the displayed integral proves the required inequality. Global complementation interchanges meet and join and leaves the cone unchanged. The four even complements therefore cover the four orientation classes while preserving the even-parity target. No sufficiency assertion for these inequalities is needed.

The KKT signs and orientation are correct (`PROOF.md:98–140`). The multiplier is positive, the three chosen rows are active, and the residual vector is exactly their positive sum. For a normalized positive table in the specified cone, the argument can be reconstructed as the stronger identity

\[
D(u_E\Vert q)-c
=D(q^*\Vert q)+a\sum_{i=1}^3 L_i\log q.
\]

Both terms on the right are nonnegative. This proves the bound and uniqueness within that cone without assuming convexity of the mixture model itself. Even translations give four distinct minimizing distributions for the even target, and odd translations give the four for the odd target.

The simplex-boundary extension is sound. An explicit way to keep a fixed orientation is to replace every Bernoulli parameter \(r\) and the mixing weight by \(\varepsilon+(1-2\varepsilon)r\); the coordinate order is preserved. Divergence to the fixed target converges term by term in the extended sense. If a limiting table has a zero entry, the first term on the right of the identity diverges because \(q^*>0\). Hence such a table cannot attain equality. This is about zero entries of the probability table; it does not incorrectly exclude full-support points on the boundary of the mixture model. The relevant exact identities are also represented faithfully by `verify.py:159–191`.

### Global reduction and equality cases

The reverse-channel construction (`PROOF.md:163–189`) has the necessary three properties: it preserves total mass and nonnegativity, creates no new support, and removes at least one positive entry. The minimum ratio is strictly positive under the stated inclusion of two nonempty slice supports. The displayed channel reconstructs the original table exactly. A local stochastic channel maps each product distribution to a product distribution, so the direction of the model-distance inequality is correct. A deterministic coordinate leaves a two-bit table, which indeed admits a two-product decomposition by conditioning one remaining bit.

The support test and group action match the intended combinatorics (`PROOF.md:191–212`; `verify.py:194–218`). The test compares slices after deleting the distinguished bit, not the unprojected slices. The explicit ordered-weight roots and midpoint subdivision argument cover continuous simplices (`PROOF.md:227–253`). Combined with a common feasible witness on each leaf, first-argument convexity gives the universal inequality without requiring the witness to be optimal throughout that leaf. Inspection of `verify.py:229–290` found this distinction preserved in the checker, including exact recognition of the parity exceptions.

The strictness argument closes both potential sources of extra maximizers (`PROOF.md:323–336`). A nonvertex point represented using at least two distinct leaf vertices has strict first-argument convexity on the common witness's finite-divergence face. If a support reduction occurred and the terminal distribution is parity, the last forward channel genuinely merges two inputs in an output fiber. Both have positive reference mass, whereas their target/reference likelihood ratios are zero and positive, respectively. Equality in log-sum is therefore impossible. Applying earlier channels cannot undo the strict bound. I found no hidden full-support assumption on the target in either step.

### Dimensional transfer

The proof of `PROOF.md:353–380` establishes the stated all-dimensional inequality for closed mixtures of products. Each conditional approximation contributes at most \(k\) product components; adjoining deterministic context bits gives at most \(2^{n-m}k\) components. Matching context masses gives the displayed exact KL decomposition, and zero-mass contexts can be omitted. The compactness argument underlying conditional minimizers is the same finite-dimensional one used initially. The corollary follows with \(m=3,k=2\), followed by monotonicity in the allowed number of components.

The stated comparison with a one-bit upper bound is correct: approximating each remaining two-bit conditional by its marginals costs its mutual information, at most \(\log 2\). The improvement is a quantitative consequence of the three-bit result. The manuscript appropriately leaves higher-dimensional sharpness and general multi-hidden-unit RBM consequences open. Finite executable tests are not used as the proof of the all-dimensional quantifier.

## Primary-source comparison and significance boundary

I checked the relevant passages directly during this review:

- [Montúfar, *Restricted Boltzmann Machines: Introduction and Review*, Section 9, item 10](https://arxiv.org/html/1806.07066#S9) records the proposed RBM(3,1) constant with an explicit base-two logarithm and attributes its suggestion to discussions with Johannes Rauh. It asks for divergence maximizers but does not name the parity distributions there. The manuscript's conversion to nats and its restraint about parity attribution are appropriate (`NOVELTY.md:9`; `PROOF.md:390`).
- [Alexandr and Hoşten, *Maximum information divergence from linear and toric models*, Proposition 2](https://arxiv.org/html/2308.15598) uses strict first-argument convexity on logarithmic Voronoi polytopes, where the reference point is an optimizer. The candidate instead constructs prescribed simplices with common feasible witnesses. The comparison in `NOVELTY.md:46` and `PROOF.md:394` correctly attributes the general convexity principle and identifies the narrower difference in the proof object.
- [Montúfar, Rauh and Ay, *Maximal Information Divergence from Statistical Models Defined by Neural Networks*, Lemma 6, PDF page 6](https://arxiv.org/pdf/1303.0268) gives the disjoint-support projection decomposition. Its Theorem 1 also supplies the established one-bit upper bound at the power-of-two component budget under discussion. The conditioning mechanism is therefore classical, as acknowledged in `NOVELTY.md:47` and `PROOF.md:371–380`.

The candidate's proposed contribution is a specific global proof architecture and exact certificate for this model, together with its equality classification. That is a coherent disciplinary contribution to assess. These three comparisons do not establish that no earlier, recent, or unpublished proof exists. The bounded-search qualification in `NOVELTY.md:30,42,48` must remain. The constructive interface and conditioning consequence demonstrate scoped reuse; this review supplies no evidence for a four-star impact assessment.

## Severity, revisions, and recommendation

- **Critical:** none identified within this review's scope.
- **Major:** none identified within this review's scope.
- **Minor requiring repair:** none identified.
- **Required revisions:** none from this role.

An optional expository addition at `PROOF.md:140` would display the divergence identity above and name the order-preserving smoothing. That would make the uniqueness and zero-entry argument easier to check in isolation. It is not a missing mathematical step requiring a hold, since both facts follow directly from the written supporting-plane argument and parameter approximation.

I recommend **Accept** for this domain-review component of the internal editorial gate, preserving the existing unrefereed-candidate, computer-assistance, novelty, and independence limitations. This recommendation does not replace the other role reports or the deterministic publication gates.
