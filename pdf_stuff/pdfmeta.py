"""
Pretty-print the metadata from the PDF.

TODO:
    - allow setting metadata and re-saving
        - Specify in-place vs to a new file.
    - subcommands for printing verus setting metadata
"""
import argparse
import logging
import sys
from pathlib import Path
import fitz
import pendulum
import rich


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
    output_opt = parser.add_mutually_exclusive_group()
    output_opt.add_argument(
        "--output",
        "-o",
        type=Path,
        help=("Path to output file"),
    )
    output_opt.add_argument(
        "--inplace",
        action="store_true",
        help=("Make changes in place"),
    )
    parser.add_argument(
        "--verbatim",
        action="store_true",
        help=("Print the raw metadata without date parsing or colorization."),
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

    # Set output
    if args.inplace:
        output = args.input
    elif args.output:
        output = args.output

    # Run the script
    doc = fitz.open(args.input)

    if not args.verbatim:
        pprint_metadata(doc)
    else:
        print(doc.metadata)


def parse_dt(string, timezone=pendulum.local_timezone()):
    """Parse a string with good default options."""
    # Handle timezones given as strings, e.g. "UTC" or "Europe/Paris"
    if isinstance(timezone, str):
        timezone = pendulum.timezone(timezone)
    # Try the defaults available through pendulum/dateutil
    try:
        return pendulum.parse(
            string,
            day_first=False,
            year_first=True,
            tz=timezone,
            strict=False,
        )
    except Exception as e:
        logger.debug(f"{e}")
        logger.debug(
            f"Default datetime parser failed for: {string}, trying alternatives..."
        )

    # Try some PDF-specific alternatives
    try:
        # For strings of the form: 20210329190207-05'00' -- with timezone
        new_string = string.replace(r"'", r"")
        # dt = pendulum.from_format(new_string, r"YYYYMMDDHHmmssZZ")
        dt = pendulum.parse(
            new_string,
            day_first=False,
            year_first=True,
            tz=timezone,
            strict=False,
        )
        return timezone.convert(dt)
    except Exception as e:
        logger.debug(f"{e}")
        logger.warning(f"Unable to parse: {string}")
        return string


def pprint_metadata(doc: fitz.Document):
    """Pretty-print a Fitz document's metadata."""
    # Human-readable datetimes
    ret = {**doc.metadata}
    try:
        if not "creationDate" in ret:
            ret["creationDate"] = ("",)
        elif not ret["creationDate"].strip():  # handle blank
            ret["creationDate"] = ""
        elif ret["creationDate"].startswith(r"D:"):
            ret["creationDate"] = parse_dt(ret["creationDate"][2:]).to_rfc2822_string()
        else:
            ret["creationDate"] = parse_dt(ret["creationDate"]).to_rfc2822_string()
    except Exception as e:
        logger.warning("Unable to parse `creationDate`, using default")

    try:
        if not "modDate" in ret:
            ret["modDate"] = ""
        elif not ret["modDate"].strip():  # handle blank
            ret["modDate"] = ""
        elif ret["modDate"].startswith(r"D:"):
            ret["modDate"] = parse_dt(ret["modDate"][2:]).to_rfc2822_string()
        else:
            ret["modDate"] = parse_dt(ret["modDate"]).to_rfc2822_string()
    except Exception as e:
        logger.warning("Unable to parse `modDate`, using default")

    # Pretty print
    rich.print(ret)


if __name__ == "__main__":
    main()
