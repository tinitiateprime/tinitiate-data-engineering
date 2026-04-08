# 🟧 AWS Data Engineering

Amazon Web Services (AWS) is the oldest and most widely adopted cloud platform. An AWS Data Engineer must understand how to chain together AWS's managed services to build scalable, secure pipelines.

## 🛠️ Core AWS Data Services

### 1. 🪣 Storage
- **Amazon S3 (Simple Storage Service)**: The foundation of the AWS Data Lake. Object storage that is infinitely scalable, cheap, and highly durable (99.999999999%).

### 2. 📥 Ingestion & Streaming
- **Amazon Kinesis**: Real-time data streaming service (similar to managed Kafka).
- **AWS DMS (Database Migration Service)**: Replicates and streams changes (CDC) from on-prem or RDS databases into S3 or Redshift.

### 3. ⚙️ Processing & ETL
- **AWS Glue**: A serverless data integration service. Includes the **Glue Data Catalog** (central metadata repository) and **Glue ETL** (serverless PySpark).
- **Amazon EMR (Elastic MapReduce)**: A managed cluster platform that simplifies running big data frameworks like Apache Spark, Hadoop, and Presto.

### 4. 🗄️ Warehousing & Analytics
- **Amazon Redshift**: AWS's flagship Cloud Data Warehouse. Uses columnar storage and MPP (Massively Parallel Processing).
- **Amazon Athena**: Serverless interactive query service. Allows you to write SQL directly against files (Parquet, CSV) sitting in S3 without loading them into a database.

### 5. 🕒 Orchestration
- **AWS Step Functions**: Serverless visual workflow orchestrator.
- **Amazon MWAA (Managed Workflows for Apache Airflow)**: Fully managed Airflow environment.

## 🗺️ Standard AWS Pipeline Architecture

```mermaid
flowchart LR
    A[App DB (RDS)] -->|DMS| B[(S3 Raw Bucket)]
    C[Web Logs] -->|Kinesis Firehose| B
    
    B --> D{AWS Glue ETL<br>PySpark}
    D -->|Clean & Partition| E[(S3 Curated Bucket)]
    
    E -->|Glue Crawler| F[Glue Data Catalog]
    
    F -.-> G[(Amazon Redshift)]
    E -->|COPY Command| G
    
    F -.-> H(Amazon Athena)
    E --> H

    style B fill:#ffcc80,stroke:#e65100
    style E fill:#ffe082,stroke:#f57f17
```

## 🗣️ Interview Talking Point
*"To optimize costs and performance on AWS, I ensure that data landing in S3 is transformed into columnar formats like **Parquet** and properly **partitioned** (e.g., by `year/month/day`). This drastically reduces the amount of data scanned by Amazon Athena, lowering query times and reducing cost per query."*