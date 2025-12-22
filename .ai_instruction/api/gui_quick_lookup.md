# Quick Lookup — GUI Framework

> Last Updated: 2026-01-01

> Find the right function fast. Organised by task, not by module.

**Rule:** If a function exists here, use it. Do not reimplement.

**Important:** If a task is not listed here, you MUST still search the detailed GUI docs (`gui_foundation.md`, `gui_patterns.md`, `gui_orchestration.md`) before implementing. Absence from this index does not mean absence from the framework.

**Architecture:** G10a (design) owns presentation. G10b (controller) owns logic. Never mix them.

**Re-exports:** All design tokens (SPACING_*, TEXT_COLOURS, type literals) are re-exported through G02a. Always import from G02a, never directly from G01a.

---

## 📦 Imports

| I need to... | Use | From |
|--------------|-----|------|
| Import core packages | `from core.C00_set_packages import *` | C00 |
| Get the module logger | `logger = get_logger(__name__)` | C01 |
| Import widget primitives & factories | `from gui.G02a_widget_primitives import ...` | G02a |
| Import layout utilities | `from gui.G02b_layout_utils import ...` | G02b |
| Import layout patterns | `from gui.G03a_layout_patterns import ...` | G03a |
| Import container patterns | `from gui.G03b_container_patterns import ...` | G03b |
| Import form patterns | `from gui.G03c_form_patterns import ...` | G03c |
| Import table patterns | `from gui.G03d_table_patterns import ...` | G03d |
| Import widget components | `from gui.G03e_widget_components import ...` | G03e |
| Import PageProtocol | `from gui.G03f_renderer import PageProtocol` | G03f |
| Import AppShell | `from gui.G04d_app_shell import AppShell` | G04d |

---

## 🏷️ Type Aliases (for Widget References)

Use these in G10a `__init__` to declare widget references with proper type hints.

| Type Alias | Maps To | Use For |
|------------|---------|---------|
| `WidgetType` | `tk.Misc` | Parent parameters in method signatures |
| `EventType` | `tk.Event` | Event handler parameters |
| `FrameType` | `ttk.Frame` | Frame references |
| `LabelType` | `ttk.Label` | Label references |
| `EntryType` | `ttk.Entry` | Entry field references |
| `ButtonType` | `ttk.Button` | Button references |
| `ComboboxType` | `ttk.Combobox` | Combobox references |
| `SpinboxType` | `ttk.Spinbox` | Spinbox references |
| `RadioType` | `ttk.Radiobutton` | Radio button references |
| `CheckboxType` | `ttk.Checkbutton` | Checkbox references |
| `TreeviewType` | `ttk.Treeview` | Table/tree references |
| `TextType` | `tk.Text` | Textarea/console references |
| `ToplevelType` | `tk.Toplevel` | Dialog window references |
| `NotebookType` | `ttk.Notebook` | Tabbed container references |
| `DateEntryType` | `DateEntry` | Date picker references |
| `StringVar` | `tk.StringVar` | String variable for entries |
| `BooleanVar` | `tk.BooleanVar` | Boolean variable for checkboxes |
| `IntVar` | `tk.IntVar` | Integer variable for spinboxes |
| `DoubleVar` | `tk.DoubleVar` | Float variable |

**Example usage in G10a:**
```python
self.search_entry: EntryType | None = None
self.search_var: StringVar | None = None
self.submit_btn: ButtonType | None = None
self.results_table: TreeviewType | None = None
```

---

## 🧱 Widget Factories (G02a)

