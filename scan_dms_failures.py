git diff -- tests/unit/db/test_employee_profile_complete_repo.py

git diff -- tests/unit/domain/services/test_employee_profile_complete_service.py

git add tests/unit/db/test_employee_profile_complete_repo.py
git add tests/unit/domain/services/test_employee_profile_complete_service.py

git diff --cached --name-only

git commit -m "Increase employee profile complete coverage"
git push

