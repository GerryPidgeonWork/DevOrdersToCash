# ====================================================================================================
# G20a_deliveroo_dialogs_design.py
# ----------------------------------------------------------------------------------------------------
# Deliveroo MFC Dialogs — Design Layer
#
# Purpose:
#   - Define the visual layout and widget structure for Deliveroo MFC mapping dialogs.
#   - Expose named widget references for controller wiring (G20b).
#   - Keep presentation separate from business logic.
#
# Usage:
#   1. Import dialog classes from this module.
#   2. Call dialog.build(parent) to create the dialog.
#   3. Wire event handlers in G20b controller.
#   4. Call dialog.destroy() when done.
#
# Dialogs:
#   - MfcMappingsDialog: View/edit all Deliveroo → GoPuff MFC name mappings
#   - MfcMappingEntryDialog: Add/edit a single MFC mapping
#   - UnmappedMfcDialog: Map unmapped MFCs before processing
#   - SetGopuffNameDialog: Set a single GoPuff name for an unmapped MFC
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-01-06
# Project:      GUI Framework v1.0
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
#   G20+ pages are the application layer. They consume G02 (primitives), G03 (patterns),
#   and G04 (orchestration). Dialogs are modal windows created via make_dialog.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- G02a: Widget Primitives + Design Tokens (THE FACADE) -------------------------------------------
# G20+ pages import ONLY from G02a. Never import from G00a directly.
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

# --- G03d: Table Patterns ---------------------------------------------------------------------------
from gui.G03d_table_patterns import (
    TableColumn, TableResult, create_table, create_zebra_table,
    create_table_with_toolbar, insert_rows, insert_rows_zebra, clear_table,
)

# --- G03f: Renderer Protocol ------------------------------------------------------------------------
from gui.G03f_renderer import PageProtocol

# --- G04 Application Infrastructure -----------------------------------------------------------------
from gui.G04d_app_shell import AppShell


# ====================================================================================================
# 3. APP CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Basic application settings for standalone testing.
# ====================================================================================================

APP_TITLE: str = "Deliveroo MFC Dialogs"
APP_SUBTITLE: str = "MFC name mapping management"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Gerry Pidgeon"

WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600
START_MAXIMIZED: bool = False


# ====================================================================================================
# 4. MFC MAPPINGS DIALOG (DESIGN)
# ----------------------------------------------------------------------------------------------------
# Modal dialog for viewing/editing Deliveroo → GoPuff MFC name mappings.
# Design only - callbacks are wired by controller (G20b).
# ====================================================================================================

