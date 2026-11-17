# Completed evaluation: plain-language results

The system finds reusable-looking past translations that ordinary matching misses. Using those examples helps in some cases, especially with consistent wording, but does not reliably improve accuracy across every language.

## New language tests

We translated the same 300 English software-localization sentences into Spanish, German and Simplified Chinese: 900 language-specific test cases, each under four conditions. No language was skipped.

This table isolates the added value of semantic fallback over ordinary fuzzy matching. Identical outputs count as ties; below the fuzzy threshold the ordinary system is exactly the zero-shot baseline already judged. No new or invented judgments are needed for this comparison.

| Target language | Better | Worse | Tie | New meaning errors | Meaning errors fixed |
|---|---:|---:|---:|---:|---:|
| Spanish | 14 | 8 | 278 | 3 | 1 |
| German | 20 | 3 | 277 | 1 | 2 |
| Simplified Chinese | 8 | 6 | 286 | 2 | 5 |

The system used semantic fallback on 43/300 sources. Ordinary matching handled 22; 235 received no memory examples. Most ties therefore reflect deliberate non-use of memory, not a failed translation attempt.

German showed the clearest added benefit in this sample. Spanish and Chinese were mixed; these results do not establish a general accuracy improvement. Judgments prioritize meaning, then reuse of appropriate terminology/phrasing.

## Full system versus translating without any memory

This includes benefits from ordinary fuzzy matches as well as semantic fallback. It must not be described as the isolated contribution of semantic search.

| Target language | Better | Worse | Tie | Character-only chrF: no memory → router |
|---|---:|---:|---:|---:|
| Spanish | 22 | 11 | 267 | 68.61 → 69.46 |
| German | 28 | 6 | 266 | 58.77 → 60.16 |
| Simplified Chinese | 19 | 8 | 273 | 42.22 → 44.14 |

Always supplying semantic examples produced more preferred outputs, but also more newly introduced meaning errors: 17 Spanish, 15 German and 29 Chinese. That more aggressive policy is not a free improvement. All four conditions are in the [full summary](../../multilingual/validation-v1/summary.json).

## Original Spanish medical-text experiments, rerun

On the 300 real below-threshold cases, the corrected router received **50 wins, 9 losses and 241 ties** under the localization rubric. It introduced two accuracy errors and fixed one. The generic rubric, which does not reward memory consistency, preferred it 25 times and preferred the baseline 32 times, with 243 ties.

On the separate 200-case comparison, reusing memory strongly improved reference similarity over no-memory translation. Semantic retrieval did not beat ordinary thresholded fuzzy matching overall. The prior post-hoc tiered policy's apparent edge was not statistically convincing in this rerun.

The constructed rewording tests expose a real failure mode: the localization judge rated 79/80 baseline outputs accurate, versus 71/80 with retrieved examples. The 40 forced opposite-meaning stress cases had 39/40 accuracy ratings in both conditions under that rubric; this is not a dedicated human-verified polarity-safety result.

The three embedding models again recovered the original/accepted near-duplicate first on 95–97.5% of paraphrases and 100% of restructures. Good retrieval does not guarantee a good translation.

## What can be claimed

LocRAG is a tested translation-memory assistant that can recover overlooked examples and improve consistency. Its benefit depends on the language and content, and it sometimes introduces meaning errors. General translation-accuracy improvement is unproven.

## Checks and limitations

- All planned automated runs completed. No empty translations or failed judgments were found.
- The 200-case comparison deduplicates identical prompts. The first run exposed concurrent cache misses generating different outputs for equivalent no-context conditions; `emea-mt-deduplicated` is the corrected result and supersedes `emea-mt`.
- The multilingual experiment and corrected router reuse their baseline output when context is absent; these invariants were checked on every result.
- The judge is Claude Sonnet 5.5, not a human review panel. A/B order is randomized; judge noise, reference quality and rubric preferences remain limitations.
- Software data are new held-out inputs; the medical runs reproduce previously studied inputs and do not constitute fresh independent medical validation.
- English retrieval inputs are shared across target languages; this does not test German- or Chinese-source retrieval.
- Exploratory sign tests and segment-bootstrap intervals are in `final_summary.json`; they are unadjusted for multiple comparisons and do not account for document dependence or judge error.
- Medical scores use chrF++; the multilingual primary metric is character-only chrF. Absolute scores should not be pooled across these studies or used to rank languages.

Rebuild this report without model calls: `uv run python scripts/summarize_run.py`. Input hashes are in `final_summary.json`. Raw [multilingual outputs](../../multilingual/validation-v1/rows.jsonl), [medical router outputs](emea-router/rows.jsonl), [medical comparison](emea-mt-deduplicated/rag_mt_summary.md), and [retrieval probes](emea-retrieval/probes_summary.md) remain available.
