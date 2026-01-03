"""
UI Components - Επαναχρησιμοποιήσιμα components - Phase 2
"""

import customtkinter as ctk
from datetime import datetime
import database
import theme_config
from tkinter import messagebox
from tkcalendar import Calendar

class TaskCard(ctk.CTkFrame):
    """Καρτέλα εργασίας για προβολή"""
    
    def __init__(self, parent, task_data, on_click=None):
        self.theme = theme_config.get_current_theme()
        theme = theme_config.get_current_theme()
        super().__init__(
            parent, 
            corner_radius=10, 
            fg_color=theme["card_bg"],
            border_color=theme["card_border"],
            border_width=1
        )
        
        self.task = task_data
        self.on_click = on_click
        self.theme = theme
        self.create_card()
        
        # Clickable
        if on_click:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda e: on_click(task_data))
        
    def create_card(self):
        """Δημιουργία της καρτέλας"""
        
        # Status indicator
        status_color = "#2fa572" if self.task['status'] == 'completed' else "#ff9800"
        status_text = "✓ Ολοκληρωμένη" if self.task['status'] == 'completed' else "⏳ Εκκρεμής"
        
        # Priority indicator
        priority_colors = {"low": "#4CAF50", "medium": "#FF9800", "high": "#f44336"}
        priority_color = priority_colors.get(self.task. get('priority', 'medium'), "#FF9800")
        
        # Header with status and priority
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        status_label = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=theme_config.get_font("small", "bold"),
            text_color=status_color
        )
        status_label.pack(side="left")
        
        priority_label = ctk.CTkLabel(
            header_frame,
            text=f"  •  {self.task.get('priority', 'medium').upper()}",
            font=theme_config.get_font("tiny", "bold"),
            text_color=priority_color
        )
        priority_label.pack(side="left")
        
        # Task type and item - Phase 2.3
        type_text = f"🔧 {self.task['task_type_name']}"
        if self.task.get('task_item_name'):
            type_text += f" → {self.task['task_item_name']}"
        
        type_label = ctk.CTkLabel(
            self,
            text=f"🔧 {self.task['task_type_name']}",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"]
        )
        type_label.grid(row=1, column=0, sticky="w", padx=15, pady=2)
        
        # Description
        desc_text = self.task['description'][:80] + "..." if len(self.task['description']) > 80 else self.task['description']
        desc_label = ctk.CTkLabel(
            self,
            text=desc_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            wraplength=500,
            justify="left"
        )
        desc_label.grid(row=2, column=0, sticky="w", padx=15, pady=2)
        
        # Unit and date
        info_text = f"📍 {self.task['unit_name']} ({self.task['group_name']}) | 📅 {self.task['created_date']}"
        if self.task.get('technician_name'):
            info_text += f" | 👤 {self.task['technician_name']}"
        
        info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=theme_config.get_font("tiny"),
            text_color=self.theme["text_disabled"]
        )
        info_label.grid(row=3, column=0, sticky="w", padx=15, pady=(2, 10))
        
        # Bind click to all widgets
        if self.on_click:
            for widget in [self, header_frame, status_label, priority_label, type_label, desc_label, info_label]: 
                widget.bind("<Button-1>", lambda e: self.on_click(self.task))
                widget.configure(cursor="hand2")


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
                self.current_date = datetime.strptime(current_date, "%Y-%m-%d")
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
        self.selected_date = self.calendar.get_date()
        if self.callback:
            self.callback(self.selected_date)
        self.destroy()

