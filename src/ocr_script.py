from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

import json
import os


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
    # pdf_convert("../Angela Suhas Project Proposal.pdf")
    # pdf_convert("../gha_raw_pdf/Africa7.pdf")

    # path = "../gha_raw_pdf/chapters"
    # for filename in os.listdir(path):
    #     if filename.split('.')[-1] != "pdf":
    #         continue
    #     file_path = os.path.join(path, filename)
    #     print("converting ", str(file_path))
    #     pdf_convert(str(file_path))

    # for volume in ["../gha_raw_pdf/africa6_all.pdf", "../gha_raw_pdf/africa7_all.pdf"]:
    pdf_convert("../gha_raw_pdf/chapters/africa7_10.pdf")
