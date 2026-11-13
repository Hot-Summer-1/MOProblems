"""
merge_temp.py - 将 temp.json 中新加入的比赛合并到 problems/{source}/{name}/info.json

用法: python tools/merge_temp.py

temp.json 格式（原始 API 响应）:
{
  "code": 0,
  "msg": "查询成功",
  "data": {
    "total": N,
    "rows": [
      {
        "id": 1009,
        "name": "国际数学奥林匹克",
        "short": "IMO",
        "years": ["2026", "2025", ""],
        "source": ["abroad"],
        ...
      }
    ]
  }
}

info.json 格式（source/name 由目录路径推断）:
{
  "display_name": "国际数学奥林匹克",
  "years": {
    "2026": {
      "count": 0,
      "no_problem_content": true,
      "begin_index": 0
    },
    ...
  }
}
"""

import json
import os
import sys
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_FILE = os.path.join(BASE_DIR, "temp.json")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")


def convert_item(raw):
    """将原始 API 格式的单条记录转换为 info.json 的元数据"""
    source_val = raw.get("source", [])
    if isinstance(source_val, list):
        source_val = source_val[0] if source_val else ""
    elif source_val:
        source_val = str(source_val)
    else:
        source_val = ""

    seen = set()
    years = []
    for year in raw.get("years", []):
        if not isinstance(year, str) or not year.strip() or year in seen:
            continue
        seen.add(year)
        years.append(year)

    return {
        "name": raw.get("short", ""),
        "display_name": raw.get("name", ""),
        "source": source_val,
        "years": years,
    }


def make_year_entry():
    """返回一个年份条目的标准结构"""
    return OrderedDict([
        ("count", 0),
        ("no_problem_content", True),
        ("begin_index", 0)
    ])


def load_info(info_path):
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f, object_pairs_hook=OrderedDict)

    if "years" not in info and all(isinstance(v, dict) for v in info.values()):
        raise ValueError(
            f"{info_path} 仍是旧版扁平结构，请先运行迁移脚本转换为新版结构"
        )
    return info


def merge_info(item):
    source = item["source"]
    name = item["name"]
    if not source or not name:
        print(f"  [!] 跳过（缺少 source 或 name）: {item['display_name']}")
        return None

    folder_path = os.path.join(PROBLEMS_DIR, source, name)
    os.makedirs(folder_path, exist_ok=True)
    info_path = os.path.join(folder_path, "info.json")

    if os.path.exists(info_path):
        info = load_info(info_path)
        years = info.get("years", OrderedDict())
    else:
        years = OrderedDict()

    added = 0
    for year in item["years"]:
        if year not in years:
            years[year] = make_year_entry()
            added += 1

    ordered = OrderedDict()
    for year in item["years"]:
        ordered[year] = years[year]
    for year, entry in years.items():
        if year not in ordered:
            ordered[year] = entry

    new_info = OrderedDict([
        ("display_name", item["display_name"]),
        ("years", ordered),
    ])

    with open(info_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(new_info, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return info_path, added


def main():
    if not os.path.exists(TEMP_FILE):
        print(f"[错误] 未找到 {TEMP_FILE}")
        sys.exit(1)

    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        temp_data = json.load(f)

    new_rows = temp_data.get("data", {}).get("rows", [])
    if not new_rows:
        print("[提示] temp.json 中没有新比赛数据")
        sys.exit(0)

    converted = [convert_item(r) for r in new_rows]
    print(f"[转换] temp.json 中共 {len(converted)} 条记录")

    created = 0
    updated = 0
    for item in converted:
        info_path = os.path.join(PROBLEMS_DIR, item["source"], item["name"], "info.json")
        was_existing = os.path.exists(info_path)

        result = merge_info(item)
        if result is None:
            continue

        _, added = result
        if was_existing:
            updated += 1
            print(f"  [~] 更新: {item['display_name']} ({item['source']}/{item['name']})，新增 {added} 个年份")
        else:
            created += 1
            print(f"  [+] 新增: {item['display_name']} ({item['source']}/{item['name']})，共 {added} 个年份")

    print(f"\n[完成] 新增 {created} 个竞赛，更新 {updated} 个竞赛")


if __name__ == "__main__":
    main()
