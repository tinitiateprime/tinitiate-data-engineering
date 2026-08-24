"first_name": {"col": "first_name", "type": "text"},
"last_name": {"col": "last_name", "type": "text"},
"mid_name": {"col": "mid_name", "type": "text"},


"first_name",
"last_name",
"mid_name",


first_name: Optional[str] = Field(None, alias="firstName")
last_name: Optional[str] = Field(None, alias="lastName")
mid_name: Optional[str] = Field(None, alias="midName")


{
  "firstName": "...",
  "lastName": "...",
  "midName": "...",
  "employeeName": "..."
}
