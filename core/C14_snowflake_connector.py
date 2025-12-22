# ====================================================================================================
# C14_snowflake_connector.py
# ----------------------------------------------------------------------------------------------------
# Provides a unified Snowflake connection interface and SQL execution utilities for PyBaseEnv.
#
# Purpose:
#   - Establish secure Okta SSO connections to Snowflake.
#   - Auto-select an appropriate Role/Warehouse context.
#   - Support both interactive (CLI/GUI) and automated (config-based) connections.
#   - Load and execute .sql files stored in the /sql/ directory.
#   - Support lightweight parameter substitution for templated SQL files.
#   - Return results as raw tuples or pandas DataFrames.
#
# Usage:
#   from core.C14_snowflake_connector import (
#       get_snowflake_credentials,
#       connect_to_snowflake,
#       run_query,
#       load_sql_file,
#       run_sql_file,
#       run_sql_to_dataframe,
#       run_sql_file_to_dataframe,
#   )
#
#   init_logging()  # from C01, recommended before connecting
#   conn = connect_to_snowflake("user@example.com")
#   if conn:
#       rows = run_query(conn, "SELECT CURRENT_DATE();")
#       df = run_sql_file_to_dataframe(conn, "orders_summary.sql", params={"start_date": "2025-11-01"})
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
#
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C02_set_file_paths import PROJECT_ROOT
from core.C04_config_loader import get_config


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

# --- Default Snowflake Configuration -----------------------------------------------------------------
SNOWFLAKE_ACCOUNT: str = "HC77929-GOPUFF"
SNOWFLAKE_EMAIL_DOMAIN: str = "gopuff.com"

CONTEXT_PRIORITY: List[Dict[str, str]] = [
    {"role": "OKTA_ANALYTICS_ROLE", "warehouse": "ANALYTICS"},
    {"role": "OKTA_READER_ROLE", "warehouse": "READER_WH"},
]

DEFAULT_DATABASE: str = "DBT_PROD"
DEFAULT_SCHEMA: str = "CORE"
AUTHENTICATOR: str = "externalbrowser"
TIMEOUT_SECONDS: int = 20


# --- Snowflake Credential Builder --------------------------------------------------------------------
def get_snowflake_credentials(email_address: str) -> Dict[str, Any] | None:
    """
    Description:
        Validate a user email address and build a Snowflake Okta SSO credential
        dictionary suitable for snowflake.connector.connect().

    Args:
        email_address (str):
            User's email address to be used for Snowflake authentication.

    Returns:
        Dict[str, Any] | None:
            A credential mapping containing keys such as 'user', 'account', and
            'authenticator' if the email is valid; otherwise None.

    Raises:
        None.

    Notes:
        - The email must contain an '@' symbol and match the allowed domain
          defined in SNOWFLAKE_EMAIL_DOMAIN.
        - On success, the SNOWFLAKE_USER environment variable is set and all
          validation steps are logged.
    """
    if not email_address or "@" not in email_address:
        logger.error("❌ Invalid email provided: %s", email_address)
        return None

    required_suffix = f"@{SNOWFLAKE_EMAIL_DOMAIN}"
    if not email_address.endswith(required_suffix):
        logger.error(
            "❌ Email '%s' does not match required domain '%s'.",
            email_address,
            SNOWFLAKE_EMAIL_DOMAIN,
        )
        return None

    os.environ["SNOWFLAKE_USER"] = email_address
    logger.info("📧 Using Snowflake email: %s", email_address)

    return {
        "user": email_address,
        "account": SNOWFLAKE_ACCOUNT,
        "authenticator": AUTHENTICATOR,
    }


# --- Snowflake Context Setter ------------------------------------------------------------------------
def set_snowflake_context(
    conn: Any,
    role: str,
    warehouse: str,
    database: str = DEFAULT_DATABASE,
    schema: str = DEFAULT_SCHEMA,
) -> bool:
    """
    Description:
        Apply role, warehouse, database, and schema context to an active
        Snowflake connection.

    Args:
        conn (Any):
            Active Snowflake connection object.
        role (str):
            Target Snowflake role (for example, 'OKTA_ANALYTICS_ROLE').
        warehouse (str):
            Target warehouse name.
        database (str):
            Database name to select. Defaults to DEFAULT_DATABASE.
        schema (str):
            Schema name to select. Defaults to DEFAULT_SCHEMA.

    Returns:
        bool:
            True if all context settings are applied successfully; otherwise
            False.

    Raises:
        None.

    Notes:
        - Any failure is logged via log_exception and results in False.
        - A short summary of the final active context is logged on success.
    """
    cur = conn.cursor()
    try:
        cur.execute(f"USE ROLE {role}")
        cur.execute(f"USE WAREHOUSE {warehouse}")
        cur.execute(f"USE DATABASE {database}")
        cur.execute(f"USE SCHEMA {schema}")

        cur.execute(
            """
            SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(),
                   CURRENT_DATABASE(), CURRENT_SCHEMA()
            """
        )
        role_now, wh_now, db_now, sc_now = cur.fetchone()

        logger.info(
            "📂 Active Context → Role=%s, Warehouse=%s, DB=%s, Schema=%s",
            role_now,
            wh_now,
            db_now,
            sc_now,
        )
        cur.close()
        return True

    except Exception as exc:
        log_exception(exc, context=f"set_snowflake_context({role}/{warehouse})")
        cur.close()
        return False


