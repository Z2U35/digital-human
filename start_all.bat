@echo off

REM 初始化 conda 环境
CALL "C:\Users\lxin3\anaconda3\condabin\conda.bat" activate digitalhuman

REM 启动后端 GSVI.bat
start "" cmd /k "cd /d "%~dp0GPT-SoViTS-inference\Start" && GSVI.bat"

REM 等待后端启动（根据需要调整等待时间）
timeout /t 10 /nobreak >nul

REM 启动 main.py
start "" cmd /k "cd /d "%~dp0" && python main.py"

pause
exit
