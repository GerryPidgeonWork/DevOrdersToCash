# GUI Orchestration Documentation

> **Layer:** G04 (Application Infrastructure)  
> **Status:** Complete and Stable  
> **Last Updated:** 2026-01-01

> ⚠️ **Import Rule:** Pages import from G02a only (widgets, tokens, types). Never import directly from G01 modules. Never use raw `ttk.Frame`/`ttk.Label` — use `make_frame()`/`make_label()` from G02a.

---

## 1. Layer Overview

G04 provides **application infrastructure** — the orchestration layer that wires together UI patterns (G03), manages navigation, maintains state, and provides the application entry point.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          G04d AppShell                              │
│              (top-level orchestrator, owns root window)             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │
│  │  G04a State   │  │  G04b Nav     │  │  G04c Menu    │           │
│  │  (AppState)   │◄─┤  (Navigator)  │  │  (AppMenu)    │           │
│  └───────────────┘  └───────┬───────┘  └───────┬───────┘           │
│                             │                   │                   │
│                             ▼                   │                   │
│                    ┌─────────────────┐          │                   │
│                    │  G03f Renderer  │◄─────────┘                   │
│                    └────────┬────────┘                              │
│                             │                                       │
│              ┌──────────────┼──────────────┐                       │
│              ▼              ▼              ▼                       │
│         PageClass      PageClass      PageClass                    │
│         (G10+ pages implementing PageProtocol)                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Principles:**

- **AppShell owns everything** — creates and wires all components
- **Navigator owns routing** — page registration, history, caching
- **AppState owns data** — schema-validated, serialisable state
- **AppMenu owns chrome** — menu bar, keyboard shortcuts
- **Renderer owns mounting** — page instantiation via PageProtocol
- **Pages own nothing** — they receive controller, build UI, return frame

---

## 2. Module Reference

### G04a_app_state
**Purpose:** Centralised, schema-validated application state.

| Export | Type | Description |
|--------|------|-------------|
| `AppState` | class | State manager with get/set/update |
| `StateSchemaType` | type alias | Schema definition type |

**Key Methods:**

| Method | Description |
|--------|-------------|
| `get_state(key)` | Get value (validates key) |
| `set_state(key, value)` | Set value (validates key + type) |
| `update_state(**kwargs)` | Bulk update multiple keys |
| `reset_state()` | Reset all to defaults |
| `extend_schema(keys)` | Add custom keys at runtime |
| `save_to_json(path)` | Persist state to file |
| `load_from_json(path)` | Restore state from file |
| `snapshot()` | Get shallow copy of state dict |
| `diff_state(other)` | Compare against another state |

**Default Schema:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `current_page` | str \| None | None | Currently displayed page |
| `previous_page` | str \| None | None | Previously displayed page |
| `navigation_history` | list | [] | Full navigation stack |
| `history_index` | int | -1 | Current position in history |
| `theme` | str | "default" | Active theme name |
| `debug_mode` | bool | False | Debug mode flag |
| `session_data` | dict | {} | Arbitrary session storage |

---

### G04b_navigator
**Purpose:** Page routing with history and caching.

| Export | Type | Description |
|--------|------|-------------|
| `Navigator` | class | Routing and history controller |
| `NavigationEntry` | dataclass | History entry (page_name, params) |

**Key Methods:**

| Method | Description |
|--------|-------------|
| `register_page(name, class)` | Register a page class |
| `is_registered(name)` | Check if page exists |
| `navigate(name, params, ...)` | Navigate to page |
| `back()` | Go to previous in history |
| `forward()` | Go to next in history |
| `reload()` | Reload current page (bypass cache) |
| `clear_cache(name)` | Clear cached page(s) |
| `current_page()` | Get current page name |
| `previous_page()` | Get previous page name |
| `registered_pages()` | List all registered names |

**Navigation Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | required | Registered page name |
| `params` | dict | {} | Parameters for page.build() |
| `force_reload` | bool | False | Bypass cache |
| `add_to_history` | bool | True | Add to history stack |

---

### G04c_app_menu
**Purpose:** Standard menu bar with navigation integration.

| Export | Type | Description |
|--------|------|-------------|
| `AppMenu` | class | Menu bar controller |
| `DEFAULT_APP_NAME` | str | Default app name |
| `DEFAULT_APP_VERSION` | str | Default version |
| `DEFAULT_APP_AUTHOR` | str | Default author |
| `DEFAULT_APP_YEAR` | str | Default copyright year |

**Built-in Menus:**

| Menu | Items | Shortcuts |
|------|-------|-----------|
| **File** | Exit | Ctrl+Q |
| **View** | Home, Back, Forward, Reload | Ctrl+H, Alt+←, Alt+→, Ctrl+R |
| **Help** | About | — |

