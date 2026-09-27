---
brand_id: google-teaching
kind: brand
summary: Google brand teaching style — user-confirmed teaching deck preset (Microsoft YaHei, two-line header system, P05 section divider page, 4-color rotation)
primary_color: "#4285F4"
---

# Google Teaching Brand Specification

> Identity-only preset. No SVG page roster — pages are composed freely under these constraints.
>
> **本品牌与上游自带的 `google` 品牌的关系**：颜色 / 字体 / 语气 / 图标风格四节继承上游 `google` 品牌（`skills/ppt-master/templates/brands/google/`），并在此基础上叠加用户已确认的高校教学课件版式（§VII 章节过渡页、§VIII 内容页页眉、§IX 随堂测验交互）。差异点：**本品牌为无徽标品牌（§IV），严禁放置任何谷歌图标**。
> 上游 `google` 品牌更新时，本文件不会自动跟随；如需同步，请手动比对 `google/templates/design_spec.md` 的前六节。
>
> **权威归属**：§VII / §VIII / §IX 是本品牌的**版式实现细则**（给 Strategist 落 `design_spec.md` 用）。若与用户规约 `my-ppt-master/SKILL.md` 的 §一.4 / §一.6 / Rule 3 / Rule 5 出现不一致，**一律以 `SKILL.md` 为准**，并回来修正本文件。

## I. Brand Overview

