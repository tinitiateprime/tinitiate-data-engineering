$env:PYTHONPATH="$PWD\main-function\mt-dm-lambda-src"

py -c "import v1.handlers.employees as e; print(e.__file__)"


py -m pytest main-function\tests\unit\v1\test_employees.py -v --cov=v1.handlers.employees --cov-report=term-missing