class TaskForm(ctk.CTkFrame):
    """Φόρμα για προσθήκη/επεξεργασία εργασίας - Phase 2.3 Updated"""
    
    def __init__(self, parent, on_save_callback, task_data=None):
        super().__init__(parent, fg_color="transparent")
        
        self.on_save_callback = on_save_callback
        self.task_data = task_data
        self.is_edit_mode = task_data is not None
        
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_form()
        
        if self.is_edit_mode:
            self.populate_form()

    def create_form(self):
        """Δημιουργία της φόρμας - Phase 2. 3 - Compact 2-Column Layout"""

        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.pack(fill="both", expand=True)

        # Configure grid για 2 στήλες
        scrollable.grid_columnconfigure(0, weight=1)
        scrollable.grid_columnconfigure(1, weight=1)

        theme = theme_config.get_current_theme()

        # ===== ROW 0:  Ομάδα Μονάδων | Τύπος Εργασίας =====

        # LEFT:  Ομάδα Μονάδων
        ctk.CTkLabel(
            scrollable,
            text="Ομάδα Μονάδων:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        groups = database.get_all_groups()
        self.groups_dict = {g['name']: g['id'] for g in groups}

        self.group_combo = ctk.CTkComboBox(
            scrollable,
            values=list(self.groups_dict.keys()),
            width=300,
            state="readonly",
            command=self.on_group_change
        )
        self.group_combo.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=(0, 15))
        if self.groups_dict:
            self.group_combo.set(list(self.groups_dict.keys())[0])

        # RIGHT: Τύπος Εργασίας
        ctk.CTkLabel(
            scrollable,
            text="Τύπος Εργασίας:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=0, column=1, sticky="w", padx=(5, 10), pady=(10, 5))

        task_types = database.get_all_task_types()
        self.task_types_dict = {tt['name']: tt['id'] for tt in task_types}

        self.task_type_combo = ctk.CTkComboBox(
            scrollable,
            values=list(self.task_types_dict.keys()),
            width=300,
            state="readonly",
            command=self.on_task_type_change
        )
        self.task_type_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))
        if self.task_types_dict:
            self.task_type_combo.set(list(self.task_types_dict.keys())[0])

        # ===== ROW 2: Μονάδα | Είδος Εργασίας =====

        # LEFT: Μονάδα
        ctk.CTkLabel(
            scrollable,
            text="Μονάδα:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        self.units_dict = {}
        self.unit_combo = ctk.CTkComboBox(
            scrollable,
            values=[],
            width=300,
            state="readonly"
        )
        self.unit_combo.grid(row=3, column=0, sticky="ew", padx=(10, 5), pady=(0, 15))

        # RIGHT: Είδος Εργασίας
        ctk.CTkLabel(
            scrollable,
            text="Είδος Εργασίας:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=2, column=1, sticky="w", padx=(5, 10), pady=(10, 5))

        self.task_items_dict = {}
        self.task_item_combo = ctk.CTkComboBox(
            scrollable,
            values=[],
            width=300,
            state="readonly"
        )
        self.task_item_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))

        # ===== ROW 4: Κατάσταση | Προτεραιότητα =====

        # LEFT: Κατάσταση
        ctk.CTkLabel(
            scrollable,
            text="Κατάσταση:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=4, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        self.status_var = ctk.StringVar(value="pending")

        status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        status_frame.grid(row=5, column=0, sticky="w", padx=(10, 5), pady=(0, 15))

        ctk.CTkRadioButton(
            status_frame,
            text="Εκκρεμής",
            variable=self.status_var,
            value="pending"
        ).pack(side="left", padx=(0, 15))

        ctk.CTkRadioButton(
            status_frame,
            text="Ολοκληρωμένη",
            variable=self.status_var,
            value="completed"
        ).pack(side="left")

        # RIGHT:  Προτεραιότητα
        ctk.CTkLabel(
            scrollable,
            text="Προτεραιότητα:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=4, column=1, sticky="w", padx=(5, 10), pady=(10, 5))

        self.priority_combo = ctk.CTkComboBox(
            scrollable,
            values=["Χαμηλή (low)", "Μεσαία (medium)", "Υψηλή (high)"],
            width=300,
            state="readonly"
        )
        self.priority_combo.grid(row=5, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))
        self.priority_combo.set("Μεσαία (medium)")

        # ===== ROW 6: Ημερομηνία | Τεχνικός =====

        # LEFT:  Ημερομηνία με Calendar
        date_label_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        date_label_frame.grid(row=6, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        ctk.CTkLabel(
            date_label_frame,
            text="Ημερομηνία:",
            font=theme_config.get_font("body", "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            date_label_frame,
            text="(📅 για calendar)",
            font=theme_config.get_font("tiny"),
            text_color=theme["text_disabled"]
        ).pack(side="left", padx=5)

        date_entry_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        date_entry_frame.grid(row=7, column=0, sticky="w", padx=(10, 5), pady=(0, 15))

        self.created_date_entry = ctk.CTkEntry(date_entry_frame, width=220)
        self.created_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.created_date_entry.pack(side="left", padx=(0, 5))

        calendar_btn = ctk.CTkButton(
            date_entry_frame,
            text="📅",
            command=self.open_date_picker,
            width=60,
            height=32,
            **theme_config.get_button_style("primary")
        )
        calendar_btn.pack(side="left")

        # RIGHT:  Τεχνικός
        ctk.CTkLabel(
            scrollable,
            text="Όνομα Τεχνικού:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=6, column=1, sticky="w", padx=(5, 10), pady=(10, 5))

        self.technician_entry = ctk.CTkEntry(scrollable, width=300)
        self.technician_entry.grid(row=7, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))

        # ===== ROW 8: Περιγραφή (FULL WIDTH) =====

        ctk.CTkLabel(
            scrollable,
            text="Περιγραφή Εργασίας:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.description_text = ctk.CTkTextbox(scrollable, height=80)
        self.description_text.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))

        # ===== ROW 10: Σημειώσεις (FULL WIDTH) =====

        ctk.CTkLabel(
            scrollable,
            text="Σημειώσεις:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.notes_text = ctk.CTkTextbox(scrollable, height=60)
        self.notes_text.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 20))

        # ===== ROW 12: Κουμπιά (FULL WIDTH) =====

        buttons_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        buttons_frame.grid(row=12, column=0, columnspan=2, pady=(10, 20))

        save_text = "💾 Ενημέρωση" if self.is_edit_mode else "💾 Αποθήκευση"
        save_btn = ctk.CTkButton(
            buttons_frame,
            text=save_text,
            command=self.save_task,
            width=150,
            height=40,
            corner_radius=10,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("success")
        )
        save_btn.pack(side="left", padx=(0, 10))

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✖ Ακύρωση",
            command=self.on_save_callback,
            width=150,
            height=40,
            corner_radius=10,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("secondary")
        )
        cancel_btn.pack(side="left")

        # Κουμπί διαγραφής (μόνο σε edit mode)
        if self.is_edit_mode:
            delete_btn = ctk.CTkButton(
                buttons_frame,
                text="🗑️ Διαγραφή",
                command=self.delete_task,
                width=150,
                height=40,
                corner_radius=10,
                font=theme_config.get_font("body", "bold"),
                **theme_config.get_button_style("danger")
            )
            delete_btn.pack(side="left", padx=(10, 0))

        # Initialize cascade selects
        self.on_group_change(self.group_combo.get() if self.groups_dict else None)
        self.on_task_type_change(self.task_type_combo.get() if self.task_types_dict else None)

    def open_date_picker(self):
        """Άνοιγμα calendar picker"""
        current_date = self.created_date_entry.get()

        def on_date_selected(selected_date):
            self.created_date_entry.delete(0, "end")
            self.created_date_entry.insert(0, selected_date)

        DatePickerDialog(self, current_date, on_date_selected)
    def on_group_change(self, selected_group):
        """Callback όταν αλλάζει η ομάδα - φιλτράρει τις μονάδες - Phase 2.3"""
        if not selected_group:
            return
        
        group_id = self.groups_dict.get(selected_group)
        if not group_id:
            return
        
        # Παίρνουμε τις μονάδες της επιλεγμένης ομάδας
        units = database.get_units_by_group(group_id)
        self.units_dict = {u['name']: u['id'] for u in units}
        
        # Ενημέρωση dropdown
        if self.units_dict:
            unit_names = list(self.units_dict.keys())
            self.unit_combo.configure(values=unit_names)
            self.unit_combo.set(unit_names[0])
        else:
            self.unit_combo.configure(values=["Καμία μονάδα"])
            self.unit_combo.set("Καμία μονάδα")
    
    def on_task_type_change(self, selected_type):
        """Callback όταν αλλάζει ο τύπος - φιλτράρει τα είδη - Phase 2.3"""
        if not selected_type:
            return
        
        type_id = self.task_types_dict.get(selected_type)
        if not type_id:
            return
        
        # Παίρνουμε τα είδη του επιλεγμένου τύπου
        items = database.get_task_items_by_type(type_id)
        self.task_items_dict = {item['name']: item['id'] for item in items}
        
        # Ενημέρωση dropdown
        if self.task_items_dict:
            item_names = list(self.task_items_dict.keys())
            self.task_item_combo.configure(values=item_names)
            self.task_item_combo.set(item_names[0])
        else:
            self.task_item_combo.configure(values=["Κανένα είδος"])
            self.task_item_combo.set("Κανένα είδος")
    
    def populate_form(self):
        """Γέμισμα της φόρμας με υπάρχοντα δεδομένα - Updated Phase 2.3"""
        if not self.task_data:
            return
        
        # Βρίσκουμε και ορίζουμε την ομάδα (θα trigger-άρει το cascade)
        unit = database.get_unit_by_id(self.task_data['unit_id'])
        if unit:
            for group_name, group_id in self.groups_dict.items():
                if group_id == unit['group_id']:
                    self.group_combo.set(group_name)
                    self.on_group_change(group_name)
                    break
            
            # Βρίσκουμε και ορίζουμε τη μονάδα
            for unit_name, unit_id in self.units_dict.items():
                if unit_id == self.task_data['unit_id']:
                    self.unit_combo.set(unit_name)
                    break
        
        # Βρίσκουμε και ορίζουμε τον τύπο εργασίας (θα trigger-άρει το cascade)
        for type_name, type_id in self.task_types_dict.items():
            if type_id == self.task_data['task_type_id']:
                self.task_type_combo.set(type_name)
                self.on_task_type_change(type_name)
                break
        
        # Βρίσκουμε και ορίζουμε το είδος εργασίας
        if self.task_data.get('task_item_id'):
            for item_name, item_id in self.task_items_dict.items():
                if item_id == self.task_data['task_item_id']:
                    self.task_item_combo.set(item_name)
                    break
        
        # Περιγραφή
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", self.task_data['description'])
        
        # Κατάσταση
        self. status_var.set(self. task_data['status'])
        
        # Προτεραιότητα
        priority_map = {"low": "Χαμηλή (low)", "medium": "Μεσαία (medium)", "high": "Υψηλή (high)"}
        self.priority_combo.set(priority_map. get(self.task_data. get('priority', 'medium'), "Μεσαία (medium)"))
        
        # Ημερομηνία
        self.created_date_entry.delete(0, "end")
        self.created_date_entry.insert(0, self.task_data['created_date'])
        
        # Τεχνικός
        if self.task_data.get('technician_name'):
            self.technician_entry.delete(0, "end")
            self.technician_entry.insert(0, self.task_data['technician_name'])
        
        # Σημειώσεις
        if self.task_data.get('notes'):
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", self.task_data['notes'])
    
    def save_task(self):
        """Αποθήκευση της εργασίας - Updated Phase 2.3"""
        
        # Validation
        if not self.description_text.get("1.0", "end-1c").strip():
            messagebox.showerror("Σφάλμα", "Η περιγραφή είναι υποχρεωτική!")
            return
        
        # Validation: Είδος Εργασίας (REQUIRED)
        task_item_key = self.task_item_combo.get()
        if not task_item_key or task_item_key == "Κανένα είδος":
            messagebox.showerror("Σφάλμα", "Το Είδος Εργασίας είναι υποχρεωτικό!")
            return
        
        # Παίρνουμε τα δεδομένα
        unit_key = self.unit_combo.get()
        unit_id = self.units_dict.get(unit_key)
        
        if not unit_id or unit_key == "Καμία μονάδα":
            messagebox.showerror("Σφάλμα", "Η Μονάδα είναι υποχρεωτική!")
            return
        
        task_type_key = self.task_type_combo.get()
        task_type_id = self.task_types_dict.get(task_type_key)
        
        task_item_id = self.task_items_dict.get(task_item_key)
        
        description = self.description_text.get("1.0", "end-1c").strip()
        status = self.status_var.get()
        
        priority_map = {"Χαμηλή (low)": "low", "Μεσαία (medium)": "medium", "Υψηλή (high)": "high"}
        priority = priority_map.get(self.priority_combo.get(), "medium")
        
        technician = self.technician_entry.get().strip()
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        created_date = self.created_date_entry.get().strip()
        completed_date = created_date if status == "completed" else None
        
        # Αποθήκευση
        try:
            if self.is_edit_mode:
                # Update
                database.update_task(
                    self.task_data['id'],
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, technician if technician else None,
                    notes if notes else None, task_item_id
                )
                messagebox.showinfo("Επιτυχία", "Η εργασία ενημερώθηκε με επιτυχία!")
            else:
                # Insert
                database.add_task(
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, technician if technician else None,
                    notes if notes else None, task_item_id
                )
                messagebox.showinfo("Επιτυχία", "Η εργασία αποθηκεύτηκε με επιτυχία!")
            
            self.on_save_callback()
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αποθήκευσης: {str(e)}")
    
    def delete_task(self):
        """Διαγραφή εργασίας"""
        if not self.is_edit_mode:
            return
        
        result = messagebox.askyesno("Επιβεβαίωση", 
                                     "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτή την εργασία;\n\n"
                                     "Η εργασία θα μεταφερθεί στον Κάδο Ανακύκλωσης.")
        
        if result: 
            try:
                database.delete_task(self.task_data['id'])
                messagebox.showinfo("Επιτυχία", "Η εργασία διαγράφηκε!")
                self.on_save_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής: {str(e)}")


