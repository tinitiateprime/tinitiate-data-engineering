cd C:\code\mt-dm-gsapdi-lambda-1\main-function\mt-dm-lambda-src
py -c "import domain.services.po_funding_detail_service as m; [print(n) for n in dir(m) if not n.startswith('_')]"
