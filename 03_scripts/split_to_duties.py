import csv
import re
import hashlib
from pathlib import Path

# ============================================================
# 配置区（你只需要改这里 4 行）
# ============================================================

BASE_DIR = Path("/Users/haipei/Desktop/消防/Legal_DB/02_Laws")  # 你给的根目录
LAW_DIR = "XF_FireLaw_2021"                                   # 当前法律项目文件夹名
LAW_ID = "XF_FireLaw_2021"                                    # law_id（建议写死）

INPUT_CSV = BASE_DIR / LAW_DIR / "04_output" / "XF_FireLaw_2021_atomic_v1.csv"
OUTPUT_CSV = BASE_DIR / LAW_DIR / "04_output" / "XF_FireLaw_2021_atoms_v1.csv"

FIELD_ARTICLE_NO = "article_no"
FIELD_CONTENT = "content_cn"  # 如果你的内容列不是 content_cn，请改成 content/text/clause_text 等

# ============================================================
# 拆分/识别规则（一般不用改）
# ============================================================

RE_ITEM_MARKER = re.compile(r"(（[一二三四五六七八九十百千0-9]+）)")  # （一）（二）...
RE_WS = re.compile(r"[ \t]+")
SPLIT_PRIMARY = re.compile(r"[；;\n]+")  # 先按分号/换行拆
SENT_SPLIT = re.compile(r"。+")         # 长句再按句号拆句

# 过滤混入文本的章/节标题（即便 v1 没章节字段，文本里也可能有）
RE_CHAPTER_LINE = re.compile(r"^第[一二三四五六七八九十百千0-9]+章.*$")
RE_SECTION_LINE = re.compile(r"^第[一二三四五六七八九十百千0-9]+节.*$")

# Scope 识别：总述句/引出句常见信号
SCOPE_HINTS = ("下列", "如下", "包括以下", "包括下列", "履行下列", "应当履行下列", "职责如下", "包括：", "如下：")

# ============================================================
# 基础工具
# ============================================================

CN_NUM = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNIT = {"十": 10, "百": 100, "千": 1000}

def norm(s: str) -> str:
    s = (s or "").replace("\u3000", " ").replace("\r\n", "\n").replace("\r", "\n").strip()
    s = RE_WS.sub(" ", s)
    return s

def filter_heading_lines(text: str) -> str:
    lines = []
    for line in (text or "").splitlines():
        t = line.strip()
        if not t:
            continue
        if RE_CHAPTER_LINE.match(t):
            continue
        if RE_SECTION_LINE.match(t):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def cn_to_int(cn: str) -> int:
    """
    简单可靠的中文数字转 int（支持：十/百/千；也支持阿拉伯数字）
    例：十七->17，一百零二->102，第三条/第17条 都能处理
    """
    cn = (cn or "").strip()
    if not cn:
        return 0
    # 先尝试阿拉伯数字
    m = re.search(r"\d+", cn)
    if m:
        return int(m.group())

    # 只保留中文数字与单位
    s = "".join([ch for ch in cn if ch in CN_NUM or ch in CN_UNIT])
    if not s:
        return 0

    total = 0
    unit = 1
    # 从右到左处理
    for ch in reversed(s):
        if ch in CN_NUM:
            total += CN_NUM[ch] * unit
        else:
            unit = CN_UNIT[ch]
            if unit < 10:
                unit = 10
    # 处理“十七”这种前面省略“一”
    if "十" in s and s[0] == "十":
        total += 10
    return total

def extract_article_idx(article_no: str) -> int:
    # 从 “第十七条” 提取 17
    m = re.search(r"第(.+?)条", article_no)
    if m:
        return cn_to_int(m.group(1))
    return cn_to_int(article_no)

def strip_item_marker_prefix(s: str) -> str:
    return re.sub(r"^（[一二三四五六七八九十百千0-9]+）\s*", "", (s or "")).strip()

