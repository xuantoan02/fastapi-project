#!/bin/bash
set -e

echo "Running tests..."

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

pytest tests/ -v --cov=src/app --cov-report=term-missing "$@"
