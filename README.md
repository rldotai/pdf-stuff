# pdf-stuff

Scripts for working with PDFs-- comparing PDFs, extracting glyphs, that sort of thing.

Provides:

- `pdfdiff.py`
    - A script for identifying differences in PDFs by comparing them page by page as images.
- `pdf2text.py`
    - A script for extracting the text from a PDF.

## Installation

I haven't yet uploaded this to PyPI, but you can still clone the repo and install it thus:

```bash
# Install like a regular Python package
pip install .

# For development/hacking
pip install --editable .
```

You can also just run the scripts in a standalone fashion, i.e. without installing the package:

```bash
# Standalone
python pdf_stuff/pdfdiff.py one.pdf two.pdf --output="one-vs-two.pdf"
```

# Usage

## pdfdiff.py

Compare two PDFs to look for differences.

```bash
# Compare two PDFs
pdfdiff.py one.pdf another.pdf

# See help message for more options
pdfdiff.py --help
```

### Example

I created a few PDFs using [my `makedown` project](https://github.com/rldotai/makedown), which is basically a Makefile that wraps `pandoc`.
The default is [`example/makedown-1.pdf`](example/makedown-1.pdf) and the one with a bit of customization is [`example/makedown-2.pdf`](example/makedown-2.pdf).

We can see the difference between my slightly customized template and the default by comparing them via:

```bash
pdfdiff.py example/makedown-1.pdf example/makedown-2.pdf
```

The results are mostly identical, except for the lists, which use a consistent bullet type and less spacing when generated via my template.

A | B | Diff
:--:|:---:|:---:
![PDF difference](resources/pandoc-list.png) | ![PDF difference](resources/cool-list.png) | ![PDF difference](resources/diff-list.png)


## pdf2text.py

Extract the text from a PDF.

Note that this does not (currently) perform any OCR nor attempt to handle any weird glyph shenanigans; it is essentially equivalent to copy-and-pasting text from a PDF that you've opened up in a PDF viewer.

```bash
# Extract the text from `file.pdf` and save as `file.pdf.txt`
pdf2text.py file.pdf --output=file.pdf.txt

# If output unspecified, it will print to stdout
pdf2text.py file.pdf

# Use the `pdfplumber` backend
pdf2text.py file.pdf --backend=pdfplumber
```

## pdfmeta.py

Print metadata from the PDF.
May eventually support modifying the metadata as well.

```bash
# Default, with date parsing and colored output
pdfmeta.py file.pdf

# Verbatim, no colored output
pdfmeta.py --verbatim file.pdf
```

# TODO

Move the following from scattered notebooks into this repo:

- [ ] Metadata extraction \& pretty-printing
- [ ] Image extraction
- [ ] Text extraction
- [ ] OCR
- [ ] HTML image w/ text overlay

## Improvements

- [ ] More options for `pdfdiff.py` and `pdf2txt.py`
    - Handle page ranges
- [ ] Options specific to `pdfdiff.py`
    - Omit pages that are identical
    - Handle pages of different sizes but same aspect ratio
    - Implement more diff algorithms
- [ ] Add debug logging to `pdfdiff.py`
- [ ] Image (rather than PDF) output for `pdfdiff.py`
- [ ] Allow for custom page separator in `pdf2txt.py`?
- [ ] `pdfmeta.py`
    - Allow setting metadata
    - Are there additional things that count as metadata we should look for?

