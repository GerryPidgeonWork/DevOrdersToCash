# ====================================================================================================
# C19_google_drive_integration.py
# ----------------------------------------------------------------------------------------------------
# Provides Google Drive integration via both local mapped drives and the Google Drive API.
#
# Purpose:
#   - Detect Google Drive App installation and list configured accounts.
#   - Extract drive roots from paths (Windows drive letters, macOS mount points).
#   - Authenticate with Google Drive API using OAuth 2.0.
#   - Upload, download, search, and list files on Google Drive.
#
# Usage:
#   from core.C19_google_drive_integration import (
#       # Local drive detection
#       is_google_drive_installed,
#       get_google_drive_accounts,
#       extract_drive_root,
#       # API operations
#       get_drive_service,
#       find_folder_id,
#       find_file_id,
#       upload_file,
#       upload_dataframe_as_csv,
#       download_file,
#   )
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
from core.C02_set_file_paths import (
    PROJECT_ROOT,
    GDRIVE_CREDENTIALS_FILE,
    GDRIVE_TOKEN_FILE,
)
from core.C03_system_processes import detect_os, user_download_folder


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

# --- Constants ---------------------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/drive"]


# --- Local Drive Detection (Google Drive App) -------------------------------------------------------
# Functions to detect Google Drive App installation, list configured accounts, and extract drive roots.
#
# Windows Detection Strategy:
#   1. Scan all drive letters for Google Drive indicators
#   2. Use wmic to get volume label which contains the email address
#   3. Check for ".shortcut-targets-by-id" folder as backup indicator
#
# macOS Detection Strategy:
#   - Scan /Volumes for Google Drive mount points

def _get_drivefs_path() -> Path | None:
    """
    Description:
        Get the path to Google Drive's DriveFS installation folder based on the current OS.

    Args:
        None.

    Returns:
        Path | None: Path to the DriveFS folder, or None if OS is unsupported.

    Raises:
        None.

    Notes:
        - Windows: C:/Program Files/Google/Drive File Stream
        - macOS: /Applications/Google Drive.app
    """
    current_os = detect_os()

    if current_os == "Windows":
        return Path(r"C:\Program Files\Google\Drive File Stream")
    elif current_os == "macOS":
        return Path("/Applications/Google Drive.app")

    logger.warning("Unsupported OS for Google Drive detection: %s", current_os)
    return None


def is_google_drive_installed() -> bool:
    """
    Description:
        Check if Google Drive App is installed.

    Args:
        None.

    Returns:
        bool: True if Google Drive App is installed, False otherwise.

    Raises:
        None.

    Notes:
        - On Windows, checks for the installation folder.
        - On macOS, checks for the application bundle.
    """
    drivefs_path = _get_drivefs_path()
    if drivefs_path and drivefs_path.exists():
        logger.info("Google Drive App detected: %s", drivefs_path)
        return True

    # Fallback: check if any Google Drive is actually mounted
    current_os = detect_os()
    if current_os == "Windows":
        # Check for any drive with the Google Drive indicator folder
        import string
        for letter in string.ascii_uppercase:
            indicator = Path(f"{letter}:") / ".shortcut-targets-by-id"
            try:
                if indicator.exists():
                    logger.info("Google Drive App detected via mounted drive: %s:", letter)
                    return True
            except (PermissionError, OSError):
                continue

    logger.info("Google Drive App not detected.")
    return False


def get_google_drive_accounts() -> List[Dict[str, str]]:
    """
    Description:
        Retrieve a list of Google Drive accounts configured in the Google Drive App.
        Each account includes the associated email address and the local mount point (drive root).

    Args:
        None.

    Returns:
        List[Dict[str, str]]: List of dictionaries with keys:
            - "email": The Google account email address.
            - "root": The local drive root (e.g., "H:" on Windows, "/Volumes/GoogleDrive" on macOS).

    Raises:
        None.

    Notes:
        - On Windows, uses wmic to get volume labels which contain email addresses.
        - On macOS, scans /Volumes for Google Drive mount points.
        - Returns empty list if Google Drive is not installed.
    """
    accounts: List[Dict[str, str]] = []
    current_os = detect_os()

    if current_os == "Windows":
        accounts = _get_windows_google_drives()
    elif current_os == "macOS":
        accounts = _get_macos_google_drives()
    else:
        logger.warning("Google Drive detection not supported on %s", current_os)

    # Sort by email for consistent ordering
    accounts.sort(key=lambda x: x["email"].lower())

    logger.info("Found %s Google Drive account(s).", len(accounts))
    return accounts


