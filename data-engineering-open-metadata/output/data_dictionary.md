# Data Dictionary

## Scope

This dictionary covers Bronze, Silver, and Gold layer database objects.

## bronze_layer.dept

**Layer:** BRONZE

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| deptno | integer | NO |  |  |
| dname | character varying | YES |  |  |
| loc | character varying | YES |  |  |

## bronze_layer.emp

**Layer:** BRONZE

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| empno | integer | NO |  |  |
| ename | character varying | YES |  |  |
| job | character varying | YES |  |  |
| mgr | numeric | YES |  |  |
| hiredate | date | YES |  |  |
| sal | numeric | YES |  |  |
| commission | numeric | YES |  |  |
| deptno | integer | YES |  |  |

## bronze_layer.emp_projects

**Layer:** BRONZE

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| emp_projectno | integer | NO |  |  |
| empno | integer | NO |  |  |
| projectno | integer | NO |  |  |
| start_date | date | YES |  |  |
| end_date | date | YES |  |  |

## bronze_layer.projects

**Layer:** BRONZE

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| projectno | integer | NO |  |  |
| project_name | character varying | YES |  |  |
| budget | numeric | YES |  |  |
| monthly_commission | numeric | YES |  |  |

## bronze_layer.salgrade

**Layer:** BRONZE

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| grade | integer | YES |  |  |
| losal | integer | YES |  |  |
| hisal | integer | YES |  |  |

## gold_layer.vw_department_salary_summary

**Layer:** GOLD

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| deptno | integer | YES |  |  |
| department_name | character varying | YES |  |  |
| department_location | character varying | YES |  |  |
| employee_count | bigint | YES |  |  |
| total_salary | numeric | YES |  |  |
| average_salary | numeric | YES |  |  |
| minimum_salary | numeric | YES |  |  |
| maximum_salary | numeric | YES |  |  |
| total_commission | numeric | YES |  |  |
| total_compensation | numeric | YES |  |  |

## gold_layer.vw_employee_department_report

**Layer:** GOLD

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| empno | integer | YES |  |  |
| employee_name | character varying | YES |  |  |
| job | character varying | YES |  |  |
| manager_empno | numeric | YES |  |  |
| hiredate | date | YES |  |  |
| salary | numeric | YES |  |  |
| commission | numeric | YES |  |  |
| total_compensation | numeric | YES |  |  |
| deptno | integer | YES |  |  |
| department_name | character varying | YES |  |  |
| department_location | character varying | YES |  |  |
| years_of_service | numeric | YES |  |  |

## gold_layer.vw_employee_project_assignment_report

**Layer:** GOLD

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| emp_projectno | integer | YES |  |  |
| empno | integer | YES |  |  |
| employee_name | character varying | YES |  |  |
| job | character varying | YES |  |  |
| department_name | character varying | YES |  |  |
| projectno | integer | YES |  |  |
| project_name | character varying | YES |  |  |
| budget | numeric | YES |  |  |
| monthly_commission | numeric | YES |  |  |
| start_date | date | YES |  |  |
| end_date | date | YES |  |  |
| project_status | text | YES |  |  |
| project_duration_days | integer | YES |  |  |

## gold_layer.vw_employee_salary_grade_report

**Layer:** GOLD

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| empno | integer | YES |  |  |
| employee_name | character varying | YES |  |  |
| job | character varying | YES |  |  |
| salary | numeric | YES |  |  |
| salary_grade | integer | YES |  |  |
| grade_min_salary | integer | YES |  |  |
| grade_max_salary | integer | YES |  |  |
| department_name | character varying | YES |  |  |
| department_location | character varying | YES |  |  |
| salary_position | text | YES |  |  |

## gold_layer.vw_project_summary_report

**Layer:** GOLD

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| projectno | integer | YES |  |  |
| project_name | character varying | YES |  |  |
| budget | numeric | YES |  |  |
| monthly_commission | numeric | YES |  |  |
| assigned_employee_count | bigint | YES |  |  |
| project_first_start_date | date | YES |  |  |
| project_last_end_date | date | YES |  |  |
| total_employee_salary | numeric | YES |  |  |
| total_employee_commission | numeric | YES |  |  |
| total_employee_compensation | numeric | YES |  |  |
| project_status | text | YES |  |  |

## silver_layer.dept

**Layer:** SILVER

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| deptno | integer | NO |  |  |
| dname | character varying | YES |  |  |
| loc | character varying | YES |  |  |

## silver_layer.emp

**Layer:** SILVER

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| empno | integer | NO |  |  |
| ename | character varying | YES |  |  |
| job | character varying | YES |  |  |
| mgr | numeric | YES |  |  |
| hiredate | date | YES |  |  |
| sal | numeric | YES |  |  |
| commission | numeric | YES |  |  |
| deptno | integer | YES |  |  |

## silver_layer.emp_projects

**Layer:** SILVER

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| emp_projectno | integer | NO |  |  |
| empno | integer | NO |  |  |
| projectno | integer | NO |  |  |
| start_date | date | YES |  |  |
| end_date | date | YES |  |  |

## silver_layer.projects

**Layer:** SILVER

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| projectno | integer | NO |  |  |
| project_name | character varying | YES |  |  |
| budget | numeric | YES |  |  |
| monthly_commission | numeric | YES |  |  |

## silver_layer.salgrade

**Layer:** SILVER

| Column | Data Type | Nullable | Description | Source / Lineage Notes |
|---|---|---|---|---|
| grade | integer | NO |  |  |
| losal | integer | YES |  |  |
| hisal | integer | YES |  |  |

