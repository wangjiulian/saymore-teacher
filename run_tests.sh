#!/bin/bash

# Run tests with coverage reporting

echo "Installing test dependencies..."
pip install -r test-requirements.txt

echo "Running tests with coverage..."
python -m pytest tests/ -v --cov=. --cov-report=term --cov-report=html

echo "Test run complete. HTML coverage report available in htmlcov/ directory." 