# AGENTS.md（my-ppt-master 携带 · 可跨环境复用）

> 本文件随 `my-ppt-master` 仓库一起分发。每到一个新环境，把它**复制到包含
> `ppt-master/` 与 `my-ppt-master/` 的同级父目录（即工作区根）**即可自动生效；
> 或让 `apply.py` 在 install 时自动写过去（见下方「部署」）。

## 我是谁

`my-ppt-master` 是 `ppt-master` 的**教学课件定制覆盖层**。它的规则
**优先级高于上游一切默认流程**，冲突一律以它为准。

## 必读顺序（任何 ppt 生成任务，动手前必须照此，不许跳过）

1. `my-ppt-master/RED_LINES.md` —— **最高优先级红线**（R1~R6）。
2. `my-ppt-master/SKILL.md` —— 教学排版与动效规约，含 **§6 无动画纯静态两页版**。
3. `ppt-master/skills/ppt-master/SKILL.md` —— 上游默认流程。

> 若只读到了第 3 层就动手，即为违规。务必先读第 1、2 层。
> 更稳的做法：先跑 `python my-ppt-master/apply.py`，它会把上面第 1、2 层
> 的指针**直接注入上游 SKILL.md 顶部**，从此无论哪次会话都先看到红线。

## 四条硬闸门

- **① 停在 SVG（R1）**：写完 `<项目>/svg_output/` + 跑完 SVG 质量门即停。
  **严禁同一轮导出 PPTX**。导出须用户明确说「导出 / 定稿 / 可以了 / export」。
- **② 真实预览（R4，双轨都要）**：质量门后 ① 用 `python my-ppt-master/build_preview.py <项目目录>`
  生成单文件 `preview.html`；② 再起端口服务
  `ppt-master/skills/ppt-master/scripts/svg_editor/server.py <项目目录> --live --timeout 0`
  （或把 `my-ppt-master/live_preview.bat` 复制到项目根双击），真实 URL 从
  `<项目目录>/live_preview/lock.json` 读取。**不得用文字描述页面，不得编造端口**。
- **③ 成人教育走静态版（SKILL.md §6）**：`ppt-mysql-adult` 等成人专科项目，
  凡"点击揭晓答案"的习题页，**必须拆成 A 提问页 / B 揭晓页 两页静态**，
  禁用 `animations.json` 与任何 `<p:timing>` 动画（§3 动画版不适用）。
- **④ 开工声明（R3）**：每轮第一条消息写明当前 **route / profile / Step 编号**。

## 跨环境部署（三选一，推荐第 1 种）

1. **跑 apply.py（首选）**：`python my-ppt-master/apply.py` —— 自动把红线与
   指针注入上游 SKILL.md，并（若启用）把本文件写到工作区根。重装幂等。
2. **手动复制**：把本 `AGENTS.md` 复制到 `ppt-master/` 的同级父目录
   （也就是工作区根目录，使其与 `ppt-master/`、`my-ppt-master/` 同级）。
3. **提示词兜底**：任务提示词开头加一句
   "按 `my-ppt-master/RED_LINES.md`（最高优先级）走；只到 SVG+质量门+真实预览，
   成人项目习题页走 §6 静态两页禁动画；严禁导出 PPTX，等我确认。"
   这条不依赖任何文件，换环境最省心。

## 故障自检

新环境若怀疑规则没生效，跑 `python my-ppt-master/apply.py --check`，
看上游 SKILL.md 是否含「USER RED LINES / MY-PPT-MASTER POINTER」受管块。
