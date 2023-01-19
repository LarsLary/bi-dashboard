dirs := dash vis computation database

build:
	pyinstaller dash/app.py
	pyinstaller app.spec

quality:
	black --check --preview $(dirs)
	isort --check-only $(dirs)
	flake8 $(dirs)
	
format:
	isort $(dirs)
	black --preview $(dirs)
