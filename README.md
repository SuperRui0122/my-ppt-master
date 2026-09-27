# my-ppt-master

> 配套 [ppt-master](https://github.com/hugohe3/ppt-master)（MIT，作者 Hugo He）的**教学课件定制层**。
> 提供无徽标教学品牌模板 `google-teaching`、28 条教学排版与动效强制规约（§一 排版 6 + §二 教学红线 15 + §三 讲稿 1），以及两台电脑协同备课的完整流程。
>
> **当前版本 v2.1.0**（2026-09-27）—— 重写安装器，修复 v1.x 的品牌注册失效与 `git pull` 冲突问题；加固 Rule 15 代码保真门禁（`data-lead` 权威缩进 + 语义可运行门禁）。
> 详细安装步骤、双机协作流程、故障排查见 **[`CUSTOM_STYLE_SPEC.md`](./CUSTOM_STYLE_SPEC.md)**。

---

## 30 秒上手

### 1. 目录布局（必须是同级）

```text
D:\南开\PPT-master\
├── ppt-master\        ← 上游仓库，只 git pull，永不手工编辑
└── my-ppt-master\     ← 本仓库，你所有的手工编辑都在这里
```

```bash
git clone https://atomgit.com/hugohe3/ppt-master.git
git clone https://gitee.com/wang-changani/my-ppt-master.git
pip install pyyaml
```

### 2. 双击 `apply.bat`

看到 `[OK] 上游完整性门 attribution_guard.py 通过` 即安装成功。

### 3. 日常只用两个按钮

| 按钮 | 什么时候按 |
|---|---|
| **`update.bat`** | 想跟上上游 ppt-master 的新版本时 |
| **`push.bat`** | 收工时（提交并推送到 Gitee） |

> ⚠️ **`update.bat` 不能省。** 直接 `git pull` 会把本仓库注入的规约指针冲掉，AI 就再也读不到你的教学规约了。`update.bat` 会 pull 完自动装回去，且永不冲突。

> 📦 **只推 Gitee。** 2026-09-27 起放弃 GitHub 镜像——国内直连 Gitee 稳定，GitHub 需代理且实测频繁报 502。异地备份改用离线 `.bundle` 文件，见 [`CUSTOM_STYLE_SPEC.md`](./CUSTOM_STYLE_SPEC.md) §4.6。

---

## 仓库内容

| 文件 / 目录 | 作用 |
|---|---|
| `SKILL.md` | **规则正文**。28 条教学排版与动效强制规约（唯一权威源） |
| `RED_LINES.md` | **最高优先级红线**。R1~R6：停在 SVG 不抢跑导出、默认走 Default、动手前声明路线、给真实预览地址、确认门不得代签、考核内容忠于源文档 |
| `CUSTOM_STYLE_SPEC.md` | 安装步骤、双机协作流程、故障排查、历史缺陷说明 |
| `google-teaching/` | 无徽标教学品牌模板（`templates/design_spec.md` + 矢量素材） |
| `apply.py` / `apply.bat` | 安装器（幂等，可反复运行） |
| `update.py` / `update.bat` | 更新器：pull 上游 + 自动重装，**永不冲突** |
| `push.py` / `push.bat` | 推送器：提交并推送到所有远端 |
| `uninstall.py` / `uninstall.bat` | 卸载器：把上游还原干净 |
| `sync_from_ppt_master.py` | 回流工具：把在 ppt-master 里现场调好的品牌模板取回本仓库 |
| `build_preview.py` / `preview.bat` | **翻页预览器**：把一册逐页 SVG 打包成单文件、离线可用的 `preview.html`（键盘翻页 + 缩略图 + 讲稿对照），不再需要逐页打开 SVG |

### 安装器改了上游哪些文件？

只有 3 处，其中 2 处是上游受跟踪文件（所以需要 `update.bat` 来兜底）：

| # | 落点 | 受版本控制 |
|---|---|---|
| 1 | `skills/ppt-master/templates/brands/google-teaching/` | 否 —— 新目录，永不冲突 |
| 2 | `skills/ppt-master/templates/brands/brands_index.json` | **是** |
| 3 | `skills/ppt-master/SKILL.md`（注入两个标记块：红线 + 规约指针） | **是** |

全部改动都带标记、可幂等重跑、可一键撤销（`uninstall.bat`）。实测卸载后 `git status` **完全为空** —— 上游逐字节还原，零删除行。

> 两个标记块由 `apply.py` **统一管理**：注入时先剥离所有受管块再整体插入，所以顺序恒定、无残留。它也能自动清理早期 `ppt-master-user-rules/apply_user_rule.py` 留下的旧格式块。


---

## 常用命令

```bash
python apply.py --check       # 体检：品牌装了吗？索引注册了吗？指针在吗？
python apply.py --dry-run     # 预览将要做的改动
python apply.py --uninstall   # 干净卸载
python update.py --dry-run    # 预览更新流程
python update.py --force      # 上游有手工改动时，丢弃后继续更新
python push.py -m "补充第3章样式"
python apply.py --ppt-master D:\path\to\ppt-master   # 手动指定上游位置

python build_preview.py .                        # 在当前册目录生成翻页预览
python build_preview.py --all                    # 为 projects 下所有册批量生成
python build_preview.py <册目录> --open           # 生成指定册并打开浏览器
```

> 💡 **看课件效果别再用文件管理器逐页点开 SVG。** 双击 `preview.bat`，它会为 `ppt-master/projects` 下每一册生成一个 `preview.html`（单文件、含全部图片、可直接拷给别人）。打开后用 `←` `→` 翻页、`S` 看缩略图、`N` 对着讲稿备注备课。
> 注意：`preview.html` 是**快照**，改完 SVG 或讲稿后要重跑一次才会刷新。

---

## v1.x → v2.0 修复了什么

| 缺陷 | 后果 | v2.0 修法 |
|---|---|---|
| `brands_index.json` schema 猜错 | 品牌**从未注册成功**，AI 发现不了 | 改用上游官方 `register_template.py` |
| 向 `AGENTS.md` / `CLAUDE.md` 追加写 | `git pull` 必然冲突 | 改为注入上游 `SKILL.md` 标记块 + `update.bat` 还原 |
| 品牌模板标题带中文括号 `## IV. Logo（…）` | 上游校验器直接拒绝，装不进去 | 标题改纯净，说明移到引用块 |
| 两份规范 90% 重复且已漂移 | 页脚/页码/字号四处分叉；一处还写着「放置 google logo」与红线自相矛盾 | `SKILL.md` 成为唯一权威源 |
| 推送脚本谎报远端（只推一个却说推了两个） | 以为有异地备份，其实没有 | `push.py` 如实报告推了哪几个远端；`sync_to_github.bat` 已删除 |

---

## 许可

MIT。本仓库包含来自 ppt-master（Copyright (c) 2025-2026 Hugo He）的品牌矢量素材，继续受其原始 MIT 许可约束。详见 [`LICENSE`](./LICENSE)。
