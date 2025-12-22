# GUI Pages — Gx0a/Gx0b Contract

> Decision guide for page development. Where does code belong?

---

## The Contract

| Layer | File | Owns | Never |
|-------|------|------|-------|
| **Design** | Gx0a | Widget creation, layout, visual structure | Business logic, event handlers, data operations |
| **Controller** | Gx0b | Event wiring, validation, business logic | Widget instantiation (except header_actions buttons) |

**One sentence:** Gx0a builds the UI and exposes handles. Gx0b grabs those handles and makes them do things.

---

## Numbering Scheme

```
G00-G04  = Framework (locked, shared by all GUIs)
G1x      = GUI 1 pages (G10a/b, G11a/b, G12a/b, ...)
G2x      = GUI 2 pages (G20a/b, G21a/b, G22a/b, ...)
G3x      = GUI 3 pages (G30a/b, G31a/b, G32a/b, ...)
...
G9x      = GUI 9 pages
```

**Template files use `Gx0` to indicate "copy and rename for your GUI".**

---

## Lifecycle

```
1. AppShell calls ControlledPage.__init__(controller=app_shell)
   └── Creates Gx0a design instance
   └── Creates Gx0b controller instance

2. AppShell calls ControlledPage.build(parent, params)
   └── Calls design.build(parent, params)
       └── Creates all widgets
       └── Stores references (self.example_btn, self.search_var, etc.)
       └── Returns root frame
   └── Calls controller.set_page(design)
       └── Stores page reference
       └── Calls _wire_events()
       └── Calls _initialise_state()

3. Page is now live — user interacts
   └── Events fire → controller handlers execute
   └── Handlers access widgets via self.page.widget_name
   └── Handlers access state via self.app.app_state
   └── Handlers navigate via self.app.navigator
```

---

## Decision Rules

### "Where does this code go?"

| If you need to... | Put it in | Why |
|-------------------|-----------|-----|
| Create a label, entry, button, frame | Gx0a | Widget creation = design |
| Set widget text, placeholder, initial value | Gx0a | Initial appearance = design |
| Define column weights, row heights | Gx0a | Layout structure = design |
| Configure colours, fonts, spacing | Gx0a | Visual styling = design |
| Respond to button click | Gx0b | Event handling = controller |
| Validate user input | Gx0b | Business rule = controller |
| Show/hide error message | Gx0b | Conditional logic = controller |
| Enable/disable a widget | Gx0b | State change = controller |
| Fetch data from API/database | Gx0b | Data operation = controller |
| Navigate to another page | Gx0b | App flow = controller |
| Update app_state | Gx0b | State management = controller |
| Add buttons to header_actions | Gx0b | Dynamic content wired to handlers |

### Quick Test

> "Does this code need to know what the user did or what the data contains?"
> - **Yes** → Gx0b (controller)
> - **No** → Gx0a (design)

---

## Widget Reference Pattern

**Gx0a declares and creates:**
```python
def __init__(self, controller: Any) -> None:
    # Declare references (None until build)
    self.search_entry: EntryType | None = None
    self.search_var: StringVar | None = None
    self.submit_btn: ButtonType | None = None

def build(self, parent: WidgetType, params: Dict[str, Any]) -> WidgetType:
    # Create and assign
    self.search_var = StringVar(value="")
    self.search_entry = make_entry(parent, textvariable=self.search_var)
    self.submit_btn = make_button(parent, text="Search")  # NO command here
```

**Gx0b wires and uses:**
```python
def _wire_events(self) -> None:
    if self.page.submit_btn is not None:
        self.page.submit_btn.configure(command=self._on_submit)
    if self.page.search_entry is not None:
        self.page.search_entry.bind("<Return>", lambda e: self._on_submit())

def _on_submit(self) -> None:
    value = self.page.search_var.get()
    # ... business logic ...
```

---

## ControlledPage Wrapper

The wrapper connects design + controller and implements `PageProtocol`:

```python
class ControlledSearchPage:
    """Register THIS with AppShell, not the raw design."""

    def __init__(self, controller: AppShell) -> None:
        self.app = controller
        self.design = SearchPageDesign(controller=controller)
        self.controller = SearchPageController(app=controller)

    def build(self, parent: WidgetType, params: Dict[str, Any]) -> WidgetType:
        frame = self.design.build(parent, params)
        self.controller.set_page(self.design)
        return frame
```

**Registration:**
```python
app.register_page("search", ControlledSearchPage)  # ✓ Correct
app.register_page("search", SearchPageDesign)      # ✗ No controller wiring
```

---

## Naming Convention

| Suffix | Type | Example |
|--------|------|---------|
| `_var` | StringVar, IntVar, BooleanVar | `self.name_var` |
| `_entry` | Entry field | `self.name_entry` |
| `_btn` | Button | `self.submit_btn` |
| `_combo` | Combobox | `self.category_combo` |
| `_check` | Checkbox | `self.enabled_check` |
| `_radio` | Radio button | `self.option_radio` |
| `_label` | Dynamic label | `self.status_label` |
| `_frame` | Frame reference | `self.results_frame` |
| `_table` / `_tree` | Treeview | `self.results_table` |

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `command=self._on_click` in Gx0a | Gx0a has no `_on_click` | Wire in Gx0b |
| `make_button(...)` in Gx0b | Widget creation in controller | Create in Gx0a, wire in Gx0b |
| Validation logic in Gx0a | Business rule in design | Move to Gx0b `_validate_*()` |
| `self.page.label.configure(text=...)` in Gx0a | Self-reference during build | Just set text directly |
| Forgetting `if widget is not None:` in Gx0b | Widget may not exist | Always guard references |
| Registering Gx0a with AppShell | No controller wiring | Register ControlledPage wrapper |

---

## File Pairing

```
gui/
├── Gx0a_design_template.py           ← Copy for new pages
├── Gx0b_control_template.py          ← Copy for new pages
│
├── G10a_main_design.py               ← GUI 1: Main page design
├── G10b_main_controller.py           ← GUI 1: Main page controller
├── G11a_settings_design.py           ← GUI 1: Settings page design
├── G11b_settings_controller.py       ← GUI 1: Settings page controller
│
├── G20a_dashboard_design.py          ← GUI 2: Dashboard page design
├── G20b_dashboard_controller.py      ← GUI 2: Dashboard page controller
├── G21a_reports_design.py            ← GUI 2: Reports page design
├── G21b_reports_controller.py        ← GUI 2: Reports page controller
```

**Rule:** Every Gx0a has a matching Gx0b. Run via Gx0b.

---

## Summary

| Principle | Rule |
|-----------|------|
| Separation | Gx0a = what it looks like. Gx0b = what it does. |
| References | Gx0a exposes. Gx0b consumes. |
| Events | Never wire in Gx0a. Always wire in Gx0b. |
| Entry point | Run Gx0b, not Gx0a (unless previewing layout). |
| Registration | Register `ControlledPage`, not raw design. |