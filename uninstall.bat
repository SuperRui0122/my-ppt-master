@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  [my-ppt-master] 正在卸载：还原上游文件 + 删除品牌目录 ...
echo.
python "%~dp0apply.py" --uninstall
set RC=%errorlevel%
echo.
if %RC% neq 0 echo  [失败] 退出码 %RC% —— 请查看上面的错误信息。
if %RC% equ 0 echo  [完成] 已卸载，ppt-master 已还原干净。
echo.
pause
