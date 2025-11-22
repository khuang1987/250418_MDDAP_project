@echo off
cd /d %~dp0
echo ========================================
echo SA Data Cleaning ETL - MES Batch Report
echo ========================================
echo.
echo NOTE: MES processing requires SFC data to be processed first
echo If SFC data file does not exist, Checkin_SFC field will be empty
echo.
echo It is recommended to use run_all_etl.bat to run the complete process
echo.
pause
echo.
cd /d "%~dp0..\01_核心ETL程序"
echo Current directory: %CD%
python etl_dataclean_mes_batch_report.py
if %errorlevel% neq 0 (
    echo MES data processing failed, exiting
    pause >nul
    exit /b %errorlevel%
)
cd /d "%~dp0"
echo.
echo ========================================
echo Processing completed, press any key to exit...
pause >nul
