@echo off
powershell -Command "cd '%~dp0..\01_核心ETL程序'; python etl_dataclean_sap_routing.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
if %errorlevel% neq 0 (
    echo SAP Routing processing failed, exiting
    pause >nul
    exit /b %errorlevel%
)
echo.
echo ========================================
echo SAP Routing processing completed!
echo ========================================
echo.
pause
