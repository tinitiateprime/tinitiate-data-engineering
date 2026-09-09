Get-ChildItem -Path .\main-function -Recurse -Filter *.py |
    Select-String -Pattern "core\.router"


Get-ChildItem -Path .\main-function -Recurse -Filter *.py |
    Select-String -Pattern "core\.api_handler"

from core.router import router

from v1.logic import router


from core.api_handler import api_handler


from core.responses import api_handler
