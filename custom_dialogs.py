"""
Custom Themed Dialogs - Αντικατάσταση των Windows Messageboxes
================================================================

Όμορφα, themed dialogs που ταιριάζουν με την εφαρμογή σας!

ΧΡΗΣΗ:
    from custom_dialogs import show_info, show_error, show_warning, ask_yes_no
    
    # Αντί για:
    # messagebox.showinfo("Τίτλος", "Μήνυμα")
    
    # Χρησιμοποιήστε:
    # show_info("Τίτλος", "Μήνυμα")
"""

import customtkinter as ctk
import theme_config


class CustomDialog(ctk.CTkToplevel):
    """Base class για custom dialogs"""
    
    def __init__(self, parent, title, message, dialog_type="info", buttons=None):
        """
        Args:
            parent: Parent window
            title: Τίτλος dialog
            message: Μήνυμα
            dialog_type: "info", "error", "warning", "question"
            buttons: List of (text, callback) tuples
        """
        super().__init__(parent)
        
        self.result = None
        self.theme = theme_config.get_current_theme()
        
        # Window setup
        self.title(title)
        self.geometry("500x320")
        self.resizable(False, False)
        self.configure(fg_color=self.theme["bg_primary"])
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent(parent)
        
        # Build UI
        self.create_ui(title, message, dialog_type, buttons)
        
        # Focus
        self.focus()
    
    def center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()
        
        # Get parent position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        # Calculate center position (higher up to avoid cut-off)
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 3  # Higher: //3 instead of //2
        
        self.geometry(f"+{x}+{y}")
    
    def create_ui(self, title, message, dialog_type, buttons):
        """Create dialog UI"""
        
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ═══════════════════════════════════════════════════════════
        # ICON & TITLE ROW
        # ═══════════════════════════════════════════════════════════
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Icon
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "question": "❓"
        }
        
        color_map = {
            "info": self.theme["accent_blue"],
            "success": self.theme["accent_green"],
            "error": self.theme["accent_red"],
            "warning": self.theme["accent_orange"],
            "question": self.theme["accent_blue"]
        }
        
        icon = icon_map.get(dialog_type, "ℹ️")
        color = color_map.get(dialog_type, self.theme["accent_blue"])
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=theme_config.get_font("title", "bold"),
            text_color=color
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title_label.pack(side="left")
        
        # ═══════════════════════════════════════════════════════════
        # MESSAGE
        # ═══════════════════════════════════════════════════════════
        message_frame = ctk.CTkFrame(
            container,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_color=self.theme["card_border"],
            border_width=1
        )
        message_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=theme_config.get_font("body"),
            text_color=self.theme["text_primary"],
            wraplength=380,
            justify="left"
        )
        message_label.pack(padx=15, pady=15)
        
        # ═══════════════════════════════════════════════════════════
        # BUTTONS
        # ═══════════════════════════════════════════════════════════
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        if buttons:
            # Custom buttons
            for btn_text, btn_callback in buttons:
                btn = ctk.CTkButton(
                    buttons_frame,
                    text=btn_text,
                    command=lambda cb=btn_callback: self.on_button_click(cb),
                    width=120,
                    height=40,
                    **theme_config.get_button_style("primary")
                )
                btn.pack(side="right", padx=5)
        else:
            # Default OK button
            ok_btn = ctk.CTkButton(
                buttons_frame,
                text="OK",
                command=self.on_ok,
                width=120,
                height=40,
                **theme_config.get_button_style("primary")
            )
            ok_btn.pack(side="right")
        
        # Bind Escape to close
        self.bind("<Escape>", lambda e: self.on_cancel())
        
        # Bind Enter to OK (if single button)
        if not buttons or len(buttons) == 1:
            self.bind("<Return>", lambda e: self.on_ok())
    
    def on_button_click(self, callback):
        """Handle button click"""
        self.result = callback()
        self.destroy()
    
    def on_ok(self):
        """Handle OK button"""
        self.result = True
        self.destroy()
    
    def on_cancel(self):
        """Handle Cancel/Escape"""
        self.result = False
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS - Drop-in replacements για messagebox
# ═══════════════════════════════════════════════════════════════════════════

