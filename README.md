# MOProblems

常见数学竞赛问题库（与数之谜同步更新）。题目正文以 HTML 格式存储，数学公式转换为 MathML，由浏览器原生渲染。

## 目录结构

```
problems/
├── china/        # 国内竞赛
├── abroad/       # 国际竞赛
├── university/   # 大学竞赛
└── original/     # 原创竞赛
```

每个竞赛对应一个目录 `problems/{source}/{name}/`，例如 `problems/china/bj/` 中 `source` 为 `china`、`name` 为 `bj`。竞赛的 `source` 和 `name` 均由路径推断，不在 `info.json` 中重复存储。

```
problems/{source}/{name}/
├── info.json     # 竞赛元数据及各年份题目信息
├── 0.html        # 题目文件（文件名由 begin_index 决定）
└── ...
```

`tools/` 目录包含项目辅助工具：

- **`merge_temp.py`** — 将 `temp.json`（API 原始响应）中的比赛合并到对应 `problems/{source}/{name}/info.json`，自动创建目录、补充缺失年份。
- **`md_to_html.py`** — 将题目 Markdown 文件批量转换为 HTML，公式转换为 MathML 由浏览器原生渲染，默认删除原 `.md` 文件。需要先安装依赖：`pip install markdown latex2mathml`。
- **`check_valid.py`** — 校验所有 `info.json` 的结构、字段、年份、题目文件对应关系，以及 name/display_name 唯一性。

## info.json 结构

每个 `problems/{source}/{name}/info.json` 记录该竞赛的展示名称和各年份的题目信息。`source` 与 `name` 由目录路径推断：

```json
{
  "display_name": "北京创新题",
  "years": [
    {
      "name": "2025(A卷)",
      "count": 0,
      "no_problem_content": true,
      "begin_index": 0
    },
    {
      "name": "2025(B卷)",
      "count": 0,
      "no_problem_content": true,
      "begin_index": 0
    }
  ]
}
```

### 竞赛字段

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `display_name` | `string` | 竞赛的中文全称，用于展示 | `"北京创新题"` |
| `years` | `array` | 年份/届次列表，数组顺序即展示顺序 | 见下 |

`source` 目录共 4 类：`china`（国内）、`abroad`（国际）、`university`（大学）、`original`（原创）。

### 年份条目字段

`years` 中每个元素对应一个年份，包含 4 个字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `string` | 年份/届次，同一竞赛内不可重复 |
| `count` | `int` | 该年份题目数量，默认为 0 |
| `no_problem_content` | `bool` | 是否暂无题目内容，`true` 表示尚未录入，默认为 `false` |
| `begin_index` | `int` | 题目文件名称起始值，默认为 0 |

题目文件命名为 `{begin_index + i}.html`（`i = 0..count-1`）。例如 `begin_index` 为 0、`count` 为 6 时，题目文件为 `0.html` 至 `5.html`。文件内容为 HTML 片段，其中数学公式已由 LaTeX 转换为 MathML，浏览器可直接渲染。当 `no_problem_content` 为 `true` 时，`count` 可表示该年份应有的题目数量，但对应文件暂不存在。
