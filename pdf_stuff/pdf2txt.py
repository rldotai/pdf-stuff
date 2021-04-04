"""
Extract the text from a PDF.

There is not an agreed upon method for doing this in every case, so multiple
backends (PyMuPDF and `pdfplumber`) are available; the results might be slightly
different depending on which was used.
"""
import argparse
import logging
import sys
from pathlib import Path
import fitz
import pdfplumber


try:
    import logzero

    logger = logzero.setup_logger(__name__)
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)


def main(argv=None):
    """Parse arguments and run the script."""

    # Create parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        type=Path,
        help="Path to input PDF file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w"),
        default="-",
        help=("Path to output file. If unspecified, uses stdout."),
    )
    parser.add_argument(
        "--backend",
        choices={"pdfplumber", "pymupdf", "fitz"},
        type=str.lower,
        default="pymupdf",
        help="Backend to use for extracting text. Defaults to PyMuPDF.",
    )

    # Set logging verbosity
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--verbose",
        "-v",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="Turn on debug logging.",
    )
    verbosity.add_argument(
        "-q",
        "--quiet",
        dest="verbose",
        action="store_const",
        const=logging.ERROR,
        help="Turn off debug logging except for reporting errors.",
    )
    args = parser.parse_args(argv)

    # Set logging levels
    logger.setLevel(args.verbose)

    # Adjust logging levels for pdfminer/pdfplumber as they can be quite verbose
    logging.getLogger("pdfplumber").setLevel(logging.WARNING)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)

    # Log input arguments
    logger.debug(f"args: {vars(args)}")

    # Run the script
    if args.backend == "pdfplumber":
        lines = get_pdf_lines_plumber(args.input)
    elif args.backend in {"fitz", "pymupdf"}:
        lines = get_pdf_lines_fitz(args.input)
    else:
        raise ValueError(f"No backend available for: {args.backend}")

    # Join the lines together
    text = "\n".join(lines)

    # Write the result to the output
    with args.output as f:
        f.write(text)
        f.write("\n")


def get_pdf_lines_plumber(pdf_path: Path) -> list[str]:
    """Convert a PDF to text using pdfplumber, return a list of text lines."""
    logger.debug(f"Extracting text lines from: {pdf_path} with pdfplumber")
    with pdfplumber.open(pdf_path) as pdf:
        # Create empty list where I'll be storing the lines
        lines = []

        # Iterate over the pages in the PDF
        for ix, page in enumerate(pdf.pages):
            logger.info(f"Extracting from page: {ix:d}")

            # Get the text from the page
            text = page.extract_text()

            # Separate the block of text into distinct lines
            page_lines = text.splitlines()

            # Add the lines to the list
            lines.extend(page_lines)

    return lines


def get_pdf_lines_fitz(pdf_path: Path) -> list[str]:
    """Convert a PDF to text using pdfplumber, return a list of text lines."""
    logger.debug(f"Extracting text lines from: {pdf_path} with PyMuPDF")
    with fitz.open(pdf_path) as doc:
        # Create empty list where I'll be storing the lines
        lines = []
        for ix, page in enumerate(doc):
            logger.info(f"Extracting from page: {ix:d}")

            # Get the text from the page
            text = page.get_text("text")

            # Separate the block of text into distinct lines
            page_lines = text.splitlines()

            # Add the lines to the list
            lines.extend(page_lines)

    return lines


if __name__ == "__main__":
    main()
