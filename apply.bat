@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  [my-ppt-master] 正在安装教学规约与品牌模板到 ppt-master ...
echo.
where python >nul 2>nul
if errorlevel 1 echo  [失败] 找不到 python 命令，请先安装 Python 并加入 PATH。
if errorlevel 1 pause
if errorlevel 1 exit /b 1
python "%~dp0apply.py"
set RC=%errorlevel%
echo.
if %RC% neq 0 echo  [失败] 退出码 %RC% —— 请查看上面的错误信息。
if %RC% equ 0 echo  [完成] 安装成功，可以在 ppt-master 中开始备课了。
echo.
pause
