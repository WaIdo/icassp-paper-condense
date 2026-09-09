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
| Font sizes in the block | **12 pt on every line, in all seven papers.** The only sub-12 pt spans above the abstract are a superscript affiliation marker (`1,*`, 8 pt) in one paper and a teaser figure's panel labels in another | there is **no accepted-paper precedent for a 9 pt affiliation row**. Dropping to 9 pt is a deviation — justified only when 12 pt does not fit the 178 mm block, which is what happens with two affiliations on one row (see `author-block.md`) |
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

## Section headings

Measured by `corpus_baseline.py` (`head_ab_pt` / `head_be_pt`) as the white
*above* and *below* a numbered heading, **net of that paper's own
in-paragraph line gap** — so a 9 pt and a 10 pt paper are directly comparable.

| paper | extra above (pt) | extra below (pt) |
|---|---|---|
| 2604.17062v1 | 10.59 | 4.29 |
| 2603.01640v2 | 10.49 | 6.56 |
| 2603.27533v1 | 12.26 | 6.13 |
| 2603.29291v1 | 12.76 | 7.41 |
| 2603.19757v1 | 13.69 | 7.62 |
| 2604.03002v1 | 16.88 | 7.65 |
| 2606.11783v1 | 17.46 | 9.37 |
| **corpus range** | **10.5 – 17.5** | **4.3 – 9.4** |
| stock `article` skips (`-3.5ex/2.3ex`, `-3.25ex/1.5ex`) | 15.12 | 8.20 |

Two things follow. First, **the untouched template already sits inside the
accepted band** — nobody has to tighten headings to look normal, so any
tightening is a page-buying decision, not a correction. Second, the band is
wide: the loosest accepted paper leaves 1.7× the white of the tightest, which
means a few pt of tightening is invisible at this venue.

The one paper measured with reduced skips (`-1.8ex/1.0ex`, `-1.6ex/0.6ex`)
came out at 7.21 above / 3.06 below — below the corpus floor on both. It is
flagged by `measure_layout.py` for exactly that reason. It stayed because the
page it buys was load-bearing; see the worked case in `compression.md`.

## Tables

| quantity | accepted papers | consequence |
|---|---|---|
| Caption size | 8.9 – 9.0 pt (i.e. the kit's 9 pt) | keep captions at `\small`/9 pt |
| Table-body size | one paper (2603.01640v2) sets its four tables at 5.42 / 6.61 / 6.81 / 6.94 pt with 8.93 pt captions; ratios to caption size across all 7 papers are 0.61, 0.70, 0.77, 0.87, 0.88, 0.97, 1.00, 1.00, 1.00 | **three of the seven do not shrink the tabular at all**, and the floor among those that do is 0.61. `\scriptsize` (7 pt against a 9 pt caption, ratio 0.78) sits mid-range, so it is safe |
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

## Reference venue names

| quantity | accepted papers |
|---|---|
| Lines carrying an abbreviated venue (`Proc.`, `Trans.`, `Conf.`, `Int.`) | 0 / 0 / 0 / 0 / 0 / 2 / 2 |
| Lines carrying a full venue name (`Proceedings of`, `Transactions on`, `International Conference`) | 0 / 7 / 10 / 10 / 11 / 21 / 21 |

Six of the seven print venue names in full. IEEE editorial style prescribes the
abbreviated forms, so abbreviating is *more* compliant than what the corpus
does, not less — but it will not look like the neighbouring papers. It is also
the single largest reference-page lever measured here (see `compression.md`),
which is why it is worth knowing that both forms get accepted.

## Prose texture (per 1000 body words, references stripped)

| mark | accepted papers | notes |
|---|---|---|
| `;` | median 1.15, max 4.77 (body prose only: median 1.04, max 5.01) | the "AI feel" signal is `independent clause; independent clause` in body prose; caption keys (`ℓ: labels; †: external`) are separate and normal |
| `:` | median 8.55, max 15.28 | usually already in range |
| `—` | median 1.55, max 3.83 | usually already in range |

Measure the two ledgers separately: a paper with an eight-panel figure and four
symbol-keyed tables can sit at 50/1000 in captions while its body prose is at
3/1000 — the second number is the one that matters.

## Italics

| quantity | accepted papers | consequence |
|---|---|---|
| Italic runs in the body (pages 1–4, title block and Index Terms excluded) | 0 / 1 / 8 / 11 / 14 / 27 / 29 | there is **no venue norm**: the corpus spans "none at all" to one every other paragraph. Italics density is therefore never evidence for a change — do not propose adding or removing emphasis on the grounds that the venue does or does not use it |

What the corpus is consistent about is the *use*, not the count: an example
string quoted from data (a caption, a label, a class name) appears in quotation
marks, and italics carry defined terms and method names. A paper that
italicises quoted example strings is the odd one out — but it is still the
author's markup, so it is a proposal like any other text change.

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

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
