py -m pip install pytest-xdist pytest-cov

py -m pytest --version

py -m pytest -n auto -q --no-cov-on-fail --dist loadscope --cov=main-function/mt-dm-lambda-src --cov=auth-function/mt-dm-lambda-auth-src --cov-report=term-missing main-function/tests auth-function/tests
