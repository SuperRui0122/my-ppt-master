# PPT 任务提示词（my-ppt-master 通用）

> 规约细节**不用写进提示词** —— `my-ppt-master` 里有完整规约（`RED_LINES.md` / `SKILL.md` / `AGENTS.md`），
> agent 会自己读。提示词只需交代「做什么、源教案在哪」。
> 最后更新：2026-10-24（同步 R4 单文件预览、R7 默认不产讲稿）

## 短版（推荐，日常就用这个）

把 `【】` 换掉即可：

```text
按 my-ppt-master 规约做大课【N】课件（先读 RED_LINES.md + SKILL.md + .workbuddy-ai/memory/MEMORY.md）。
源教案：D:\南开\大数据技术备课系统\outputs\Python编程语言项目\课程实训手册\01_通讯录\课时【XX】_*.md
参照 ch01 生成器体系复用。先出页面规划等我确认，再生成 SVG；只到 SVG + 质量门 + 单文件 preview.html，严禁导出 PPTX，不要写讲稿。
```

## 详版（备用：换环境、首次协作、或 agent 没读懂短版时）

---

# 任务：为《Python编程语言项目》大课【N】（课时【X–Y】）制作教学课件

## 第一件事：加载规约（按优先级从高到低，全部读完再动手）
1. `D:\南开\PPT-master\my-ppt-master\RED_LINES.md`            ← 用户红线 R1~R7，最高优先级
2. `D:\南开\PPT-master\my-ppt-master\SKILL.md`                ← 教学排版 16 条规约
3. `D:\南开\PPT-master\.workbuddy-ai\memory\MEMORY.md`        ← 本项目长期记忆（环境 / 约定 / 已知陷阱）
4. `D:\南开\PPT-master\.workbuddy-ai\memory\<最新日期>.md`     ← 最近工作日志
5. `D:\南开\PPT-master\ppt-master\skills\ppt-master\SKILL.md` 及 `workflows/generate-pptx.md` ← 上游默认流程

本轮第一条回复必须声明：**route / profile / 当前 Step 编号**（RED_LINES R3）。

## 任务范围
- 课程集：《Python编程语言项目》· 阶段一「基础编程篇」· 项目一《学生通讯录管理系统 v1.0》
- 本课件 = 大课【N】，覆盖课时【X、Y、Z】
- 受众：高职大数据技术专业大一新生（26 级），零编程基础，抗拒纯理论、重视上手
- 教学定位：**手把手**，一行一行敲代码；可以用库，但功能必须学生自己一点一点实现；课时长度可动态调整，不要为卡 45 分钟切碎流程

## 源教案（唯一内容依据，逐字通读，不得自行发挥）
- `D:\南开\大数据技术备课系统\outputs\Python编程语言项目\课程实训手册\01_通讯录\课时【XX】_*.md`
- （按需列出本大课覆盖的全部课时文件）

若发现教案与「阶段一零超纲铁律」（禁用 `def` / `class` / `dict` / 外部文件 I/O）冲突，或口径不一致，**先报告给用户，不要自己改 md**。