# --- Snowflake Connection Handler --------------------------------------------------------------------
def connect_to_snowflake(email_address: str) -> Any | None:
    """
    Description:
        Establish an Okta-based Snowflake SSO connection with automatic context
        selection based on a priority list of role/warehouse combinations.

    Args:
        email_address (str):
            Email address used for Snowflake authentication.

    Returns:
        Any | None:
            An active Snowflake connection object if login and context
            selection succeed; otherwise None.

    Raises:
        None.

    Notes:
        - This function uses |print()| for interactive Okta prompts as a
          deliberate exception to the usual "no print in core modules" rule.
        - All non-interactive feedback, including failures, is written to the
          central logging system.
        - If the login fails due to a user mismatch, SNOWFLAKE_USER is cleared
          from the environment as a safety measure.
    """
    creds = get_snowflake_credentials(email_address)
    if not creds:
        return None

    logger.info("🔄 Initiating Snowflake SSO session via Okta...")
    print("Please complete the Okta authentication in the browser window.\n")

    conn_container: Dict[str, Any] = {}

    def connector() -> None:
        """
        Description:
            Worker function that performs the actual Snowflake connection in a
            background thread so that a timeout can be enforced.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Redirects stdout/stderr into in-memory buffers to avoid noisy
              console output from the Snowflake driver.
            - Stores either 'conn' or 'error' in conn_container.
        """
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                conn_obj = snowflake.connector.connect(**creds)
                conn_container["conn"] = conn_obj
        except Exception as exc:
            conn_container["error"] = exc

    thread = threading.Thread(target=connector, daemon=True)
    thread.start()
    thread.join(timeout=TIMEOUT_SECONDS)

    # --- Timeout handling ---------------------------------------------------------------------------
    if thread.is_alive():
        logger.error(
            "⏰ Timeout after %s seconds waiting for Okta login.",
            TIMEOUT_SECONDS,
        )
        return None

    if "error" in conn_container:
        err = str(conn_container["error"])
        logger.error("❌ Connection failed: %s", err)

        if "differs from the user currently logged in" in err:
            logger.warning(
                "User mismatch detected — clearing SNOWFLAKE_USER environment variable."
            )
            os.environ.pop("SNOWFLAKE_USER", None)

        return None

    if "conn" not in conn_container:
        logger.error("❌ Unexpected failure — no connection object returned.")
        return None

    conn = conn_container["conn"]
    logger.info("✅ Authentication successful for %s", creds["user"])
    print("Retrieving available roles and warehouses...\n")

    # --- Discover available roles and warehouses ----------------------------------------------------
    try:
        cur = conn.cursor()
        available_roles = {row[1] for row in cur.execute("SHOW ROLES")}
        available_whs = {row[0] for row in cur.execute("SHOW WAREHOUSES")}
        cur.close()
    except Exception as exc:
        log_exception(exc, context="Retrieving Snowflake roles/warehouses")
        conn.close()
        return None

    # --- Attempt context selection ------------------------------------------------------------------
    for context_item in CONTEXT_PRIORITY:
        role = context_item["role"]
        wh = context_item["warehouse"]

        if role in available_roles and wh in available_whs:
            logger.info("🔧 Matching context available → %s/%s", role, wh)
            if set_snowflake_context(conn, role, wh):
                return conn
            logger.warning(
                "⚠️ Failed to apply context %s/%s; trying next option.",
                role,
                wh,
            )

    # --- No valid context found ----------------------------------------------------------------------
    logger.error("❌ No valid role/warehouse combination found for this user.")
    print("\nRequired contexts (role / warehouse):")
    for ctx in CONTEXT_PRIORITY:
        print(f"  • {ctx['role']}  /  {ctx['warehouse']}")
    conn.close()
    return None


