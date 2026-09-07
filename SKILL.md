---
name: icassp-paper-condense
description: Condense, typeset and fact-check a LaTeX paper to ICASSP's 4-page-plus-references limit (spconf.sty) without deleting any figure or table content, then verify every edit by measurement. Use this whenever a user wants to shrink, compress, tighten, squeeze, fit, or polish a paper for ICASSP or another IEEE signal-processing venue on the spconf template, mentions a page overflow, an over-long fifth page, a last page that is half empty, one-word last lines, a table that is too wide or too tall, an abstract over 80 mm, adding an author or affiliation without breaking the page count, or asks to check that the paper's numbers, citations and claims still hold after editing -- even if they never say "ICASSP" but the paper is a 4+1-page two-column IEEE conference submission.
---

# ICASSP paper condensation

You are shrinking a finished paper into ICASSP's budget: **4 pages of technical
content, plus an optional 5th page that may hold only references, funding
acknowledgements and the Compliance-with-Ethical-Standards statement.** The
paper is usually already written and already good; your job is to make it fit
and keep it correct, not to rewrite it. Everything below follows from three
facts about this task:

1. **A page-limited paper is a zero-sum layout.** Every line you add is paid
   for by a line somewhere else, and `\flushbottom` means freed lines do not
   sit as white space -- they pull later content upward, sometimes dragging a
   section heading onto the wrong page. So measure before and after every
   edit, and know where each line came from.
2. **Verification, not impression.** "It looks fine" is how a references-free
   PDF gets reported as "five pages". Every claim in your report carries a
   number or a `file:line`.
3. **The author has already made judgment calls.** Deleting a claim that holds
   is as wrong as adding one that doesn't. When you are unsure whether a change
   sharpens or merely weakens, ask.

## Red lines (stop and ask the author before crossing)

- **Never cut figure or table content**: no dropping metric columns, no
  removing panels, no shrinking a figure until labels are unreadable. Space
  comes from layout and prose. If those run out, present the gap in mm and the
  options with their costs; the author chooses.
- **Never over-correct.** Before changing any statement, answer: which *quantity*
  is the sentence wrong about, is your evidence a *unique* reading, does it
  outrank what it contradicts, and does the change make the claim *more
  accurate* or only *weaker*? "Only weaker" means leave it. See
  `references/fact-check.md`, section "Over-correction".
- **Never edit twice without rebuilding.** Run `scripts/verify_all.sh` after
  every change.
- **Not verifiable ≠ wrong.** A claim you cannot check locally (source PDF or
  checkpoint missing) goes into a "for the author to confirm" list, not into
  an edit.

## Tools

All scripts need Python 3 with PyMuPDF (`pip install pymupdf`) and poppler
(`pdftotext`, `pdfinfo`, `pdffonts`). Run them from the paper directory.

| script | what it answers |
|---|---|
| `scripts/measure_layout.py main.pdf` | pages, per-column bottoms, last-column gap, log/bibtex counts, references cited/orphaned/`[?]`, first-citation order of refs and floats, what is on page 5, abstract height, title-block geometry, font sizes, page numbers |
| `scripts/find_runts.py main.pdf --main main.tex` | every paragraph and caption whose last line has ≤2 words, with fill %; exit code = count |
| `scripts/check_citations.py --main main.tex` | cite keys ↔ bib entries ↔ bbl items, each key's context, IEEE et-al rule, missing year/pages, duplicates, `%` inside entries |
| `scripts/diff_numbers.py old.pdf new.pdf` | numbers lost or gained on the body pages between two builds |
| `scripts/corpus_baseline.py papers/ICASSP2026/ --also main.pdf` | measure accepted papers from the venue and place yours beside them |
| `scripts/verify_all.sh main.tex --backup old.pdf` | rebuild + all of the above; non-zero exit if any gate fails |

`measure_layout.py --json` gives machine-readable output when you need to
compute with it.

## Workflow

### Phase 0 — baseline (measure only, change nothing)

1. Back up: `cp main.pdf backup/$(date +%Y%m%d_%H%M%S)_$(git rev-parse --short HEAD).pdf`.
2. `measure_layout.py main.pdf` and `find_runts.py`. Note the overflow in mm
   and convert to lines (9 pt spconf: 1 line ≈ 3.67 mm, ≈10 words per full line).
3. If accepted papers from the venue are available, `corpus_baseline.py` them.
   Almost every "is this normal?" question in this task is settled by that
   table, not by memory. If no corpus is available, say so; do not assert
   venue conventions you have not measured.
4. Write the gap ledger (`references/compression.md`, "Gap ledger"): overflow
   lines ÷ words available to condense. Above ~20 % the gap cannot be closed by
   prose alone -- tell the author now, with the layout levers and their
   measured yields, rather than discovering it three hours in.
5. Report and **stop**. Do not enter Phase A without the author's go-ahead.

### Phase A — figures, tables and their captions (nothing in the body)

Work in this order; it is roughly benefit ÷ risk:

1. **Table bodies.** `\small` → `\caption{...}` → `\scriptsize` applied to the
   `tabular` only, so the caption stays at the kit's 9 pt. Return the width you
   freed as `\tabcolsep` so the table still spans the column. The vertical lever
   in short tables is booktabs' `\aboverulesep`/`\belowrulesep`, not
   `\arraystretch`, which is usually already at the content floor. Read actual
   span sizes from the PDF; do not infer sizes from box heights.
2. **Float placement and numbering.** Floats declared at the same point tend to
   land in one column. Numbering follows `\caption` declaration order, not page
   position: if `measure_layout.py` shows figures cited out of order, move the
   float's declaration to just after its first `\ref`, then re-measure all
   column bottoms. One figure with several panels is `Fig. 3(a, b)`, never
   `Figs. 3(a, b)` -- accepted papers contain zero `Figs.`.