## 复用已有生成器（省掉 90% 重复劳动）
参照 `D:\南开\PPT-master\ppt-master\projects\ppt-python-crawler\python-ch01_ppt169_20261007\generators\`：
- `ppt_kit.py` → **原样复制**（通用 SVG 渲染工具包，不用改）
- `gen_python_ch01.py` → 复制改名；`r_*` 页型函数是通用的，保留；只需改 `write_design_spec()` / `write_spec_lock()` 里的项目名与描述文案
- `gen_python_ch01_content.py` → 按本大课教案**重写**逐页内容模型
- `gen_python_ch01_notes.py` → 逐页口播备注（索引键 = 页面标题）；**R7：默认不产，仅在用户本轮明确要讲稿时才写**
- 也可整目录复制 ch01 项目后清理内容，比从零 init 更快
- 可直接复用的校验脚本：`audit_titles.py`（§14 标题门禁）、`audit_pages_notes.py`（页码 + 备注 1:1，**仅在本轮有讲稿时才跑**）

## 内容与版式要求（沿用 SKILL.md 全部规约，重点如下）
- 画布 1280×720；正文区 y=114~662；页眉线 y=98；页脚线 y=680；页脚「NN / Total」
- 三节配色：第 1 节蓝 `#4285F4` · 第 2 节绿 `#34A853` · 第 3 节黄 `#FBBC05`（黄系文字用 `#B06000`）
- B1 双轨页眉：上行「第X节 · 小节简称 ▸ X.Y 专题简称」（小节简称 ≤8 字 / 专题简称 ≤6 字），下行「X.Y.N 核心标题」（≤12 字，严禁破折号 `——`）
- 严禁任何谷歌图标；严禁口语化盘面（口语化串词只允许进 Notes，而 Notes 仅在用户明确要求时产出）；测验一律两页式静态（A 提问页全中性灰零答案痕迹 + B 揭晓页绿标 ✓ + ans_bar）
- 全片 0 动画、0 切换特效；代码 / 终端一律深色 Consolas 卡，保留 4 空格物理缩进
- 可用页型：`cover` / `divider` / `closing` / `cards2` / `cards3` / `cards4` / `kpi_card` / `table` / `steps` / `flow` / `layers` / `image` / `code` / `echo` / `quiz_q` / `quiz_a`
- 规模参照 ch01（大课 1 = 76 页 / 3 课时），大课 N 大致 75~85 页

## 硬性红线
- **R1**：本轮只交 SVG，禁止导出 PPTX。写完 `svg_output/` 并跑完质量门后立即停下，报告项目路径 + 页面清单 + 门禁结果，等用户明确说「导出 / export / 可以了 / 定稿」才导出。
- **R2**：默认走 Default 流程，不得擅自路由到 Quick。
- **R6**：考核、评分、学分内容 100% 忠于源教案，禁止编造。
- **R7**：默认不产讲稿 / 演讲者备注 / 任何独立讲稿文件；只有用户在本轮明确说「要讲稿 / 演讲稿 / 备注 / 口播稿」才写。

## 交付前门禁顺序（一步都不能跳，版式自审必须排在 SVG 质量门之前）
1. 归因
2. **版式自审**：`"C:\Users\wangRui\AppData\Local\Programs\Python\Python314\python.exe" "D:\南开\PPT-master\my-ppt-master\check_layout.py" "<project>" --json` ← 必须 **0 blocking**
3. AST 语法门禁（Python 代码过 AST，保 4 空格缩进）
4. **双轨标题**：`... "<project>\generators\audit_titles.py" "<project>\svg_output"` ← ⚠️ 参数是 `svg_output` 目录，不是项目根
5. **SVG 质量门**：`... "D:\南开\PPT-master\ppt-master\skills\ppt-master\scripts\svg_quality_checker.py" "<project>" --canonical-authoring --stage final --json`
6. **预览（R4 · 只交单文件）**：`... "D:\南开\PPT-master\my-ppt-master\build_preview.py" "<project>"` → 产出 `<project>\preview.html`，向用户报告其绝对路径即算交付。**不启动端口服务，不读 `live_preview/lock.json`，禁止报告或编造端口 URL**
   - 改动 `svg_output/` 后必须重跑第 5 步刷新 `validation/svg_quality_report.json`，否则导出器拒收

## 环境（固定用这两个）
- Python：`C:\Users\wangRui\AppData\Local\Programs\Python\Python314\python.exe`（自带 Pillow；用托管 3.13 会把所有 `<image>` 误判为损坏）
- SKILL_DIR：`D:\南开\PPT-master\ppt-master\skills\ppt-master`

## 本轮先做什么（不要一上来就写 SVG）
先读完规约 + 源教案，然后输出一份**页面规划清单**（每页：页型 + 上行面包屑 + 下行标题 + 核心要点），交用户确认后，再开始生成 SVG。

## 重要提醒
- **内容改动必须改生成器，不要直接改 SVG**：SVG 是生成器产出物，直接手改会在下次重新生成时丢失。若已手改，需先把改动同步回 `gen_python_ch0N_content.py` 再重新生成。
- **改了页面 `title`（slug 来源）后，必须先清空 `svg_output/` 再生成**，否则旧文件残留会让标题门禁报「N 不连续」。
- 临时脚本用完即删，不要在项目根留 `scratch/`。