# --- SQL Execution Helper ----------------------------------------------------------------------------
def run_query(conn: Any, sql: str, fetch: bool = True) -> Any | None:
    """
    Description:
        Execute a SQL query safely against an open Snowflake connection with
        full logging and optional result fetching.

    Args:
        conn (Any):
            Active Snowflake connection object.
        sql (str):
            SQL statement to execute.
        fetch (bool):
            When True, fetch all result rows and return them; when False,
            execute without returning data.

    Returns:
        Any | None:
            A sequence of result rows if fetch=True and the query returns
            data; otherwise None.

    Raises:
        None.

    Notes:
        - Any exceptions during execution are logged via log_exception and
          result in a None return value.
        - Only a short preview of the SQL (first 100 characters) is logged to
          avoid excessive log size.
    """
    try:
        cur = conn.cursor()
        cur.execute(sql)

        preview_raw = sql.replace("\n", " ")
        preview = preview_raw[:100]
        if len(preview_raw) > 100:
            preview = f"{preview}..."

        logger.info("🧠 Executed SQL (preview): %s", preview)

        if fetch:
            data = cur.fetchall()
            cur.close()
            logger.info("📦 Rows fetched: %s", len(data))
            return data

        cur.close()
        logger.info("✅ Query executed successfully (no fetch).")
        return None

    except Exception as exc:
        log_exception(exc, context="run_query")
        return None


# --- SQL File Loading --------------------------------------------------------------------------------
def load_sql_file(file_name: str, params: Dict[str, Any] | None = None) -> str:
    """
    Description:
        Load a SQL file from the /sql/ directory, optionally applying .format()
        parameter substitution.

    Args:
        file_name (str):
            Name of SQL file. May be given with or without ".sql".
        params (Dict[str, Any] | None):
            Dictionary of parameters to substitute in the SQL template.

    Returns:
        str:
            The fully formatted SQL text ready for execution.

    Raises:
        FileNotFoundError:
            If the SQL file does not exist.
        ValueError:
            If a placeholder in the SQL file is missing from params.
        Exception:
            For any other unexpected read/substitution errors.

    Notes:
        - Parameter replacement uses Python str.format(), so SQL placeholders
          must be in the form {param_name}.
    """
    try:
        sql_folder = PROJECT_ROOT / "sql"
        sql_path = (sql_folder / file_name).with_suffix(".sql")

        if not sql_path.exists():
            logger.error("❌ SQL file not found: %s", sql_path)
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        sql_text = sql_path.read_text(encoding="utf-8")

        if params:
            try:
                sql_text = sql_text.format(**params)
                logger.info("🧩 Applied SQL parameters: %s", params)
            except KeyError as exc:
                logger.error("❌ Missing parameter in SQL template: %s", exc)
                raise ValueError(f"Missing SQL parameter: {exc}") from exc

        logger.info("📄 Loaded SQL file: %s", sql_path.name)
        return sql_text

    except Exception as exc:
        log_exception(exc, context="load_sql_file")
        raise


# --- SQL File Execution (Raw Tuples) -----------------------------------------------------------------
def run_sql_file(
    conn: Any,
    file_name: str,
    params: Dict[str, Any] | None = None,
    fetch: bool = True,
) -> Any:
    """
    Description:
        Load a SQL file, apply substitutions if required, and execute it using
        the shared run_query helper.

    Args:
        conn (Any):
            Active Snowflake connection object.
        file_name (str):
            Name of SQL file (with or without extension).
        params (Dict[str, Any] | None):
            Optional mapping of SQL template placeholders.
        fetch (bool):
            Whether to fetch and return query results.

    Returns:
        Any | None:
            Result set (list of tuples) if fetch=True, otherwise None.

    Raises:
        None.

    Notes:
        - All exceptions are logged and return None.
        - SQL files must reside within <project_root>/sql/.
    """
    try:
        sql_text = load_sql_file(file_name, params)
        logger.info("🚀 Executing SQL file: %s", file_name)
        return run_query(conn, sql_text, fetch=fetch)

    except Exception as exc:
        log_exception(exc, context=f"run_sql_file({file_name})")
        return None


