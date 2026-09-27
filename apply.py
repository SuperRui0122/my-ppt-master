# -*- coding: utf-8 -*-
"""
my-ppt-master 安装器 / 卸载器  (v2.0.0)

把本仓库的个性化配置安全、幂等地挂载到 ppt-master 上游仓库。

它只做三件事：
  1. 复制 google-teaching 品牌目录到上游 templates/brands/
  2. 调用上游官方 register_template.py 重新生成 brands_index.json
  3. 向上游 skills/ppt-master/SKILL.md 注入一段「用户规约指针」标记块

设计约束（很重要，请不要改）：
  * 绝不向 AGENTS.md / CLAUDE.md 追加写 —— 那两个是上游受跟踪文件，
    一旦改动，git pull 必然冲突，违背「永不冲突」的核心承诺。
  * 绝不手写 brands_index.json —— 它由上游 register_template.py 生成，
    手写会因为 schema 不一致而静默失效（见 README「历史缺陷」一节）。
  * 只触碰上游的 2 个受跟踪文件（SKILL.md 与 brands_index.json），
    且改动完全可逆 —— update.py 会在 git pull 前把它们还原。

用法:
  python apply.py                       # 安装 / 重新安装（幂等，可重复运行）
  python apply.py --check               # 只体检，不写盘
  python apply.py --dry-run             # 打印将要做的改动，不写盘
  python apply.py --uninstall           # 干净卸载（还原上游文件 + 删除品牌目录）
  python apply.py --ppt-master <路径>   # 手动指定上游仓库根目录
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "2.0.0"

# ──────────────────────────────────────────────────────────────────────
# 上游仓库内的相对路径
# ──────────────────────────────────────────────────────────────────────
SKILL_DIR_REL = Path("skills") / "ppt-master"
SKILL_MD_REL = SKILL_DIR_REL / "SKILL.md"
BRANDS_DIR_REL = SKILL_DIR_REL / "templates" / "brands"
BRAND_ID = "google-teaching"
BRAND_DST_REL = BRANDS_DIR_REL / BRAND_ID
INDEX_REL = BRANDS_DIR_REL / "brands_index.json"
REGISTER_REL = SKILL_DIR_REL / "scripts" / "register_template.py"
GUARD_REL = SKILL_DIR_REL / "scripts" / "attribution_guard.py"

# 本安装器会改动的【上游受版本控制】文件。
# update.py 会在 git pull 之前把它们 git checkout 还原，
# 因此上游更新与个性化定制永远不会冲突。
TOUCHED_TRACKED = (SKILL_MD_REL, INDEX_REL)

# ──────────────────────────────────────────────────────────────────────
# 注入标记（幂等靠这些标记定位）
#
# 向上游 SKILL.md 注入两个受管块，顺序固定：
#   1. 用户红线（RED_LINES.md）—— 最高优先级，放最前面
#   2. 用户教学规约指针 —— 指向本仓库的 SKILL.md / CUSTOM_STYLE_SPEC.md
#
# 实现方式：先把所有受管块剥掉，再把两个块整体插到锚点之前。
# 这样顺序恒定、无残留，重复运行结果完全一致。
# ──────────────────────────────────────────────────────────────────────
ANCHOR = "## Mandatory Load Order"

RED_LINES_BEGIN = "<!-- BEGIN USER RED LINES (managed by my-ppt-master/apply.py) -->"
RED_LINES_END = "<!-- END USER RED LINES -->"
POINTER_BEGIN = "<!-- BEGIN MY-PPT-MASTER POINTER (managed by my-ppt-master/apply.py) -->"
POINTER_END = "<!-- END MY-PPT-MASTER POINTER -->"

# 剥离时按「前缀」匹配，以便同时清理旧版 apply_user_rule.py 注入的块
MANAGED_BLOCKS = (
    ("<!-- BEGIN USER RED LINES", RED_LINES_END),
    ("<!-- BEGIN MY-PPT-MASTER POINTER", POINTER_END),
)

HERE = Path(__file__).resolve().parent
BRAND_SRC = HERE / BRAND_ID
RED_LINES_SRC = HERE / "RED_LINES.md"


# ──────────────────────────────────────────────────────────────────────
# 基础工具
# ──────────────────────────────────────────────────────────────────────
def read_text(path: Path) -> str:
    """读文本，统一 LF 行尾、剥离 BOM。"""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def read_text_eol(path: Path) -> tuple[str, str]:
    """读文本，返回 (LF 规范化文本, 原文件的行尾风格)。

    Windows 上 git 常以 core.autocrlf=true 检出 CRLF。若我们改完写回 LF，
    git 会把文件判为「已修改」，进而让后续 git pull 失败。所以必须保留原行尾。
    """
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    eol = "\r\n" if crlf > lf_only else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text, eol


def write_text(path: Path, text: str, eol: str = "\n") -> None:
    """写文本，UTF-8 无 BOM，按 eol 还原行尾风格。"""
    data = text.replace("\r\n", "\n")
    if eol == "\r\n":
        data = data.replace("\n", "\r\n")
    path.write_bytes(data.encode("utf-8"))


def dir_fingerprint(root: Path) -> str:
    """目录内容指纹（相对路径 + 文件字节），用于判断品牌目录是否需要重装。"""
    if not root.is_dir():
        return "<missing>"
    digest = hashlib.sha256()
    for item in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(item.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:16]


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


# ──────────────────────────────────────────────────────────────────────
# 定位上游仓库
# ──────────────────────────────────────────────────────────────────────
def looks_like_ppt_master(root: Path) -> bool:
    return (root / REGISTER_REL).is_file() and (root / SKILL_MD_REL).is_file()


def find_ppt_master(explicit: str | None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env = os.environ.get("PPT_MASTER_HOME")
    if env:
        candidates.append(Path(env).expanduser())
    candidates += [
        HERE.parent / "ppt-master",           # 推荐的同级布局
        HERE / "ppt-master",
        HERE.parent / "PPT-master" / "ppt-master",
        Path.cwd() / "ppt-master",
    ]
    for cand in candidates:
        try:
            resolved = cand.resolve()
        except OSError:
            continue
        if looks_like_ppt_master(resolved):
            return resolved
    return None


def resolve_or_die(explicit: str | None) -> Path:
    root = find_ppt_master(explicit)
    if root:
        print(f"[*] 上游 ppt-master 仓库：{root}")
        return root
    bad("未找到 ppt-master 仓库。")
    print("      已尝试的位置：")
    for cand in (HERE.parent / "ppt-master", HERE / "ppt-master",
                 HERE.parent / "PPT-master" / "ppt-master", Path.cwd() / "ppt-master"):
        print(f"        - {cand}")
    print("\n      请用 --ppt-master <路径> 指定，或把 my-ppt-master 放到 ppt-master 的同级目录。")
    sys.exit(2)


# ──────────────────────────────────────────────────────────────────────
# 前置检查
# ──────────────────────────────────────────────────────────────────────
def preflight() -> None:
    """检查运行环境与源文件是否齐备。"""
    problems: list[str] = []

    if not BRAND_SRC.is_dir():
        problems.append(f"缺少品牌源目录：{BRAND_SRC}")
    elif not (BRAND_SRC / "templates" / "design_spec.md").is_file():
        problems.append(f"品牌源目录缺少 templates/design_spec.md：{BRAND_SRC}")

    if not RED_LINES_SRC.is_file():
        problems.append(f"缺少红线文件：{RED_LINES_SRC}")

    if not (HERE / "SKILL.md").is_file():
        problems.append(f"缺少教学规约：{HERE / 'SKILL.md'}")

    if sys.version_info < (3, 8):
        problems.append(f"Python 版本过低：{sys.version.split()[0]}（需要 3.8+）")

    # 上游 register_template.py 依赖 PyYAML
    try:
        import yaml  # noqa: F401
    except ImportError:
        problems.append(
            "当前 Python 缺少 PyYAML（上游 register_template.py 需要）。\n"
            f"        请执行：{Path(sys.executable).name} -m pip install pyyaml\n"
            f"        当前解释器：{sys.executable}"
        )

    if problems:
        bad("环境检查未通过：")
        for p in problems:
            print(f"        - {p}")
        sys.exit(3)
    ok(f"环境检查通过（Python {sys.version.split()[0]}，{sys.executable}）")


# ──────────────────────────────────────────────────────────────────────
# 注入块
# ──────────────────────────────────────────────────────────────────────
def build_red_lines() -> str:
    body = read_text(RED_LINES_SRC).strip("\n")
    return f"{RED_LINES_BEGIN}\n{body}\n{RED_LINES_END}"


def build_pointer() -> str:
    src = HERE.as_posix()
    return f"""{POINTER_BEGIN}
