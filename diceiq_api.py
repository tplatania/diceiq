# DiceIQ — Top-level entry point for Gunicorn
# Usage: gunicorn --bind 0.0.0.0:$PORT diceiq_api:app

from backend.app import app
