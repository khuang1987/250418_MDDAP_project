@echo off
cd /d %~dp0
echo ========================================
echo SA Data Cleaning - Test Runner
echo ========================================
echo.
echo Available test scripts:
echo.
echo 1. Operation Cleaning Test
echo 2. MES Results Verification
echo 3. PT Calculation Test
echo 4. Overdue Logic Test
echo 5. Complete Logic Verification
echo 6. All Tests
echo.
set /p choice="Please select test to run (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running Operation Cleaning Test...
    cd /d "%~dp0..\02_测试验证脚本"
    echo Current directory: %CD%
    python test_operation_cleaning.py
)
if "%choice%"=="2" (
    echo.
    echo Running MES Results Verification...
    cd /d "%~dp0..\02_测试验证脚本"
    echo Current directory: %CD%
    python verify_mes_results.py
)
if "%choice%"=="3" (
    echo.
    echo Running PT Calculation Test...
    cd /d "%~dp0..\02_测试验证脚本"
    echo Current directory: %CD%
    python test_pt_calculation.py
)
if "%choice%"=="4" (
    echo.
    echo Running Overdue Logic Test...
    cd /d "%~dp0..\02_测试验证脚本"
    echo Current directory: %CD%
    python test_overdue_logic_fix.py
)
if "%choice%"=="5" (
    echo.
    echo Running Complete Logic Verification...
    cd /d "%~dp0..\02_测试验证脚本"
    echo Current directory: %CD%
    python verify_complete_logic.py
)
if "%choice%"=="6" (
    echo.
    echo Running All Tests...
    cd /d "%~dp0..\02_测试验证脚本"
    echo Current directory: %CD%
    echo.
    echo 1/5: Operation Cleaning Test
    python test_operation_cleaning.py
    echo.
    echo 2/5: MES Results Verification
    python verify_mes_results.py
    echo.
    echo 3/5: PT Calculation Test
    python test_pt_calculation.py
    echo.
    echo 4/5: Overdue Logic Test
    python test_overdue_logic_fix.py
    echo.
    echo 5/5: Complete Logic Verification
    python verify_complete_logic.py
)

cd /d "%~dp0"
echo.
echo ========================================
echo Test completed!
echo ========================================
echo.
pause