def make_scope_id(law_id: str, article_no: str, scope_idx: int, scope_text: str) -> str:
    base = f"{law_id}|{article_no}|S{scope_idx}|{scope_text}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]
    safe_article = re.sub(r"[^A-Za-z0-9一二三四五六七八九十百千0-9]+", "", article_no)
    return f"{law_id}_{safe_article}_S{scope_idx:02d}_{h}"

def make_duty_id(law_id: str, article_no: str, duty_no: str, duty_text: str) -> str:
    base = f"{law_id}|{article_no}|{duty_no}|{duty_text}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]
    safe_article = re.sub(r"[^A-Za-z0-9一二三四五六七八九十百千0-9]+", "", article_no)
    safe_duty = re.sub(r"[^0-9_]+", "", duty_no)
    return f"{law_id}_{safe_article}_{safe_duty}_{h}"

# ============================================================
# Scope 识别逻辑
# ============================================================

def is_scope_intro(text: str) -> bool:
    """
    判定“总述引出句”：不当义务，但提供主体/范围
    规则：含下列/如下等，或以冒号结尾并紧接列表结构（由外层保证）
    """
    t = norm(text)
    if not t:
        return False
    if t.endswith("：") or t.endswith(":"):
        return True
    for kw in SCOPE_HINTS:
        if kw in t:
            return True
    return False

def split_by_items_with_preface(text: str):
    """返回 (preface, items)"""
    t = text.strip()
    matches = list(RE_ITEM_MARKER.finditer(t))
    if not matches:
        return "", []
    first = matches[0].start()
    preface = t[:first].strip()
    items = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(t)
        seg = t[start:end].strip()
        if seg:
            items.append(seg)
    return preface, items

def split_by_punct(text: str):
    """
    非列项结构时：按分号/换行拆块；块太长再按句号拆
    """
    t = (text or "").strip()
    if not t:
        return []
    chunks = [c.strip() for c in SPLIT_PRIMARY.split(t) if c.strip()]
    out = []
    for c in chunks:
        if len(c) >= 80 and "。" in c:
            sents = [x.strip() for x in SENT_SPLIT.split(c) if x.strip()]
            for s in sents:
                out.append(s + "。")
        else:
            out.append(c)
    return out

def clean_duties(duties):
    duties = [norm(d) for d in duties if norm(d)]
    duties = [d for d in duties if len(d) >= 6]  # 过短通常无信息
    return duties

# ============================================================
# 主流程：每条法条 -> scope + duties
# ============================================================

def process_article(article_no: str, content: str):
    """返回 scopes(list[dict]), duties(list[dict])"""
    article_no = norm(article_no)
    article_idx = extract_article_idx(article_no)
    text = filter_heading_lines(content)

    scopes = []
    duties = []

    # Case 1: 有列项（（一）（二）...）
    preface, items = split_by_items_with_preface(text)
    scope_id = ""

    if items:
        # 处理 preface：如果是引出句，做 scope 节点
        preface = norm(preface)
        if preface and is_scope_intro(preface):
            scope_idx = 1
            scope_id = make_scope_id(LAW_ID, article_no, scope_idx, preface)
            scopes.append({
                "law_id": LAW_ID,
                "article_no": article_no,
                "article_idx": article_idx,
                "scope_idx": scope_idx,
                "scope_id": scope_id,
                "scope_text": preface
            })
        else:
            # preface 不是引出句：它可能本身包含义务
            if preface:
                for j, d in enumerate(clean_duties(split_by_punct(preface)), start=1):
                    duty_no = f"{article_idx}_{j}" if article_idx else f"{article_no}_{j}"
                    duties.append({
                        "law_id": LAW_ID,
                        "article_no": article_no,
                        "article_idx": article_idx,
                        "duty_idx": j,
                        "duty_no": duty_no,
                        "scope_id": "",
                        "duty_text": d
                    })

        # 列项每条生成 duty，继承 scope_id（如有）
        duty_start = len(duties) + 1
        for item in items:
            body = strip_item_marker_prefix(item)
            parts = clean_duties(split_by_punct(body))
            if not parts:
                parts = [norm(body)] if norm(body) else []
            for p in parts:
                duty_idx = duty_start
                duty_no = f"{article_idx}_{duty_idx}" if article_idx else f"{article_no}_{duty_idx}"
                duties.append({
                    "law_id": LAW_ID,
                    "article_no": article_no,
                    "article_idx": article_idx,
                    "duty_idx": duty_idx,
                    "duty_no": duty_no,
                    "scope_id": scope_id,
                    "duty_text": p
                })
                duty_start += 1

        return scopes, duties

    # Case 2: 无列项结构：按标点拆成 duties（无 scope）
    parts = clean_duties(split_by_punct(text))
    if not parts:
        parts = [norm(text)] if norm(text) else []

    for i, d in enumerate(parts, start=1):
        duty_no = f"{article_idx}_{i}" if article_idx else f"{article_no}_{i}"
        duties.append({
            "law_id": LAW_ID,
            "article_no": article_no,
            "article_idx": article_idx,
            "duty_idx": i,
            "duty_no": duty_no,
            "scope_id": "",
            "duty_text": d
        })

    return scopes, duties

