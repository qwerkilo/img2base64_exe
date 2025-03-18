@echo off
cd /d "%~dp0"
cmd /c venv\Scripts\python.exe -m pyinstaller --noconfirm --onefile --windowed --add-data "config.json;." --add-data "styles.py;." "main.py"