## Per system (n=72 rows each)

| system | mean score | mean MQM pts (lower better) | rows with major+ error | rows with critical error |
|---|---:|---:|---:|---:|
| tm_as_is | 37.2 | 6.85 | 59 | 31 |
| hybrid_ctx | 96.9 | 0.22 | 1 | 0 |
| zero_shot | 96.8 | 0.18 | 0 | 0 |
| nmt_deepl | 93.7 | 0.56 | 2 | 1 |

## Mean judge score by band

| band | n | tm_as_is | hybrid_ctx | zero_shot | nmt_deepl | hybrid − TM [95% CI] | hybrid W/T/L vs TM |
|---|---:|---:|---:|---:|---:|---:|---:|
| 100 | 12 | 78.1 | 94.2 | 97.2 | 94.2 | +16.1 [+1.3, +35.2] | 4/8/0 |
| 95-99 | 12 | 42.3 | 99.0 | 97.3 | 94.2 | +56.7 [+38.2, +73.8] | 12/0/0 |
| 85-94 | 12 | 22.7 | 98.7 | 97.4 | 88.0 | +76.0 [+60.8, +87.8] | 12/0/0 |
| 75-84 | 12 | 33.3 | 97.6 | 97.5 | 96.2 | +64.2 [+50.0, +77.8] | 12/0/0 |
| 50-74 | 12 | 42.1 | 94.8 | 96.4 | 94.2 | +52.8 [+41.8, +65.3] | 12/0/0 |
| <50 | 12 | 4.6 | 97.2 | 94.7 | 95.2 | +92.6 [+82.7, +98.2] | 12/0/0 |
| all | 72 | 37.2 | 96.9 | 96.8 | 93.7 | +59.7 [+51.8, +67.7] | 64/8/0 |

## Pairwise vs hybrid_ctx (judge score), all bands

- hybrid − tm_as_is: +59.7 [+51.8, +67.7]; W/T/L 64/8/0
- hybrid − zero_shot: +0.2 [-1.4, +1.4]; W/T/L 41/14/17
- hybrid − nmt_deepl: +3.2 [+0.4, +6.8]; W/T/L 44/14/14

## Agreement of metrics with the judge (Spearman over row×system)

- kiwi: rho=0.53 (n=288)
- comet: rho=0.47 (n=288)
- chrf: rho=0.36 (n=288)

## Do metrics flag the outputs the judge found major/critical errors in?

**all systems**

| metric | AUC: clean > major/critical | flagged errors that score above the clean median |
|---|---:|---:|
| kiwi | 0.92 | 2/62 |
| comet | 0.72 | 15/62 |
| chrf | 0.59 | 26/62 |

**generated only (hybrid, zero-shot, DeepL)**

| metric | AUC: clean > major/critical | flagged errors that score above the clean median |
|---|---:|---:|
| kiwi | 0.68 | 0/3 |
| comet | 0.90 | 0/3 |
| chrf | 0.82 | 0/3 |

## Major/critical errors in generated outputs, with metric scores

- E467660b72381:es hybrid_ctx band 100: Kiwi 0.848, COMET 0.733, chrF 62 | major: 'no debe' = must not; source says it is not necessary
- K02022f544e6a:zh_CN nmt_deepl band 100: Kiwi 0.845, COMET 0.792, chrF 13 | major: 钥匙扣 (key fob) for keyring database
- K13d0f2203fe4:de nmt_deepl band 85-94: Kiwi 0.818, COMET 0.655, chrF 46 | critical: watches as wristwatches
