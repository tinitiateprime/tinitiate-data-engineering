{
  "entity": "IrcCensusReport",
  "entity_snake": "irc_census_report",
  "entity_plural_snake": "irc_census_reports",
  "physical_view": "irc_census_report_mv",
  "logical_id_field": "row_id",
  "lookup_field": "row_id",
  "default_sort_field": "row_id",
  "route_base": "/v1/irc-census-reports",
  "columns": [
    {
      "name": "row_id",
      "col": "row_id",
      "type": "int",
      "alias": "rowId",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "my_id",
      "col": "MY_ID",
      "type": "text",
      "alias": "myId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "last_first_name",
      "col": "LAST_FIRST_NAME",
      "type": "text",
      "alias": "lastFirstName",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "prir_name",
      "col": "PRIR_NAME",
      "type": "text",
      "alias": "prirName",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "s_empl_status_cd",
      "col": "S_EMPL_STATUS_CD",
      "type": "text",
      "alias": "sEmplStatusCd",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "hire_dt",
      "col": "HIRE_DT",
      "type": "date",
      "alias": "hireDt",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "reh_dt",
      "col": "REH_DT",
      "type": "date",
      "alias": "rehDt",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "term_dt",
      "col": "TERM_DT",
      "type": "date",
      "alias": "termDt",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "seniority_dt",
      "col": "SENIORITY_DT",
      "type": "date",
      "alias": "seniorityDt",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "term_reason_cd",
      "col": "TERM_REASON_CD",
      "type": "text",
      "alias": "termReasonCd",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "taxble_entity_id",
      "col": "TAXBLE_ENTITY_ID",
      "type": "text",
      "alias": "taxbleEntityId",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "locator_cd",
      "col": "LOCATOR_CD",
      "type": "text",
      "alias": "locatorCd",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "empl_class_cd",
      "col": "EMPL_CLASS_CD",
      "type": "text",
      "alias": "emplClassCd",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "pto_accrl_cd",
      "col": "PTO_ACCRL_CD",
      "type": "text",
      "alias": "ptoAccrlCd",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "bu_name",
      "col": "BU_NAME",
      "type": "text",
      "alias": "buName",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "dept_num",
      "col": "DEPT_NUM",
      "type": "text",
      "alias": "deptNum",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "detl_job_cd",
      "col": "DETL_JOB_CD",
      "type": "text",
      "alias": "detlJobCd",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "title_desc",
      "col": "TITLE_DESC",
      "type": "text",
      "alias": "titleDesc",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "mgr_name",
      "col": "MGR_NAME",
      "type": "text",
      "alias": "mgrName",
      "required": false,
      "sortable": true,
      "selectable": true
    }
  ]
}
