# Unstructured Preprocessing API
API for preprocessing unstructured documents so they are ready for ingestion into vector dbs/knowledge graphs

## Key modules
### 1. PDF processing
- /v0/pdf/upload-and-extract-pdf/
- /v0/pdf/extract-online-pdf/

### 2. Process excel files


## Return schema
The API always returns a json object if successful. The following schema will 
be followed:
- PDF:
    type: Enum("Title", "Table", "Paragraph", "NarrativeText")
    id_: str
    text: str
    metadata_template: str, defaults to `{key}: {value}` unless otherwise specified
    text_template: str, defaults to `{metadata_str}\n\n{content}`
    metadata:
        company_name: Optional[str]
        composite_figi: Optional[str]
        isin: Optional[str]
        sedol: Optional[str]
        gics_industry: Optional[str]
        source_url: str
        source: str
        publish_year: int
        report_year: int
        access_datetime: datetime
        report_type: Enum("annual_report", "esg_report", "research_report", "others")
        node_type: Enum("text", "table", "image")