| I need to... | Use | Key Parameters |
|--------------|-----|----------------|
| Create a label | `make_label(parent, text=..., fg_colour=..., size=...)` | `fg_colour`, `size`, `bold` |
| Create a status label (OK/Error toggle) | `make_status_label(parent, text_ok=..., text_error=...)` | `text_ok`, `text_error` |
| Create a frame/container | `make_frame(parent, bg_colour=..., padding=...)` | `bg_colour`, `bg_shade`, `border_weight` |
| Create a text entry | `make_entry(parent, textvariable=..., width=...)` | `textvariable`, `width`, `state` |
| Create a combobox/dropdown | `make_combobox(parent, textvariable=..., values=...)` | `textvariable`, `values`, `state` |
| Create a spinbox | `make_spinbox(parent, textvariable=..., from_=..., to=...)` | `from_`, `to`, `increment` |
| Create a date picker | `make_date_picker(parent, textvariable=...)` | `textvariable`, `date_pattern` |
| Create a button | `make_button(parent, text=..., bg_colour=..., fg_colour=...)` | `text`, `bg_colour`, `fg_colour`, `command` |
| Create a checkbox | `make_checkbox(parent, text=..., variable=...)` | `text`, `variable` |
| Create a radio button | `make_radio(parent, text=..., variable=..., value=...)` | `text`, `variable`, `value` |
| Create a separator line | `make_separator(parent, orient=...)` | `orient` ("horizontal"/"vertical") |
| Create vertical space | `make_spacer(parent, height=...)` | `height` |
| Create multi-line text input | `make_textarea(parent, width=..., height=...)` | `width`, `height` |
| Create read-only console | `make_console(parent, width=..., height=...)` | `width`, `height` |
| Create scrollable container | `make_scrollable_frame(parent)` | Frame with `.content` (add children to `.content`) |
| Create tabbed container | `make_notebook(parent)` | use `.add(frame, text="Tab")` |
| Create basic treeview | `make_treeview(parent, columns=...)` | `columns`, `show` |
| Create zebra-striped treeview | `make_zebra_treeview(parent, columns=...)` | `columns` |

---

## 📝 Typography Helpers (G02a)

| I need to... | Use | Size |
|--------------|-----|------|
| Create page title | `page_title(parent, text=...)` | DISPLAY, bold |
| Create page subtitle | `page_subtitle(parent, text=...)` | TITLE |
| Create section title | `section_title(parent, text=...)` | TITLE, bold |
| Create body text | `body_text(parent, text=...)` | BODY |
| Create small/caption text | `small_text(parent, text=...)` | SMALL |
| Create muted metadata | `meta_text(parent, text=...)` | SMALL, grey |
| Create horizontal divider | `divider(parent)` | — |

---

## 🎨 Parameter Values Reference

Use these values for styling parameters in widget factories.

**Colour Parameters:**

| Parameter | Type | Valid Values |
|-----------|------|--------------|
| `fg_colour` | TextColourType | "BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY", "SUCCESS", "ERROR", "WARNING" |
| `bg_colour` | ContainerRoleType | "PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR" |
| `bg_shade` | ShadeType | "LIGHT", "MID", "DARK", "XDARK" |
| `border_colour` | ContainerRoleType | "PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR" |

**Size Parameters:**

| Parameter | Type | Valid Values |
|-----------|------|--------------|
| `size` | SizeType | "DISPLAY", "HEADING", "TITLE", "BODY", "SMALL" |
| `padding` | SpacingType | "XS", "SM", "MD", "LG", "XL", "XXL" |
| `border_weight` | BorderWeightType | "NONE", "THIN", "MEDIUM", "THICK" |

**Spacing Constants (pixels):**

| Token | Value | Use |
|-------|-------|-----|
| `SPACING_XS` | 4 | Tight spacing |
| `SPACING_SM` | 8 | Default element spacing |
| `SPACING_MD` | 16 | Standard padding |
| `SPACING_LG` | 24 | Card padding |
| `SPACING_XL` | 32 | Page margins |
| `SPACING_XXL` | 48 | Major sections |

**Usage Examples:**
```python
# Label with colour and size
make_label(parent, text="Error!", fg_colour="ERROR", size="HEADING", bold=True)

# Button with background and foreground colours
make_button(parent, text="Save", bg_colour="SUCCESS", fg_colour="WHITE")

# Frame with shade and border
make_frame(parent, bg_colour="SECONDARY", bg_shade="LIGHT", border_colour="PRIMARY", border_weight="THIN", padding="MD")
```

---

## 📐 Layout Utilities (G02b)

