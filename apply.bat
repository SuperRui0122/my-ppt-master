@echo off
chcp 65001 >nul
echo 正在安装 Google-Teaching 个性化配置到 ppt-master...
python "%~dp0apply.py"
pause
