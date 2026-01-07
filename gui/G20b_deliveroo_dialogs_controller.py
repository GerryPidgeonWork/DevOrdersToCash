# ====================================================================================================
# G20b_deliveroo_dialogs_controller.py
# ----------------------------------------------------------------------------------------------------
# Deliveroo MFC Dialogs — Controller Layer
#
# Purpose:
#   - Wire event handlers to G20a dialog widget references.
#   - Implement business logic for MFC mapping dialogs.
#   - Keep logic separate from presentation.
#
# Usage:
#   1. Import controller functions from this module.
#   2. Call show_mfc_mappings_dialog(parent, drive_root, log_callback) from G10b.
#   3. Call show_unmapped_mfc_dialog(parent, unmapped, reference_folder) when needed.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-01-06
# Project:      GUI Framework v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

if "" in sys.path:
    sys.path.remove("")

sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

from core.C01_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- G02a: Widget Primitives (for dialog utilities) ------------------------------------------------
from gui.G02a_widget_primitives import (
    ask_yes_no,
    show_warning,
    show_error,
)

# --- G03d: Table Patterns --------------------------------------------------------------------------
from gui.G03d_table_patterns import (
    insert_rows_zebra,
    get_selected_values,
)

# --- G20a: Dialog Designs --------------------------------------------------------------------------
from gui.G20a_deliveroo_dialogs_design import (
    MfcMappingsDialog,
    MfcMappingEntryDialog,
    UnmappedMfcDialog,
    SetGopuffNameDialog,
)


# ====================================================================================================
# 3. MFC MAPPINGS DIALOG CONTROLLER
# ----------------------------------------------------------------------------------------------------
# Opens a modal dialog for viewing/editing Deliveroo → GoPuff MFC name mappings.
# All wiring is done here (strict compliance - no wire_events in design).
# ====================================================================================================

