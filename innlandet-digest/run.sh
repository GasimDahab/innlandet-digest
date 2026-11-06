#!/bin/bash
# Autonomous runner for the walking skeleton
set -e
cd "$(dirname "$0")"
python3 scripts/run_digest.py
echo "Digest generated successfully."
