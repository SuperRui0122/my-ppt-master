#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一册逐页 SVG 课件打包成「单文件、离线可用」的翻页预览器。

这是 my-ppt-master 定制层自带的查看工具，只读课件产物，不改任何源文件。

用法（在任意目录下均可）：
    python build_preview.py                          # 从当前目录向上找 svg_output/
    python build_preview.py <项目目录>                # 指定某一册
    python build_preview.py --all                    # 批量处理 projects/ 下所有册
    python build_preview.py <项目目录> --open         # 生成后打开浏览器
    python build_preview.py <项目目录> --title "册名"  # 手动指定册名

约定（缺省项可不存在）：
    项目目录/svg_output/*.svg     必需，文件名形如 01_cover.svg（数字前缀决定页序）
    项目目录/notes/NN_slide.md    可选，逐页讲稿备注
    项目目录/design_spec.md       可选，用于提取册名与每页标题

产出：
    项目目录/preview.html

为什么做成「自包含单文件」：
    不能简单用 <img src="svg_output/01.svg"> 引用 —— SVG 内部的
    <image href="../images/x.png"> 在 file:// 下可能被浏览器拦截。所以这里做双重内联：
    SVG 里的图片先转 base64 data URI，整个 SVG 再编码成 data:image/svg+xml;base64
    放进 JS 数组。结果是零外部依赖：双击即开、无跨源问题、可直接拷给别人。

姊妹副本：用户级技能 ~/.workbuddy-ai/skills/svg-deck-preview/scripts/build_preview.py
         改动本文件时请同步那一份（反之亦然）。
"""
from __future__ import annotations

import argparse
import base64
import json
import pathlib
import re
import sys
import webbrowser

MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

IMAGE_RE = re.compile(r'(<image\b[^>]*?\b(?:xlink:href|href)=")([^"]+)(")')
TITLE_IN_SVG = re.compile(r'<text\b[^>]*\by="82"[^>]*>(.*?)</text>', re.S)
ROSTER_ROW = re.compile(
    r"^\|\s*(P\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
    re.M,
)


# ------------------------------------------------------------------ 目录定位

def find_project(start: pathlib.Path, max_up: int = 8) -> pathlib.Path | None:
    """从 start 起向上逐级查找含 svg_output/ 的目录。"""
    cur = start.resolve()
    for _ in range(max_up + 1):
        if (cur / "svg_output").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def find_decks(start: pathlib.Path, max_up: int = 8) -> list[pathlib.Path]:
    """定位 projects/ 根，返回其下所有含 svg_output/ 的册目录。"""
    cur = start.resolve()
    root: pathlib.Path | None = None
    for _ in range(max_up + 1):
        if cur.name == "projects" and cur.is_dir():
            root = cur
            break
        if (cur / "projects").is_dir():
            root = cur / "projects"
            break
        if cur.parent == cur:
            break
        cur = cur.parent
    if root is None:
        return []
    return sorted({p.parent for p in root.glob("*/*/svg_output") if p.is_dir()})


# ------------------------------------------------------------------ 元数据

def guess_title(root: pathlib.Path) -> str:
    """从 design_spec.md 的 H1 猜册名，失败则用目录名。"""
    spec = root / "design_spec.md"
    if spec.exists():
        text = spec.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m:
            title = m.group(1).strip()
            title = re.sub(
                r"\s*[-—–|:：]\s*Design\s*Spec\s*$", "", title, flags=re.I
            ).strip()
            if title:
                return title
    return root.name


def load_roster(spec: pathlib.Path) -> dict[int, str]:
    if not spec.exists():
        return {}
    out: dict[int, str] = {}
    for pid, _kind, _sec, title in ROSTER_ROW.findall(
        spec.read_text(encoding="utf-8", errors="ignore")
    ):
        try:
            out[int(pid[1:])] = title.strip()
        except ValueError:
            continue
    return out


def load_note(notes_dir: pathlib.Path, page_no: int) -> str:
    f = notes_dir / ("%02d_slide.md" % page_no)
    if not f.exists():
        return ""
    lines = f.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
    return "\n".join(ln for ln in lines[1:] if ln.strip()).strip()


# ------------------------------------------------------------------ 构建

