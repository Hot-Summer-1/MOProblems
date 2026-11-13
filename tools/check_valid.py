import json
import os
import sys
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
SOURCES = ("china", "abroad", "university", "original")

ENTRY_KEYS = ("name", "count", "no_problem_content", "begin_index")


class DuplicateKeyError(ValueError):
    pass


def no_duplicate_keys(pairs):
    result = OrderedDict()
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"重复的键: {key!r}")
        result[key] = value
    return result


def load_info(path, errors):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f, object_pairs_hook=no_duplicate_keys)
    except DuplicateKeyError as exc:
        errors.append(f"{path}: JSON {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: JSON 解析失败: {exc}")
    return None


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_entry(info_path, index, entry, errors, warnings):
    prefix = f"{info_path} 的 years[{index}]"
    if not isinstance(entry, dict):
        errors.append(f"{prefix}: 条目必须是对象")
        return

    year_name = entry.get("name")
    if isinstance(year_name, str) and year_name.strip():
        prefix = f"{info_path} 的 year='{year_name}'"
    elif "name" in entry:
        errors.append(f"{prefix}: name 必须是非空字符串")

    missing = [key for key in ENTRY_KEYS if key not in entry]
    if missing:
        errors.append(f"{prefix}: 缺少字段 {missing}")
        return

    extra = [key for key in entry if key not in ENTRY_KEYS]
    if extra:
        warnings.append(f"{prefix}: 存在未知字段 {extra}")

    if not is_int(entry["count"]) or entry["count"] < 0:
        errors.append(f"{prefix}: count 必须是非负整数")
    if not isinstance(entry["no_problem_content"], bool):
        errors.append(f"{prefix}: no_problem_content 必须是布尔值")
    if not is_int(entry["begin_index"]) or entry["begin_index"] < 0:
        errors.append(f"{prefix}: begin_index 必须是非负整数")


def check_files(folder, years, errors, warnings):
    name = os.path.basename(folder)
    try:
        files = os.listdir(folder)
    except OSError as exc:
        errors.append(f"{folder}: 无法读取目录: {exc}")
        return

    present = {
        int(f[:-3]) for f in files
        if f.endswith(".md") and f[:-3].isdigit()
    }
    unknown_files = [
        f for f in files
        if f != "info.json" and not (f.endswith(".md") and f[:-3].isdigit())
    ]
    if unknown_files:
        warnings.append(f"{name}: 存在未识别的文件 {sorted(unknown_files)}")

    covered = set()
    for index, entry in enumerate(years):
        if not isinstance(entry, dict):
            continue
        year_name = entry.get("name", f"#{index}")
        count = entry.get("count")
        begin = entry.get("begin_index")
        no_content = entry.get("no_problem_content")
        if not (is_int(count) and is_int(begin) and isinstance(no_content, bool)):
            continue

        expected = set(range(begin, begin + count))
        if no_content:
            found = sorted(present & expected)
            if found:
                warnings.append(
                    f"{name} 的 year='{year_name}': no_problem_content=true 但存在题目文件 "
                    f"{[f'{i}.md' for i in found]}"
                )
        else:
            missing = sorted(expected - present)
            if missing:
                errors.append(
                    f"{name} 的 year='{year_name}': 缺少题目文件 "
                    f"{[f'{i}.md' for i in missing]}"
                )
        covered |= expected

    extra = sorted(present - covered)
    if extra:
        warnings.append(f"{name}: 存在不属于任何年份的题目文件 {[f'{i}.md' for i in extra]}")


def check_info(info_path, errors, warnings):
    info = load_info(info_path, errors)
    if info is None:
        return None

    if not isinstance(info, dict):
        errors.append(f"{info_path}: 根节点必须是对象")
        return None

    missing = [key for key in ("display_name", "years") if key not in info]
    if missing:
        errors.append(f"{info_path}: 缺少字段 {missing}")
        return None

    extra = [key for key in info if key not in ("display_name", "years")]
    if extra:
        warnings.append(f"{info_path}: 存在未知字段 {extra}")

    if not isinstance(info["display_name"], str) or not info["display_name"].strip():
        errors.append(f"{info_path}: display_name 必须是非空字符串")

    years = info["years"]
    if not isinstance(years, list):
        errors.append(f"{info_path}: years 必须是数组")
        return None
    if not years:
        warnings.append(f"{info_path}: years 为空")

    seen = set()
    for index, entry in enumerate(years):
        check_entry(info_path, index, entry, errors, warnings)
        if isinstance(entry, dict):
            year_name = entry.get("name")
            if isinstance(year_name, str) and year_name.strip():
                if year_name in seen:
                    errors.append(f"{info_path}: years 中存在重复的 name='{year_name}'")
                seen.add(year_name)

    check_files(os.path.dirname(info_path), years, errors, warnings)

    return info


def main():
    if not os.path.isdir(PROBLEMS_DIR):
        print(f"[错误] 未找到 problems 目录: {PROBLEMS_DIR}")
        sys.exit(1)

    errors = []
    warnings = []
    infos = []

    for source in sorted(os.listdir(PROBLEMS_DIR)):
        source_path = os.path.join(PROBLEMS_DIR, source)
        if not os.path.isdir(source_path):
            continue
        if source not in SOURCES:
            errors.append(f"未知的分类目录: {source}")

        for name in sorted(os.listdir(source_path)):
            folder = os.path.join(source_path, name)
            if not os.path.isdir(folder):
                continue
            info_path = os.path.join(folder, "info.json")
            if not os.path.isfile(info_path):
                errors.append(f"{folder}: info.json 不存在")
                continue
            info = check_info(info_path, errors, warnings)
            if info is not None:
                infos.append((source, name, info))

    print(f"总竞赛数: {len(infos)}")
    print(f"总年份数: {sum(len(info['years']) for _, _, info in infos)}\n")

    name_map = {}
    display_map = {}
    for source, name, info in infos:
        name_map.setdefault(name, []).append(f"{source}/{name}")
        display_map.setdefault(info["display_name"], []).append(f"{source}/{name}")

    for name, paths in sorted(name_map.items()):
        if len(paths) > 1:
            errors.append(f"重复的 name='{name}': {paths}")
    for display_name, paths in sorted(display_map.items()):
        if len(paths) > 1:
            errors.append(f"重复的 display_name='{display_name}': {paths}")

    if warnings:
        print(f"[警告] 共 {len(warnings)} 条:")
        for message in warnings:
            print(f"  {message}")
        print()

    if errors:
        print(f"[错误] 共 {len(errors)} 条:")
        for message in errors:
            print(f"  {message}")
        print("\n检查未通过")
        sys.exit(1)

    print("[通过] 所有 info.json 均合法")
    print("\n检查完毕")


if __name__ == "__main__":
    main()
