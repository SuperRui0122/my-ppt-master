@echo off
chcp 65001 >nul
setlocal
echo.
echo  [my-ppt-master] SVG 课件翻页预览器
echo  ------------------------------------------------
echo.

if not "%~1"=="" (
  python "%~dp0build_preview.py" %*
) else (
  rem 先静默探测当前目录；失败则兜底批量处理 projects 下所有册
  python "%~dp0build_preview.py" . 2>nul
  if errorlevel 1 (
    echo  [提示] 当前目录下没找到 svg_output，改为批量处理 projects 下所有册...
    echo.
    python "%~dp0build_preview.py" "%~dp0..\ppt-master\projects" --all
  )
)

set RC=%errorlevel%
echo.
if %RC% neq 0 (
  echo  [失败] 退出码 %RC% —— 请查看上面的错误信息。
) else (
  echo  [完成] 用浏览器打开各册目录下的 preview.html 即可翻页浏览。
)
echo.
pause
