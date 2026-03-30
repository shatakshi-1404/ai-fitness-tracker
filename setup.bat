@echo off
echo.
echo  ==========================================
echo   AI Fitness Trainer — Windows Setup
echo  ==========================================
echo.

python --version >nul 2>&1 || (
  echo ERROR: Python not found. Install Python 3.9+ from python.org
  pause
  exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Installing dependencies...
venv\Scripts\pip install --upgrade pip -q
venv\Scripts\pip install -r requirements.txt

echo.
echo  Setup complete!
echo.
echo  To run the app:
echo    venv\Scripts\activate
echo    python app.py
echo.
echo  Then open: http://127.0.0.1:5000
echo.
pause
