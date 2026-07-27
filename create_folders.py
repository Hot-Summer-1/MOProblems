import json
import os
import shutil

# 读取competitions.json
with open('competitions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 删除并重新创建problems文件夹
if os.path.exists('problems'):
    shutil.rmtree('problems')

# 按source和name创建对应文件夹，并在每个文件夹中创建info.json
for item in data:
    source = item['source']
    name = item['name']
    path = f'problems/{source}/{name}'
    os.makedirs(path, exist_ok=True)
    
    # 在每个文件夹中创建info.json，包含count=0
    info_path = os.path.join(path, 'info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({"count": 0}, f, ensure_ascii=False, indent=2)
    
    print(f'创建info.json (count=0): {path}')

print(f'\n总共创建了 {len(data)} 个文件夹，每个文件夹内包含 count=0 的 info.json')