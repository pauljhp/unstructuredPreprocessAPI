from typing import Annotated, List, Any, Optional, Dict, Hashable, Union
from pathlib import Path
from fastapi import (
    Depends,
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    responses
)
from fastapi.security import OAuth2PasswordBearer
from models import GetUrlPdfParamsContainer
from api import concurrent_partition_pdf
from tempfile import NamedTemporaryFile, TemporaryDirectory
import io
import requests
import utils
from deprecated import deprecated


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

task_status = {}
result_dir = Path("~/task_results")
result_dir.mkdir(exist_ok=True, parents=True)


def process_pdf_file(
        task_id: str,
        file_path: str,
        chunk_size: int = 8,
        max_workers: int = 16,
        additional_metadata: Dict[str, Any] = {}):
    task_status[task_id] = "pending"
    try:
        print("processing")
        extracted_elems = concurrent_partition_pdf(
            file_name=file_path,
            chunk_size=chunk_size,
            max_workers=max_workers,
            additional_metadata=additional_metadata
        )
        result_path = result_dir.joinpath(f"{task_id}.json")
        utils.save_result(extracted_elems, result_path.as_posix())
        task_status[task_id] = "completed"
    finally:
        Path(file_path).unlink()
    print("finished")


@app.get("/")
def root():
    return {"Introduction": "Unstructured extract file api. v1.0"}


@app.post("/v1/pdf/extract-pdf/")
async def create_file(background_tasks: BackgroundTasks,
                      file: UploadFile = File(...),
                      chunk_size: int = 8,
                      max_workers: int = 16,
                      additional_metadata: Optional[Dict[str, Any]] = None):
    if additional_metadata is None:
        additional_metadata = {}
    task_id = str(utils.get_random_uuid())
    tf = NamedTemporaryFile(mode="wb", delete=False)
    await file.seek(0)
    data = await file.read()
    tf.write(data)
    tf.close()

    task_status[task_id] = "initiated"
    background_tasks.add_task(
        process_pdf_file,
        task_id,
        tf.name,
        chunk_size,
        max_workers,
        additional_metadata
    )
    return {"task_id": task_id}


@app.post("/v1/pdf/extract-pdf-from-url/")
async def create_file(background_tasks: BackgroundTasks,
                      items: GetUrlPdfParamsContainer):
    if items.additional_metadata is None:
        items.additional_metadata = {}
    task_id = str(utils.get_random_uuid())
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
                status_code=400,
                detail="Failed to fetch PDF from URL."
            )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error happened. {e}"
        )
    finally:
        tf.close()

    task_status[task_id] = "initiated"
    background_tasks.add_task(
        process_pdf_file,
        task_id,
        tf.name,
        items.chunk_size,
        items.max_workers,
        items.additional_metadata
    )
    return {"task_id": task_id}


@app.get("/v1/tasks/get-results/{task_id}")
async def get_result(task_id: str) -> responses.JSONResponse:
    result_path = result_dir.joinpath(f"{task_id}.json")
    print(result_path.as_posix())
    if result_path.exists():
        result = utils.load_result(result_path)
        return responses.JSONResponse(
            status_code=200,
            content=result
        )
    else:
        return responses.JSONResponse(
            status_code=404,
            content={"message": "Result not found or already retrieved."}
        )


@app.get("/v1/tasks/status/{task_id}")
async def get_status(task_id: str) -> responses.JSONResponse:
    status = task_status.get(task_id)
    match status:
        case "initiated" | "pending":
            return responses.JSONResponse(
                status_code=202,
                content={"message": {"status": status}}
            )
        case "completed":
            return responses.JSONResponse(
                status_code=200,
                content={"message": {"status": status}}
            )
        case "removed":
            return responses.JSONResponse(
                status_code=501,
                content={"message": {"status": status}}
            )
        case _:
            return responses.JSONResponse(
                status_code=404,
                content={"message": f"task id {task_id} does not exist!"}
            )


@app.get("/v1/cleanup/{task_id}")
async def remove_task(task_id: str) -> Dict[str, str]:
    result_path = result_dir.joinpath(f"{task_id}.json")
    result_path.unlink()
    task_status["task_id"] = "removed"
    return {"message": f"success! {task_id} removed"}


# @deprecated(version="1.0", reason="The /v0/ endpoints have been deprecated. Use /v1/ instead")
# @app.post("/v0/pdf/extract-pdf/")
# async def create_file(
#     file: UploadFile = File(...),
#     chunk_size: Annotated[int, "chunk size for cutting pdfs up"] = 8,
#     max_workers: Annotated[int, "max workers for concurrent processing"] = 16,
#     additional_metadata: Annotated[Optional[Dict[Hashable, Any]],
#                                    "Addtional metadata to be written into the results"] = {}
# ):
#     tf = NamedTemporaryFile(mode="wb", delete=False)
#     try:
#         await file.seek(0)
#         data = await file.read()
#         if not data:
#             raise ValueError("No data in file")

#         tf.write(data)
#         tf.flush()
#     finally:
#         tf.close()

#     try:
#         extracted_elems = concurrent_partition_pdf(
#             file_name=tf.name,
#             chunk_size=chunk_size,
#             max_workers=max_workers,
#             additional_metadata=additional_metadata
#         )
#         return extracted_elems
#     finally:
#         Path(tf.name).unlink()


# @deprecated(version="1.0", reason="The /v0/ endpoints have been deprecated. Use /v1/ instead")
# @app.post("/v0/pdf/extract-pdf-from-url/")
# def get_content(
#     items: GetUrlPdfParamsContainer
# ):
#     tf = NamedTemporaryFile(mode="wb", delete=False)
#     try:
#         res = requests.get(items.url)
#         if res.status_code == 200:
#             data = io.BytesIO(res.content)
#             data.seek(0)
#             tf.write(data.getvalue())
#             tf.flush()
#         else:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to fetch PDF from URL."
#             )
#     except requests.RequestException as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"An error happened. {e}"
#         )
#     finally:
#         tf.close()

#     try:
#         extracted_elems = concurrent_partition_pdf(
#             file_name=tf.name,
#             chunk_size=items.chunk_size,
#             max_workers=items.max_workers,
#             additional_metadata=items.additional_metadata
#         )
#         return extracted_elems
#     finally:
#         Path(tf.name).unlink()
