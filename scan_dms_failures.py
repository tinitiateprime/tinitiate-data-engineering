Select-String `
-Path "main-function\mt-dm-lambda-src\db\repositories\po_funding_detail_repo.py" `
-Pattern "^def get_po_funding_detail" `
-Context 0,12



Get-Content ".\main-function\mt-dm-lambda-src\db\repositories\po_funding_detail_repo.py" |
Select-String -Pattern "def get_po_funding_detail" -Context 0,12
