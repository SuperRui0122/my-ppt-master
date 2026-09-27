@echo off
chcp 65001 >nul
echo.
echo  [已改名] sync_to_github.bat 现在叫 push.bat，本文件仅作兼容保留。
echo           它不再谎称「双线推送」—— 现在会如实报告推了哪几个远端。
echo.
call "%~dp0push.bat" %*
