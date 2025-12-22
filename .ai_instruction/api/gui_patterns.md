# GUI Patterns Documentation

> **Layer:** G03 (Patterns & Components)  
> **Status:** Complete and Stable  
> **Last Updated:** 2026-01-01

> ⚠️ **Import Rule:** Pages import from G02a only (widgets, tokens, types). Never import directly from G01 modules.

---

## 1. Layer Overview

G03 provides **reusable UI patterns** built on top of the G02 primitives. While G02 creates individual widgets, G03 composes them into higher-level building blocks for application pages.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         G04+ ORCHESTRATION                          │
│              (Navigator, Controllers, Application Shell)            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         G03 PATTERNS LAYER                          │
├───────────┬───────────┬───────────┬───────────┬───────────┬─────────┤
│   G03a    │   G03b    │   G03c    │   G03d    │   G03e    │  G03f   │
│  layouts  │ containers│   forms   │  tables   │ components│ renderer│
└───────────┴───────────┴───────────┴───────────┴───────────┴─────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         G02 PRIMITIVES LAYER                        │
│              (widget factories, layout utils, base window)          │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Principles:**

- G03 modules import from G02a (never from G01 directly)
- G03 modules may import from peer G03 modules (e.g., G03c imports from G03b)
- G03 patterns return frames/widgets — caller owns geometry (`.pack()`, `.grid()`)
- G03f is the bridge to G04 — defines protocols that G04 implements

---

## 2. Module Reference

### G03a_layout_patterns
**Purpose:** Page-level layout structures.

| Function | Returns | Description |
|----------|---------|-------------|
| `page_layout()` | Frame | Standard page container with padding |
| `make_content_row()` | Frame | Row with weighted columns, auto-packed |
| `header_content_footer_layout()` | `(outer, header, content, footer)` | Three-region vertical layout |
| `two_column_layout()` | `(outer, left, right)` | Two weighted columns |
| `three_column_layout()` | `(outer, col1, col2, col3)` | Three weighted columns |
| `sidebar_content_layout()` | `(outer, sidebar, content)` | Fixed sidebar + expanding content |
| `section_with_header()` | `(outer, header, content)` | Section with header area |
| `toolbar_content_layout()` | `(outer, toolbar, content)` | Toolbar row above content |
| `button_row()` | Frame | Aligned button container |
| `form_row()` | `(outer, label_frame, widget_frame)` | Label + input columns |
| `split_row()` | `(outer, left_frame)` | N-column split with weights |

**Note:** Layout functions returning tuples include the outer container first. Always unpack and pack the outer frame.

---

### G03b_container_patterns
**Purpose:** Styled container compositions.

| Function | Returns | Description |
|----------|---------|-------------|
| `make_card()` | Frame | Raised card container |
| `make_panel()` | Frame | Bordered panel container |
| `make_section()` | Frame | Flat section container |
| `make_surface()` | Frame | Borderless surface container |
| `make_titled_card()` | tuple[2] | Card with title header |
| `make_titled_section()` | tuple[2] | Section with title + optional divider |
| `make_page_header()` | Frame | Page title + subtitle |
| `make_page_header_with_actions()` | tuple[2] | Page header + actions area |
| `make_section_header()` | Frame | Section title |
| `make_alert_box()` | Frame | Alert/notification box |
| `make_status_banner()` | Frame | Full-width status banner |

---

### G03c_form_patterns
**Purpose:** Form field compositions.

| Export | Type | Description |
|--------|------|-------------|
| `FormField` | dataclass | Field specification (input to form builders) |
| `FormResult` | dataclass | Form builder result (frame, fields dict, variables dict) |
| `form_field_entry()` | `(frame, label, widget)` | Label + entry row |
| `form_field_combobox()` | `(frame, label, widget)` | Label + combobox row |
| `form_field_spinbox()` | `(frame, label, widget)` | Label + spinbox row |
| `form_field_checkbox()` | `(frame, label, widget)` | Checkbox with alignment spacer |
| `validation_message()` | `(frame, label, show_func, hide_func)` | Error label with show/hide |
| `form_group()` | FormResult | Build form from field specs |
| `form_section()` | FormResult | Titled section with form fields |
| `form_button_row()` | `(frame, buttons_dict)` | Aligned action buttons |

