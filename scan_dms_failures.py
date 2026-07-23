UPDATE etl_control.etl_table_config
SET
    load_strategy = 'SNAPSHOT_REPLACE',
    updated_datetime = CURRENT_TIMESTAMP
WHERE source_schema IN ('CP', 'TE')
  AND source_table IN
  (
      'LAB_HS',
      'GL_POST_SUM',
      'GL_DETL',
      'BILLING_SUM',
      'BILLING_DETL_HIST',
      'TS_LINE',
      'TS_CELL',
      'TS',
      'TASK_EMPL',
      'TASK'
  );

UPDATE etl_control.etl_table_config
SET
    timestamp_column = 'TIME_STAMP',
    load_strategy = 'AUTO',
    updated_datetime = CURRENT_TIMESTAMP
WHERE source_schema IN ('CP', 'TE')
  AND source_table IN
  (
      'LAB_HS',
      'GL_POST_SUM',
      'GL_DETL',
      'BILLING_SUM',
      'BILLING_DETL_HIST',
      'TS_LINE',
      'TS_CELL',
      'TS',
      'TASK_EMPL',
      'TASK'
  );
