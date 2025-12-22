# ====================================================================================================
# C10_pdf_utils.py
# ----------------------------------------------------------------------------------------------------
# Provides shared PDF reading, manipulation, and extraction utilities for the project.
#
# Purpose:
#   - Centralise reusable functions for PDF text extraction, rotation, merging, and splitting.
#   - Support consistent PDF processing across all invoice providers.
#   - Provide table extraction helpers using pdfplumber for structured data.
#   - Enable validation of PDF files before processing.
#
# Usage:
#   from core.C10_pdf_utils import *
#
#   text = extract_pdf_text("invoice.pdf")
#   value = extract_field(text, r"Invoice No\.?\s*(\S+)")
#   rotated = rotate_pdf("sideways.pdf", 270)
#
#   # Or via class:
#   from core.C10_pdf_utils import PDFUtils
#   text = PDFUtils.extract_pdf_text("invoice.pdf")
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2026-01-01
# Project:      PyBaseEnv
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external and standard-library packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external (and commonly-used standard-library) packages must be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# This module must not import any GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
# PyPDF2 components needed for PDF manipulation (PyPDF2 module imported via C00)
from PyPDF2 import PdfReader, PdfWriter


# ====================================================================================================
# 3. MODULE IMPLEMENTATION (CLASSES / FUNCTIONS)
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Define implementation elements that are internal to this module, such as helper functions and
#   classes. These items are not intended for external reuse unless explicitly promoted to the
#   public API (Section 98).
#
# Rules:
#   - Items here are local to this script and support its specific purpose.
#   - Do not implement reusable utilities here; move those into shared implementation modules.
#   - Do not implement cross-project abstractions here; elevate those to Core modules.
#   - No execution or side-effects in this section.
# ====================================================================================================

