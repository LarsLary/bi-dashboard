@ECHO OFF
python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt
cls

color 0C
echo ""
echo "The dashboard will now load in your browser. Please do not close this console window - it must be kept open during the whole analysis."
echo "Press CTRL+C to stop the app!"
echo ""
color 08

python main.py
deactivate
cls