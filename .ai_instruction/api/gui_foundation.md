# GUI Foundation Documentation

> **Layer:** G00–G02 (Foundational)  
> **Status:** Complete and Stable  
> **Last Updated:** 2026-01-01

---

## 1. Architecture Overview

The GUI framework follows a strict layered architecture where each layer builds upon the previous one. No layer may import from a higher-numbered layer.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         G03+ APPLICATION PAGES                       │
│                    (Consume G02, never modify it)                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           G02 PRIMITIVES                             │
├──────────────────────┬──────────────────────┬───────────────────────┤
│   G02a_widget_       │   G02b_layout_       │   G02c_gui_base       │
│   primitives         │   utils              │                       │
│   (factories)        │   (layout helpers)   │   (base window)       │
└──────────────────────┴──────────────────────┴───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         G01 STYLE RESOLVERS                          │
├────────────┬────────────┬────────────┬────────────┬─────────────────┤
│   G01c     │   G01d     │   G01e     │   G01f     │                 │
│   text     │   container│   input    │   control  │   (parallel)    │
└────────────┴────────────┴────────────┴────────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       G01b STYLE BASE                                │
│              (shared utilities, type aliases, re-exports)            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      G01a STYLE CONFIG                               │
│                (pure design tokens, Literal types)                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      G00a GUI PACKAGES                               │
│                  (tk, ttk, init_gui_theme, DateEntry)                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Inheritance Chains

### G01 Style Chain
```
G01a_style_config (pure tokens)
    ↓
G01b_style_base (utilities + re-exports)
    ↓
┌───────┬───────┬───────┬───────┐
G01c    G01d    G01e    G01f     ← parallel siblings
(text)  (container) (input) (control)
```

**Rule:** G01c/d/e/f import from G01b ONLY, never directly from G01a.

### G02 Primitive Chain
```
G01a + G01b
    ↓
G02a_widget_primitives  ← imports ALL G01 modules
    
G01a (tokens only)
    ↓
G02b_layout_utils       ← parallel to G02a (no cross-import)

G01a + G01b
    ↓
G02c_gui_base           ← parallel to G02a/G02b (no cross-import)
```

---

## 3. Module Reference

### G00a_gui_packages
**Purpose:** Central hub for GUI library imports.

| Export | Type | Description |
|--------|------|-------------|
| `tk` | module | tkinter |
| `ttk` | module | tkinter.ttk |
| `init_gui_theme()` | function | Initialise sv_ttk theme |
| `DateEntry` | class \| None | tkcalendar.DateEntry if available |

---

### G01a_style_config
**Purpose:** Pure design tokens with zero logic.

| Export | Type | Description |
|--------|------|-------------|
| `GUI_PRIMARY` | ColourFamily | Blue colour palette (LIGHT/MID/DARK/XDARK) |
| `GUI_SECONDARY` | ColourFamily | Grey colour palette |
| `GUI_SUCCESS` | ColourFamily | Green colour palette |
| `GUI_WARNING` | ColourFamily | Amber colour palette |
| `GUI_ERROR` | ColourFamily | Red colour palette |
| `TEXT_COLOURS` | dict | Named text colours (BLACK/WHITE/GREY/PRIMARY/etc.) |
| `SPACING_XS/SM/MD/LG/XL/XXL` | int | 4/8/16/24/32/48 pixels |
| `FONT_SIZES` | dict | DISPLAY/HEADING/TITLE/BODY/SMALL → int |
| `BORDER_WEIGHTS` | dict | NONE/THIN/MEDIUM/THICK → int |
| `GUI_FONT_FAMILY` | tuple | Preferred font stack |
| `GUI_FONT_FAMILY_MONO` | tuple | Monospace font stack |

**Literal Types:**
- `ShadeType` = "LIGHT" | "MID" | "DARK" | "XDARK"
- `SizeType` = "DISPLAY" | "HEADING" | "TITLE" | "BODY" | "SMALL"
- `TextColourType` = "BLACK" | "WHITE" | "GREY" | "PRIMARY" | "SECONDARY" | "SUCCESS" | "ERROR" | "WARNING"
- `SpacingType` = "XS" | "SM" | "MD" | "LG" | "XL" | "XXL"
- `BorderWeightType` = "NONE" | "THIN" | "MEDIUM" | "THICK"

