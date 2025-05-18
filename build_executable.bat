@echo off
echo ===================================
echo Good-GYM - Building Executable
echo ===================================
echo.

echo Creating GPU virtual environment (if not exists)...
if not exist gpu_env (
    python -m venv gpu_env
    call gpu_env\Scripts\activate.bat
    
    echo Installing PyTorch with GPU support...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
    
    echo Installing other dependencies...
    pip install -r requirements.txt
    pip install pyinstaller
) else (
    call gpu_env\Scripts\activate.bat
)

echo.
echo Building application...

REM Creating output directory
if not exist dist mkdir dist

REM Using PyInstaller to package the application
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --icon=assets/Logo.png ^
    --add-data "assets;assets/" ^
    --add-data "yolo11s-pose.pt;." ^
    --name "Good-GYM" ^
    --hidden-import=cv2 ^
    --hidden-import=PyQt5 ^
    --hidden-import=torch ^
    --hidden-import=ultralytics ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    workout_qt_modular.py

echo.
if exist dist\Good-GYM.exe (
    echo Build successful! Executable located at: dist\Good-GYM.exe
    echo.
    echo You can now run dist\Good-GYM.exe to start the application.
) else (
    echo Build failed, please check error messages.
)

echo.
echo Press any key to exit...
pause > nul 