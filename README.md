# MOProblems

常见数学竞赛问题库（与数之谜同步更新）

## 目录结构

```
problems/
├── china/        # 国内竞赛
├── abroad/       # 国际竞赛
├── university/   # 大学竞赛
└── original/     # 原创竞赛

tools/
├── merge_temp.py     # 合并 temp.json 到 competitions.json
└── check_valid.py    # 校验 competitions.json 及对应文件夹
```

`problems/{source}/{name}` 目录名对应 `competitions.json` 中每个条目的 `source` 和 `name` 字段。例如 `problems/china/bj/` 表示 source 为 `"china"`、name 为 `"bj"` 的竞赛。

## tools 工具说明

`tools/` 目录包含项目辅助工具：

- **`merge_temp.py`** — 将 `temp.json`（API 原始响应）中的新比赛自动转换为 `competitions.json` 格式并合并。运行时会根据新增比赛的 `source` 和 `name` 自动创建 `problems/{source}/{name}/info.json`（空 JSON 对象）。
- **`check_valid.py`** — 校验工具，检查 `competitions.json` 中所有条目的 UUID 合法性、id/name 唯一性、years 重复性，以及 `problems/{source}/{name}/` 文件夹和 `info.json` 是否存在。

## competitions.json 数据结构

`competitions.json` 定义了所有竞赛的元数据，其结构如下：

```json
[
  {
    "id": "0d866ffd-91a6-46e3-91a8-12e3d3a213f3",
    "name": "bj",
    "display_name": "北京创新题",
    "years": ["高考", "2026二模", ...],
    "source": "china"
  },
  ...
]
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `id` | `string` | UUID v4，全局唯一标识 | `"0d866ffd-91a6-46e3-91a8-12e3d3a213f3"` |
| `name` | `string` | 竞赛的英文短名称，同时用作 `problems/{source}/{name}` 目录名 | `"bj"` |
| `display_name` | `string` | 竞赛的中文全称，用于展示 | `"北京创新题"` |
| `years` | `string[]` | 该竞赛包含的年份/届次列表，每个元素格式因竞赛而异 | `["2025(66届)", "2024(65届)", ...]` |
| `source` | `string` | 竞赛分类，共 4 类：`china`（国内）、`abroad`（国际）、`university`（大学）、`original`（原创） | `"china"` |

### source 分类

| source | 分类 | 说明 |
|---|---|---|
| `china` | 国内竞赛 | 中国各级数学竞赛及模拟 |
| `abroad` | 国际竞赛 | 国际及各国地区数学竞赛 |
| `university` | 大学竞赛 | 面向大学生的数学竞赛 |
| `original` | 原创竞赛 | 由社区或个人原创的题目 |