---

### G01b_style_base
**Purpose:** Shared utilities and type re-exports.

| Export | Type | Description |
|--------|------|-------------|
| `ColourFamily` | TypeAlias | dict[ShadeType, str] |
| `resolve_colour()` | function | Resolve colour name → ColourFamily |
| `get_default_shade()` | function | Get default shade for a family |
| `resolve_text_font()` | function | Build font tuple from tokens |
| `resolve_font_family()` | function | Select available font from stack |

**Additional Literal Types:**
- `ContainerRoleType` = "PRIMARY" | "SECONDARY" | "SUCCESS" | "WARNING" | "ERROR"
- `ContainerKindType` = "SURFACE" | "CARD" | "PANEL" | "SECTION"
- `InputControlType` = "ENTRY" | "COMBOBOX" | "SPINBOX"
- `ControlWidgetType` = "BUTTON" | "CHECKBOX" | "RADIO" | "SWITCH"
- `ControlVariantType` = "PRIMARY" | "SECONDARY" | "SUCCESS" | "WARNING" | "ERROR"

---

### G01c_text_styles
**Purpose:** Text/label style resolution with caching.

| Export | Type | Description |
|--------|------|-------------|
| `resolve_text_style()` | function | Core resolver → style name |
| `text_style_heading()` | function | Convenience: HEADING size |
| `text_style_body()` | function | Convenience: BODY size |
| `text_style_small()` | function | Convenience: SMALL size |
| `text_style_error()` | function | Convenience: ERROR colour |
| `text_style_success()` | function | Convenience: SUCCESS colour |
| `text_style_warning()` | function | Convenience: WARNING colour |

---

### G01d_container_styles
**Purpose:** Container/frame style resolution with caching.

| Export | Type | Description |
|--------|------|-------------|
| `resolve_container_style()` | function | Core resolver → style name |
| `container_style_card()` | function | Convenience: raised relief |
| `container_style_panel()` | function | Convenience: solid relief |
| `container_style_section()` | function | Convenience: flat, thin border |
| `container_style_surface()` | function | Convenience: no border |

---

### G01e_input_styles
**Purpose:** Input field style resolution with caching.

| Export | Type | Description |
|--------|------|-------------|
| `resolve_input_style()` | function | Core resolver → style name |
| `input_style_entry_default()` | function | Convenience: default entry |
| `input_style_entry_error()` | function | Convenience: error state |
| `input_style_entry_success()` | function | Convenience: success state |
| `input_style_combobox_default()` | function | Convenience: default combobox |
| `input_style_spinbox_default()` | function | Convenience: default spinbox |

---

### G01f_control_styles
**Purpose:** Button/checkbox/radio style resolution with state handling.

| Export | Type | Description |
|--------|------|-------------|
| `resolve_control_style()` | function | Core resolver → style name |
| `control_button_primary/secondary/success/warning/error()` | functions | Button conveniences |
| `control_checkbox_primary/success()` | functions | Checkbox conveniences |
| `control_radio_primary/warning()` | functions | Radio conveniences |
| `control_switch_primary/error()` | functions | Switch conveniences |
| `debug_dump_button_styles()` | function | Debug utility |

---

### G02a_widget_primitives
**Purpose:** Unified widget API with factories and style wrappers.

**Style Wrappers (return style names):**
| Function | Maps To |
|----------|---------|
| `label_style()` | G01c.resolve_text_style() |
| `frame_style()` | G01d.resolve_container_style() |
| `entry_style()` | G01e.resolve_input_style() |
| `button_style()` | G01f.resolve_control_style() |

**Widget Factories (return widgets):**
| Function | Creates |
|----------|---------|
| `make_label()` | ttk.Label |
| `make_status_label()` | StatusLabel (toggles OK/error) |
| `make_frame()` | ttk.Frame (with .content attribute) |
| `make_entry()` | ttk.Entry |
| `make_combobox()` | ttk.Combobox |
| `make_spinbox()` | ttk.Spinbox |
| `make_date_picker()` | DateEntry or ttk.Entry fallback |
| `make_button()` | ttk.Button |
| `make_checkbox()` | ttk.Checkbutton |
| `make_radio()` | ttk.Radiobutton |
| `make_separator()` | ttk.Separator |
| `make_spacer()` | ttk.Frame (fixed size) |
| `make_textarea()` | tk.Text |
| `make_console()` | tk.Text (monospace, with scrollbar) |
| `make_scrollable_frame()` | ScrollableFrame (see below) |
| `make_notebook()` | ttk.Notebook |
| `make_treeview()` | ttk.Treeview |
| `make_zebra_treeview()` | ttk.Treeview (alternating rows) |

