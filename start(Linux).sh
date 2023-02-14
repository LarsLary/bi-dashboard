#!/bin/sh

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
clear
printf 'Press CTRL+C to stop the app!\n'
python3 main.py
deactivate
clear
