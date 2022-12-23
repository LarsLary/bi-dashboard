dirs := dash vis computation

quality:
	black --check --preview $(dirs)
	isort --check-only --profile black $(dirs)
	flake8 $(dirs)
	
format:
	isort --profile black $(dirs)
	black --preview $(dirs)