**FormField dataclass fields:** `name`, `label`, `field_type`, `required`, `options`, `default`

**FormResult dataclass fields:** `frame`, `fields` (dict by name), `variables` (dict by name)

---

### G03d_table_patterns
**Purpose:** Table/treeview compositions.

| Export | Type | Description |
|--------|------|-------------|
| `TableColumn` | dataclass | Column specification |
| `TableResult` | dataclass | Table builder result container |
| `create_table()` | TableResult | Basic table with vertical scroll |
| `create_table_with_horizontal_scroll()` | TableResult | Table with both scrollbars |
| `create_zebra_table()` | TableResult | Alternating row colours |
| `apply_zebra_striping()` | None | Apply striping to existing rows |
| `create_table_with_toolbar()` | tuple[3] | Toolbar + table composition |
| `insert_rows()` | list[str] | Insert data rows |
| `insert_rows_zebra()` | list[str] | Insert rows + apply striping |
| `get_selected_values()` | list[dict] | Get selected row values (keys are column IDs) |
| `clear_table()` | None | Remove all rows |

---

### G03e_widget_components
**Purpose:** High-level composite components.

| Export | Type | Description |
|--------|------|-------------|
| `FilterBarResult` | dataclass | Filter bar result container |
| `MetricCardResult` | dataclass | Metric card result container |
| `filter_bar()` | FilterBarResult | Horizontal filter controls |
| `search_box()` | tuple[3] | Search entry + button |
| `metric_card()` | MetricCardResult | Single metric display |
| `metric_row()` | tuple[2] | Row of metric cards |
| `dismissible_alert()` | tuple[2] | Alert with dismiss button |
| `toast_notification()` | Frame | Auto-dismissing notification |
| `action_header()` | tuple[2] | Header with action buttons |
| `empty_state()` | Frame | Empty data placeholder |

---

### G03f_renderer
**Purpose:** Page instantiation and mounting delegate.

| Export | Type | Description |
|--------|------|-------------|
| `WindowProtocol` | Protocol | Window interface contract |
| `PageProtocol` | Protocol | Page interface contract |
| `G03Renderer` | class | Page factory and mount delegate |

---

## 3. Pattern Categories

### Layout Patterns (G03a)

Layout patterns create **structural frames** that define page regions. They configure grid weights and return frames ready for content.

```python
from gui.G03a_layout_patterns import (
    page_layout, two_column_layout, header_content_footer_layout
)

# Page with header, content, footer
outer, header, content, footer = header_content_footer_layout(
    parent, header_height=60, footer_height=40
)
outer.pack(fill="both", expand=True)

# Two-column split inside content
col_outer, left, right = two_column_layout(
    content, left_weight=1, right_weight=2, gap=SPACING_MD
)
col_outer.pack(fill="both", expand=True)
```

---

### Container Patterns (G03b)

Container patterns create **styled regions** with consistent visual treatment.

```python
from gui.G03b_container_patterns import (
    make_card, make_titled_section, make_page_header_with_actions
)

# Page header with actions
header, actions = make_page_header_with_actions(
    parent, title="Dashboard", subtitle="System overview"
)
header.pack(fill="x")
make_button(actions, text="Refresh", command=on_refresh).pack(side="left")

# Titled card
card, card_content = make_titled_card(parent, title="Statistics")
card.pack(fill="x", pady=SPACING_MD)
make_label(card_content, text="Content here").pack()
```

---

### Form Patterns (G03c)

Form patterns create **data entry compositions** with consistent label/input alignment.