def build(root: pathlib.Path, title: str, *, quiet: bool = False) -> int:
    svg_dir = root / "svg_output"
    notes_dir = root / "notes"
    out = root / "preview.html"

    if not svg_dir.is_dir():
        print("找不到 svg_output 目录：%s" % svg_dir, file=sys.stderr)
        return 1

    svg_files = sorted(svg_dir.glob("*.svg"))
    if not svg_files:
        print("svg_output 里没有 .svg：%s" % svg_dir, file=sys.stderr)
        return 1

    roster = load_roster(root / "design_spec.md")
    uri_cache: dict[str, str] = {}
    missing: list[str] = []

    def to_data_uri(p: pathlib.Path) -> str:
        key = str(p)
        if key not in uri_cache:
            mime = MIME.get(p.suffix.lower(), "application/octet-stream")
            uri_cache[key] = "data:%s;base64,%s" % (
                mime,
                base64.b64encode(p.read_bytes()).decode("ascii"),
            )
        return uri_cache[key]

    def inline_images(text: str) -> str:
        def repl(m: re.Match[str]) -> str:
            href = m.group(2)
            if href.startswith("data:"):
                return m.group(0)
            target = (svg_dir / href).resolve()
            if not target.exists():
                missing.append(href)
                return m.group(0)
            return m.group(1) + to_data_uri(target) + m.group(3)

        return IMAGE_RE.sub(repl, text)

    pages = []
    for f in svg_files:
        try:
            page_no = int(f.name.split("_")[0])
        except ValueError:
            continue
        raw = f.read_text(encoding="utf-8", errors="ignore")

        title_text = ""
        m = TITLE_IN_SVG.search(raw)
        if m:
            title_text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title_text:
            title_text = roster.get(page_no, f.stem)
        title_text = re.sub(r"^\d+(?:\.\d+)*\s*", "", title_text).strip() or f.stem

        inlined = inline_images(raw)
        pages.append(
            {
                "n": page_no,
                "file": f.name,
                "title": title_text,
                "src": "data:image/svg+xml;base64,"
                + base64.b64encode(inlined.encode("utf-8")).decode("ascii"),
                "note": load_note(notes_dir, page_no),
            }
        )

    if not pages:
        print("没有解析出任何页面。", file=sys.stderr)
        return 1

    pages.sort(key=lambda p: p["n"])
    html = TEMPLATE.replace("__DECK_TITLE__", title).replace(
        "__PAGES_JSON__", json.dumps(pages, ensure_ascii=False, separators=(",", ":"))
    )
    out.write_text(html, encoding="utf-8")

    if not quiet:
        print("  %-46s %3d 页  %5.1f MB" % (root.name[:46], len(pages),
                                            out.stat().st_size / 1024 / 1024))
    if missing:
        print("    警告：%d 处图片引用未找到 -> %s"
              % (len(missing), sorted(set(missing))), file=sys.stderr)
    return 0


