# Data Warehouse

A Data Warehouse (DW) is a centralized repository designed for analytics and reporting. It stores structured, cleaned, and integrated data from multiple sources, optimized for query performance.

## Core Characteristics
- 🧱 **Schema-on-write**: Data is structured when it enters the warehouse
- ⏱️ **Time-variant**: Historical data is preserved for trend analysis
- 📊 **Subject-oriented**: Organized around business domains (sales, finance, marketing)
- 🛡️ **Non-volatile**: Data is stable and not overwritten routinely

## Flow Diagram
```mermaid
flowchart TD
    A[Operational Systems] --> B[ETL/ELT Processes]
    B --> C[Data Warehouse]
    C --> D[BI Tools & Dashboards]
    C --> E[Data Science]
    style A fill:#ffebee
    style B fill:#ffe0b2
    style C fill:#c8e6c9
    style D fill:#bbdefb
    style E fill:#e3f2fd
``` 

## Mind Map
```mermaid
mindmap
  root((Data Warehouse))
    Characteristics
      Schema on write
      Time variant
      Subject oriented
      Non volatile
    Components
      ETL/ELT
      Fact tables
      Dimension tables
      OLAP Cubes
    Workloads
      Reporting
      Dashboards
      Ad-hoc analysis
    Technologies
      Snowflake
      Redshift
      BigQuery
      Azure Synapse
    Examples
      Retail sales
      Banking ledgers
      Healthcare claims
``` 

## Business Examples

### Retail
- **Scenario**: Consolidate POS, e-commerce, and inventory data
- **Outcome**: Daily and monthly sales dashboards for executives

### Healthcare
- **Scenario**: Combine claims, patient, and treatment data
- **Outcome**: Regulatory compliance reports and cost analysis

### Finance
- **Scenario**: Store trading, balances, and customer data
- **Outcome**: Risk analytics and quarterly financial reports

## Implementation Notes
- Modern warehouses are cloud-native (Snowflake, BigQuery) with elastic scaling
- Combine with a semantic layer (LookML, dbt) for business user accessibility
- Data marts or schema separation often used for multi-department access

> A warehouse provides a single source of truth for structured analytical needs and remains central to BI ecosystems.