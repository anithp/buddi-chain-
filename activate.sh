#!/bin/bash
# Activation script for Buddi Tokenization PoC virtual environment

echo "🐍 Activating virtual environment..."

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python3 start.py' first."
    exit 1
fi

source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📍 You can now run:"
echo "   - python app/main.py (to start the server)"
echo "   - python scripts/setup_db.py (to setup database)"
echo "   - python scripts/demo_data.py (to create demo data)"
echo ""
echo "🛑 To deactivate, run: deactivate"
