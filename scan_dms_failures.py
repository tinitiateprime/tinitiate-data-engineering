$src = "main-function\mt-dm-lambda-src"
$tests = "main-function\tests\unit"

Write-Host "`n=== REPOSITORIES MISSING TESTS ==="
Get-ChildItem "$src\db\repositories\*_repo.py" | ForEach-Object {
    $name = $_.BaseName
    $test = Join-Path "$tests\db" "test_$name.py"
    if (-not (Test-Path $test)) {
        Write-Host $name
    }
}

Write-Host "`n=== MODELS MISSING TESTS ==="
Get-ChildItem "$src\domain\models\*.py" | Where-Object {
    $_.Name -ne "__init__.py"
} | ForEach-Object {
    $name = $_.BaseName
    $test = Join-Path "$tests\domain\models" "test_$name.py"
    if (-not (Test-Path $test)) {
        Write-Host $name
    }
}

Write-Host "`n=== SERVICES MISSING TESTS ==="
Get-ChildItem "$src\domain\services\*_service.py" | ForEach-Object {
    $name = $_.BaseName
    $test = Join-Path "$tests\domain\services" "test_$name.py"
    if (-not (Test-Path $test)) {
        Write-Host $name
    }
}

Write-Host "`n=== HANDLERS MISSING TESTS ==="
Get-ChildItem "$src\v1\handlers\*.py" | Where-Object {
    $_.Name -ne "__init__.py"
} | ForEach-Object {
    $name = $_.BaseName
    $test = Join-Path "$tests\v1" "test_$name.py"
    if (-not (Test-Path $test)) {
        Write-Host $name
    }
}