# --- SQL to DataFrame --------------------------------------------------------------------------------
def run_sql_to_dataframe(
    conn: Any,
    sql: str,
    standardise: bool = True,
) -> pd.DataFrame | None:
    """
    Description:
        Executes a SQL query string and returns results as a pandas DataFrame.

    Args:
        conn (Any):
            Active Snowflake connection.
        sql (str):
            SQL query string to execute.
        standardise (bool):
            If True, apply standardise_columns() to normalise column names.
            Defaults to True.

    Returns:
        pd.DataFrame | None:
            Query results as DataFrame, or None on error.

    Raises:
        None.

    Notes:
        - Attempts fetch_pandas_all() for optimal performance.
        - Falls back to manual DataFrame construction if Arrow unavailable.
        - All exceptions are logged and return None.
    """
    try:
        logger.info("🚀 Executing SQL to DataFrame...")
        cur = conn.cursor()
        cur.execute(sql)

        # Try Arrow-based fetch first, fallback to manual construction
        try:
            df = cur.fetch_pandas_all()
        except Exception as arrow_exc:
            logger.warning("⚠️ Arrow fetch failed, using fallback: %s", arrow_exc)
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=columns)

        cur.close()
        logger.info("📦 Returned %s rows, %s columns", len(df), len(df.columns))

        if standardise:
            from core.C12_data_processing import standardise_columns
            df = standardise_columns(df)

        return df

    except Exception as exc:
        log_exception(exc, context="run_sql_to_dataframe")
        return None


# --- SQL File to DataFrame ---------------------------------------------------------------------------
def run_sql_file_to_dataframe(
    conn: Any,
    file_name: str,
    params: Dict[str, Any] | None = None,
    standardise: bool = True,
) -> pd.DataFrame | None:
    """
    Description:
        Load a SQL file, apply substitutions if required, execute it, and
        return results as a pandas DataFrame.

    Args:
        conn (Any):
            Active Snowflake connection object.
        file_name (str):
            Name of SQL file (with or without extension).
        params (Dict[str, Any] | None):
            Optional mapping of SQL template placeholders.
        standardise (bool):
            If True, apply standardise_columns() to normalise column names.
            Defaults to True.

    Returns:
        pd.DataFrame | None:
            Query results as DataFrame, or None on error.

    Raises:
        None.

    Notes:
        - Combines load_sql_file() and run_sql_to_dataframe().
        - SQL files must reside within <project_root>/sql/.
    """
    try:
        sql_text = load_sql_file(file_name, params)
        logger.info("🚀 Executing SQL file to DataFrame: %s", file_name)
        return run_sql_to_dataframe(conn, sql_text, standardise=standardise)

    except Exception as exc:
        log_exception(exc, context=f"run_sql_file_to_dataframe({file_name})")
        return None


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
    # --- Configuration Constants ---
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_EMAIL_DOMAIN",
    "CONTEXT_PRIORITY",
    "DEFAULT_DATABASE",
    "DEFAULT_SCHEMA",
    # --- Credential & Context Management ---
    "get_snowflake_credentials",
    "set_snowflake_context",
    "connect_to_snowflake",
    # --- SQL Execution (Raw) ---
    "run_query",
    "load_sql_file",
    "run_sql_file",
    # --- SQL Execution (DataFrame) ---
    "run_sql_to_dataframe",
    "run_sql_file_to_dataframe",
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
        Self-test entry point for C14_snowflake_connector.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Validates Snowflake connection via Okta SSO and basic query execution.
        - Uses print() for interactive prompts as an explicit exception.
    """
    logger.info("🔍 Running C14_snowflake_connector self-test...")
    print("🔍 Running C14_snowflake_connector self-test...\n")

    test_email: str = get_config("snowflake", "email", default="")  # type: ignore[assignment]
    if not test_email:
        test_email = input("Enter your Snowflake/Okta email address: ").strip()

    connection = connect_to_snowflake(test_email)

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_ROLE(),
                       CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
                """
            )
            user, acct, role, wh, db, sc = cursor.fetchone()

            print(
                f"\n👤 {user} | 🏢 {acct} | 🧩 {role} | 🏭 {wh} | "
                f"📚 {db} | 📁 {sc}\n"
            )

            # Test run_query
            sample_sql = "SELECT CURRENT_DATE(), CURRENT_TIMESTAMP();"
            result = run_query(connection, sample_sql)
            if result:
                print(f"🧾 Sample query result: {result}")

            # Test run_sql_to_dataframe
            df = run_sql_to_dataframe(connection, sample_sql)
            if df is not None:
                logger.info("🧾 DataFrame result:\n%s", df)

            cursor.close()
            connection.close()
            logger.info("✅ C14_snowflake_connector self-test completed successfully.")

        except Exception as exc:
            log_exception(exc, context="C14 self-test main block")
    else:
        logger.error("❌ Snowflake connection test failed.")
        print("❌ Snowflake connection test failed. Check logs for details.")


if __name__ == "__main__":
    init_logging(enable_console=True)
    main()