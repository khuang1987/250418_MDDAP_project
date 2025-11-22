@echo off
echo Testing SAP Routing script...
echo.
echo Script directory: %~dp0
echo.
echo Target directory: %~dp0..\01_核心ETL程序
echo.
cd /d "%~dp0..\01_核心ETL程序"
echo Current directory: %CD%
echo.
echo Files in directory:
dir /b *.py
echo.
echo Running SAP Routing script...
python etl_dataclean_sap_routing.py
echo.
echo Exit code: %errorlevel%
pause