| I need to... | Use | Notes |
|--------------|-----|-------|
| Pack widget left-to-right | `layout_row(widget, fill="x", padx=...)` | Horizontal packing |
| Pack widget top-to-bottom | `layout_col(widget, fill="y", pady=...)` | Vertical packing |
| Configure grid weights | `grid_configure(parent, rows={0:1}, cols={0:1,1:2})` | Row/col weight dicts |
| Stack widgets vertically | `stack_vertical(parent, widgets, spacing=...)` | List of widgets |
| Stack widgets horizontally | `stack_horizontal(parent, widgets, spacing=...)` | List of widgets |
| Apply padding to widget | `apply_padding(widget, padx=..., pady=...)` | Configure padding |
| Fill remaining space | `fill_remaining(widget)` | `pack(fill="both", expand=True)` |
| Centre widget in parent | `center_in_parent(widget)` | Uses place(). ⚠️ Do not use inside grid-managed containers. |

---

## 📄 Layout Patterns (G03a)

| I need to... | Use | Returns |
|--------------|-----|---------|
| Create page container | `page_layout(parent, padding=..., bg_colour=...)` | Frame |
| Create weighted row | `make_content_row(parent, weights={0:1,1:1}, min_height=...)` | Frame with grid |
| Create header/content/footer | `header_content_footer_layout(parent)` | `(outer, header, content, footer)` |
| Create two-column layout | `two_column_layout(parent, left_weight=1, right_weight=1)` | `(outer, left, right)` |
| Create three-column layout | `three_column_layout(parent, weights=(1,1,1))` | `(outer, col1, col2, col3)` |
| Create sidebar + content | `sidebar_content_layout(parent, sidebar_width=...)` | `(outer, sidebar, content)` |
| Create section with header | `section_with_header(parent, title=...)` | `(outer, header, content)` |
| Create toolbar + content | `toolbar_content_layout(parent)` | `(outer, toolbar, content)` |
| Create button row | `button_row(parent, buttons=[...], align="right")` | Frame |
| Create form field row | `form_row(parent, label=..., widget=...)` | `(outer, label_frame, widget_frame)` |
| Create split row (label:value) | `split_row(parent, left_text=..., right_text=...)` | `(outer, left_frame)` |

**Note:** Layout functions return the outer container first. Always unpack and pack the outer: `outer, left, right = two_column_layout(...); outer.pack(fill="both", expand=True)` |

---

## 📦 Container Patterns (G03b)

| I need to... | Use | Notes |
|--------------|-----|-------|
| Create card (raised) | `make_card(parent, bg_colour=..., padding=...)` | `.content` for children |
| Create panel (solid border) | `make_panel(parent, bg_colour=...)` | `.content` for children |
| Create section (flat) | `make_section(parent)` | `.content` for children |
| Create surface (no border) | `make_surface(parent)` | `.content` for children |
| Create card with title | `make_titled_card(parent, title=...)` | `(card, content)` |
| Create section with title | `make_titled_section(parent, title=...)` | `(section, content)` |
| Create page header | `make_page_header(parent, title=..., subtitle=...)` | Frame |
| Create page header with actions | `make_page_header_with_actions(parent, title=...)` | `(header, actions_frame)` |
| Create section header | `make_section_header(parent, title=...)` | Frame |
| Create alert box | `make_alert_box(parent, message=..., variant="info")` | Frame |
| Create status banner | `make_status_banner(parent, text=..., variant="success")` | Frame |

---

## 📋 Form Patterns (G03c)

| I need to... | Use | Returns |
|--------------|-----|---------|
| Create labelled entry field | `form_field_entry(parent, label=..., var=...)` | `(frame, label, widget)` |
| Create labelled combobox | `form_field_combobox(parent, label=..., var=..., values=...)` | `(frame, label, widget)` |
| Create labelled spinbox | `form_field_spinbox(parent, label=..., var=..., from_=..., to=...)` | `(frame, label, widget)` |
| Create labelled checkbox | `form_field_checkbox(parent, label=..., var=...)` | `(frame, label, widget)` |
| Create validation message | `validation_message(parent, text=..., variant="error")` | `(frame, label, show_func, hide_func)` |
| Create form group (vertical) | `form_group(parent, fields=[...], spacing=...)` | `FormResult` |
| Create form section (titled) | `form_section(parent, title=..., fields=[...])` | `FormResult` |
| Create form button row | `form_button_row(parent, submit_text=..., cancel_text=...)` | `(frame, buttons_dict)` |

