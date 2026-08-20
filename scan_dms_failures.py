{
  "entity": "EmployeeProfile",
  "entity_snake": "employee_profile",
  "entity_plural_snake": "employee_profiles",
  "materialized_view": "employee_profile_complete_vw",
  "logical_id_field": "employee_key",
  "lookup_field": "employee_key",
  "default_sort_field": "employee_key",
  "route_base": "/v1/employee-profiles",
  "columns": [
    {
      "name": "employee_key",
      "col": "employee_key",
      "type": "text",
      "alias": "employeeKey",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "email_key",
      "col": "email_key",
      "type": "text",
      "alias": "emailKey",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "empl_id",
      "col": "empl_id",
      "type": "text",
      "alias": "emplId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "my_id",
      "col": "my_id",
      "type": "text",
      "alias": "myId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "sotv_employee_id",
      "col": "sotv_employee_id",
      "type": "text",
      "alias": "sotvEmployeeId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "employee_name",
      "col": "employee_name",
      "type": "text",
      "alias": "employeeName",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "job_title",
      "col": "job_title",
      "type": "text",
      "alias": "jobTitle",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "org_id",
      "col": "org_id",
      "type": "text",
      "alias": "orgId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "dept_name",
      "col": "dept_name",
      "type": "text",
      "alias": "deptName",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "location",
      "col": "location",
      "type": "text",
      "alias": "location",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "mgr_name",
      "col": "mgr_name",
      "type": "text",
      "alias": "mgrName",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "mgr_empl_id",
      "col": "mgr_empl_id",
      "type": "text",
      "alias": "mgrEmplId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "hire_date",
      "col": "hire_date",
      "type": "date",
      "alias": "hireDate",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "clearance_status",
      "col": "clearance_status",
      "type": "text",
      "alias": "clearanceStatus",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "clearance_eligibility",
      "col": "clearance_eligibility",
      "type": "text",
      "alias": "clearanceEligibility",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "sotv_headline",
      "col": "sotv_headline",
      "type": "text",
      "alias": "sotvHeadline",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "certifications",
      "col": "certifications",
      "type": "jsonb",
      "alias": "certifications",
      "required": false,
      "sortable": false,
      "selectable": true
    },
    {
      "name": "certification_names",
      "col": "certification_names",
      "type": "text[]",
      "alias": "certificationNames",
      "required": false,
      "sortable": false,
      "selectable": true
    },
    {
      "name": "certification_count",
      "col": "certification_count",
      "type": "bigint",
      "alias": "certificationCount",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "skills",
      "col": "skills",
      "type": "jsonb",
      "alias": "skills",
      "required": false,
      "sortable": false,
      "selectable": true
    },
    {
      "name": "skill_names",
      "col": "skill_names",
      "type": "text[]",
      "alias": "skillNames",
      "required": false,
      "sortable": false,
      "selectable": true
    },
    {
      "name": "skill_count",
      "col": "skill_count",
      "type": "bigint",
      "alias": "skillCount",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "education",
      "col": "education",
      "type": "jsonb",
      "alias": "education",
      "required": false,
      "sortable": false,
      "selectable": true
    },
    {
      "name": "education_count",
      "col": "education_count",
      "type": "bigint",
      "alias": "educationCount",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "languages",
      "col": "languages",
      "type": "text[]",
      "alias": "languages",
      "required": false,
      "sortable": false,
      "selectable": true
    },
    {
      "name": "language_count",
      "col": "language_count",
      "type": "bigint",
      "alias": "languageCount",
      "required": false,
      "sortable": true,
      "selectable": true
    }
  ]
}