# --- Class-Based PDF Utilities -----------------------------------------------------------------------
class PDFUtils:
    """
    Description:
        Namespace-style container for shared PDF reading, manipulation, and
        extraction helpers used throughout the project.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - All methods are implemented as @staticmethod, making this class a
          pure namespace with no instance state.
        - Methods are designed to be side-effect free apart from logging.
        - Uses PyPDF2 for PDF manipulation and pdfplumber for text/table extraction.
    """

    # --- Text Extraction -----------------------------------------------------------------------------

    @staticmethod
    def extract_pdf_text(pdf_path_or_stream: str | Path | BytesIO) -> str:
        """
        Description:
            Extracts all text content from a PDF file or in-memory stream
            using pdfplumber for accurate text extraction.

        Args:
            pdf_path_or_stream (str | Path | BytesIO): Path to the PDF file
                or a BytesIO stream containing PDF data.

        Returns:
            str: Concatenated text from all pages, separated by newlines.

        Raises:
            None: Errors are logged and an empty string is returned.

        Notes:
            - Uses pdfplumber which provides better text extraction than PyPDF2
              for most invoice formats.
            - Each page's text is joined with double newlines for clarity.
        """
        try:
            with pdfplumber.open(pdf_path_or_stream) as pdf:
                all_text = []
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    all_text.append(page_text)
                result = "\n\n".join(all_text)
                logger.debug("Extracted %d characters from PDF.", len(result))
                return result
        except Exception as exc:
            log_exception(exc, logger, "extract_pdf_text")
            return ""

    @staticmethod
    def extract_pdf_text_by_page(pdf_path: str | Path, page_num: int) -> str:
        """
        Description:
            Extracts text from a specific page of a PDF file.

        Args:
            pdf_path (str | Path): Path to the PDF file.
            page_num (int): Zero-based page index to extract.

        Returns:
            str: Text content of the specified page, or empty string if
                the page does not exist or an error occurs.

        Raises:
            None: Errors are logged and an empty string is returned.

        Notes:
            - Page numbering is zero-based (first page is 0).
            - Returns empty string if page_num is out of range.
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < 0 or page_num >= len(pdf.pages):
                    logger.warning("Page %d out of range (0-%d).", page_num, len(pdf.pages) - 1)
                    return ""
                page_text = pdf.pages[page_num].extract_text() or ""
                logger.debug("Extracted %d characters from page %d.", len(page_text), page_num)
                return page_text
        except Exception as exc:
            log_exception(exc, logger, f"extract_pdf_text_by_page(page={page_num})")
            return ""

    @staticmethod
    def get_pdf_page_count(pdf_path: str | Path) -> int:
        """
        Description:
            Returns the number of pages in a PDF file.

        Args:
            pdf_path (str | Path): Path to the PDF file.

        Returns:
            int: Number of pages in the PDF, or 0 if an error occurs.

        Raises:
            None: Errors are logged and 0 is returned.

        Notes:
            - Uses PyPDF2 PdfReader for efficiency.
        """
        try:
            reader = PdfReader(str(pdf_path))
            count = len(reader.pages)
            logger.debug("PDF has %d pages: %s", count, pdf_path)
            return count
        except Exception as exc:
            log_exception(exc, logger, "get_pdf_page_count")
            return 0

    # --- Field Extraction (Regex) --------------------------------------------------------------------

    @staticmethod
    def extract_field(
        text: str,
        pattern: str,
        flags: int = re.IGNORECASE,
        group: int = 1
    ) -> str | None:
        """
        Description:
            Extracts a value from text using a regular expression pattern,
            returning a specific capturing group.

        Args:
            text (str): The text to search.
            pattern (str): Regular expression pattern with at least one
                capturing group.
            flags (int): Regex flags to apply. Defaults to re.IGNORECASE.
            group (int): Capturing group index to return. Defaults to 1
                (first capturing group).

        Returns:
            str | None: The matched group value if found, otherwise None.

        Raises:
            None: No exceptions are raised; returns None on no match.

        Notes:
            - Designed for extracting single values like invoice numbers,
              dates, or reference codes from invoice text.
            - Use extract_all_fields() if multiple matches are expected.
        """
        match = re.search(pattern, text, flags)
        if match:
            try:
                result = match.group(group)
                logger.debug("Extracted field: pattern='%s' -> '%s'", pattern, result)
                return result
            except IndexError:
                logger.warning("Group %d not found in pattern '%s'.", group, pattern)
                return None
        logger.debug("No match found for pattern: '%s'", pattern)
        return None

    @staticmethod
    def extract_all_fields(
        text: str,
        pattern: str,
        flags: int = re.IGNORECASE,
        group: int = 1
    ) -> list[str]:
        """
        Description:
            Extracts all occurrences of a pattern from text, returning
            a list of matched values.

        Args:
            text (str): The text to search.
            pattern (str): Regular expression pattern with at least one
                capturing group.
            flags (int): Regex flags to apply. Defaults to re.IGNORECASE.
            group (int): Capturing group index to extract from each match.
                Defaults to 1.

        Returns:
            list[str]: List of matched values. Empty list if no matches.

        Raises:
            None: Returns empty list on errors.

        Notes:
            - Useful for extracting multiple line items or repeated values.
        """
        try:
            matches = re.finditer(pattern, text, flags)
            results = []
            for match in matches:
                try:
                    results.append(match.group(group))
                except IndexError:
                    continue
            logger.debug("Extracted %d matches for pattern: '%s'", len(results), pattern)
            return results
        except Exception as exc:
            log_exception(exc, logger, "extract_all_fields")
            return []

    # --- PDF Manipulation ----------------------------------------------------------------------------

    @staticmethod
    def rotate_pdf(
        pdf_path: str | Path,
        angle: int = 270
    ) -> BytesIO:
        """
        Description:
            Rotates all pages in a PDF by the specified angle and returns
            the result as an in-memory BytesIO stream.

        Args:
            pdf_path (str | Path): Path to the input PDF file.
            angle (int): Rotation angle in degrees (90, 180, 270).
                Defaults to 270.

        Returns:
            BytesIO: In-memory stream containing the rotated PDF.

        Raises:
            ValueError: If the PDF cannot be read or rotated.

        Notes:
            - Common use case: rotating sideways-scanned invoices.
            - The returned BytesIO can be passed directly to extract_pdf_text().
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            for page in reader.pages:
                page.rotate(angle)
                writer.add_page(page)

            output_stream = BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)

            logger.info("Rotated PDF by %d degrees: %s", angle, pdf_path)
            return output_stream

        except Exception as exc:
            log_exception(exc, logger, f"rotate_pdf(angle={angle})")
            raise ValueError(f"Failed to rotate PDF: {exc}") from exc

    @staticmethod
    def merge_pdfs(
        pdf_paths: list[str | Path],
        output_path: str | Path | None = None
    ) -> BytesIO:
        """
        Description:
            Merges multiple PDF files into a single PDF.

        Args:
            pdf_paths (list[str | Path]): List of paths to PDF files to merge,
                in the order they should appear.
            output_path (str | Path | None): Optional path to save the merged
                PDF. If None, only returns the BytesIO stream.

        Returns:
            BytesIO: In-memory stream containing the merged PDF.

        Raises:
            ValueError: If no valid PDFs are provided or merge fails.

        Notes:
            - Common use case: prepending a cover sheet to an invoice.
            - PDFs are merged in the order provided.
        """
        try:
            writer = PdfWriter()

            for pdf_path in pdf_paths:
                reader = PdfReader(str(pdf_path))
                for page in reader.pages:
                    writer.add_page(page)

            output_stream = BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)

            if output_path:
                with open(output_path, "wb") as f:
                    f.write(output_stream.getvalue())
                logger.info("Merged %d PDFs to: %s", len(pdf_paths), output_path)
                output_stream.seek(0)

            logger.debug("Merged %d PDFs into stream.", len(pdf_paths))
            return output_stream

        except Exception as exc:
            log_exception(exc, logger, "merge_pdfs")
            raise ValueError(f"Failed to merge PDFs: {exc}") from exc

    @staticmethod
    def extract_pages(
        pdf_path: str | Path,
        page_numbers: list[int],
        output_path: str | Path | None = None
    ) -> BytesIO:
        """
        Description:
            Extracts specific pages from a PDF and returns them as a new PDF.

        Args:
            pdf_path (str | Path): Path to the source PDF file.
            page_numbers (list[int]): Zero-based indices of pages to extract.
            output_path (str | Path | None): Optional path to save the
                extracted PDF.

        Returns:
            BytesIO: In-memory stream containing the extracted pages.

        Raises:
            ValueError: If extraction fails.

        Notes:
            - Page numbering is zero-based (first page is 0).
            - Pages are extracted in the order specified.
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            for page_num in page_numbers:
                if 0 <= page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
                else:
                    logger.warning("Page %d out of range, skipping.", page_num)

            output_stream = BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)

            if output_path:
                with open(output_path, "wb") as f:
                    f.write(output_stream.getvalue())
                logger.info("Extracted pages %s to: %s", page_numbers, output_path)
                output_stream.seek(0)

            return output_stream

        except Exception as exc:
            log_exception(exc, logger, "extract_pages")
            raise ValueError(f"Failed to extract pages: {exc}") from exc

    @staticmethod
    def extract_pages_matching(
        pdf_path: str | Path,
        search_pattern: str,
        flags: int = re.IGNORECASE
    ) -> BytesIO | None:
        """
        Description:
            Searches through all pages in a PDF and extracts those containing
            text matching the specified pattern.

        Args:
            pdf_path (str | Path): Path to the PDF file.
            search_pattern (str): Regex pattern to search for in page text.
            flags (int): Regex flags. Defaults to re.IGNORECASE.

        Returns:
            BytesIO | None: In-memory stream containing matching pages,
                or None if no pages match.

        Raises:
            None: Returns None on errors.

        Notes:
            - Useful for extracting specific sections like financial summaries.
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            for page in reader.pages:
                page_text = page.extract_text() or ""
                if re.search(search_pattern, page_text, flags):
                    writer.add_page(page)

            if len(writer.pages) == 0:
                logger.debug("No pages matched pattern: '%s'", search_pattern)
                return None

            output_stream = BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)

            logger.info("Extracted %d pages matching '%s'.", len(writer.pages), search_pattern)
            return output_stream

        except Exception as exc:
            log_exception(exc, logger, "extract_pages_matching")
            return None

    @staticmethod
    def remove_pages_containing(
        pdf_path: str | Path,
        search_text: str,
        output_path: str | Path | None = None
    ) -> BytesIO:
        """
        Description:
            Removes pages from a PDF that contain the specified text.

        Args:
            pdf_path (str | Path): Path to the source PDF file.
            search_text (str): Text to search for (case-insensitive).
                Pages containing this text will be removed.
            output_path (str | Path | None): Optional path to save the
                filtered PDF.

        Returns:
            BytesIO: In-memory stream containing the PDF with matching
                pages removed.

        Raises:
            ValueError: If filtering fails.

        Notes:
            - Useful for removing existing cover sheets before adding new ones.
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()
            removed_count = 0

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if search_text.lower() in page_text.lower():
                    logger.debug("Removing page %d (contains '%s').", i, search_text)
                    removed_count += 1
                else:
                    writer.add_page(page)

            output_stream = BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)

            if output_path:
                with open(output_path, "wb") as f:
                    f.write(output_stream.getvalue())
                output_stream.seek(0)

            logger.info("Removed %d pages containing '%s'.", removed_count, search_text)
            return output_stream

        except Exception as exc:
            log_exception(exc, logger, "remove_pages_containing")
            raise ValueError(f"Failed to remove pages: {exc}") from exc

    # --- Table Extraction ----------------------------------------------------------------------------

    @staticmethod
    def extract_tables(
        pdf_path: str | Path,
        page_num: int | None = None
    ) -> list[list[list[str]]]:
        """
        Description:
            Extracts tables from a PDF using pdfplumber's table detection.

        Args:
            pdf_path (str | Path): Path to the PDF file.
            page_num (int | None): Specific page to extract from (zero-based).
                If None, extracts from all pages.

        Returns:
            list[list[list[str]]]: Nested list structure where:
                - Outer list: tables found
                - Middle list: rows in each table
                - Inner list: cells in each row

        Raises:
            None: Returns empty list on errors.

        Notes:
            - pdfplumber is particularly effective at detecting bordered tables.
            - Returns empty list if no tables are found.
        """
        try:
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                pages_to_process = [pdf.pages[page_num]] if page_num is not None else pdf.pages

                for page in pages_to_process:
                    page_tables = page.extract_tables() or []
                    tables.extend(page_tables)

            logger.debug("Extracted %d tables from PDF.", len(tables))
            return tables

        except Exception as exc:
            log_exception(exc, logger, "extract_tables")
            return []

    @staticmethod
    def extract_tables_to_dataframe(
        pdf_path: str | Path,
        page_num: int | None = None
    ) -> list[pd.DataFrame]:
        """
        Description:
            Extracts tables from a PDF and converts them to pandas DataFrames.

        Args:
            pdf_path (str | Path): Path to the PDF file.
            page_num (int | None): Specific page to extract from (zero-based).
                If None, extracts from all pages.

        Returns:
            list[pd.DataFrame]: List of DataFrames, one per table found.
                First row is used as column headers.

        Raises:
            None: Returns empty list on errors.

        Notes:
            - Assumes the first row of each table contains headers.
            - Empty tables are skipped.
        """
        try:
            tables = PDFUtils.extract_tables(pdf_path, page_num)
            dataframes = []

            for table in tables:
                if not table or len(table) < 2:
                    continue

                headers = table[0]
                rows = table[1:]
                df = pd.DataFrame(rows, columns=headers)
                dataframes.append(df)

            logger.debug("Converted %d tables to DataFrames.", len(dataframes))
            return dataframes

        except Exception as exc:
            log_exception(exc, logger, "extract_tables_to_dataframe")
            return []

    # --- Validation ----------------------------------------------------------------------------------

    @staticmethod
    def is_valid_pdf(file_path: str | Path) -> bool:
        """
        Description:
            Checks whether a file is a valid, readable PDF.

        Args:
            file_path (str | Path): Path to the file to validate.

        Returns:
            bool: True if the file is a valid PDF, False otherwise.

        Raises:
            None: All errors result in False being returned.

        Notes:
            - Checks both file existence and PDF readability.
            - Useful for validation before processing.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning("File does not exist: %s", file_path)
                return False

            if not path.suffix.lower() == ".pdf":
                logger.warning("File does not have .pdf extension: %s", file_path)
                return False

            # Try to read the PDF
            reader = PdfReader(str(file_path))
            _ = len(reader.pages)  # Access pages to verify readability

            logger.debug("Valid PDF: %s", file_path)
            return True

        except Exception as exc:
            logger.warning("Invalid PDF (%s): %s", file_path, exc)
            return False


