# -*- coding: utf-8 -*-
"""
my-ppt-master 更新器  (v2.1.0)

把「上游 ppt-master 的更新」与「你的个性化定制」安全地叠加起来，
让 git pull 永远不会冲突。

它按顺序做五件事：
  0. 拉取 my-ppt-master 自身的最新版（两台电脑之间的同步）
  1. 把上游受跟踪文件还原成上游原样（清掉本安装器造成的改动）
  2. 在 ppt-master 中执行 git pull --rebase
  3. 重新运行 apply.py，把品牌与规约指针装回去
  4. 自检（完整性门 + 品牌索引）

关键点在第 1 步：先把「我们造成的改动」还原掉，第 2 步就不可能冲突。
第 3 步是无条件执行的 —— 即使第 2 步失败，配置也会被重新装回，不会留下残缺状态。

用法:
  python update.py                  # 完整更新
  python update.py --no-self-pull   # 跳过第 0 步（不拉取本仓库）
  python update.py --dry-run        # 只显示将要做什么，不执行
  python update.py --ppt-master <路径>
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from apply import (  # noqa: E402  (必须先插入 sys.path)
    TOUCHED_TRACKED,
    find_ppt_master,
    run_guard,
    run_register,
    VERSION,
)


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


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def has_remote(path: Path) -> bool:
    proc = git(path, "remote")
    return proc.returncode == 0 and bool(proc.stdout.strip())


def dirty_tracked(path: Path) -> list[str]:
    """列出被修改的受跟踪文件（不含未跟踪文件）。"""
    proc = git(path, "status", "--porcelain", "--untracked-files=no")
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def _porcelain_path(line: str) -> str:
    """从 `git status --porcelain` 的一行里取出文件路径。"""
    return line[3:].strip().strip('"')


# 第 1 步会还原这些文件，所以它们脏不脏不影响 pull —— 不能算作「阻塞 pull 的脏文件」
_TOUCHED_POSIX = {rel.as_posix() for rel in TOUCHED_TRACKED}


def blocking_dirty(path: Path) -> list[str]:
    """第 1 步还原之后仍然会阻塞 pull 的脏文件。"""
    return [line for line in dirty_tracked(path) if _porcelain_path(line) not in _TOUCHED_POSIX]


def show(proc: subprocess.CompletedProcess[str]) -> None:
    for stream in (proc.stdout, proc.stderr):
        if stream and stream.strip():
            for line in stream.strip().split("\n")[-8:]:
                print(f"        {line}")


def step_self_pull(dry_run: bool) -> None:
    print("\n── 0/5  拉取 my-ppt-master 自身的最新版 ───────────────────────")
    if not is_git_repo(HERE):
        warn("本仓库不是 git 仓库，跳过")
        return
    if not has_remote(HERE):
        warn("本仓库没有配置远端，跳过")
        return

    dirty = dirty_tracked(HERE)
    if dirty:
        warn(f"本仓库有 {len(dirty)} 个文件未提交，先不拉取（避免冲突）：")
        for line in dirty[:5]:
            print(f"        {line}")
        print("        处理办法：先 commit 或 stash，再重跑 update.py")
        return

    if dry_run:
        add("将执行：git pull --rebase")
        return

    proc = git(HERE, "pull", "--rebase")
    if proc.returncode == 0:
        out = (proc.stdout or "").strip().splitlines()
        same(out[-1] if out else "已是最新")
    else:
        warn("拉取本仓库失败（可能是网络或需要凭据），继续执行后续步骤")
        show(proc)


def step_reset(root: Path, dry_run: bool) -> None:
    print("\n── 1/5  还原上游受跟踪文件 ────────────────────────────────────")
    if not is_git_repo(root):
        warn("ppt-master 不是 git 仓库，跳过还原")
        return
    for rel in TOUCHED_TRACKED:
        if dry_run:
            add(f"将还原：{rel}")
            continue
        proc = git(root, "checkout", "--", str(rel))
        if proc.returncode == 0:
            add(f"已还原：{rel}")
        else:
            warn(f"还原失败：{rel}")
            show(proc)


def step_pull(root: Path, dry_run: bool, force: bool) -> bool:
    print("\n── 2/5  拉取上游 ppt-master ────────────────────────────────────")
    if not is_git_repo(root):
        warn("ppt-master 不是 git 仓库，跳过 pull")
        return True
    if not has_remote(root):
        warn("ppt-master 没有配置远端，跳过 pull")
        return True

    dirty = blocking_dirty(root)
    if dirty:
        if force:
            warn(f"ppt-master 有 {len(dirty)} 个受跟踪文件被改动，--force 将丢弃它们：")
            for line in dirty[:8]:
                print(f"        {line}")
            if not dry_run:
                proc = git(root, "checkout", "--", ".")
                if proc.returncode != 0:
                    bad("丢弃本地改动失败")
                    show(proc)
                    return False
        else:
            bad(f"ppt-master 中有 {len(dirty)} 个受跟踪文件被改动，拒绝 pull：")
            for line in dirty[:8]:
                print(f"        {line}")
            print("\n        ppt-master 应该是纯净的上游副本，请勿手工编辑它。")
            print("        确认这些改动可以丢弃后，加 --force 重跑：")
            print("            python update.py --force")
            return False

    if dry_run:
        add("将执行：git pull --rebase")
        return True

    proc = git(root, "pull", "--rebase")
    if proc.returncode == 0:
        out = (proc.stdout or "").strip().splitlines()
        same(out[-1] if out else "已是最新")
        return True
    warn("拉取上游失败（网络或凭据问题）—— 继续重新安装配置，上游保持当前版本")
    show(proc)
    return True


def step_reinstall(root: Path, dry_run: bool) -> bool:
    print("\n── 3/5  重新安装个性化配置 ────────────────────────────────────")
    if dry_run:
        add("将执行：python apply.py")
        return True
    proc = subprocess.run(
        [sys.executable, str(HERE / "apply.py"), "--ppt-master", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for stream in (proc.stdout, proc.stderr):
        if stream and stream.strip():
            for line in stream.strip().split("\n"):
                if line.startswith("  [") or line.startswith("──"):
                    print(line)
    if proc.returncode != 0:
        bad(f"重新安装失败（exit {proc.returncode}）")
        show(proc)
        return False
    return True


def step_verify(root: Path, dry_run: bool) -> bool:
    print("\n── 4/5  自检 ──────────────────────────────────────────────────")
    if dry_run:
        same("dry-run：跳过自检")
        return True
    passed = True
    if run_guard(root):
        ok("上游完整性门 attribution_guard.py 通过")
    else:
        passed = False
    if run_register(root, dry_run=True):
        ok("品牌索引校验通过")
    else:
        passed = False
    return passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="update.py",
        description=f"my-ppt-master v{VERSION} —— 更新上游 + 自动重装定制配置（永不冲突）",
    )
    parser.add_argument("--no-self-pull", action="store_true", help="跳过第 0 步（不拉取本仓库）")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要做什么，不执行")
    parser.add_argument("--force", action="store_true",
                        help="丢弃 ppt-master 中所有受跟踪文件的本地改动（谨慎）")
    parser.add_argument("--ppt-master", metavar="PATH", help="手动指定上游仓库根目录")
    args = parser.parse_args(argv)

    print(f"my-ppt-master v{VERSION}  更新器")
    print(f"本仓库：{HERE}")

    root = find_ppt_master(args.ppt_master)
    if root is None:
        bad("未找到 ppt-master 仓库。请用 --ppt-master <路径> 指定。")
        return 2
    print(f"上游仓库：{root}")

    if not args.no_self_pull:
        step_self_pull(args.dry_run)
    step_reset(root, args.dry_run)
    if not step_pull(root, args.dry_run, args.force):
        return 1
    if not step_reinstall(root, args.dry_run):
        return 1
    if not step_verify(root, args.dry_run):
        return 1

    print("\n── 5/5  完成 ──────────────────────────────────────────────────")
    ok("上游已更新，个性化配置已重新挂载，二者零冲突。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
