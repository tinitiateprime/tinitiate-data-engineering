Get-ChildItem .\tests\unit\db\test_project_modifications_repo.py

py -m pytest .\tests\unit\db\test_project_modifications_repo.py -v --cov=db.repositories.project_modifications_repo --cov-report=term-missing

Get-ChildItem .\tests\unit\db\*project_modifications*

py -m pytest .\tests\unit\domain\models\test_project_modifications.py -v --cov=domain.models.project_modifications --cov-report=term-missing

py -m pytest .\tests\unit\domain\services\test_project_modifications_service.py -v --cov=domain.services.project_modifications_service --cov-report=term-missing

py -m pytest .\tests\unit\v1\test_project_modifications.py -v --cov=v1.handlers.project_modifications --cov-report=term-missing

Get-ChildItem .\tests\unit\db\*project_modifications*
