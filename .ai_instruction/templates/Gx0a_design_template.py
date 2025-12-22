# ====================================================================================================
# {{FILENAME}}
# ----------------------------------------------------------------------------------------------------
# Page Design Template — Visual Layout Layer
#
# Purpose:
#   - Define the visual layout and widget structure for a page.
#   - Expose named widget references for controller wiring (G10b).
#   - Keep presentation separate from business logic.
#
# Usage:
#   1. Copy this template and rename to your page name (e.g., G10a_users_design.py).
#   2. Update APP_TITLE, APP_SUBTITLE, and other configuration values.
#   3. Define widget references in __init__.
#   4. Build your layout in the build_row_X() methods.
#   5. Create a matching G10b controller to wire event handlers.
#   6. Run via G10b (which imports this design).
#
# Widget Naming Convention:
#   {section}_{purpose}_{type}
#   - _var    : StringVar, IntVar, BooleanVar
#   - _entry  : Entry field
#   - _btn    : Button
#   - _combo  : Combobox
#   - _check  : Checkbox
#   - _status : Status label
#   - _label  : Label (if dynamic)
#   - _frame  : Frame (if referenced later)
#
# ----------------------------------------------------------------------------------------------------
# Author:       {{AUTHOR}}
# Created:      {{DATE}}
# Project:      {{PROJECT_NAME}}
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys
from pathlib import Path

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages ----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True

# --- Suppress Pylance warnings for dynamically-added .content attribute (G02a/G03a frames) -----------
# pyright: reportAttributeAccessIssue=false


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# PAGE LAYER POSITION:
#   G10+ pages are the application layer. They consume G02 (primitives), G03 (patterns),
#   and G04 (orchestration). Pages implement PageProtocol from G03f.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging, DEBUG
logger = get_logger(__name__)

# --- G02a: Widget Primitives + Design Tokens (THE FACADE) -------------------------------------------
# G10+ pages import ONLY from G02a. Never import from G00a directly.
from gui.G02a_widget_primitives import (
    # Widget type aliases (for type hints)
    WidgetType, EventType, FrameType, LabelType, EntryType, ButtonType,
    ComboboxType, RadioType, CheckboxType, TreeviewType, TextType,
    # Tkinter variable types
    StringVar, BooleanVar, IntVar,
    # Spacing tokens (re-exported from G01a)
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
    # Widget factories
    make_label, make_status_label, make_frame, make_entry, make_combobox, make_spinbox,
    make_button, make_checkbox, make_radio, make_textarea, make_console,
    make_separator, make_spacer,
    # Typography helpers
    page_title, section_title, body_text, small_text,
    # Dialog functions
    make_dialog, ask_directory, ask_open_file, ask_yes_no, show_info,
)

# --- G02b: Layout Utilities --------------------------------------------------------------------------
from gui.G02b_layout_utils import (
    layout_row, layout_col, grid_configure, stack_vertical, stack_horizontal,
)

# --- G03a: Layout Patterns ---------------------------------------------------------------------------
from gui.G03a_layout_patterns import (
    page_layout, make_content_row, two_column_layout, three_column_layout,
    section_with_header, button_row,
)

# --- G03b: Container Patterns ------------------------------------------------------------------------
from gui.G03b_container_patterns import (
    make_card, make_panel, make_section, make_titled_card, make_titled_section,
    make_page_header, make_page_header_with_actions,
)

# --- G03c: Form Patterns (uncomment if using forms) --------------------------------------------------
# from gui.G03c_form_patterns import (
#     FormField, FormResult, form_field_entry, form_field_combobox, form_group, form_section,
# )

# --- G03d: Table Patterns (uncomment if using tables) ------------------------------------------------
# from gui.G03d_table_patterns import (
#     TableColumn, TableResult, create_table, create_zebra_table, insert_rows, clear_table,
# )

# --- G03e: Widget Components (uncomment if using components) -----------------------------------------
# from gui.G03e_widget_components import (
#     filter_bar, metric_card, metric_row, dismissible_alert, empty_state,
# )

# --- G03f: Renderer Protocol ------------------------------------------------------------------------
from gui.G03f_renderer import PageProtocol

# --- G04 Application Infrastructure -----------------------------------------------------------------
from gui.G04d_app_shell import AppShell


# ====================================================================================================
# 3. APP CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Basic application settings. Update these values to customise the window.
# ====================================================================================================

