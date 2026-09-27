# -*- coding: utf-8 -*-
"""
my-ppt-master 推送器  (v2.0.0)

把本仓库的改动提交，并推送到所有已配置的远端（Gitee + GitHub）。

用法:
  python push.py                       # 自动生成提交信息
  python push.py -m "补充第3章样式"     # 自定义提交信息
  python push.py --dry-run             # 只显示将要做什么，不推送
  python push.py --remote gitee        # 只推指定远端

如果还没有配置 GitHub 远端，本脚本会提示你执行：

    git remote add github https://github.com/SuperRui0122/my-ppt-master.git

（Gitee 是主仓，GitHub 是镜像。两个都推，任何一边挂掉都不影响你取回代码。）
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VERSION = "2.0.0"
HERE = Path(__file__).resolve().parent

# 建议配置的远端（只用于提示，不强制）
SUGGESTED_REMOTES = {
    "origin": "https://gitee.com/wang-changani/my-ppt-master.git",
    "github": "https://github.com/SuperRui0122/my-ppt-master.git",
}


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


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(HERE), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def current_branch() -> str:
    proc = git("rev-parse", "--abbrev-ref", "HEAD")
    return proc.stdout.strip() if proc.returncode == 0 else "main"


def list_remotes() -> list[str]:
    proc = git("remote")
    return [r.strip() for r in proc.stdout.splitlines() if r.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="push.py",
        description=f"my-ppt-master v{VERSION} —— 提交并推送到所有远端",
    )
    parser.add_argument("-m", "--message", help="提交信息（默认自动生成）")
    parser.add_argument("--remote", help="只推送到指定远端")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要做什么")
    args = parser.parse_args(argv)

    print(f"my-ppt-master v{VERSION}  推送器")
    print(f"仓库：{HERE}")

    if not (HERE / ".git").exists():
        bad("这里不是 git 仓库，无法推送。")
        return 2

    print("\n── 1/4  检查远端 ──────────────────────────────────────────────")
    remotes = list_remotes()
    if not remotes:
        bad("没有配置任何远端。请先执行：")
        for name, url in SUGGESTED_REMOTES.items():
            print(f"        git remote add {name} {url}")
        return 2
    for name in remotes:
        url = git("remote", "get-url", name).stdout.strip()
        same(f"{name} -> {url}")
    missing = [n for n in SUGGESTED_REMOTES if n not in remotes]
    if missing:
        warn(f"建议补上这些远端：{', '.join(missing)}")
        for name in missing:
            print(f"        git remote add {name} {SUGGESTED_REMOTES[name]}")

    targets = [args.remote] if args.remote else remotes
    for name in targets:
        if name not in remotes:
            bad(f"远端不存在：{name}")
            return 2

    branch = current_branch()
    print(f"\n── 2/4  提交改动（分支 {branch}） ─────────────────────────────")
    status = git("status", "--porcelain")
    changed = [line for line in status.stdout.splitlines() if line.strip()]
    if not changed:
        same("没有需要提交的改动")
    else:
        for line in changed[:20]:
            print(f"        {line}")
        if len(changed) > 20:
            print(f"        ...（共 {len(changed)} 项）")
        if args.dry_run:
            add("将执行：git add -A && git commit")
        else:
            git("add", "-A")
            message = args.message or f"update: 同步个性化配置 {datetime.now():%Y-%m-%d %H:%M}"
            proc = git("commit", "-m", message)
            if proc.returncode == 0:
                add(f"已提交：{message}")
            else:
                warn("提交失败（可能没有实际改动）")
                for line in (proc.stdout + proc.stderr).splitlines()[-4:]:
                    print(f"        {line}")

    print(f"\n── 3/4  推送到远端 ────────────────────────────────────────────")
    failures: list[str] = []
    for name in targets:
        if args.dry_run:
            add(f"将执行：git push {name} {branch}")
            continue
        proc = git("push", name, branch)
        if proc.returncode == 0:
            add(f"已推送到 {name}")
        else:
            bad(f"推送到 {name} 失败")
            for line in (proc.stdout + proc.stderr).splitlines()[-6:]:
                print(f"        {line}")
            failures.append(name)

    print("\n── 4/4  结果 ──────────────────────────────────────────────────")
    if args.dry_run:
        same("dry-run：未做任何推送")
        return 0
    if failures:
        bad(f"以下远端推送失败：{', '.join(failures)}")
        print("        常见原因：网络不通、需要重新登录、或远端有他人提交需要先 pull。")
        return 1
    ok(f"已成功推送到：{', '.join(targets)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