3. **In-figure typography.** Pairwise overlap checks miss three things: text
   escaping its own panel (do a containment check), a legend entry that reads
   as a formula but does not match the method (check it against the code --
   legends describe the toy drawing, readers cite them as definitions), and
   abbreviation periods that differ between panels. After any figure rebuild,
   confirm the PDF bounding box is unchanged so the page does not reflow.
4. **Captions.** Run an n-gram comparison against the body; a sentence that
   appears in both is deleted from the caption, not the body. Fix ≤2-word last
   lines with the accounting rule below. Every comparison table's caption must
   carry the same scope qualifier the prose uses ("among backbones of
   comparable scale", "≤ N M parameters") -- reviewers check superlatives
   against the table, not against the paragraph that scoped them.
5. Run `verify_all.sh`, report using the template below, and **stop for the
   author's confirmation**. Say how many mm Phase A saved and how many words
   Phase B will need.

### Phase B — body text (only after the author confirms Phase A)

1. **Delete repetition before deleting information.** Three kinds cost nothing:
   the experiments section restating the method section verbatim; a sentence
   that a caption already says; and "colon + restating clause" endings
   (`..., which shows X: averaging is not generically beneficial.`) -- those are
   simultaneously a runt source, a repetition and a punctuation-density
   contributor.
2. **Short last lines.** With W words on the last line and ~N words per full
   line, cutting k words leaves ≈ N + W − k. Cut 2–3 words; cutting 5+ makes a
   new half-empty tail. `find_runts.py` reports W and fill %.
3. **Punctuation and "AI feel".** Measure semicolon/colon density per 1000 words
   against the corpus *before* editing, and keep two ledgers: body prose
   (`independent clause; independent clause` is the tell -- split into
   sentences) versus caption keys (`ℓ: labels; †: external model;`) which are a
   normal compression device and stay.
4. **Fill the last page.** Measure the corpus's last-column gap first (accepted
   ICASSP 2026 papers: 0.1–9.0 mm). The main lever is the bibliography
   `\itemsep`, tuned by bisection with a full rebuild each step. Do not expand
   `et al.` author lists to fill space -- IEEE style requires et al. past six
   authors, so expanding is a violation, not a trick. A concrete, paper-specific
   future-work sentence in the conclusion is venue-normal (3 of 6 corpus
   conclusions) and fills the last line honestly.
5. **Fact-check what you touched**, using `references/fact-check.md`. Numbers
   rarely break; sentences with "prevents / ensures / all / both / no existing"
   do.
6. `verify_all.sh --backup <phase-A pdf>`; every number in the diff must be
   explainable.

### After every edit

```
verify_all.sh main.tex --backup <previous.pdf>
```
must show: pages ≤ limit · Overfull 0 · undefined 0 · BibTeX warnings 0 ·
conclusion still on the last body page · page 5 holds only references /
acknowledgements / ethics · all column bottoms flush except the last ·
runts 0 · references all cited, none `[?]` · float order ascending · every
lost/gained number explained.

## Report template

```
## Changed
| edit | evidence (measurement or file:line) | yield |

## Gates (verify_all.sh)
pages / Overfull / undefined / last body page / page-5 contents / column
bottoms / runts / citations / numbers-vs-backup

## Remaining gap
X mm ≈ Y lines; Phase B needs ≈ Z words

## For the author to decide
(each: current state, options, cost of each -- do not decide for them)

## Could not verify locally
(what to check, against what, and what to change if it disagrees)
```

Report conclusions and evidence, not the process.

## When to stop and ask

1. End of Phase A -- always.
2. Gap ledger above ~20 % of condensable prose.
3. Any edit that changes a claim: dropping a qualifier, softening "all" to
   "most", changing a competitor's attribute marker, rewording what was
   measured.
4. A factual error with more than one defensible fix.

Everything else: finish the phase, then report.

## Reference files

Read these when the situation arises; they hold the measured facts and the
worked reasoning behind the rules above.

| file | read it when |
|---|---|
| `references/rules.md` | you need to know what the kit *requires* versus *suggests*, and what `spconf.sty` actually does |
| `references/measurements.md` | deciding whether something is "normal for the venue": title block, abstract, table fonts, reference spacing, last-page gap, punctuation density |
| `references/compression.md` | choosing a lever and estimating its yield; the gap ledger; the runt rule; `\flushbottom` behaviour |
| `references/author-block.md` | adding an author or a second affiliation without spending a body line |
| `references/fact-check.md` | before touching any sentence's meaning; over-correction; which sentences actually break |
| `references/pitfalls.md` | silent failures: BibTeX skipping entries, `&&` masking exit codes, appending to the wrong file, float numbering, "not reported/used" symbols |

## License and attribution

MIT — see `LICENSE`. Copyright (c) 2026 WaIdo (github.com/WaIdo).
Source: https://github.com/WaIdo/icassp-paper-condense

You may use, modify and redistribute this skill, including inside a paid or
closed product, provided the copyright notice and the licence text travel with
it. That matters here because agents copy single files out of skills: each
script carries an SPDX header and each reference file a one-line footer, so a
file that ends up somewhere else still says where it came from. Keep them when
you edit.

Two things this skill does **not** license, because they are not its to give:
the ICASSP paper kit and `spconf.sty` (IEEE/ICASSP's own terms), and the papers
you point `corpus_baseline.py` at. The venue figures quoted in
`references/measurements.md` are measurements of published work — facts about
page geometry and font sizes, not reproductions of it.