| Property | Value |
|---|---|
| Brand Name | Google |
| Use Cases | Product launches, developer events (Google I/O style), corporate updates, multi-product decks, ecosystem education / training |
| Tone | Modern, friendly, optimistic, clear, multi-color expressive |
| Sources | Bundled Google SVG assets; [Google Brand Resource Center](https://about.google/brand-resource-center/guidance/), reviewed 2026-07-13 |

## II. Color Scheme

| Role | HEX | Provenance | Notes |
|---|---|---|---|
| primary | `#4285F4` | fact | Google Blue — extracted from `google_g_logo.svg` |
| secondary | `#34A853` | fact | Google Green |
| accent (warm) | `#FBBC05` | fact | Google Yellow |
| accent (alert) | `#EA4335` | fact | Google Red |
| text | `#202124` | approx | Standard Material / Google product UI text |
| bg | `#FFFFFF` | approx | Default light presentation background |

The four primary brand colors (Blue / Green / Yellow / Red) carry equal weight in Google brand usage; the `primary` / `secondary` / `accent` role split above is a slide-layout presentation hierarchy convention, not a brand prominence statement. Strategist may rotate any of the four into the dominant role per page rhythm.

## III. Typography

| Role | Family | Weight |
|---|---|---|
| title | `"Segoe UI", "Microsoft YaHei", sans-serif` | 500–700 |
| body | `"Segoe UI", "Microsoft YaHei", sans-serif` | 400 |

> `Google Sans` and `Roboto` are references. PPT Master neither auto-embeds fonts nor follows CSS tails in PowerPoint. The rows above are the default Windows/Office export; replace them only with a user-confirmed target-installed face.

> **Teaching-deck type scale (user-confirmed defaults, 2026-08-03)**:
> - Face: Microsoft YaHei everywhere (user-confirmed override of the default Segoe UI lead).
> - Page-header two-line system: section label 25.33px (19pt) bold; page title 32px (24pt) bold.
> - Role anchors: body 24, title 32, subtitle 32, annotation 18, code 22, footnote 16.

## IV. Logo

> **本品牌为「无徽标」品牌（user-confirmed, 2026-09-05）**：全课件严禁出现任何谷歌品牌图标。
>
> 上游 `google` 品牌的双锁标体系（`../images/google_wordmark.svg` / `../images/google_g_logo.svg`）**在本品牌中一律禁用**。`images/` 目录内保留两份上游矢量文件仅为与上游 `google` 品牌保持目录结构一致，**不作为本品牌的可选素材**。

- **封面**：仅保留课程标题、副标题与装饰色条；严禁放置 `google_wordmark.svg`。
- **内容页右上角**：保持留白；严禁放置 `google_g_logo.svg`。
- **章节过渡页 / 封底**：同封面规则。
- **理由**：教学课件需保持纯净规整的现代学术风格，不出现任何商业品牌标识，避免在课堂与对外材料中产生「背书 / 合作 / 赞助」的暗示。


## V. Voice & Tone

- Formality: neutral
- Person: we / you (English), 我们 / 你 (Chinese)
- Emoji: allowed
- Abbreviations: common-abbrev-allowed

## VI. Icon Style

- Preference: one consistent Material-aligned family; filled or stroke according to the deck context

> This is a presentation convention, not permission to imitate Google's visual identity. When the deck uses `templates/icons/`, choose one compatible family and keep weight/fill treatment consistent.

## VII. Section Page Design（章节页版式）

User-confirmed section/divider page pattern (2026-08-04) for every section opener（章节页）in teaching decks. Reuse this layout for all chapter section pages; the four Google colors rotate by section number.

- **Canvas**: white background; left 520px tinted field + left 14px solid brand-color bar (full height); right area holds one task card per 子任务 plus a footer note.
- **Section color rotation**（按节配色，数字/图标用深一号主色）:
  - 01 蓝：field `#E8F0FE` · bar/number/icon `#4285F4`
  - 02 绿：field `#E6F4EA` · bar/number/icon `#34A853`
  - 03 黄：field `#FEF7E0` · bar `#FBBC05` · number/icon `#F9AB00`
  - 04 红：field `#FCE8E6` · bar/number/icon `#EA4335`
- **Big number**: 200px bold solid brand color（`section_number` 锚点），top-left inside the tinted field (`x=100 y=380`, bounds `80 180 320 260`).
- **Title block**（浅色块内、数字下方，教案长标题上下分流法则）:
  - 当源教案小节标题含破折号 `——`、修辞比喻或排比长句时，严禁整句照搬进主标题导致折行；
  - Section title: 32px bold `#202124`，仅提纯核心技术实体，**严格 ≤ 8~10 字**（确保左栏 520px 内单行呈现，如 `一维数组与底层机制`）；
  - Subtitle: 20~24px `#5F6368`，用于消化修辞比喻或范围说明，**严格 ≤ 16 字**（如 `连续内存模型、寻址公式与 AI 协同实战`）.
- **Task cards**（右侧）: white rounded cards `600×96` rx=16, one per 子任务; 40px brand-color icon + 24px bold task name `#202124` + 18px `#5F6368` description. Keep task titles short enough to fit the 600px card.
- **Footer note**（右下）: bulb icon 36px brand color + 20px `#202124` one-line takeaway, kept short（≤约 20 字）.

## VIII. Content Page Header（内容页页眉版式 — B1 双轨面包屑 + `X.Y.N` 极简主标题体系）

User-confirmed B1 header pattern (updated 2026-09-27) for every content page（正文内容页）in teaching decks. Top-left two-line title system with strict separation of responsibilities and zero em-dashes (`——`).

- **Top-left two-line title system**（左上角 B1 双轨标题体系）:
  - **Line 1 — section & topic breadcrumb（上行面包屑导航）**: 25.33px (19pt) bold 课节主题色（如 `#4285F4`）
    - 固定格式：**`第X节 · 小节简称  ▸  X.Y 专题简称`**（如 `第三节 · 一维数组  ▸  3.1 检索效率导论`）
    - 脱水红线：严禁照搬教案破折号长标题或修辞比喻；**小节简称 ≤ 8 字**，**专题简称 ≤ 6 字**，严禁含 `——`。
  - **Line 2 — page title（下行页面主标题 · 款式 B1）**: 32px (24pt) bold `#202124`（深色）
    - 固定格式：**`X.Y.N 本页核心标题`**（如 `3.1.3 千万级数据检索效率对比`、`2.4.1 SHOW DATABASES 查库语法`）
    - 字数红线：**核心标题严格 ≤ 12 字**（含 `X.Y.N ` 前缀总长 ≤ 18 字符），严禁出现破折号 `——` 或 `专题名N——` 复读前缀，严禁堆砌超过 2 个抽象尾缀词。
  - 两行比例约 1.26:1；标签行在上（约 y=58）、标题行在下（约 y=96），页眉组 bounds 约 `40 28 1120 96`
- **Top-right area**（页眉右上角）: 保持纯净留白（**严禁使用任何谷歌品牌图标**，禁止放置 `google_g_logo.svg`），维持干净现代的教学幻灯片版式。
- **Page top accent bar**: 1280×6 `#4285F4` 细条在页面最顶部（封面/结尾页用四色分段 14px 条）。
- **Footer area**（页脚）: 页码 + 章节名，16px `#9AA0A6`；`《课程名称》·第X节` 居左、页码 `NN / Total` 居右（`x=1240 text-anchor=end`），组 bounds 约 `40 660 1200 40`。
- **Section pages** use §VII instead; cover/ending pages are exempt from this header.

## IX. Quiz & Practice Interaction Pattern（随堂测验/习题交互与动效规范）

User-confirmed quiz/exercise interaction pattern (2026-09-05) for all quiz and practice slides in teaching decks:

- **Strictly forbid revealing answers initially（严禁提前泄露答案，强制教学红线）**:
  - 测验/客观题/练习题页面进入时，**一律严禁在初始状态直接标出正确答案或展示答案解析**；
  - 必须保证课堂练习与互动的真实意义，留出独立思考时间。
- **Initial Neutral State（初始中性显示）**:
  - 题干及所有选项卡片（A、B、C、D）统一采用中性浅灰色呈现（`#F1F3F4` 底色、`#DADCE0` 边框、`#202124` 深色文字，常规字重）；
  - 正确选项不得有任何颜色高亮或字体加粗区别；
  - 底部的答案与解析提示条（`ans_bar`）**默认完全隐藏**。
- **On-Click Reveal Animation（点击分步揭晓动效）**:
  - 必须使用 PowerPoint 原生淡入动画（`entrance_fade`，时长 0.25s）：
    - **第 1 次点击（Click 1 · 揭晓第 1 题）**：第 1 题正确选项平滑淡入转为绿色高亮卡片（`#E6F4EA` 浅绿底、`#34A853` 绿色边框与加粗绿字），同时底部的答案与详细解析条伴随淡入（`with-previous`）；
    - **第 2 次点击（Click 2 · 揭晓第 2 题）**：多题页面第 2 次点击再揭晓第 2 题的高亮与解析条；
    - **再次点击**：平滑切入下一张幻灯片。
- **OOXML Timing（底层实现标准）**:
  - 通过标准 OpenXML `<p:timing>` 序列节点，为正确选项高亮层与解析条绑定 `on-click` + `with-previous` 级联时序，原生支持 PowerPoint 与 WPS 放映模式。

