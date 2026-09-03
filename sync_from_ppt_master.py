# -*- coding: utf-8 -*-
"""
从本地 ppt-master 同步个性化配置更新到本仓库
"""
import os
import sys
import shutil

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(current_dir, "..", "ppt-master"),
        os.path.join(current_dir, "ppt-master"),
        os.path.join(os.path.dirname(current_dir), "PPT-master", "ppt-master"),
    ]
    
    target_dir = None
    for c in candidates:
        norm = os.path.abspath(c)
        if os.path.isdir(norm) and os.path.isdir(os.path.join(norm, "skills", "ppt-master")):
            target_dir = norm
            break
            
    if not target_dir:
        print("[错误] 未检测到 ppt-master 目录。")
        sys.exit(1)

    print(f"[*] 检测到 ppt-master: {target_dir}")
    
    # 同步 google-teaching 模板
    src_brand = os.path.join(target_dir, "skills", "ppt-master", "templates", "brands", "google-teaching")
    dst_brand = os.path.join(current_dir, "google-teaching")
    if os.path.exists(src_brand):
        shutil.copytree(src_brand, dst_brand, dirs_exist_ok=True)
        print(f"[+] 已同步模板文件到本仓库")

    # 同步 CUSTOM_STYLE_SPEC.md
    src_spec = os.path.join(target_dir, "CUSTOM_STYLE_SPEC.md")
    dst_spec = os.path.join(current_dir, "CUSTOM_STYLE_SPEC.md")
    if os.path.exists(src_spec):
        shutil.copy2(src_spec, dst_spec)
        print(f"[+] 已同步样式规范到本仓库")

    print("[SUCCESS] 同步完成！接下来将自动推送到 GitHub...")

if __name__ == "__main__":
    main()
