curl.exe -X GET "https://mt-dm-data.hii-next-dev.com/test/v1/contracts/111120" `
  -H "Authorization: Bearer <TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{"filters":{"proj_id":{"eq":"111120.430"}},"page":{"limit":50}}'
