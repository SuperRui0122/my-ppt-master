@echo off
chcp 65001 >nul
echo [1/2] 正在从 ppt-master 提取最新个性化配置...
python "%~dp0sync_from_ppt_master.py"
if %errorlevel% neq 0 (
    echo 同步失败，请检查路径。
    pause
    exit /b
)

echo [2/2] 正在推送到 GitHub (SuperRui0122/my-ppt-master)...
cd /d "%~dp0"
git add .
git commit -m "update: sync personalized configurations"
git push origin main
echo.
echo [完成] 最新个性化配置已成功同步推送到 GitHub！
pause
