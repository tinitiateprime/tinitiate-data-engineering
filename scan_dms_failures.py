# PROJECT INFO
git add tests/unit/db/test_project_info_repo.py
git add tests/unit/domain/models/test_project_info.py
git add tests/unit/domain/services/test_project_info_service.py
git add tests/unit/v1/test_project_info.py

# PROJECT FINANCIAL
git add tests/unit/v1/test_project_financial.py

# PO FUNDING DETAIL
git add tests/unit/db/test_po_funding_detail_repo.py
git add tests/unit/domain/services/test_po_funding_detail_service.py
git add tests/unit/v1/test_po_funding_detail.py

# GL DETAILS
git add tests/unit/db/test_gl_details_repo.py
git add tests/unit/domain/services/test_gl_details_service.py
git add tests/unit/v1/test_gl_details.py

git diff --cached --name-only

git status

git commit -m "Add unit test coverage for project info, project financial, PO funding detail, and GL details"

git push origin jay-api-coverage-fix
