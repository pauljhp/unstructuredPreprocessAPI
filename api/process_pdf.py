from utils import split_pdf_into_chunks, pdf_has_table
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.pdf import Element
from typing import List, Optional, Dict, Hashable, Any
from pathlib import Path
from markdownify import markdownify as md
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from urllib3.exceptions import LocationValueError
from llama_index.readers.smart_pdf_loader import SmartPDFLoader
from models import LlamaIndexUnstructuredNodeTypeMap
# import itertools


HI_RES_MODEL_NAME = "detectron2_onnx"  # latest ocr model
LLMSHERPA_API_URL = os.environ.get("LLMSHERPA_API_URL")


def unstructured_partition_pdf(
    file_name: str,
    additional_metadata: Optional[Dict[Hashable, Any]] = None,
    strict_table_detection: bool = False
) -> List[Element]:
    """assumes files follow the `chunk_{no}_chunk_size_{chunk_size}"""
    try:
        fpath = Path(file_name)
        fname = fpath.stem
        chunk_no = int(fname.split("__")[0].split("_")[-1])
        chunk_size = int(fname.split("__")[1].split("_")[-1])
        has_table = pdf_has_table(file_name, strict=strict_table_detection)
        if has_table:
            # print("extracting tables")
            elems = partition_pdf(
                file_name,
                strategy="hi_res",
                infer_table_structure=True,
                chunking_strategy="by_title",
                hi_res_model_name=HI_RES_MODEL_NAME
            )
            elements = []
            for elem in elems:
                element = elem.to_dict()
                if "coordinates" in element["metadata"].keys():
                    element["metadata"].pop("coordinates")
                element["metadata"]["page_number"] += chunk_no * chunk_size
                if elem.category == "Table":
                    element["text"] = element["metadata"].pop("text_as_html")
                    element["text"] = md(element["text"])
                if additional_metadata is not None:
                    element["metadata"].update(additional_metadata)
                elements.append(element)
            return elements
        else:
            # print("no tables detected")
            elements = []
            try:
                loader = SmartPDFLoader(llmsherpa_api_url=LLMSHERPA_API_URL)
                documents = loader.load_data(file_name)
                for document in documents:
                    document = document.to_dict()
                    document["metadata"]["node_type"] = document["metadata"]\
                        .pop("chunk_type")
                    document["metadata"]["node_type"] = LlamaIndexUnstructuredNodeTypeMap\
                        .get(document["metadata"]["node_type"])

            except LocationValueError:  # no host specified with smartpdf
                elems = partition_pdf(
                    file_name,
                    strategy="fast",
                    infer_table_structure=False,
                    chunking_strategy="by_title",
                )

                for elem in elems:
                    element = elem.to_dict()
                    element["id_"] = element.pop("element_id")
                    element["metadata"]["page_number"] += chunk_no * chunk_size
                    element["metadata_template"] = "{key}: {value}"
                    element["text_template"] = "{metadata_str}\n\n{content}"

                    if "coordinates" in element["metadata"].keys():
                        element["metadata"].pop("coordinates")

                    if additional_metadata is not None:
                        element["metadata"].update(additional_metadata)

                    elements.append(element)
            return elements
    except UnicodeDecodeError:
        return {}


def concurrent_partition_pdf(
    file_name: str,
    chunk_size: int = 16,
    max_workers: int = 4,
    additional_metadata: Optional[Dict[Hashable, Any]] = None
) -> List[Element]:
    splitted_filenames = split_pdf_into_chunks(
        file_name,
        chunk_size=chunk_size
    )
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                unstructured_partition_pdf,
                fname,
                additional_metadata
            )
            for fname in splitted_filenames]
        for future in as_completed(futures):
            elements = future.result()
            results += elements
    return results
