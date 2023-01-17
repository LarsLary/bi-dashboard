dirs := dash vis computation database

quality:
	black --check --preview $(dirs)
	isort --check-only $(dirs)
	flake8 $(dirs)
	
format:
	isort $(dirs)
	black --preview $(dirs)