# ------------------------------------------------------------------ 模板

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__DECK_TITLE__ · 翻页预览</title>
<style>
  :root{
    --bg:#F1F3F4; --panel:#FFFFFF; --line:#DADCE0; --line2:#E8EAED;
    --ink:#202124; --ink2:#3C4043; --ink3:#5F6368; --muted:#9AA0A6;
    --blue:#4285F4; --blue-soft:#E8F0FE;
  }
  *{box-sizing:border-box;}
  html,body{height:100%;margin:0;}
  body{
    font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;
    background:var(--bg); color:var(--ink);
    display:flex; flex-direction:column; overflow:hidden;
    -webkit-font-smoothing:antialiased;
  }
  header{
    height:58px; flex:none; display:flex; align-items:center; gap:16px;
    padding:0 18px; background:var(--panel); border-bottom:1px solid var(--line);
  }
  .brand{font-size:15px;font-weight:700;color:var(--ink2);white-space:nowrap;
         max-width:30vw; overflow:hidden; text-overflow:ellipsis;}
  .cur-title{
    flex:1; min-width:0; font-size:15px; color:var(--ink3);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }
  .cur-title b{color:var(--ink); font-weight:700;}
  .tools{display:flex; gap:8px; flex:none;}
  button{
    font-family:inherit; font-size:13px; color:var(--ink2);
    background:var(--panel); border:1px solid var(--line); border-radius:8px;
    padding:7px 12px; cursor:pointer; transition:.15s; white-space:nowrap;
  }
  button:hover{background:var(--blue-soft); border-color:var(--blue); color:var(--blue);}
  button.on{background:var(--blue-soft); border-color:var(--blue); color:var(--blue); font-weight:700;}
  button:disabled{opacity:.4; cursor:not-allowed;}
  button:disabled:hover{background:var(--panel); border-color:var(--line); color:var(--ink2);}
  main{flex:1; min-height:0; display:flex;}
  #side{
    width:196px; flex:none; background:var(--panel); border-right:1px solid var(--line);
    overflow-y:auto; overflow-x:hidden; padding:12px 10px; scrollbar-width:thin;
  }
  #side.hide{display:none;}
  .thumb{
    position:relative; margin:0 0 10px; border:2px solid transparent; border-radius:8px;
    overflow:hidden; cursor:pointer; background:#fff; box-shadow:0 1px 3px rgba(0,0,0,.10);
    transition:.15s;
  }
  .thumb:hover{border-color:var(--blue); transform:translateY(-1px);}
  .thumb.active{border-color:var(--blue); box-shadow:0 0 0 3px var(--blue-soft);}
  .thumb img{display:block; width:100%; aspect-ratio:16/9; object-fit:contain; background:#fff;}
  .thumb .cap{
    position:absolute; left:0; right:0; bottom:0; padding:2px 6px;
    font-size:11px; color:#fff; background:linear-gradient(transparent,rgba(0,0,0,.62));
    display:flex; gap:6px; align-items:baseline;
  }
  .thumb .cap b{font-weight:700;}
  .thumb .cap em{font-style:normal; opacity:.9; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
  #stage{
    flex:1; min-width:0; display:flex; align-items:center; justify-content:center;
    padding:20px; overflow:auto;
  }
  #page{
    max-width:100%; max-height:100%; width:auto; height:auto;
    background:#fff; border-radius:6px; box-shadow:0 6px 28px rgba(0,0,0,.16);
  }
  #stage.actual #page{max-width:none; max-height:none;}
  #notePanel{
    width:340px; flex:none; background:var(--panel); border-left:1px solid var(--line);
    overflow-y:auto; padding:18px 18px 26px;
  }
  #notePanel.hide{display:none;}
  #notePanel h3{margin:0 0 12px; font-size:13px; font-weight:700; color:var(--blue); letter-spacing:.5px;}
  #noteBody{font-size:14px; line-height:1.85; color:var(--ink2); white-space:pre-wrap;}
  #noteBody .empty{color:var(--muted);}
  footer{
    height:60px; flex:none; display:flex; align-items:center; justify-content:center;
    gap:14px; background:var(--panel); border-top:1px solid var(--line);
  }
  .pager{display:flex; align-items:center; gap:6px; font-size:14px; color:var(--ink3);}
  .pager input{
    width:64px; padding:6px 8px; font-family:inherit; font-size:14px; text-align:center;
    color:var(--ink); background:var(--bg); border:1px solid var(--line); border-radius:8px;
  }
  .pager input:focus{outline:none; border-color:var(--blue); background:#fff;}
  .pager input::-webkit-outer-spin-button,
  .pager input::-webkit-inner-spin-button{-webkit-appearance:none; margin:0;}
  .pager input[type=number]{-moz-appearance:textfield;}
  .hint{position:fixed; right:16px; bottom:72px; font-size:12px; color:var(--muted);
        background:rgba(255,255,255,.94); border:1px solid var(--line2); border-radius:8px;
        padding:8px 12px; line-height:1.7; pointer-events:none; transition:opacity .4s;}
  .hint.fade{opacity:0;}
</style>
</head>
<body>

<header>
  <div class="brand" title="__DECK_TITLE__">__DECK_TITLE__</div>
  <div class="cur-title" id="curTitle"></div>
  <div class="tools">
    <button id="btnSide" title="显示/隐藏缩略图 (S)">缩略图</button>
    <button id="btnNote" title="显示/隐藏讲稿备注 (N)">讲稿</button>
    <button id="btnFit" title="适应窗口 / 原始大小 (Z)">适应窗口</button>
    <button id="btnFull" title="全屏 (F)">全屏</button>
  </div>
</header>

<main>
  <aside id="side"><div id="thumbs"></div></aside>
  <section id="stage"><img id="page" alt=""></section>
  <aside id="notePanel" class="hide"><h3>演讲讲稿与演示者备注</h3><div id="noteBody"></div></aside>
</main>

<footer>
  <button id="prev">‹ 上一页</button>
  <div class="pager">
    <input id="pagerInput" type="number" min="1" step="1" value="1">
    <span>/ <b id="total">0</b> 页</span>
  </div>
  <button id="next">下一页 ›</button>
</footer>

<div class="hint" id="hint">
  ← → / 空格 翻页 ｜ Home / End 首末页<br>
  S 缩略图 ｜ N 讲稿 ｜ Z 缩放 ｜ F 全屏
</div>

<script>
const PAGES = __PAGES_JSON__;
const TOTAL = PAGES.length;

const $ = id => document.getElementById(id);
const elTitle = $('curTitle'), elPage = $('page'), elThumbs = $('thumbs');
const elSide = $('side'), elNotePanel = $('notePanel'), elNoteBody = $('noteBody');
const elInput = $('pagerInput'), elTotal = $('total');
const btnPrev = $('prev'), btnNext = $('next'), elStage = $('stage');

let cur = 0;
const thumbEls = [];

PAGES.forEach((p, i) => {
  const d = document.createElement('div');
  d.className = 'thumb';
  d.title = p.n + '. ' + p.title;

  const im = document.createElement('img');
  im.loading = 'lazy';
  im.decoding = 'async';
  im.src = p.src;
  im.alt = p.title;

  const cap = document.createElement('div');
  cap.className = 'cap';
  const b = document.createElement('b');
  b.textContent = String(p.n).padStart(2, '0');
  const em = document.createElement('em');
  em.textContent = p.title;
  cap.append(b, em);

  d.append(im, cap);
  d.addEventListener('click', () => go(i));
  elThumbs.append(d);
  thumbEls.push(d);
});

function render() {
  const p = PAGES[cur];
  elPage.src = p.src;
  elPage.alt = p.n + '. ' + p.title;
  elTitle.innerHTML = '<b>' + String(p.n).padStart(2, '0') + ' / ' + TOTAL + '</b> &nbsp; ' + p.title;
  elInput.value = p.n;
  btnPrev.disabled = cur === 0;
  btnNext.disabled = cur === TOTAL - 1;

  elNoteBody.innerHTML = '';
  if (p.note) {
    elNoteBody.textContent = p.note;
  } else {
    const s = document.createElement('div');
    s.className = 'empty';
    s.textContent = '（本页暂无讲稿备注）';
    elNoteBody.append(s);
  }

  thumbEls.forEach((el, i) => el.classList.toggle('active', i === cur));
  const active = thumbEls[cur];
  if (active) active.scrollIntoView({block: 'nearest', behavior: 'smooth'});
}

function go(i) {
  cur = Math.max(0, Math.min(TOTAL - 1, i));
  render();
}

btnPrev.addEventListener('click', () => go(cur - 1));
btnNext.addEventListener('click', () => go(cur + 1));

elInput.addEventListener('change', () => {
  const v = parseInt(elInput.value, 10);
  if (!isNaN(v)) go(v - 1);
  else elInput.value = PAGES[cur].n;
});
elInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') elInput.blur();
  e.stopPropagation();
});