APP_TITLE: str = "{{APP_TITLE}}"
APP_SUBTITLE: str = "{{APP_SUBTITLE}}"
APP_VERSION: str = "{{APP_VERSION}}"
APP_AUTHOR: str = "{{AUTHOR}}"

WINDOW_WIDTH: int = 1200
WINDOW_HEIGHT: int = 800
START_MAXIMIZED: bool = False


# ====================================================================================================
# 4. COLOUR CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Change these values to restyle the entire page.
#
# Available bg_colour presets: "PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"
# Available bg_shade values:   "LIGHT", "MID", "DARK", "XDARK"
# Available fg_colour values:  "BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY", "SUCCESS", "ERROR", "WARNING"
# ====================================================================================================

PAGE_BG_COLOUR = "SECONDARY"
PAGE_BG_SHADE = "LIGHT"

ACCENT_COLOUR = "PRIMARY"
ACCENT_SHADE = "MID"

CARD_BG_COLOUR = "SECONDARY"
CARD_BG_SHADE = "LIGHT"


# ====================================================================================================
# 5. ROW CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Configure each row's visibility and column weights.
#
# Weights control column width ratios:
#   {0: 1, 1: 1}             = Two equal columns (50% / 50%)
#   {0: 3, 1: 7}             = Two columns (30% / 70%)
#   {0: 1, 1: 1, 2: 1}       = Three equal columns
#   {0: 1, 1: 1, 2: 1, 3: 1} = Four equal columns (25% each)
#
# Set USE_ROW_X = False to hide an entire row.
# ====================================================================================================

# -----------------------------------------
# Row 1
# -----------------------------------------
USE_ROW_1: bool = True
ROW_1_TITLE: str = "Section One"
ROW_1_WEIGHTS: Dict[int, int] = {0: 1, 1: 1}
ROW_1_MIN_HEIGHT: int = 200

# -----------------------------------------
# Row 2
# -----------------------------------------
USE_ROW_2: bool = True
ROW_2_TITLE: str = "Section Two"
ROW_2_WEIGHTS: Dict[int, int] = {0: 1, 1: 1, 2: 1}
ROW_2_MIN_HEIGHT: int = 250

# -----------------------------------------
# Row 3 (disabled by default)
# -----------------------------------------
USE_ROW_3: bool = False
ROW_3_TITLE: str = "Section Three"
ROW_3_WEIGHTS: Dict[int, int] = {0: 1, 1: 1}
ROW_3_MIN_HEIGHT: int = 200


# ====================================================================================================
# 6. PAGE CLASS
# ----------------------------------------------------------------------------------------------------
# The main page class implementing PageProtocol.
#
# Structure:
#   - __init__: Store controller reference, declare widget references
#   - build(): Construct the page layout, return root frame
#   - build_page_header(): Render title/subtitle
#   - build_row_X(): Build each content row
#
# Widget References:
#   Declare all widgets that need controller wiring as instance attributes.
#   Initialise to None in __init__, assign in build methods.
# ====================================================================================================

