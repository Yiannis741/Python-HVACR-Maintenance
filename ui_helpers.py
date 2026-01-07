"""
UI Helpers - Reusable UI component factories και helper functions
"""

import customtkinter as ctk
from typing import Optional, Callable, Any, Dict
import theme_config
from config import UIConfig, FontConfig


# ═══════════════════════════════════════════════════════════════════════════
# LABEL FACTORIES
# ═══════════════════════════════════════════════════════════════════════════

def create_form_label(parent: ctk.CTkFrame, text: str, row: int, column: int = 0,
                     columnspan: int = 1, **kwargs) -> ctk.CTkLabel:
    """
    Factory για form labels με consistent styling.
    
    Args:
        parent: Parent widget
        text: Το κείμενο του label
        row: Grid row
        column: Grid column (default: 0)
        columnspan: Grid columnspan (default: 1)
        **kwargs: Extra grid options
    
    Returns:
        CTkLabel: Το δημιουργημένο label
    
    Example:
        >>> label = create_form_label(frame, "Όνομα Μονάδας:", row=0, column=0)
    """
    theme = theme_config.get_current_theme()
    
    label = ctk.CTkLabel(
        parent,
        text=text,
        font=theme_config.get_font("body", "bold"),
        text_color=theme["text_primary"]
    )
    
    label.grid(
        row=row,
        column=column,
        columnspan=columnspan,
        sticky="w",
        padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_SMALL),
        pady=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_SMALL),
        **kwargs
    )
    
    return label


def create_section_title(parent: ctk.CTkFrame, text: str, icon: str = "",
                        pack_kwargs: Optional[Dict] = None) -> ctk.CTkLabel:
    """
    Factory για section titles με consistent styling.
    
    Args:
        parent: Parent widget
        text: Το κείμενο του title
        icon: Optional emoji icon
        pack_kwargs: Extra pack options
    
    Returns:
        CTkLabel: Το δημιουργημένο label
    
    Example:
        >>> title = create_section_title(frame, "Στοιχεία Μονάδας", icon="🏢")
    """
    theme = theme_config.get_current_theme()
    pack_kwargs = pack_kwargs or {}
    
    full_text = f"{icon} {text}" if icon else text
    
    label = ctk.CTkLabel(
        parent,
        text=full_text,
        font=theme_config.get_font("heading", "bold"),
        text_color=theme["accent_blue"]
    )
    
    default_pack = {
        "anchor": "w",
        "padx": UIConfig.PADDING_LARGE,
        "pady": (UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM)
    }
    default_pack.update(pack_kwargs)
    
    label.pack(**default_pack)
    
    return label


def create_info_label(parent: ctk.CTkFrame, text: str, 
                     pack_kwargs: Optional[Dict] = None) -> ctk.CTkLabel:
    """
    Factory για info/secondary labels.
    
    Args:
        parent: Parent widget
        text: Το κείμενο
        pack_kwargs: Extra pack options
    
    Returns:
        CTkLabel: Το δημιουργημένο label
    
    Example:
        >>> info = create_info_label(frame, "Επιλέξτε μια ομάδα από τη λίστα")
    """
    theme = theme_config.get_current_theme()
    pack_kwargs = pack_kwargs or {}
    
    label = ctk.CTkLabel(
        parent,
        text=text,
        font=theme_config.get_font("small"),
        text_color=theme["text_secondary"]
    )
    
    default_pack = {
        "anchor": "w",
        "padx": UIConfig.PADDING_LARGE,
        "pady": UIConfig.PADDING_SMALL
    }
    default_pack.update(pack_kwargs)
    
    label.pack(**default_pack)
    
    return label


# ═══════════════════════════════════════════════════════════════════════════
# INPUT FACTORIES
# ═══════════════════════════════════════════════════════════════════════════

