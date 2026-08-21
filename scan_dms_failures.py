cd C:\code\mt-dm-gsapdi-lambda-1\main-function

git status
git branch --show-current

git add tests/unit/db/test_financials_updated_repo.py
git add tests/unit/domain/models/test_financials_updated.py
git add tests/unit/domain/services/test_financials_updated_service.py
git add tests/unit/v1/test_financials_updated.py

git add tests/unit/db/test_gl_details_repo.py
git add tests/unit/domain/models/test_gl_details.py
git add tests/unit/domain/services/test_gl_details_service.py
git add tests/unit/v1/test_gl_details.py

git add tests/unit/db/test_po_funding_detail_repo.py
git add tests/unit/domain/models/test_po_funding_detail.py
git add tests/unit/domain/services/test_po_funding_detail_service.py
git add tests/unit/v1/test_po_funding_detail.py

git status
git diff --cached --stat

git commit -m "Add generated unit tests for financials, GL details, and PO funding"

git push origin jay-api-coverage-fix