def show_mfc_mappings_dialog(
    parent: Any,
    drive_root: str,
    log_callback: Callable[[str], None] | None = None,
) -> None:
    """Show the MFC Mappings dialog for managing Deliveroo → GoPuff mappings.

    Description:
        Opens a modal dialog showing current mappings with Add/Edit/Delete functionality.
        Changes are saved immediately to the CSV file on the shared drive.

    Args:
        parent: Parent widget (dialog will be modal to this).
        drive_root: Google Drive root path (e.g., "H:").
        log_callback: Optional callback to log messages to console.

    Returns:
        None.

    Raises:
        None (errors shown via dialog).
    """
    from implementation.I01_project_set_file_paths import initialise_provider_paths, get_provider_paths
    from implementation.I02_project_shared_functions import load_mfc_mapping, save_mfc_mapping

    def log(message: str) -> None:
        """Log message via callback if provided."""
        if log_callback:
            log_callback(message)
        logger.info(message)

    # 1. Check Google Drive is selected
    if not drive_root:
        show_warning("Please select a Google Drive account first.")
        return

    # 2. Get reference folder path
    initialise_provider_paths(drive_root)
    provider_paths = get_provider_paths("deliveroo")

    if not provider_paths:
        show_error("Failed to initialise Deliveroo paths.")
        return

    reference_folder = provider_paths.get("01_csvs_03_reference")
    if not reference_folder:
        show_error("Reference folder path not configured.\nExpected: 01 CSVs/03 Reference")
        return

    # 3. Load current mappings
    mappings = load_mfc_mapping(reference_folder)

    # 4. Create dialog design
    dialog_design = MfcMappingsDialog()
    dialog_design.build(parent)

    # ------------------------------------------------------------------------------------------------
    # HELPER FUNCTIONS
    # ------------------------------------------------------------------------------------------------

    def refresh_table() -> None:
        """Clear and repopulate the table with zebra striping."""
        rows = [(dr_name, gp_name) for dr_name, gp_name in sorted(mappings.items())]
        insert_rows_zebra(dialog_design.tree, rows, clear_existing=True)
        dialog_design.update_count(len(mappings))

    # ------------------------------------------------------------------------------------------------
    # BUTTON HANDLERS
    # ------------------------------------------------------------------------------------------------

    def on_add() -> None:
        """Open entry dialog to add a new mapping."""
        entry_design = MfcMappingEntryDialog()
        entry_design.build(dialog_design.dialog, title="Add MFC Mapping")

        def do_save() -> None:
            dr_name, gp_name = entry_design.get_values()
            if not dr_name or not gp_name:
                show_warning("Both fields are required.", title="Validation", parent=entry_design.dialog)
                return

            mappings[dr_name] = gp_name
            if save_mfc_mapping(reference_folder, mappings):
                refresh_table()
                log(f"MFC Mapping added: {dr_name} → {gp_name}")
                entry_design.destroy()
            else:
                show_error("Failed to save mapping.", title="Error", parent=entry_design.dialog)

        # Wire entry dialog (strict compliance - wiring in controller)
        entry_design.save_btn.configure(command=do_save)
        entry_design.cancel_btn.configure(command=entry_design.destroy)

    def on_edit() -> None:
        """Open entry dialog to edit the selected mapping."""
        selected = get_selected_values(dialog_design.tree)
        if not selected:
            show_warning("Please select a mapping to edit.", title="Selection", parent=dialog_design.dialog)
            return

        old_dr_name = selected[0][0]
        old_gp_name = selected[0][1]

        entry_design = MfcMappingEntryDialog()
        entry_design.build(
            dialog_design.dialog,
            title="Edit MFC Mapping",
            initial_dr_name=old_dr_name,
            initial_gp_name=old_gp_name,
        )

        def do_save() -> None:
            new_dr_name, new_gp_name = entry_design.get_values()
            if not new_dr_name or not new_gp_name:
                show_warning("Both fields are required.", title="Validation", parent=entry_design.dialog)
                return

            # Remove old mapping if key changed
            if new_dr_name != old_dr_name and old_dr_name in mappings:
                del mappings[old_dr_name]

            mappings[new_dr_name] = new_gp_name

            if save_mfc_mapping(reference_folder, mappings):
                refresh_table()
                log(f"MFC Mapping updated: {new_dr_name} → {new_gp_name}")
                entry_design.destroy()
            else:
                show_error("Failed to save mapping.", title="Error", parent=entry_design.dialog)

        # Wire entry dialog
        entry_design.save_btn.configure(command=do_save)
        entry_design.cancel_btn.configure(command=entry_design.destroy)

    def on_delete() -> None:
        """Delete the selected mapping."""
        selected = get_selected_values(dialog_design.tree)
        if not selected:
            show_warning("Please select a mapping to delete.", title="Selection", parent=dialog_design.dialog)
            return

        dr_name = selected[0][0]

        if ask_yes_no("Confirm Delete", f"Delete mapping for '{dr_name}'?", parent=dialog_design.dialog):
            if dr_name in mappings:
                del mappings[dr_name]
                if save_mfc_mapping(reference_folder, mappings):
                    refresh_table()
                    log(f"MFC Mapping deleted: {dr_name}")
                else:
                    show_error("Failed to save after deletion.", title="Error", parent=dialog_design.dialog)

    # ------------------------------------------------------------------------------------------------
    # WIRE EVENTS (strict compliance - all wiring in controller)
    # ------------------------------------------------------------------------------------------------

    dialog_design.add_btn.configure(command=on_add)
    dialog_design.edit_btn.configure(command=on_edit)
    dialog_design.delete_btn.configure(command=on_delete)
    dialog_design.close_btn.configure(command=dialog_design.destroy)

    # Double-click to edit
    dialog_design.tree.bind("<Double-1>", lambda e: on_edit())

    # Initial table load
    refresh_table()

    log(f"MFC Mappings dialog opened ({len(mappings)} mappings)")


# ====================================================================================================
# 4. UNMAPPED MFC DIALOG CONTROLLER
# ----------------------------------------------------------------------------------------------------
# Shows dialog prompting user to map unmapped MFC names before processing.
# ====================================================================================================

