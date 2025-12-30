#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消防泵房履职尽责判断清单生成管道
生成4个输出文件到 ../04_output 目录
"""

import csv
import os
import sys
import re
from typing import List, Dict, Tuple, Optional

# ==================== 配置常量 ====================

# 消防泵房相关关键词
PUMPHOUSE_KEYWORDS = [
    "消防水泵", "泵房", "消防供水", "供水设施", "消防水池", "消防水箱",
    "消火栓", "自动喷水", "稳压", "增压", "水泵接合器",
    "消防设施", "消防产品",
    "维护", "保养", "检修", "检测", "检查", "测试", "巡查", "演练",
    "完好", "有效", "正常", "可用",
    "管理", "记录", "台账", "档案", "隐患", "整改", "报告", "上报",
]

# 责任类型
DUTY_TYPES = [
    "配置存在义务",
    "持续可用义务",
    "行为履行义务",
    "响应处置义务",
    "证据留存义务",
]

# 证据类型
EVIDENCE_TYPES = [
    "现场照片",
    "维保记录",
    "打卡记录（时间/地点）",
    "IoT快照（运行/压力/液位）",
    "管理台账",
]

# ==================== 文件搜索逻辑 ====================

def get_script_dir() -> str:
    """获取脚本所在目录的绝对路径"""
    return os.path.dirname(os.path.abspath(__file__))

def find_input_csv() -> Optional[str]:
    """
    查找输入CSV文件
    优先级：
    1. 03_scripts 目录下的 XF_FireLaw_2021_atomic_v1.csv
    2. 上级目录递归搜索：同时包含 "XF" "FireLaw" "atomic" 的 .csv
    3. 上级目录递归搜索：包含 "atomic" 的 .csv
    """
    script_dir = get_script_dir()
    
    # 优先级1: 同目录下的文件
    candidate1 = os.path.join(script_dir, "XF_FireLaw_2021_atomic_v1.csv")
    if os.path.exists(candidate1):
        return candidate1
    
    # 优先级2-3: 在上级目录递归搜索
    parent_dir = os.path.dirname(script_dir)
    
    # 收集所有CSV文件
    csv_files = []
    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    # 优先级2: 同时包含 "XF" "FireLaw" "atomic"
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        if "XF" in filename and "FireLaw" in filename and "atomic" in filename:
            return csv_file
    
    # 优先级3: 包含 "atomic"
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        if "atomic" in filename:
            return csv_file
    
    return None

# ==================== 法条筛选逻辑 ====================

def safe_text_from_row(row: Dict) -> str:
    """从CSV行中提取所有文本内容"""
    return " ".join(str(v) for v in row.values() if v is not None)

def is_pumphouse_related(row: Dict) -> bool:
    """判断法条是否与消防泵房相关"""
    text = safe_text_from_row(row)
    return any(kw in text for kw in PUMPHOUSE_KEYWORDS)

# ==================== 责任判断句生成逻辑 ====================

def extract_duty_type(content: str) -> str:
    """根据内容判断责任类型（按优先级判断）"""
    
    # 优先级1: 行为履行义务（检查、检测、维护、保养、巡查、测试、演练等）
    # 这些是最常见的，优先判断
    if any(kw in content for kw in ["检查", "检测", "维护", "保养", "巡查", "测试", "演练"]):
        return "行为履行义务"
    
    # 优先级2: 证据留存义务（记录、台账、档案、存档等）
    if any(kw in content for kw in ["记录", "台账", "档案", "存档", "备查", "建立档案"]):
        return "证据留存义务"
    
    # 优先级3: 响应处置义务（报告、上报、整改、消除等）
    if any(kw in content for kw in ["报告", "上报", "整改", "消除", "通知", "报警"]):
        return "响应处置义务"
    
    # 优先级4: 持续可用义务（保持、确保、完好、有效、正常、可用、畅通等）
    if any(kw in content for kw in ["保持", "确保", "完好", "有效", "正常", "可用", "畅通"]):
        return "持续可用义务"
    
    # 优先级5: 配置存在义务（配置、设置、配备、建立、安装等）
    if any(kw in content for kw in ["配置", "设置", "配备", "建立", "安装"]):
        return "配置存在义务"
    
    # 默认
    return "行为履行义务"

def generate_duty_judgment(content: str, article_no: str) -> str:
    """生成责任判断句：是否 + 行为/状态 + 对象"""
    
    # 提取关键对象（优先匹配更具体的）
    obj = None
    if "消防水泵" in content or "水泵" in content:
        obj = "消防水泵"
    elif "稳压泵" in content or "稳压" in content:
        obj = "稳压泵"
    elif "消防水池" in content or "水池" in content:
        obj = "消防水池"
    elif "消防水箱" in content or "水箱" in content:
        obj = "消防水箱"
    elif "泵房" in content:
        obj = "消防泵房"
    elif "消防供水" in content or "供水设施" in content:
        obj = "消防供水设施"
    else:
        obj = "消防泵房设施"  # 默认使用泵房相关表述
    
    # 提取关键行为/状态（按优先级）
    behavior = None
    if "维护" in content and "保养" in content:
        behavior = "定期维护保养"
    elif "维护" in content or "保养" in content:
        behavior = "定期维护保养"
    elif "检查" in content and "检测" in content:
        behavior = "定期检查检测"
    elif "检查" in content or "检测" in content:
        behavior = "定期检查"
    elif "巡查" in content:
        behavior = "每日巡查"
    elif "测试" in content:
        behavior = "定期测试"
    elif "配置" in content or "设置" in content or "配备" in content:
        behavior = "已配置"
    elif "记录" in content or "台账" in content:
        behavior = "建立记录台账"
    elif "完好" in content or "有效" in content:
        behavior = "保持完好有效"
    elif "整改" in content or "消除" in content:
        behavior = "及时整改消除"
    elif "报告" in content or "上报" in content:
        behavior = "及时报告上报"
    elif "演练" in content:
        behavior = "组织演练"
    
    # 生成判断句
    if behavior:
        return f"是否{behavior}{obj}"
    else:
        return f"是否已履行{obj}相关义务"

def get_evidence_requirements(duty_type: str, content: str) -> str:
    """根据责任类型和内容确定最低证据要求"""
    evidence_list = []
    
    if duty_type == "配置存在义务":
        evidence_list.extend(["现场照片", "管理台账"])
    elif duty_type == "持续可用义务":
        evidence_list.extend(["现场照片", "IoT快照（运行/压力/液位）"])
    elif duty_type == "行为履行义务":
        if "巡查" in content:
            evidence_list.extend(["打卡记录（时间/地点）", "管理台账"])
        elif "维护" in content or "保养" in content:
            evidence_list.extend(["维保记录", "现场照片"])
        else:
            evidence_list.extend(["维保记录", "管理台账"])
    elif duty_type == "响应处置义务":
        evidence_list.extend(["管理台账", "现场照片"])
    elif duty_type == "证据留存义务":
        evidence_list.extend(["管理台账", "维保记录"])
    
    # 去重并返回
    evidence_list = list(dict.fromkeys(evidence_list))  # 保持顺序的去重
    return "+".join(evidence_list) if evidence_list else "管理台账"

def extract_rulebook_entries(filtered_rows: List[Dict]) -> List[Dict]:
    """从筛选出的法条中提取责任判断清单条目"""
    rulebook = []
    seen_judgments = set()  # 去重
    
    for row in filtered_rows:
        content = row.get('content_cn', '')
        article_no = row.get('article_no', '')
        
        # 跳过空内容
        if not content or not content.strip():
            continue
        
        # 生成责任类型
        duty_type = extract_duty_type(content)
        
        # 生成判断句
        judgment = generate_duty_judgment(content, article_no)
        
        # 根据判断句本身调整责任类型（更准确）
        if "已配置" in judgment or "配置" in judgment:
            duty_type = "配置存在义务"
        elif "保持" in judgment or "完好" in judgment or "有效" in judgment:
            duty_type = "持续可用义务"
        elif "记录" in judgment or "台账" in judgment:
            duty_type = "证据留存义务"
        elif "报告" in judgment or "上报" in judgment or "整改" in judgment or "消除" in judgment:
            duty_type = "响应处置义务"
        elif "检查" in judgment or "检测" in judgment or "维护" in judgment or "保养" in judgment or "巡查" in judgment:
            duty_type = "行为履行义务"
        
        # 去重：如果判断句已存在，跳过
        if judgment in seen_judgments:
            continue
        seen_judgments.add(judgment)
        
        # 获取证据要求
        evidence = get_evidence_requirements(duty_type, content)
        
        rulebook.append({
            '责任类型': duty_type,
            '责任判断句': judgment,
            '最低证据要求': evidence
        })
    
    return rulebook

# ==================== 文件生成逻辑 ====================

def generate_pumphouse_law_subset(input_csv: str, output_csv: str) -> int:
    """生成消防泵房相关法条子集"""
    print(f"\n[步骤1] 筛选消防泵房相关法条...")
    
    with open(input_csv, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("[ERROR] CSV 无表头")
            return 0
        
        rows = list(reader)
        fieldnames = list(reader.fieldnames)
    
    # 添加新列
    new_col = "是否适用于消防泵房"
    if new_col not in fieldnames:
        fieldnames.append(new_col)
    
    # 标记所有行（筛选出相关的）
    filtered = []
    for row in rows:
        if is_pumphouse_related(row):
            row[new_col] = "是"
            filtered.append(row)
        else:
            row[new_col] = "否"
    
    # 写入输出（只包含相关的行，但即使为空也输出表头）
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if filtered:
            writer.writerows(filtered)
    
    print(f"  ✓ 已生成: {output_csv}")
    print(f"  ✓ 命中条数: {len(filtered)}")
    return len(filtered)

def generate_rulebook(filtered_rows: List[Dict], output_csv: str):
    """生成责任判断清单"""
    print(f"\n[步骤2] 生成责任判断清单...")
    
    rulebook = extract_rulebook_entries(filtered_rows)
    
    # 写入CSV
    fieldnames = ['责任类型', '责任判断句', '最低证据要求']
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if rulebook:
            writer.writerows(rulebook)
    
    print(f"  ✓ 已生成: {output_csv}")
    print(f"  ✓ 清单条目数: {len(rulebook)}")
    return rulebook

def generate_evidence_chain_sample(rulebook: List[Dict], output_md: str):
    """生成证据链样例"""
    print(f"\n[步骤3] 生成证据链样例...")
    
    # 选择一个典型的责任判断句作为示例
    sample_entry = None
    for entry in rulebook:
        if "维护" in entry['责任判断句'] or "检查" in entry['责任判断句']:
            sample_entry = entry
            break
    if not sample_entry and rulebook:
        sample_entry = rulebook[0]
    
    if not sample_entry:
        sample_entry = {
            '责任类型': '行为履行义务',
            '责任判断句': '是否定期维护保养消防水泵',
            '最低证据要求': '维保记录+现场照片'
        }
    
    content = f"""# 消防泵房履职尽责证据链样例

