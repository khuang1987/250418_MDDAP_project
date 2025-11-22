@echo off
echo ========================================
echo SA Data Cleaning ETL - Complete Process
echo ========================================
echo.

echo Step 0: Converting SAP Routing Standard Time
echo ========================================
powershell -Command "cd '%~dp0..\01_核心ETL程序'; python etl_dataclean_sap_routing.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
if %errorlevel% neq 0 (
    echo SAP Routing standard time conversion failed, exiting
    pause >nul
    exit /b %errorlevel%
)

echo.
echo Step 1: Processing SFC Batch Report Data
echo ========================================
powershell -Command "cd '%~dp0..\01_核心ETL程序'; python etl_dataclean_sfc_batch_report.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
if %errorlevel% neq 0 (
    echo SFC data processing failed, exiting
    pause >nul
    exit /b %errorlevel%
)

echo.
echo Step 2: Processing MES Batch Report Data (requires SFC data)
echo ========================================
powershell -Command "cd '%~dp0..\01_核心ETL程序'; python etl_dataclean_mes_batch_report.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"
if %errorlevel% neq 0 (
    echo MES data processing failed, exiting
    pause >nul
    exit /b %errorlevel%
)

echo.
echo ========================================
echo All processing completed!
echo ========================================
echo.
echo Press any key to exit...
pause >nul
