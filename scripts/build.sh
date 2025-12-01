#!/bin/bash
# Build the package for distribution
#
# Usage:
#   ./scripts/build.sh
#
# This script:
#   1. Cleans previous builds
#   2. Rebuilds the README files
#   3. Rebuilds the master prompts
#   4. Builds the Python package

set -e

cd "$(dirname "$0")/.."

echo "=== Cleaning previous builds ==="
rm -rf dist/ build/ *.egg-info

echo "=== Rebuilding README files ==="
poetry run python scripts/build_readme.py

echo "=== Rebuilding master prompts ==="
poetry run python scripts/build_master_prompt.py

echo "=== Building package ==="
poetry build

echo ""
echo "=== Build complete ==="
ls -la dist/
