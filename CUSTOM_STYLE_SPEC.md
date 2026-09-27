# my-ppt-master 安装与双机协作说明书

> **版本**：v2.0.0（2026-09-27）
> **适用**：高校 / 成人开放教育课程课件（《数据结构》《Python爬虫开发：从入门到实战》等）
> **配套上游**：PPT Master v6.6.0+（MIT 协议，作者 Hugo He）
> **排版规约正文在哪**：见同目录 [`SKILL.md`](./SKILL.md)。**本文件不再重复规则正文**，只讲「怎么装、怎么同步、怎么排错」——避免两份文件长期漂移后互相矛盾（v1.x 就出过这个问题，见 §七）。

---

## 一、架构：谁是谁，谁改谁

整个体系是三层，**每层只允许一种改动方式**：

```text
D:\南开\PPT-master\
├── ppt-master\          ← 第 1 层：上游仓库（只读）
│                            只允许 `git pull`，永远不要手工编辑
│
├── my-ppt-master\       ← 第 2 层：你的定制仓库（唯一权威源）
│   │                        你所有的手工编辑都在这里发生
│   ├── RED_LINES.md         最高优先级红线 R1~R6（停在 SVG、默认 Default…）
│   ├── SKILL.md             15 条教学排版与动效强制规约（规则正文）
│   ├── CUSTOM_STYLE_SPEC.md 本文件：安装与协作说明
│   ├── google-teaching\     无徽标教学品牌模板（design_spec.md + 矢量素材）
│   ├── apply.py             安装器：把上面几样东西挂载进第 1 层
│   ├── update.py            更新器：pull 上游 + 自动重装（永不冲突）
│   └── uninstall.py         卸载器：把第 1 层还原干净
│
└── projects\            ← 第 3 层：课件工程与产物（不进版本库）
                             教案 MD、SVG 源码 → 可进 Git
                             PPTX 成品        → 走网盘，不进 Git
```

**为什么第 1 层不能改**：`ppt-master` 是 13000+ 文件的上游项目，作者持续更新。你一旦手工改它的文件，下次 `git pull` 就会冲突或覆盖。所以本仓库采用「**幂等注入**」——所有改动都由脚本写入，脚本随时可以重跑或撤销。

**为什么第 3 层的 PPTX 不进 Git**：

| 问题 | 说明 |
|---|---|
| 二进制无法合并 | 两台电脑同时改同一个 PPTX，Git 只能二选一，不能合并，必丢工作 |
| 配额爆仓 | Gitee 免费版单仓 500MB；一个 100 页课件 PPTX 常有 20~80MB，几章就满 |
| 仓库会损坏 | 用网盘同步 `.git` 目录会破坏仓库结构（这是最常见的数据事故） |

结论：**源文件走 Git，成品走网盘**。类比：SVG 是源代码，ppt-master 是编译器，PPTX 是可执行文件——编译产物不进版本库。

---

## 二、在新电脑上安装（3 步）

### 步骤 1：下载上游 ppt-master

```bash
git clone https://atomgit.com/hugohe3/ppt-master.git
```

（国内用 AtomGit 镜像，速度远快于 GitHub。上游官方仓库是 `https://github.com/hugohe3/ppt-master`。）

### 步骤 2：把本仓库放到**同级目录**

```bash
git clone https://gitee.com/wang-changani/my-ppt-master.git
```

目录必须是这个相对位置：

```text
某目录\
├── ppt-master\
└── my-ppt-master\      ← 与 ppt-master 同级
```

### 步骤 3：安装依赖并一键挂载

```bash
pip install -r ppt-master/requirements.txt
pip install pyyaml                      # 安装器需要
```

然后双击 **`apply.bat`**，或在命令行运行：

```bash
python my-ppt-master/apply.py
```

看到以下输出即成功：

```text
── 4/4  自检 ──────────────────────────────────
  [OK]   上游完整性门 attribution_guard.py 通过
  [OK]   品牌索引校验通过
```

**安装器做了三件事，仅此三件**：

