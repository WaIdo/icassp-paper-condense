# icassp-paper-condense

[English](README.md) · **简体中文**

一个用于把 LaTeX 论文压进 **ICASSP「4 页正文 + 1 页参考文献」限制**（spconf 模板）
的 agent skill：**只改排版，绝不删改你的文字、图和表**，每一次改动都用测量而不是
肉眼来验证。

**Claude Code** 与 **OpenAI Codex** 通用（两端读同一份 `SKILL.md` 格式）。
其中的本会数值全部实测自 7 篇已录用的 ICASSP 2026 论文；流程与「坑」来自在一篇
真实投稿上做这件事的过程，包括其中犯过的错。

## 它做什么

1. **阶段 0** —— 只测量：页数、每栏栏底、溢出量（mm）、单词末行、字号分布、
   引用顺序，同时量本会语料，产出「缺口账单」，然后**停下**。
2. **阶段 A** —— 只动图、表和它们的 caption：表格字号与横线留白、浮动体聚拢与
   编号顺序、图内排版、caption 去重与限定域。**做完停下等作者确认。**
3. **阶段 B** —— 正文，**只排版**：用 microtype、`\looseness`、连字符、
   浮动体位置来省行，一个字不动；然后填满末页，并做事实核查。
   凡是需要动文字才能解决的，写成建议交给你，不会自己改。
4. 每次改动之后：重新编译，跑一遍必须全过的七项闸门。

**三条红线**：

- **你的文字一个字都不会被改。** 不删段落、不删句子、也不删"两个多余的词"——
  对正文它只能改**同样这些字怎么排**：microtype、`\looseness`、连字符、
  浮动体位置。实测在一篇 5 页论文上，**光是启用 microtype 就省了 32 行
  （约一整页），一个字没动**。排版手段用尽还不够时，它会把"可以删哪几个词、
  能省几行"写成建议交给你，然后停下——删不删你说了算。
- **图和表的内容不删**：不砍指标列，不去掉面板。
- **不过度修正**：一处改动如果只让主张变弱、没让它更准确，就不改；
  发现事实问题会连证据和建议措辞一起报给你，而不是自己改掉。

## 动手前先备份

这套流程里的每一步都只有"有东西可回退"时才是可逆的，而压页排版恰恰是那种
第三次尝试可能比第一次更糟的活。请备份**整个源码目录**，不要只存 PDF：

```bash
git add -A && git commit -m "pre-condensation snapshot"
# 没用 git 的话：
cp -r my-paper my-paper.backup-$(date +%Y%m%d_%H%M%S)
```

流程的阶段 0 第一件事就是做这个，没有备份不往下走。另外每完成一个阶段
在 `backup/` 里留一份带日期的 PDF，这样 `diff_numbers.py` 随时有上一版可比。

## 安装

### Claude Code

```bash
git clone https://github.com/WaIdo/icassp-paper-condense ~/.claude/skills/icassp-paper-condense
```
或把整个目录放进项目的 `.claude/skills/` 下。Claude Code 依据 `SKILL.md` 里的
`name` / `description` 自动发现它。

### Codex

```bash
git clone https://github.com/WaIdo/icassp-paper-condense ~/.codex/skills/icassp-paper-condense
```

### 依赖

```bash
pip install pymupdf
```
以及 poppler（`pdftotext`、`pdfinfo`、`pdffonts`）和带 `latexmk` 的 TeX 发行版。
macOS 上：`brew install poppler`。

## 脚本

在论文所在目录下运行。

| 脚本 | 用途 |
|---|---|
| `scripts/measure_layout.py main.pdf` | 完整的版面 / 合规报告（可加 `--json`） |
| `scripts/find_runts.py main.pdf --main main.tex` | 找出末行只有 ≤2 个词的段落与 caption |
| `scripts/check_citations.py --main main.tex` | 引用 ↔ bib ↔ bbl 核对、引用上下文、IEEE 的 et al. 规则 |
| `scripts/diff_numbers.py old.pdf new.pdf` | 两次编译之间正文页丢失/新增了哪些数字 |
| `scripts/corpus_baseline.py papers/ICASSP2026/ --also main.pdf` | 实测已录用论文，并把自己这篇并排放进去比 |
| `scripts/verify_all.sh main.tex --backup old.pdf` | 重编译 + 跑全部闸门；有任何一项不过则返回非零 |

## 目录结构

```
SKILL.md                  流程、红线、闸门、报告模板
references/
  rules.md                ICASSP 的硬性条款 vs 指导性条款；spconf.sty 的真实行为
  measurements.md         本会基线（题头、摘要、表格、参考文献、标点密度）
  compression.md          各压缩杠杆及其实测收益；缺口账单；末行记账公式；\flushbottom
  author-block.md         加作者 / 加第二单位而不占用正文空间
  fact-check.md           哪些句子真的会错；证据等级；过度修正
  pitfalls.md             静默失败清单，每一条都真实发生过
scripts/                  见上表
```

## 适用范围

面向使用 spconf 模板、有硬性页数限制、且允许一页「仅参考文献」的 IEEE 会议
（ICASSP、ICIP 等）。测量脚本对任何双栏 PDF 都可用；
`references/measurements.md` 里的本会数值取自 ICASSP 2026，换会议时
应当用 `corpus_baseline.py` 重新实测，而不是沿用。

## 许可

MIT —— 见 [`LICENSE`](LICENSE)。Copyright (c) 2026 WaIdo (github.com/WaIdo)。

每个脚本开头都带 `SPDX-License-Identifier: MIT` 标识，每份 reference 文件末尾
都带一行出处说明——这样即使某个文件被单独拷贝出去，也仍然带着它的来源与条款。
修改时请保留它们。

**本许可不覆盖**：ICASSP paper kit 与 `spconf.sty`（归 IEEE/ICASSP 所有）；
以及你用 `corpus_baseline.py` 去量的那些论文（归各自作者所有）。
`references/measurements.md` 中引用的本会数值是**对已发表论文的测量**——
关于版心几何、字号、标点计数的事实观察，而非对其内容的复制。

如果这个项目对你的工作有帮助，欢迎（但不强制）在文中给出仓库链接。
