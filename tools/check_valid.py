import json
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPETITIONS_FILE = os.path.join(BASE_DIR, "competitions.json")

with open(COMPETITIONS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"总条目数: {len(data)}\n")

# 检查 UUID 格式 (8-4-4-4-12 十六进制)
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

invalid_uuids = []
for e in data:
    eid = e['id']
    if not uuid_pattern.match(eid):
        invalid_uuids.append((eid, e['name']))

if invalid_uuids:
    print(f"[错误] 发现不合法 UUID 的 id:")
    for eid, name in invalid_uuids:
        print(f"  id='{eid}' (name='{name}')")
else:
    print("[通过] 所有 id 均为合法 UUID")

# 1. 检查 id 是否重复
id_set = set()
duplicate_ids = []
for e in data:
    eid = e['id']
    if eid in id_set:
        duplicate_ids.append(eid)
    id_set.add(eid)

if duplicate_ids:
    print(f"[错误] 发现重复的 id: {duplicate_ids}")
else:
    print("[通过] 无重复 id")

# 2. 检查 name 是否重复
name_map = {}
for e in data:
    name = e['name']
    if name not in name_map:
        name_map[name] = []
    name_map[name].append(e['display_name'])

duplicate_names = {k: v for k, v in name_map.items() if len(v) > 1}
if duplicate_names:
    print(f"[错误] 发现重复的 name:")
    for n, displays in duplicate_names.items():
        print(f"  name='{n}' 出现在 {len(displays)} 个条目: {displays}")
else:
    print("[通过] 无重复 name")

# 3. 检查每个条目 years 内是否有重复内容
print()
has_year_dup = False
for e in data:
    years = e.get('years', [])
    seen = set()
    dup_years = []
    for y in years:
        if y in seen:
            dup_years.append(y)
        seen.add(y)
    if dup_years:
        has_year_dup = True
        print(f"[错误] '{e['name']}' ({e['display_name']}) 的 years 内有重复: {dup_years}")
    empty_years = [y for y in years if not y or not y.strip()]
    if empty_years:
        has_year_dup = True
        print(f"[错误] '{e['name']}' ({e['display_name']}) 的 years 内有空内容")

if not has_year_dup:
    print("[通过] 所有条目的 years 无重复且无空内容")

# 4. 检查每个条目对应的 problems/{source}/{name}/ 文件夹和 info.json 是否存在
print()
has_folder_missing = False
for e in data:
    source = e.get("source", "")
    name = e.get("name", "")
    if not source or not name:
        print(f"[跳过] '{e.get('display_name', '?')}' 缺少 source 或 name")
        continue

    folder_path = os.path.join(BASE_DIR, "problems", source, name)
    info_path = os.path.join(folder_path, "info.json")

    if not os.path.isdir(folder_path):
        has_folder_missing = True
        print(f"[错误] '{e['display_name']}' ({e['name']}) 文件夹不存在: {os.path.join('problems', source, name)}")
    elif not os.path.isfile(info_path):
        has_folder_missing = True
        print(f"[错误] '{e['display_name']}' ({e['name']}) info.json 不存在: {os.path.join('problems', source, name, 'info.json')}")

if not has_folder_missing:
    print("[通过] 所有条目的文件夹和 info.json 均存在")

print("\n检查完毕")
