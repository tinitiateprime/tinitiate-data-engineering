{
  "entity": "ContractModifications",
  "entity_snake": "contract_modifications",
  "entity_plural_snake": "contract_modifications",
  "materialized_view": "gold.contract_modifications_vw",
  "logical_id_field": "project_id",
  "lookup_field": "project_id",
  "default_sort_field": "effective_date",
  "route_base": "/v1/contracts/modifications",
  "columns": [
    {
      "name": "project_id",
      "col": "project_id",
      "type": "text",
      "alias": "projectId",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "mod_number",
      "col": "mod_number",
      "type": "text",
      "alias": "modNumber",
      "required": true,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "reason_for_modification",
      "col": "reason_for_modification",
      "type": "text",
      "alias": "reasonForModification",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "award_status",
      "col": "award_status",
      "type": "int",
      "alias": "awardStatus",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "effective_date",
      "col": "effective_date",
      "type": "timestamptz",
      "alias": "effectiveDate",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "negotiated_value",
      "col": "negotiated_value",
      "type": "numeric",
      "alias": "negotiatedValue",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "exercised_value",
      "col": "exercised_value",
      "type": "numeric",
      "alias": "exercisedValue",
      "required": false,
      "sortable": true,
      "selectable": true
    },
    {
      "name": "funded_amount",
      "col": "funded_amount",
      "type": "numeric",
      "alias": "fundedAmount",
      "required": false,
      "sortable": true,
      "selectable": true
    }
  ]
}