class MfcMappingsDialog:
    """Dialog design for viewing/editing Deliveroo MFC mappings.

    Description:
        Creates a modal dialog with a table of mappings and Add/Edit/Delete buttons.
        All widget creation happens here; business logic is handled via callbacks.

    Attributes:
        dialog: The Toplevel window.
        tree: Treeview widget for the mappings table.
        add_btn: Add button widget.
        edit_btn: Edit button widget.
        delete_btn: Delete button widget.
        close_btn: Close button widget.
        count_label: Label showing mapping count.
        on_add: Callback for add button (set by controller).
        on_edit: Callback for edit button (set by controller).
        on_delete: Callback for delete button (set by controller).
        on_close: Callback for close button (set by controller).
    """

    def __init__(self) -> None:
        """Initialise dialog with empty widget references."""
        self.dialog: Any = None
        self.tree: Any = None
        self.add_btn: Any = None
        self.edit_btn: Any = None
        self.delete_btn: Any = None
        self.close_btn: Any = None
        self.count_label: Any = None

        # Callbacks (wired by controller)
        self.on_add: Callable[[], None] | None = None
        self.on_edit: Callable[[], None] | None = None
        self.on_delete: Callable[[], None] | None = None
        self.on_close: Callable[[], None] | None = None

    def build(self, parent: Any) -> Any:
        """Build the dialog and all widgets.

        Args:
            parent: Parent widget (dialog will be modal to this).

        Returns:
            The Toplevel dialog window.
        """
        # Create modal dialog
        self.dialog = make_dialog(
            parent,
            title="Deliveroo MFC Mappings",
            width=650,
            height=500,
            modal=True,
            resizable=True,
        )

        # Main frame with padding
        main_frame = make_frame(self.dialog, padding="MD")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title label
        make_label(
            main_frame,
            text="Deliveroo → GoPuff MFC Name Mappings",
            size="HEADING",
            bg_colour="SECONDARY", bg_shade='LIGHT',
            bold=True,
        ).grid(row=0, column=0, sticky="w", pady=(0, SPACING_XS))

        # Instructions
        make_label(
            main_frame,
            text="Map Deliveroo restaurant names to GoPuff location names for order matching.",
            bg_colour="SECONDARY", bg_shade='LIGHT',
            size="SMALL",
        ).grid(row=1, column=0, sticky="w", pady=(0, SPACING_MD))

        # Create table with toolbar
        columns = [
            TableColumn(id="deliveroo_name", heading="Deliveroo Name", width=280),
            TableColumn(id="gopuff_name", heading="GoPuff Name", width=280),
        ]

        outer_frame, toolbar, table_result = create_table_with_toolbar(
            main_frame, columns=columns, height=12, selectmode="browse"
        )
        outer_frame.grid(row=2, column=0, sticky="nsew", pady=(0, SPACING_SM))

        self.tree = table_result.treeview

        # Toolbar buttons
        self.add_btn = make_button(
            toolbar, text="Add",
            fg_colour="WHITE", bg_colour="PRIMARY", bg_shade="MID"
        )
        self.add_btn.pack(side="left", padx=(0, SPACING_XS))

        self.edit_btn = make_button(
            toolbar, text="Edit",
            fg_colour="WHITE", bg_colour="GREY", bg_shade="MID"
        )
        self.edit_btn.pack(side="left", padx=(0, SPACING_XS))

        self.delete_btn = make_button(
            toolbar, text="Delete",
            fg_colour="WHITE", bg_colour="ERROR"
        )
        self.delete_btn.pack(side="left", padx=(0, SPACING_XS))

        # Count label in toolbar
        self.count_label = make_label(
            toolbar, text="0 mapping(s)",
            size="SMALL", italic=True,
        )
        self.count_label.pack(side="right", padx=SPACING_XS)

        # Bottom button row
        bottom_frame = make_frame(main_frame)
        bottom_frame.grid(row=3, column=0, sticky="ew", pady=(SPACING_SM, 0))

        self.close_btn = make_button(
            bottom_frame, text="Close",
            fg_colour="WHITE", bg_colour="GREY", bg_shade="DARK"
        )
        self.close_btn.pack(side="right")

        return self.dialog

    def update_count(self, count: int) -> None:
        """Update the mapping count label.

        Args:
            count: Number of mappings to display.
        """
        if self.count_label:
            self.count_label.configure(text=f"{count} mapping(s)")

    def destroy(self) -> None:
        """Close and destroy the dialog."""
        if self.dialog:
            self.dialog.destroy()


# ====================================================================================================
# 5. MFC MAPPING ENTRY DIALOG (DESIGN)
# ----------------------------------------------------------------------------------------------------
# Simple form dialog for adding/editing a single MFC mapping.
# ====================================================================================================

