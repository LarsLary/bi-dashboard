#!/bin/sh

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH='.'
python3 dash/app.py
