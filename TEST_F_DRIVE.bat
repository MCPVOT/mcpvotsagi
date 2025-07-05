@echo off
echo.
echo ========================================
echo F: Drive Data Intelligence Test
echo ========================================
echo.

REM Check if F: drive exists
if exist F:\ (
    echo [OK] F: drive found
) else (
    echo [WARNING] F: drive not found - will use local storage
)

echo.
echo Testing F: Drive Integration...
echo.

REM Run the data intelligence demo
python F_DRIVE_DATA_INTELLIGENCE.py

echo.
echo ========================================
echo Test complete!
echo ========================================
echo.
pause