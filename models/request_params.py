from pydantic import BaseModel
from typing import Dict, Hashable, Any, Optional


class PdfProcessRequestContainer(BaseModel):
    chunk_size: int = 16
    max_workers: int = 4
    additional_metadata: Optional[Dict[Hashable, Any]] = None
    strict_table_detection: bool = False
