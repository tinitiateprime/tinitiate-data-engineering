cd C:\code\mt-dm-gsapdi-lambda-1\main-function

py -m pytest `
tests\unit\db\test_gl_details_repo.py `
tests\unit\domain\models\test_gl_details.py `
tests\unit\domain\services\test_gl_details_service.py `
tests\unit\v1\test_gl_details.py `
-v `
--cov=db.repositories.gl_details_repo `
--cov=domain.models.gl_details `
--cov=domain.services.gl_details_service `
--cov=v1.handlers.gl_details `
--cov-report=term-missing