**Customisation Methods:**

| Method | Description |
|--------|-------------|
| `add_menu(label)` | Add custom menu, returns tk.Menu |
| `add_command_to_file_menu(...)` | Insert command before Exit |

---

### G04d_app_shell
**Purpose:** Top-level orchestrator and application entry point.

| Export | Type | Description |
|--------|------|-------------|
| `AppShell` | class | Application orchestrator |
| `DEFAULT_TITLE` | str | Default window title |
| `DEFAULT_WIDTH` | int | Default width (1024) |
| `DEFAULT_HEIGHT` | int | Default height (768) |
| `DEFAULT_MIN_WIDTH` | int | Minimum width (800) |
| `DEFAULT_MIN_HEIGHT` | int | Minimum height (600) |

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | str | "GUI Framework..." | Window title |
| `width` | int | 1024 | Initial width |
| `height` | int | 768 | Initial height |
| `min_width` | int | 800 | Minimum width |
| `min_height` | int | 600 | Minimum height |
| `app_name` | str | title | Name for About dialog |
| `app_version` | str | "1.0.0" | Version for About |
| `app_author` | str | "Unknown" | Author for About |
| `enable_cache` | bool | True | Enable page caching |
| `start_page` | str | "home" | Initial page name |
| `start_maximized` | bool | False | Start maximized |
| `bg_colour` | str | None | Background hex colour |

**Accessor Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `root` | tk.Tk | Root Tk window |
| `window` | BaseWindow | BaseWindow instance |
| `app_state` | AppState | State manager |
| `navigator` | Navigator | Routing controller |
| `menu` | AppMenu | Menu bar |
| `content_frame` | ttk.Frame | Page mount target |

---

## 3. Component Wiring

AppShell creates and wires all components in a specific order:

```python
# 1. Create window (G02c)
self._window = BaseWindow(title, width, height, ...)

# 2. Create state (G04a)
self._app_state = AppState()

# 3. Create renderer (G03f) and inject window
self._renderer = G03Renderer()
self._renderer.set_window(self)  # AppShell implements WindowProtocol

# 4. Create navigator (G04b) with renderer + state
self._navigator = Navigator(
    renderer=self._renderer,
    app_state=self._app_state,
    enable_cache=enable_cache,
)
self._navigator.set_controller(self)  # Pages receive AppShell as controller

# 5. Create menu (G04c) with navigator
self._menu = AppMenu(
    root=self._root,
    navigator=self._navigator,
    app_state=self._app_state,
    ...
)
```

**Dependency Graph:**

```
BaseWindow ◄─── AppShell (owns)
                    │
                    ├──► AppState (creates)
                    │
                    ├──► G03Renderer (creates, injects self)
                    │         │
                    │         ▼
                    ├──► Navigator (creates, passes renderer + state)
                    │         │
                    │         ▼
                    └──► AppMenu (creates, passes navigator)
```

---

## 4. Navigation Lifecycle

### Page Registration

```python
app = AppShell(title="My App", start_page="home")
app.register_page("home", HomePage)
app.register_page("settings", SettingsPage)
app.register_page("users", UsersPage)
app.run()
```

### Navigation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. navigator.navigate("settings", params={"tab": "display"})       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Navigator checks cache (if enabled + not force_reload)          │
│    - If cached: renderer.mount_cached_frame(frame)                 │
│    - If not: renderer.render_page(SettingsPage, controller, params)│
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Renderer instantiates page: page = SettingsPage(controller)     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Renderer calls build: frame = page.build(parent, params)        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Renderer mounts: window.set_content(frame)                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Navigator updates history + app_state                           │
└─────────────────────────────────────────────────────────────────────┘
```

### History Navigation

```python
# Back/Forward use cached params
navigator.back()    # Goes to previous, doesn't add to history
navigator.forward() # Goes to next, doesn't add to history

# New navigation truncates forward history
# History: [home, settings, users] at index 2
navigator.back()  # Now at index 1 (settings)
navigator.navigate("profile")  # Truncates: [home, settings, profile]
```

---

## 5. State Management

### Reading State

```python
# In a page or controller
current = self.controller.app_state.get_state("current_page")
debug = self.controller.app_state.get_state("debug_mode")
```

### Writing State

```python
# Single value
self.controller.app_state.set_state("theme", "dark")

