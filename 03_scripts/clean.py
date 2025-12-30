#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
clean.py —— 自动将 *.raw 转换为工程版 *.txt
特性：
- 不删除任何法律文本，只做结构整理
- 确保 “第X条” 独立成行，避免合并导致漏条
- 输出同名 .txt 文件，原始 .raw 永不覆盖
用法：
    cd Legal_DB/02_Laws/<某法律>/
    python3 03_scripts/clean.py
"""

import re
from pathlib import Path
from collections import Counter

# ==================== 正则规则 ====================

# 含“零/〇/两/数字/百/千”可匹配到 101、102 等高序条文
RE_ARTICLE = re.compile(r"(第[〇零一二三四五六七八九十百千万两\d]+条)")

# 当条号出现在句末后面，无换行（典型：xx责任。    第一百零一条）
RE_PUNCT_BEFORE_ARTICLE = re.compile(
    r"([。！？；])([\s\u3000]*)(第[〇零一二三四五六七八九十百千万两\d]+条)"
)

# 行首条号，用于统计检测
RE_ARTICLE_LINE = re.compile(r"^[\s\u3000]*(第[〇零一二三四五六七八九十百千万两\d]+条)")


# ==================== 功能函数 ====================

def ensure_article_newline(text: str):
    """句号/问号/分号后若紧跟条号，则强制换行"""
    return RE_PUNCT_BEFORE_ARTICLE.sub(r"\1\n\3", text)


def isolate_article_header(text: str):
    """
    若为 “第X条 内容…” 则拆成两行：
        第X条
        内容…
    不丢字符，不改内容，只换结构。
    """
    lines = text.splitlines()
    output = []

    for line in lines:
        m = RE_ARTICLE_LINE.match(line)
        if not m:
            output.append(line); continue

        art = m.group(1)
        rest = line[m.end():].strip()

        output.append(art)          # 条号单独占一行
        if rest: output.append(rest)

    return "\n".join(output)


def stat_articles(text: str):
    """统计条号数量与重复（用于人工快速确认是否漏条）"""
    nos = [RE_ARTICLE_LINE.match(l).group(1)
           for l in text.splitlines() if RE_ARTICLE_LINE.match(l)]
    c = Counter(nos)
    return len(nos), [k for k, v in c.items() if v > 1]


def process(raw_path: Path):
    raw = raw_path.read_text(encoding="utf-8", errors="ignore").replace("\r","")

    step1 = ensure_article_newline(raw)
    step2 = isolate_article_header(step1)

    total, duplicate = stat_articles(step2)

    out_path = raw_path.with_suffix(".txt")  # 自动生成同名 txt

    out_path.write_text(step2, encoding="utf-8")

    print(f"\n✔ 生成工程文件：{out_path.name}")
    print(f"📄 条号识别：{total} 条")
    print(f"⚠ 重复条号: {duplicate}" if duplicate else "✔ 无重复条号")
    print("🔍 建议人工抽检第1条 + 中间1条 + 最后一条确认无漏。\n")


# ==================== 主入口 ====================

def main():
    base = Path(__file__).resolve().parent.parent
    data = base / "02_data"

    raws = list(data.glob("*.raw"))
    if not raws:
        print("❌ 未找到 *.raw，请将原始法律放入 02_data/ 并命名为 <LawID>.raw")
        return

    print(f"[INFO] Found raw files → {[r.name for r in raws]}")

    for raw in raws:
        print(f"→ Cleaning {raw.name} ...")
        process(raw)

    print("\n🎉 All .raw processed → 你现在可直接运行 convert.py\n")


if __name__ == "__main__":
    main()
