# ====================================================================================================
# {{FILENAME}}
# ----------------------------------------------------------------------------------------------------
# Page Controller Template — Business Logic Layer
#
# Purpose:
#   - Wire event handlers to widget references from G10a design.
#   - Implement business logic and data operations.
#   - Keep logic separate from presentation.
#
# Usage:
#   1. Copy this template and rename to match your G10a (e.g., G10b_users_controller.py).
#   2. Import your G10a design class.
#   3. Wire event handlers in the _wire_events() method.
#   4. Implement handler methods for each event.
#   5. Run this file as the application entry point.
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
# CONTROLLER LAYER POSITION:
#   G10b controllers wire event handlers to G10a design widgets.
#   Controllers own business logic; designs own presentation.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging, DEBUG
logger = get_logger(__name__)

# --- G02a: Type Aliases & Utilities (for controller wiring) ----------------------------------------
from gui.G02a_widget_primitives import (
    # Type aliases for event handlers and method signatures
    EventType, WidgetType,
    # Spacing tokens (for dynamic button creation in header_actions)
    SPACING_XS, SPACING_SM,
    # Widget factories (for dynamic content in controller)
    make_button,
)

# --- G04 Application Infrastructure -----------------------------------------------------------------
from gui.G04d_app_shell import AppShell

# --- Design Layer (UPDATE THIS IMPORT) --------------------------------------------------------------
from gui.{{DESIGN_MODULE}} import (
    TemplatePage,
    APP_TITLE,
    APP_VERSION,
    APP_AUTHOR,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    START_MAXIMIZED,
)


# ====================================================================================================
# 3. CONTROLLER CLASS
# ----------------------------------------------------------------------------------------------------
# The controller wraps the design page and wires event handlers.
#
# Pattern:
#   - Store reference to the design page instance.
#   - Wire events after build() completes (via after_build callback or manual wiring).
#   - Implement handler methods that access design.widget_name.
#
# Validation Pattern:
#   - Validation logic lives here, not in G10a.
#   - Use design's error labels to display messages.
#   - Return bool from validators for flow control.
# ====================================================================================================

