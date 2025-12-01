#!/bin/bash
# Deploy the package to PyPI
#
# Usage:
#   ./scripts/deploy_pypi.sh [--test]
#
# Options:
#   --test    Deploy to TestPyPI instead of production PyPI
#
# Prerequisites:
#   - poetry-plugin-pypi-token or PYPI_TOKEN environment variable
#   - For TestPyPI: TEST_PYPI_TOKEN environment variable
#
# To set up tokens:
#   poetry config pypi-token.pypi <your-pypi-token>
#   poetry config pypi-token.testpypi <your-testpypi-token>

set -e

cd "$(dirname "$0")/.."

# Check for --test flag
USE_TEST_PYPI=false
if [[ "$1" == "--test" ]]; then
    USE_TEST_PYPI=true
fi

# Build first
echo "=== Building package ==="
./scripts/build.sh

echo ""
if $USE_TEST_PYPI; then
    echo "=== Deploying to TestPyPI ==="
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry publish -r testpypi
    echo ""
    echo "=== Deployed to TestPyPI ==="
    echo "Install with: pip install -i https://test.pypi.org/simple/ nice-vibes"
else
    echo "=== Deploying to PyPI ==="
    poetry publish
    echo ""
    echo "=== Deployed to PyPI ==="
    echo "Install with: pip install nice-vibes"
fi
