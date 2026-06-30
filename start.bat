@echo off
cd /d "%~dp0backend"
echo Starting Carbon Labs at http://localhost:8000
echo Press Ctrl+C to stop.
py server.py