```python
from gui.G03c_form_patterns import (
    FormField, form_section, form_button_row
)

# Declarative form definition
fields = [
    FormField(name="email", label="Email", required=True),
    FormField(name="role", label="Role", field_type="combobox",
              options=["Admin", "User", "Guest"]),
    FormField(name="active", label="Active", field_type="checkbox", default=True),
]

result = form_section(parent, title="User Details", fields=fields)
result.frame.pack(fill="x")

# Access values via result.variables["email"].get()

# Button row
btn_row, buttons = form_button_row(
    parent,
    buttons=[("Save", on_save), ("Cancel", on_cancel)],
    alignment="right"
)
btn_row.pack(fill="x")
```

---

### Table Patterns (G03d)

Table patterns create **data table compositions** with scrollbars and helpers.

```python
from gui.G03d_table_patterns import (
    TableColumn, create_table_with_toolbar, insert_rows_zebra
)

columns = [
    TableColumn(id="id", heading="ID", width=50, anchor="center"),
    TableColumn(id="name", heading="Name", width=200),
    TableColumn(id="status", heading="Status", width=100),
]

outer, toolbar, table = create_table_with_toolbar(parent, columns=columns)
outer.pack(fill="both", expand=True)

# Add toolbar buttons
make_button(toolbar, text="Add", command=on_add).pack(side="left")
make_button(toolbar, text="Delete", command=on_delete).pack(side="left")

# Populate with data
data = [
    (1, "Alice", "Active"),
    (2, "Bob", "Inactive"),
]
insert_rows_zebra(table.treeview, data)
```

---

### Widget Components (G03e)

Widget components are **ready-to-use UI compositions** for common patterns.

```python
from gui.G03e_widget_components import (
    metric_row, filter_bar, dismissible_alert, empty_state
)

# Metrics dashboard row
metrics = [
    {"title": "Users", "value": "1,234", "role": "PRIMARY"},
    {"title": "Revenue", "value": "$45K", "role": "SUCCESS"},
    {"title": "Errors", "value": "3", "role": "ERROR"},
]
row, cards = metric_row(parent, metrics)
row.pack(fill="x")

# Update a metric value dynamically
cards[0].value_label.configure(text="1,235")

# Filter bar
filters = [
    {"name": "status", "label": "Status", "type": "combobox",
     "options": ["All", "Active", "Inactive"]},
    {"name": "search", "label": "Search", "type": "entry"},
]
result = filter_bar(parent, filters, on_search=do_search)
result.frame.pack(fill="x")

# Empty state
empty = empty_state(
    parent,
    title="No results",
    message="Try adjusting your filters.",
    action_text="Clear Filters",
    on_action=clear_filters
)
```

---

## 4. Renderer Protocol (G03f)

G03f defines the **contract between G03 (UI) and G04 (orchestration)**. It is the sole point of page instantiation.

### WindowProtocol

Any window that hosts pages must implement:

```python
class WindowProtocol(Protocol):
    @property
    def content_frame(self) -> ttk.Frame:
        """Return the frame where pages are mounted."""
        ...

    def set_content(self, frame: tk.Misc) -> None:
        """Mount a frame into the content area."""
        ...
```

G02c's `BaseWindow` implements this protocol.

---

### PageProtocol

Any page class must implement:

```python
class PageProtocol(Protocol):
    def __init__(self, controller: Any) -> None:
        """Receive controller for business logic delegation."""
        ...

    def build(self, parent: tk.Misc, params: dict[str, Any]) -> tk.Misc:
        """Build and return the page's root frame."""
        ...
```

---

