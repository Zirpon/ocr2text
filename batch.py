#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2016 findingorder <https://github.com/findingorder>
# SPDX-License-Identifier: MIT

"""Example of using ocrmypdf as a library in a script.

This script will recursively search a directory for PDF files and run OCR on
them. It will log the results. It runs OCR on every file, even if it already
has text. OCRmyPDF will detect files that already have text.

You should edit this script to meet your needs.

#ocrmypdf.ocr(input_file: PathOrIO, output_file: PathOrIO, *, language: Iterable[str] | None = None, image_dpi: int | None = None, output_type: str | None = None, sidecar: StrPath | None = None, jobs: int | None = None, use_threads: bool | None = None, title: str | None = None, author: str | None = None, subject: str | None = None, keywords: str | None = None, rotate_pages: bool | None = None, remove_background: bool | None = None, deskew: bool | None = None, clean: bool | None = None, clean_final: bool | None = None, unpaper_args: str | None = None, oversample: int | None = None, remove_vectors: bool | None = None, force_ocr: bool | None = None, skip_text: bool | None = None, redo_ocr: bool | None = None, skip_big: float | None = None, optimize: int | None = None, jpg_quality: int | None = None, png_quality: int | None = None, jbig2_lossy: bool | None = None, jbig2_page_group_size: int | None = None, pages: str | None = None, max_image_mpixels: float | None = None, tesseract_config: Iterable[str] | None = None, tesseract_pagesegmode: int | None = None, tesseract_oem: int | None = None, tesseract_thresholding: int | None = None, pdf_renderer: str | None = None, tesseract_timeout: float | None = None, tesseract_non_ocr_timeout: float | None = None, rotate_pages_threshold: float | None = None, pdfa_image_compression: str | None = None, user_words: os.PathLike | None = None, user_patterns: os.PathLike | None = None, fast_web_view: float | None = None, plugins: Iterable[StrPath] | None = None, plugin_manager=None, keep_temporary_files: bool | None = None, progress_bar: bool | None = None, **kwargs)

"""

#############################
# 批量pdf图片 ocr识别文字 转换为可复制文字的pdf 仅此而已
#############################
from __future__ import annotations

import logging
import sys
from pathlib import Path

import ocrmypdf
from pdf2docx import Converter
from pdf2docx import parse

# pylint: disable=logging-format-interpolation
# pylint: disable=logging-not-lazy

script_dir = Path(__file__).parent
print(script_dir)

if len(sys.argv) > 1:
    start_dir = Path(sys.argv[1])
else:
    start_dir = Path('.')

print(start_dir)

if len(sys.argv) > 2:
    log_file = Path(sys.argv[2])
else:
    log_file = script_dir.with_name('ocr-tree.log')

print(log_file)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    filename=log_file,
    filemode='a',
)

ocrmypdf.configure_logging(ocrmypdf.Verbosity.quiet)

for filename in start_dir.glob("**/*.pdf"):
    logging.info(f"Processing {filename}")
    print(f"Processing {filename}")
    print(filename)
    output_file = f"{filename}_tmp.pdf"
    print(output_file)

    result = ocrmypdf.ocr(filename, output_file, deskew=True, language=["chi_sim","eng"], jobs=2, skip_text=True, progress_bar=True, optimize=1, png_quality=30, jpeg_quality=40)
    #, jbig2_page_group_size=1

    if result == ocrmypdf.ExitCode.already_done_ocr:
        logging.error("Skipped document because it already contained text")
    elif result == ocrmypdf.ExitCode.ok:
        logging.info("OCR complete")
    logging.info(result)

    #pdf 转 doc

    docx_file = f"{filename}_tmp.docx"
    #parse(filename, docx_file)

    cv = Converter(output_file)
    cv.convert(docx_file)
    cv.close()