# --- Function Facade (Backwards Compatible API) ------------------------------------------------------
def extract_pdf_text(pdf_path_or_stream: str | Path | BytesIO) -> str:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_pdf_text() to
        extract all text from a PDF.

    Args:
        pdf_path_or_stream (str | Path | BytesIO): Path or stream to extract from.

    Returns:
        str: Extracted text content.

    Raises:
        None.

    Notes:
        - Provided for backwards compatibility with function-based APIs.
    """
    return PDFUtils.extract_pdf_text(pdf_path_or_stream)


def extract_pdf_text_by_page(pdf_path: str | Path, page_num: int) -> str:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_pdf_text_by_page().

    Args:
        pdf_path (str | Path): Path to the PDF file.
        page_num (int): Zero-based page index.

    Returns:
        str: Text from the specified page.

    Raises:
        None.
    """
    return PDFUtils.extract_pdf_text_by_page(pdf_path, page_num)


def get_pdf_page_count(pdf_path: str | Path) -> int:
    """
    Description:
        Facade function that delegates to PDFUtils.get_pdf_page_count().

    Args:
        pdf_path (str | Path): Path to the PDF file.

    Returns:
        int: Number of pages in the PDF.

    Raises:
        None.
    """
    return PDFUtils.get_pdf_page_count(pdf_path)