| # | 动作 | 落在上游的路径 | 是否受版本控制 |
|---|---|---|---|
| 1 | 复制品牌目录 | `skills/ppt-master/templates/brands/google-teaching/` | 否（新目录，永不冲突） |
| 2 | 重新生成品牌索引 | `skills/ppt-master/templates/brands/brands_index.json` | **是** |
| 3 | 注入两个标记块（红线 + 规约指针） | `skills/ppt-master/SKILL.md` | **是** |

第 2、3 项会改动上游受跟踪文件——**这正是 `update.bat` 存在的原因**（见 §三）。

> 两个标记块由 `apply.py` 统一管理：注入时**先剥离所有受管块，再整体插入**，因此顺序恒定、无残留、重复运行结果逐字节一致。它也能自动识别并清理早期 `ppt-master-user-rules/apply_user_rule.py` 留下的旧格式块。
>
> 另外安装器会**保留原文件的行尾风格**（Windows 上 git 常以 CRLF 检出）。否则写回 LF 会让 git 判定文件被修改，进而阻塞后续 `git pull`。


### 安装器可选参数

| 命令 | 作用 |
|---|---|
| `python apply.py` | 安装 / 重新安装（幂等，可反复运行） |
| `python apply.py --check` | 只体检，不写盘。装完、更新完、出问题时都可以跑 |
| `python apply.py --dry-run` | 打印将要做的改动，不写盘 |
| `python apply.py --uninstall` | 干净卸载（还原上游文件 + 删除品牌目录） |
| `python apply.py --ppt-master <路径>` | 手动指定上游仓库位置 |

---

## 三、日常更新（**这一步不能省**）

上游作者更新了 ppt-master，你想跟上：

**双击 `update.bat`**（等价于 `python update.py`）。它按顺序做四件事：

1. 拉取本仓库 `my-ppt-master` 自己的最新版
2. 把上游受跟踪文件（`SKILL.md`、`brands_index.json`）**还原成上游原样**
3. `git pull --rebase` 拉取上游更新
4. 重新运行 `apply.py`，把品牌与规约指针装回去

因为第 2 步先把「我们造成的改动」清掉了，所以**第 3 步永远不会冲突**。这是「永不冲突」承诺的真正实现方式。

> ⚠️ **不要只做 `git pull` 不做第 4 步。** 只 pull 的话，上游会把 `SKILL.md` 里的红线块与规约指针一起覆盖掉、把 `brands_index.json` 里的品牌条目冲掉，AI 就再也读不到你的教学规约与红线了。跑 `update.bat`，或事后补一次 `apply.py`，都可以恢复。

> ⚠️ 如果你在 `ppt-master` 里手工改过文件，`update.bat` 会拒绝执行并提示你先处理。`ppt-master` 应该是纯净的上游副本。

---

## 四、两台电脑协同（办公室 ↔ 家里）

### 4.1 分工原则

**两台电脑都可能改同一章**，所以不做「一台写、一台读」的分工，而是用 Git 的标准流程：**开工先拉，收工就推**。

### 4.2 每次开工（在任意一台电脑上）

```bash
cd my-ppt-master && git pull        # 拉取另一台电脑的改动
cd ../projects/数据结构 && git pull  # 拉取教案与 SVG 源码改动
python ../my-ppt-master/apply.py    # 确保规约已挂载（可选，update.bat 里已有）
```

### 4.3 每次收工

```bash
cd projects/数据结构
git add -A && git commit -m "第3章 一维数组：补充检索效率对比页"
git push
```

### 4.4 如果两边都改了同一章

Git 会告诉你冲突。教案是纯文本 Markdown，**可以手工合并**——这正是把教案放进 Git 的价值。而 PPTX 是二进制，冲突后只能二选一，所以它不进 Git。

### 4.5 如果嫌命令行麻烦

在 `my-ppt-master` 里已经准备了脚本：

| 脚本 | 时机 | 作用 |
|---|---|---|
| `apply.bat` | 新电脑首次 / 重装 | 挂载定制配置 |
| `update.bat` | 拉上游更新时 | pull + 自动重装（**永不冲突**） |
| `push.bat` | 收工时 | 提交并推送到 Gitee |
| `uninstall.bat` | 想还原上游时 | 干净卸载 |

### 4.6 远端与备份策略：只用 Gitee

**2026-09-27 决定：本仓库只保留 Gitee 一个远端，放弃 GitHub 镜像。**

