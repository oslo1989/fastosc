create-venv:
	@pyenv virtualenv 3.7.13 fastosc-venv-3.7.13
	#pyenv activate fastosc-venv-3.7.13

install-deps:
	@pip install --upgrade pip && pip install -r requirements.txt

upload-pip:
	@rm -rf dist
	@rm -rf src/fastosc.egg-info
	@python -m build
	@twine upload dist/*

lint-fix:
	@ruff src --quiet --fix --unsafe-fixes

lint:
	@ruff src --quiet
	@mypy src

format:
	@ruff format src

lint-format: lint-fix format lint