def create_form_entry(parent: ctk.CTkFrame, row: int, column: int = 0,
                     columnspan: int = 1, width: Optional[int] = None,
                     placeholder: str = "", **kwargs) -> ctk.CTkEntry:
    """
    Factory για form entry fields με consistent styling.
    
    Args:
        parent: Parent widget
        row: Grid row
        column: Grid column
        columnspan: Grid columnspan
        width: Entry width (default: από config)
        placeholder: Placeholder text
        **kwargs: Extra grid/entry options
    
    Returns:
        CTkEntry: Το δημιουργημένο entry
    
    Example:
        >>> entry = create_form_entry(frame, row=1, column=0, placeholder="Εισάγετε όνομα")
    """
    width = width or UIConfig.FORM_INPUT_WIDTH
    
    entry = ctk.CTkEntry(
        parent,
        width=width,
        height=UIConfig.FORM_INPUT_HEIGHT,
        font=theme_config.get_font("input"),
        placeholder_text=placeholder
    )
    
    entry.grid(
        row=row,
        column=column,
        columnspan=columnspan,
        sticky="ew",
        padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_SMALL),
        pady=(0, UIConfig.PADDING_LARGE),
        **kwargs
    )
    
    return entry


def create_form_combobox(parent: ctk.CTkFrame, values: list, row: int, column: int = 0,
                        columnspan: int = 1, width: Optional[int] = None,
                        command: Optional[Callable] = None, **kwargs) -> ctk.CTkComboBox:
    """
    Factory για form combobox με consistent styling.
    
    Args:
        parent: Parent widget
        values: Οι επιλογές
        row: Grid row
        column: Grid column
        columnspan: Grid columnspan
        width: Combobox width (default: από config)
        command: Callback function
        **kwargs: Extra options
    
    Returns:
        CTkComboBox: Το δημιουργημένο combobox
    
    Example:
        >>> combo = create_form_combobox(frame, ["Option 1", "Option 2"], row=1)
    """
    width = width or UIConfig.FORM_INPUT_WIDTH
    
    combobox = ctk.CTkComboBox(
        parent,
        values=values,
        width=width,
        height=UIConfig.FORM_INPUT_HEIGHT,
        font=theme_config.get_font("input"),
        state="readonly",
        command=command
    )
    
    combobox.grid(
        row=row,
        column=column,
        columnspan=columnspan,
        sticky="ew",
        padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_SMALL),
        pady=(0, UIConfig.PADDING_LARGE),
        **kwargs
    )
    
    if values:
        combobox.set(values[0])
    
    return combobox


def create_form_textbox(parent: ctk.CTkFrame, row: int, column: int = 0,
                       columnspan: int = 2, height: Optional[int] = None,
                       **kwargs) -> ctk.CTkTextbox:
    """
    Factory για form textbox με consistent styling.
    
    Args:
        parent: Parent widget
        row: Grid row
        column: Grid column
        columnspan: Grid columnspan
        height: Textbox height (default: από config)
        **kwargs: Extra options
    
    Returns:
        CTkTextbox: Το δημιουργημένο textbox
    
    Example:
        >>> textbox = create_form_textbox(frame, row=3, columnspan=2)
    """
    height = height or UIConfig.FORM_TEXTBOX_HEIGHT
    
    textbox = ctk.CTkTextbox(
        parent,
        height=height,
        font=theme_config.get_font("input")
    )
    
    textbox.grid(
        row=row,
        column=column,
        columnspan=columnspan,
        sticky="ew",
        padx=UIConfig.PADDING_MEDIUM,
        pady=(0, UIConfig.PADDING_LARGE),
        **kwargs
    )
    
    return textbox


# ═══════════════════════════════════════════════════════════════════════════
# BUTTON FACTORIES
# ═══════════════════════════════════════════════════════════════════════════

def create_styled_button(parent: ctk.CTkFrame, text: str, command: Callable,
                        style_type: str = "primary", width: Optional[int] = None,
                        height: Optional[int] = None, **kwargs) -> ctk.CTkButton:
    """
    Factory για styled buttons με consistent styling.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Callback function
        style_type: "primary", "success", "danger", "secondary", "special"
        width: Button width (default: από config)
        height: Button height (default: από config)
        **kwargs: Extra button options
    
    Returns:
        CTkButton: Το δημιουργημένο button
    
    Example:
        >>> btn = create_styled_button(frame, "Αποθήκευση", on_save, "success")
    """
    width = width or UIConfig.FORM_BUTTON_WIDTH
    height = height or UIConfig.FORM_BUTTON_HEIGHT
    
    style = theme_config.get_button_style(style_type)
    
    button = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        font=theme_config.get_font("body", "bold"),
        **style,
        **kwargs
    )
    
    return button