class MfcMappingEntryDialog:
    """Dialog design for adding/editing a single MFC mapping.

    Description:
        Simple form dialog with Deliveroo name and GoPuff name fields.
        Used as sub-dialog of MfcMappingsDialog.

    Attributes:
        dialog: The Toplevel window.
        dr_entry: Entry for Deliveroo name.
        gp_entry: Entry for GoPuff name.
        save_btn: Save button.
        cancel_btn: Cancel button.
        on_save: Callback for save (set by controller).
        on_cancel: Callback for cancel (set by controller).
    """

    def __init__(self) -> None:
        """Initialise dialog with empty widget references."""
        self.dialog: Any = None
        self.dr_entry: Any = None
        self.gp_entry: Any = None
        self.save_btn: Any = None
        self.cancel_btn: Any = None

        # Callbacks
        self.on_save: Callable[[], None] | None = None
        self.on_cancel: Callable[[], None] | None = None

    def build(
        self,
        parent: Any,
        title: str = "Add MFC Mapping",
        initial_dr_name: str = "",
        initial_gp_name: str = "",
    ) -> Any:
        """Build the entry dialog.

        Args:
            parent: Parent dialog window.
            title: Dialog title.
            initial_dr_name: Initial value for Deliveroo name field.
            initial_gp_name: Initial value for GoPuff name field.

        Returns:
            The Toplevel dialog window.
        """
        self.dialog = make_dialog(
            parent,
            title=title,
            width=420,
            height=160,
            modal=True,
            resizable=False,
        )

        # Main frame
        main_frame = make_frame(self.dialog, padding="MD")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Deliveroo name field
        make_label(main_frame, text="Deliveroo Name:", size="SMALL").grid(
            row=0, column=0, sticky="w", pady=SPACING_XS
        )
        self.dr_entry = make_entry(main_frame, width=45)
        self.dr_entry.grid(row=0, column=1, sticky="ew", pady=SPACING_XS, padx=(SPACING_XS, 0))
        if initial_dr_name:
            self.dr_entry.insert(0, initial_dr_name)

        # GoPuff name field
        make_label(main_frame, text="GoPuff Name:", size="SMALL").grid(
            row=1, column=0, sticky="w", pady=SPACING_XS
        )
        self.gp_entry = make_entry(main_frame, width=45)
        self.gp_entry.grid(row=1, column=1, sticky="ew", pady=SPACING_XS, padx=(SPACING_XS, 0))
        if initial_gp_name:
            self.gp_entry.insert(0, initial_gp_name)

        # Button row
        btn_frame = make_frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(SPACING_MD, 0))

        self.save_btn = make_button(
            btn_frame, text="Save",
            fg_colour="WHITE", bg_colour="PRIMARY", bg_shade="MID"
        )
        self.save_btn.pack(side="left", padx=SPACING_XS)

        self.cancel_btn = make_button(
            btn_frame, text="Cancel",
            fg_colour="WHITE", bg_colour="GREY", bg_shade="MID"
        )
        self.cancel_btn.pack(side="left", padx=SPACING_XS)

        # Focus the appropriate field
        if initial_gp_name:
            self.gp_entry.focus_set()
            self.gp_entry.select_range(0, "end")
        else:
            self.dr_entry.focus_set()

        return self.dialog

    def get_values(self) -> Tuple[str, str]:
        """Get current field values.

        Returns:
            Tuple of (deliveroo_name, gopuff_name).
        """
        dr_name = self.dr_entry.get().strip() if self.dr_entry else ""
        gp_name = self.gp_entry.get().strip() if self.gp_entry else ""
        return dr_name, gp_name

    def destroy(self) -> None:
        """Close and destroy the dialog."""
        if self.dialog:
            self.dialog.destroy()


# ====================================================================================================
# 6. UNMAPPED MFC DIALOG (DESIGN)
# ----------------------------------------------------------------------------------------------------
# Modal dialog for mapping unmapped MFCs before processing.
# ====================================================================================================