class UnitsManagement(ctk.CTkFrame):
    """Διαχείριση Μονάδων και Ομάδων - Phase 2.3 Updated"""
    
    def __init__(self, parent, refresh_callback):
        super().__init__(parent, fg_color="transparent")
        
        self.refresh_callback = refresh_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        
    def create_ui(self):
        """Δημιουργία UI - Phase 2.3: Only Units and Groups"""
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)
        
        self.tab1 = self.tabview.add("Μονάδες")
        self.tab2 = self.tabview.add("Ομάδες")
        
        # Tab Μονάδες
        self.create_units_tab(self.tab1)
        
        # Tab Ομάδες
        self.create_groups_tab(self.tab2)

    def create_units_tab(self, parent):
        """Tab για διαχείριση μονάδων - Grouped by Category"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        theme = theme_config.get_current_theme()

        # Header με κουμπί προσθήκης
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=15, padx=10)

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Προσθήκη Νέας Μονάδας",
            command=self.add_unit_dialog,
            height=40,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("success")
        )
        add_btn.pack(side="left")

        # Info label
        info_label = ctk.CTkLabel(
            header_frame,
            text="💡 Οι μονάδες είναι οργανωμένες ανά ομάδα.  Κλικ στο βέλος για άνοιγμα/κλείσιμο.",
            font=theme_config.get_font("small"),
            text_color=theme["text_secondary"]
        )
        info_label.pack(side="right", padx=20)

        # Scrollable frame για τις ομάδες
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Παίρνουμε όλες τις ομάδες
        groups = database.get_all_groups()

        if not groups:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν ομάδες.  Προσθέστε μία στην καρτέλα 'Ομάδες'.",
                font=theme_config.get_font("body"),
                text_color=theme["text_secondary"]
            ).pack(pady=50)
            return

        # Dictionary για να κρατάμε τα expanded states
        if not hasattr(self, 'expanded_groups'):
            self.expanded_groups = {group['id']: True for group in groups}  # Όλα expanded by default

        # Δημιουργία collapsible section για κάθε ομάδα
        for group in groups:
            self.create_group_section(scrollable, group, theme)

    def create_group_section(self, parent, group, theme):
        """Δημιουργία collapsible section για μία ομάδα"""

        # Container για την ομάδα
        group_container = ctk.CTkFrame(parent, fg_color="transparent")
        group_container.pack(fill="x", pady=5, padx=5)

        # Παίρνουμε τις μονάδες της ομάδας
        units = database.get_units_by_group(group['id'])
        units_count = len(units)

        # Header της ομάδας (clickable)
        header_frame = ctk.CTkFrame(
            group_container,
            corner_radius=10,
            fg_color=theme["card_bg"],
            border_color=theme["accent_blue"],
            border_width=2,
            cursor="hand2"
        )
        header_frame.pack(fill="x", pady=(0, 5))

        # Expand/Collapse state
        is_expanded = self.expanded_groups.get(group['id'], True)

        # Header label με arrow, όνομα ομάδας και count
        arrow_var = ctk.StringVar(value="▼" if is_expanded else "▶")

        header_label = ctk.CTkLabel(
            header_frame,
            textvariable=arrow_var,
            font=theme_config.get_font("body", "bold"),
            text_color=theme["accent_blue"],
            cursor="hand2"
        )
        header_label.pack(side="left", padx=(15, 5), pady=12)

        name_label = ctk.CTkLabel(
            header_frame,
            text=f"{group['name']} ({units_count} μονάδες)",
            font=theme_config.get_font("body", "bold"),
            text_color=theme["accent_blue"],
            cursor="hand2"
        )
        name_label.pack(side="left", padx=0, pady=12)

        # Description αν υπάρχει
        if group.get('description'):
            desc_label = ctk.CTkLabel(
                header_frame,
                text=f"• {group['description']}",
                font=theme_config.get_font("small"),
                text_color=theme["text_secondary"]
            )
            desc_label.pack(side="left", padx=10)

        # Units container (collapsible)
        units_container = ctk.CTkFrame(group_container, fg_color="transparent")

        # Δημιουργία του περιεχομένου των μονάδων
        if units:
            for unit in units:
                unit_frame = ctk.CTkFrame(
                    units_container,
                    corner_radius=8,
                    fg_color=theme["card_bg"],
                    border_color=theme["card_border"],
                    border_width=1
                )
                unit_frame.pack(fill="x", pady=3, padx=5)

                # Unit info
                info_parts = [
                    f"🔧 {unit['name']}",
                    f"📍 {unit['location']}",
                    f"🏷️ {unit['model']}"
                ]

                if unit.get('serial_number'):
                    info_parts.append(f"S/N: {unit['serial_number']}")

                info_text = " | ".join(info_parts)

                label = ctk.CTkLabel(
                    unit_frame,
                    text=info_text,
                    font=theme_config.get_font("small"),
                    text_color=theme["text_primary"],
                    anchor="w"
                )
                label.pack(side="left", padx=15, pady=10, fill="x", expand=True)

                # Edit button
                edit_btn = ctk.CTkButton(
                    unit_frame,
                    text="✏️",
                    command=lambda u=unit: self.edit_unit_dialog(u),
                    width=40,
                    height=30,
                    **theme_config.get_button_style("primary")
                )
                edit_btn.pack(side="right", padx=10, pady=10)
        else:
            # Άδεια ομάδα
            empty_label = ctk.CTkLabel(
                units_container,
                text="Δεν υπάρχουν μονάδες σε αυτή την ομάδα.",
                font=theme_config.get_font("small"),
                text_color=theme["text_disabled"]
            )
            empty_label.pack(pady=10, padx=20)

        # Αρχική κατάσταση (show/hide)
        if is_expanded:
            units_container.pack(fill="x", padx=20)

        # Toggle function - LOCAL UPDATE ΜΟΝΟ!
        def toggle_group(event=None):
            current_state = self.expanded_groups[group['id']]
            new_state = not current_state
            self.expanded_groups[group['id']] = new_state

            # Update arrow
            arrow_var.set("▼" if new_state else "▶")

            # Show/Hide container (NO FULL REFRESH!)
            if new_state:
                units_container.pack(fill="x", padx=20)
            else:
                units_container.pack_forget()

        # Bind click events
        header_frame.bind("<Button-1>", toggle_group)
        header_label.bind("<Button-1>", toggle_group)
        name_label.bind("<Button-1>", toggle_group)

    def create_groups_tab(self, parent):
        """Tab για διαχείριση ομάδων - Compact View"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        theme = theme_config.get_current_theme()

        # Header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=15, padx=10)

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Προσθήκη Νέας Ομάδας",
            command=self.add_group_dialog,
            height=40,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        add_btn.pack(side="left")

        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        groups = database.get_all_groups()

        if not groups:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν ομάδες.",
                font=theme_config.get_font("body"),
                text_color=theme["text_secondary"]
            ).pack(pady=50)
            return

        # Grid configuration για 2 στήλες
        scrollable.grid_columnconfigure(0, weight=1)
        scrollable.grid_columnconfigure(1, weight=1)

        for idx, group in enumerate(groups):
            row = idx // 2
            col = idx % 2

            # Group card
            group_frame = ctk.CTkFrame(
                scrollable,
                corner_radius=10,
                fg_color=theme["card_bg"],
                border_color=theme["accent_blue"],
                border_width=2
            )
            group_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)

            # Content frame
            content_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=12)

            # Group name
            name_label = ctk.CTkLabel(
                content_frame,
                text=f"📂 {group['name']}",
                font=theme_config.get_font("body", "bold"),
                text_color=theme["accent_blue"],
                anchor="w"
            )
            name_label.pack(anchor="w")

            # Description
            if group.get('description'):
                desc_label = ctk.CTkLabel(
                    content_frame,
                    text=group['description'],
                    font=theme_config.get_font("small"),
                    text_color=theme["text_secondary"],
                    anchor="w",
                    wraplength=250
                )
                desc_label.pack(anchor="w", pady=(5, 0))

            # Units count
            units = database.get_units_by_group(group['id'])
            count_label = ctk.CTkLabel(
                content_frame,
                text=f"🔧 {len(units)} μονάδες",
                font=theme_config.get_font("small"),
                text_color=theme["text_disabled"],
                anchor="w"
            )
            count_label.pack(anchor="w", pady=(5, 0))

            # Edit button
            edit_btn = ctk.CTkButton(
                group_frame,
                text="✏️ Επεξεργασία",
                command=lambda g=group: self.edit_group_dialog(g),
                width=120,
                height=30,
                **theme_config.get_button_style("primary")
            )
            edit_btn.pack(pady=(0, 10))

                    
    def add_unit_dialog(self, unit_data=None):
        """Dialog για προσθήκη/επεξεργασία μονάδας"""
        
        is_edit_mode = unit_data is not None
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Μονάδας" if is_edit_mode else "Προσθήκη Νέας Μονάδας")
        dialog.geometry("500x600")
        dialog.grab_set()
        
        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Μονάδας:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450)
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Ομάδα
        ctk.CTkLabel(dialog, text="Ομάδα:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        groups = database.get_all_groups()
        groups_dict = {g['name']: g['id'] for g in groups}
        group_combo = ctk.CTkComboBox(dialog, values=list(groups_dict.keys()), width=450, state="readonly")
        group_combo.pack(padx=20, pady=(0, 15))
        if groups_dict:
            group_combo.set(list(groups_dict.keys())[0])
        
        # Τοποθεσία
        ctk.CTkLabel(dialog, text="Τοποθεσία:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        location_entry = ctk.CTkEntry(dialog, width=450)
        location_entry.pack(padx=20, pady=(0, 15))
        
        # Μοντέλο
        ctk.CTkLabel(dialog, text="Μοντέλο:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        model_entry = ctk.CTkEntry(dialog, width=450)
        model_entry.pack(padx=20, pady=(0, 15))
        
        # Serial Number
        ctk.CTkLabel(dialog, text="Σειριακός Αριθμός:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        serial_entry = ctk.CTkEntry(dialog, width=450)
        serial_entry.pack(padx=20, pady=(0, 15))
        
        # Ημερομηνία εγκατάστασης
        ctk.CTkLabel(dialog, text="Ημερομηνία Εγκατάστασης (YYYY-MM-DD):", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        install_entry = ctk.CTkEntry(dialog, width=450)
        install_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        install_entry.pack(padx=20, pady=(0, 20))
        
        # Populate fields if editing
        if is_edit_mode:
            name_entry.insert(0, unit_data['name'])
            location_entry.insert(0, unit_data.get('location', ''))
            model_entry.insert(0, unit_data.get('model', ''))
            serial_entry.insert(0, unit_data.get('serial_number', ''))
            install_entry.delete(0, "end")
            install_entry.insert(0, unit_data.get('installation_date', ''))
            
            # Set group
            for group_name, group_id in groups_dict.items():
                if group_id == unit_data['group_id']:
                    group_combo.set(group_name)
                    break
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return
            
            group_id = groups_dict.get(group_combo.get())
            location = location_entry.get().strip()
            model = model_entry.get().strip()
            serial = serial_entry.get().strip()
            install_date = install_entry.get().strip()
            
            try:
                if is_edit_mode:
                    database.update_unit(unit_data['id'], name, group_id, location, model, serial, install_date)
                    messagebox.showinfo("Επιτυχία", "Η μονάδα ενημερώθηκε με επιτυχία!")
                else:
                    database.add_unit(name, group_id, location, model, serial, install_date)
                    messagebox.showinfo("Επιτυχία", "Η μονάδα προστέθηκε με επιτυχία!")
                dialog.destroy()
                self.refresh_callback()
                self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία: {str(e)}")
        
        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"), height=40).pack(pady=10)
    
    def edit_unit_dialog(self, unit):
        """Wrapper για επεξεργασία μονάδας"""
        self.add_unit_dialog(unit_data=unit)
        
    def add_group_dialog(self, group_data=None):
        """Dialog για προσθήκη/επεξεργασία ομάδας"""
        
        is_edit_mode = group_data is not None
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Ομάδας" if is_edit_mode else "Προσθήκη Νέας Ομάδας")
        dialog.geometry("500x350")
        dialog.grab_set()
        
        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Ομάδας:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450)
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100)
        desc_text.pack(padx=20, pady=(0, 20))
        
        # Populate fields if editing
        if is_edit_mode:
            name_entry.insert(0, group_data['name'])
            desc_text.insert("1.0", group_data.get('description', ''))
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return
            
            desc = desc_text.get("1.0", "end-1c").strip()
            
            try:
                if is_edit_mode:
                    result = database.update_group(group_data['id'], name, desc)
                    if result:
                        messagebox.showinfo("Επιτυχία", "Η ομάδα ενημερώθηκε με επιτυχία!")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    else:
                        messagebox.showerror("Σφάλμα", "Το όνομα υπάρχει ήδη!")
                else:
                    result = database.add_group(name, desc)
                    if result:
                        messagebox.showinfo("Επιτυχία", "Η ομάδα προστέθηκε με επιτυχία!")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    else:
                        messagebox.showerror("Σφάλμα", "Το όνομα υπάρχει ήδη!")
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία: {str(e)}")
        
        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"), height=40).pack(pady=10)
    
    def edit_group_dialog(self, group):
        """Wrapper για επεξεργασία ομάδας"""
        self.add_group_dialog(group_data=group)
    
    def refresh_ui(self):
        """Ανανέωση του UI - Phase 2.3"""
        # Clear and recreate tabs
        self.create_units_tab(self.tab1)
        self.create_groups_tab(self.tab2)


# ----- PHASE 2.3: NEW TASK MANAGEMENT COMPONENT -----

class TaskManagement(ctk.CTkFrame):
    """Διαχείριση Τύπων και Ειδών Εργασιών - Phase 2. 3"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.theme = theme_config.get_current_theme()
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_ui()

    def create_ui(self):
        """Δημιουργία UI"""

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tab1 = self.tabview.add("Τύποι Εργασιών")
        self.tab2 = self.tabview.add("Είδη Εργασιών")

        # Tab Τύποι Εργασιών
        self.create_task_types_tab(self.tab1)

        # Tab Είδη Εργασιών
        self.create_task_items_tab(self.tab2)

    def refresh_ui(self):
        """Ανανέωση του UI"""
        # Clear and recreate tabs
        self.create_task_types_tab(self.tab1)
        self.create_task_items_tab(self.tab2)

    def create_task_types_tab(self, parent):
        """Tab για διαχείριση τύπων εργασιών"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        # Info label
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_color=self.theme["accent_blue"],
            border_width=1
        )
        info_frame.pack(fill="x", pady=10, padx=10)

        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Οι προκαθορισμένοι τύποι (Service, Βλάβη, Επισκευή, Απλός Έλεγχος) προστατεύονται και δεν μπορούν να διαγραφούν.  Μπορείτε να προσθέσετε δικούς σας custom τύπους.",
            font=theme_config.get_font("small"),
            wraplength=800,
            text_color=self.theme["accent_blue"]
        )
        info_label.pack(padx=15, pady=10)

        # Κουμπί προσθήκης
        add_btn = ctk.CTkButton(
            parent,
            text="➕ Προσθήκη Custom Τύπου Εργασίας",
            command=self.add_task_type_dialog,
            height=40,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        add_btn.pack(pady=15)

        # Λίστα τύπων εργασιών
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        task_types = database.get_all_task_types()

        # Separate predefined and custom
        predefined_types = [tt for tt in task_types if tt['is_predefined']]
        custom_types = [tt for tt in task_types if not tt['is_predefined']]

        # Predefined types section
        if predefined_types:
            ctk.CTkLabel(
                scrollable,
                text="📌 Προκαθορισμένοι Τύποι",
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(anchor="w", padx=10, pady=(10, 5))

            for task_type in predefined_types:
                type_frame = ctk.CTkFrame(
                    scrollable,
                    corner_radius=10,
                    fg_color=self.theme["card_bg"],
                    border_color=self.theme["accent_blue"],
                    border_width=2
                )
                type_frame.pack(fill="x", pady=5, padx=10)

                info_text = f"🔧 {task_type['name']}"
                if task_type.get('description'):
                    info_text += f" - {task_type['description']}"

                label = ctk.CTkLabel(
                    type_frame,
                    text=info_text,
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_primary"]
                )
                label.pack(side="left", padx=15, pady=10)

        # Custom types section
        if custom_types:
            ctk.CTkLabel(
                scrollable,
                text="⚙️ Custom Τύποι",
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["accent_green"]
            ).pack(anchor="w", padx=10, pady=(20, 5))

            for task_type in custom_types:
                type_frame = ctk.CTkFrame(
                    scrollable,
                    corner_radius=10,
                    fg_color=self.theme["card_bg"],
                    border_color=self.theme["card_border"],
                    border_width=1
                )
                type_frame.pack(fill="x", pady=5, padx=10)

                info_text = f"🔧 {task_type['name']}"
                if task_type.get('description'):
                    info_text += f" - {task_type['description']}"

                label = ctk.CTkLabel(
                    type_frame,
                    text=info_text,
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_primary"]
                )
                label.pack(side="left", padx=15, pady=10, fill="x", expand=True)

                # Delete button
                delete_btn = ctk.CTkButton(
                    type_frame,
                    text="🗑️",
                    command=lambda tt=task_type: self.delete_task_type(tt),
                    width=40,
                    height=30,
                    **theme_config.get_button_style("danger")
                )
                delete_btn.pack(side="right", padx=10, pady=10)

        if not custom_types:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν custom τύποι.  Προσθέστε έναν! ",
                font=theme_config.get_font("small"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=20)

    def add_task_type_dialog(self):
        """Dialog για προσθήκη custom τύπου εργασίας"""

        dialog = ctk.CTkToplevel(self)
        dialog.title("Προσθήκη Custom Τύπου Εργασίας")
        dialog.geometry("500x350")
        dialog.grab_set()

        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Τύπου:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                   pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450)
        name_entry.pack(padx=20, pady=(0, 15))

        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                 pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100)
        desc_text.pack(padx=20, pady=(0, 20))

        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return

            desc = desc_text.get("1.0", "end-1c").strip()

            result = database.add_task_type(name, desc)
            if result:
                messagebox.showinfo("Επιτυχία", "Ο τύπος εργασίας προστέθηκε με επιτυχία!")
                dialog.destroy()
                self.refresh_ui()
            else:
                messagebox.showerror("Σφάλμα", "Το όνομα υπάρχει ήδη!")

        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                      height=40).pack(pady=10)

    def delete_task_type(self, task_type):
        """Διαγραφή custom τύπου εργασίας"""

        result = messagebox.askyesno(
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον τύπο '{task_type['name']}';"
        )

        if result:
            delete_result = database.delete_task_type(task_type['id'])

            if delete_result:
                messagebox.showinfo("Επιτυχία", "Ο τύπος εργασίας διαγράφηκε!")
                self.refresh_ui()
            else:
                messagebox.showerror("Σφάλμα",
                                     "Ο τύπος δεν μπορεί να διαγραφεί (είτε είναι προκαθορισμένος, είτε χρησιμοποιείται σε εργασίες).")

    def create_task_items_tab(self, parent):
        """Tab για διαχείριση ειδών εργασιών - Phase 2.3"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        # Info label
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_color=self.theme["accent_green"],
            border_width=1
        )
        info_frame.pack(fill="x", pady=10, padx=10)

        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Τα είδη εργασιών είναι υποκατηγορίες των τύπων. Επιλέξτε έναν τύπο για να δείτε τα είδη του.  Μπορείτε να προσθέσετε, επεξεργαστείτε ή αφαιρέσετε είδη.",
            font=theme_config.get_font("small"),
            wraplength=800,
            text_color=self.theme["accent_green"]
        )
        info_label.pack(padx=15, pady=10)

        # Επιλογή Τύπου Εργασίας
        selector_frame = ctk.CTkFrame(parent, fg_color="transparent")
        selector_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            selector_frame,
            text="Τύπος Εργασίας:",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=10)

        task_types = database.get_all_task_types()
        self.task_types_dict = {tt['name']: tt['id'] for tt in task_types}

        self.selected_type_var = ctk.StringVar()
        self.type_selector = ctk.CTkComboBox(
            selector_frame,
            values=list(self.task_types_dict.keys()),
            width=250,
            state="readonly",
            command=self.on_type_selected,
            variable=self.selected_type_var
        )
        self.type_selector.pack(side="left", padx=10)
        if self.task_types_dict:
            self.type_selector.set(list(self.task_types_dict.keys())[0])

        # Κουμπί προσθήκης
        self.add_item_btn = ctk.CTkButton(
            selector_frame,
            text="➕ Προσθήκη Είδους",
            command=self.add_task_item_dialog,
            height=35,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        self.add_item_btn.pack(side="right", padx=10)

        # Λίστα ειδών
        self.items_scrollable = ctk.CTkScrollableFrame(parent)
        self.items_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial load
        self.load_items_for_selected_type()

    def on_type_selected(self, selected_type):
        """Callback όταν επιλέγεται τύπος - Phase 2.3"""
        self.load_items_for_selected_type()

    def load_items_for_selected_type(self):
        """Φόρτωση ειδών για τον επιλεγμένο τύπο - Phase 2.3"""

        # Clear existing items
        for widget in self.items_scrollable.winfo_children():
            widget.destroy()

        selected_type = self.type_selector.get()
        type_id = self.task_types_dict.get(selected_type)

        if not type_id:
            return

        items = database.get_task_items_by_type(type_id)

        if not items:
            ctk.CTkLabel(
                self.items_scrollable,
                text="Δεν υπάρχουν είδη για αυτόν τον τύπο.  Προσθέστε ένα!",
                font=theme_config.get_font("small"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=30)
            return

        # Count label
        ctk.CTkLabel(
            self.items_scrollable,
            text=f"📊 {len(items)} είδη για τον τύπο '{selected_type}'",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Display items
        for item in items:
            item_frame = ctk.CTkFrame(
                self.items_scrollable,
                corner_radius=10,
                fg_color=self.theme["card_bg"],
                border_color=self.theme["card_border"],
                border_width=1
            )
            item_frame.pack(fill="x", pady=5, padx=10)

            info_text = f"📌 {item['name']}"
            if item.get('description'):
                info_text += f"\n   {item['description']}"

            label = ctk.CTkLabel(
                item_frame,
                text=info_text,
                font=theme_config.get_font("small"),
                text_color=self.theme["text_primary"],
                justify="left"
            )
            label.pack(side="left", padx=15, pady=10, fill="x", expand=True)

            # Action buttons
            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)

            # Edit button
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️",
                command=lambda i=item: self.edit_task_item_dialog(i),
                width=35,
                height=30,
                **theme_config.get_button_style("primary")
            )
            edit_btn.pack(side="left", padx=2)

            # Delete button
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️",
                command=lambda i=item: self.delete_task_item(i),
                width=35,
                height=30,
                **theme_config.get_button_style("danger")
            )
            delete_btn.pack(side="left", padx=2)

    def add_task_item_dialog(self, item_data=None):
        """Dialog για προσθήκη/επεξεργασία είδους - Phase 2.3"""

        is_edit_mode = item_data is not None

        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Είδους" if is_edit_mode else "Προσθήκη Νέου Είδους Εργασίας")
        dialog.geometry("500x400")
        dialog.grab_set()

        # Current type
        selected_type = self.type_selector.get()
        type_id = self.task_types_dict.get(selected_type)

        ctk.CTkLabel(
            dialog,
            text=f"Τύπος: {selected_type}",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(pady=(20, 10))

        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Είδους:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                    pady=(10, 5))
        name_entry = ctk.CTkEntry(dialog, width=450)
        name_entry.pack(padx=20, pady=(0, 15))

        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή (προαιρετική):", font=theme_config.get_font("body", "bold")).pack(
            anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100)
        desc_text.pack(padx=20, pady=(0, 20))

        # Populate if editing
        if is_edit_mode:
            name_entry.insert(0, item_data['name'])
            if item_data.get('description'):
                desc_text.insert("1.0", item_data['description'])

        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return

            desc = desc_text.get("1.0", "end-1c").strip()

            try:
                if is_edit_mode:
                    result = database.update_task_item(item_data['id'], name, desc)
                    if result:
                        messagebox.showinfo("Επιτυχία", "Το είδος ενημερώθηκε με επιτυχία!")
                        dialog.destroy()
                        self.load_items_for_selected_type()
                    else:
                        messagebox.showerror("Σφάλμα", "Το όνομα υπάρχει ήδη για αυτόν τον τύπο!")
                else:
                    result = database.add_task_item(name, type_id, desc)
                    if result:
                        messagebox.showinfo("Επιτυχία", "Το είδος προστέθηκε με επιτυχία!")
                        dialog.destroy()
                        self.load_items_for_selected_type()
                    else:
                        messagebox.showerror("Σφάλμα", "Το όνομα υπάρχει ήδη για αυτόν τον τύπο!")
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία: {str(e)}")

        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                      height=40).pack(pady=10)

    def edit_task_item_dialog(self, item):
        """Wrapper για επεξεργασία είδους - Phase 2.3"""
        self.add_task_item_dialog(item_data=item)

    def delete_task_item(self, item):
        """Διαγραφή είδους εργασίας - Phase 2.3"""

        result = messagebox.askyesno(
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε το είδος '{item['name']}'?\n\nΑυτή η ενέργεία θα είναι δυνατή μόνο αν δεν χρησιμοποιείται σε υπάρχουσες εργασίες."
        )

        if result:
            delete_result = database.delete_task_item(item['id'])

            if delete_result:
                messagebox.showinfo("Επιτυχία", "Το είδος διαγράφηκε!")
                self.load_items_for_selected_type()
            else:
                messagebox.showerror("Σφάλμα",
                                     "Το είδος δεν μπορεί να διαγραφεί γιατί χρησιμοποιείται σε υπάρχουσες εργασίες!")


# ----- PHASE 2: NEW COMPONENTS -----

class TaskHistoryView(ctk.CTkFrame):
    """Προβολή ιστορικού εργασιών με φίλτρα"""
    
    def __init__(self, parent, on_task_select=None):
        super().__init__(parent, fg_color="transparent")
        
        self.on_task_select = on_task_select
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        self.load_tasks()
        
    def create_ui(self):
        """Δημιουργία UI"""
        
        # Filters Frame
        filters_frame = ctk.CTkFrame(self, height=120)
        filters_frame.pack(fill="x", pady=(0, 10))
        filters_frame.pack_propagate(False)
        
        # Row 1: Search and Status
        row1 = ctk.CTkFrame(filters_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk. CTkLabel(row1, text="🔍 Αναζήτηση:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(0, 5))
        self.search_entry = ctk. CTkEntry(row1, width=200, placeholder_text="Περιγραφή, σημειώσεις, μονάδα...")
        self.search_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Κατάσταση:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(20, 5))
        self.status_combo = ctk.CTkComboBox(row1, values=["Όλες", "Εκκρεμείς", "Ολοκληρωμένες"], width=150, state="readonly")
        self.status_combo.set("Όλες")
        self.status_combo.pack(side="left", padx=5)
        
        # Row 2: Unit, Task Type, Dates
        row2 = ctk.CTkFrame(filters_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(row2, text="Μονάδα:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(0, 5))
        units = database.get_all_units()
        unit_names = ["Όλες"] + [f"{u['name']} - {u['group_name']}" for u in units]
        self.units_dict = {f"{u['name']} - {u['group_name']}": u['id'] for u in units}
        self.unit_combo = ctk.CTkComboBox(row2, values=unit_names, width=200, state="readonly")
        self.unit_combo.set("Όλες")
        self.unit_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Είδος:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(20, 5))
        task_types = database.get_all_task_types()
        type_names = ["Όλα"] + [tt['name'] for tt in task_types]
        self.types_dict = {tt['name']: tt['id'] for tt in task_types}
        self. type_combo = ctk.CTkComboBox(row2, values=type_names, width=150, state="readonly")
        self.type_combo.set("Όλα")
        self.type_combo.pack(side="left", padx=5)
        
        # Row 3: Buttons
        row3 = ctk.CTkFrame(filters_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk. CTkButton(row3, text="🔍 Αναζήτηση", command=self.apply_filters, width=120, **theme_config.get_button_style("primary")).pack(side="left", padx=5)
        ctk.CTkButton(row3, text="🔄 Καθαρισμός", command=self.clear_filters, width=120, **theme_config.get_button_style("secondary")).pack(side="left", padx=5)
        
        # Tasks List
        self.tasks_frame = ctk.CTkScrollableFrame(self)
        self.tasks_frame. pack(fill="both", expand=True)
        
    def load_tasks(self, tasks=None):
        """Φόρτωση εργασιών"""
        
        # Clear existing
        for widget in self.tasks_frame. winfo_children():
            widget.destroy()
        
        if tasks is None:
            tasks = database.get_all_tasks()
        
        if not tasks:
            no_tasks = ctk.CTkLabel(
                self.tasks_frame,
                text="Δεν βρέθηκαν εργασίες",
                font=theme_config.get_font("body")
            )
            no_tasks.pack(pady=50)
            return
        
        # Count label
        count_label = ctk.CTkLabel(
            self.tasks_frame,
            text=f"📊 Βρέθηκαν {len(tasks)} εργασίες",
            font=ctk. CTkFont(size=13, weight="bold")
        )
        count_label.pack(anchor="w", padx=10, pady=10)
        
        # Task cards
        for task in tasks: 
            card = TaskCard(self. tasks_frame, task, on_click=self.on_task_click if self.on_task_select else None)
            card.pack(fill="x", pady=5, padx=10)
    
    def on_task_click(self, task):
        """Callback όταν κάνεις κλικ σε εργασία"""
        if self.on_task_select:
            self.on_task_select(task)
    
    def apply_filters(self):
        """Εφαρμογή φίλτρων"""
        
        # Gather filter values
        search_text = self.search_entry.get().strip() or None
        
        status_map = {"Όλες": None, "Εκκρεμείς": "pending", "Ολοκληρωμένες": "completed"}
        status = status_map.get(self.status_combo.get())
        
        unit_key = self.unit_combo.get()
        unit_id = self.units_dict.get(unit_key) if unit_key != "Όλες" else None
        
        type_key = self.type_combo.get()
        task_type_id = self.types_dict.get(type_key) if type_key != "Όλα" else None
        
        # Apply filters
        filtered_tasks = database.filter_tasks(
            status=status,
            unit_id=unit_id,
            task_type_id=task_type_id,
            search_text=search_text
        )
        
        self.load_tasks(filtered_tasks)
    
    def clear_filters(self):
        """Καθαρισμός φίλτρων"""
        self.search_entry.delete(0, "end")
        self.status_combo.set("Όλες")
        self.unit_combo.set("Όλες")
        self.type_combo. set("Όλα")
        self.load_tasks()


class RecycleBinView(ctk.CTkFrame):
    """Κάδος Ανακύκλωσης"""
    
    def __init__(self, parent, refresh_callback):
        super().__init__(parent, fg_color="transparent")
        
        self. refresh_callback = refresh_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        self.load_deleted_tasks()
        
    def create_ui(self):
        """Δημιουργία UI"""
        
        # Header
        header_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🗑️ Διαγραμμένες Εργασίες",
            font=theme_config.get_font("title", "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Ανανέωση",
            command=self.load_deleted_tasks,
            width=120,
            **theme_config.get_button_style("primary")
        ).pack(side="right", padx=10)
        
        # Tasks List
        self.tasks_frame = ctk.CTkScrollableFrame(self)
        self.tasks_frame.pack(fill="both", expand=True)
        
    def load_deleted_tasks(self):
        """Φόρτωση διαγραμμένων εργασιών"""
        
        # Clear existing
        for widget in self.tasks_frame. winfo_children():
            widget.destroy()
        
        tasks = database.get_deleted_tasks()
        
        if not tasks:
            no_tasks = ctk.CTkLabel(
                self.tasks_frame,
                text="Ο Κάδος Ανακύκλωσης είναι άδειος",
                font=theme_config.get_font("body")
            )
            no_tasks.pack(pady=50)
            return
        
        # Task cards with action buttons
        for task in tasks: 
            container = ctk.CTkFrame(self.tasks_frame, fg_color="transparent")
            container. pack(fill="x", pady=5, padx=10)
            
            # Task info
            info_frame = ctk.CTkFrame(container, corner_radius=10, fg_color="#ffe0e0")
            info_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            # Title
            title_label = ctk.CTkLabel(
                info_frame,
                text=f"🔧 {task['task_type_name']}:  {task['description'][:50]}...",
                font=theme_config.get_font("small", "bold"),
                anchor="w"
            )
            title_label.pack(anchor="w", padx=15, pady=(10, 5))
            
            # Details
            details_label = ctk.CTkLabel(
                info_frame,
                text=f"📍 {task['unit_name']} | 📅 {task['created_date']}",
                font=theme_config.get_font("tiny"),
                text_color="gray",
                anchor="w"
            )
            details_label.pack(anchor="w", padx=15, pady=(0, 10))
            
            # Action buttons
            actions_frame = ctk.CTkFrame(container, fg_color="transparent")
            actions_frame. pack(side="right")
            
            restore_btn = ctk.CTkButton(
                actions_frame,
                text="↩️ Επαναφορά",
                command=lambda t=task: self.restore_task(t['id']),
                width=120,
                **theme_config.get_button_style("success")
            )
            restore_btn.pack(pady=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️ Διαγραφή",
                command=lambda t=task:  self.permanent_delete_task(t['id']),
                width=120,
                **theme_config.get_button_style("danger")
            )
            delete_btn.pack(pady=2)
    
    def restore_task(self, task_id):
        """Επαναφορά εργασίας"""
        result = messagebox.askyesno("Επιβεβαίωση", "Επαναφορά αυτής της εργασίας;")
        
        if result:
            try: 
                database.restore_task(task_id)
                messagebox.showinfo("Επιτυχία", "Η εργασία επαναφέρθηκε!")
                self.load_deleted_tasks()
                self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία επαναφοράς: {str(e)}")
    
    def permanent_delete_task(self, task_id):
        """Οριστική διαγραφή εργασίας"""
        result = messagebox.askyesno("ΠΡΟΣΟΧΗ!", 
                                     "Είστε ΣΙΓΟΥΡΟΙ ότι θέλετε να διαγράψετε ΟΡΙΣΤΙΚΑ αυτή την εργασία?\n\n"
                                     "Αυτή η ενέργεια ΔΕΝ μπορεί να αναιρεθεί!")
        
        if result: 
            try:
                database.permanent_delete_task(task_id)
                messagebox.showinfo("Επιτυχία", "Η εργασία διαγράφηκε οριστικά!")
                self.load_deleted_tasks()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής: {str(e)}")


class TaskRelationshipsView(ctk.CTkFrame):
    """Διαχείριση σχέσεων εργασιών"""
    
    def __init__(self, parent, task_data, refresh_callback):
        super().__init__(parent, fg_color="transparent")
        
        self.task_data = task_data
        self.refresh_callback = refresh_callback
        self. pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        self.load_relationships()
        
    def create_ui(self):
        """Δημιουργία UI"""
        
        # Header
        header_label = ctk.CTkLabel(
            self,
            text=f"🔗 Συνδεδεμένες Εργασίες για:  {self.task_data['description'][:50]}...",
            font=theme_config.get_font("heading", "bold"),
            wraplength=700
        )
        header_label. pack(pady=(0, 20))
        
        # Add relationship button
        add_btn = ctk.CTkButton(
            self,
            text="➕ Σύνδεση με άλλη εργασία",
            command=self.add_relationship_dialog,
            height=40,
            **theme_config.get_button_style("success")
        )
        add_btn.pack(pady=10)
        
        # Relationships frame
        self.relations_frame = ctk.CTkScrollableFrame(self, height=400)
        self.relations_frame.pack(fill="both", expand=True, pady=10)
        
    def load_relationships(self):
        """Φόρτωση συνδέσεων"""
        
        # Clear existing
        for widget in self.relations_frame.winfo_children():
            widget.destroy()
        
        relations = database.get_related_tasks(self.task_data['id'])
        
        # Parent tasks
        if relations['parents']:
            ctk.CTkLabel(
                self.relations_frame,
                text="⬆️ Γονικές Εργασίες (Αυτή η εργασία συνδέεται με: )",
                font=ctk. CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=10, pady=(10, 5))
            
            for parent in relations['parents']:
                self.create_relation_card(parent, "parent")
        
        # Child tasks
        if relations['children']: 
            ctk.CTkLabel(
                self.relations_frame,
                text="⬇️ Παιδικές Εργασίες (Συνδεδεμένες με αυτή την εργασία: )",
                font=ctk. CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=10, pady=(20, 5))
            
            for child in relations['children']: 
                self.create_relation_card(child, "child")
        
        if not relations['parents'] and not relations['children']:
            ctk.CTkLabel(
                self.relations_frame,
                text="Δεν υπάρχουν συνδεδεμένες εργασίες",
                font=ctk.CTkFont(size=13)
            ).pack(pady=50)
    
    def create_relation_card(self, task, relation_type):
        """Δημιουργία καρτέλας συνδεδεμένης εργασίας"""
        
        container = ctk.CTkFrame(self.relations_frame, fg_color="transparent")
        container.pack(fill="x", pady=5, padx=10)
        
        # Task card
        card_frame = ctk.CTkFrame(container, corner_radius=10, fg_color="#e8f4f8")
        card_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Info
        info_text = f"🔧 {task['task_type_name']}: {task['description'][:60]}.. .\n"
        info_text += f"📍 {task['unit_name']} | 📅 {task['created_date']}"
        
        info_label = ctk.CTkLabel(
            card_frame,
            text=info_text,
            font=theme_config.get_font("small"),
            justify="left"
        )
        info_label.pack(anchor="w", padx=15, pady=10)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            container,
            text="✖",
            command=lambda:  self.remove_relationship(task, relation_type),
            width=40,
            **theme_config.get_button_style("danger")
        )
        remove_btn.pack(side="right")
    
    def add_relationship_dialog(self):
        """Dialog για προσθήκη σύνδεσης"""
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Σύνδεση με άλλη εργασία")
        dialog.geometry("600x500")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Επιλέξτε εργασία για σύνδεση:",
            font=theme_config.get_font("body", "bold")
        ).pack(pady=20)
        
        # List of tasks
        tasks_frame = ctk.CTkScrollableFrame(dialog, height=350)
        tasks_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        all_tasks = database.get_all_tasks()
        # Exclude current task
        available_tasks = [t for t in all_tasks if t['id'] != self.task_data['id']]
        
        selected_task = {"task":  None}
        
        for task in available_tasks: 
            task_btn = ctk.CTkButton(
                tasks_frame,
                text=f"{task['task_type_name']}: {task['description'][:50]}...  | {task['unit_name']}",
                command=lambda t=task: self.select_task_for_relation(t, selected_task, dialog),
                anchor="w",
                **theme_config.get_button_style("primary")
            )
            task_btn.pack(fill="x", pady=3, padx=5)
    
    def select_task_for_relation(self, task, selected_container, dialog):
        """Επιλογή εργασίας για σύνδεση"""
        
        result = messagebox.askyesno("Επιβεβαίωση", 
                                     f"Σύνδεση με:\n\n{task['task_type_name']}: {task['description'][:80]}...")
        
        if result:
            try:
                # Add relationship (current task is parent, selected is child)
                database.add_task_relationship(self.task_data['id'], task['id'], "related")
                messagebox.showinfo("Επιτυχία", "Η σύνδεση δημιουργήθηκε!")
                dialog.destroy()
                self.load_relationships()
                self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία:  {str(e)}")
    
    def remove_relationship(self, task, relation_type):
        """Αφαίρεση σύνδεσης"""
        
        result = messagebox.askyesno("Επιβεβαίωση", "Αφαίρεση αυτής της σύνδεσης;")
        
        if result:
            try: 
                if relation_type == "parent": 
                    database.remove_task_relationship(task['id'], self.task_data['id'])
                else:
                    database.remove_task_relationship(self.task_data['id'], task['id'])
                
                messagebox.showinfo("Επιτυχία", "Η σύνδεση αφαιρέθηκε!")
                self.load_relationships()
                self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία: {str(e)}")
