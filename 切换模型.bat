@echo off
chcp 65001 >nul
title Claude Model Switcher
PowerShell -NoExit -ExecutionPolicy Bypass -File "C:\Users\JCK\.claude\Switch-ClaudeModel.ps1"
