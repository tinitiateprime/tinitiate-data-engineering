# Repository
py -m pytest C:\code\mt-dm-gsapdi-lambda-1\main-function\tests\unit\db\test_po_funding_detail_repo.py -v

# Model
py -m pytest C:\code\mt-dm-gsapdi-lambda-1\main-function\tests\unit\domain\models\test_po_funding_detail.py -v

# Service
py -m pytest C:\code\mt-dm-gsapdi-lambda-1\main-function\tests\unit\services\test_po_funding_detail_service.py -v

# Handler
py -m pytest C:\code\mt-dm-gsapdi-lambda-1\main-function\tests\unit\v1\test_po_funding_detail.py -v
