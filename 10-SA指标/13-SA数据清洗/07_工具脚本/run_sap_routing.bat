@echo off
cd /d %~dp0
echo ========================================
echo SA Data Cleaning ETL - SAP Routing
echo ========================================
echo.
echo Processing SAP Routing Standard Time...
echo.
cd /d "%~dp0..\01_核心ETL程序"
echo Current directory: %CD%
python etl_dataclean_sap_routing.py
if %errorlevel% neq 0 (
    echo SAP Routing processing failed, exiting
    pause >nul
    exit /b %errorlevel%
)
cd /d "%~dp0"
echo.
echo ========================================
echo SAP Routing processing completed!
echo ========================================
echo.
echo Press any key to exit...
pause >nul
