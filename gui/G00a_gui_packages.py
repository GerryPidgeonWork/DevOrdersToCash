# ====================================================================================================
# G00a_gui_packages.py
# ----------------------------------------------------------------------------------------------------
# Centralised GUI import hub for Tkinter, ttk, and optional ttkbootstrap.
#
# Purpose:
#   - Provide a single, safe import location for all GUI-related libraries.
#   - Prevent GUI imports from appearing in the core library (critical architecture rule).
#   - Avoid premature Tk/ttkbootstrap initialisation during module loading.
#   - Keep GUI modules lightweight by importing everything from this shared hub.
#
# Usage:
#       from gui.G00a_gui_packages import tk, ttk, tkFont, Calendar, DateEntry
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
# ensure the core library can be imported safely, and prevent project-local paths from overriding
# installed site-packages.
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
# 2. GUI PACKAGE IMPORTS
# ----------------------------------------------------------------------------------------------------
# Tkinter imports must only occur in this module.
# This prevents:
#   - Accidental root window creation,
#   - Premature ttkbootstrap initialisation,
#   - Circular dependencies,
#   - Environment crashes on systems without a GUI subsystem.
#
# CRITICAL ARCHITECTURE RULE:
#   This module is the ONLY location where GUI packages may be imported directly.
#   All other GUI modules must import from this hub.
# ----------------------------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Misc, Pack, scrolledtext
import tkinter.font as tkFont


# ====================================================================================================
# 3. MODULE IMPLEMENTATION (CLASSES / FUNCTIONS)
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Define implementation elements for GUI package management, including optional package loading,
#   theme initialisation, and debug utilities.
#
# Rules:
#   - Items here support the GUI import hub's specific purpose.
#   - No execution or side-effects in this section.
# ====================================================================================================

# --- Debug Configuration -----------------------------------------------------------------------------
DEBUG_GUI_IMPORTS: bool = False


def gui_debug(msg: str) -> None:
    """Internal debug output for GUI package loading (disabled by default)."""
    if DEBUG_GUI_IMPORTS:
        # Lazy import to avoid circular dependencies at module load time
        import logging
        logging.getLogger(__name__).debug("[G00a] %s", msg)


# --- Optional ttkbootstrap Support (Opt-In Only) -----------------------------------------------------
# ttkbootstrap must not auto-import because:
#   • It is not guaranteed to exist in all environments.
#   • Importing it too early overrides themes and breaks framework styling.
#   • BaseGUI initialisation must happen first.
#
# Usage:
#       from gui.G00a_gui_packages import enable_ttkbootstrap
#       enable_ttkbootstrap()
#
# Calling this is optional. Silent fallback is used if import fails.
# -----------------------------------------------------------------------------------------------------
tb = None
Window = None
Style = None
ThemedLabel = ttk.Label
ThemedButton = ttk.Button
ThemedFrame = ttk.Frame


def enable_ttkbootstrap() -> None:
    """Opt-in activation of ttkbootstrap. Silent fallback to pure ttk."""
    global tb, Window, Style, ThemedLabel, ThemedButton, ThemedFrame

    try:
        import ttkbootstrap as ttkb  # type: ignore
        tb = ttkb
        Window = tb.Window
        Style = tb.Style
        ThemedLabel = tb.Label
        ThemedButton = tb.Button
        ThemedFrame = tb.Frame

    except Exception as exc:
        # Expected fallback — do not raise, do not warn, just revert to ttk
        gui_debug(f"ttkbootstrap import failed → {exc!r}")
        tb = None
        Window = None
        Style = None
        ThemedLabel = ttk.Label
        ThemedButton = ttk.Button
        ThemedFrame = ttk.Frame


# --- Optional tkcalendar Support ---------------------------------------------------------------------
# tkcalendar (Calendar, DateEntry) provides date-based UI components.
# It is an optional package — importing must never break the framework.
# -----------------------------------------------------------------------------------------------------
try:
    from tkcalendar import Calendar, DateEntry  # type: ignore