# ============================================================
# 入口
# ============================================================

def main():
    if not INPUT_CSV.exists():
        print(f"[ERROR] 找不到输入文件: {INPUT_CSV}")
        return

    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if FIELD_ARTICLE_NO not in fieldnames:
        print(f"[ERROR] 输入CSV缺少字段: {FIELD_ARTICLE_NO}")
        print(f"[INFO] 当前字段: {fieldnames}")
        return
    if FIELD_CONTENT not in fieldnames:
        print(f"[ERROR] 输入CSV缺少字段: {FIELD_CONTENT}")
        print(f"[INFO] 当前字段: {fieldnames}")
        return

    fields = [
        "row_type",        # scope | duty
        "law_id",
        "article_no",
        "article_idx",
        "scope_id",        # for scope rows: its own id; for duty rows: parent scope id (may be empty)
        "scope_idx",       # only for scope rows
        "scope_text",      # only for scope rows
        "duty_id",         # only for duty rows
        "duty_idx",        # only for duty rows
        "duty_no",         # only for duty rows (uses underscore)
        "duty_text"        # only for duty rows
    ]

    total_articles = 0
    total_scopes = 0
    total_duties = 0

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fields)
        writer.writeheader()

        for r in rows:
            article_no = r.get(FIELD_ARTICLE_NO, "")
            content = r.get(FIELD_CONTENT, "") or ""
            if not norm(article_no) or not content.strip():
                continue

            total_articles += 1
            scopes, duties = process_article(article_no, content)

            for s in scopes:
                writer.writerow({
                    "row_type": "scope",
                    "law_id": s.get("law_id", ""),
                    "article_no": s.get("article_no", ""),
                    "article_idx": s.get("article_idx", ""),
                    "scope_id": s.get("scope_id", ""),
                    "scope_idx": s.get("scope_idx", ""),
                    "scope_text": s.get("scope_text", ""),
                    "duty_id": "",
                    "duty_idx": "",
                    "duty_no": "",
                    "duty_text": ""
                })
                total_scopes += 1

            for d in duties:
                duty_id = make_duty_id(LAW_ID, d["article_no"], d["duty_no"], d["duty_text"])
                writer.writerow({
                    "row_type": "duty",
                    "law_id": d.get("law_id", ""),
                    "article_no": d.get("article_no", ""),
                    "article_idx": d.get("article_idx", ""),
                    "scope_id": d.get("scope_id", ""),
                    "scope_idx": "",
                    "scope_text": "",
                    "duty_id": duty_id,
                    "duty_idx": d.get("duty_idx", ""),
                    "duty_no": d.get("duty_no", ""),
                    "duty_text": d.get("duty_text", "")
                })
                total_duties += 1

    print(f"[OK] 输出: {OUTPUT_CSV}")
    print(f"[OK] 法条数: {total_articles} | scope数: {total_scopes} | duty数: {total_duties}")
    print("[NEXT] 下一步：只在 duties 表上做五类义务映射；scope 负责主体/范围继承，不做映射。")

if __name__ == "__main__":
    main()
