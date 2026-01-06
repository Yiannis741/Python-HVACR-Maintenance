"""
UI helpers: small danger icon button + confirm dialog
Πρόταση για ασφαλέστερα κουμπιά διαγραφής / επικίνδυνων ενεργειών.
"""

import customtkinter as ctk
from tkinter import messagebox

def confirm_action(parent, title, message, on_confirm):
    """
    Απλή modal επιβεβαίωσης. Αν ο χρήστης απαντήσει Yes, καλείται το on_confirm().
    parent: widget (για να γίνει modal focus σωστά)
    title, message: κείμενα διάλογου
    on_confirm: callable χωρίς παραμέτρους
    """
    # μπορείς να χρησιμοποιήσεις custom dialog αν θες πιο ωραίο UI
    result = messagebox.askyesno(title, message, parent=parent, icon='warning')
    if result:
        try:
            on_confirm()
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Παρουσιάστηκε σφάλμα: {e}", parent=parent)
        return True
    return False


class SmallDangerButton(ctk.CTkButton):
    """
    Μικρό κουμπί-εικονίδιο για επικίνδυνες ενέργειες.
    Χρησιμοποιεί απλό emoji (🗑️) ή μπορείς να βάλεις FontAwesome icon αν έχεις.
    Σχεδιάστηκε για να αντικαταστήσει μεγάλα, επιθετικά danger buttons.
    """

    def __init__(self, parent, command=None, tooltip_text=None, **kwargs):
        theme = kwargs.pop("theme", None)
        # default small size
        super().__init__(
            parent,
            text="🗑️",        # μπορείς να αλλάξεις σε '' + image αν έχεις icon
            width=36,
            height=36,
            fg_color="transparent",
            hover=False,
            corner_radius=8,
            command=command,
            **kwargs
        )
        # text color red
        try:
            # αν χρησιμοποιείς theme_config, μπορείς να περάσεις χρώμα από εκεί
            self.configure(text_color="#C0392B")
        except Exception:
            pass

        # Προαιρετικό tooltip (πολύ απλό)
        if tooltip_text:
            self._create_tooltip(parent, tooltip_text)

    def _create_tooltip(self, parent, text):
        # πολύ απλό tooltip: εμφανίζει Toplevel όταν hover
        tip = None

        def on_enter(e):
            nonlocal tip
            if tip:
                return
            tip = ctk.CTkToplevel(parent)
            tip.overrideredirect(True)
            tip.wm_attributes("-topmost", True)
            lbl = ctk.CTkLabel(tip, text=text, font=("Segoe UI", 9), fg_color="#333", text_color="white")
            lbl.pack()
            x = parent.winfo_pointerx() + 10
            y = parent.winfo_pointery() + 10
            tip.geometry(f"+{x}+{y}")

        def on_leave(e):
            nonlocal tip
            if tip:
                tip.destroy()
                tip = None

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)