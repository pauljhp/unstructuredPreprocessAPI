# Unstructured Preprocessing API
API for preprocessing unstructured documents so they are ready for ingestion into vector dbs/knowledge graphs

## Key modules

### 1. PDF processing
- /v1/pdf/extract-pdf/
Submit a task by uploading a file. 
Usage: 
`res = requests.post(endpoint, files={"file": open(filepath, "rb")}, json=data)`

- /v1/pdf/extract-pdf-from-url/
Similar to the `extract-pdf` endpoint, but instead of uploading a file, just submit the url to the pdf file. 

- /v1/tasks/get-results/{task_id}
Used for retrieving finished tasks

- /v1/tasks/status/{task_id}
Used for querying task status. 202 means task is pending. Status code 404 means task does not exist. 


Deprecated:
- /v0/pdf/upload-and-extract-pdf/
- /v0/pdf/extract-online-pdf/

### 2. Process excel files


### Usage


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