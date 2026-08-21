git ls-files main-function/mt-dm-lambda-src/domain/models/project_status_report.py

git show HEAD:main-function/mt-dm-lambda-src/domain/models/project_status_report.py



git add main-function/mt-dm-lambda-src/domain/services/project_status_report_service.py

git commit -m "Fix project status report service tests"
git push origin jay-api-coverage-fix


git grep -n "test_lvl_no" -- main-function/tests/unit/domain/services/test_project_status_report_service.py

git add main-function/mt-dm-lambda-src/domain/services/project_status_report_service.py
