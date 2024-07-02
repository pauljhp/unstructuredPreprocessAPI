from .request_params import PdfProcessRequestContainer
from pydantic import BaseModel
from typing import Annotated, Optional, Dict, Hashable, Any


class User:
    def __init__(self, username: str, password: str = None):
        self.username = username
        self.password = password


class GetUrlPdfParamsContainer(BaseModel):
    url: str
    chunk_size: Annotated[int, "chunk size for cutting pdfs up"] = 16
    max_workers: Annotated[int, "max workers for concurrent processing"] = 4
    additional_metadata: Annotated[
        Optional[Dict[Hashable, Any]],
        "Addtional metadata to be written into the results"] = {}


LlamaIndexUnstructuredNodeTypeMap = {
    "para": "Text",
    "table": "Table",
    "list_item": "Text"
}