class UnmappedMfcDialog:
    """Dialog design for mapping unmapped MFC names.

    Description:
        Shows a table of unmapped Deliveroo names that need GoPuff mappings.
        User must map all before continuing.

    Attributes:
        dialog: The Toplevel window.
        tree: Treeview widget for the unmapped items.
        set_btn: Set GoPuff Name button.
        continue_btn: Continue button (disabled until all mapped).
        cancel_btn: Cancel button.
        status_label: Label showing remaining count.
        result: Dict tracking completion state.
        on_set_name: Callback for set button.
        on_continue: Callback for continue button.
        on_cancel: Callback for cancel button.
    """

    def __init__(self) -> None:
        """Initialise dialog with empty widget references."""
        self.dialog: Any = None
        self.tree: Any = None
        self.set_btn: Any = None
        self.continue_btn: Any = None
        self.cancel_btn: Any = None
        self.status_label: Any = None
        self.result: Dict[str, bool] = {"completed": False}

        # Callbacks
        self.on_set_name: Callable[[], None] | None = None
        self.on_continue: Callable[[], None] | None = None
        self.on_cancel: Callable[[], None] | None = None

    def build(self, parent: Any, unmapped_count: int) -> Any:
        """Build the unmapped MFC dialog.

        Args:
            parent: Parent widget.
            unmapped_count: Number of unmapped items (for title).

        Returns:
            The Toplevel dialog window.
        """
        self.dialog = make_dialog(
            parent,
            title="Map Unmapped MFCs",
            width=700,
            height=550,
            modal=True,
            resizable=True,
        )

        # Main frame
        main_frame = make_frame(self.dialog, padding="MD")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        make_label(
            main_frame,
            text=f"Found {unmapped_count} Unmapped MFC(s)",
            size="HEADING",
            bold=True,
        ).grid(row=0, column=0, sticky="w", pady=(0, SPACING_XS))

        # Instructions
        make_label(
            main_frame,
            text="Please provide the GoPuff location name for each Deliveroo restaurant.\n"
                 "Double-click a row or select and click 'Set GoPuff Name' to map.",
            size="SMALL",
        ).grid(row=1, column=0, sticky="w", pady=(0, SPACING_MD))

        # Table with toolbar
        columns = [
            TableColumn(id="deliveroo_name", heading="Deliveroo Name", width=300),
            TableColumn(id="gopuff_name", heading="GoPuff Name", width=300),
        ]

        outer_frame, toolbar, table_result = create_table_with_toolbar(
            main_frame, columns=columns, height=12, selectmode="browse"
        )
        outer_frame.grid(row=2, column=0, sticky="nsew", pady=(0, SPACING_SM))

        self.tree = table_result.treeview

        # Set button
        self.set_btn = make_button(
            toolbar, text="Set GoPuff Name",
            fg_colour="WHITE", bg_colour="PRIMARY", bg_shade="MID"
        )
        self.set_btn.pack(side="left", padx=(0, SPACING_XS))

        # Status label
        self.status_label = make_label(
            toolbar, text=f"{unmapped_count} remaining to map",
            size="SMALL", italic=True,
        )
        self.status_label.pack(side="right", padx=SPACING_XS)

        # Bottom buttons
        bottom_frame = make_frame(main_frame)
        bottom_frame.grid(row=3, column=0, sticky="ew", pady=(SPACING_SM, 0))

        self.continue_btn = make_button(
            bottom_frame, text="Continue",
            fg_colour="WHITE", bg_colour="SUCCESS"
        )
        self.continue_btn.configure(state="disabled")
        self.continue_btn.pack(side="right", padx=(SPACING_XS, 0))

        self.cancel_btn = make_button(
            bottom_frame, text="Cancel",
            fg_colour="WHITE", bg_colour="GREY", bg_shade="DARK"
        )
        self.cancel_btn.pack(side="right")

        return self.dialog

    def update_status(self, remaining: int) -> None:
        """Update status label and continue button state.

        Args:
            remaining: Number of unmapped items remaining.
        """
        if self.status_label:
            self.status_label.configure(text=f"{remaining} remaining to map")
        if self.continue_btn:
            if remaining == 0:
                self.continue_btn.configure(state="normal")
            else:
                self.continue_btn.configure(state="disabled")

    def wait_for_close(self) -> bool:
        """Block until dialog closes.

        Returns:
            bool: True if user completed mapping, False if cancelled.
        """
        if self.dialog:
            self.dialog.wait_window()
        return self.result.get("completed", False)

    def set_completed(self, completed: bool) -> None:
        """Set completion state before destroying.

        Args:
            completed: Whether mapping was completed successfully.
        """
        self.result["completed"] = completed

    def destroy(self) -> None:
        """Close and destroy the dialog."""
        if self.dialog:
            self.dialog.destroy()


# ====================================================================================================
# 7. SET GOPUFF NAME DIALOG (DESIGN)
# ----------------------------------------------------------------------------------------------------
# Simple input dialog for setting a GoPuff name for a single unmapped MFC.
# ====================================================================================================

