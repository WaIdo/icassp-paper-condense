# ICASSP rules: what is required, what is suggested, what the template does

Two kinds of rule live in the ICASSP paper kit. Confusing them wastes effort in
both directions: treating a suggestion as law makes you cut content that no one
would have objected to, and treating a requirement as a suggestion gets the
paper bounced by the format checker. Keep them apart.

## Hard rules (violate → rejected at submission or removed later)

| rule | exact form | how to check |
|---|---|---|
| Page count | "a maximum of 4 pages for technical content including figures and possible references, and with one additional optional 5th page containing **only** references, funding acknowledgements, and a Compliance with Ethical Standards statement" | `measure_layout.py`: pages ≤ 5, and the headings found on page 5 |
| Page size | US Letter, 612 × 792 pt | `pdfinfo` |
| Text block | 178 mm wide (spconf sets it; do not touch `\textwidth`) | `measure_layout.py` text-block width |
| Font size | "Use a font size that is no smaller than 9 points throughout the paper, **including figure captions**" | `measure_layout.py` font histogram; captions and body at 9 pt |
| File size | 5 MB | `pdfinfo` |
| Fonts | all embedded, no Type 3 | `pdffonts` — the `emb` column must all be `yes`, `type` never `Type 3` |
| Page numbers | none — added by the publisher | `measure_layout.py` |
| Authors | PDF author list must match the online submission form; ORCiD is validated in the ORCiD portal, not written into the PDF | manual |
| Review model | single-blind: authors are named | — |
| Ethics statement | required "irrespective of whether ethical approval was needed"; "Authors are responsible for correctness of the statements provided" | see the caution in `fact-check.md` about copying the kit's example wording |

The kit's own phrase for measurements: "The Paper Kit description should be
considered the final word."

## Guidance (should; not a rejection, but reviewers and checkers notice)

| item | kit wording | measured practice in accepted papers |
|---|---|---|
| Abstract | "no more than 80 mm (3.125") in length"; elsewhere "approximately 100 to 150 words" | 7 accepted ICASSP 2026 papers: 54.6 – 83.8 mm ink height, 16 – 25 lines. One is over 80 mm. ~200 words / 22 lines / 80 mm is unremarkable |
| Line density | "no more than 3.2 lines/cm" | spconf's `\ninept` gives 10.4 pt leading ≈ 2.7 lines/cm |
| Title block | title bold caps, authors, affiliation | see `measurements.md` — every accepted paper starts the title at 33.1 – 34.1 mm; the block runs 4 – 9 lines |
| Table bodies | (the 9 pt rule names captions, not table bodies) | accepted papers set table bodies at 5.4 – 6.9 pt while captions stay at 9 pt; `\scriptsize` (7 pt) is conservative |
| In-figure text | not specified | axis labels and panel annotations at 6 – 7 pt are universal in the corpus |
| Footnotes | not specified | 3 of 7 accepted papers have 8 pt first-page footnotes; that is spconf's own `\footnotesize` via `\thanks` |

## What `spconf.sty` actually does (facts that decide several tactics)

- `\ninept` is only `\def\baselinestretch{.95}\let\normalsize\small\normalsize`.
  The size ladder is therefore the stock 10 pt one: `\tiny` 5, `\scriptsize` 7,
  `\footnotesize` 8, `\small` 9. Under `\ninept`, `\normalsize` **is** 9 pt —
  useful inside the title block, where the outer group is `\large`.
- `\@makecaption` hard-codes `\vskip 10pt` above every caption and ignores
  `\abovecaptionskip`. Override it in the preamble if you need the skip smaller;
  3 pt reads fine.
- `\flushbottom` is on. Column bottoms are stretched to the text block, so a
  freed line never stays as white space: it pulls later material up, and if a
  section heading plus two lines cannot fit in the freed room, the glue between
  paragraphs stretches instead (visible, and eventually an `Underfull \vbox`).
- `\@maketitle` uses `\vskip 2em` before the title, `\vskip 1.5em` between
  title and author block, `\vskip 1.5em` after. The author/address tabular is
  set in `{\large \lineskip .5em ...}`. `\name{}` is one row; each `\\` in
  `\address{}` is a new row (and a new tabular cell, so font commands do not
  carry across rows).
- **`spconf.sty` never touches `\section`'s spacing.** It redefines `\@sect`,
  which sets the *face* (bold, section titles in capitals) — the before/after
  skips are still `article`'s, sized for a 10 pt one-column class: section
  `{-3.5ex plus -1ex minus -.2ex}{2.3ex plus .2ex}`, subsection
  `{-3.25ex ...}{1.5ex plus .2ex}`. That is why heading spacing is a real lever
  here and not in a class that already tuned it (see `compression.md`).
- `\thebibliography` is a `\list` with default `\itemsep`; you can redefine it
  after loading the style to tune reference spacing (see `compression.md`).
- Two-affiliation support exists as `\twoauthors{...}{...}{...}{...}`, which
  places two author/address groups side by side.

## Reference style

The kit ships `IEEEbib.bst`. Two behaviours matter:

- `and others` in the `.bib` renders as " et al." IEEE's rule: list up to six
  authors in full; beyond six, first author + et al. Both directions are rules —
  a five-author entry printed as et al. is as wrong as a nine-author entry
  printed in full.
- Numbering is by order of first `\citation` in the `.aux`, which is the order
  LaTeX *executes* `\cite`. A `\cite` inside a float executes when the float is
  declared, not where it is placed, so printed first-appearance order can be
  non-monotonic (2 of 7 accepted ICASSP 2026 papers have exactly one such
  inversion). Do not fight it with `\nocite` ordering.

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
