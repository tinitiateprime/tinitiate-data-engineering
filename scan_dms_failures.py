Get-ChildItem main-function\tests\unit -Recurse -File |
Select-Object -ExpandProperty FullName

Get-ChildItem main-function\tests\unit -Recurse -File |
Where-Object { $_.Name -match "ar_history|gl_details|financials_updated|non_labor|period_target|po_funding|po_open|project_status|real_time|timesheet|voucher" } |
Select-Object -ExpandProperty FullName

