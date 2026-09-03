# -*- coding: utf-8 -*-
"""
一键安装/注入个性化配置到 ppt-master
"""
import os
import sys
import json
import shutil

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 自动探测 ppt-master 目录
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
        print("[提示] 未在默认位置检测到 ppt-master 目录。")
        val = input("请输入 ppt-master 项目的绝对路径: ").strip().strip('"')
        if os.path.isdir(val):
            target_dir = val
        else:
            print("[错误] 找不到指定的 ppt-master 路径: " + val)
            sys.exit(1)

    print(f"[*] 检测到 ppt-master 路径: {target_dir}")
    
    # 1. 复制 google-teaching 模板目录
    src_brand = os.path.join(current_dir, "google-teaching")
    dst_brand = os.path.join(target_dir, "skills", "ppt-master", "templates", "brands", "google-teaching")
    if os.path.exists(src_brand):
        os.makedirs(dst_brand, exist_ok=True)
        shutil.copytree(src_brand, dst_brand, dirs_exist_ok=True)
        print(f"[+] 已复制模板: {dst_brand}")
    else:
        print("[警告] 本地未找到 google-teaching 目录")

    # 2. 复制 CUSTOM_STYLE_SPEC.md
    src_spec = os.path.join(current_dir, "CUSTOM_STYLE_SPEC.md")
    dst_spec = os.path.join(target_dir, "CUSTOM_STYLE_SPEC.md")
    if os.path.exists(src_spec):
        shutil.copy2(src_spec, dst_spec)
        print(f"[+] 已复制规范: {dst_spec}")

    # 3. 注册到 brands_index.json
    index_file = os.path.join(target_dir, "skills", "ppt-master", "templates", "brands", "brands_index.json")
    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            brands = data.get("brands", [])
            already = any(b.get("id") == "google-teaching" for b in brands)
            if not already:
                brands.append({
                    "id": "google-teaching",
                    "name": "Google 教学与研讨风",
                    "description": "基于 Google Design 规范的浅色现代教学与研讨型 PPT，具备标志性四色点缀与规整排版体系",
                    "dir": "templates/brands/google-teaching"
                })
                data["brands"] = brands
                with open(index_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("[+] 已注册 google-teaching 到 brands_index.json")
            else:
                print("[=] brands_index.json 中已存在 google-teaching，无需重复添加")
        except Exception as e:
            print(f"[警告] 注册 brands_index.json 失败: {e}")

    # 4. 检查并提示规则引用
    for rule_file in ["AGENTS.md", "CLAUDE.md"]:
        rf_path = os.path.join(target_dir, rule_file)
        if os.path.exists(rf_path):
            with open(rf_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "CUSTOM_STYLE_SPEC.md" not in content:
                with open(rf_path, "a", encoding="utf-8") as f:
                    f.write("\n- 优先参考自定义风格规范：`CUSTOM_STYLE_SPEC.md`\n")
                print(f"[+] 已向 {rule_file} 追加 CUSTOM_STYLE_SPEC.md 引用")
            else:
                print(f"[=] {rule_file} 已包含规范引用")

    print("\n[SUCCESS] Google-Teaching 个性化配置注入完成！可以在 ppt-master 中直接使用！\n")

if __name__ == "__main__":
    main()
