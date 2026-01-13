#!/bin/bash
# Backend test runner script

echo "==================================="
echo "Running Backend Tests (pytest)"
echo "==================================="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with coverage
pytest --cov=apps --cov-report=html --cov-report=term-missing -v

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo "📊 Coverage report: backend/htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi
