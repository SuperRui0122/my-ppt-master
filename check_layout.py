#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_layout.py — 教学课件 SVG 版式自审门禁（my-ppt-master 第 16 条）。

为什么需要它
------------
上游 `svg_quality_checker.py` 只校验**画布级**边界（是否超出 1280×720）与结构契约
（data-pptx-* 标记、分组、字号锚点等）。**卡片内部**的下列缺陷它一律不查，因此本文件
是 SKILL.md §四 / §十一.2 / §十三.1 三条规约的唯一可执行校验：

  A 行距过密  同一 <text> 内相邻 <tspan> 的 0 < dy < 0.85 × 字号  -> 文字上下重叠
              （dy = 0 是行内富文本运行，如「代码 + 绿色注释」，跳过不报）
  B 卡内越界  文本包围盒超出所在卡片右界或下界
  C 文本互压  两个文本块包围盒相交
  D 徽章越界  带 rx 的小色块内文本宽度超出色块
  E 折行过早  多行文本块中，非末行宽度 < 0.58 × 同块最宽行 -> 明显没排满就换行
              （典型成因：「下推防孤字」一次推下多个词元，把首行掏空）

用法
----
    python check_layout.py <project_path>            # 人读摘要，0 issues 时退出码 0
    python check_layout.py <project_path> --json     # 机器可读，写 validation/layout_audit.json
    python check_layout.py <project_path> --svg-dir <dir>   # 指定 SVG 目录（默认 svg_output/）

