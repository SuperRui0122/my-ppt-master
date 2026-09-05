---
name: my-ppt-master
description: >
  Custom brand presets, teaching presentation design specifications, and interactive animation rules
  for PPT Master. Defines the Google-Teaching style (Microsoft YaHei, two-line header system,
  P05 section divider page, 4-color rotation, strictly forbidden Google logos, single-image-per-slide policy,
  and native step-by-step interactive quiz reveal animations).
metadata:
  version: "1.1.0"
  author: "SuperRui0122"
  repository: "https://github.com/SuperRui0122/my-ppt-master"
---

# My PPT Master 教学课件专属设计与动效 Skill 规约

本文档为用户定制专属的教学课件制作与动效排版 Skill 规约，适用于高校与成人专科课程 PPTX 自动化生成与维护。

---

## 一、 核心排版与视觉规范（Google-Teaching 风格）

1. **画布比例**：全局统一强制为 **16:9 宽屏**（13.333 × 7.5 英寸 / 1280 × 720 像素）。
2. **全局字体**：一律使用 **微软雅黑（`Microsoft YaHei`）**，彻底替换默认的西文字体。
3. **字号阶梯**：
   - 正文：`24px` / `Pt(14~15)`
   - 页面主标题：`32px` / `Pt(24)`（加粗 bold，深黑 `#202124`）
   - 章节小标签：`25.33px` / `Pt(17~19)`（加粗 bold，主题主色）
   - 代码块：`22px` / `Pt(12~13)`
   - 注释与补充：`18px` / `Pt(11~12)`
   - 页脚与页码：`16px` / `Pt(11)`（中灰 `#9AA0A6`）
   - 过渡页大数字：`200px` / `Pt(110)`
4. **页眉与装饰条**：
   - 顶部贯穿 `6px` 专属课节主题色细条；
   - 左上角两行双轨标题（上行小标签 + 下行页面主标题，黄金比例 1.26:1）。
5. **四色轮换体系**：
   - 课节 01 蓝：主色 `#4285F4` · 浅底 `#E8F0FE`
   - 课节 02 绿：主色 `#34A853` · 浅底 `#E6F4EA`
   - 课节 03 黄：主色 `#FBBC05` · 浅底 `#FEF7E0`
   - 课节 04 红：主色 `#EA4335` · 浅底 `#FCE8E6`

---

## 二、 强制教学红线（Strict Constraints）

### 1. 严禁出现谷歌图标（No Brand Logos）
- 页面（包括封面、封底、内容页右上角等所有区域）**一律严禁放置任何谷歌品牌图标**（如 `google_g_logo.svg`、`google_wordmark.svg`）；
- 内容页右上角保持干净纯白留白，维持纯净现代的学术教学版式。

### 2. 单页独立大图原则（Single High-Res Image Per Slide）
- 实操截屏与软件界面必须保证在教室大屏与投影仪上清晰可见细节；
- **严禁单页塞入多张小截图**，所有操作向导截屏一律单页独立大图呈现，左侧为操作要点卡片，右侧为高清独立大图。

### 3. 随堂习题/测验互动动效规则（Interactive Quiz Animation）
- **严禁提前泄露答案**：习题、随堂测验、客观选择题页面进入时，**绝对禁止在初始未点击状态直接标出正确答案或展示答案解析**，确保课堂提问与互动的真实意义；
- **初始中性状态**：
  - 题目题号徽章、题干及所有选项（A、B、C、D）一律采用中性浅灰底色（`#F1F3F4`）和边框（`#DADCE0`）；
  - 正确选项不得有任何颜色高亮或字体加粗；
  - 底部的答案与解析提示条（`ans_bar`）**默认完全隐藏**；
- **分步点击揭晓动效**：
  - 必须绑定 PowerPoint 原生淡入动画（`entrance_fade`，时长 0.25s）：
    - **第 1 次点击（Click 1 · 揭晓第 1 题）**：第 1 题正确选项平滑淡入覆盖为绿色高亮卡片（浅绿底 `#E6F4EA`、深绿边框 `#34A853`、加粗绿字），同时底部的答案与详细解析条同步伴随淡入（`with-previous`）；
    - **第 2 次点击（Click 2 · 揭晓第 2 题）**：多题页面第 2 次点击再揭晓第 2 题的正确选项高亮与答案解析条；
    - **再次点击**：平滑切入下一页；
- **底层技术实现**：
  - 必须通过标准 OpenXML `<p:timing>` 序列节点与 `p:cTn` 树状结构注入动画，原生支持 PowerPoint 与 WPS 放映模式。

---

## 三、 演示者视图（Presenter View）讲稿规范

- 生成课件时，必须同步提炼 100~200 字的逐页口播讲稿与上机避坑指导；
- 通过底层 API 直接写入 PPTX 幻灯片的备注区（Notes），方便教师在放映模式下开启演示者视图随堂参考。