**FormField dataclass (input specification):** `FormField(name="email", label="Email", field_type="entry", required=True, options=[], default=None)`

**FormResult dataclass (output):** `FormResult(frame, fields, variables)` — `fields` and `variables` are dicts keyed by field name

---

## 📊 Table Patterns (G03d)

| I need to... | Use | Returns |
|--------------|-----|---------|
| Define a table column | `TableColumn(id="order_id", heading="Order ID", width=100, anchor="w")` | dataclass |
| Create basic table | `create_table(parent, columns=[...], height=...)` | `TableResult` |
| Create table with h-scroll | `create_table_with_horizontal_scroll(parent, columns=...)` | `TableResult` |
| Create zebra-striped table | `create_zebra_table(parent, columns=...)` | `TableResult` |
| Create table with toolbar | `create_table_with_toolbar(parent, columns=...)` | `(toolbar, TableResult)` |
| Insert rows into table | `insert_rows(tree, rows=[...])` | — |
| Insert rows with zebra | `insert_rows_zebra(tree, rows=[...])` | — |
| Get selected row values | `get_selected_values(tree)` | List of dicts (keys are column IDs) |
| Clear all rows | `clear_table(tree)` | — |
| Apply zebra striping | `apply_zebra_striping(tree)` | — |

**TableResult dataclass:** `(frame, treeview, scrollbar_y, scrollbar_x)`

---

## 🧩 Widget Components (G03e)

| I need to... | Use | Returns |
|--------------|-----|---------|
| Create filter bar | `filter_bar(parent, filters=[...], on_apply=...)` | `FilterBarResult` |
| Create search box | `search_box(parent, on_search=..., placeholder=...)` | `(frame, entry, var)` |
| Create metric card | `metric_card(parent, title=..., value=..., subtitle=...)` | `MetricCardResult` |
| Create row of metrics | `metric_row(parent, metrics=[...])` | Frame |
| Create dismissible alert | `dismissible_alert(parent, message=..., on_dismiss=...)` | Frame |
| Create toast notification | `toast_notification(parent, message=..., duration=...)` | — |
| Create header with actions | `action_header(parent, title=..., actions=[...])` | Frame |
| Create empty state | `empty_state(parent, title=..., message=..., action=...)` | Frame |

---

## 💬 Dialog Functions (G02a)

| I need to... | Use | Returns |
|--------------|-----|---------|
| Create modal dialog | `make_dialog(parent, title=..., width=..., height=...)` | `Toplevel` |
| Open folder picker | `ask_directory(title=..., initial_dir=...)` | `str \| None` |
| Open single file picker | `ask_open_file(title=..., filetypes=[...])` | `str \| None` |
| Open multi-file picker | `ask_open_files(title=..., filetypes=[...])` | `list[str]` |
| Open save file dialog | `ask_save_file(title=..., default_extension=...)` | `str \| None` |
| Show Yes/No confirmation | `ask_yes_no(title=..., message=...)` | `bool` |
| Show OK/Cancel confirmation | `ask_ok_cancel(title=..., message=...)` | `bool` |
| Show info message | `show_info(title=..., message=...)` | `None` |

**Filetypes format:** `[("CSV Files", "*.csv"), ("All Files", "*.*")]`

> ⚠️ **Thread Safety:** Dialogs are modal and block the main thread. Never call them from inside long-running background threads.

---

## 🚀 AppShell & Navigation (G04d)

| I need to... | Use | Notes |
|--------------|-----|-------|
| Access app state | `self.app.app_state` | Get/set session data |
| Access navigator | `self.app.navigator` | Page navigation |
| Access root window | `self.app.root` | Tk root for dialogs |
| Navigate to page | `self.app.navigator.navigate("page_name", params={...})` | Pass data via params |
| Reload current page | `self.app.navigator.reload()` | Re-runs build() |
| Go back | `self.app.navigator.back()` | Previous page |
| Clear navigation cache | `self.app.navigator.clear_cache()` | Force fresh builds |
| Register a page | `app.register_page("name", PageClass)` | At startup |