## 场景描述
假设某单位于2024年1月15日对消防泵房进行月度维护保养。

## 责任判断
**判断项**: {sample_entry['责任判断句']}  
**责任类型**: {sample_entry['责任类型']}  
**最低证据要求**: {sample_entry['最低证据要求']}

## 证据链时间线

### 2024-01-15 09:00
**行为**: 维保人员到达消防泵房  
**证据**: 打卡记录（时间/地点）- 显示维保人员张三于09:00在消防泵房打卡

### 2024-01-15 09:05-09:30
**行为**: 检查消防水泵运行状态、压力表读数、液位计读数  
**设备状态**: 
- 主泵运行正常，压力0.65MPa
- 稳压泵运行正常，压力0.50MPa
- 消防水池液位：2.8米（正常范围）
- 消防水箱液位：1.2米（正常范围）

**证据**: 
- IoT快照（运行/压力/液位）- 系统自动记录09:15时刻的运行参数
- 现场照片 - 维保人员拍摄的压力表、液位计读数照片

### 2024-01-15 09:30-10:00
**行为**: 对消防水泵进行润滑保养，检查电气连接  
**设备状态**: 完成保养后，设备运行正常

**证据**: 
- 现场照片 - 保养过程照片（润滑点、电气连接检查）
- 维保记录 - 详细记录保养内容、发现的问题、处理措施

