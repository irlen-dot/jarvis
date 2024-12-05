@echo off
poetry install
poetry run pyinstaller --onefile --name jarvis jarvis/jarvis/cli.py
echo Executable created in dist/jarvis.exe