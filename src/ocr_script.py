from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

import json
import os
import argparse


def pdf_convert(pdf_string):

    print("start")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr=True
    pipeline_options.do_table_structure=True
    pipeline_options.table_structure_options.do_cell_matching = True
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    print("converting", pdf_string)
    result = converter.convert(pdf_string)

    output_dir = Path("../gha_texts/chapters")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = result.input.file.stem

    # markdown version
    # with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
    #     fp.write(result.document.export_to_markdown())

    # json version
    out_path = output_dir / f"{doc_filename}.json"
    print("writing ocr output", str(out_path))
    with out_path.open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(result.document.export_to_dict()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OCR script input.")
    parser.add_argument('-f', '--file', type=str, default="../gha_raw_pdf/africa7_all.pdf",
                        help='The input filename (default: ../gha_raw_pdf/africa7_all.pdf)')
    args = parser.parse_args()

    pdf_convert(args.file)