def extract_field(
    text: str,
    pattern: str,
    flags: int = re.IGNORECASE,
    group: int = 1
) -> str | None:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_field().

    Args:
        text (str): Text to search.
        pattern (str): Regex pattern with capturing group.
        flags (int): Regex flags. Defaults to re.IGNORECASE.
        group (int): Capturing group to return. Defaults to 1.

    Returns:
        str | None: Matched value or None.

    Raises:
        None.
    """
    return PDFUtils.extract_field(text, pattern, flags, group)


def extract_all_fields(
    text: str,
    pattern: str,
    flags: int = re.IGNORECASE,
    group: int = 1
) -> list[str]:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_all_fields().

    Args:
        text (str): Text to search.
        pattern (str): Regex pattern with capturing group.
        flags (int): Regex flags. Defaults to re.IGNORECASE.
        group (int): Capturing group to extract. Defaults to 1.

    Returns:
        list[str]: List of matched values.

    Raises:
        None.
    """
    return PDFUtils.extract_all_fields(text, pattern, flags, group)


def rotate_pdf(pdf_path: str | Path, angle: int = 270) -> BytesIO:
    """
    Description:
        Facade function that delegates to PDFUtils.rotate_pdf().

    Args:
        pdf_path (str | Path): Path to the PDF file.
        angle (int): Rotation angle in degrees. Defaults to 270.

    Returns:
        BytesIO: In-memory stream with rotated PDF.

    Raises:
        ValueError: If rotation fails.
    """
    return PDFUtils.rotate_pdf(pdf_path, angle)