原因：GitHub 在国内需要代理，实测频繁出现 `CONNECT tunnel failed, response 502`，每次推送都失败。维护成本高于它带来的价值。

代价是失去「海外异地备份」这一层。补偿方式是**离线备份**——两台电脑本身就是天然两份，再定期导出一个单文件备份，丢到移动硬盘或网盘：

```bash
git bundle create my-ppt-master.bundle --all
```

恢复时：

```bash
git clone my-ppt-master.bundle my-ppt-master
```

`.bundle` 是单个文件、含完整 Git 历史、不含工作区产物，非常适合冷备。建议每次做完一个章节导出一次，文件名带上日期，例如 `my-ppt-master-2026-09-27.bundle`。

> 上游 `ppt-master` 的官方仓库仍在 GitHub（`hugohe3/ppt-master`），国内建议用 AtomGit 镜像 `https://atomgit.com/hugohe3/ppt-master.git`。那是上游的归属信息，与本仓库的远端策略无关，不要删。

---

## 五、课件工程的目录约定

推荐在 `ppt-master/projects/` 下按课程分目录（上游 `.gitignore` 已排除 `projects/*`，所以这里可以独立 `git init` 成你自己的仓库）：

```text
ppt-master\projects\
├── 数据结构\                  ← 独立 Git 仓库（推 Gitee）
│   ├── 教案\
│   │   ├── 第01章_绪论.md
│   │   └── 第02章_线性表.md
│   ├── _brand-google-teaching\ ← 可选：项目级模板工作区副本
│   └── ds-ch3_ppt169_20260927\ ← ppt-master 生成的项目目录
│       ├── design_spec.md      ← 策略师产物（SVG 之前的规范）
│       ├── svg_output\         ← Executor 逐页手写的 SVG 源码 ★进 Git
│       ├── svg_final\          ← 质量门通过后的定稿 SVG ★进 Git
│       ├── notes\              ← 演讲者备注
│       └── *.pptx              ← 成品 ✗ 不进 Git，拷到网盘
└── python爬虫\
    └── ...
```

**判断某文件该不该进 Git 的一句话标准**：能不能用文本编辑器打开并手工合并？能 → 进；不能（二进制）→ 走网盘。

---

## 六、故障排查

### 6.1 「AI 好像没用我的教学规约」

先跑体检：

```bash
python apply.py --check
```

| 报错 | 原因 | 处理 |
|---|---|---|
| `brands_index.json 中缺少 google-teaching` | 品牌没注册（Stage-1 发现不了它） | `python apply.py` |
| `上游 SKILL.md 中缺少：红线块、指针块` | 上游 pull 后覆盖了，AI 读不到规约与红线 | `python apply.py` |
| `已安装但与源仓库不一致` | 品牌模板在别处被改过 | `python apply.py` |
| `attribution_guard.py 未通过` | 上游文件被非本工具改坏了 | `git -C ppt-master checkout -- .` 后重跑 |

### 6.2 「报 `ModuleNotFoundError: No module named 'yaml'`」

上游 `register_template.py` 需要 PyYAML，而它用的是**你运行 apply.py 的那个 Python**：

```bash
python -m pip install pyyaml
```

安装器现在会在开始前检查这一项并给出明确提示。

### 6.3 「品牌注册失败：missing required section: IV. Logo」

这是 v1.x 的真实故障。原因是 `design_spec.md` 的章节标题写成了：

```markdown
## IV. Logo（严禁使用谷歌徽标规则）     ← 中文括号会破坏上游的严格正则
```

上游 `register_template.py` 要求章节标题是**精确的** `## IV. Logo`。补充说明必须放到标题下面的引用块里，不能塞进标题。v2.0 已修复。

### 6.4 「`update.bat` 说 ppt-master 不干净」

说明 `ppt-master` 里有手工改动。确认那些改动没用之后：

```bash
git -C ppt-master checkout -- .        # 丢弃所有受跟踪文件的改动
git -C ppt-master clean -fd            # 删除所有未跟踪文件（谨慎！）
```

### 6.5 「AI 直接输出了 PPTX，跳过了 SVG」

这**不是**安装问题，是 agent 没有严格执行 `SKILL.md` 的强制加载顺序。判断方法：