**ScrollableFrame (returned by `make_scrollable_frame()`):**

This is NOT a tuple. It's a Frame subclass with additional attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `.content` | ttk.Frame | Add children here, NOT to the outer frame |

```python
# Usage pattern:
scrollable = make_scrollable_frame(parent)
scrollable.pack(fill="both", expand=True)

# Add widgets to .content, not to scrollable directly
make_label(scrollable.content, text="Row 1").pack()
make_label(scrollable.content, text="Row 2").pack()
```

**Typography Helpers (return labels):**
| Function | Size | Bold |
|----------|------|------|
| `page_title()` | DISPLAY | Yes |
| `page_subtitle()` | TITLE | No |
| `section_title()` | TITLE | Yes |
| `body_text()` | BODY | No |
| `small_text()` | SMALL | No |
| `meta_text()` | SMALL | No (grey) |
| `divider()` | — | Separator |

**Re-exports:**
- `StringVar`, `BooleanVar`, `IntVar`, `DoubleVar`

---

### G02b_layout_utils
**Purpose:** Declarative layout helpers.

| Function | Description |
|----------|-------------|
| `layout_row()` | Frame with weighted columns |
| `layout_col()` | Frame with weighted rows |
| `grid_configure()` | Apply column/row weights declaratively |
| `stack_vertical()` | Pack widgets top-to-bottom with spacing |
| `stack_horizontal()` | Pack widgets left-to-right with spacing |
| `apply_padding()` | Add padding to already-placed widget |
| `fill_remaining()` | Configure row/column to expand |
| `center_in_parent()` | Center widget using place(). ⚠️ Do not use inside grid-managed containers. |

---

### G02c_gui_base
**Purpose:** Base window class with scroll engine.

| Member | Type | Description |
|--------|------|-------------|
| `root` | tk.Tk | Main window |
| `main_frame` | ttk.Frame | Scrollable content area |
| `content_frame` | ttk.Frame | Alias for main_frame |
| `canvas` | tk.Canvas | Scroll engine canvas |
| `build_widgets()` | method | Override in subclasses |
| `set_content()` | method | Replace visible content |
| `center_window()` | method | Center on screen |
| `toggle_fullscreen()` | method | Toggle fullscreen mode |
| `get_overlay_layer()` | method | Lazy-create overlay frame |
| `bind_scroll_widget()` | method | Bind scroll to specific widget |
| `run()` | method | Start mainloop |
| `close()` / `safe_close()` | methods | Destroy window |

---

## 4. Parameter Conventions

### Naming (British English)
All colour parameters use British spelling:
- `fg_colour` (not fg_color)
- `bg_colour` (not bg_color)
- `border_colour` (not border_color)

### Standard Parameter Order
All widget factories follow this order:

```python
def make_widget(
    parent: tk.Misc | tk.Widget,
    # 1. Content
    text: str = "",                          # or textvariable
    # 2. Widget-specific
    command: Callable | None = None,         # buttons/checkboxes
    variable: tk.Variable | None = None,     # checkboxes/radios
    value: str | int = "",                   # radios
    values: list[str] | None = None,         # comboboxes
    from_: float = 0,                        # spinboxes
    to: float = 100,                         # spinboxes
    width: int = 40,                         # text areas
    height: int = 10,                        # text areas
    # 3. Typography
    size: SizeType = "BODY",
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    # 4. Colours (fg before bg)
    fg_colour: TextColourType = "BLACK",
    bg_colour: str | ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    # 5. Border
    border_colour: str | ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    # 6. Spacing
    padding: SpacingType | None = "SM",
    indent: int = SPACING_SM,                # checkboxes/radios only
    # 7. Other
    font_family: str | None = None,
    readonly: bool = False,
    scrollbar: bool = True,
    # 8. Kwargs
    **kwargs: Any,
) -> Widget:
```

