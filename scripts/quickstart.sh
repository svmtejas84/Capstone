#!/bin/bash
# Quick start script for toxicity-nav with new Open-Meteo + AQICN pipeline
# Run from project root: bash scripts/quickstart.sh

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Toxicity Nav - Quick Start"
echo "=============================="
echo ""

# Step 1: Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python $python_version"

# Step 2: Create/activate venv if not present
if [ ! -d ".venv" ]; then
    echo ""
    echo "✓ Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip setuptools wheel
else
    echo ""
    echo "✓ Using existing virtual environment (.venv)"
    source .venv/bin/activate
fi

# Step 3: Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -e ".[dev]" -q

# Step 4: Check/create .env
echo ""
echo "✓ Checking .env configuration..."
if [ ! -f ".env" ]; then
    echo "  Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "  ⚠️  IMPORTANT: Edit .env and add your AQICN_TOKEN:"
    echo "     nano .env"
    echo ""
else
    echo "  .env already exists"
fi

# Step 5: Check Redis
echo ""
echo "✓ Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "  Redis is running ✓"
    else
        echo "  Redis is installed but not running"
        echo "  Start Redis in another terminal:"
        echo "    redis-server"
    fi
else
    echo "  Redis not found. Install with:"
    echo "    brew install redis  # macOS"
    echo "    apt install redis-server  # Ubuntu/Debian"
    echo "    docker run -d -p 6379:6379 redis:7-alpine  # Docker"
fi

# Step 6: Display next steps
echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Make sure Redis is running:"
echo "     redis-server"
echo ""
echo "  2. In a new terminal, start the ingestor daemon:"
echo "     cd $PROJECT_ROOT"
echo "     source .venv/bin/activate"
echo "     python -m ingestion.ingestor"
echo ""
echo "  3. In another terminal, start the API server:"
echo "     cd $PROJECT_ROOT"
echo "     source .venv/bin/activate"
echo "     uvicorn router.api.main:app --reload"
echo ""
echo "  4. Frontend will be available at:"
echo "     http://localhost:5173"
echo ""
echo "Documentation:"
echo "  - docs/ARCHITECTURE.md     - Complete architecture reference"
echo "  - docs/CHANGELOG.md        - Dated change log"
echo "  - INTEGRATION_GUIDE.md      - Deployment options"
echo "  - REFACTORING_CHECKLIST.md  - What changed and why"
echo ""
