from pypdf import PdfReader, PdfWriter
import pdfplumber
from typing import List
from pathlib import Path


def pdf_page_has_table(page: pdfplumber.page, strict: bool = False) -> bool:
    lines = page.lines
    text = page.extract_text()
    has_table = bool(lines) and bool(text)
    if has_table:
        if strict:
            return True
    else:
        table_settings = {
            "vertical_strategy": "text",  # or 'lines'
            "horizontal_strategy": "text",  # or 'lines'
        }
        table = page.extract_table(table_settings)
        if table:
            return True
    return False


def pdf_has_table(filepath: str, strict: bool = False) -> bool:
    # TODO - add edge case table detection
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            has_table = pdf_page_has_table(page)
            if has_table:
                return True
    return False


def split_pdf_into_chunks(
        filepath: str,
        chunk_size: int = 16
) -> List[str]:
    """splits large pdf into smaller chunks
    :return: List of the splitted document paths
    """
    filepath_obj = Path(filepath)
    filename = filepath_obj.stem.replace(" ", "_")
    output_path = filepath_obj.parent.joinpath(f"{filename}_splitted_chunks")
    output_path.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(filepath)
    current_writer = PdfWriter()
    section_num = 0
    output_dirs = []
    for page_num, page in enumerate(reader.pages):
        if page_num % chunk_size == chunk_size - 1:
            output_dir = output_path.joinpath(
                f"chunk_{section_num}__chunk_size_{chunk_size}.pdf").as_posix()
            current_writer.write(output_dir)
            output_dirs.append(output_dir)
            current_writer = PdfWriter()
            section_num += 1
        current_writer.add_page(page)

    if len(reader.pages) % chunk_size == 0 or len(reader.pages) < chunk_size:
        output_dir = output_path.joinpath(
            f"chunk_{section_num}__chunksize_{chunk_size}.pdf").as_posix()
        current_writer.write(output_dir)
        output_dirs.append(output_dir)
    return output_dirs
