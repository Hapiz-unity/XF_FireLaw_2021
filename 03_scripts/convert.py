import re
import csv
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent
TXT_DIR = BASE_DIR / "02_data"
OUTPUT_DIR = BASE_DIR / "04_output"

INPUT_TXT_NAME = "XF_FireLaw_2021.txt"
OUTPUT_CSV_NAME = "XF_FireLaw_2021_atomic_v1.csv"

LAW_NAME = "中华人民共和国消防法"
VERSION = "2021修正"

CHAPTER_LINE_PATTERN = re.compile(r"^[\s\u3000]*第[一二三四五六七八九十百千0-9]+章.*$")
SECTION_LINE_PATTERN = re.compile(r"^[\s\u3000]*第[一二三四五六七八九十百千0-9]+节.*$")
ARTICLE_LINE_PATTERN = re.compile(r"^[\s\u3000]*(第[一二三四五六七八九十百千0-9]+条)(.*)$")


def load_txt():
    txt_path = TXT_DIR / INPUT_TXT_NAME
    if not txt_path.exists():
        raise FileNotFoundError(f"未找到文本文件：{txt_path}")
    return txt_path.read_text(encoding="utf-8", errors="ignore")


def extract_articles(text: str):
    lines = text.splitlines()
    articles = []
    current_no = None
    buffer = []

    for line in lines:
        stripped = line.strip()
        m = ARTICLE_LINE_PATTERN.match(line)

        if m:
            if current_no is not None:
                articles.append((current_no, "\n".join(buffer).strip()))
            current_no = m.group(1)
            rest = m.group(2).strip()
            buffer = []
            if rest:
                buffer.append(rest)
        else:
            if current_no is not None:
                buffer.append(line)

    if current_no:
        articles.append((current_no, "\n".join(buffer).strip()))

    return articles


def clean_content(raw: str):
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append(line)
            continue
        if CHAPTER_LINE_PATTERN.match(stripped):
            continue
        if SECTION_LINE_PATTERN.match(stripped):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def write_csv(matches):
    OUTPUT_DIR.mkdir(exist_ok=True)
    csv_path = OUTPUT_DIR / OUTPUT_CSV_NAME

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["law_name", "version", "article_no", "content_cn", "content_en", "notes"])
        for no, content in matches:
            writer.writerow([LAW_NAME, VERSION, no, clean_content(content), "", ""])

    print(f"[✔] 输出成功 → {csv_path}")
    print(f"[i] 共 {len(matches)} 条")


def main():
    print("[INFO] 加载文本…")
    text = load_txt()
    print("[INFO] 拆条中…")
    matches = extract_articles(text)
    print(f"[INFO] 拆出 {len(matches)} 条")
    write_csv(matches)


if __name__ == "__main__":
    main()