### 2024-01-15 10:00
**行为**: 填写维保记录表，签字确认  
**证据**: 
- 维保记录 - 纸质记录表，包含维保人员签名、日期
- 管理台账 - 电子台账系统同步更新本次维保记录

## 证据链完整性评估

| 证据类型 | 是否提供 | 备注 |
|---------|---------|------|
| 现场照片 | ✓ | 包含压力表、液位计、保养过程照片 |
| 维保记录 | ✓ | 纸质记录+电子台账双重记录 |
| 打卡记录（时间/地点） | ✓ | 系统自动记录 |
| IoT快照（运行/压力/液位） | ✓ | 系统自动记录关键参数 |
| 管理台账 | ✓ | 电子台账系统记录 |

## 履职尽责结论
基于上述证据链，该单位在2024年1月15日的消防泵房维护保养工作中：
- ✓ 按时履行了维护保养义务
- ✓ 完整记录了维护保养过程
- ✓ 保留了必要的证据材料
- ✓ 符合《中华人民共和国消防法》相关要求

**结论**: 本次维护保养工作履职尽责，证据链完整。
"""
    
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ 已生成: {output_md}")

def generate_report_template(output_md: str):
    """生成对外结论报告模板"""
    print(f"\n[步骤4] 生成对外结论报告模板...")
    
    content = f"""# 消防泵房履职尽责分析报告

