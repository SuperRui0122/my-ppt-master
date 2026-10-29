#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_preview.py — 单文件预览器双端门禁（PREVIEW_SPEC.md 的可执行校验）。

为什么需要它
------------
`build_preview.py` 的响应式能力全部藏在模板字符串里，一旦有人「为了手机端」删掉
某个媒体查询、或把 viewport 元信息去掉，产物照样能生成、照样能打开，但手机端会
退回桌面布局且**没有任何报错**。本脚本把 PREVIEW_SPEC.md 第五节的要求固化成断言。

检查项
------
  P1  产物存在          <project>/<册目录名>.preview.html
  P2  R8 命名            前缀必须等于册目录名（清洗后）
  P3  viewport 元信息    width=device-width + viewport-fit=cover
  P4  移动端高度单位     100dvh（不是 100vh）
  P5  B 布局媒体查询     (max-width:820px), (pointer:coarse)
  P6  C 布局媒体查询     (pointer:coarse) and (orientation:landscape)
  P7  抽屉遮罩元素       id="backdrop"
  P8  滑动翻页           touchstart 监听
  P9  页数一致           data:image/svg+xml 计数 == svg_output/*.svg 数
  P10 桌面元素未丢       <header> / <footer> / id="side" / id="btnFit"
  P11 体积阈值           >25 MB 给 WARN（手机加载慢，但不阻断）

用法
----
    python check_preview.py <project_path>
    python check_preview.py <project_path> --json     # 写 validation/preview_audit.json
    python check_preview.py <project_path> --html <file>   # 指定产物（默认按 R8 推导）

退出码：0 = 通过；1 = 存在阻断项；2 = 用法/路径错误。
"""

import argparse
import json
import os
import re
import sys

BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def deck_slug(root):
    slug = BAD_CHARS.sub("_", os.path.basename(os.path.abspath(root))).strip().strip(".")
    slug = re.sub(r"\s+", "_", slug)
    return slug or "deck"


def main(argv=None):
    ap = argparse.ArgumentParser(description="单文件预览器双端门禁")
    ap.add_argument("directory", help="含 svg_output/ 的册目录")
    ap.add_argument("--html", default=None, help="预览产物路径（默认 <册目录名>.preview.html）")
    ap.add_argument("--json", action="store_true", help="写 validation/preview_audit.json")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.directory)
    svg_dir = os.path.join(root, "svg_output")
    if not os.path.isdir(svg_dir):
        print("[ERROR] 找不到 svg_output：%s" % svg_dir, file=sys.stderr)
        return 2

    slug = deck_slug(root)
    html_path = args.html or os.path.join(root, slug + ".preview.html")
    if not os.path.isfile(html_path):
        print("[FAIL] P1 产物不存在：%s" % html_path, file=sys.stderr)
        print("       先跑：python build_preview.py \"%s\"" % root, file=sys.stderr)
        return 1

    text = open(html_path, encoding="utf-8", errors="ignore").read()
    n_svg = len([f for f in os.listdir(svg_dir) if f.lower().endswith(".svg")])
    n_page = len(re.findall(r"data:image/svg\+xml", text))
    size_mb = os.path.getsize(html_path) / 1024 / 1024

    checks = []   # (编号, 名称, 通过?, 阻断?, 详情)

    def add(pid, name, ok, detail="", block=True):
        checks.append((pid, name, ok, block, detail))

    add("P1", "产物存在", True, os.path.basename(html_path))
    add("P2", "R8 命名", os.path.basename(html_path) == slug + ".preview.html",
        "" if os.path.basename(html_path) == slug + ".preview.html"
        else "应为 %s.preview.html" % slug)
    add("P3", "viewport 元信息",
        'name="viewport"' in text and "width=device-width" in text)
    add("P4", "移动端高度单位", "100dvh" in text, "缺 100dvh，移动端地址栏会吃内容")
    add("P5", "B 布局媒体查询（竖屏/触屏）",
        "(max-width:820px), (pointer:coarse)" in text,
        "缺 820px + pointer:coarse，横屏手机会掉回桌面布局")
    add("P6", "C 布局媒体查询（横屏演示）",
        "(pointer:coarse) and (orientation:landscape)" in text,
        "缺横屏演示模式")
    add("P7", "抽屉遮罩", 'id="backdrop"' in text)
    add("P8", "滑动翻页", "touchstart" in text)
    add("P9", "页数一致", n_page == n_svg,
        "预览 %d 页 / SVG %d 页（不一致通常意味着产物是旧快照，重跑即可）" % (n_page, n_svg))
    add("P10", "桌面元素未丢",
        all(k in text for k in ("<header>", "<footer>", 'id="side"', 'id="btnFit"')),
        "header/footer/#side/btnFit 至少缺一个，桌面端会被手机适配改坏")
    add("P11", "体积阈值", size_mb <= 25.0,
        "%.1f MB，手机加载偏慢（建议压缩图片或分册）" % size_mb, block=False)

    block_fail = [c for c in checks if c[3] and not c[2]]
    warn_fail = [c for c in checks if not c[3] and not c[2]]
    legacy = os.path.join(root, "preview.html")
    legacy_hit = os.path.isfile(legacy) and os.path.abspath(legacy) != os.path.abspath(html_path)

    print("Preview audit: %s  (%d pages, %.1f MB)" % (slug, n_page, size_mb))
    for pid, name, ok, block, detail in checks:
        if ok:
            continue
        tag = "[BLOCK]" if block else "[WARN ]"
        print("  %s %-4s %-26s %s" % (tag, pid, name, detail))
    if legacy_hit:
        print("  [WARN ] P12  遗留裸 preview.html（R8 规定只提示不自动删）")

    if block_fail:
        print("\n[FAIL] %d 项阻断：预览器双端能力被削，按 PREVIEW_SPEC.md 修复后重跑。" % len(block_fail))
        print("       修复：改 build_preview.py 模板 → 重跑 build_preview.py → 再跑本脚本")
    else:
        print("\n[PASS] 0 项阻断 —— 双端预览门禁通过（%d 项警告请人工判断）。" % (len(warn_fail) + (1 if legacy_hit else 0)))

    if args.json:
        out_dir = os.path.join(root, "validation")
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "preview_audit.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump({
                "deck": slug,
                "html": html_path,
                "pages": n_page,
                "svg": n_svg,
                "size_mb": round(size_mb, 2),
                "blocking": len(block_fail),
                "warnings": len(warn_fail),
                "checks": [{"id": p, "name": n, "ok": o, "blocking": b, "detail": d}
                           for p, n, o, b, d in checks],
            }, f, ensure_ascii=False, indent=2)
        print("JSON: %s" % out)

    return 1 if block_fail else 0


if __name__ == "__main__":
    sys.exit(main())