---

## 5. Section Structure Template

All GUI modules follow the numbered section pattern:

| Section | Title | Status |
|---------|-------|--------|
| **1** | System Imports | 🔒 LOCKED |
| **2** | Project Imports | 🔒 LOCKED |
| **3–97** | Implementation | 🔓 FLEXIBLE |
| **98** | Public API Surface | 🔒 LOCKED |
| **99** | Main Execution / Self-Test | 🔒 LOCKED |

### Section 99 Pattern
```python
def main() -> None:
    """
    Description:
        Self-test / smoke test for module.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Notes:
        - Test description here.
    """
    logger.info("[Gxx] Running smoke test...")
    # ... test code ...


if __name__ == "__main__":
    init_logging()
    main()
```

---

## 6. Usage Examples

### Creating a Styled Label
```python
from gui.G02a_widget_primitives import make_label

lbl = make_label(
    parent,
    text="Hello World",
    size="HEADING",
    bold=True,
    fg_colour="PRIMARY",
)
lbl.pack()
```

### Creating a Button with Callback
```python
from gui.G02a_widget_primitives import make_button

btn = make_button(
    parent,
    text="Click Me",
    command=on_click,
    fg_colour="WHITE",
    bg_colour="SUCCESS",
)
btn.pack()
```

### Creating a Card Frame
```python
from gui.G02a_widget_primitives import make_frame

card = make_frame(
    parent,
    kind="CARD",
    bg_colour="SECONDARY",
    bg_shade="LIGHT",
    border_colour="PRIMARY",
    border_weight="THIN",
    padding="MD",
)
card.pack(fill="x", pady=8)

# Add children to card.content, NOT card directly
make_label(card.content, text="Card Title").pack()
```

### Layout with Weighted Columns
```python
from gui.G02b_layout_utils import layout_row

row = layout_row(parent, weights=(1, 2, 1))
row.pack(fill="x")

ttk.Label(row, text="Left").grid(row=0, column=0, sticky="ew")
ttk.Label(row, text="Center (2x)").grid(row=0, column=1, sticky="ew")
ttk.Label(row, text="Right").grid(row=0, column=2, sticky="ew")
```

### Vertical Stacking with Spacing
```python
from gui.G02b_layout_utils import stack_vertical
from gui.G02a_widget_primitives import SPACING_SM, make_label

widgets = [
    make_label(parent, text="Line 1"),
    make_label(parent, text="Line 2"),
    make_label(parent, text="Line 3"),
]
stack_vertical(parent, widgets, spacing=SPACING_SM)
```

### Subclassing BaseWindow
```python
from gui.G02c_gui_base import BaseWindow
from gui.G02a_widget_primitives import page_title, make_button

class MyWindow(BaseWindow):
    def build_widgets(self) -> None:
        page_title(self.main_frame, text="My App").pack(pady=16)
        
        make_button(
            self.main_frame,
            text="Close",
            command=self.safe_close,
            bg_colour="PRIMARY",
        ).pack()


if __name__ == "__main__":
    app = MyWindow(title="My App", width=800, height=600)
    app.center_window()
    app.run()
```

---

## 7. Design Decisions

### Why the Re-Export Chain? (Facade Pattern)

The architecture follows a deliberate re-export chain: G01a → G01b → G02a → G03+

```
G01a (pure tokens)     ← defines SPACING_SM, ShadeType, etc.
  ↓ re-exports
G01b (+ utilities)     ← adds resolve_colour(), re-exports G01a
  ↓ re-exports  
G02a (+ widget factories) ← adds make_label(), re-exports G01b
  ↓
G03+ (consumers)       ← imports ONLY from G02a
```

**Rationale:**

1. **Single import point** — G03 developers only need `from gui.G02a_widget_primitives import ...`. No need to remember which tokens live in G01a vs G01b.

2. **Implementation hiding** — G03 doesn't know or care that `SPACING_SM` originates in G01a. If G01a is refactored (split, renamed, merged), G03 code is untouched as long as G02a maintains its exports.

3. **Consistent naming** — G01b can re-export with normalised naming. Internal quirks stay internal.

