import argparse
import io
import logging
import sys

import fitz
import numpy as np
import PIL.Image as Image

from pathlib import Path


try:
    import logzero

    logger = logzero.setup_logger(__name__)
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)


def main(argv=None):
    """Parse arguments (or use supplied `argv`) and run the script."""
    # Define the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pdf_1",
        type=argparse.FileType("r"),
        help="First input PDF",
    )

    parser.add_argument(
        "pdf_2",
        type=argparse.FileType("r"),
        help="Second input PDF",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default="diff.pdf",
        help="The resulting diff of the PDFs.",
    )
    parser.add_argument(
        "--method",
        type=str,
        default="any",
        choices={"any", "xor"},
        help="The method to use for visualizing differences.",
    )
    parser.add_argument(
        "--dpi",
        type=float,
        default=192,
        help="DPI (resolution) to use for comparisons.",
    )

    # Set logging verbosity
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="Logging verbosity",
    )
    verbosity.add_argument(
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="verbose",
        help="Logging verbosity",
    )


    # Actually parse the arguments
    args = vars(parser.parse_args(argv))

    # Set logging level
    logger.setLevel(args["verbose"])

    # Debug message for logging type
    if "logzero" in sys.modules:
        logger.debug("Using `logzero` for logging.")
    else:
        logger.debug("`logzero` unavailable, using default logging module.")

    # Perform the comparison
    out_doc = compare_pdfs(
        args["pdf_1"], args["pdf_2"], dpi=args["dpi"], method=args["method"]
    )

    out_doc.save(args["output"])


def image_diff(img_a, img_b, method="xor") -> Image:
    """Compute the difference between two images."""
    # Convert to array
    arr_a = np.array(img_a)
    arr_b = np.array(img_b)

    # Difference
    diff = np.array(arr_a) ^ np.array(arr_b)
    diff = np.atleast_3d(diff)  # Handles 2d and single-channel 3d images

    # Image from difference
    img_result = np.empty((*diff.shape[:2], 3), dtype=np.uint8)

    # Blank page, white background
    img_result[:, :] = [255, 255, 255]  # white page

    if method == "xor":
        # XOR of pages
        img_result ^= diff
    elif method == "any":
        # Any difference --> red
        img_result[np.any(diff, axis=-1)] = [255, 0, 0]
    else:
        raise ValueError(f"Unknown image diff method: {method!r}")

    # Save diff to buffer
    buf = io.BytesIO()
    Image.fromarray(img_result).save(buf, format="JPEG")

    return buf.getvalue()


def compare_pdfs(path_a, path_b, dpi=300, **kwargs):
    """Compare two PDFs, producing an output PDF for the differences.

    Currently assumes that the two PDFs are of the same length and dimensions,
    like you've just made a small change to one and want to verify that they're
    no visually indistinguishable.
    """
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    # Images for the two documents to compare
    doc_a = fitz.open(path_a)
    doc_b = fitz.open(path_b)

    # TODO: initial comparisons for the documents, e.g., number of pages

    # The PDF constructed based on the differences
    ret = fitz.open()

    # Iterate over pairs of pages
    for ix, (page_a, page_b) in enumerate(zip(doc_a, doc_b)):
        # Get page rectangles
        rect = page_a.rect

        # Check that the rectangles are the same
        if page_a.rect != page_b.rect:
            logger.info("Different page rects?")
            logger.info(f"{page_a.rect}")
            logger.info(f"page_b.rect")

        # Get pixmap
        pix_a = page_a.getPixmap(matrix=mat, clip=None, alpha=False, annots=True)
        pix_b = page_b.getPixmap(matrix=mat, clip=None, alpha=False, annots=True)

        # Get images from PNGs
        img_a = Image.open(io.BytesIO(pix_a.getPNGData()))
        img_b = Image.open(io.BytesIO(pix_b.getPNGData()))

        # Perform the comparison
        result = image_diff(img_a, img_b, **kwargs)

        # New page in output document
        out_page = ret.new_page(-1, width=rect.width, height=rect.height)

        # Insert difference in new page
        out_page.insert_image(rect, stream=result)

    return ret
