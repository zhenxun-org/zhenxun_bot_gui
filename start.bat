@echo off
cd /d %~dp0
echo 启动真寻Bot GUI...
poetry run python run.py
pause