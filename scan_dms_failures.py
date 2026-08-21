Get-ChildItem .\main-function\mt-dm-lambda-src\domain\services -Recurse -File |
    Select-String "def get_project_forecasts"

Get-ChildItem .\main-function\mt-dm-lambda-src\db\repositories -Recurse -File |
    Select-String "project_forecast"