class SetGopuffNameDialog:
    """Dialog design for setting a single GoPuff name.

    Description:
        Simple input dialog for entering a GoPuff name for a Deliveroo restaurant.

    Attributes:
        dialog: The Toplevel window.
        gp_entry: Entry for GoPuff name.
        save_btn: Save button.
        cancel_btn: Cancel button.
        on_save: Callback for save.
        on_cancel: Callback for cancel.
    """

    def __init__(self) -> None:
        """Initialise dialog with empty widget references."""
        self.dialog: Any = None
        self.gp_entry: Any = None
        self.save_btn: Any = None
        self.cancel_btn: Any = None

        # Callbacks
        self.on_save: Callable[[], None] | None = None
        self.on_cancel: Callable[[], None] | None = None

    def build(
        self,
        parent: Any,
        deliveroo_name: str,
        initial_value: str = "",
    ) -> Any:
        """Build the input dialog.

        Args:
            parent: Parent dialog.
            deliveroo_name: Deliveroo name being mapped (shown as label).
            initial_value: Initial value for GoPuff name field.

        Returns:
            The Toplevel dialog window.
        """
        self.dialog = make_dialog(
            parent,
            title="Set GoPuff Name",
            width=450,
            height=130,
            modal=True,
            resizable=False,
        )

        # Main frame
        main_frame = make_frame(self.dialog, padding="MD")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Deliveroo name label
        make_label(
            main_frame,
            text=f"Deliveroo: {deliveroo_name}",
            size="SMALL",
            bold=True,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, SPACING_SM))

        # GoPuff name entry
        make_label(main_frame, text="GoPuff Name:", size="SMALL").grid(
            row=1, column=0, sticky="w", pady=SPACING_XS
        )
        self.gp_entry = make_entry(main_frame, width=50)
        self.gp_entry.grid(row=1, column=1, sticky="ew", pady=SPACING_XS, padx=(SPACING_XS, 0))
        if initial_value:
            self.gp_entry.insert(0, initial_value)

        # Button row
        btn_frame = make_frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(SPACING_MD, 0))

        self.save_btn = make_button(
            btn_frame, text="Save",
            fg_colour="WHITE", bg_colour="PRIMARY", bg_shade="MID"
        )
        self.save_btn.pack(side="left", padx=SPACING_XS)

        self.cancel_btn = make_button(
            btn_frame, text="Cancel",
            fg_colour="WHITE", bg_colour="GREY", bg_shade="MID"
        )
        self.cancel_btn.pack(side="left", padx=SPACING_XS)

        self.gp_entry.focus_set()

        return self.dialog

    def get_value(self) -> str:
        """Get current GoPuff name value.

        Returns:
            str: The entered GoPuff name, stripped of whitespace.
        """
        return self.gp_entry.get().strip() if self.gp_entry else ""

    def destroy(self) -> None:
        """Close and destroy the dialog."""
        if self.dialog:
            self.dialog.destroy()


# ====================================================================================================
# 8. TEST PAGE (FOR SELF-TEST)
# ----------------------------------------------------------------------------------------------------
# Simple page to launch the MFC Mappings dialog for testing.
# ====================================================================================================

class TestPage(PageProtocol):
    """Test page with button to launch the MFC Mappings dialog."""

    def __init__(self, controller: Any) -> None:
        """Store controller reference."""
        self.controller = controller
        self.root: Any = None

    def build(self, parent: WidgetType, params: Dict[str, Any]) -> WidgetType:
        """Build test page with dialog launcher button."""
        self.root = parent

        frame = make_frame(parent, padding="LG")
        frame.pack(fill="both", expand=True)

        # Title
        make_label(
            frame,
            text="Deliveroo MFC Dialogs - Design Preview",
            size="HEADING",
            bold=True,
        ).pack(pady=(0, SPACING_MD))

        # Instructions
        make_label(
            frame,
            text="Click a button below to preview the dialog design.",
            size="BODY",
        ).pack(pady=(0, SPACING_LG))

        # Button to open MFC Mappings dialog
        btn = make_button(
            frame,
            text="Open MFC Mappings Dialog",
            fg_colour="WHITE",
            bg_colour="PRIMARY",
            bg_shade="MID",
        )
        btn.configure(command=self._open_mappings_dialog)
        btn.pack(pady=SPACING_SM)

        return frame

    def _open_mappings_dialog(self) -> None:
        """Open the MFC Mappings dialog for preview."""
        dialog = MfcMappingsDialog()
        dialog.build(self.root)
        dialog.update_count(0)
        dialog.close_btn.configure(command=dialog.destroy)


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Expose dialog classes for use by controllers.
# ====================================================================================================

__all__ = [
    "MfcMappingsDialog",
    "MfcMappingEntryDialog",
    "UnmappedMfcDialog",
    "SetGopuffNameDialog",
]


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
# This section is the ONLY location where runtime execution should occur.
#
# NOTE: For production use, import the dialog classes and wire via G20b controller.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Launch the MFC Mappings dialog in standalone mode for layout preview.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - No event handlers are wired in this mode.
        - Use G20b controller for full functionality.
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

    app.register_page("main", TestPage)

    logger.info("Running in standalone mode (no controller wiring)")
    logger.info("=" * 60)

    app.run()


if __name__ == "__main__":
    init_logging()
    main()
