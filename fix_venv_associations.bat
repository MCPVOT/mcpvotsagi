@echo off
REM Fix Python file associations for virtual environment
REM This script sets up file associations to work with the current venv

echo ================================================
echo  FIXING PYTHON FILE ASSOCIATIONS FOR VENV
echo ================================================
echo.

REM Check if we're in a virtual environment
python -c "import sys; print('Virtual environment active' if sys.prefix != sys.base_prefix else 'System Python')"

REM Get the current Python executable path
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%i

echo Current Python executable: %PYTHON_EXE%

REM Set file associations for the current user only (doesn't require admin)
echo Setting file associations for current user...

REM Create registry entries for current user
reg add "HKCU\Software\Classes\.py" /ve /t REG_SZ /d "Python.File" /f
reg add "HKCU\Software\Classes\Python.File\shell\open\command" /ve /t REG_SZ /d "\"%PYTHON_EXE%\" \"%%1\" %%*" /f

REM Also set for .pyw files
reg add "HKCU\Software\Classes\.pyw" /ve /t REG_SZ /d "Python.NoConFile" /f
reg add "HKCU\Software\Classes\Python.NoConFile\shell\open\command" /ve /t REG_SZ /d "\"%PYTHON_EXE%w\" \"%%1\" %%*" /f

echo.
echo File associations updated for current user!
echo Python scripts will now run with: %PYTHON_EXE%
echo.
echo Test by running: python test_script.py
echo.
pause