---

## 📏 Spacing Tokens (G02a)

| Token | Value | Use For |
|-------|-------|---------|
| `SPACING_XS` | 4px | Tight gaps |
| `SPACING_SM` | 8px | Small gaps |
| `SPACING_MD` | 16px | Standard padding |
| `SPACING_LG` | 24px | Section gaps |
| `SPACING_XL` | 32px | Large gaps |
| `SPACING_XXL` | 48px | Major sections |

---

## 🎨 Colour Configuration

**Colour Presets:** `"PRIMARY"`, `"SECONDARY"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"GREY"`, `"WHITE"`

**Shade Options:** `"LIGHT"`, `"MID"`, `"DARK"`, `"XDARK"`

**Text Colours:** `"BLACK"`, `"WHITE"`, `"GREY"`, `"PRIMARY"`, `"SECONDARY"`, `"SUCCESS"`, `"ERROR"`, `"WARNING"`

**Size Options:** `"DISPLAY"`, `"HEADING"`, `"TITLE"`, `"BODY"`, `"SMALL"`

---

## 🔌 Controller Wiring (G10b)

### Wire Button Click
```python
# In G10a: declare reference
self.submit_btn: ButtonType | None = None

# In G10a build: create button (no command)
self.submit_btn = make_button(parent, text="Submit")

# In G10b _wire_events():
if self.page.submit_btn is not None:
    self.page.submit_btn.configure(command=self._on_submit)
```

### Wire Entry Validation
```python
# In G10b _wire_events():
if self.page.name_entry is not None:
    self.page.name_entry.bind("<FocusOut>", self._on_validate_name)

# Handler signature:
def _on_validate_name(self, event: EventType | None = None) -> None:
```

### Wire Combobox Selection
```python
# In G10b _wire_events():
if self.page.category_combo is not None:
    self.page.category_combo.bind("<<ComboboxSelected>>", self._on_category_change)
```

### Wire Checkbox Toggle
```python
# In G10b _wire_events():
if self.page.enabled_var is not None:
    self.page.enabled_var.trace_add("write", self._on_enabled_toggle)

# Handler signature:
def _on_enabled_toggle(self, *args) -> None:
```

### Wire Treeview Selection
```python
# In G10b _wire_events():
if self.page.results_tree is not None:
    self.page.results_tree.bind("<<TreeviewSelect>>", self._on_row_select)
```

### Wire Treeview Double-Click
```python
# In G10b _wire_events():
if self.page.results_tree is not None:
    self.page.results_tree.bind("<Double-1>", self._on_row_double_click)
```

### Add Header Action Buttons
```python
# In G10b _wire_events():
if self.page.header_actions is not None:
    save_btn = make_button(self.page.header_actions, text="Save", ...)
    save_btn.configure(command=self._on_save)
    save_btn.pack(side="right", padx=SPACING_SM)
```

### Access App State
```python
# In G10b handler:
session = self.app.app_state.get_state("session_data")
session["last_query"] = value
self.app.app_state.set_state("session_data", session)
```

### Navigate to Another Page
```python
# In G10b handler:
self.app.navigator.navigate("results", params={"query": value})
```

---

## 📖 Example Recipe — Search + Table Page

A common pattern: search input, action buttons, results table with row interaction.

**G10a Design Structure:**
```
┌─────────────────────────────────────────────────┐
│ Page Header                    [Refresh] [Export]│  ← header_actions
├─────────────────────────────────────────────────┤
│ Row 1: Search                                    │
│ ┌─────────────────────────────────┐ ┌─────────┐ │
│ │ 🔍 Search entry                 │ │ Search  │ │  ← search_entry, search_btn
│ └─────────────────────────────────┘ └─────────┘ │
├─────────────────────────────────────────────────┤
│ Row 2: Results                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ ID  │ Name        │ Status   │ Created     │ │  ← results_table (zebra)
│ │ 001 │ Widget A    │ Active   │ 2025-01-15  │ │
│ │ 002 │ Widget B    │ Pending  │ 2025-01-14  │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│ Status: 2 results found                          │  ← status_label
└─────────────────────────────────────────────────┘
```

