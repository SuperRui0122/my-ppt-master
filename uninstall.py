# -*- coding: utf-8 -*-
"""
my-ppt-master 卸载器  (v2.1.0)

等价于 `python apply.py --uninstall`，单独提供一个入口方便双击 / 记忆。

它会：
  1. 移除上游 SKILL.md 中由本仓库注入的指针块
  2. 删除 google-teaching 品牌目录
  3. 重建 brands_index.json（清掉 google-teaching 条目）
  4. 运行上游完整性门自检

卸载后 ppt-master 会回到「干净的上游副本」状态，可以安全地 git pull。
注意：卸载只影响 ppt-master，不会删除本仓库的任何文件。

用法:
  python uninstall.py
  python uninstall.py --ppt-master <路径>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    argv = [sys.executable, str(HERE / "apply.py"), "--uninstall", *sys.argv[1:]]
    return subprocess.run(argv).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
