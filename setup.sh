#!/usr/bin/env bash
# ── AI Fitness Trainer — Setup Script ──────────────────
set -e
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ⚡  AI Fitness Trainer — Setup          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.9+"; exit 1; }

# Create and activate virtual environment
echo "📦  Creating virtual environment..."
python3 -m venv venv

echo "⚡  Activating venv and installing dependencies..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  ./venv/Scripts/pip install -r requirements.txt
else
  ./venv/bin/pip install --upgrade pip -q
  ./venv/bin/pip install -r requirements.txt
fi

echo ""
echo "✅  Setup complete!"
echo ""
echo "To run the app:"
echo "  source venv/bin/activate      (Mac/Linux)"
echo "  venv\\Scripts\\activate         (Windows)"
echo "  python app.py"
echo ""
echo "Then open: http://127.0.0.1:5000"
echo ""
