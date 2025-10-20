@echo off
REM Trading Scanner Streamlit Dashboard Launcher for Windows
REM This script activates the virtual environment and starts the Streamlit app

echo 🚀 Starting Trading Scanner Dashboard...

REM Activate virtual environment
if exist ".venv" (
    echo 📦 Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found. Please run: python -m venv .venv
    exit /b 1
)

REM Install/update dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt

REM Start Streamlit
echo 🌐 Launching Streamlit dashboard...
echo 💡 Dashboard will be available at: http://localhost:8501
echo 💡 Use Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py --server.port 8501 --server.address localhost