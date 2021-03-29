"""
Common utilities for working with PDFs.
"""
import io

import fitz
import numpy as np
import PIL.Image as Image

from pathlib import Path


def get_page_images(filename, page_nums=None, dpi=300):
    """Get the images of PDF pages using PyMuPDF, returning a generator."""
    doc = fitz.open(filename)

    # Matrix for defining the DPI of the extracted images
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for ix, page in enumerate(doc):
        if page_nums is not None and ix not in page_nums:
            continue
        else:
            pix = page.getPixmap(matrix=mat, clip=None, alpha=False, annots=True)
            ret = Image.open(io.BytesIO(pix.getPNGData()))
            yield ret
