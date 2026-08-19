py -c "import db.repositories.po_funding_detail_repo as m; print([n for n in dir(m) if not n.startswith('_')])"


cd C:\code\mt-dm-gsapdi-lambda-1
py generate_api_tests.py po_funding_detail --force