## 用户教学规约（最高优先级 · 由 my-ppt-master 注入）

> 本节由 `my-ppt-master/apply.py` 自动维护，**请勿手工编辑**。
> 上游 `git pull` 后重跑 `update.bat`（或 `python apply.py`）即可恢复本节。
> 卸载：`python apply.py --uninstall`

在开始任何 PPT 生成 / 修改任务之前，**必须**先读取并全程遵守以下两份文件：

| 文件 | 作用 |
|---|---|
| `{src}/SKILL.md` | 教学课件排版与动效规约（15 条强制规则：B1 双轨标题体系、四色轮换、章节过渡页、Z-Order 防遮挡门禁、拆页阈值、AST 语法门禁等） |
| `{src}/CUSTOM_STYLE_SPEC.md` | 安装方式、双机协作流程、故障排查与历史缺陷说明 |

**优先级规则**：

1. 上述 `SKILL.md` 中的规则**优先于本文件其余部分的默认取值**，包括 Quick 模式的提速默认行为（不得因为「用户没说要慢」就跳过 SVG 中间产物或确认门）。
2. 与本文件其它章节冲突时，一律以 `{src}/SKILL.md` 为准。
3. 涉及考核方式、评分标准、学分政策的内容，一律忠于用户的源教案文档，**禁止自行发挥或补全**。

