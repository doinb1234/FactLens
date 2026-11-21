# -*- coding: utf-8 -*-
"""用 Edge 无头模式给原型页面截图（供博客与墨刀复刻指南使用）。

用法: python tools/screenshots.py
输出: docs/design/assets/shots/*.png
"""
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO = ROOT / "docs" / "prototype"
OUT = ROOT / "docs" / "design" / "assets" / "shots"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# (输出文件名, 相对原型目录的页面, hash, 虚拟时间预算)
SHOTS = [
    ("front-home",     "index.html", "#home",            3000),
    ("front-report",   "index.html", "#home?demo=1",     12000),
    ("front-history",  "index.html", "#history?seed=1",  3000),
    ("front-about",    "index.html", "#about",           3000),
    ("admin-login",    "admin.html", "",                 3000),
    ("admin-overview", "admin.html", "#overview?demo=1", 4000),
    ("admin-records",  "admin.html", "#records?demo=1",  4000),
    ("admin-sources",  "admin.html", "#sources?demo=1",  4000),
    ("admin-config",   "admin.html", "#config?demo=1",   4000),
]


def shot(name: str, page: str, hash_part: str, budget: int) -> Path:
    url = (PROTO / page).as_uri() + hash_part
    out = OUT / f"{name}.png"
    with tempfile.TemporaryDirectory() as prof:
        cmd = [
            EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
            "--hide-scrollbars", f"--user-data-dir={prof}",
            f"--window-size=1440,960", f"--virtual-time-budget={budget}",
            f"--screenshot={out}", url,
        ]
        subprocess.run(cmd, capture_output=True, timeout=90)
    if not out.exists() or out.stat().st_size < 3000:
        print(f"[FAIL] {name} (missing or empty)")
        return None
    print(f"[ OK ] {name}.png ({out.stat().st_size // 1024}KB)")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, page, h, budget in SHOTS:
        if shot(name, page, h, budget):
            ok += 1
        time.sleep(0.4)
    print(f"done: {ok}/{len(SHOTS)}")
    return 0 if ok == len(SHOTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