def show_info(title, message, parent=None):
    """
    Εμφάνιση info dialog.
    
    Drop-in replacement για: messagebox.showinfo(title, message)
    """
    if parent is None:
        import tkinter as tk
        parent = tk._default_root
    
    dialog = CustomDialog(parent, title, message, dialog_type="info")
    parent.wait_window(dialog)
    return dialog.result


def show_success(title, message, parent=None):
    """
    Εμφάνιση success dialog.
    
    Παρόμοιο με showinfo αλλά με success styling.
    """
    if parent is None:
        import tkinter as tk
        parent = tk._default_root
    
    dialog = CustomDialog(parent, title, message, dialog_type="success")
    parent.wait_window(dialog)
    return dialog.result


def show_error(title, message, parent=None):
    """
    Εμφάνιση error dialog.
    
    Drop-in replacement για: messagebox.showerror(title, message)
    """
    if parent is None:
        import tkinter as tk
        parent = tk._default_root
    
    dialog = CustomDialog(parent, title, message, dialog_type="error")
    parent.wait_window(dialog)
    return dialog.result


def show_warning(title, message, parent=None):
    """
    Εμφάνιση warning dialog.
    
    Drop-in replacement για: messagebox.showwarning(title, message)
    """
    if parent is None:
        import tkinter as tk
        parent = tk._default_root
    
    dialog = CustomDialog(parent, title, message, dialog_type="warning")
    parent.wait_window(dialog)
    return dialog.result


def ask_yes_no(title, message, parent=None):
    """
    Εμφάνιση Yes/No dialog.
    
    Drop-in replacement για: messagebox.askyesno(title, message)
    
    Returns:
        bool: True αν ο χρήστης πάτησε "Ναι", False αλλιώς
    """
    if parent is None:
        import tkinter as tk
        parent = tk._default_root
    
    # Custom buttons
    buttons = [
        ("Όχι", lambda: False),
        ("Ναι", lambda: True)
    ]
    
    dialog = CustomDialog(parent, title, message, dialog_type="question", buttons=buttons)
    parent.wait_window(dialog)
    
    return dialog.result if dialog.result is not None else False


def ask_ok_cancel(title, message, parent=None):
    """
    Εμφάνιση OK/Cancel dialog.
    
    Drop-in replacement για: messagebox.askokcancel(title, message)
    
    Returns:
        bool: True αν ο χρήστης πάτησε "OK", False αλλιώς
    """
    if parent is None:
        import tkinter as tk
        parent = tk._default_root
    
    # Custom buttons
    buttons = [
        ("Ακύρωση", lambda: False),
        ("OK", lambda: True)
    ]
    
    dialog = CustomDialog(parent, title, message, dialog_type="question", buttons=buttons)
    parent.wait_window(dialog)
    
    return dialog.result if dialog.result is not None else False


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Test custom dialogs
    """
    import customtkinter as ctk
    
    app = ctk.CTk()
    app.title("Custom Dialogs Test")
    app.geometry("400x300")
    
    def test_info():
        show_info("Πληροφορία", "Αυτό είναι ένα info dialog!")
    
    def test_success():
        show_success("Επιτυχία", "Η εργασία ολοκληρώθηκε με επιτυχία!")
    
    def test_error():
        show_error("Σφάλμα", "Κάτι πήγε στραβά!")
    
    def test_warning():
        show_warning("Προειδοποίηση", "Προσοχή! Αυτή η ενέργεια είναι μη αναστρέψιμη.")
    
    def test_yes_no():
        result = ask_yes_no("Επιβεβαίωση", "Θέλετε να συνεχίσετε;")
        print(f"User clicked: {'Yes' if result else 'No'}")
    
    # Buttons
    ctk.CTkButton(app, text="Test Info", command=test_info).pack(pady=10)
    ctk.CTkButton(app, text="Test Success", command=test_success).pack(pady=10)
    ctk.CTkButton(app, text="Test Error", command=test_error).pack(pady=10)
    ctk.CTkButton(app, text="Test Warning", command=test_warning).pack(pady=10)
    ctk.CTkButton(app, text="Test Yes/No", command=test_yes_no).pack(pady=10)
    
    app.mainloop()
