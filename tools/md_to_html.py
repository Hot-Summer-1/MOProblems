"""
md_to_html.py - 将 problems 目录下的 Markdown 题目文件转换为 HTML

用法: python tools/md_to_html.py [--keep]

将每个 .md 题目文件转换为同名 .html 文件，默认删除原 .md 文件。
转换使用 Python-Markdown 库处理排版，并在转换前保护 $...$、$$...$$、
\\(...\\)、\\[...\\] 等公式片段，最后用 latex2mathml 转换为 MathML，
由浏览器原生渲染，无需额外加载 MathJax / KaTeX。

依赖: pip install markdown latex2mathml
"""

import argparse
import html
import os
import re
import sys

try:
    import markdown
    import latex2mathml.converter as latex2mathml
except ImportError:
    print("[错误] 缺少依赖，请先执行: pip install markdown latex2mathml")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")

MATH = re.compile(r"\\\[.*?\\\]|\$\$.*?\$\$|\\\(.*?\\\)|\$[^$\n]+?\$", re.DOTALL)
LIST_ITEM = re.compile(r"^ {0,3}(?:[-*+]|\d+[.)])\s+")
PLACEHOLDER = "MATHPLACEHOLDER{}END"
DISPLAY_DELIMITERS = ("\\[", "$$")
INLINE_DELIMITERS = ("\\(", "$")


def normalize_list_spacing(text):
    """在列表前后补空行，满足 Python-Markdown 对列表的解析要求"""
    lines = text.split("\n")
    result = []
    for line in lines:
        is_item = bool(LIST_ITEM.match(line))
        previous = result[-1] if result else ""
        if is_item and previous.strip() and not LIST_ITEM.match(previous):
            result.append("")
        elif not is_item and line.strip() and LIST_ITEM.match(previous):
            result.append("")
        result.append(line)
    return "\n".join(result)


def protect_math(text):
    formulas = []

    def replace(match):
        formulas.append(match.group(0))
        return PLACEHOLDER.format(len(formulas) - 1)

    return MATH.sub(replace, text), formulas


def render_math(formula):
    """将 LaTeX 公式转换为 MathML，转换失败时回退为原始文本"""
    is_display = formula.startswith(DISPLAY_DELIMITERS)
    is_inline = formula.startswith(INLINE_DELIMITERS)

    if is_display:
        body = formula[2:-2]
    elif is_inline:
        body = formula[1:-1] if formula.startswith("$") else formula[2:-2]
    else:
        return html.escape(formula, quote=False)

    try:
        return latex2mathml.convert(
            body.strip(), display="block" if is_display else "inline"
        )
    except Exception:
        return html.escape(formula, quote=False)


def convert(text):
    protected, formulas = protect_math(text)
    protected = normalize_list_spacing(protected)
    output = markdown.markdown(protected, extensions=["extra", "sane_lists"])
    for index, formula in enumerate(formulas):
        output = output.replace(PLACEHOLDER.format(index), render_math(formula))
    return output


def main():
    parser = argparse.ArgumentParser(description="将题目 Markdown 文件转换为 HTML")
    parser.add_argument("--keep", action="store_true", help="保留原 .md 文件")
    args = parser.parse_args()

    if not os.path.isdir(PROBLEMS_DIR):
        print(f"[错误] 未找到 problems 目录: {PROBLEMS_DIR}")
        sys.exit(1)

    converted = 0
    for root, _, files in os.walk(PROBLEMS_DIR):
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue
            md_path = os.path.join(root, filename)
            html_path = md_path[:-3] + ".html"

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(html_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(convert(content))

            if not args.keep:
                os.remove(md_path)

            print(f"[转换] {os.path.relpath(md_path, BASE_DIR)} -> "
                  f"{os.path.relpath(html_path, BASE_DIR)}")
            converted += 1

    print(f"\n[完成] 共转换 {converted} 个文件")
    if not converted:
        print("[提示] 没有找到需要转换的 .md 文件")


if __name__ == "__main__":
    main()
