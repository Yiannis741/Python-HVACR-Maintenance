"""
Date Picker Dialog Component
=============================
Calendar picker dialog για επιλογή ημερομηνίας

Extracted από ui_components.py για καλύτερη οργάνωση.
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from tkcalendar import Calendar
import theme_config
import utils_refactored


class DatePickerDialog(ctk.CTkToplevel):
    """Calendar picker dialog για επιλογή ημερομηνίας"""

    def __init__(self, parent, current_date=None, callback=None):
        super().__init__(parent)

        self.callback = callback
        self.selected_date = None

        self.title("📅 Επιλογή Ημερομηνίας")
        self.geometry("400x450")
        self.resizable(False, False)
        self.grab_set()

        # Parse current date
        if current_date:
            try:
                db_date = utils_refactored.format_date_for_db(current_date)
                self.current_date = datetime.strptime(db_date, "%Y-%m-%d")
            except:
                self.current_date = datetime.now()
        else:
            self.current_date = datetime.now()

        self.create_ui()

        # Center the dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_ui(self):
        """Δημιουργία UI"""

        theme = theme_config.get_current_theme()

        # Header
        header = ctk.CTkLabel(
            self,
            text="📅 Επιλέξτε Ημερομηνία",
            font=theme_config.get_font("heading", "bold")
        )
        header.pack(pady=(20, 10))

        # Quick selection buttons
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(pady=10)

        quick_buttons = [
            ("Σήμερα", 0),
            ("Χθες", -1),
            ("Προχθές", -2),
            ("Πριν 3 μέρες", -3),
            ("Πριν 1 εβδομάδα", -7),
        ]

        for text, days_offset in quick_buttons:
            btn = ctk.CTkButton(
                quick_frame,
                text=text,
                command=lambda d=days_offset: self.select_quick_date(d),
                width=120,
                height=32,
                **theme_config.get_button_style("primary")
            )
            btn.pack(side="left", padx=3)

        # Calendar widget
        cal_frame = ctk.CTkFrame(self)
        cal_frame.pack(pady=15, padx=20, fill="both", expand=True)

        self.calendar = Calendar(
            cal_frame,
            selectmode='day',
            year=self.current_date.year,
            month=self.current_date.month,
            day=self.current_date.day,
            date_pattern='yyyy-mm-dd',
            background=theme["card_bg"],
            foreground=theme["text_primary"],
            selectbackground=theme["accent_blue"],
            selectforeground="white",
            normalbackground=theme["bg_secondary"],
            normalforeground=theme["text_primary"],
            weekendbackground=theme["bg_tertiary"],
            weekendforeground=theme["text_secondary"],
            headersbackground=theme["accent_blue"],
            headersforeground="white",
            bordercolor=theme["card_border"],
            font=("Segoe UI", 10),
            headersfontt=("Segoe UI", 10, "bold")
        )
        self.calendar.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ok_btn = ctk.CTkButton(
            btn_frame,
            text="✔️ Επιλογή",
            command=self.confirm_selection,
            width=140,
            height=40,
            **theme_config.get_button_style("success")
        )
        ok_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="✖ Ακύρωση",
            command=self.destroy,
            width=140,
            height=40,
            **theme_config.get_button_style("secondary")
        )
        cancel_btn.pack(side="left", padx=5)

    def select_quick_date(self, days_offset):
        """Επιλογή γρήγορης ημερομηνίας"""
        target_date = datetime.now() + timedelta(days=days_offset)
        self.calendar.selection_set(target_date)

    def confirm_selection(self):
        """Επιβεβαίωση επιλογής"""
        # Get date from calendar (yyyy-mm-dd format)
        calendar_date = self.calendar.get_date()
        # Convert to display format (DD/MM/YY)
        date_obj = datetime.strptime(calendar_date, '%Y-%m-%d')
        display_date = date_obj.strftime('%d/%m/%y')

        if self.callback:
            self.callback(display_date)
        self.destroy()