function toggle(el) { el.classList.toggle('hide'); }

$('btnSide').addEventListener('click', function () {
  toggle(elSide); this.classList.toggle('on', !elSide.classList.contains('hide'));
});
$('btnNote').addEventListener('click', function () {
  toggle(elNotePanel); this.classList.toggle('on', !elNotePanel.classList.contains('hide'));
});
$('btnFit').addEventListener('click', function () {
  elStage.classList.toggle('actual');
  this.textContent = elStage.classList.contains('actual') ? '原始大小' : '适应窗口';
});
$('btnFull').addEventListener('click', () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen();
});
elStage.addEventListener('click', () => elStage.classList.toggle('actual'));

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  switch (e.key) {
    case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ':
      e.preventDefault(); go(cur + 1); break;
    case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
      e.preventDefault(); go(cur - 1); break;
    case 'Home': e.preventDefault(); go(0); break;
    case 'End': e.preventDefault(); go(TOTAL - 1); break;
    case 'f': case 'F':
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
      break;
    case 's': case 'S': $('btnSide').click(); break;
    case 'n': case 'N': $('btnNote').click(); break;
    case 'z': case 'Z': $('btnFit').click(); break;
  }
});

elTotal.textContent = TOTAL;
$('btnSide').classList.add('on');
render();
setTimeout(() => $('hint').classList.add('fade'), 6000);
</script>
</body>
</html>
"""


# ------------------------------------------------------------------ 入口

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="把逐页 SVG 课件打包成单文件翻页预览器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("directory", nargs="?", default=None,
                    help="含 svg_output/ 的项目目录；省略则从当前目录向上查找")
    ap.add_argument("--all", action="store_true",
                    help="批量处理 projects/ 下所有含 svg_output/ 的册")
    ap.add_argument("--title", default=None, help="预览器左上角册名")
    ap.add_argument("--open", action="store_true", help="生成后用默认浏览器打开")
    args = ap.parse_args(argv)

    start = pathlib.Path(args.directory).resolve() if args.directory else pathlib.Path.cwd()

    if args.all:
        decks = find_decks(start)
        if not decks:
            print("没找到 projects/ 目录，或其中没有任何含 svg_output/ 的册。", file=sys.stderr)
            return 1
        print("批量生成 %d 册预览：" % len(decks))
        rc = 0
        for deck in decks:
            rc |= build(deck, args.title or guess_title(deck), quiet=False)
        print("完成。")
        return rc

    root = find_project(start)
    if root is None:
        print("从 %s 向上没找到含 svg_output/ 的目录。\n"
              "请显式指定项目目录，例如：\n"
              "  python build_preview.py D:\\南开\\PPT-master\\ppt-master\\projects\\<课程>\\<册>"
              % start, file=sys.stderr)
        return 1

    title = args.title or guess_title(root)
    print("册名：%s" % title)
    code = build(root, title, quiet=False)
    if code == 0:
        print("输出：%s" % (root / "preview.html"))
        if args.open:
            webbrowser.open((root / "preview.html").as_uri())
    return code


if __name__ == "__main__":
    raise SystemExit(main())
