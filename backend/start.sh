#!/bin/bash
# Exit on error
set -e

echo "Starting backend..."
echo "Current directory: $(pwd)"
echo "Listing directory contents:"
ls -la

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:.
echo "PYTHONPATH set to: $PYTHONPATH"

# Run Uvicorn
# app.main:app means: look for module 'app', submodule 'main', object 'app'
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