def merge_pdfs(
    pdf_paths: list[str | Path],
    output_path: str | Path | None = None
) -> BytesIO:
    """
    Description:
        Facade function that delegates to PDFUtils.merge_pdfs().

    Args:
        pdf_paths (list[str | Path]): Paths to PDFs to merge.
        output_path (str | Path | None): Optional output file path.

    Returns:
        BytesIO: In-memory stream with merged PDF.

    Raises:
        ValueError: If merge fails.
    """
    return PDFUtils.merge_pdfs(pdf_paths, output_path)


def extract_pages(
    pdf_path: str | Path,
    page_numbers: list[int],
    output_path: str | Path | None = None
) -> BytesIO:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_pages().

    Args:
        pdf_path (str | Path): Path to the source PDF.
        page_numbers (list[int]): Zero-based page indices to extract.
        output_path (str | Path | None): Optional output file path.

    Returns:
        BytesIO: In-memory stream with extracted pages.

    Raises:
        ValueError: If extraction fails.
    """
    return PDFUtils.extract_pages(pdf_path, page_numbers, output_path)


def extract_pages_matching(
    pdf_path: str | Path,
    search_pattern: str,
    flags: int = re.IGNORECASE
) -> BytesIO | None:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_pages_matching().

    Args:
        pdf_path (str | Path): Path to the PDF file.
        search_pattern (str): Regex pattern to match.
        flags (int): Regex flags. Defaults to re.IGNORECASE.

    Returns:
        BytesIO | None: Stream with matching pages, or None if no matches.

    Raises:
        None.
    """
    return PDFUtils.extract_pages_matching(pdf_path, search_pattern, flags)


def remove_pages_containing(
    pdf_path: str | Path,
    search_text: str,
    output_path: str | Path | None = None
) -> BytesIO:
    """
    Description:
        Facade function that delegates to PDFUtils.remove_pages_containing().

    Args:
        pdf_path (str | Path): Path to the source PDF.
        search_text (str): Text to search for in pages to remove.
        output_path (str | Path | None): Optional output file path.

    Returns:
        BytesIO: In-memory stream with filtered PDF.

    Raises:
        ValueError: If filtering fails.
    """
    return PDFUtils.remove_pages_containing(pdf_path, search_text, output_path)