- 看项目目录里有没有 `design_spec.md` 和 `svg_final/`——有，说明流程走完了；没有，说明跳过了中间产物。

`apply.py` 注入的指针块已经写明「用户规约优先于上游默认值，包括 Quick 模式的提速默认行为」。如果仍然跳过，在对话里直接说：

> 「按 my-ppt-master/SKILL.md 的流程走：先只生成 SVG，跑完质量门后停下来给我看，我确认后再导出 PPTX。」

---

## 七、为什么 v2.0 要重写（历史缺陷说明）

v1.x 有几个会**静默失效**的缺陷，记录在此避免重蹈覆辙。

### 缺陷 1：品牌注册逻辑错误（最严重）

v1.x 的 `apply.py` 这样注册品牌：

```python
brands = data.get("brands", [])
brands.append({"id": "google-teaching", ...})
data["brands"] = brands
```

但上游 `brands_index.json` 的真实结构是**扁平字典**：

```json
{
  "google": { "summary": "...", "primary_color": "#4285F4" },
  "huawei": { "summary": "...", "primary_color": "#CF0A2C" }
}
```

没有 `brands` 键。所以 `data.get("brands", [])` 永远返回空列表，代码往索引里塞了一个上游根本不认识的 `"brands"` 键，而 `google-teaching` **实际上从未注册成功**——AI 在 Stage-1 永远发现不了这个品牌。

**v2.0 修法**：改为调用上游官方工具 `register_template.py google-teaching --kind brand`，由它生成正确 schema 并做完整校验。

### 缺陷 2：向 AGENTS.md / CLAUDE.md 追加写

v1.x 会往这两个**上游受跟踪文件**追加一行引用。后果：`git pull` 必然冲突，直接违背 README 里「永不冲突」的承诺。

**v2.0 修法**：完全不碰这两个文件。改为向上游 `SKILL.md` 注入带标记的受管块，并在 `update.py` 里在 pull 之前还原，冲突概率归零。

> 相关：早期另有一个独立的 `ppt-master-user-rules/apply_user_rule.py` 负责注入红线。它与本安装器**各管一块**，会在 `update.py` 还原 `SKILL.md` 时互相丢块。v2.0 已把红线并入本安装器（正文见 `RED_LINES.md`），由 `apply.py` 统一管理两个块——**一个安装器管全部**。旧脚本可以不再使用；若之前跑过它，`apply.py` 会自动识别并清理其旧格式标记。

### 缺陷 3：规范正文两处重复且已漂移

v1.x 的 `SKILL.md` 与 `CUSTOM_STYLE_SPEC.md` 有约 90% 内容重复，且已经漂移出不一致：

| 项目 | SKILL.md 说的 | CUSTOM_STYLE_SPEC.md 说的 |
|---|---|---|
| 页脚左栏格式 | `《课程名称》·第X节` | `第X章 · 章节名称` |
| 页脚页码 | `NN / Total` | `NN` |
| 过渡页左栏宽度 | 340~520px | 520px |
| 大数字字号 | `Pt(96~110)` | `Pt(110)` |

更糟的是 `CUSTOM_STYLE_SPEC.md` 第 375 行的「一键激活 Prompt」里写着：

> 右上角放置 24x24 `google_g_logo.svg`

而全文有 5 处红线写着「**严禁**放置任何谷歌图标」。自相矛盾。

**v2.0 修法**：`SKILL.md` 成为规则**唯一权威源**；本文件改为只讲安装与协作，不再复制规则正文。

### 缺陷 4：推送脚本名不副实

`sync_to_github.bat` 的 echo 输出「已成功双线同步推送到 Gitee 与 GitHub」，但实际只执行了 `git push origin main`，而当时 `origin` 只指向 Gitee。你以为有异地备份，其实没有。

**v2.0 修法**：`push.bat` 会检查并推送到**所有已配置的远端**，并如实报告推了哪几个。`sync_to_github.bat` 已删除；2026-09-27 进一步决定只保留 Gitee 一个远端，见 §4.6。

---

## 八、规则速查

### 8.1 最高优先级红线（正文见 [`RED_LINES.md`](./RED_LINES.md)）

红线**高于**下面 15 条规约，也高于上游任何 route authority 文档：

