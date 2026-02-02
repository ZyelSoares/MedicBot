@echo off
title MediBot - Robo de Manutenção
:: Solicita permissão de administrador e executa o MediBot
powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0MediBot.ps1\"' -Verb RunAs"