except Exception:
    Calendar = None
    DateEntry = None


# --- Windows Theme Initialisation --------------------------------------------------------------------
# On Windows 11 (and other Windows versions), the native "vista" and "winnative"
# themes render ttk.Button using OS-native controls that completely ignore the
# `background` property. This means custom button background colours are discarded.
#
# Solution:
#   - Detect Windows platform at runtime.
#   - Switch to the "clam" theme, which fully honours ttk styling properties.
#   - This MUST be called immediately after creating the Tk root window,
#     BEFORE any ttk styles are registered.
#
# Usage:
#   root = tk.Tk()
#   init_gui_theme()  # Call immediately after creating root
# -----------------------------------------------------------------------------------------------------
GUI_THEME_INITIALISED: bool = False


def init_gui_theme() -> None:
    """
    Initialise the ttk theme for cross-platform button background support.

    On Windows, this switches from the native theme (vista/winnative) to "clam",
    which correctly honours button background colours.

    MUST be called immediately after creating the Tk root window, BEFORE any
    ttk styles or widgets are created.

    Usage:
        root = tk.Tk()
        init_gui_theme()  # <-- Call here
        # ... create widgets

    Args:
        None.

    Returns:
        None.

    Notes:
        - Idempotent: safe to call multiple times.
        - On non-Windows platforms, this is a no-op.
    """
    global GUI_THEME_INITIALISED

    if GUI_THEME_INITIALISED:
        return

    GUI_THEME_INITIALISED = True

    # Only switch theme on Windows
    if not sys.platform.startswith("win"):
        return

    try:
        style = ttk.Style()
        current_theme = style.theme_use()

        # Only switch if using a Windows-native theme that ignores background
        if current_theme in ("vista", "winnative", "xpnative"):
            style.theme_use("clam")
            gui_debug(f"Switched theme from '{current_theme}' to 'clam'")

    except Exception as exc:
        gui_debug(f"Warning: Could not initialise theme: {exc}")
        GUI_THEME_INITIALISED = False  # Allow retry


def is_gui_theme_initialised() -> bool:
    """Check if the GUI theme has been initialised."""
    return GUI_THEME_INITIALISED


def reset_gui_theme_flag() -> None:
    """Reset the theme initialisation flag (for testing purposes only)."""
    global GUI_THEME_INITIALISED
    GUI_THEME_INITIALISED = False


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Explicit declaration of the public API surface.
# This helps IDEs, documentation generators, and users understand what's intended for external use.
# ====================================================================================================

__all__ = [
    # Tkinter / ttk namespaces
    "tk",
    "ttk",
    "tkFont",
    "messagebox",
    "filedialog",
    "Misc",
    "Pack",
    "scrolledtext",

    # Optional tkcalendar widgets
    "Calendar",
    "DateEntry",

    # Optional ttkbootstrap activator
    "enable_ttkbootstrap",

    # Theme initialisation utilities
    "init_gui_theme",
    "is_gui_theme_initialised",
    "reset_gui_theme_flag",
]


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
# This section is the ONLY location where runtime execution should occur.
# Rules:
#   - No side-effects at import time.
#   - Any test or demonstration logic should be gated behind __main__.
#
# This ensures safe importing from other modules and prevents hidden execution paths.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Self-test for GUI package imports.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Verifies all expected packages are importable.
        - Reports optional package availability.
    """
    print("G00a_gui_packages self-test initialised.")
    print(f"  tk:           {tk}")
    print(f"  ttk:          {ttk}")
    print(f"  tkFont:       {tkFont}")
    print(f"  Calendar:     {Calendar}")
    print(f"  DateEntry:    {DateEntry}")
    print(f"  ttkbootstrap: {tb}")
    print("Self-test complete.")


if __name__ == "__main__":
    main()