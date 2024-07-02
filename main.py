from typing import Annotated, List, Any, Optional, Dict, Hashable
from pathlib import Path
from fastapi import (
    Depends,
    FastAPI,
    File,
    UploadFile,
    HTTPException
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from models import GetUrlPdfParamsContainer
from api import concurrent_partition_pdf
from tempfile import NamedTemporaryFile
import io
import requests


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
def root():
    return {"Introduction": "Unstructured extract file api. v0.0"}


@app.post("/v0/pdf/extract-pdf/")
async def create_file(
    file: UploadFile = File(...),
    chunk_size: Annotated[int, "chunk size for cutting pdfs up"] = 16,
    max_workers: Annotated[int, "max workers for concurrent processing"] = 4,
    additional_metadata: Annotated[Optional[Dict[Hashable, Any]],
                                   "Addtional metadata to be written into the results"] = {}
):
    tf = NamedTemporaryFile(mode="wb", delete=False)
    try:
        await file.seek(0)
        data = await file.read()
        if not data:
            raise ValueError("No data in file")

        tf.write(data)
        tf.flush()
    finally:
        tf.close()

    try:
        extracted_elems = concurrent_partition_pdf(
            file_name=tf.name,
            chunk_size=chunk_size,
            max_workers=max_workers,
            additional_metadata=additional_metadata
        )
        return extracted_elems
    finally:
        Path(tf.name).unlink()


@app.post("/v0/pdf/extract-pdf-from-url/")
def get_content(
    items: GetUrlPdfParamsContainer
):
    tf = NamedTemporaryFile(mode="wb", delete=False)
    try:
        res = requests.get(items.url)
        if res.status_code == 200:
            data = io.BytesIO(res.content)
            data.seek(0)
            tf.write(data.getvalue())
            tf.flush()
        else:
            raise HTTPException(
                status_code=400, detail="Failed to fetch PDF from URL.")
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"An error happened. {e}")
    finally:
        tf.close()

    try:
        extracted_elems = concurrent_partition_pdf(
            file_name=tf.name,
            chunk_size=items.chunk_size,
            max_workers=items.max_workers,
            additional_metadata=items.additional_metadata
        )
        return extracted_elems
    finally:
        Path(tf.name).unlink()
