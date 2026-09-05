# Response to the five-role internal round

Date: 5 September 2026. All five roles recommended Accept with no required scientific revision. This response records the small post-review delta without changing or overwriting the frozen submission.

| Finding | Disposition |
|---|---|
| EIC-1, optional Minor provenance wording | Actioned in `NOVELTY.md`: replaced “independently reconstructed within this run” with “separately reconstructed within the producer-coordinated workflow.” |
| Applications A1, optional Minor scaling guidance | Actioned in `README.md`: explicit table size, O(n * 2^n * C) reconstruction arithmetic cost, exponential worst-case budget and amortized `Oracle` verification guidance. |
| Methodology optional exact-regression maintenance | Retained as a future maintenance suggestion. Existing exact in-code reconstruction/feasibility checks and the shipped tests remain unchanged; the review found no failing query. The report records its additional exact controls, but no separately shipped alternate implementation is claimed. |
| Domain optional display of the stronger divergence identity and smoothing | No manuscript change: the reviewer found these already implied by the written argument and did not require a repair. The report displays the identity and an explicit smoothing for readers. |
| Devil's Advocate | No required revision. Preserve the stated rational-input, feasible-not-optimal, model, quantifier and assurance boundaries. |

The final scientific payload is byte-identical to the frozen reviewed target except for the two nonmathematical documentation edits above. The publication package additionally contains these editorial records; execution receipts, build metadata and manifest may be regenerated. Exact per-file comparison and fresh extracted replay are separate release checks. No acceptance vote has been represented as external peer review, a novelty guarantee, or proof of a four-star result.