**G10a Widget References:**
```python
self.header_actions: FrameType | None = None
self.search_entry: EntryType | None = None
self.search_var: StringVar | None = None
self.search_btn: ButtonType | None = None
self.results_table: TreeviewType | None = None
self.status_label: LabelType | None = None
```

**G10b Controller Wiring:**
```python
def _wire_events(self) -> None:
    # Header buttons (created dynamically)
    if self.page.header_actions:
        refresh_btn = make_button(self.page.header_actions, text="Refresh", ...)
        refresh_btn.configure(command=self._on_refresh)
        refresh_btn.pack(side="right", padx=SPACING_SM)

    # Search
    if self.page.search_btn:
        self.page.search_btn.configure(command=self._on_search)
    if self.page.search_entry:
        self.page.search_entry.bind("<Return>", lambda e: self._on_search())

    # Table double-click → navigate to detail
    if self.page.results_table:
        self.page.results_table.bind("<Double-1>", self._on_row_double_click)

def _on_row_double_click(self, event: EventType | None = None) -> None:
    selected = get_selected_values(self.page.results_table)
    if selected:
        self.app.navigator.navigate("detail", params={"id": selected[0]["id"]})
```

---

## 🚫 Anti-Patterns — Never Do This

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| `import tkinter as tk` | Use type aliases from G02a |
| `ttk.Button(parent, text="Click")` | `make_button(parent, text="Click")` |
| `ttk.Label(parent, text="Hello")` | `make_label(parent, text="Hello")` |
| `ttk.Frame(parent)` | `make_frame(parent)` |
| `ttk.Entry(parent)` | `make_entry(parent)` |
| `tk.Toplevel(parent)` | `make_dialog(parent)` |
| `filedialog.askopenfilename()` | `ask_open_file()` |
| `messagebox.askyesno()` | `ask_yes_no()` |
| Button command in G10a | Wire command in G10b `_wire_events()` |
| Business logic in G10a | Put logic in G10b controller methods |
| Widget creation in G10b | Create widgets in G10a, wire in G10b |
| Import from G01 modules | Import from G02a (the facade) |
| `parent.grid_rowconfigure(0, weight=1)` | `grid_configure(parent, rows={0:1})` |

> **Note on G00a:** If you must annotate with `tk`/`ttk` types directly, import from `G00a_gui_packages` — but **never instantiate widgets directly**. Prefer the type aliases above (`EntryType`, `ButtonType`, etc.) which provide the same IDE support.

---

## 🔢 Module Reference

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| G02a | Widget primitives & facade | 70+ (factories, type aliases, dialogs) |
| G02b | Layout utilities | 8 (layout_row, grid_configure, etc.) |
| G03a | Layout patterns | 12 (page_layout, two_column_layout, etc.) |
| G03b | Container patterns | 13 (make_card, make_page_header, etc.) |
| G03c | Form patterns | 12 (form_field_entry, form_group, etc.) |
| G03d | Table patterns | 14 (create_table, insert_rows, etc.) |
| G03e | Widget components | 12 (filter_bar, metric_card, etc.) |
| G03f | Renderer protocol | 3 (PageProtocol, G03Renderer) |
| G04d | Application shell | 6 (AppShell, defaults) |

> *Export counts are indicative. `__all__` in each module's source code is authoritative.*

---

## 📁 Template Files

| File | Purpose |
|------|---------|
| `Gx0a_design_template.py` | Starting point for page design layer |
| `Gx0b_control_template.py` | Starting point for page controller layer |

**Numbering Scheme:**
```
G00-G04  = Framework (locked, shared by all GUIs)
G1x      = GUI 1 pages (G10a/b, G11a/b, G12a/b, ...)
G2x      = GUI 2 pages (G20a/b, G21a/b, G22a/b, ...)
...up to G9x
```

**Workflow:**
1. Copy both templates
2. Rename to match your GUI (e.g., `G10a_main_design.py`, `G10b_main_controller.py`)
3. Update placeholders: `{{FILENAME}}`, `{{AUTHOR}}`, `{{DATE}}`, etc.
4. Design layout in Gx0a, wire events in Gx0b
5. Run via Gx0b (the controller is the entry point)