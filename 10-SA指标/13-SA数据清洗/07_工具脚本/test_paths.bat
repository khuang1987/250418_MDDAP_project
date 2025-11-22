@echo off
echo Testing directory paths...
echo.

echo Current directory: %CD%
echo Script directory: %~dp0
echo.

echo Testing ETL program directory:
cd /d "%~dp0..\01_核心ETL程序"
echo ETL directory: %CD%
dir /b *.py | findstr /C:"etl_dataclean_sap_routing.py"
if %errorlevel% equ 0 (
    echo Found: etl_dataclean_sap_routing.py
) else (
    echo NOT Found: etl_dataclean_sap_routing.py
)
echo.

echo Testing test script directory:
cd /d "%~dp0..\02_测试验证脚本"
echo Test directory: %CD%
dir /b *.py | findstr /C:"test_operation_cleaning.py"
if %errorlevel% equ 0 (
    echo Found: test_operation_cleaning.py
) else (
    echo NOT Found: test_operation_cleaning.py
)
echo.

cd /d "%~dp0"
echo Back to tools directory: %CD%
pause