若上述文件不存在，说明用户尚未完成安装：请提示用户运行
`python "{src}/apply.py"` 后重试，**不要静默忽略本节**。

{POINTER_END}"""


def build_combined() -> str:
    """两个受管块的整体内容，顺序固定：红线在前，指针在后。"""
    return f"{build_red_lines()}\n\n{build_pointer()}\n"


def strip_managed(text: str) -> tuple[str, int]:
    """剥掉所有受管块（含旧版 apply_user_rule.py 注入的），返回 (干净文本, 剥掉几个)。"""
    removed = 0
    while True:
        hit = None
        for begin_prefix, end_mark in MANAGED_BLOCKS:
            idx = text.find(begin_prefix)
            if idx != -1 and (hit is None or idx < hit[0]):
                end_idx = text.find(end_mark, idx)
                if end_idx != -1:
                    hit = (idx, end_idx + len(end_mark))
        if hit is None:
            break
        tail_raw = text[hit[1]:]
        # 旧版 apply_user_rule.py 会在 END 标记之后留下一行 "---" 分隔线，一并清掉
        tail_raw = re.sub(r"^\s*---[ \t]*\n", "", tail_raw, count=1)
        head = text[:hit[0]].rstrip("\n")
        tail = tail_raw.lstrip("\n")
        text = f"{head}\n\n{tail}" if head else tail
        removed += 1
    return text, removed


def inject_managed(text: str) -> tuple[str, str]:
    """先剥离所有受管块，再把两个块整体插到锚点之前。返回 (新文本, 动作)。"""
    clean, removed = strip_managed(text)
    lines = clean.split("\n")

    insert_at = None
    for idx, line in enumerate(lines):
        if line.strip() == ANCHOR:
            insert_at = idx
            break
    if insert_at is None:
        raise RuntimeError(
            f"在上游 SKILL.md 中找不到锚点 {ANCHOR!r}。\n"
            "        上游结构可能已变更，请人工检查后更新 apply.py 的 ANCHOR 常量。"
        )

    merged = lines[:insert_at] + build_combined().split("\n") + lines[insert_at:]
    new_text = "\n".join(merged)
    return new_text, ("replaced" if removed else "inserted")


# ──────────────────────────────────────────────────────────────────────
# 品牌注册（调用上游官方工具）
# ──────────────────────────────────────────────────────────────────────
def index_has_brand(root: Path) -> bool:
    index = root / INDEX_REL
    if not index.is_file():
        return False
    try:
        data = json.loads(read_text(index))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    return isinstance(data, dict) and BRAND_ID in data


def _report(proc: subprocess.CompletedProcess[str]) -> None:
    for stream in (proc.stdout, proc.stderr):
        if stream and stream.strip():
            for line in stream.strip().split("\n"):
                print(f"        {line}")


def run_register(root: Path, *, dry_run: bool = False) -> bool:
    cmd = [sys.executable, str(root / REGISTER_REL), BRAND_ID, "--kind", "brand"]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        bad(f"上游 register_template.py 执行失败（exit {proc.returncode}）")
        _report(proc)
        return False
    return True


def run_register_rebuild(root: Path) -> bool:
    """删除品牌后重建全量索引，把 google-teaching 条目清掉。"""
    cmd = [sys.executable, str(root / REGISTER_REL), "--kind", "brand", "--rebuild-all"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        _report(proc)
    return proc.returncode == 0


def run_guard(root: Path) -> bool:
    cmd = [sys.executable, str(root / GUARD_REL)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        bad(f"上游完整性门 attribution_guard.py 未通过（exit {proc.returncode}）")
        _report(proc)
        return False
    return True


# ──────────────────────────────────────────────────────────────────────
# 三个动作
# ──────────────────────────────────────────────────────────────────────
def do_install(root: Path, *, dry_run: bool) -> int:
    print("\n── 1/4  安装 google-teaching 品牌目录 ─────────────────────────")
    dst = root / BRAND_DST_REL
    if dir_fingerprint(BRAND_SRC) == dir_fingerprint(dst):
        same(f"品牌目录已是最新：{dst}")
    elif dry_run:
        add(f"将复制 {BRAND_SRC} -> {dst}")
    else:
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(BRAND_SRC, dst)
        add(f"已复制品牌目录：{dst}")

    print("\n── 2/4  注册品牌索引（调用上游官方工具） ──────────────────────")
    if dry_run:
        if not dst.is_dir():
            warn("品牌目录尚未安装，无法预演注册（dry-run 不写盘）")
        elif not run_register(root, dry_run=True):
            return 1
        else:
            same("dry-run：未写盘")
    else:
        if not run_register(root):
            return 1
        if index_has_brand(root):
            add(f"已在 brands_index.json 中登记 {BRAND_ID}")
        else:
            bad(f"注册后仍未在 brands_index.json 中找到 {BRAND_ID}")
            return 1

    print("\n── 3/4  注入用户红线与规约指针到上游 SKILL.md ─────────────────")
    skill_md = root / SKILL_MD_REL
    text, eol = read_text_eol(skill_md)
    new_text, action = inject_managed(text)
    verb = {"inserted": "注入", "replaced": "更新"}[action]
    detail = f"受管块（红线 + 指针，SKILL.md {len(text.splitlines())} -> {len(new_text.splitlines())} 行）"
    if new_text == text:
        same("受管块已是最新，无需改动")
    elif dry_run:
        add(f"将{verb}{detail}")
    else:
        write_text(skill_md, new_text, eol)
        add(f"已{verb}{detail}")

    print("\n── 4/4  自检 ──────────────────────────────────────────────────")
    if dry_run:
        same("dry-run：跳过完整性门")
        return 0
    if not run_guard(root):
        return 1
    ok("上游完整性门 attribution_guard.py 通过")
    if not run_register(root, dry_run=True):
        return 1
    ok("品牌索引校验通过")
    return 0


def do_check(root: Path) -> int:
    problems = 0

    print("\n── 1/4  品牌目录 ──────────────────────────────────────────────")
    dst = root / BRAND_DST_REL
    if dir_fingerprint(BRAND_SRC) == dir_fingerprint(dst):
        ok(f"已安装且与源仓库一致：{dst}")
    elif dst.is_dir():
        bad(f"已安装但与源仓库不一致（需要重跑 apply.py）：{dst}")
        problems += 1
    else:
        bad(f"未安装：{dst}")
        problems += 1

    print("\n── 2/4  品牌索引 ──────────────────────────────────────────────")
    if index_has_brand(root):
        ok(f"brands_index.json 中已登记 {BRAND_ID}")
    else:
        bad(f"brands_index.json 中缺少 {BRAND_ID}（Stage-1 无法发现该品牌）")
        problems += 1

    print("\n── 3/4  SKILL.md 受管块 ───────────────────────────────────────")
    text = read_text(root / SKILL_MD_REL)
    if build_combined().rstrip("\n") in text:
        ok("红线块与指针块均存在且为最新")
    else:
        missing = []
        if RED_LINES_BEGIN not in text and "<!-- BEGIN USER RED LINES" not in text:
            missing.append("红线块")
        if POINTER_BEGIN not in text:
            missing.append("指针块")
        if missing:
            bad(f"上游 SKILL.md 中缺少：{'、'.join(missing)}（AI 读不到你的规则）")
        else:
            warn("受管块存在但内容已过期（路径或版本变了），重跑 apply.py 即可更新")
        problems += 1

    print("\n── 4/4  上游完整性门 ──────────────────────────────────────────")
    if run_guard(root):
        ok("attribution_guard.py 通过")
    else:
        problems += 1

    print()
    if problems:
        bad(f"体检发现 {problems} 项问题 —— 请运行：python apply.py")
        return 1
    ok("体检全部通过，配置完好。")
    return 0


def do_uninstall(root: Path) -> int:
    print("\n── 1/3  移除上游 SKILL.md 中的受管块 ──────────────────────────")
    skill_md = root / SKILL_MD_REL
    text, eol = read_text_eol(skill_md)
    new_text, removed = strip_managed(text)
    if not removed:
        same("受管块不存在，无需移除")
    else:
        write_text(skill_md, new_text, eol)
        add(f"已移除 {removed} 个受管块（SKILL.md {len(text.splitlines())} -> {len(new_text.splitlines())} 行）")

    print("\n── 2/3  删除品牌目录并重建索引 ────────────────────────────────")
    dst = root / BRAND_DST_REL
    if dst.exists():
        shutil.rmtree(dst)
        add(f"已删除品牌目录：{dst}")
    else:
        same("品牌目录不存在")
    if run_register_rebuild(root):
        add("已重建 brands_index.json（google-teaching 条目已清除）")
    else:
        warn("索引重建失败，请手动检查 brands_index.json")

    print("\n── 3/3  自检 ──────────────────────────────────────────────────")
    if run_guard(root):
        ok("上游完整性门 attribution_guard.py 通过（上游已还原干净）")
        return 0
    bad("完整性门未通过 —— 上游文件可能被其它改动污染")
    return 1


# ──────────────────────────────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="apply.py",
        description=f"my-ppt-master v{VERSION} —— 把教学规约与品牌模板挂载到 ppt-master",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="只体检，不写盘")
    mode.add_argument("--dry-run", action="store_true", help="打印将要做的改动，不写盘")
    mode.add_argument("--uninstall", action="store_true", help="干净卸载")
    parser.add_argument("--ppt-master", metavar="PATH", help="手动指定上游仓库根目录")
    args = parser.parse_args(argv)

    print(f"my-ppt-master v{VERSION}  安装器")
    print(f"源仓库：{HERE}")

    preflight()
    root = resolve_or_die(args.ppt_master)

    if args.check:
        return do_check(root)
    if args.uninstall:
        return do_uninstall(root)
    return do_install(root, dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
    except RuntimeError as exc:
        print(f"\n[错误] {exc}")
        sys.exit(1)
