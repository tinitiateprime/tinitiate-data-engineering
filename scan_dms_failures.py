Get-ChildItem tests -Recurse -Filter "*financials_updated*"

py -m pytest `
tests\unit\db\test_financials_updated_repo.py `
tests\unit\domain\models\test_financials_updated.py `
tests\unit\domain\services\test_financials_updated_service.py `
tests\unit\v1\test_financials_updated.py `
-v `
--cov=db.repositories.financials_updated_repo `
--cov=domain.models.financials_updated `
--cov=domain.services.financials_updated_service `
--cov=v1.handlers.financials_updated `
--cov-report=term-missing

