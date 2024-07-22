from .pdf_processing import split_pdf_into_chunks, pdf_has_table

from tempfile import TemporaryDirectory
import uuid
import json


def create_tempdir(session_id: str) -> TemporaryDirectory:
    return TemporaryDirectory(prefix=session_id)


def get_random_uuid():
    return uuid.uuid4()


def get_uuid_from_uname(username: str, fname: str):
    return uuid.uuid5(namespace=username, name=fname)


def save_result(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


def load_result(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