# Multiple values
self.controller.app_state.update_state(
    theme="dark",
    debug_mode=True,
)
```

### Extending Schema

```python
# Add application-specific keys
app.app_state.extend_schema({
    "user_id": ((str, type(None)), None),
    "preferences": ((dict,), {}),
    "last_sync": ((str, type(None)), None),
})
```

### Session Persistence

```python
# Save on exit
app.app_state.save_to_json("session.json")

# Restore on startup
app.app_state.load_from_json("session.json")
```

---

## 6. Menu Customisation

### Adding a Custom Menu

```python
app = AppShell(...)

# Add Tools menu
tools = app.menu.add_menu("Tools")
tools.add_command(label="Export Data", command=on_export)
tools.add_command(label="Import Data", command=on_import)
tools.add_separator()
tools.add_command(label="Preferences", command=on_preferences)
```

### Adding to File Menu

```python
# Add Save before Exit
app.menu.add_command_to_file_menu(
    label="Save",
    command=on_save,
    accelerator="Ctrl+S",
)

# Note: You must bind the accelerator manually
app.root.bind_all("<Control-s>", lambda e: on_save())
```

---

## 7. Usage Examples

### Minimal Application

```python
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_frame, page_title

class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params):
        frame = make_frame(parent, padding="MD")
        page_title(frame, text="Hello World").pack(expand=True)
        return frame

app = AppShell(title="My App")
app.register_page("home", HomePage)
app.run()
```

### Canonical Pattern-Compliant Page

This is the **gold-standard** structure for production pages using G02/G03 patterns:

```python
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_button, SPACING_MD
from gui.G03a_layout_patterns import page_layout
from gui.G03b_container_patterns import make_page_header_with_actions, make_titled_card

class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params):
        # 1. Create page container with standard padding
        page = page_layout(parent, padding=SPACING_MD)
        page.pack(fill="both", expand=True)
        
        # 2. Page header with actions area
        header, actions = make_page_header_with_actions(
            page, title="Dashboard", subtitle="Welcome back"
        )
        header.pack(fill="x", pady=(0, SPACING_MD))
        
        # 3. Action buttons in header
        make_button(
            actions, text="Settings", bg_colour="SECONDARY",
            command=lambda: self.controller.navigator.navigate("settings")
        ).pack(side="left")
        
        # 4. Content in titled cards
        card, card_content = make_titled_card(page, title="Quick Stats")
        card.pack(fill="x")
        
        # ... add content to card_content ...
        
        return page

app = AppShell(title="My App", start_page="home")
app.register_page("home", HomePage)
app.run()
```

### Multi-Page Application

```python
from gui.G04d_app_shell import AppShell
from gui.G02a_widget_primitives import make_frame, make_button, SPACING_MD
from gui.G03b_container_patterns import make_page_header_with_actions

class HomePage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params):
        frame = make_frame(parent, padding="MD")
        
        header, actions = make_page_header_with_actions(
            frame, title="Dashboard", subtitle="Welcome back"
        )
        header.pack(fill="x")
        
        make_button(
            actions, text="Settings",
            command=lambda: self.controller.navigator.navigate("settings")
        ).pack(side="left")
        
        # ... more UI
        return frame

class SettingsPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params):
        frame = make_frame(parent, padding="MD")
        
        tab = params.get("tab", "general")
        # Build settings UI based on tab...
        
        return frame

app = AppShell(
    title="My Application",
    app_name="My App",
    app_version="2.0.0",
    start_page="home",
)

app.register_page("home", HomePage)
app.register_page("settings", SettingsPage)

# Add custom menu
tools = app.menu.add_menu("Tools")
tools.add_command(label="Clear Cache", command=lambda: app.navigator.clear_cache())

app.run()
```

### Passing Parameters Between Pages

```python
class UsersPage:
    def build(self, parent, params):
        # ... show user list
        
        def on_edit(user_id):
            self.controller.navigator.navigate(
                "user_detail",
                params={"user_id": user_id, "mode": "edit"}
            )
        
        # ... button with on_edit callback

class UserDetailPage:
    def build(self, parent, params):
        user_id = params.get("user_id")
        mode = params.get("mode", "view")
        
        # Load and display user based on params
```

---

## 8. Architectural Invariants

G04 enforces strict boundaries for clean orchestration:

**1. AppShell is the only entry point**
Applications create one AppShell and call `run()`. No other module starts `mainloop()`.

```python
# ✅ Correct
app = AppShell(...)
app.run()

# ❌ Wrong - don't call mainloop elsewhere
root = tk.Tk()
root.mainloop()
```

**2. Pages receive controller, not components**
Pages get a single controller reference (AppShell). They access navigator/state through it.

```python
# ✅ Correct
class MyPage:
    def __init__(self, controller):
        self.controller = controller
    
    def on_save(self):
        self.controller.navigator.navigate("home")
        self.controller.app_state.set_state("saved", True)

