from .request_params import PdfProcessRequestContainer
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict, Hashable, Any


class User:
    def __init__(self, username: str, password: str = None):
        self.username = username
        self.password = password


class GetUrlPdfParamsContainer(BaseModel):
    url: str
    chunk_size: Annotated[
        int,
        "chunk size for cutting pdfs up"
    ] = Field(default=8)
    max_workers: Annotated[
        int,
        "max workers for concurrent processing"
    ] = Field(default=16)
    additional_metadata: Annotated[
        Optional[Dict[str, Any]],
        "Addtional metadata to be written into the results"
    ] = Field(default=None)


LlamaIndexUnstructuredNodeTypeMap = {
    "para": "Text",
    "table": "Table",
    "list_item": "Text"
}