**报告编号**: [自动生成]  
**报告日期**: [填写日期]  
**分析对象**: [单位名称]  
**分析期间**: [起始日期] 至 [终止日期]

---

## 一、报告目的

本报告旨在依据《中华人民共和国消防法》（2021修正）及相关消防技术标准，对[单位名称]在指定期间内消防泵房相关消防安全职责的履行情况进行客观分析，评估其履职尽责情况，为消防安全管理提供参考依据。

---

## 二、分析依据

### 2.1 法律依据
- 《中华人民共和国消防法》（2021修正）
- 《建筑消防设施维护管理标准》（GB 25201-2010）
- 其他相关消防法律法规及技术标准

### 2.2 记录依据
本报告基于以下记录材料进行分析：
- 消防泵房维保记录（[期间]）
- 消防设施检查记录（[期间]）
- 消防设施检测报告（[期间]）
- 管理台账及档案材料
- 现场检查照片及视频资料
- IoT系统运行数据记录（如适用）

---

## 三、履职尽责分析结论

### 3.1 配置存在义务履行情况

**分析项**: 是否已配置消防水泵、稳压泵、消防水池、消防水箱等必要设施

**分析结果**: 
[ ] 已完全履行 - 所有必要设施均已配置到位
[ ] 部分履行 - 存在部分设施缺失或配置不符合标准
[ ] 未履行 - 存在重大配置缺失

**具体情况**: 
[在此详细说明配置情况，包括设施清单、配置位置、技术参数等]

---

### 3.2 持续可用义务履行情况

**分析项**: 是否保持消防泵房设施完好有效、正常运行

**分析结果**: 
[ ] 已完全履行 - 设施持续保持完好有效状态
[ ] 部分履行 - 存在部分设施故障或异常情况
[ ] 未履行 - 存在重大故障或长期停用情况

**具体情况**: 
[在此详细说明设施运行状态，包括正常运行时间、故障记录、维修情况等]

---

### 3.3 行为履行义务履行情况

**分析项**: 是否定期进行维护保养、检查检测、巡查等工作

**分析结果**: 
[ ] 已完全履行 - 按标准要求完成所有维护检查工作
[ ] 部分履行 - 存在部分工作未按标准执行或执行不到位
[ ] 未履行 - 存在重大工作缺失或长期未执行

**具体情况**: 
[在此详细说明维护检查工作执行情况，包括工作频次、工作内容、执行人员等]

---

### 3.4 响应处置义务履行情况

**分析项**: 是否及时报告隐患、整改问题、响应异常情况

**分析结果**: 
[ ] 已完全履行 - 及时报告并整改所有发现的问题
[ ] 部分履行 - 存在部分问题未及时报告或整改
[ ] 未履行 - 存在重大隐患未报告或未整改

**具体情况**: 
[在此详细说明隐患报告和整改情况，包括发现的问题、报告时间、整改措施、整改结果等]

---

### 3.5 证据留存义务履行情况

**分析项**: 是否建立并保存完整的记录台账、档案材料

**分析结果**: 
[ ] 已完全履行 - 记录台账完整、档案材料齐全
[ ] 部分履行 - 存在部分记录缺失或档案不完整
[ ] 未履行 - 存在重大记录缺失或档案管理混乱

**具体情况**: 
[在此详细说明记录台账和档案管理情况，包括记录完整性、保存方式、可追溯性等]

---

## 四、综合评估结论

### 4.1 总体评价
[ ] 履职尽责情况良好
[ ] 履职尽责情况一般，存在改进空间
[ ] 履职尽责情况较差，存在重大风险

### 4.2 主要问题
1. [问题1描述]
2. [问题2描述]
3. [问题3描述]