# ❌ Wrong - don't pass multiple references
class MyPage:
    def __init__(self, navigator, app_state, menu):  # Wrong!
        ...
```

**3. Navigation always goes through Navigator**
Never call `renderer.render_page()` directly. Navigator manages history and caching.

```python
# ✅ Correct
self.controller.navigator.navigate("settings")

# ❌ Wrong - bypasses history and caching
self.controller._renderer.render_page(SettingsPage, ...)
```

**4. State access is schema-safe**
All state keys must be declared. AppState rejects unknown keys.

```python
# ✅ Correct - extend schema first
app.app_state.extend_schema({
    "custom_key": ((str,), "default")
})
app.app_state.set_state("custom_key", "value")

# ❌ Wrong - undeclared key
app.app_state.set_state("random_key", "value")  # Raises KeyError
```

**5. Menu commands delegate to Navigator**
Menu handlers call navigator methods, not renderer directly.

```python
# ✅ Correct (built into AppMenu)
def _on_back(self):
    self._navigator.back()

# ❌ Wrong
def _on_back(self):
    self._renderer.mount_cached_frame(...)  # Bypasses Navigator
```

**6. G04 never creates widgets**
G04 modules orchestrate — they don't build UI. All widget creation happens through G02/G03. The only exception is AppMenu using `tk.Menu` for the native menu bar.

```python
# ✅ Correct - pages use G02/G03 patterns
from gui.G02a_widget_primitives import make_button
from gui.G03b_container_patterns import make_card

# ❌ Wrong - G04 modules creating widgets
class Navigator:
    def show_loading(self):
        ttk.Label(self._root, text="Loading...")  # Wrong! G04 doesn't build UI
```

---

## 9. WindowProtocol Implementation

AppShell implements `WindowProtocol` from G03f, enabling the Renderer to mount pages:

```python
class AppShell:
    @property
    def content_frame(self) -> ttk.Frame:
        """Get the frame where pages mount."""
        return self._content_frame

    def set_content(self, frame: tk.Misc) -> None:
        """Mount a page frame — hides existing, packs new."""
        # Hide all existing children
        for child in self._content_frame.winfo_children():
            child.pack_forget()
            child.grid_forget()
            child.place_forget()
        
        # Pack new frame
        frame.pack(in_=self._content_frame, fill=tk.BOTH, expand=True)
```

This separation means:
- **Renderer knows how to build** — instantiate, call build(), mount
- **AppShell knows where to mount** — owns content_frame, implements set_content()
- **Navigator knows when to build** — routing decisions, cache checks

---

## 10. Quick Reference

### Application Startup

```python
from gui.G04d_app_shell import AppShell

app = AppShell(title="My App", start_page="home")
app.register_page("home", HomePage)
app.register_page("settings", SettingsPage)
app.run()
```

### Page Template

```python
from gui.G02a_widget_primitives import make_frame

class MyPage:
    def __init__(self, controller):
        self.controller = controller
    
    def build(self, parent, params):
        frame = make_frame(parent, padding="MD")
        # Build UI using G02a/G03 patterns...
        return frame
```

### Navigation

```python
# Navigate with params
self.controller.navigator.navigate("page", params={"key": "value"})

# History navigation
self.controller.navigator.back()
self.controller.navigator.forward()

# Reload (bypasses cache)
self.controller.navigator.reload()
```

### State Access

```python
# Read
value = self.controller.app_state.get_state("key")

# Write
self.controller.app_state.set_state("key", value)

# Bulk update
self.controller.app_state.update_state(key1=val1, key2=val2)
```

### Component Access from Pages

```python
self.controller.navigator      # Navigator instance
self.controller.app_state      # AppState instance
self.controller.menu           # AppMenu instance
self.controller.root           # tk.Tk root window
self.controller.window         # BaseWindow instance
```

---

## 11. Import Patterns

### For Application Entry Point

```python
from gui.G04d_app_shell import AppShell
```

### For Page Classes

```python
# G02a for widgets and tokens
from gui.G02a_widget_primitives import (
    make_button, make_label, make_entry,
    SPACING_SM, SPACING_MD,
)

# G03 for patterns
from gui.G03a_layout_patterns import page_layout
from gui.G03b_container_patterns import make_page_header_with_actions
from gui.G03c_form_patterns import form_section
from gui.G03d_table_patterns import create_table_with_toolbar
from gui.G03e_widget_components import metric_row, filter_bar
```

### For Extending State

```python
from gui.G04a_app_state import AppState, StateSchemaType
```

---

*End of GUI Orchestration Documentation*