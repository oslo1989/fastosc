upload-pip:
	@rm -rf dist
	@rm -rf src/fastosc.egg-info
	@python -m build
	@twine upload dist/*
