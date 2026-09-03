# my-ppt-master 个性化配置与品牌模板库

这是专门用于搭配 `ppt-master` 使用的**轻量级个性化定制扩展包**（总大小只有 20 多 KB）。

## 包含内容
- **`google-teaching/`**：Google 教学与研讨风专属模板、四色设计规范与矢量 SVG 图标
- **`CUSTOM_STYLE_SPEC.md`**：自定义排版、网格体系与字阶样式规范
- **`apply.bat` / `apply.py`**：一键注入脚本，自动将个性化模板与配置安装到任意电脑的 `ppt-master` 中
- **`sync_to_github.bat`**：一键提取并备份脚本，当你修改或新增了新模板后，双击即可一键同步备份到 GitHub

---

## 在新电脑上使用方法

### 方式 1：Git 极速同步（秒级完成）
1. 在新电脑上克隆原作者的 `ppt-master`：
   ```bash
   git clone https://atomgit.com/hugohe3/ppt-master.git
   ```
2. 克隆本配置仓库（只有 20 KB，秒下）：
   ```bash
   git clone https://github.com/SuperRui0122/my-ppt-master.git
   ```
3. 双击运行 `my-ppt-master` 文件夹里的 **`apply.bat`**，立即完成注入！

### 方式 2：网盘备份同步（夸克网盘 / 百度网盘 / 微信）
1. 直接把整个 `my-ppt-master` 文件夹（不到 25KB）上传到夸克网盘；
2. 在新电脑上下载该文件夹，双击运行 **`apply.bat`** 即可自动注入。
