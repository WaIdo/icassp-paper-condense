# Venue measurements: what accepted ICASSP papers actually do

Every number here was measured with `scripts/corpus_baseline.py` and
`scripts/measure_layout.py` on seven accepted ICASSP 2026 papers (arXiv
2603.01640v2, 2603.19757v1, 2603.27533v1, 2603.29291v1, 2604.03002v1,
2604.17062v1, 2606.11783v1), all on the spconf template. Re-measure with your
own corpus when you have one; the point of this file is the *method* as much as
the values. Use these as evidence when deciding whether a deviation is a
problem, and as the target when deciding how far to go.

## Page geometry

| quantity | accepted papers | notes |
|---|---|---|
| Pages | 5 in 7/7 | four with references only on page 5; the others add acknowledgements and/or an ethics statement |
| Text block | 178.0 mm wide, columns bottom at ≈255.1 – 255.2 mm on a letter page | spconf default; `\flushbottom` keeps every full column at the same y |
| Last-page right-column gap | 0.1 / 2.2 / 2.6 / 3.9 / 4.9 / 7.6 / 9.0 mm | a 34 mm gap is an outlier; under 10 mm is normal, 1–2 mm is achievable with `\itemsep` |
| Body leading (9 pt) | 10.40 pt ≈ 3.67 mm per line; ≈10 words per full line; ≈59–60 lines per column | the unit for the gap ledger |

## Title block

| quantity | accepted papers | consequence |
|---|---|---|
| First title line y | 33.1 – 34.1 mm (official template 34.1) | **nobody trims `\vskip 2em`; do not be the one paper that does** |
| Lines in the block (title + authors + affiliations + emails) | 4 / 4 / 4 / 5 / 6 / 7 / 8 / 9 | line count is not the constraint |
| Font sizes in the block | 12 pt names everywhere; affiliation lines at 12, 9 or 8 pt | one accepted paper sets names 12 pt / affiliation 8 pt on one line; setting affiliation and e-mail rows at 9 pt is conservative and buys a whole line (see `author-block.md`) |
| E-mail line | the one paper that prints e-mails uses the normal face, 97.8 mm | `\texttt` at 12 pt ran 158.6 mm in one case; monospace is the outlier |

## Abstract

| quantity | accepted papers |
|---|---|
| Lines | 16 / 20 / 21 / 22 / 22 / 22 / 25 |
| Ink height (first line top → last line bottom) | 54.6 / 64.5 / 69.3 / 73.3 / 76.6 / 79.4 / 83.8 mm |
| Kit limit | 80 mm; one accepted paper is at 83.8 |

Measure the abstract as ink height *between* the ABSTRACT heading and the Index
Terms line, not from heading to heading — including the inter-block gap adds
~2.4 mm and produces a false "over the limit".

## Tables

| quantity | accepted papers | consequence |
|---|---|---|
| Caption size | 8.9 – 9.0 pt (i.e. the kit's 9 pt) | keep captions at `\small`/9 pt |
| Table-body size | 5.42 / 6.61 / 6.81 / 6.94 pt in the MSP-ReID paper; 0.61 – 0.77 of caption size across the corpus | `\scriptsize` (7 pt) for the tabular is above venue practice, so it is safe |
| Stub-head alignment in two-row headers | top-row 3 : bottom-row 2; three-row headers centred | booktabs' manual uses bottom alignment; bottom needs no `\multirow` |

Vertical cost in a short table: booktabs `\aboverulesep`/`\belowrulesep` are
sized for 10 pt and dominate; `\arraystretch` is usually already at the
content floor. A `\tightrules` macro that sets `\aboverulesep 0.2ex`,
`\belowrulesep 0.3ex`, `\abovetopsep 0pt`, `\belowbottomsep 0pt` reclaims more
than any `\arraystretch` change.

## References

| quantity | accepted papers | consequence |
|---|---|---|
| Gap before each `[n]` entry (median) | 0.15 / 1.43 / 1.49 / 1.50 / 1.78 / 1.92 / 3.65 mm | with `\itemsep 0pt` the gap is ≈1.1 mm — tighter than 6 of 7 accepted papers; 2.2 pt of `\itemsep` lands at ≈1.7 mm |
| Entry count | 16 – 35 | a 4+1 page paper carries 20 – 30 |
| First-citation order inversions | 0 in 5 papers, 1 in 2 papers (including the venue's own showcase paper) | one inversion caused by a float is venue-normal |
| `Figs.` (plural abbreviation) | 0 occurrences in 7 papers | one figure's panels are `Fig. 3(a, b)` |

## Prose texture (per 1000 body words, references stripped)

| mark | accepted papers | notes |
|---|---|---|
| `;` | median 1.15, max 4.77 (body prose only: median 1.04, max 5.01) | the "AI feel" signal is `independent clause; independent clause` in body prose; caption keys (`ℓ: labels; †: external`) are separate and normal |
| `:` | median 8.55, max 15.28 | usually already in range |
| `—` | median 1.55, max 3.83 | usually already in range |

Measure the two ledgers separately: a paper with an eight-panel figure and four
symbol-keyed tables can sit at 50/1000 in captions while its body prose is at
3/1000 — the second number is the one that matters.

## Conclusions

3 of 6 accepted papers with a conclusion end on a forward-looking sentence
("In future work, we plan to…", "Future work includes…"). A specific one — naming
the paper's own two or three real limits — is a convention worth restoring and
a legitimate way to fill a short last line. Generic ones ("opens promising
directions") are the AI-feel sentence par excellence.

## Compliance statement

The kit gives three example statements. The one for existing data reads:
"conducted retrospectively using human subject data made available in **open
access** by (Source). Ethical approval was not required **as confirmed by the
license** attached with the open access data." Both premises must be true of
*your* datasets before you copy it: a CC BY-NC-SA licence says nothing about
ethics approval, and a dataset obtained under a signed agreement is not open
access. Write what the authors did (retrospective study on released benchmarks,
no new footage, no recruited subjects) rather than what a licence "confirms".
