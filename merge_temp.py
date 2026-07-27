"""
merge_temp.py - 将 temp.json 中新加入的比赛自动转换为 competitions.json 格式并合并

用法: python merge_temp.py

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
        "status": "",
        "ordinal": 50,
        ...
      }
    ]
  }
}

competitions.json 格式（目标格式）:
[
  {
    "id": "uuid4-string",
    "name": "IMO",
    "display_name": "国际数学奥林匹克",
    "years": ["2026", "2025"],
    "source": "abroad"
  },
  ...
]
"""

import json
import uuid
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_FILE = os.path.join(BASE_DIR, "temp.json")
COMPETITIONS_FILE = os.path.join(BASE_DIR, "competitions.json")


def convert_item(raw):
    """将原始 API 格式的单条记录转换为目标格式"""
    # source: 数组 → 字符串（取第一个元素）
    source_val = raw.get("source", [])
    if isinstance(source_val, list) and len(source_val) > 0:
        source_val = source_val[0]
    elif isinstance(source_val, list):
        source_val = ""
    else:
        source_val = str(source_val) if source_val else ""

    # years: 过滤空字符串
    years = [y for y in raw.get("years", []) if y != ""]

    return {
        "id": str(uuid.uuid4()),
        "name": raw.get("short", ""),
        "display_name": raw.get("name", ""),
        "years": years,
        "source": source_val,
    }


def main():
    # 1. 检查 temp.json 是否存在
    if not os.path.exists(TEMP_FILE):
        print(f"[错误] 未找到 {TEMP_FILE}")
        sys.exit(1)

    # 2. 读取 temp.json
    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        temp_data = json.load(f)

    # 提取 rows
    new_rows = temp_data.get("data", {}).get("rows", [])
    if not new_rows:
        print("[提示] temp.json 中没有新比赛数据")
        sys.exit(0)

    # 3. 转换新数据
    converted = [convert_item(r) for r in new_rows]
    print(f"[转换] temp.json 中共 {len(converted)} 条记录")

    # 4. 读取现有 competitions.json
    if os.path.exists(COMPETITIONS_FILE):
        with open(COMPETITIONS_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    # 5. 按 name 去重合并
    existing_names = {item["name"] for item in existing}
    merged_count = 0
    for item in converted:
        if item["name"] not in existing_names:
            existing.append(item)
            existing_names.add(item["name"])
            merged_count += 1
            print(f"  [+] 新增: {item['display_name']} ({item['name']})")
        else:
            print(f"  [~] 跳过(已存在): {item['display_name']} ({item['name']})")

    # 6. 写回 competitions.json
    with open(COMPETITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n[完成] 合并 {merged_count} 条新记录，competitions.json 共 {len(existing)} 条")


if __name__ == "__main__":
    main()