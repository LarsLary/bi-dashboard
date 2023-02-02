@ECHO OFF
python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt
cls
echo Press CTRL+C to stop the app!
python main.py
deactivate
cls