| # | 红线 | 一句话 |
|---|---|---|
| R1 | 停在 SVG | 先把页面写进 `svg_output/` 并跑完质量门，**立即停下等用户审阅**；只有用户说「导出」才导 PPTX |
| R2 | 默认走 Default | 不得擅自路由到 Quick；用户明确说「快速」才可 |
| R3 | 动手前声明路线 | 每轮第一条消息写明 route / profile / Step 编号 |
| R4 | 给真实预览地址 | 必须启动 `svg_editor/server.py --daemon` 并报告真实 URL，禁止编造端口 |
| R5 | 确认门不得代签 | 用户沉默 ≠ 确认；代为决策必须显著标注 |
| R6 | 考核内容忠于源文档 | 禁止编造考试形式、评分标准、学分政策 |

### 8.2 教学排版与动效规约（正文见 [`SKILL.md`](./SKILL.md)）

| # | 规则 | 一句话 |
|---|---|---|
| 1 | 画布与字体 | 16:9 / 1280×720，全局微软雅黑 |
| 2 | 字号阶梯 | 正文 16pt、标题 24pt、代码 11~13.5pt 自适应 |
| 3 | B1 双轨页眉 | 上行 `第X节 · 小节 ▸ X.Y 专题`，下行 `X.Y.N 核心标题`，废除破折号 |
| 4 | 四色轮换 | 蓝 `#4285F4` / 绿 `#34A853` / 黄 `#FBBC05` / 红 `#EA4335` |
| 5 | 无徽标红线 | 全课件严禁出现任何谷歌图标 |
| 6 | 单页独立大图 | 严禁一页塞多张小截图 |
| 7 | 随堂测验动效 | 初始不泄题，点击分步淡入揭晓 |
| 8 | 卡片换行安全 | 容器边界零溢出 + `word_wrap` 兜底 |
| 9 | 章节过渡页 | 左侧色块 + 200px 大数字 + 标题上下分流 |
| 10 | 代码与回显成对 | 输入页必配输出回显页，左右双栏 |
| 11 | 课堂字号分级 | 字号不妥协，放不下就拆页 |
| 12 | 拆页纵向重平衡 | 锁定 `y = 114 ~ 662`，杜绝底部空白 |
| 13 | 词元保护折行 | 中英混排不断词，消灭 1~2 字孤行 |
| 14 | Z-Order 防遮挡 | 内嵌小结框与正文净间距 ≥ 18px |
| 15 | 代码语法保真 | 物理 4 空格缩进 + AST 语法门禁 + 图片 rId 对齐 |

---

## 九、版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v2.0.0-2 | 2026-09-27 | 放弃 GitHub 镜像，远端只保留 Gitee；`push.py` 去除 github 建议远端，删除 `sync_to_github.bat`；新增 §4.6（放弃理由 + 离线 `.bundle` 冷备方案）；`SKILL.md` frontmatter `repository` 改指 Gitee |
| v2.0.0 | 2026-09-27 | 重写安装器（改用上游官方注册工具、删除 AGENTS.md 写入）；修复品牌模板 `IV. Logo` 标题致校验失败；合并去重两份漂移规范；并入红线 `RED_LINES.md` 由 `apply.py` 统一管理；新增 `update.bat` / `uninstall.bat` / `push.bat` / `LICENSE` / `.gitignore` |
| v1.6.0 | 2026-09-27 | 新增 Rule 15（代码物理 4 空格缩进、AST 语法保真、图片 rId 对齐） |
| v1.5.0 | 2026-09-26 | 页眉体系升级为 B1 双轨（面包屑 + `X.Y.N` 极简标题，零破折号） |
| v1.4.0 | 2026-09-25 | 新增 Rule 13（内嵌框防遮挡与 Z-Order 门禁）、Rule 14（跨小节编号单调重排） |
| v1.3.0 | 2026-09-24 | 新增 Rule 10~12（源文档忠实度、拆页抗留白、词元保护折行） |
| v1.2.0 | 2026-09-20 | 新增 Rule 9（课堂可读性字号分级与自适应排版） |
| v1.0.0 | 2026-09-03 | 初始版本：Google-Teaching 风格 + 品牌模板 |
