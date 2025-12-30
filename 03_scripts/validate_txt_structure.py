#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
from dataclasses import dataclass

# ===================== 配置区：只改这里 =====================
BASE_DIR = Path("/Users/haipei/Desktop/消防/Legal_DB/02_Laws/XF_FireLaw_2021")
TXT_PATH = BASE_DIR / "02_data" / "XF_FireLaw_2021.txt"
# ============================================================

RE_ARTICLE_LINE = re.compile(r"^[\s\u3000]*第[一二三四五六七八九十百千0-9]+条")
RE_ARTICLE_MERGED = re.compile(r"^[\s\u3000]*第[一二三四五六七八九十百千0-9]+条[ \t\u3000]+.+")
RE_ITEM_LINE = re.compile(r"^[\s\u3000]*（[一二三四五六七八九十百千0-9]+）")
RE_CHAPTER = re.compile(r"^[\s\u3000]*第[一二三四五六七八九十百千0-9]+章")
RE_SECTION = re.compile(r"^[\s\u3000]*第[一二三四五六七八九十百千0-9]+节")
RE_TRUNC = re.compile(r"(\.\.\.|…)")


@dataclass
class Issue:
    level: str   # ERROR | WARN | INFO
    line_no: int
    message: str
    excerpt: str


def strip_bom(s: str) -> str:
    return s.lstrip("\ufeff")


def excerpt_line(line: str, maxlen: int = 80) -> str:
    t = line.rstrip("\n")
    return (t[:maxlen] + "…") if len(t) > maxlen else t


def main():
    if not TXT_PATH.exists():
        print(f"[ERROR] 找不到文件：{TXT_PATH}")
        return

    text = strip_bom(TXT_PATH.read_text(encoding="utf-8", errors="ignore"))
    lines = text.splitlines()

    issues: list[Issue] = []

    # 1) 逐行检查：合并条头、截断符号、疑似章/节混入
    for i, line in enumerate(lines, start=1):
        s = line.rstrip("\n")

        if RE_TRUNC.search(s):
            issues.append(Issue(
                "WARN", i,
                "检测到疑似截断符号（... 或 …）。如果来自网页复制，可能导致条文缺失。",
                excerpt_line(s)
            ))

        if RE_ARTICLE_MERGED.match(s):
            issues.append(Issue(
                "ERROR", i,
                "条号与正文在同一行（建议改成：'第X条'独立一行，正文另起一行），否则下游拆分/列项识别更容易出错。",
                excerpt_line(s)
            ))

        # 章/节行不是错误，但提醒：如果你不想进 atomic 内容，应当保持它们独立且可过滤
        if RE_CHAPTER.match(s):
            issues.append(Issue(
                "INFO", i,
                "检测到“第X章 …”行（正常）。convert.py 可过滤掉。",
                excerpt_line(s)
            ))

        if RE_SECTION.match(s):
            issues.append(Issue(
                "INFO", i,
                "检测到“第X节 …”行（正常）。convert.py 可过滤掉。",
                excerpt_line(s)
            ))

    # 2) 检查每个“第X条”后面是否有正文（至少一行非空且不是下一个条头）
    article_lines = [(idx, lines[idx-1]) for idx in range(1, len(lines)+1) if RE_ARTICLE_LINE.match(lines[idx-1])]
    if not article_lines:
        issues.append(Issue("ERROR", 1, "未检测到任何“第X条”行。请确认 txt 是否包含条号且条号在行首。", ""))
    else:
        for k, (line_no, line_text) in enumerate(article_lines):
            # 下一行必须存在
            if line_no >= len(lines):
                issues.append(Issue(
                    "ERROR", line_no,
                    "条文标题在文件末尾，后面没有正文。",
                    excerpt_line(line_text)
                ))
                continue

            # 向下找第一行非空
            j = line_no  # next line index (1-based)
            found = None
            while j < len(lines)+1:
                if lines[j-1].strip() == "":
                    j += 1
                    continue
                found = (j, lines[j-1])
                break

            if not found:
                issues.append(Issue(
                    "ERROR", line_no,
                    "条文标题后面没有任何正文内容。",
                    excerpt_line(line_text)
                ))
                continue

            next_nonempty_no, next_nonempty_text = found
            # 如果紧跟着就是下一条条头，说明这一条正文为空
            if RE_ARTICLE_LINE.match(next_nonempty_text):
                issues.append(Issue(
                    "ERROR", line_no,
                    "条文标题后面紧跟下一条条号，当前条文正文缺失。",
                    f"{excerpt_line(line_text)}  -> next: {excerpt_line(next_nonempty_text)}"
                ))

    # 3) 检查列项是否“独立成行”
    #    如果出现 “： （一）xxx” 在同一行，提示建议换行
    for i, line in enumerate(lines, start=1):
        s = line.strip()
        if "（一）" in s and not RE_ITEM_LINE.match(line):
            # 行里包含（ 一 ）但不是以（ 一 ）开头（可能是同一行粘连）
            issues.append(Issue(
                "WARN", i,
                "检测到列项标记（如（一））不在行首。建议把每个（x）列项独立成行，避免列项拆分失败。",
                excerpt_line(line)
            ))

    # 4) 汇总输出
    # 排序：ERROR > WARN > INFO
    level_order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    issues.sort(key=lambda x: (level_order.get(x.level, 9), x.line_no))

    err = sum(1 for x in issues if x.level == "ERROR")
    warn = sum(1 for x in issues if x.level == "WARN")
    info = sum(1 for x in issues if x.level == "INFO")

    print(f"[RESULT] 文件: {TXT_PATH}")
    print(f"[RESULT] ERROR={err}, WARN={warn}, INFO={info}")
    print("-" * 80)

    if not issues:
        print("[OK] 未发现结构问题。")
        return

    for x in issues[:300]:  # 防止输出太长
        print(f"[{x.level}] L{x.line_no}: {x.message}")
        if x.excerpt:
            print(f"        {x.excerpt}")

    if len(issues) > 300:
        print(f"... 省略 {len(issues)-300} 条输出（太多了）")

    print("-" * 80)
    print("修复优先级建议：")
    print("1) 先处理 ERROR：第X条和正文同一行、条文正文缺失等")
    print("2) 再处理 WARN：列项不在行首、出现 .../… 疑似截断")
    print("3) INFO 仅提示：章/节行存在（可由 convert.py 过滤）")


if __name__ == "__main__":
    main()
