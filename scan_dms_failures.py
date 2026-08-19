$src = "main-function\mt-dm-lambda-src"
$tests = "main-function\tests\unit"

Get-ChildItem "$src\v1\handlers\*.py" |
Where-Object { $_.Name -ne "__init__.py" } |
ForEach-Object {

    $api = $_.BaseName

    $repoTest = Test-Path "$tests\db\test_${api}_repo.py"
    $modelTest = Test-Path "$tests\domain\models\test_${api}.py"
    $serviceTest = Test-Path "$tests\domain\services\test_${api}_service.py"
    $handlerTest = Test-Path "$tests\v1\test_${api}.py"

    [PSCustomObject]@{
        API     = $api
        DB      = if ($repoTest) {"YES"} else {"MISSING"}
        Model   = if ($modelTest) {"YES"} else {"MISSING"}
        Service = if ($serviceTest) {"YES"} else {"MISSING"}
        Handler = if ($handlerTest) {"YES"} else {"MISSING"}
    }
} | Format-Table -AutoSize