def _get_windows_google_drives() -> List[Dict[str, str]]:
    """
    Description:
        Detect Google Drive mounts on Windows using wmic to read volume labels.

    Args:
        None.

    Returns:
        List[Dict[str, str]]: List of detected drives with "email" and "root".

    Raises:
        None.

    Notes:
        - Volume labels typically contain the email address (e.g., "gerry@email.com - G")
        - Falls back to checking for ".shortcut-targets-by-id" folder as indicator.
    """
    accounts: List[Dict[str, str]] = []

    import string
    import ctypes

    # Get available drive letters using Windows API
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    except Exception as e:
        logger.warning("Could not enumerate drives: %s", e)
        return accounts

    for letter in string.ascii_uppercase:
        if not (bitmask & 1):
            bitmask >>= 1
            continue
        bitmask >>= 1

        drive_path = f"{letter}:\\"
        drive_root = f"{letter}:"

        try:
            # Check for Google Drive indicator folder
            has_indicator = Path(drive_path) / ".shortcut-targets-by-id"
            is_google_drive = False

            # Get volume label using wmic
            volume_label = _get_volume_label_wmic(drive_root)

            # Check if this is a Google Drive
            if volume_label:
                if "Google Drive" in volume_label or " - G" in volume_label:
                    is_google_drive = True
                elif "@" in volume_label:
                    # Volume label contains an email address
                    is_google_drive = True

            # Fallback: check for indicator folder
            if not is_google_drive:
                try:
                    if has_indicator.exists():
                        is_google_drive = True
                except (PermissionError, OSError):
                    pass

            if is_google_drive:
                # Extract email from volume label
                email = _extract_email_from_volume_label(volume_label)
                accounts.append({
                    "email": email or f"Account on {drive_root}",
                    "root": drive_root
                })
                logger.debug("Found Google Drive: %s -> %s", drive_root, email)

        except Exception as e:
            logger.debug("Error checking drive %s: %s", drive_root, e)
            continue

    return accounts


def _get_volume_label_wmic(drive_root: str) -> str | None:
    """
    Description:
        Get the volume label for a drive using wmic command.

    Args:
        drive_root: Drive letter with colon (e.g., "H:").

    Returns:
        str | None: Volume label, or None if unavailable.

    Raises:
        None.

    Notes:
        - Uses Windows Management Instrumentation Command-line (wmic).
    """
    try:
        cmd = f'wmic logicaldisk where "DeviceID=\'{drive_root}\'" get VolumeName'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            timeout=5
        )

        if result.returncode != 0:
            return None

        # Parse output - skip header line
        lines = result.stdout.strip().splitlines()
        for line in lines:
            line = line.strip()
            if line and "VolumeName" not in line:
                return line

    except subprocess.TimeoutExpired:
        logger.debug("Timeout getting volume label for %s", drive_root)
    except Exception as e:
        logger.debug("Error getting volume label for %s: %s", drive_root, e)

    return None


def _extract_email_from_volume_label(volume_label: str | None) -> str | None:
    """
    Description:
        Extract email address from a Google Drive volume label.

    Args:
        volume_label: The volume label string (e.g., "gerry@email.com - G").

    Returns:
        str | None: Extracted email address, or None if not found.

    Raises:
        None.

    Notes:
        - Google Drive volume labels typically follow pattern "email@domain.com - G"
        - Handles truncated labels and various formats.
    """
    if not volume_label:
        return None

    # Try to extract email using " - " separator
    if " - " in volume_label:
        possible_email = volume_label.split(" - ")[0].strip()
        if "@" in possible_email:
            return possible_email

    # Check if the whole label looks like an email (possibly truncated)
    if "@" in volume_label:
        # Remove trailing dots from truncated labels
        email = volume_label.rstrip(".")
        # If it still looks like an email, return it
        if "@" in email and "." in email.split("@")[-1]:
            return email

    return None


