@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  [my-ppt-master] 正在提交并推送到所有远端（Gitee + GitHub）...
echo.
python "%~dp0push.py" %*
set RC=%errorlevel%
echo.
if %RC% neq 0 echo  [失败] 退出码 %RC% —— 请查看上面的错误信息。
if %RC% equ 0 echo  [完成] 已推送。
echo.
pause