### 4.3 改进建议
1. [建议1]
2. [建议2]
3. [建议3]

---

## 五、风险提示与免责声明

### 5.1 风险提示
1. 本报告基于提供的历史记录材料进行分析，如记录材料不完整或不准确，可能影响分析结论的准确性。
2. 消防安全管理是一个持续的过程，本报告仅反映指定期间内的情况，不排除期间外存在其他问题。
3. 本报告不替代现场消防安全检查，建议结合现场实际情况综合判断。

### 5.2 免责声明
1. 本报告仅作为消防安全管理参考，不构成法律意见或专业建议。
2. 报告编制方不对因使用本报告而产生的任何直接或间接损失承担责任。
3. 报告使用者应结合实际情况，自行判断并承担相应责任。
4. 本报告的有效性受限于提供材料的真实性和完整性。

---

## 六、附件清单

1. 消防泵房履职尽责判断清单
2. 证据链分析材料
3. 相关记录台账复印件
4. 现场检查照片（如适用）

---

**报告编制**: [编制人员]  
**审核**: [审核人员]  
**批准**: [批准人员]  

**报告日期**: [日期]  
**报告版本**: V1.0
"""
    
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ 已生成: {output_md}")

# ==================== 主流程 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("消防泵房履职尽责判断清单生成管道")
    print("=" * 60)
    
    # 1. 查找输入CSV文件
    print("\n[步骤0] 查找输入CSV文件...")
    input_csv = find_input_csv()
    
    if not input_csv:
        print("\n[ERROR] 未找到输入CSV文件！")
        print("\n请检查以下位置：")
        print("  1. 03_scripts 目录下的 XF_FireLaw_2021_atomic_v1.csv")
        print("  2. 上级目录及其子目录中同时包含 'XF' 'FireLaw' 'atomic' 的 .csv 文件")
        print("  3. 上级目录及其子目录中包含 'atomic' 的 .csv 文件")
        print("\n您可以使用以下命令查找：")
        script_dir = get_script_dir()
        parent_dir = os.path.dirname(script_dir)
        print(f"  find {parent_dir} -name '*atomic*.csv' -type f")
        return 1
    
    print(f"  ✓ 找到输入文件: {os.path.abspath(input_csv)}")
    
    # 2. 确定输出目录
    script_dir = get_script_dir()
    output_dir = os.path.join(os.path.dirname(script_dir), "04_output")
    os.makedirs(output_dir, exist_ok=True)
    print(f"  ✓ 输出目录: {os.path.abspath(output_dir)}")
    
    # 3. 读取输入CSV
    print(f"\n[步骤0.5] 读取输入CSV...")
    with open(input_csv, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("[ERROR] CSV 无表头")
            return 2
        all_rows = list(reader)
    
    print(f"  ✓ 读取到 {len(all_rows)} 条法条")
    
    # 筛选消防泵房相关法条
    filtered_rows = [row for row in all_rows if is_pumphouse_related(row)]
    print(f"  ✓ 筛选出 {len(filtered_rows)} 条相关法条")
    
    # 4. 生成输出文件
    output_files = {
        'pumphouse_law_subset': os.path.join(output_dir, 'pumphouse_law_subset_v1.csv'),
        'rulebook': os.path.join(output_dir, 'pumphouse_rulebook_v1.csv'),
        'evidence_chain': os.path.join(output_dir, 'evidence_chain_sample.md'),
        'report_template': os.path.join(output_dir, 'duty_conclusion_report_template.md'),
    }
    
    # 生成文件1: 法条子集
    generate_pumphouse_law_subset(input_csv, output_files['pumphouse_law_subset'])
    
    # 生成文件2: 责任判断清单
    rulebook = extract_rulebook_entries(filtered_rows)
    generate_rulebook(filtered_rows, output_files['rulebook'])
    
    # 生成文件3: 证据链样例
    generate_evidence_chain_sample(rulebook, output_files['evidence_chain'])
    
    # 生成文件4: 报告模板
    generate_report_template(output_files['report_template'])
    
    # 5. 完成提示
    print("\n" + "=" * 60)
    print("✓ 所有文件生成完成！")
    print("=" * 60)
    print("\n生成的文件：")
    for key, path in output_files.items():
        print(f"  - {os.path.basename(path)}")
    print(f"\n输出目录: {os.path.abspath(output_dir)}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

