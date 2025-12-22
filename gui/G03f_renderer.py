# ====================================================================================================
# G03f_renderer.py
# ----------------------------------------------------------------------------------------------------
# Page renderer (UI factory and mounting delegate) for the GUI framework.
#
# Purpose:
#   - Act as the sole point of instantiation for Page classes in the framework.
#   - Call page lifecycle methods (build) and mount the resulting UI frame into BaseWindow.
#   - Maintain the architectural boundary: G03 handles construction, G04 handles orchestration.
#   - Provide error page rendering for graceful failure recovery.
#
# Relationships:
#   - G02c_gui_base  → BaseWindow (implements WindowProtocol).
#   - G03f_renderer  → page instantiation and mounting (THIS MODULE).
#   - G04+           → orchestration layer (Navigator, Controllers).
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
# INHERITANCE CHAIN:
#   G03 modules import from G02a/G02b/G02c (the unified API layer).
#   G02a re-exports tokens from G01a/G01b, so G03 never imports G01 directly.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C01_logging_handler import get_logger, log_exception, init_logging, DEBUG
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from gui.G00a_gui_packages import tk, ttk


# ====================================================================================================
# 3. PROTOCOL DEFINITIONS
# ----------------------------------------------------------------------------------------------------
# Structural typing protocols for window and page interfaces.
# ====================================================================================================

class WindowProtocol(Protocol):
    """
    Protocol defining the window interface required by G03Renderer.

    Attributes:
        content_frame: The parent frame for page content.

    Methods:
        set_content: Mount a frame into the window's content area.
    """

    @property
    def content_frame(self) -> ttk.Frame:
        """Get the content frame where pages are mounted."""
        ...

    def set_content(self, frame: tk.Misc) -> None:
        """Mount a frame into the window's content area."""
        ...


class PageProtocol(Protocol):
    """
    Protocol defining the page interface expected by G03Renderer.

    Methods:
        __init__: Receives the controller for business logic delegation.
        build: Constructs and returns the page's UI frame.
    """

    def __init__(self, controller: Any) -> None:
        """Initialise the page with a controller reference."""
        ...

    def build(self, parent: tk.Misc, params: dict[str, Any]) -> tk.Misc:
        """Build the page UI and return the root frame."""
        ...


# ====================================================================================================
# 4. RENDERER CLASS
# ----------------------------------------------------------------------------------------------------
# Page instantiation and mounting delegate.
# ====================================================================================================

class G03Renderer:
    """
    Page renderer that instantiates pages, calls build(), and mounts into BaseWindow.

    This is the ONLY class allowed to instantiate Page classes or call page.build().
    Acts as the bridge between G03 (UI construction) and G04 (application orchestration).
    """

    def __init__(self) -> None:
        """Initialise the renderer with no window reference."""
        self._window: WindowProtocol | None = None
        logger.info("[G03f] Renderer initialised.")

    def set_window(self, window: WindowProtocol) -> None:
        """Inject the BaseWindow (or mock) into the renderer."""
        self._window = window
        logger.info("[G03f] Window reference injected.")

    def render_page(
        self,
        page_class: type[PageProtocol],
        controller: Any,
        params: dict[str, Any] | None = None,
    ) -> tk.Misc:
        """
        Description:
            Instantiate and mount a page into the window.

        Args:
            page_class: The Page class to instantiate (must implement PageProtocol).
            controller: The controller instance to pass to the page.
            params: Optional dictionary of parameters for page.build().

        Returns:
            tk.Misc: The frame returned by page.build(), for caching by Navigator.

        Raises:
            RuntimeError: If set_window() has not been called.

        Notes:
            Exceptions during page construction are logged and re-raised.
        """
        if self._window is None:
            raise RuntimeError(
                "Renderer must receive window via set_window() before rendering."
            )

        page_name = page_class.__name__

        try:
            logger.info("[G03f] Rendering page: %s", page_name)

            page_instance = page_class(controller)
            parent_frame = self._window.content_frame
            content_frame = page_instance.build(parent_frame, params or {})
            self._window.set_content(content_frame)

            logger.info("[G03f] Successfully mounted: %s", page_name)
            return content_frame

        except Exception as exc:
            log_exception(exc, logger, f"[G03f] Page render failure: {page_name}")
            raise

    def mount_cached_frame(self, frame: tk.Misc, page_name: str = "cached") -> None:
        """
        Description:
            Mount a previously-built frame without re-instantiation.

        Args:
            frame: The cached frame to mount.
            page_name: Name of the page for logging purposes.

        Returns:
            None.

        Raises:
            RuntimeError: If set_window() has not been called.

        Notes:
            Used by G04b Navigator for page caching.
        """
        if self._window is None:
            raise RuntimeError(
                "Renderer must receive window via set_window() before mounting."
            )

        logger.info("[G03f] Mounting cached frame: %s", page_name)
        self._window.set_content(frame)
        logger.info("[G03f] Cached frame mounted: %s", page_name)

    def render_error_page(
        self,
        error_page_class: type[PageProtocol],
        controller: Any,
        message: str,
    ) -> None:
        """
        Description:
            Render a fallback error page when the main page fails.

        Args:
            error_page_class: The ErrorPage class to instantiate.
            controller: The controller instance to pass to the error page.
            message: Error message to display on the error page.

        Returns:
            None.

        Raises:
            RuntimeError: If set_window() has not been called.

        Notes:
            If error page itself fails, logs failure but does not re-raise.
        """
        if self._window is None:
            raise RuntimeError(
                "Renderer must receive window via set_window() before rendering."
            )

        page_name = error_page_class.__name__

        try:
            logger.error("[G03f] Mounting error page: %s (reason: %s)", page_name, message[:100])

            error_page_instance = error_page_class(controller)
            parent_frame = self._window.content_frame
            error_frame = error_page_instance.build(parent_frame, {"message": message})
            self._window.set_content(error_frame)

            logger.error("[G03f] Error page mounted successfully: %s", page_name)

        except Exception as exc:
            log_exception(exc, logger, "[G03f] FATAL: Error page rendering failed")


