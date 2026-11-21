# -*- coding: utf-8 -*-
"""把 docs/design/assets/*.puml 通过 Kroki 渲染为同目录 PNG。

用法: python tools/render_diagrams.py [文件名...]（默认渲染全部）
依赖: 仅标准库；需要外网访问 kroki.io。
"""
import sys
import time
import urllib.request
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "docs" / "design" / "assets"
KROKI = "https://kroki.io/plantuml/png"


def render(puml_path: Path) -> bool:
    src = puml_path.read_text(encoding="utf-8")
    req = urllib.request.Request(
        KROKI,
        data=src.encode("utf-8"),
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception as exc:
        print(f"[FAIL] {puml_path.name}: {exc}")
        return False
    if not data.startswith(b"\x89PNG"):
        print(f"[FAIL] {puml_path.name}: 返回非 PNG: {data[:200]!r}")
        return False
    out = puml_path.with_suffix(".png")
    out.write_bytes(data)
    print(f"[ OK ] {puml_path.name} -> {out.name} ({len(data)} bytes)")
    return True


def main():
    names = sys.argv[1:]
    files = [ASSETS / n for n in names] if names else sorted(ASSETS.glob("*.puml"))
    ok = 0
    for f in files:
        if render(f):
            ok += 1
        time.sleep(0.3)
    print(f"done: {ok}/{len(files)}")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
