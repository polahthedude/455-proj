#!/bin/bash
# Startup script for Cloud Storage Server
# Used by systemd service

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the server
python -m server.app
