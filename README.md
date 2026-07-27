# MOProblems

常见数学竞赛问题库（与数之谜同步更新）

## 目录结构

```
problems/
├── china/        # 国内竞赛
├── abroad/       # 国际竞赛
├── university/   # 大学竞赛
└── original/     # 原创竞赛
```

`problems/{source}/{name}` 目录名对应 `competitions.json` 中每个条目的 `source` 和 `name` 字段。例如 `problems/china/bj/` 表示 source 为 `"china"`、name 为 `"bj"` 的竞赛。

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

| source | 分类 | 竞赛数量 | 说明 |
|---|---|---|---|
| `china` | 国内竞赛 | 20 | 中国各级数学竞赛及模拟 |
| `abroad` | 国际竞赛 | 20 | 国际及各国地区数学竞赛 |
| `university` | 大学竞赛 | 11 | 面向大学生的数学竞赛 |
| `original` | 原创竞赛 | 14 | 由社区或个人原创的题目 |