def create_button_row(parent: ctk.CTkFrame, buttons_config: list,
                     pack_kwargs: Optional[Dict] = None) -> ctk.CTkFrame:
    """
    Factory για button row με πολλαπλά buttons.
    
    Args:
        parent: Parent widget
        buttons_config: List of tuples (text, command, style_type)
        pack_kwargs: Extra pack options για το container frame
    
    Returns:
        CTkFrame: Το container frame με τα buttons
    
    Example:
        >>> buttons = [
        ...     ("Αποθήκευση", on_save, "success"),
        ...     ("Ακύρωση", on_cancel, "secondary"),
        ...     ("Διαγραφή", on_delete, "danger")
        ... ]
        >>> btn_row = create_button_row(frame, buttons)
    """
    pack_kwargs = pack_kwargs or {}
    
    button_frame = ctk.CTkFrame(parent, fg_color="transparent")
    
    default_pack = {
        "pady": (UIConfig.PADDING_MEDIUM, UIConfig.PADDING_LARGE)
    }
    default_pack.update(pack_kwargs)
    
    button_frame.pack(**default_pack)
    
    for idx, (text, command, style_type) in enumerate(buttons_config):
        btn = create_styled_button(
            button_frame,
            text=text,
            command=command,
            style_type=style_type
        )
        
        padx = (0, UIConfig.PADDING_MEDIUM) if idx < len(buttons_config) - 1 else 0
        btn.pack(side="left", padx=padx)
    
    return button_frame


# ═══════════════════════════════════════════════════════════════════════════
# CARD FACTORIES
# ═══════════════════════════════════════════════════════════════════════════

def create_card_frame(parent: ctk.CTkFrame, pack_kwargs: Optional[Dict] = None,
                     **frame_kwargs) -> ctk.CTkFrame:
    """
    Factory για card frames με consistent styling.
    
    Args:
        parent: Parent widget
        pack_kwargs: Pack options
        **frame_kwargs: Extra frame options
    
    Returns:
        CTkFrame: Το card frame
    
    Example:
        >>> card = create_card_frame(container)
        >>> create_section_title(card, "Στοιχεία")
    """
    theme = theme_config.get_current_theme()
    pack_kwargs = pack_kwargs or {}
    
    card = ctk.CTkFrame(
        parent,
        corner_radius=UIConfig.CORNER_RADIUS_LARGE,
        fg_color=theme["card_bg"],
        border_color=theme["card_border"],
        border_width=UIConfig.BORDER_WIDTH_THIN,
        **frame_kwargs
    )
    
    default_pack = {
        "fill": "x",
        "pady": (0, UIConfig.PADDING_LARGE)
    }
    default_pack.update(pack_kwargs)
    
    card.pack(**default_pack)
    
    return card


def create_stat_card(parent: ctk.CTkFrame, title: str, value: Any, column: int,
                    icon: str = "") -> ctk.CTkFrame:
    """
    Factory για statistic cards.
    
    Args:
        parent: Parent widget
        title: Card title
        value: Stat value
        column: Grid column
        icon: Optional emoji icon
    
    Returns:
        CTkFrame: Το stat card
    
    Example:
        >>> card = create_stat_card(grid_frame, "Σύνολο Μονάδων", 42, column=0, icon="📊")
    """
    theme = theme_config.get_current_theme()
    
    card = ctk.CTkFrame(
        parent,
        corner_radius=UIConfig.CORNER_RADIUS_LARGE,
        fg_color=theme["card_bg"],
        border_color=theme["card_border"],
        border_width=UIConfig.BORDER_WIDTH_THIN
    )
    
    card.grid(
        row=0,
        column=column,
        padx=UIConfig.PADDING_LARGE,
        pady=UIConfig.PADDING_LARGE,
        sticky="ew"
    )
    
    # Value
    value_text = f"{icon} {value}" if icon else str(value)
    value_label = ctk.CTkLabel(
        card,
        text=value_text,
        font=theme_config.get_font("stat_value", "bold"),
        text_color=theme["accent_blue"]
    )
    value_label.pack(pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL))
    
    # Title
    title_label = ctk.CTkLabel(
        card,
        text=title,
        font=theme_config.get_font("body"),
        text_color=theme["text_secondary"]
    )
    title_label.pack(pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_LARGE))
    
    return card


