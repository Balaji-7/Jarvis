#!/bin/bash

# Ensure dependencies are installed
pip install -r requirements.txt

# Start Gunicorn server on port 8000
gunicorn -w 4 -b 0.0.0.0:8000 server:app
