py -m pytest tests\unit\db\test_employee_profile_complete_repo.py -v --cov=db.repositories.employee_profile_complete_repo --cov-report=term-missing

py -m pytest tests\unit\domain\services\test_employee_profile_complete_service.py -v --cov=domain.services.employee_profile_complete_service --cov-report=term-missing

py -m pytest tests\unit\db\test_employee_profile_complete_repo.py tests\unit\domain\models\test_employee_profile_complete.py tests\unit\domain\services\test_employee_profile_complete_service.py tests\unit\v1\test_employee_profile_complete.py -v