def _get_macos_google_drives() -> List[Dict[str, str]]:
    """
    Description:
        Detect Google Drive mounts on macOS by scanning /Volumes.

    Args:
        None.

    Returns:
        List[Dict[str, str]]: List of detected drives with "email" and "root".

    Raises:
        None.

    Notes:
        - Checks /Volumes for directories containing "Google Drive" or email-like names.
        - Also checks ~/Google Drive as an alternative mount point.
    """
    accounts: List[Dict[str, str]] = []

    # Check /Volumes
    volumes_path = Path("/Volumes")
    if volumes_path.exists():
        for mount in volumes_path.iterdir():
            if not mount.is_dir():
                continue

            is_google_drive = False
            email = None

            # Check if name contains "Google Drive"
            if "google" in mount.name.lower() and "drive" in mount.name.lower():
                is_google_drive = True

            # Check if name looks like an email
            if "@" in mount.name and "." in mount.name:
                is_google_drive = True
                email = mount.name

            # Check for indicator folder
            indicator = mount / ".shortcut-targets-by-id"
            try:
                if indicator.exists():
                    is_google_drive = True
            except (PermissionError, OSError):
                pass

            if is_google_drive:
                accounts.append({
                    "email": email or f"Account at {mount.name}",
                    "root": str(mount)
                })

    # Check ~/Google Drive
    home_gdrive = Path.home() / "Google Drive"
    if home_gdrive.exists():
        # Avoid duplicates
        if not any(acc["root"] == str(home_gdrive) for acc in accounts):
            accounts.append({
                "email": "Default Account",
                "root": str(home_gdrive)
            })

    return accounts


def extract_drive_root(path: Path | str) -> str:
    """
    Description:
        Extract the drive root from a given path.
        On Windows, returns the drive letter (e.g., "H:").
        On macOS/Linux, returns the mount point root (e.g., "/Volumes/GoogleDrive").

    Args:
        path: A file system path (can be deeply nested).

    Returns:
        str: The drive root.

    Raises:
        None.

    Notes:
        - Handles both Path objects and strings.
        - On Windows: "H:/My Drive/Projects/File.xlsx" → "H:"
        - On macOS: "/Volumes/GoogleDrive/My Drive/Projects" → "/Volumes/GoogleDrive"
    """
    path = Path(path) if isinstance(path, str) else path
    current_os = detect_os()

    if current_os == "Windows":
        # Windows: Extract drive letter
        drive = path.drive
        if drive:
            return drive  # Returns "H:" format
        # Fallback for UNC paths or other formats
        parts = str(path).split(os.sep)
        if parts and len(parts[0]) == 2 and parts[0][1] == ":":
            return parts[0]
        return str(path.anchor) if path.anchor else str(path)

    elif current_os in ("macOS", "Linux"):
        # macOS/Linux: Find the mount point
        # For /Volumes/GoogleDrive/My Drive/... return /Volumes/GoogleDrive
        path_str = str(path)

        # Check if under /Volumes
        if path_str.startswith("/Volumes/"):
            parts = path_str.split("/")
            if len(parts) >= 3:
                return f"/Volumes/{parts[2]}"

        # Check if under home directory
        home = str(Path.home())
        if path_str.startswith(home):
            # Look for Google Drive folder
            relative = path_str[len(home):].lstrip("/")
            first_component = relative.split("/")[0] if "/" in relative else relative
            if "google" in first_component.lower() or "drive" in first_component.lower():
                return f"{home}/{first_component}"

        # Fallback: return root
        return "/" if path_str.startswith("/") else str(path)

    # Unknown OS: return as-is
    return str(path)


