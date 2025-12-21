@echo off
echo ========================================
echo Building AutoClicker Executable
echo ========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Build with PyInstaller
echo Building executable...
python -m PyInstaller AutoClicker.spec --clean
echo.

if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo Build successful!
    echo Executable location: dist\AutoClicker.exe
    echo ========================================
    echo.
    echo Opening dist folder...
    explorer dist
) else (
    echo ========================================
    echo Build failed! Check errors above.
    echo ========================================
)

pause