4. **Swap-ability** — The entire G01 layer could be replaced (different theme system) without G03 noticing, as long as G02a's contract stays the same.

5. **Reduced cognitive load** — One namespace instead of hunting across modules:
   ```python
   # ❌ Without facade (scattered imports)
   from gui.G01a_style_config import SPACING_SM
   from gui.G01b_style_base import resolve_colour
   from gui.G02a_widget_primitives import make_label
   
   # ✅ With facade (single source)
   from gui.G02a_widget_primitives import SPACING_SM, resolve_colour, make_label
   ```

This is the same principle as Python packages using `__init__.py` to re-export from submodules — the internal structure is an implementation detail, the public API is what matters.

### G02a Contract Boundaries

G02a widget factories have explicit limits on what they do and don't do:

| G02a Does | G02a Does NOT |
|-----------|---------------|
| Create and configure widgets | Apply geometry managers |
| Apply ttk styles | Call `.pack()`, `.grid()`, or `.place()` |
| Return widget instances | Store global references |
| Accept parent as first argument | Call `.mainloop()` |

**Key boundaries:**

1. **Geometry is caller's responsibility** — G02a returns widgets; the caller decides how to place them with `.pack()`, `.grid()`, or `.place()`. This keeps layout decisions in G03 page code where they belong.

2. **No `.mainloop()` calls** — Only G02c's `BaseWindow.run()` should start the event loop. G02a factories are stateless widget constructors.

3. **No global state** — G02a doesn't cache widget instances or maintain registries. Every call returns a fresh widget. The caller owns the reference.

```python
# ✅ Correct — caller controls geometry
btn = make_button(parent, text="Save", bg_colour="PRIMARY")
btn.pack(side="right", padx=SPACING_SM)  # Caller's decision

# ❌ Wrong mental model — G02a doesn't do this internally
# make_button(...).pack(...)  # G02a never calls pack()
```

### Why British Spelling?
Project convention established early. All new code uses `colour` not `color`.

### Why Separate G01 Modules?
Each G01c/d/e/f module handles a distinct widget category with its own caching strategy. This keeps cache keys isolated and prevents style name collisions.

### Why G02a Wraps G01?
G02a provides a single import point for G03+ pages. Instead of importing from 4+ G01 modules, pages import from G02a only.

### Why main() Wrapper in Section 99?
Ensures no side-effects at import time. The `main()` function is explicit and testable.

### Why No Cross-Imports Between G02a/G02b/G02c?
They serve different purposes and may be used independently. G02a (widgets), G02b (layout), G02c (windows) are parallel utilities.

---

## 8. Quick Reference

### Import Patterns

**For G03 Pages:**
```python
from gui.G02a_widget_primitives import (
    make_label, make_button, make_frame, make_entry,
    page_title, section_title, body_text,
    StringVar, BooleanVar,
    SPACING_SM, SPACING_MD, SPACING_LG,
    ShadeType, SpacingType, ContainerRoleType,
)
from gui.G02b_layout_utils import layout_row, stack_vertical
from gui.G02c_gui_base import BaseWindow
```

**Never Do This in G03:**
```python
# ❌ Don't import tokens directly from G01a
from gui.G01a_style_config import SPACING_SM  # Wrong!

# ❌ Don't import from G01c/d/e/f directly
from gui.G01c_text_styles import resolve_text_style  # Wrong!

# ✅ Use G02a re-exports instead
from gui.G02a_widget_primitives import SPACING_SM, label_style  # Correct!
```

### Colour Families
| Family | LIGHT | MID | DARK | XDARK |
|--------|-------|-----|------|-------|
| PRIMARY | Light blue | Blue | Dark blue | Navy |
| SECONDARY | Light grey | Grey | Dark grey | Charcoal |
| SUCCESS | Light green | Green | Dark green | Forest |
| WARNING | Light amber | Amber | Dark amber | Orange |
| ERROR | Light red | Red | Dark red | Maroon |

### Spacing Scale
| Token | Pixels | Use Case |
|-------|--------|----------|
| XS | 4 | Tight spacing |
| SM | 8 | Default element spacing |
| MD | 16 | Standard padding |
| LG | 24 | Card padding |
| XL | 32 | Page margins |
| XXL | 48 | Major sections |

---

*End of GUI Foundation Documentation*