# --- Google Drive API - Authentication ---------------------------------------------------------------
def get_drive_service():
    """
    Description:
        Authenticate with Google Drive API using OAuth 2.0.
        Loads token from disk if valid, refreshes if expired, or launches a browser
        for first-time authentication. Returns an authenticated Drive service.

    Args:
        None.

    Returns:
        googleapiclient.discovery.Resource | None:
            The authenticated Google Drive API service, or None on failure.

    Raises:
        None.

    Notes:
        - Requires credentials/credentials.json from Google Cloud Console.
        - Writes/reads token.json for future sessions.
    """
    creds = None

    # --- Load existing token -------------------------------------------------------------------------
    if os.path.exists(GDRIVE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GDRIVE_TOKEN_FILE, SCOPES)
            logger.info("Loaded existing token: %s", GDRIVE_TOKEN_FILE.name)
        except Exception as e:
            logger.warning("Failed to load token, re-authenticating: %s", e)
            creds = None

    # --- Validate or refresh token -------------------------------------------------------------------
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Token refreshed successfully.")
            except Exception as e:
                logger.error("Token refresh failed: %s", e)
                return None
        else:
            if not GDRIVE_CREDENTIALS_FILE.exists():
                logger.error("Missing OAuth client secret: %s", GDRIVE_CREDENTIALS_FILE)
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GDRIVE_CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("OAuth authentication completed.")
            except Exception as e:
                logger.error("OAuth error: %s", e)
                return None

        # --- Save token -------------------------------------------------------------------------------
        try:
            with open(GDRIVE_TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            logger.info("Token saved: %s", GDRIVE_TOKEN_FILE.name)
        except Exception as e:
            logger.warning("Could not save token: %s", e)

    # --- Build Drive service -------------------------------------------------------------------------
    try:
        service = build("drive", "v3", credentials=creds)
        logger.info("Google Drive API service initialised.")
        return service
    except HttpError as e:
        logger.error("HTTP error during service build: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)

    return None


# --- Google Drive API - Search Helpers ---------------------------------------------------------------
def find_folder_id(service, folder_name: str) -> str | None:
    """
    Description:
        Find the Google Drive folder ID matching a given folder name.

    Args:
        service (Resource): Active authenticated Drive service.
        folder_name (str): Name of the folder to search for.

    Returns:
        str | None: The folder ID, or None if not found.

    Raises:
        None.

    Notes:
        - Only returns the first matching folder.
    """
    if not service:
        logger.error("Invalid Drive service.")
        return None

    try:
        query = (
            "mimeType='application/vnd.google-apps.folder' "
            f"and name='{folder_name}' and trashed=false"
        )
        response = service.files().list(
            q=query, fields="files(id, name)", pageSize=1
        ).execute()
        items = response.get("files", [])
        if not items:
            logger.warning("Folder not found: %s", folder_name)
            return None
        folder_id = items[0]["id"]
        logger.info("Found folder '%s' (ID: %s)", folder_name, folder_id)
        return folder_id
    except HttpError as e:
        logger.error("Error searching for folder: %s", e)
        return None


def find_file_id(service, file_name: str, in_folder_id: str | None = None) -> str | None:
    """
    Description:
        Find a file ID in Google Drive by name, optionally within a specific folder.

    Args:
        service (Resource): Active authenticated Drive service.
        file_name (str): Name of the file to search for.
        in_folder_id (str | None): Optional folder ID to search within.

    Returns:
        str | None: The file ID, or None if not found.

    Raises:
        None.

    Notes:
        - Ignores folders; returns only file-type items.
    """
    if not service:
        logger.error("Invalid Drive service.")
        return None

    try:
        query = (
            f"name='{file_name}' and mimeType!='application/vnd.google-apps.folder' "
            "and trashed=false"
        )
        if in_folder_id:
            query += f" and '{in_folder_id}' in parents"

        response = service.files().list(
            q=query, fields="files(id, name)", pageSize=1
        ).execute()
        items = response.get("files", [])
        if not items:
            logger.warning("File not found: %s", file_name)
            return None
        file_id = items[0]["id"]
        logger.info("Found file '%s' (ID: %s)", file_name, file_id)
        return file_id
    except HttpError as e:
        logger.error("Error searching for file: %s", e)
        return None


# --- Google Drive API - File Operations --------------------------------------------------------------
def upload_file(service, local_path: Path, folder_id: str | None = None, filename: str | None = None) -> str | None:
    """
    Description:
        Upload a local file to Google Drive.

    Args:
        service (Resource): Authenticated Drive service.
        local_path (Path): Path to the local file.
        folder_id (str | None): Target folder ID.
        filename (str | None): Optional rename on upload.

    Returns:
        str | None: The file ID of the uploaded file.

    Raises:
        None.

    Notes:
        - Supports resumable uploads.
    """
    if not service:
        logger.error("Invalid Drive service.")
        return None
    if not local_path.exists():
        logger.error("File not found: %s", local_path)
        return None

    try:
        filename = filename or local_path.name
        metadata: dict[str, Any] = {"name": filename}
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaFileUpload(local_path, resumable=True)
        upload_result = (
            service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = upload_result.get("id")
        logger.info("Uploaded '%s' (ID: %s)", filename, file_id)
        return file_id
    except HttpError as e:
        logger.error("Upload error: %s", e)
        return None


def upload_dataframe_as_csv(service, csv_buffer: io.StringIO, filename: str, folder_id: str | None = None) -> str | None:
    """
    Description:
        Upload a DataFrame as CSV directly from memory.

    Args:
        service (Resource): Drive API service.
        csv_buffer (io.StringIO): CSV buffer from DataFrame.to_csv().
        filename (str): The file name (must include '.csv').
        folder_id (str | None): Optional folder ID.

    Returns:
        str | None: Uploaded file ID.

    Raises:
        None.

    Notes:
        - Avoids writing CSVs to disk.
    """
    if not service:
        logger.error("Invalid Drive service.")
        return None

    try:
        data_bytes = io.BytesIO(csv_buffer.getvalue().encode("utf-8"))
        metadata: dict[str, Any] = {"name": filename}
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaIoBaseUpload(data_bytes, mimetype="text/csv", resumable=True)
        upload = (
            service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = upload.get("id")
        logger.info("Uploaded DataFrame as '%s' (ID: %s)", filename, file_id)
        return file_id
    except HttpError as e:
        logger.error("Upload error: %s", e)
        return None


def download_file(service, file_id: str, local_path: Path) -> None:
    """
    Description:
        Download a file from Google Drive.

    Args:
        service (Resource): Drive API service.
        file_id (str): The file ID to download.
        local_path (Path): Destination path.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses MediaIoBaseDownload for chunked downloading.
    """
    if not service:
        logger.error("Invalid Drive service.")
        return

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            logger.info("Download %s%%", int(status.progress() * 100))

        with open(local_path, "wb") as out_file:
            out_file.write(fh.getbuffer())

        logger.info("File saved to: %s", local_path)
    except HttpError as e:
        logger.error("Download error: %s", e)


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
    # --- Constants ---
    "SCOPES",
    # --- Local Drive Detection ---
    "is_google_drive_installed",
    "get_google_drive_accounts",
    "extract_drive_root",
    # --- Google Drive API - Authentication ---
    "get_drive_service",
    # --- Google Drive API - Search Helpers ---
    "find_folder_id",
    "find_file_id",
    # --- Google Drive API - File Operations ---
    "upload_file",
    "upload_dataframe_as_csv",
    "download_file",
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
        Self-test entry point for C19_google_drive_integration.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates local drive detection, path extraction, and optional API connectivity.
    """
    logger.info("=" * 60)
    logger.info("Running C19_google_drive_integration self-test...")
    logger.info("=" * 60)

    # ------------------------------------------------------------------------------------------------
    # Test 1: Local Drive Detection
    # ------------------------------------------------------------------------------------------------
    logger.info("")
    logger.info("-" * 40)
    logger.info("TEST 1: Local Drive Detection")
    logger.info("-" * 40)

    current_os = detect_os()
    logger.info("Detected OS: %s", current_os)

    if is_google_drive_installed():
        logger.info("Google Drive App: INSTALLED")

        accounts = get_google_drive_accounts()
        if accounts:
            logger.info("Found %s account(s):", len(accounts))
            for acc in accounts:
                logger.info("  - %s -> %s", acc['email'], acc['root'])
        else:
            logger.warning("No accounts found.")
    else:
        logger.info("Google Drive App: NOT INSTALLED")

    # ------------------------------------------------------------------------------------------------
    # Test 2: Extract Drive Root
    # ------------------------------------------------------------------------------------------------
    logger.info("")
    logger.info("-" * 40)
    logger.info("TEST 2: Extract Drive Root")
    logger.info("-" * 40)

    if current_os == "Windows":
        test_paths = [
            "H:/My Drive/Projects/File.xlsx",
            "H:\\My Drive\\Deep\\Nested\\Folder\\file.csv",
            "C:\\Users\\Someone\\Documents\\file.txt",
        ]
    else:
        test_paths = [
            "/Volumes/GoogleDrive/My Drive/Projects",
            "/Users/gerry/Google Drive/My Drive/file.txt",
            "/home/user/documents/file.txt",
        ]

    for test_path in test_paths:
        root = extract_drive_root(test_path)
        logger.info("  %s", test_path)
        logger.info("    -> Root: %s", root)

    # ------------------------------------------------------------------------------------------------
    # Test 3: API (Optional - requires credentials)
    # ------------------------------------------------------------------------------------------------
    logger.info("")
    logger.info("-" * 40)
    logger.info("TEST 3: Google Drive API (optional)")
    logger.info("-" * 40)

    if GDRIVE_CREDENTIALS_FILE.exists():
        logger.info("Credentials file found. Testing API connection...")
        service = get_drive_service()
        if service:
            try:
                results = service.files().list(
                    pageSize=5, fields="files(id, name)"
                ).execute()
                files = results.get("files", [])
                if not files:
                    logger.warning("No files found in Drive.")
                else:
                    logger.info("Found %s file(s):", len(files))
                    for f in files:
                        logger.info("  - %s (ID: %s)", f['name'], f['id'])
            except Exception as e:
                logger.error("Listing error: %s", e)
    else:
        logger.info("Skipping API test (no credentials at %s)", GDRIVE_CREDENTIALS_FILE)

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ C19_google_drive_integration self-test completed successfully.")
    logger.info("=" * 60)


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()