def show_unmapped_mfc_dialog(
    parent: Any,
    unmapped: List[str],
    reference_folder: Path,
) -> bool:
    """Show dialog prompting user to map unmapped MFC names.

    Description:
        Displays a modal dialog with all unmapped Deliveroo restaurant names.
        User must provide GoPuff name for each before continuing.

    Args:
        parent: Parent widget (dialog will be modal to this).
        unmapped: List of unmapped Deliveroo restaurant names.
        reference_folder: Path to save updated mappings.

    Returns:
        bool: True if all mappings were provided, False if cancelled.
    """
    from implementation.I02_project_shared_functions import load_mfc_mapping, save_mfc_mapping

    # Load existing mappings to add to
    mappings = load_mfc_mapping(reference_folder)

    # Track pending mappings (initially all unmapped have empty GoPuff name)
    pending_mappings: Dict[str, str] = {name: "" for name in unmapped}

    # Create dialog design
    dialog_design = UnmappedMfcDialog()
    dialog_design.build(parent, unmapped_count=len(unmapped))

    # ------------------------------------------------------------------------------------------------
    # HELPER FUNCTIONS
    # ------------------------------------------------------------------------------------------------

    def refresh_table() -> None:
        """Clear and repopulate the table with zebra striping."""
        rows = [(dr_name, gp_name or "(not set)") for dr_name, gp_name in sorted(pending_mappings.items())]
        insert_rows_zebra(dialog_design.tree, rows, clear_existing=True)

        # Count how many are still unmapped
        remaining = sum(1 for v in pending_mappings.values() if not v)
        dialog_design.update_status(remaining)

    # ------------------------------------------------------------------------------------------------
    # BUTTON HANDLERS
    # ------------------------------------------------------------------------------------------------

    def on_set_name() -> None:
        """Open dialog to set GoPuff name for selected row."""
        selected = get_selected_values(dialog_design.tree)
        if not selected:
            show_warning("Please select a row to map.", title="Selection", parent=dialog_design.dialog)
            return

        dr_name = selected[0][0]
        current_gp = pending_mappings.get(dr_name, "")
        if current_gp == "(not set)":
            current_gp = ""

        input_design = SetGopuffNameDialog()
        input_design.build(dialog_design.dialog, deliveroo_name=dr_name, initial_value=current_gp)

        def do_save() -> None:
            gp_name = input_design.get_value()
            if not gp_name:
                show_warning("GoPuff name is required.", title="Validation", parent=input_design.dialog)
                return

            pending_mappings[dr_name] = gp_name
            refresh_table()
            input_design.destroy()

        # Wire input dialog
        input_design.save_btn.configure(command=do_save)
        input_design.cancel_btn.configure(command=input_design.destroy)
        input_design.gp_entry.bind("<Return>", lambda e: do_save())

    def on_continue() -> None:
        """Save all mappings and close dialog."""
        for dr_name, gp_name in pending_mappings.items():
            if gp_name:
                mappings[dr_name] = gp_name

        if save_mfc_mapping(reference_folder, mappings):
            dialog_design.set_completed(True)
            dialog_design.destroy()
        else:
            show_error("Failed to save mappings.", title="Error", parent=dialog_design.dialog)

    def on_cancel() -> None:
        """Cancel without saving."""
        dialog_design.set_completed(False)
        dialog_design.destroy()

    # ------------------------------------------------------------------------------------------------
    # WIRE EVENTS (strict compliance - all wiring in controller)
    # ------------------------------------------------------------------------------------------------

    dialog_design.set_btn.configure(command=on_set_name)
    dialog_design.continue_btn.configure(command=on_continue)
    dialog_design.cancel_btn.configure(command=on_cancel)

    # Double-click to set name
    dialog_design.tree.bind("<Double-1>", lambda e: on_set_name())

    # Initial table load
    refresh_table()

    # Wait for dialog to close and return result
    return dialog_design.wait_for_close()


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
__all__ = [
    "show_mfc_mappings_dialog",
    "show_unmapped_mfc_dialog",
]


# ====================================================================================================
# 99. MAIN EXECUTION / SELF-TEST
# ----------------------------------------------------------------------------------------------------
def main() -> None:
    """
    Description:
        Self-test for G20b controller functions.

    Args:
        None.

    Returns:
        None.

    Notes:
        - For full testing, use the main application (G10b).
        - This test provides basic dialog preview with wired buttons.
    """
    import tkinter as tk
    from gui.G02a_widget_primitives import init_gui_theme

    logger.info("=" * 60)
    logger.info("G20b Deliveroo Dialogs Controller - Self Test")
    logger.info("=" * 60)

    # Create test root window
    root = tk.Tk()
    root.title("G20b Controller Test")
    root.geometry("400x150")

    # Initialize GUI theme
    init_gui_theme()

    def log_to_console(message: str) -> None:
        """Test log callback."""
        logger.info("[Console] %s", message)

    def test_mappings_dialog() -> None:
        """Open MFC Mappings dialog (requires valid drive path)."""
        show_warning("This test requires a valid Google Drive path.\nIn production, this is called from G10b.")

    tk.Label(root, text="G20b Controller Test", font=("Segoe UI", 12, "bold")).pack(pady=10)
    tk.Label(root, text="Controller functions are designed to be called from G10b.").pack(pady=5)
    tk.Button(root, text="Test Info", command=test_mappings_dialog).pack(pady=10)

    logger.info("Test window ready")
    root.mainloop()


if __name__ == "__main__":
    init_logging()
    main()