### Renderer Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. G04 creates G03Renderer                                          │
│ 2. G04 calls renderer.set_window(base_window)                       │
│ 3. On navigation, G04 calls renderer.render_page(PageClass, ctrl)   │
│    a. Renderer instantiates: page = PageClass(controller)           │
│    b. Renderer calls: frame = page.build(parent, params)            │
│    c. Renderer mounts: window.set_content(frame)                    │
│    d. Renderer returns: frame (for caching)                         │
│ 4. For cached pages: renderer.mount_cached_frame(frame)             │
│ 5. On error: renderer.render_error_page(ErrorPage, ctrl, message)   │
└─────────────────────────────────────────────────────────────────────┘
```

**Why this separation?**

- **G03 owns construction** — knows how to build UI
- **G04 owns orchestration** — knows when/which page to show
- **Renderer is the bridge** — enforces protocol, handles errors
- **Testability** — mock WindowProtocol for unit testing without Tk

---

## 5. Usage Examples

### Complete Page Layout

```python
from gui.G02a_widget_primitives import SPACING_MD
from gui.G03a_layout_patterns import page_layout, header_content_footer_layout
from gui.G03b_container_patterns import make_page_header_with_actions
from gui.G03d_table_patterns import TableColumn, create_table_with_toolbar
from gui.G03e_widget_components import filter_bar

def build_users_page(parent: tk.Misc) -> tk.Misc:
    """Build a complete users management page."""
    
    # Page wrapper
    page = page_layout(parent, padding=SPACING_MD)
    page.pack(fill="both", expand=True)
    
    # Header with actions
    header, actions = make_page_header_with_actions(
        page, title="Users", subtitle="Manage system users"
    )
    header.pack(fill="x", pady=(0, SPACING_MD))
    make_button(actions, text="Add User", command=on_add).pack(side="left")
    
    # Filter bar
    filters = [
        {"name": "role", "label": "Role", "type": "combobox",
         "options": ["All", "Admin", "User"]},
    ]
    fb = filter_bar(page, filters, on_search=do_search)
    fb.frame.pack(fill="x", pady=(0, SPACING_MD))
    
    # Data table
    columns = [
        TableColumn(id="name", heading="Name", width=200),
        TableColumn(id="email", heading="Email", width=250),
        TableColumn(id="role", heading="Role", width=100),
    ]
    outer, toolbar, table = create_table_with_toolbar(page, columns=columns)
    outer.pack(fill="both", expand=True)
    
    return page
```

---

### Implementing PageProtocol

```python
class UsersPage:
    """Users management page implementing PageProtocol."""
    
    def __init__(self, controller: UsersController) -> None:
        self.controller = controller
    
    def build(self, parent: tk.Misc, params: dict[str, Any]) -> tk.Misc:
        page = page_layout(parent)
        page.pack(fill="both", expand=True)
        
        # Build UI using G03 patterns...
        
        # Wire events to controller
        refresh_btn = make_button(page, text="Refresh", 
                                   command=self.controller.refresh_users)
        
        return page
```

---

## 6. Import Patterns

### Standard G03 Imports

```python
# From G02a (unified API)
from gui.G02a_widget_primitives import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG,
    make_label, make_button, make_entry, make_frame,
    page_title, section_title, body_text,
    ShadeType, SpacingType,
)

# From peer G03 modules
from gui.G03a_layout_patterns import page_layout, two_column_layout
from gui.G03b_container_patterns import make_card, make_page_header_with_actions
from gui.G03c_form_patterns import FormField, form_section
from gui.G03d_table_patterns import TableColumn, create_table_with_toolbar
from gui.G03e_widget_components import metric_row, filter_bar
from gui.G03f_renderer import G03Renderer, PageProtocol
```

### Never Do This

```python
# ❌ Don't import tokens from G01 directly
from gui.G01a_style_config import SPACING_MD  # Wrong!

# ❌ Don't bypass G02a for style resolvers
from gui.G01c_text_styles import resolve_text_style  # Wrong!

# ✅ Always use G02a re-exports
from gui.G02a_widget_primitives import SPACING_MD, label_style
```

---

## 7. Design Decisions

### Architectural Invariants

G03 enforces strict boundaries to remain a pure composition layer:

**1. No global style mutation**
G03 never mutates ttk style registries at runtime. All styles are resolved via G02a wrappers which delegate to G01's cached resolvers. If you need a new style, define it in G01 — don't patch it in G03.

```python
# ❌ Never do this in G03
ttk.Style().configure("Custom.TButton", ...)  # Wrong!

