# Silent failures: things that succeed, report nothing, and are wrong

Every entry here happened on a real paper. None of them produced a warning.

## Build and tooling

**BibTeX skips an entry that contains a `%` comment.** There is no comment
syntax inside `@entry{...}`. A `%` line inside the braces yields "You're
missing a field name" in the `.blg` and the entry vanishes — while `pdflatex`
completes normally and the PDF is one page shorter. Put notes above the `@`,
never inside. Check `.blg` for `Warning--` / `You're missing` after every
bibliography change (`verify_all.sh` does).

**`&&` chains hide the failing step.** `bibtex main && pdflatex main` reports
the last command's status; a references-free PDF was once reported as "down to
five pages" this way. Run `bibtex` separately and look at its exit code, or
count `\bibitem` in the `.bbl`.

**Appending to a relative path from the wrong directory.** `cat >> guide.md`
with the shell's working directory in the paper folder created a new
`paper/guide.md` holding only the appended section; the real guide never
received it, and the commit succeeded. After any `>>` to a file that should
already exist, confirm the target's line count grew rather than a new file
appearing. Prefer absolute paths in scripts that write.

**Regex for coordinates that ignores negatives.** `[\d.]+` silently drops
`yMin="-0.68"` boxes from a figure-text map; use `(-?[\d.]+)`.

**Font-name filters that exclude your own paper.** A check for
`"Times" in font_name` dropped the paper's own `NimbusRomNo9L` fonts and
reported "no change". Filter by size, not by name.

**Measuring the wrong quantity.** "Model size: 86.14M" in a training log is the
whole network (backbone + BN neck + classifier); the caption's "≤86M
backbones" bound refers to the backbone (86.09M). Confirm what a printed
number *is* before declaring a bound violated.

**Two copies of a file.** When a guide exists at the repo root and in a
prompts folder, edit one, then `cmp` and copy. When a release exists as
`release/X/` and `release/upload/X/`, find out which tree is the git remote
before fixing anything — in one case the stale copies had the bug and the
uploaded tree had already fixed it, while a *different* error was live in the
uploaded tree.

## LaTeX layout

**Float numbering follows declaration order.** `\caption` numbers are assigned
when the float is declared. If Fig. 4 is cited before Fig. 3 in the printed
text, the fix is to move the float's `\begin{figure}` to just after the
paragraph that first `\ref`s it, then re-measure every column bottom.

**`\cite` inside a float fires when the float is declared.** Reference
numbering (by first `\citation` in the `.aux`) can therefore be non-monotonic
in the printed order. Two of seven accepted ICASSP 2026 papers show one such
inversion; leave it.

**`\flushbottom` turns freed lines into stretched glue**, and can pull the
next section heading onto the page you just emptied. Free a line only where
you are about to spend it.

**A `table*` caption is full-width**; adding seven words to it adds a full
page-width line and pushes body text off the page. Pay for it first.

**`\normalsize` inside `\address{}` applies to one tabular row.** Each `\\` is
a new cell; repeat the size command on every row.

**Abstract height measured heading-to-heading** includes the inter-block gap
and reads ~2.4 mm too high. Measure from the first abstract line's top to the
last one's bottom.

## Claims and citations

**A dash means two things.** CSCI-style attribute tables define `–` as
"results/attributes not reported/used". Reading it as "not used" and
downgrading a competitor's attribute marker on that basis was an over-
correction; five consistent internal records said otherwise.

**Third-party tables get venues wrong.** A workshop paper (pages 173–182) was
listed by its citing paper as the main conference (whose pages run to
6000+). Page-number magnitude decides; copy the numbers, judge the venue.

**Column order differs between your table and the source table** (e.g.
CC R-1 / CC mAP / General R-1 / General mAP versus General mAP / General R-1 /
CC mAP / CC R-1). Transcribe by column *name*.

**Method names follow the source of the numbers.** If a row's values come from
paper P's comparison table, use P's name for the method, even when the cited
paper's title does not contain it — otherwise readers cannot line the two
tables up.

**The same citation on two rows is fine** when they are two variants from one
paper ("X" and "X + re-rank"); it is not a duplicate.

**Expanding et al. to fill a page is a format violation**, not a trick: IEEE
lists up to six authors, first author + et al. beyond.

## Process

**Parallel verification with dying workers.** If the aggregation rule is
"keep the flag if ≥2 of 3 verifiers agree", a claim whose three verifiers all
timed out is silently cleared. Track *un-adjudicated* separately from
*cleared*; report both counts.

**Over-correction runs one way.** All three reverted edits in one audit had
weakened the authors' own claims. See `fact-check.md`.

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
