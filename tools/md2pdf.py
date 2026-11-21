# -*- coding: utf-8 -*-
"""Markdown -> 排版 HTML -> PDF（Edge 无头打印）。

约定：
- 文件头可写 <!-- key: value --> 注释作为元数据：
  title(封面大标题) subtitle(副标题) doctype(文档类型) version date team course
- 图片使用标准 markdown 语法，alt 文本作为图题（图 x）。
用法: python tools/md2pdf.py <md文件>
输出: 同目录同名 .html / .pdf
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS = """
@page { size: A4; margin: 22mm 18mm 20mm 18mm; }
* { box-sizing: border-box; }
body {
  font-family: "SimSun", "Songti SC", "NSimSun", serif;
  font-size: 10.5pt; line-height: 1.78; color: #1c1c1c;
  counter-reset: figcnt tblcnt;
}
h1, h2, h3, h4 { font-family: "Microsoft YaHei", "SimHei", sans-serif; color: #0f3d38; }
h1 {
  font-size: 16pt; margin: 0 0 14px; padding-bottom: 7px;
  border-bottom: 2.5px solid #0f766e; page-break-before: always; page-break-after: avoid;
}
h1.first { page-break-before: avoid; }
h2 { font-size: 13.5pt; margin: 18px 0 9px; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 14px 0 7px; page-break-after: avoid; }
h4 { font-size: 11pt; margin: 11px 0 6px; page-break-after: avoid; }
p { margin: 6px 0; text-align: justify; }
ul, ol { margin: 6px 0 6px 1.6em; padding: 0; }
li { margin: 3px 0; }
table {
  width: 100%; border-collapse: collapse; margin: 10px 0;
  font-size: 9pt; page-break-inside: avoid;
}
th { background: #e8f5f3; font-family: "Microsoft YaHei"; font-weight: 700; }
th, td { border: 1px solid #a8bcb9; padding: 4.5px 7px; text-align: left; vertical-align: top; }
tr { page-break-inside: avoid; }
td.center, th.center { text-align: center; }
code {
  font-family: Consolas, "Courier New", monospace; font-size: 8.8pt;
  background: #f3f6f6; padding: 1px 4px; border-radius: 3px; color: #0f766e;
}
pre {
  background: #f6f8f8; border: 1px solid #dbe5e3; border-radius: 6px;
  padding: 10px 12px; font-size: 8.8pt; line-height: 1.5; overflow-x: hidden;
  page-break-inside: avoid;
}
pre code { background: none; padding: 0; color: #234; }
figure { margin: 12px 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; }
figcaption {
  font-family: "Microsoft YaHei"; font-size: 9pt; color: #4a5a58; margin-top: 5px;
}
figcaption::before { counter-increment: figcnt; content: "图 " counter(figcnt) "  "; font-weight: 700; }
strong { color: #0f3d38; }
a { color: #0f766e; text-decoration: none; }
blockquote { margin: 8px 0; padding: 6px 14px; background: #f0f7f6; border-left: 4px solid #0f766e; color: #345; }
hr { border: none; border-top: 1px dashed #b9c8c5; margin: 16px 0; }

/* ---------- 封面 ---------- */
.cover { text-align: center; page-break-after: always; padding-top: 130px; }
.cover .logo-title { font-family: "Microsoft YaHei"; font-size: 26pt; font-weight: 800; color: #0f3d38; margin-bottom: 6px; }
.cover .logo-sub { font-size: 12pt; color: #56706c; margin-bottom: 90px; }
.cover .doc-type {
  font-family: "Microsoft YaHei"; font-size: 30pt; font-weight: 800; letter-spacing: 6px;
  color: #0f766e; margin-bottom: 8px;
}
.cover .doc-en { font-size: 10.5pt; color: #89a09c; margin-bottom: 110px; }
.cover table { width: 62%; margin: 0 auto; border: none; font-size: 10.5pt; }
.cover table td { border: none; padding: 7px 10px; text-align: left; }
.cover table td.k { text-align: right; color: #56706c; width: 34%; font-family: "Microsoft YaHei"; }
.cover table td.v { font-family: "Microsoft YaHei"; font-weight: 700; }

/* ---------- 目录 ---------- */
.toc { page-break-after: always; }
.toc h1 { border: none; }
.toc ul { list-style: none; margin-left: 0; }
.toc ul ul { margin-left: 1.4em; }
.toc li { margin: 5px 0; }
.toc .lvl1 { font-family: "Microsoft YaHei"; font-weight: 700; }
.toc .lvl2 { color: #456; font-size: 10pt; }
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head>
<body>
{cover}
{toc}
{content}
</body>
</html>"""


def parse_meta(md_text: str) -> dict:
    meta = {}
    for line in md_text.splitlines()[:40]:
        m = re.match(r"<!--\s*([\w-]+):\s*(.*?)\s*-->", line)
        if m:
            meta[m.group(1)] = m.group(2)
    return meta


def build_cover(meta: dict) -> str:
    members = meta.get("members", "")
    member_rows = "".join(
        f"<tr><td class='k'>团队成员</td><td class='v'>{m.strip()}</td></tr>"
        for m in members.split("|") if m.strip()
    )
    return f"""
<div class="cover">
  <div class="logo-title">{meta.get('title', '')}</div>
  <div class="logo-sub">{meta.get('subtitle', '')}</div>
  <div class="doc-type">{meta.get('doctype', '')}</div>
  <div class="doc-en">{meta.get('doctype_en', '')}</div>
  <table>
    <tr><td class="k">项目名称</td><td class="v">{meta.get('project', '')}</td></tr>
    <tr><td class="k">文档版本</td><td class="v">{meta.get('version', 'V1.0')}</td></tr>
    <tr><td class="k">编制日期</td><td class="v">{meta.get('date', '')}</td></tr>
    <tr><td class="k">团队名称</td><td class="v">{meta.get('team', '')}</td></tr>
    <tr><td class="k">所属课程</td><td class="v">{meta.get('course', '')}</td></tr>
    <tr><td class="k">指导教师</td><td class="v">{meta.get('teacher', '')}</td></tr>
    {member_rows}
  </table>
</div>
"""


def build_toc(md_text: str) -> str:
    """从 markdown 标题生成静态目录。"""
    items = []
    for line in md_text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if not m:
            continue
        level = len(m.group(1))
        title = re.sub(r"[*_`]", "", m.group(2))
        if level == 1:
            items.append(f'<li class="lvl1">{title}</li>')
        else:
            items.append(f'<li class="lvl2">{"&nbsp;" * ((level - 1) * 6)}{title}</li>')
    if not items:
        return ""
    return '<div class="toc"><h1>目 录</h1><ul>' + "".join(items) + "</ul></div>"


def postprocess(html: str) -> str:
    # 图片 → figure + 图题（alt 作为题注）
    def img_sub(m):
        alt = m.group(1).strip() or "图"
        return f'<figure><img src="{m.group(2)}" alt="{alt}"><figcaption>{alt}</figcaption></figure>'
    html = re.sub(r"<p>\s*<img alt=\"([^\"]*)\" src=\"([^\"]+)\" ?/?>\s*</p>", img_sub, html)
    # 第一个 h1 不断页
    html = html.replace("<h1>", "<h1 class=\"first\">", 1)
    return html


def convert(md_path: Path) -> Path:
    text = md_path.read_text(encoding="utf-8")
    meta = parse_meta(text)
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    body = postprocess(body)
    html = TEMPLATE.format(
        title=meta.get("title", "文档"),
        css=CSS,
        cover=build_cover(meta),
        toc=build_toc(text),
        content=body,
    )
    html_path = md_path.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    pdf_path = md_path.with_suffix(".pdf")
    with tempfile.TemporaryDirectory() as prof:
        cmd = [
            EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
            f"--user-data-dir={prof}", "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}", html_path.as_uri(),
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=180)
    if not pdf_path.exists() or pdf_path.stat().st_size < 5000:
        print(f"[FAIL] {md_path.name}: {r.stderr.decode('utf-8', 'ignore')[-300:]}")
        return None
    print(f"[ OK ] {md_path.name} -> {pdf_path.name} ({pdf_path.stat().st_size // 1024}KB)")
    return pdf_path


def main():
    for arg in sys.argv[1:]:
        p = Path(arg).resolve()
        if p.suffix != ".md":
            print(f"skip {arg}: not .md")
            continue
        convert(p)


if __name__ == "__main__":
    main()