# ═══════════════════════════════════════════════════════════════════════════
# DIALOG HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def show_error_dialog(parent: Any, title: str, message: str) -> None:
    """
    Helper για error dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Error message
    
    Example:
        >>> show_error_dialog(self, "Σφάλμα", "Δεν βρέθηκε η εγγραφή")
    """
    from tkinter import messagebox
    messagebox.showerror(title, message, parent=parent)


def show_info_dialog(parent: Any, title: str, message: str) -> None:
    """
    Helper για info dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Info message
    
    Example:
        >>> show_info_dialog(self, "Επιτυχία", "Η εγγραφή αποθηκεύτηκε")
    """
    from tkinter import messagebox
    messagebox.showinfo(title, message, parent=parent)


def show_confirm_dialog(parent: Any, title: str, message: str) -> bool:
    """
    Helper για confirm dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Confirmation message
    
    Returns:
        bool: True αν ο χρήστης επιβεβαίωσε
    
    Example:
        >>> if show_confirm_dialog(self, "Επιβεβαίωση", "Διαγραφή εγγραφής;"):
        ...     delete_record()
    """
    from tkinter import messagebox
    return messagebox.askyesno(title, message, parent=parent, icon='question')


# ═══════════════════════════════════════════════════════════════════════════
# SEPARATOR HELPER
# ═══════════════════════════════════════════════════════════════════════════

def create_separator(parent: ctk.CTkFrame, pack_kwargs: Optional[Dict] = None) -> ctk.CTkFrame:
    """
    Factory για horizontal separator line.
    
    Args:
        parent: Parent widget
        pack_kwargs: Pack options
    
    Returns:
        CTkFrame: Το separator frame
    
    Example:
        >>> sep = create_separator(container)
    """
    theme = theme_config.get_current_theme()
    pack_kwargs = pack_kwargs or {}
    
    separator = ctk.CTkFrame(
        parent,
        height=2,
        fg_color=theme["card_border"]
    )
    
    default_pack = {
        "fill": "x",
        "padx": UIConfig.PADDING_LARGE,
        "pady": UIConfig.PADDING_LARGE
    }
    default_pack.update(pack_kwargs)
    
    separator.pack(**default_pack)
    
    return separator


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=== UI Helpers Usage Examples ===\n")
    
    print("1. Create form label:")
    print("   label = create_form_label(frame, 'Όνομα:', row=0, column=0)")
    
    print("\n2. Create form entry:")
    print("   entry = create_form_entry(frame, row=1, column=0, placeholder='Εισάγετε όνομα')")
    
    print("\n3. Create styled button:")
    print("   btn = create_styled_button(frame, 'Αποθήκευση', on_save, 'success')")
    
    print("\n4. Create button row:")
    print("   buttons = [")
    print("       ('Αποθήκευση', on_save, 'success'),")
    print("       ('Ακύρωση', on_cancel, 'secondary')")
    print("   ]")
    print("   btn_row = create_button_row(frame, buttons)")
    
    print("\n5. Create card:")
    print("   card = create_card_frame(container)")
    print("   create_section_title(card, 'Στοιχεία Μονάδας', icon='🏢')")
    
    print("\n6. Show dialog:")
    print("   if show_confirm_dialog(self, 'Επιβεβαίωση', 'Διαγραφή;'):")
    print("       delete_record()")
