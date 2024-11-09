clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build
	pip3 install -e .[dev] --upgrade --no-cache

install:
	pip3 install -e .['dev']

run:
	uvicorn app.main:app --host 0.0.0.0 --port 5001 --workers 4 --reload