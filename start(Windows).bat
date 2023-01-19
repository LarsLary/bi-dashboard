@ECHO OFF
python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=.
python dash\app.py