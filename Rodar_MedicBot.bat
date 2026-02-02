@echo off
cd /d "%~dp0"
REM Inicia o MedicBot e fecha o CMD na hora (evita janela atrás).
REM Prefira usar Rodar_MedicBot.vbs para não ver nenhum terminal.
start /B pythonw medicbot.py
exit
