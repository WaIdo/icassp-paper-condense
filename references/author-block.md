# Adding an author or a second affiliation without spending a body line

## Why this needs a recipe

The title block is full-width. Pushing it down by one address row pushes the
start of *both* columns down, so page 1 loses two body lines, and with
`\flushbottom` those two lines ripple through every page. On a paper that is
exactly full, one extra `\address` row put the conclusion's last two lines on
page 5 — where the kit allows only references, acknowledgements and the ethics
statement. So the extra row has to be paid for inside the title block itself.

## Where the space is (and is not)

| candidate | measured | verdict |
|---|---|---|
| `\vskip 2em` above the title | every accepted paper starts its title at 33.1 – 34.1 mm; the official template at 34.1 | **do not touch** — trimming it makes yours the only deviating paper |
| Title-block line count | accepted papers run 4 – 9 lines | not the constraint |
| Font size of the affiliation/e-mail rows | all seven accepted papers set the whole block at 12 pt; none drops the affiliation row | **this is the lever, and it is a deviation** — take it only when 12 pt does not fit. Measured on a two-college row: at 12 pt the line ran 195.5 mm against a 178 mm block (1 Overfull, text outside the block); at 9 pt it fits at 160.6 mm. Splitting it into two 12 pt rows is compliant but cost a whole page. 9 pt is the kit's floor — 8 pt is below it and not an option |
| `\texttt` e-mails | the one accepted paper printing e-mails uses the normal face at 97.8 mm; monospace at 12 pt ran 158.6 mm | drop `\texttt` |
| Institution and e-mail on one line | — | authors rejected this as improper; keep them on separate rows |

## The recipe

Before (three-author, one affiliation, two address rows):

```latex
\name{A. One, B. Two, C. Three$^{*}$\thanks{...}\thanks{$^{*}$Corresponding author.}}
\address{College of X, University U, Country\\
\texttt{\{id1, id2, id3\}@u.edu}}
```

After (four authors, two affiliations, **still two address rows**, body untouched):

```latex
\name{A. One$^{1}$, D. Four$^{2}$, B. Two$^{1}$, C. Three$^{1,*}$\thanks{...}\thanks{$^{*}$Corresponding author.}}
\address{\normalsize$^{1}$College of X, $^{2}$College of Y, University U, Country\\
\normalsize\{id1, id4, id2, id3\}@u.edu}
```

Three things make it work:

1. **`\normalsize` on every row.** spconf wraps the block in `{\large ...}`
   (12 pt). Under `\ninept`, `\normalsize` is exactly 9 pt — the kit's floor.
   The content sits in a `tabular`, and `\\` starts a new cell, so a font
   command in one row does not carry to the next: write it on each row.
2. **Width scales by 0.75.** Two college names plus the shared university fit
   one 9 pt row (160.6 mm of 178 mm in the worked case); the e-mail list alone
   fits the next (94.4 mm). The block is two rows, shorter than the original
   two rows at 12 pt.
3. **E-mails in the normal face, braces as `\{ \}`.** Keep the e-mail order
   matching the author order.

## Verify after the change

```
measure_layout.py main.pdf     # pages unchanged; title block widths all < 178 mm; sizes [12,12,12,9,9]
find_runts.py ...              # unchanged
```
and confirm: conclusion still ends on the last body page; page 5's first line
is the ethics statement or References; every column bottom still flush; the
affiliation/e-mail *text* spans are ≥ 9.0 pt (the superscript markers at 6 pt
are normal — every paper with numbered affiliations has them).

## Do not forget

The author list on the ICASSP submission form must match the PDF (kit rule).
ORCiDs are validated in the ORCiD portal, not printed in the paper.

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
