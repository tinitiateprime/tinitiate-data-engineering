first_name: Optional[str] = Field(
    default=None,
    validation_alias="first_name",
    serialization_alias="firstName",
)

last_name: Optional[str] = Field(
    default=None,
    validation_alias="last_name",
    serialization_alias="lastName",
)

mid_name: Optional[str] = Field(
    default=None,
    validation_alias="mid_name",
    serialization_alias="midName",
)


sotv_employee_id: Optional[str] = Field(
    default=None,
    validation_alias="sotv_employee_id",
    serialization_alias="sotvEmployeeId",
)

first_name: Optional[str] = Field(
    default=None,
    validation_alias="first_name",
    serialization_alias="firstName",
)

last_name: Optional[str] = Field(
    default=None,
    validation_alias="last_name",
    serialization_alias="lastName",
)

mid_name: Optional[str] = Field(
    default=None,
    validation_alias="mid_name",
    serialization_alias="midName",
)

employee_name: Optional[str] = Field(
    default=None,
    validation_alias="employee_name",
    serialization_alias="employeeName",
)
"first_name": {"operators": {"eq", "in", "contains"}},
"last_name": {"operators": {"eq", "in", "contains"}},
"mid_name": {"operators": {"eq", "in", "contains"}},


"first_name",
"last_name",
"mid_name",

"firstName": "first_name",
"lastName": "last_name",
"midName": "mid_name",

