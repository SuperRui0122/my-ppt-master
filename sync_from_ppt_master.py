# -*- coding: utf-8 -*-
"""
my-ppt-master 回流工具  (v2.0.0)

把在 ppt-master 里现场改好的 google-teaching 品牌模板，「回流」到本仓库。

什么时候用：
  你直接在 ppt-master/skills/ppt-master/templates/brands/google-teaching/ 里
  调好了品牌样式（比如改了一处配色或字号），想把它固化成正式版本时。

⚠️ 方向提醒：
  本仓库 my-ppt-master 是唯一权威源。正常情况下改动应该发生在**本仓库**，
  然后由 apply.py 单向复制到 ppt-master。本脚本是反向的应急通道，
  因此默认只做「预览」，必须显式加 --yes 才会真正写入。

用法:
  python sync_from_ppt_master.py              # 只预览差异，不写盘
  python sync_from_ppt_master.py --yes        # 确认回流
  python sync_from_ppt_master.py --ppt-master <路径>
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from apply import BRAND_DST_REL, BRAND_SRC, find_ppt_master  # noqa: E402

BRAND_ID = "google-teaching"


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def add(msg: str) -> None:
    print(f"  [+]    {msg}")


def same(msg: str) -> None:
    print(f"  [=]    {msg}")


def warn(msg: str) -> None:
    print(f"  [!]    {msg}")


def bad(msg: str) -> None:
    print(f"  [X]    {msg}")


def compare(src: Path, dst: Path) -> tuple[list[str], list[str], list[str]]:
    """返回 (仅上游有, 内容不同, 仅本仓库有)。"""
    only_up: list[str] = []
    different: list[str] = []
    only_here: list[str] = []

    src_files = {p.relative_to(src).as_posix(): p for p in src.rglob("*") if p.is_file()}
    dst_files = {p.relative_to(dst).as_posix(): p for p in dst.rglob("*") if p.is_file()}

    for rel, up_path in sorted(src_files.items()):
        here_path = dst_files.get(rel)
        if here_path is None:
            only_up.append(rel)
        elif not filecmp.cmp(up_path, here_path, shallow=False):
            different.append(rel)
    for rel in sorted(dst_files):
        if rel not in src_files:
            only_here.append(rel)
    return only_up, different, only_here


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sync_from_ppt_master.py",
        description="把 ppt-master 中的 google-teaching 品牌模板回流到本仓库",
    )
    parser.add_argument("--yes", action="store_true", help="确认写入（不加则只预览）")
    parser.add_argument("--ppt-master", metavar="PATH", help="手动指定上游仓库根目录")
    args = parser.parse_args(argv)

    root = find_ppt_master(args.ppt_master)
    if root is None:
        bad("未找到 ppt-master 仓库。请用 --ppt-master <路径> 指定。")
        return 2

    upstream_brand = root / BRAND_DST_REL
    print(f"上游品牌目录：{upstream_brand}")
    print(f"本仓库目录  ：{BRAND_SRC}")

    if not upstream_brand.is_dir():
        bad("上游没有安装 google-teaching 品牌目录。请先运行：python apply.py")
        return 2

    only_up, different, only_here = compare(upstream_brand, BRAND_SRC)

    print("\n── 差异 ───────────────────────────────────────────────────────")
    if not (only_up or different or only_here):
        same("两边完全一致，无需回流。")
        return 0
    for rel in only_up:
        print(f"  [上游新增] {rel}")
    for rel in different:
        print(f"  [内容不同] {rel}")
    for rel in only_here:
        print(f"  [本仓库独有] {rel}")

    if not args.yes:
        print("\n  [!]    以上仅为预览。确认要回流请重跑并加上 --yes：")
        print("            python sync_from_ppt_master.py --yes")
        return 0

    print("\n── 回流 ───────────────────────────────────────────────────────")
    for rel in only_up + different:
        src = upstream_brand / rel
        dst = BRAND_SRC / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        add(f"已覆盖：{rel}")
    if only_here:
        warn("以下文件仅本仓库有，不会被删除（如需删除请手工处理）：")
        for rel in only_here:
            print(f"        {rel}")

    print()
    ok("回流完成。请检查差异后提交：")
    print("        git -C . diff")
    print("        python push.py -m \"回流品牌模板改动\"")
    print("        python apply.py      # 确认单向同步仍然一致")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
