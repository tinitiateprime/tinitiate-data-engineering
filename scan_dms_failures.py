cd C:\code\mt-dm-gsapdi-lambda-1\main-function

py -m pytest tests\unit -v `
  --cov=v1.handlers.financials_updated `
  --cov=domain.services.financials_updated_service `
  --cov=db.repositories.financials_updated_repo `
  --cov-report=term-missing


py -m pytest tests\unit -v -k "financials_updated" `
  --cov=v1.handlers.financials_updated `
  --cov=domain.services.financials_updated_service `
  --cov=db.repositories.financials_updated_repo `
  --cov-report=term-missing


