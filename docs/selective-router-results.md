# LocRAG’s selective fallback on 480 held-out sources

Does the shipped routing rule recover established Spanish wording below a 75% fuzzy cutoff, and what does it cost in accuracy? We applied the production routing code to the fixed EMEA and KDE4 English→Spanish panel. GPT-6.2 Astra translated every arm with the same product prompt. Only the supplied TM examples varied. GPT-6.2 Sol graded anonymous candidates against the previously frozen convention for consistency and, in a separate call, against the source for accuracy.

## Primary result

Of the 160 below-cutoff sources, the router gave Astra one semantic example on 39, two on 12, and three on 31. On the remaining 78 it abstained. Each abstention had exactly the same prompt and translation as the no-memory arm. A separate convention supported by two historical entries was available for 152 sources. No convention citation appeared among the router’s supplied examples on those sources.

| Below 75% fuzzy | No memory | Unthresholded fuzzy top three | Selective LocRAG |
|---|---:|---:|---:|
| Followed documented wording | 113/152 (74.3%) | 123/152 (80.9%) | 118/152 (77.6%) |
| Passed source-accuracy check | 158/160 (98.8%) | 149/160 (93.1%) | 154/160 (96.3%) |

Versus no memory, selective LocRAG fixed eight terminology inconsistencies and introduced three. Both versions passed accuracy on all eleven changes. The net consistency gain was **3.3 percentage points [95% interval −0.7, +7.7]**. Separately, the accuracy judge flagged four new meaning errors and found zero repairs, a difference of **−2.5 points [−5.0, −0.6]**.

Versus unthresholded fuzzy retrieval, LocRAG had five fewer consistency passes (**−3.3 points [−8.4, +1.4]**) and five more accuracy passes (**+3.1 points [−1.2, +7.5]**). Neither paired interval establishes a clear advantage over fuzzy retrieval. The eight terminology fixes show that the fallback can help on individual segments; the policy also carries risks.

## What abstention changed

On the 82 sources where the semantic gate opened, 78 had an independently documented convention. Consistency passes were **53/78 without memory, 60/78 with fuzzy, and 58/78 with LocRAG**. Accuracy passes were **82/82, 78/82, and 78/82**, respectively. On the 78 sources where the router abstained, it passed accuracy on 76, compared with 71 for fuzzy. The five-pass net accuracy difference between the two policies came from the abstention group. This is a description of sources selected by the gate; it does not estimate the effect of filtering semantic hits versus always supplying them.

## Results across the full sampling range

Each cell gives the number of passes. Each band contains 80 sources for accuracy. The eligible column gives the consistency denominator.

| Fuzzy band | Eligible | Consistency · none / fuzzy / LocRAG | Accuracy · none / fuzzy / LocRAG |
|---|---:|---:|---:|
| <50 | 77 | 63 / 65 / 64 | 79 / 77 / 78 |
| 50–74 | 75 | 50 / 58 / 54 | 79 / 72 / 76 |
| 75–84 | 76 | 50 / 63 / 63 | 78 / 76 / 75 |
| 85–94 | 74 | 51 / 60 / 60 | 78 / 75 / 72 |
| 95–99 | 79 | 57 / 67 / 66 | 80 / 74 / 72 |
| 100 | 70 | 55 / 61 / 61 | 79 / 70 / 68 |

The router used fuzzy examples on all 320 sources at or above 75. Its production fuzzy retriever uses a character shortlist and filters individual examples at the cutoff. The unthresholded baseline uses the archived exhaustive word-level top three. Eleven above-cutoff sources received a router example also cited by the convention assessor. Excluding those sources from the full panel leaves the router’s consistency difference versus fuzzy at −1.4 points [−3.4, +0.7]. The balanced band counts are a study design choice and do not estimate live traffic frequencies.

## Two cases

- **Terminology recovered, E454684e46b6e:es.** For “Starter pack,” Astra used *Envase de inicio* without memory and with unthresholded fuzzy matches. Only one semantic hit cleared the floor. With it, Astra used the documented *Envase de iniciación*. All three outputs passed the independent accuracy check.
- **Context introduced unsupported meaning, Ee93d0a57f8cc:es.** The English fragment ends midphrase with “chronic urinary tract.” The router output supplied *infecciones* (“infections”), completing the thought with a diagnosis absent from the source. The judge accepted the no-memory output and flagged the addition. Incomplete source text and ambiguous UI strings also make some automated accuracy decisions debatable.

## Audit and limits

We executed TMRouter.route with its production fuzzy retriever. For semantic queries the code replayed the original BGE-M3 top hits on the same TM snapshot; no new embeddings were bought. The two bilingual TMs matched the historical file hashes, and no replayed top-three score was ambiguous due to rounding at 0.80. The frozen route manifest contains all examples and exact messages. The offline summary verifies every prompt against the logged examples and every translation against its request hash.

Intervals are paired, pointwise bootstrap intervals from 10,000 resamples within domain and original band. The study covers two corpora and one target language. The evaluator is an OpenAI model, and no human post-editing time was measured. Order-reversal checks agreed on 77/78 accuracy grades and 72/72 consistency grades. This run added 2,224 completed direct OpenAI calls, estimated at **$4.87** at uncached rates. Identical requests shared completions, including cached prior judgments. [Frozen protocol and reproduction](../experiments/selective-router/protocol.md) · [Examples and exact prompts](../experiments/selective-router/panel.jsonl) · [Translations and judge evidence](../results/selective-router/outputs.jsonl) · [Numerical results](../results/selective-router/summary.json)
