import csv
import os
import sys
from typing import List

# Usage:
#   python filter_pumphouse_law.py [input_csv] [output_csv]
# Default:
#   input_csv  = XF_FireLaw_2021_atomic_v1.csv (same dir as this script)
#   output_csv = pumphouse_law_subset_v1.csv   (same dir as this script)

KEYWORDS: List[str] = [
    "消防水泵", "泵房", "消防供水", "供水设施", "消防水池", "消防水箱",
    "消火栓", "自动喷水", "稳压", "增压", "水泵接合器",
    "消防设施", "消防产品",
    "维护", "保养", "检修", "检测", "检查", "测试", "巡查", "演练",
    "完好", "有效", "正常", "可用",
    "管理", "记录", "台账", "档案", "隐患", "整改", "报告", "上报",
]

def script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def resolve_path(p: str) -> str:
    if os.path.isabs(p):
        return p
    return os.path.join(script_dir(), p)

def safe_text_from_row(row: dict) -> str:
    return " ".join(str(v) for v in row.values() if v is not None)

def main() -> int:
    input_arg = sys.argv[1] if len(sys.argv) >= 2 else "XF_FireLaw_2021_atomic_v1.csv"
    output_arg = sys.argv[2] if len(sys.argv) >= 3 else "pumphouse_law_subset_v1.csv"

    input_path = resolve_path(input_arg)
    output_path = resolve_path(output_arg)

    if not os.path.exists(input_path):
        print(f"[ERROR] 找不到输入文件: {input_path}")
        return 1

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("[ERROR] CSV 无表头")
            return 2
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    new_col = "是否适用于消防泵房"
    if new_col not in fieldnames:
        fieldnames.append(new_col)

    filtered = []
    for r in rows:
        text = safe_text_from_row(r)
        if any(k in text for k in KEYWORDS):
            r[new_col] = "是"
            filtered.append(r)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered)

    print(f"已生成泵房相关法条子集：{output_path}，共 {len(filtered)} 条")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())