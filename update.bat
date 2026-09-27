@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  [my-ppt-master] 正在更新上游 ppt-master 并重新挂载定制配置 ...
echo  （本仓库自身 → 还原上游文件 → git pull --rebase → 重新安装 → 自检）
echo.
python "%~dp0update.py" %*
set RC=%errorlevel%
echo.
if %RC% neq 0 echo  [失败] 退出码 %RC% —— 请查看上面的错误信息。
if %RC% equ 0 echo  [完成] 上游已更新，定制配置已重新挂载。
echo.
pause
