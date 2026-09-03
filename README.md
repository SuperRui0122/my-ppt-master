# my-ppt-master 个性化配置与品牌模板库

> 专用于搭配 `ppt-master` 的极简轻量级（~22KB）插件式个性化定制扩展包。  
> 保持与原作者代码彻底解耦，永不冲突，支持跨电脑一键秒级同步与网盘备份。

---

## 一、项目架构与包含内容

推荐的本地协同工作目录结构如下：

```text
d:\南开\PPT-master\
├── ppt-master\       <- 原作者的原版完整仓库（可随时直接 git pull 享受原作者最新更新）
└── my-ppt-master\    <- 您的专属配置仓库（仅 22KB，推拉秒级完成）
```

### 仓库内核心资产清单：
- **`google-teaching/`**：Google 教学与研讨风专属四色设计规范与矢量 SVG Logo
- **`CUSTOM_STYLE_SPEC.md`**：自定义排版、字阶规范与网格版式体系
- **`apply.bat` / `apply.py`（一键注入工具）**：无论在哪台新电脑上，只要双击运行，就会自动把您的个性化模板安全挂载到 `ppt-master` 中
- **`sync_to_github.bat` / `sync_from_ppt_master.py`（一键备份工具）**：未来如果您在 `ppt-master` 中调整了配置或增加了新模板，双击它就会自动提取最新修改并推送到您的 GitHub！

---

## 二、在新电脑上的完整使用姿势（闭环极简流程）

### 步骤 1：新电脑下载原作者代码（秒级）
原作者国内 AtomGit 镜像速度极快：
```bash
git clone https://atomgit.com/hugohe3/ppt-master.git
```

### 步骤 2：获取您的个性化配置（二选一）
- **方式 A（Git 方式，推荐）**：
  ```bash
  git clone https://github.com/SuperRui0122/my-ppt-master.git
  ```
- **方式 B（网盘方式）**：  
  从夸克网盘、百度网盘或微信把下载的 `my-ppt-master` 文件夹解压到 `ppt-master` 同级目录。

### 步骤 3：一键生效
直接双击运行 `my-ppt-master` 里的 **`apply.bat`**！  
所有 Google 教学规范、品牌模板与规则引用将自动注入完成，且**以后原作者无论怎么更新代码，都不会冲突或冲掉您的定制**！

---

## 三、日常调整与修改同步

若后续在 `ppt-master` 中继续打磨了模板或增加了新设计规范：
1. 双击 `my-ppt-master/sync_to_github.bat`；
2. 脚本将自动抽取最新文件、提交并推送到 GitHub 远端；
3. 如果使用网盘，直接将 `my-ppt-master` 文件夹随手扔进网盘覆盖备份即可。