class TemplatePage(PageProtocol):
    """
    Page design layer implementing PageProtocol.

    Description:
        Defines the visual layout and exposes named widget references.
        Business logic and event wiring belong in the matching G10b controller.

    Args:
        controller: The AppShell instance (or custom controller) for navigation and state.

    Widget References:
        Declare widgets here that the controller needs to access:

        # Example references (update for your page):
        self.search_entry      — Search input field
        self.search_btn        — Search button
        self.results_table     — Results treeview
        self.status_label      — Status indicator

    Notes:
        - Toggle rows via USE_ROW_X configuration variables.
        - Configure column weights via ROW_X_WEIGHTS.
        - Edit build_row_X() methods to customise content.
    """

    def __init__(self, controller: Any) -> None:
        """Store controller reference and declare widget references."""
        self.controller = controller

        # ------------------------------------------------------------------------------------------------
        # WIDGET REFERENCES
        # ------------------------------------------------------------------------------------------------
        # Declare all widgets that need controller wiring here.
        # Initialise to None; assign actual widgets in build methods.
        #
        # Naming convention: {section}_{purpose}_{type}
        #   _var    : StringVar, IntVar, BooleanVar
        #   _entry  : Entry field
        #   _btn    : Button
        #   _combo  : Combobox
        #   _check  : Checkbox
        #   _status : Status label
        #   _label  : Dynamic label
        #   _frame  : Frame container
        # ------------------------------------------------------------------------------------------------

        # Page header
        self.header_actions: FrameType | None = None  # Actions frame in header (for buttons)

        # Row 1 widgets
        self.example_entry: EntryType | None = None
        self.example_var: StringVar | None = None
        self.example_btn: ButtonType | None = None

        # Row 2 widgets
        self.status_label: LabelType | None = None

    # ------------------------------------------------------------------------------------------------
    # BUILD — Main Entry Point
    # ------------------------------------------------------------------------------------------------

    def build(self, parent: WidgetType, params: Dict[str, Any]) -> WidgetType:
        """
        Build the page layout.

        Args:
            parent: Parent widget (content_frame from AppShell).
            params: Parameters passed via navigator.navigate().

        Returns:
            The root frame of this page.
        """
        # ==========================================================================================
        # PARAMS HANDLING
        # ------------------------------------------------------------------------------------------
        # Access navigation parameters here. These come from:
        #   navigator.navigate("page_name", params={"key": "value"})
        # ==========================================================================================
        self._initial_value = params.get("initial_value", "")  # Example: pre-fill from navigation

        # ==========================================================================================
        # PAGE LAYOUT SHELL
        # ==========================================================================================
        page = page_layout(
            parent,
            padding=SPACING_LG,
            bg_colour=PAGE_BG_COLOUR,
            bg_shade=PAGE_BG_SHADE,
        )

        # ==========================================================================================
        # PAGE HEADER
        # ==========================================================================================
        self.build_page_header(page)

        # ==========================================================================================
        # ROW CONTENT
        # ==========================================================================================
        if USE_ROW_1:
            self.build_row_1(page)

        if USE_ROW_2:
            self.build_row_2(page)

        if USE_ROW_3:
            self.build_row_3(page)

        # ==========================================================================================
        # BOTTOM SPACER (push content to top)
        # ==========================================================================================
        make_spacer(page).pack(fill="both", expand=True)

        return page

    # ------------------------------------------------------------------------------------------------
    # PAGE HEADER
    # ------------------------------------------------------------------------------------------------

    def build_page_header(self, parent: WidgetType) -> None:
        """Render the page header using G03 pattern."""
        # Using make_page_header_with_actions from G03b for consistent styling.
        # The 'actions' frame can hold buttons — wire them in G10b controller.
        header, self.header_actions = make_page_header_with_actions(
            parent,
            title=APP_TITLE,
            subtitle=APP_SUBTITLE if APP_SUBTITLE else None,
            padding=SPACING_MD,
        )
        header.pack(fill="x", pady=(0, SPACING_MD))

    # ------------------------------------------------------------------------------------------------
    # ROW 1
    # ------------------------------------------------------------------------------------------------

    def build_row_1(self, parent: WidgetType) -> None:
        """Build Row 1 content."""

        # --- Section Header ---
        if ROW_1_TITLE:
            make_label(
                parent,
                text=ROW_1_TITLE,
                size="HEADING",
                bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_BG_COLOUR,
                bg_shade=PAGE_BG_SHADE,
            ).pack(anchor="w", pady=(SPACING_MD, SPACING_SM))

        # --- Row Container ---
        row = make_content_row(
            parent,
            weights=ROW_1_WEIGHTS,
            min_height=ROW_1_MIN_HEIGHT,
            bg_colour=PAGE_BG_COLOUR,
            bg_shade=PAGE_BG_SHADE,
        )

        # --- Column 0 ---
        col0 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM))

        # Column 0 content
        make_label(
            col0.content,
            text="Card Title",
            bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w", pady=(0, SPACING_SM))

        # Example: Entry with StringVar
        self.example_var = StringVar(value=self._initial_value)  # Pre-filled from params
        self.example_entry = make_entry(
            col0.content,
            textvariable=self.example_var,
            width=30,
        )
        self.example_entry.pack(anchor="w", pady=(0, SPACING_SM))

        # Example: Button (G10b controller wires the command)
        # In G10b: self.page.example_btn.configure(command=self._on_example_click)
        self.example_btn = make_button(
            col0.content,
            text="Action Button",
            fg_colour="WHITE",
            bg_colour="PRIMARY",
            bg_shade="MID",
        )
        self.example_btn.pack(anchor="w")

        # --- Column 1 ---
        col1 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, 0))

        # Column 1 content
        make_label(
            col1.content,
            text="Another Card",
            bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w", pady=(0, SPACING_SM))

        body_text(
            col1.content,
            text="Add your content here.\nThis is a placeholder card.",
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w")

    # ------------------------------------------------------------------------------------------------
    # ROW 2
    # ------------------------------------------------------------------------------------------------

    def build_row_2(self, parent: WidgetType) -> None:
        """Build Row 2 content."""

        # --- Section Header ---
        if ROW_2_TITLE:
            make_label(
                parent,
                text=ROW_2_TITLE,
                size="HEADING",
                bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_BG_COLOUR,
                bg_shade=PAGE_BG_SHADE,
            ).pack(anchor="w", pady=(SPACING_MD, SPACING_SM))

        # --- Row Container ---
        row = make_content_row(
            parent,
            weights=ROW_2_WEIGHTS,
            min_height=ROW_2_MIN_HEIGHT,
            bg_colour=PAGE_BG_COLOUR,
            bg_shade=PAGE_BG_SHADE,
        )

        # --- Column 0 ---
        col0 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM))

        make_label(
            col0.content,
            text="Column 0",
            bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w")

        # --- Column 1 ---
        col1 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, SPACING_SM))

        make_label(
            col1.content,
            text="Column 1",
            bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w")

        # --- Column 2 ---
        col2 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col2.grid(row=0, column=2, sticky="nsew", padx=(0, 0))

        make_label(
            col2.content,
            text="Column 2",
            bold=True,
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w")

        # Status label example
        self.status_label = make_label(
            col2.content,
            text="Status: Ready",
            size="SMALL",
            fg_colour="SUCCESS",
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        )
        self.status_label.pack(anchor="w", pady=(SPACING_SM, 0))

    # ------------------------------------------------------------------------------------------------
    # ROW 3 (Template — disabled by default)
    # ------------------------------------------------------------------------------------------------

    def build_row_3(self, parent: WidgetType) -> None:
        """Build Row 3 content. Disabled by default; enable via USE_ROW_3."""

        # --- Section Header ---
        if ROW_3_TITLE:
            make_label(
                parent,
                text=ROW_3_TITLE,
                size="HEADING",
                bold=True,
                fg_colour=ACCENT_COLOUR,
                bg_colour=PAGE_BG_COLOUR,
                bg_shade=PAGE_BG_SHADE,
            ).pack(anchor="w", pady=(SPACING_MD, SPACING_SM))

        # --- Row Container ---
        row = make_content_row(
            parent,
            weights=ROW_3_WEIGHTS,
            min_height=ROW_3_MIN_HEIGHT,
            bg_colour=PAGE_BG_COLOUR,
            bg_shade=PAGE_BG_SHADE,
        )

        # --- Column 0 ---
        col0 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_SM))

        make_label(
            col0.content,
            text="Row 3 Column 0",
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w")

        # --- Column 1 ---
        col1 = make_frame(
            row,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
            border_weight="MEDIUM",
            border_colour=ACCENT_COLOUR,
            padding="MD",
        )
        col1.grid(row=0, column=1, sticky="nsew", padx=(0, 0))

        make_label(
            col1.content,
            text="Row 3 Column 1",
            fg_colour=ACCENT_COLOUR,
            bg_colour=CARD_BG_COLOUR,
            bg_shade=CARD_BG_SHADE,
        ).pack(anchor="w")


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Expose page class for registration with AppShell.
# ====================================================================================================

__all__ = [
    "TemplatePage",
    "APP_TITLE",
    "APP_VERSION",
]


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
# This section is the ONLY location where runtime execution should occur.
#
# NOTE: For production use, run via the matching G10b controller instead,
#       which wires event handlers to the widget references.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Launch the page in standalone mode for layout preview.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - No event handlers are wired in this mode.
        - Use G10b controller for full functionality.
    """
    logger.info("=" * 60)
    logger.info("Application Starting: %s", APP_TITLE)
    logger.info("=" * 60)

    app = AppShell(
        title=APP_TITLE,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        app_name=APP_TITLE,
        app_version=APP_VERSION,
        app_author=APP_AUTHOR,
        start_page="main",
        start_maximized=START_MAXIMIZED,
    )

    app.register_page("main", TemplatePage)

    logger.info("Running in standalone mode (no controller wiring)")
    logger.info("=" * 60)

    app.run()


if __name__ == "__main__":
    init_logging()
    main()