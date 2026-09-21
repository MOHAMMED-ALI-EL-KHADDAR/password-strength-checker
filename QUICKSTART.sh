#!/bin/bash
# Password Strength Checker - Quick Start Setup Script
# Runs on macOS, Linux, and Windows (Git Bash)

set -e  # Exit on error

echo "🔐 Password Strength Checker - Setup"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $python_version found"

# Check if version >= 3.10
min_version="3.10"
if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" != "$min_version" ]; then
    echo "⚠️  Warning: Python 3.10+ recommended (found $python_version)"
fi

echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi
echo "✓ Virtual environment activated"

echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo ""
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    echo "   1. Activate venv: venv\\Scripts\\activate"
else
    # macOS/Linux
    echo "   1. Activate venv: source venv/bin/activate"
fi
echo "   2. Run: python3 main.py"
echo ""
echo "📖 For more info, see README.md"
echo ""