# ====================================================================================================
# 98. PUBLIC API SURFACE
# ----------------------------------------------------------------------------------------------------
# Expose renderer and protocol definitions.
# ====================================================================================================

__all__ = [
    "G03Renderer",
    "WindowProtocol",
    "PageProtocol",
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
        Self-test / smoke test for G03f_renderer module.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Tests renderer without Tk using mock objects.
        - Validates protocol compliance and error handling.
    """
    logger.info("=" * 60)
    logger.info("[G03f] Running Renderer smoke test (non-Tk)")
    logger.info("=" * 60)

    class MockFrame:
        """Mock frame for testing without Tk."""
        pass

    class MockWindow:
        """Mock window implementing WindowProtocol."""
        def __init__(self) -> None:
            self._content_frame = MockFrame()
            self.last_content: Any = None
            self.set_content_call_count: int = 0

        @property
        def content_frame(self) -> MockFrame:  # type: ignore[override]
            return self._content_frame

        def set_content(self, frame: Any) -> None:
            self.last_content = frame
            self.set_content_call_count += 1
            logger.info("[MockWindow] set_content() called (count: %d)", self.set_content_call_count)

    class MockPage:
        """Mock page implementing PageProtocol."""
        def __init__(self, controller: Any) -> None:
            self.controller = controller
            logger.info("[MockPage] __init__ called with controller: %s", controller)

        def build(self, parent: Any, params: dict[str, Any]) -> MockFrame:  # type: ignore[override]
            logger.info("[MockPage] build() called with params: %s", params)
            return MockFrame()

    class MockErrorPage:
        """Mock error page for testing error rendering."""
        def __init__(self, controller: Any) -> None:
            self.controller = controller

        def build(self, parent: Any, params: dict[str, Any]) -> MockFrame:  # type: ignore[override]
            logger.info("[MockErrorPage] build() called with message: %s", params.get("message", ""))
            return MockFrame()

    class FailingPage:
        """Mock page that raises during build()."""
        def __init__(self, controller: Any) -> None:
            pass

        def build(self, parent: Any, params: dict[str, Any]) -> MockFrame:  # type: ignore[override]
            raise ValueError("Intentional test failure")

    try:
        renderer = G03Renderer()

        logger.info("[Test 1] Attempting render without window...")
        try:
            renderer.render_page(MockPage, controller=None)  # type: ignore[arg-type]
            logger.error("[Test 1] FAILED - should have raised RuntimeError")
        except RuntimeError as e:
            logger.info("[Test 1] PASSED - got expected RuntimeError: %s", e)

        logger.info("[Test 2] Setting window and rendering page...")
        mock_window = MockWindow()
        renderer.set_window(mock_window)  # type: ignore[arg-type]
        renderer.render_page(MockPage, controller="TestController", params={"key": "value"})  # type: ignore[arg-type]

        assert mock_window.set_content_call_count == 1
        assert mock_window.last_content is not None
        logger.info("[Test 2] PASSED - page rendered successfully")

        logger.info("[Test 3] Rendering error page...")
        renderer.render_error_page(MockErrorPage, controller=None, message="Something went wrong")  # type: ignore[arg-type]

        assert mock_window.set_content_call_count == 2
        logger.info("[Test 3] PASSED - error page rendered successfully")

        logger.info("[Test 4] Testing page that fails during build()...")
        logger.info("[Test 4] NOTE: The following traceback is EXPECTED (testing error propagation)")
        try:
            renderer.render_page(FailingPage, controller=None)  # type: ignore[arg-type]
            logger.error("[Test 4] FAILED - should have raised ValueError")
        except ValueError:
            logger.info("[Test 4] PASSED - exception propagated correctly")

        logger.info("[Test 5] Testing mount_cached_frame()...")
        cached_frame = MockFrame()
        renderer.mount_cached_frame(cached_frame, page_name="CachedTestPage")  # type: ignore[arg-type]
        assert mock_window.set_content_call_count == 3
        assert mock_window.last_content is cached_frame
        logger.info("[Test 5] PASSED - cached frame mounted successfully")

        logger.info("=" * 60)
        logger.info("[G03f] All smoke tests PASSED (5 tests, 5 assertions)")
        logger.info("=" * 60)

    except Exception as exc:
        log_exception(exc, logger, "[G03f] Smoke test failure")
        sys.exit(1)


if __name__ == "__main__":
    init_logging()
    main()