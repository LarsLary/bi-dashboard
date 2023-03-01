#!/bin/sh

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
clear
printf "\n"
printf "\033[1;31mThe dashboard will now load in your browser. Please do not close this console window - it must be kept open during the whole analysis.\033[0m\n"
printf '\033[0;31mPress CTRL+C to stop the app!\033[0m\n'
printf "\n"
python3 main.py
deactivate
clear