退出码：0 = 通过；1 = 存在缺陷；2 = 用法/路径错误。
"""

import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"
CJK_K, ASC_K = 1.085, 0.62          # SKILL.md §十二 保守字宽系数
TOL_RIGHT, TOL_BOTTOM = 8.0, 6.0    # 与容器边界的容差
IX_MIN, IY_MIN = 6.0, 4.0           # 判定「文本互压」的最小交叠量
BADGE_MAX_W = 160.0                 # 视作「徽章」的最大色块宽度


def tw(s, fs):
    """保守估算像素宽度：中文 1.085×fs，ASCII 0.62×fs。"""
    return sum(fs * (ASC_K if ord(c) < 0x2E80 else CJK_K) for c in s)


def iter_texts(root):
    """递归产出 (text_elem, 继承字号)，沿祖先 <g> 正确继承 font-size。"""
    def walk(node, fs):
        for ch in node:
            try:
                cur = float(ch.get("font-size")) or fs
            except (TypeError, ValueError):
                cur = fs
            if ch.tag == NS + "text":
                yield ch, cur
            if ch.tag in (NS + "g", NS + "text"):
                yield from walk(ch, cur)
    yield from walk(root, 19.5)


def runs_of(t, inherit):
    """-> [(text, baseline_y, font_size, dy, bold)]"""
    try:
        fs = float(t.get("font-size") or inherit)
    except ValueError:
        fs = inherit
    y0 = float(t.get("y") or 0)
    kids = [c for c in t if c.tag == NS + "tspan"]
    if not kids:
        return [(t.text or "", y0, fs, 0.0, t.get("font-weight") == "bold")]
    out, y = [], y0
    for c in kids:
        dy = float(c.get("dy") or 0)
        y += dy
        try:
            f = float(c.get("font-size") or fs)
        except ValueError:
            f = fs
        out.append((c.text or "", y, f, dy, c.get("font-weight") == "bold"))
    return out


def bbox(t, inherit):
    lines = runs_of(t, inherit)
    if not lines:
        return None
    x = float(t.get("x") or 0)
    anchor = t.get("text-anchor") or "start"
    w = max(tw(s, f) for s, _, f, _, _ in lines)
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    top = min(y for _, y, f, _, _ in lines) - max(f for _, _, f, _, _ in lines)
    bot = max(y for _, y, _, _, _ in lines)
    return (x0, top, x0 + w, bot, lines[0][0])


def early_break_issues(lines):
    """E 折行过早：按段落分组，只比较同段落内的非末行、非加粗行。"""
    out = []
    if len(lines) < 3:
        return out
    dys = [d for _, _, _, d, _ in lines[1:] if d > 0]
    if not dys:
        return out
    min_dy = min(dys)
    groups, cur = [], []
    for idx, (s_, y_, f_, d_, b_) in enumerate(lines):
        # 分组边界：段距明显大于行距，或遇到加粗小标题（card_stack 的 ▸ 条目头）
        if idx > 0 and (d_ > min_dy + 8 or b_) and cur:
            groups.append(cur)
            cur = []
        cur.append(idx)
    if cur:
        groups.append(cur)
    for g in groups:
        body = [i for i in g if lines[i][0].strip() and not lines[i][4]]
        if len(body) < 2:
            continue
        ws = {i: tw(lines[i][0], lines[i][2]) for i in body}
        wmax = max(ws.values())
        for i in body[:-1]:                      # 末行天然短，不判
            if ws[i] < 0.58 * wmax:
                out.append(("E 折行过早", "行宽=%.0f 段内最宽=%.0f (%.0f%%)  %s"
                            % (ws[i], wmax, 100 * ws[i] / wmax, lines[i][0][:20])))
    return out


def containers(root):
    """识别卡片 / 深色面板容器矩形。"""
    out = []
    for r in root.iter(NS + "rect"):
        try:
            w, h = float(r.get("width")), float(r.get("height"))
        except (TypeError, ValueError):
            continue
        if w >= 250 and h >= 110 and r.get("rx"):
            out.append((float(r.get("x")), float(r.get("y")), w, h))
        elif w >= 400 and h >= 180 and r.get("fill") in ("#202124", "#F8F9FA"):
            out.append((float(r.get("x")), float(r.get("y")), w, h))
    return out


def audit_file(fp):
    """返回该页的缺陷列表 [(类别, 详情)]。"""
    root = ET.parse(fp).getroot()
    cards = containers(root)
    issues, boxes = [], []
    for t, inh in iter_texts(root):
        lines = runs_of(t, inh)
        for k in range(1, len(lines)):
            txt_, _y, f, dy, _b = lines[k]
            if 0 < dy < 0.85 * f:
                issues.append(("A 行距过密", "dy=%.1f fs=%.1f  %s" % (dy, f, txt_[:24])))
        for kind, detail in early_break_issues(lines):
            issues.append((kind, detail))
        b = bbox(t, inh)
        if not b:
            continue
        boxes.append(b)
        x0, top, x1, bot, sample = b
        for cx, cy, cw, ch in cards:
            if cx - 2 <= x0 <= cx + cw and cy - 2 <= top <= cy + ch:
                if x1 > cx + cw - TOL_RIGHT:
                    issues.append(("B 卡内右越界", "+%.1f  %s" % (x1 - cx - cw, sample[:24])))
                if bot > cy + ch - TOL_BOTTOM:
                    issues.append(("B 卡内下越界", "+%.1f  %s" % (bot - cy - ch, sample[:24])))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ix = min(a[2], b[2]) - max(a[0], b[0])
            iy = min(a[3], b[3]) - max(a[1], b[1])
            if ix > IX_MIN and iy > IY_MIN:
                issues.append(("C 文本互压", "ix=%.1f iy=%.1f  %s <-> %s"
                               % (ix, iy, a[4][:16], b[4][:16])))
    for r in root.iter(NS + "rect"):
        try:
            rw = float(r.get("width"))
        except (TypeError, ValueError):
            continue
        if rw > BADGE_MAX_W or not r.get("rx"):
            continue
        rx, ry = float(r.get("x")), float(r.get("y"))
        for t, inh in iter_texts(root):
            tx = float(t.get("x") or 0)
            ty = float(t.get("y") or 0)
            if not (rx <= tx <= rx + rw and ry <= ty <= ry + 60):
                continue
            for s, _y, f, _d, _b in runs_of(t, inh):
                w = tw(s, f)
                if (t.get("text-anchor") or "start") == "middle":
                    bx0, bx1 = tx - w / 2, tx + w / 2
                else:
                    bx0, bx1 = tx, tx + w
                if bx1 > rx + rw - 2 or bx0 < rx + 2:
                    issues.append(("D 徽章越界", "box_w=%.0f text_w=%.0f  %s" % (rw, w, s[:18])))
    return issues


def main():
    ap = argparse.ArgumentParser(description="教学课件 SVG 版式自审门禁")
    ap.add_argument("project_path")
    ap.add_argument("--svg-dir", default=None, help="SVG 目录，默认 <project>/svg_output")
    ap.add_argument("--json", action="store_true", help="写 validation/layout_audit.json")
    args = ap.parse_args()

    project = os.path.abspath(args.project_path)
    svg_dir = args.svg_dir or os.path.join(project, "svg_output")
    if not os.path.isdir(svg_dir):
        print("ERROR: SVG 目录不存在: %s" % svg_dir)
        return 2
    files = sorted(glob.glob(os.path.join(svg_dir, "*.svg")))
    if not files:
        print("ERROR: %s 下没有 SVG" % svg_dir)
        return 2

    report, total = [], 0
    for fp in files:
        try:
            iss = audit_file(fp)
        except ET.ParseError as exc:
            iss = [("X XML 解析失败", str(exc))]
        if iss:
            report.append({"file": os.path.basename(fp),
                           "issues": [{"kind": k, "detail": d} for k, d in iss]})
            total += len(iss)

    # A/B/C/D 为阻断级；E 折行过早为启发式 advisory（不阻断，人工判断）
    block_items, adv_items = [], []
    for item in report:
        for it in item["issues"]:
            (adv_items if it["kind"].startswith("E ") else block_items).append((item["file"], it))
    n_block, n_adv = len(block_items), len(adv_items)

    print("Layout audit: %d page(s), %d blocking issue(s), %d advisory warning(s)"
          % (len(files), n_block, n_adv))
    seen = set()
    for label, bucket in (("[BLOCK]", block_items), ("[WARN ]", adv_items)):
        for fn, it in bucket:
            key = (fn, it["kind"], it["detail"][:26])
            if key in seen:
                continue
            seen.add(key)
            print("  %s %-44s %-12s %s" % (label, fn[:42], it["kind"], it["detail"]))
    if n_block:
        print("\n[FAIL] 存在阻断级版式缺陷，按 SKILL.md §13.5 阻断交付。")
    else:
        print("\n[PASS] 0 blocking issue —— 版式自审门禁通过（advisory 项请人工判断）。")

    if args.json:
        out_dir = os.path.join(project, "validation")
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "layout_audit.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"pages": len(files),
                       "blocking": n_block, "advisory": n_adv,
                       "report": report}, f, ensure_ascii=False, indent=2)
        print("JSON: %s" % out)
    return 1 if n_block else 0


if __name__ == "__main__":
    sys.exit(main())
