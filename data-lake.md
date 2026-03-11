# Data Lake

A Data Lake is a centralized repository that stores raw and processed data in its native format. It supports structured, semi-structured, and unstructured data, enabling flexible analytics and machine learning.

## Key Features
- 🌊 **Schema-on-read**: Structure is applied when data is accessed, not when ingested
- ⚖️ **High variety**: Handles files, logs, images, audio, and more
- 💾 **Economical storage**: Often built on low-cost object stores (S3, ADLS)
- 🔁 **Scalable processing**: Works with batch or streaming engines

## Flow Diagram
```mermaid
flowchart LR
    A[Source Systems] --> B[Landing Zone]
    B --> C[Raw Zone]
    C --> D[Transformed Zone]
    D --> E[Analytics / ML]
    style A fill:#ffe0b2
    style B fill:#ffcc80
    style C fill:#ffe082
    style D fill:#ffd54f
    style E fill:#ffca28
``` 

## Mind Map
```mermaid
mindmap
  root((Data Lake))
    Zones
      Landing
      Raw
      Transformed
      Curated
    Data Types
      Structured
      Semi-structured
      Unstructured
    Use Cases
      Ad-hoc Queries
      ML Model Training
      Data Archiving
    Technologies
      Apache Hadoop
      AWS S3
      Azure Data Lake
      Google Cloud Storage
    Challenges
      Governance
      Cataloging
      Security
``` 

## Business Examples

### Media & Entertainment
- **Scenario**: Store video streams, user behavior logs, and social media feeds
- **Use**: Train recommendation algorithms and perform sentiment analysis

### Healthcare
- **Scenario**: Keep genomic sequences, imaging data, and EHR text notes
- **Use**: Support research, clinical decision support, and AI diagnostics

### Finance
- **Scenario**: Retain tick data, transaction logs, and customer correspondence
- **Use**: Conduct risk analytics, fraud detection, and regulatory retention

## Implementation Notes
- Data lakes often precede or complement warehouses in a lakehouse architecture
- Cataloging tools (Glue, Data Catalog, Apache Atlas) are critical for discoverability
- Enforce governance using IAM policies, encryption, and audit logging

> Data lakes provide flexibility for innovators but require discipline around metadata and security to avoid becoming data swamps.