# ✅ Use G02a style wrappers
style_name = button_style(bg_colour="PRIMARY")  # Correct
```

**2. No business logic**
G03 wires events to controllers — it never implements them. Business logic belongs in G04 controllers.

```python
# ❌ Never build business logic in G03 components
def save_user():
    db.write(user_data)  # Wrong! This is controller logic
    
make_button(parent, text="Save", command=save_user)

# ✅ Delegate to controller (G04)
make_button(parent, text="Save", command=controller.save_user)
```

**3. Validation lives in G04**
G03 provides `validation_message()` for *displaying* errors — but the validation *rules* belong in G04 controllers. G03 is the messenger, not the judge.

```python
# ❌ Don't embed validation rules in G03
if len(email_var.get()) < 5:
    show_error("Email too short")  # Wrong! Rule belongs in controller

# ✅ G03 displays, G04 decides
# In G03 page:
self.show_error = validation_message(parent)[1]

# In G04 controller:
def validate_email(self, email: str) -> bool:
    if len(email) < 5:
        self.page.show_error("Email too short")
        return False
    return True
```

**4. No retained references**
G03 returns frames and forgets them. It must not cache or store references to mounted frames. This supports garbage collection and navigation recycling.

```python
# ❌ Don't retain references
class BadComponent:
    _instances: list = []  # Wrong! Global state
    
    def build(self, parent):
        frame = make_frame(parent)
        self._instances.append(frame)  # Memory leak!
        return frame

# ✅ Build and return, nothing more
def metric_card(parent, title, value) -> MetricCardResult:
    frame = make_card(parent)
    # ... build content ...
    return MetricCardResult(frame=frame, ...)  # Caller owns it now
```

---

### Why Dataclass Results?

Functions like `form_group()` and `create_table()` return dataclass containers (`FormResult`, `TableResult`) instead of plain tuples because:

1. **Named access** — `result.treeview` is clearer than `result[1]`
2. **Type hints** — IDE knows the types of each field
3. **Extensibility** — can add fields without breaking callers
4. **Documentation** — dataclass docstrings explain each field

### Why Separate G03a-G03e?

Each module handles a distinct pattern category:

| Module | Category | Typical Use |
|--------|----------|-------------|
| G03a | Structure | Page regions, grids |
| G03b | Containers | Visual grouping |
| G03c | Forms | Data entry |
| G03d | Tables | Data display |
| G03e | Components | Dashboard elements |

This separation allows selective imports and clear mental models.

### Why G03f Renderer?

The renderer exists to:

1. **Enforce protocol** — pages must implement `PageProtocol`
2. **Centralise instantiation** — one place creates pages
3. **Handle errors** — graceful fallback to error page
4. **Enable caching** — Navigator can cache built frames
5. **Support testing** — mock window for unit tests

---

## 8. Quick Reference

### Result Container Fields

**FormResult:**
- `frame` — outer container
- `fields` — dict of widgets by name
- `variables` — dict of tk variables by name

**TableResult:**
- `frame` — outer container
- `treeview` — the ttk.Treeview widget
- `scrollbar_y` — vertical scrollbar
- `scrollbar_x` — horizontal scrollbar (if present)

**FilterBarResult:**
- `frame` — outer container
- `filters` — dict of filter widgets
- `variables` — dict of filter variables
- `search_button` — search button widget
- `clear_button` — clear button widget (if present)

**MetricCardResult:**
- `frame` — card container
- `value_label` — label showing the value
- `title_label` — label showing the title
- `subtitle_label` — label showing subtitle (if present)

### Common Parameter Patterns

| Parameter | Type | Description |
|-----------|------|-------------|
| `parent` | tk.Misc | Parent widget (always first) |
| `padding` | int | Pixel padding |
| `gap` | int | Pixel gap between elements |
| `role` | str | Semantic colour (PRIMARY, SUCCESS, etc.) |
| `shade` | str | Colour shade (LIGHT, MID, DARK, XDARK) |
| `on_*` | Callable | Event callback |

---

*End of GUI Patterns Documentation*