def extract_tables(
    pdf_path: str | Path,
    page_num: int | None = None
) -> list[list[list[str]]]:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_tables().

    Args:
        pdf_path (str | Path): Path to the PDF file.
        page_num (int | None): Specific page, or None for all pages.

    Returns:
        list[list[list[str]]]: Nested list of tables/rows/cells.

    Raises:
        None.
    """
    return PDFUtils.extract_tables(pdf_path, page_num)


def extract_tables_to_dataframe(
    pdf_path: str | Path,
    page_num: int | None = None
) -> list[pd.DataFrame]:
    """
    Description:
        Facade function that delegates to PDFUtils.extract_tables_to_dataframe().

    Args:
        pdf_path (str | Path): Path to the PDF file.
        page_num (int | None): Specific page, or None for all pages.

    Returns:
        list[pd.DataFrame]: List of DataFrames, one per table.

    Raises:
        None.
    """
    return PDFUtils.extract_tables_to_dataframe(pdf_path, page_num)


def is_valid_pdf(file_path: str | Path) -> bool:
    """
    Description:
        Facade function that delegates to PDFUtils.is_valid_pdf().

    Args:
        file_path (str | Path): Path to the file to validate.

    Returns:
        bool: True if valid PDF, False otherwise.

    Raises:
        None.
    """
    return PDFUtils.is_valid_pdf(file_path)


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Declare a concise, intentional list of functions or objects that this module exposes for external
#   use. This section acts as a "public interface" and prevents accidental consumption of internal
#   helpers or implementation details.
#
# Rules:
#   - Only list functions or objects that are explicitly intended to be imported by other modules.
#   - Do NOT expose one-off helpers or short-lived utilities; those must remain internal to this file.
#   - If more than a small number of items belong here, consider whether they should be elevated to a
#     shared implementation module or to the Core library (C-modules).
#   - This section must contain no executable code and no import statements.
#   - For Python enforcement, "__all__" may be declared here, but this is optional.
#
# Benefit:
#   This provides a predictable "contract location" across the codebase, improving navigability,
#   reducing implicit coupling, and discouraging scripts from evolving into accidental libraries.
# ----------------------------------------------------------------------------------------------------

__all__ = [
    # --- Class-Based API ---
    "PDFUtils",
    # --- Text Extraction ---
    "extract_pdf_text",
    "extract_pdf_text_by_page",
    "get_pdf_page_count",
    # --- Field Extraction (Regex) ---
    "extract_field",
    "extract_all_fields",
    # --- PDF Manipulation ---
    "rotate_pdf",
    "merge_pdfs",
    "extract_pages",
    "extract_pages_matching",
    "remove_pages_containing",
    # --- Table Extraction ---
    "extract_tables",
    "extract_tables_to_dataframe",
    # --- Validation ---
    "is_valid_pdf",
]


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
# This section is the ONLY location where runtime execution should occur.
# Rules:
#   - No side-effects at import time.
#   - Initialisation (e.g., logging) must be triggered here.
#   - Any test or demonstration logic should be gated behind __main__.
#
# This ensures safe importing from other modules and prevents hidden execution paths.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Self-test entry point for C10_pdf_utils.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates regex field extraction with sample invoice text.
    """
    logger.info("=" * 60)
    logger.info("C10_pdf_utils self-test started.")
    logger.info("=" * 60)

    # Test extract_field with sample text
    sample_text = """
    INVOICE NO. 9607633
    ACCOUNT NO. 28783
    TAX POINT DATE 21/11/2025
    OWN REF.NO. GUK4781022
    """

    logger.info("Testing extract_field()...")
    invoice_no = extract_field(sample_text, r"INVOICE\s*NO\.?\s*(\S+)")
    logger.info("Invoice No: %s", invoice_no)

    account_no = extract_field(sample_text, r"ACCOUNT\s*NO\.?\s*(\S+)")
    logger.info("Account No: %s", account_no)

    po_ref = extract_field(sample_text, r"OWN\s*REF\.?\s*NO\.?\s*(\S+)")
    logger.info("PO Reference: %s", po_ref)

    date_val = extract_field(sample_text, r"TAX\s+POINT\s+DATE\s*(\S+)")
    logger.info("Date: %s", date_val)

    # Test extract_all_fields
    logger.info("Testing extract_all_fields()...")
    all_numbers = extract_all_fields(sample_text, r"(\d+)")
    logger.info("All numbers found: %s", all_numbers)

    logger.info("=" * 60)
    logger.info("C10_pdf_utils self-test completed successfully.")
    logger.info("=" * 60)


if __name__ == "__main__":
    init_logging()
    main()