class TemplatePageController:
    """
    Controller for TemplatePage — wires events and implements business logic.

    Description:
        Wraps the G10a design class, wires event handlers to widget references,
        and implements all business logic. The design layer remains pure presentation.

    Args:
        app: The AppShell instance for navigation and state access.

    Attributes:
        app: AppShell reference for navigation/state.
        page: TemplatePage design instance (set after build).

    Notes:
        - Wire events in _wire_events() after page.build() completes.
        - Access widgets via self.page.widget_name.
        - Access state via self.app.app_state.
        - Navigate via self.app.navigator.
    """

    def __init__(self, app: AppShell) -> None:
        """Store app reference; page reference set after build."""
        self.app = app
        self.page: TemplatePage | None = None

    def set_page(self, page: TemplatePage) -> None:
        """
        Store the page reference and wire events.

        Args:
            page: The TemplatePage design instance after build().
        """
        self.page = page
        self._wire_events()
        self._initialise_state()
        logger.info("[Controller] Page wired and initialised.")

    # ------------------------------------------------------------------------------------------------
    # EVENT WIRING
    # ------------------------------------------------------------------------------------------------

    def _wire_events(self) -> None:
        """Wire event handlers to design widget references."""
        if self.page is None:
            logger.warning("[Controller] Cannot wire events: page is None.")
            return

        # ----- Example: Header action buttons -----
        # The header_actions frame from make_page_header_with_actions can hold buttons.
        # Add buttons here and wire their commands:
        # if self.page.header_actions is not None:
        #     save_btn = make_button(self.page.header_actions, text="Save", ...)
        #     save_btn.configure(command=self._on_save)
        #     save_btn.pack(side="right", padx=SPACING_SM)

        # ----- Example: Button click -----
        if self.page.example_btn is not None:
            self.page.example_btn.configure(command=self._on_example_click)

        # ----- Example: Entry validation on focus out -----
        if self.page.example_entry is not None:
            self.page.example_entry.bind("<FocusOut>", self._on_example_validate)

        # ----- Example: Combobox selection -----
        # if self.page.some_combo is not None:
        #     self.page.some_combo.bind("<<ComboboxSelected>>", self._on_combo_select)

        # ----- Example: Checkbox toggle -----
        # if self.page.some_check_var is not None:
        #     self.page.some_check_var.trace_add("write", self._on_check_toggle)

        logger.debug("[Controller] Events wired.")

    # ------------------------------------------------------------------------------------------------
    # INITIALISATION
    # ------------------------------------------------------------------------------------------------

    def _initialise_state(self) -> None:
        """Set initial widget states after wiring."""
        if self.page is None:
            return

        # ----- Example: Set initial values -----
        # if self.page.example_var is not None:
        #     self.page.example_var.set("Initial value")

        # ----- Example: Disable a button until ready -----
        # if self.page.example_btn is not None:
        #     self.page.example_btn.configure(state="disabled")

        # ----- Example: Load data from app_state -----
        # saved_value = self.app.app_state.get_state("session_data").get("last_input", "")
        # if self.page.example_var is not None:
        #     self.page.example_var.set(saved_value)

        logger.debug("[Controller] Initial state set.")

    # ------------------------------------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------------------------------------

    def _on_example_click(self) -> None:
        """Handle example button click."""
        if self.page is None or self.page.example_var is None:
            return

        value = self.page.example_var.get()
        logger.info("[Controller] Button clicked with value: %s", value)

        # ----- Example: Validate before processing -----
        if not self._validate_example_input(value):
            return

        # ----- Example: Update status -----
        if self.page.status_label is not None:
            self.page.status_label.configure(text=f"Processed: {value}")

        # ----- Example: Save to app_state -----
        # session = self.app.app_state.get_state("session_data")
        # session["last_input"] = value
        # self.app.app_state.set_state("session_data", session)

        # ----- Example: Navigate to another page -----
        # self.app.navigator.navigate("results", params={"query": value})

    def _on_example_validate(self, event: EventType | None = None) -> None:
        """Handle example entry focus out — validate input."""
        if self.page is None or self.page.example_var is None:
            return

        value = self.page.example_var.get()
        self._validate_example_input(value)

    # ------------------------------------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------------------------------------

    def _validate_example_input(self, value: str) -> bool:
        """
        Validate example input.

        Args:
            value: The input string to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not value.strip():
            self._show_error("Input cannot be empty.")
            return False

        if len(value) < 3:
            self._show_error("Input must be at least 3 characters.")
            return False

        self._clear_error()
        return True

    def _show_error(self, message: str) -> None:
        """Display error message in status label."""
        if self.page is not None and self.page.status_label is not None:
            self.page.status_label.configure(text=f"Error: {message}", foreground="red")

    def _clear_error(self) -> None:
        """Clear error message from status label."""
        if self.page is not None and self.page.status_label is not None:
            self.page.status_label.configure(text="Status: Ready", foreground="green")

    # ------------------------------------------------------------------------------------------------
    # BUSINESS LOGIC
    # ------------------------------------------------------------------------------------------------

    # Add your business logic methods here.
    # Keep them separate from event handlers for testability.
    #
    # Example:
    # def _process_data(self, data: Dict[str, Any]) -> bool:
    #     """Process data and return success status."""
    #     try:
    #         # ... processing logic ...
    #         return True
    #     except Exception as exc:
    #         log_exception(exc, logger, "[Controller] Data processing failed")
    #         return False


# ====================================================================================================
# 4. CONTROLLED PAGE WRAPPER
# ----------------------------------------------------------------------------------------------------
# This wrapper class implements PageProtocol and connects the design to the controller.
# Register this class with AppShell, not the raw TemplatePage design.
# ====================================================================================================

class ControlledTemplatePage:
    """
    Wrapper that connects TemplatePage design to TemplatePageController.

    This class implements PageProtocol and should be registered with AppShell.
    It creates both the design and controller, wiring them together after build.
    """

    def __init__(self, controller: AppShell) -> None:
        """
        Create design and controller instances.

        Args:
            controller: The AppShell instance (passed by Navigator).
        """
        self.app = controller
        self.design = TemplatePage(controller=controller)
        self.controller = TemplatePageController(app=controller)

    def build(self, parent: WidgetType, params: Dict[str, Any]) -> WidgetType:
        """
        Build the page and wire the controller.

        Args:
            parent: Parent widget from AppShell.
            params: Navigation parameters.

        Returns:
            The root frame from the design.
        """
        frame = self.design.build(parent, params)
        self.controller.set_page(self.design)
        return frame


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Expose the controlled page for registration with AppShell.
# ====================================================================================================

__all__ = [
    "ControlledTemplatePage",
    "TemplatePageController",
]


# ====================================================================================================
# 99. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
# This is the production entry point. Run this file, not G10a.
# ====================================================================================================

def main() -> None:
    """
    Description:
        Launch the application with controller wiring.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - This is the production entry point.
        - Run this file instead of G10a for full functionality.
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

    # Register the CONTROLLED page (not raw TemplatePage)
    app.register_page("main", ControlledTemplatePage)

    # ----- Example: Register additional pages -----
    # app.register_page("settings", ControlledSettingsPage)
    # app.register_page("results", ControlledResultsPage)

    logger.info("Running with controller wiring")
    logger.info("=" * 60)

    app.run()


if __name__ == "__main__":
    init_logging()
    main()