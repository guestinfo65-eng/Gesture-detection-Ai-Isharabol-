@echo off
title IshaaraBol
echo Starting IshaaraBol server on http://localhost:8080 ...
echo Camera allow karne ke liye Chrome/Edge use karein.
if "%FIREWORKS_API_KEY%"=="" (
  echo.
  echo NOTE: FIREWORKS_API_KEY set nahi hai - AI Assistant offline replies dega.
  echo Isse set karne ke liye:  set FIREWORKS_API_KEY=fw_your_key_here
  echo.
)
python server.py
pause
