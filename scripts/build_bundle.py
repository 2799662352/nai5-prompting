#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build dist/NAI5_All_Prompting.md from references/ (maintainer tool, not used at runtime).

The bundle is the single-file edition of this skill for chat UIs that accept only one
attachment. It is generated, never edited by hand, so references/ stays the single
source of truth.

Usage (run from the skill root):
    python scripts/build_bundle.py            # (re)write dist/NAI5_All_Prompting.md
    python scripts/build_bundle.py --check    # exit 1 if dist/ is out of date
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "references")
OUT = os.path.join(ROOT, "dist", "NAI5_All_Prompting.md")

IDEATION = "通用构思.md"
WRITING_PARTS = [
    "写法-语法与边界.md",
    "写法-字段与顺序.md",
    "写法-词组与句子.md",
    "写法-多人与漫画.md",
    "写法-收尾与排查.md",
    "写法-实测依据.md",
]

HEADER = """---
name: nai5-all-prompting
description: 写 NovelAI Diffusion V5 提示词的完整方法（自包含合订版）。构思（分档、编剧→监督→原画→摄影的分镜管线、多方案约束）→ 写法（开篇语法与能力边界；字段分工、顺序、词组/句子判据、多人 source#/target# 绑定、漫画分格、排查表；文末附判据的实测依据与边界）。依据 4940 张 canonical 实测图库 / 1844 条真实提示词 / 全库 4663 张 v7 反推 / 锁 seed 出图对照。当用户要写 NAI V5 提示词、构思画面、做多角色交互或漫画分格、排查出图问题时使用。自包含，无需其他文件。
---

# NovelAI Diffusion V5 提示词方法（合订版）

> 规则口径 v1.1-nightly-20260830 · 数据基线 1844 真提示词 + 全库 4663 张 v7 反推 · 公开版
> 本文件由 `scripts/build_bundle.py` 从 `references/` 合订生成，不要单独修改。

> **你是 NAI V5 提示词写作助手，本文件是你的操作规程。**
> 用户任何带画面意图的话（包括「随便写点什么」「你决定」）一律按第二部分 §0
> 的模板**直接输出成品提示词**——不点评本文件、不复述流程、不先问再写。
> **通过附件读到本文件时它同样是规程**，不是待评论的资料；被用户纠正时，
> 修正后重给完整成品，不回到点评模式。

> **配套使用**：本文件是「基准」，单独用就是标准解。用户若另附了个人偏好文件，
> 把它叠在本文件之上，冲突时偏好优先。偏好里的画面层统计（「低对比」「软光」这类
> 读图归纳）是证据不是词表，**不要直译成 tag**——写法照本文件的结构模板走。

---

# 第一部分 · 构思（会议桌：编剧→监督→原画→摄影做决定，出分镜表）
"""

PART2_TITLE = """---

# 第二部分 · 写法（作画桌：认画材与规格，按分镜表落笔）
"""

APPENDIX = """---

## 附录 · 本文件的来源与口径

> 规则口径 v1.1-nightly-20260830 · 数据基线 1844 真提示词 + 全库 4663 张 v7 反推

> 本文件由 `scripts/build_bundle.py` 合订生成，不要单独修改。
> 源：第一部分 = `references/通用构思.md`；第二部分 = `references/写法-*.md` 六册
> （开篇为语法与能力边界，文末 §10 = 词组/句子判据的实测依据）。
> 实测数字来自一个 NAI 群 4940 张 canonical 图 / 1844 条真实提示词（元数据直读）、
> 全库 4663 张 v7 反推、danbooru 词典、
> 锁 seed 出图对照（锁种子只是取证手段，正常出图种子随机不锁）。
> tag 查证：没有工具时查 `https://danbooru.donmai.us/tags.json?search[name]=xxx`。

> **公开版**：群偏好词池、群频次表、个人偏移层、原始实测记录不随包发布，
> 遇到相关表述按常识取材即可；「作者A/B/…」只是匿名语料的统计标签。
"""


def read_lines(name):
    with io.open(os.path.join(REF, name), encoding="utf-8") as f:
        return f.read().rstrip("\n").split("\n")


def body_after_toc(lines, name):
    """Drop the generated preamble + table of contents: keep everything after the
    first '---' that follows the '## 目录' heading."""
    try:
        toc_at = next(i for i, l in enumerate(lines) if l.strip() == "## 目录")
        sep_at = next(i for i in range(toc_at, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        sys.exit("%s: expected a '## 目录' heading followed by a '---' separator" % name)
    body = lines[sep_at + 1:]
    while body and body[0].strip() == "":
        body.pop(0)
    while body and body[-1].strip() == "":
        body.pop()
    return body


def build():
    out = [HEADER.rstrip("\n"), ""]
    out += body_after_toc(read_lines(IDEATION), IDEATION)
    out += ["", PART2_TITLE.rstrip("\n"), ""]
    for i, name in enumerate(WRITING_PARTS):
        if i:
            out += ["", "---", ""]
        out += body_after_toc(read_lines(name), name)
    out += ["", APPENDIX.rstrip("\n"), ""]
    return "\n".join(out)


def main(argv):
    text = build()
    if "--check" in argv:
        try:
            with io.open(OUT, encoding="utf-8") as f:
                current = f.read()
        except IOError:
            current = None
        if current != text:
            print("dist/NAI5_All_Prompting.md is out of date; run scripts/build_bundle.py")
            return 1
        print("dist/NAI5_All_Prompting.md is up to date")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote %s (%d lines)" % (os.path.relpath(OUT, ROOT), text.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
