"""
Task Form Component
===================
Φόρμα δημιουργίας/επεξεργασίας εργασιών με chain management

Extracted από ui_components.py για καλύτερη οργάνωση.
Αυτό είναι το μεγαλύτερο component (909 lines).
"""

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import theme_config
import custom_dialogs
import utils_refactored
from components.date_picker import DatePickerDialog

class TaskForm(ctk.CTkFrame):
    """Φόρμα για προσθήκη/επεξεργασία εργασίας - Phase 2.3 Updated"""

    def __init__(self, parent, on_save_callback, task_data=None):
        super().__init__(parent, fg_color="transparent")

        self.on_save_callback = on_save_callback
        self.task_data = task_data
        self.is_edit_mode = task_data is not None

        # ═══ CHAIN STATUS LOGIC ═══
        self.is_last_in_chain = True  # Default: allow editing
        self.chain_info = None

        if self.is_edit_mode and task_data:
            # Get chain info
            full_chain = utils_refactored.get_full_task_chain(task_data['id'])
            if len(full_chain) > 1:
                # We're in a chain
                self.chain_info = {
                    'position': next((i for i, t in enumerate(full_chain, 1) if t['id'] == task_data['id']), 1),
                    'length': len(full_chain),
                    'is_last': full_chain[-1]['id'] == task_data['id']
                }
                self.is_last_in_chain = self.chain_info['is_last']

        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_form()

        if self.is_edit_mode:
            self.populate_form()

    def create_form(self):
        """Δημιουργία της φόρμας - Phase 2. 3 - Compact 2-Column Layout"""

        # ═══ CHAIN WARNING BANNER ═══
        if self.chain_info and not self.is_last_in_chain:
            theme = theme_config.get_current_theme()

            # Show warning at top
            warning_frame = ctk.CTkFrame(
                self,
                fg_color=theme["accent_orange"],
                corner_radius=8
            )
            warning_frame.pack(fill="x", pady=(0, 15))

            warning_text = (
                f"🔗 Αυτή είναι η εργασία {self.chain_info['position']}/{self.chain_info['length']} στην αλυσίδα.\n"
                f"🔒 Μόνο ο τελευταίος κρίκος (#{self.chain_info['length']}) μπορεί να αλλάξει την κατάσταση.\n"
                f"✅ Η κατάσταση συγχρονίζεται αυτόματα σε όλη την αλυσίδα."
            )

            ctk.CTkLabel(
                warning_frame,
                text=warning_text,
                font=theme_config.get_font("body", "bold"),
                text_color="white",
                justify="left"
            ).pack(padx=15, pady=10)

        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.pack(fill="both", expand=True)

        # Configure grid για 2 στήλες
        scrollable.grid_columnconfigure(0, weight=1)
        scrollable.grid_columnconfigure(1, weight=1)

        theme = theme_config.get_current_theme()

        # ===== ROW 0:  Ομάδα Μονάδων | Τύπος Εργασίας =====


        ctk.CTkLabel(
            scrollable,
            text="Τοποθεσία:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        # Get locations from database
        try:
            locations = database.get_all_locations()
            location_names = [loc['name'] for loc in locations]
            if not location_names:
                location_names = ["Δεν υπάρχουν τοποθεσίες"]
        except:
            location_names = ["Σφάλμα φόρτωσης"]

        self.location_combo = ctk.CTkComboBox(
            scrollable,
            values=location_names,
            width=300,
            state="readonly",
            font=theme_config.get_font("input")
        )
        self.location_combo.grid(row=1, column=0, sticky="ew", padx=(10, 10), pady=(0, 15))

        if location_names and location_names[0] not in ["Δεν υπάρχουν τοποθεσίες", "Σφάλμα φόρτωσης"]:
            self.location_combo.set(location_names[0])

                # ===== ROW 2:  Ομάδα Μονάδων | Τύπος Εργασίας =====




        # LEFT:  Ομάδα Μονάδων
        ctk.CTkLabel(
            scrollable,
            text="Ομάδα Μονάδων:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        groups = database.get_all_groups()
        self.groups_dict = {g['name']: g['id'] for g in groups}

        self.group_combo = ctk.CTkComboBox(
            scrollable,
            values=list(self.groups_dict.keys()),
            width=300,
            state="readonly",
            command=self.on_group_change,
            font=theme_config.get_font("input")
        )
        self.group_combo.grid(row=3, column=0, sticky="ew", padx=(10, 5), pady=(0, 15))
        
        # Set default group
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
            command=self.on_task_type_change,
            font=theme_config.get_font("input")
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
        ).grid(row=4, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        self.units_dict = {}
        self.unit_combo = ctk.CTkComboBox(
            scrollable,
            values=[],
            width=300,
            state="readonly",
            font=theme_config.get_font("input")
        )
        self.unit_combo.grid(row=5, column=0, sticky="ew", padx=(10, 5), pady=(0, 15))

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
            state="readonly",
            font=theme_config.get_font("input")
        )
        self.task_item_combo.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))

        # ===== ROW 4: Κατάσταση | Προτεραιότητα =====

        # LEFT: Κατάσταση
        ctk.CTkLabel(
            scrollable,
            text="Κατάσταση:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=6, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        self.status_var = ctk.StringVar(value="pending")

        status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        status_frame.grid(row=7, column=0, sticky="w", padx=(10, 5), pady=(0, 15))

        # ΣΗΜΑΝΤΙΚΟ: Αποθηκεύουμε σε μεταβλητές!
        self.status_pending_radio = ctk.CTkRadioButton(
            status_frame,
            text="⏳ Εκκρεμής",
            variable=self.status_var,
            value="pending",
            font=theme_config.get_font("body")
        )
        self.status_pending_radio.pack(side="left", padx=(0, 20))

        self.status_completed_radio = ctk.CTkRadioButton(
            status_frame,
            text="✅ Ολοκληρωμένη",
            variable=self.status_var,
            value="completed",
            font=theme_config.get_font("body")
        )
        self.status_completed_radio.pack(side="left")

        # ═══ CHAIN LOCK LOGIC ═══
        # ΤΩΡΑ που τα δημιουργήσαμε, μπορούμε να τα disable!
        if not self.is_last_in_chain:
            theme = theme_config.get_current_theme()

            self.status_pending_radio.configure(state="disabled")
            self.status_completed_radio.configure(state="disabled")

            # Add warning label
            warning_label = ctk.CTkLabel(
                status_frame,
                text="🔒",
                font=theme_config.get_font("small"),
                text_color=theme["accent_orange"]
            )
            warning_label.pack(side="left", padx=(20, 0))

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
            state="readonly",
            font=theme_config.get_font("input")
        )
        self.priority_combo.grid(row=5, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))
        self.priority_combo.set("Μεσαία (medium)")

        # ===== ROW 6: Ημερομηνία

        # RIGHT:  Ημερομηνία με Calendar
        date_label_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        date_label_frame.grid(row=6, column=1, sticky="w", padx=(10, 5), pady=(10, 5))

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
        date_entry_frame.grid(row=7, column=1, sticky="w", padx=(10, 5), pady=(0, 15))

        self.created_date_entry = ctk.CTkEntry(
            date_entry_frame,
            width=220,
            font=theme_config.get_font("input"),
            state="readonly"
        )
        # Set initial (unlock → set → lock)
        self.created_date_entry.configure(state="normal")
        self.created_date_entry.insert(0, utils_refactored.get_today_display())
        self.created_date_entry.configure(state="readonly")

        self.created_date_entry.insert(0, utils_refactored.get_today_display())
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

        # RIGHT:  Ημερομηνία Ολοκλήρωσης
        date_completed_label_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        date_completed_label_frame.grid(row=6, column=1, sticky="e", padx=(5, 10), pady=(10, 5))
        
        ctk.CTkLabel(
            date_completed_label_frame,
            text="Ολοκλήρωσης:",
            font=theme_config.get_font("body", "bold")
        ).pack(side="left")
        
        ctk.CTkLabel(
            date_completed_label_frame,
            text="(📅 για calendar)",
            font=theme_config.get_font("tiny"),
            text_color=theme["text_disabled"]
        ).pack(side="left", padx=5)
        
        date_completed_entry_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        date_completed_entry_frame.grid(row=7, column=1, sticky="e", padx=(5, 10), pady=(0, 15))
        
        self.completed_date_entry = ctk.CTkEntry(
            date_completed_entry_frame,
            width=220,
            font=theme_config.get_font("input"),
            state="readonly",
            placeholder_text="Προαιρετικό"
        )
        self.completed_date_entry.pack(side="left", padx=(0, 5))
        
        completed_calendar_btn = ctk.CTkButton(
            date_completed_entry_frame,
            text="📅",
            command=self.open_completed_date_picker,
            width=60,
            height=32,
            **theme_config.get_button_style("primary")
        )
        completed_calendar_btn.pack(side="left")
        


        # ===== ROW 8: Περιγραφή (FULL WIDTH) =====

        ctk.CTkLabel(
            scrollable,
            text="Περιγραφή Εργασίας:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.description_text = ctk.CTkTextbox(
            scrollable,
            height=80,
            font=theme_config.get_font("input")
        )
        self.description_text.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))

        # ===== ROW 10: Σημειώσεις (FULL WIDTH) =====

        ctk.CTkLabel(
            scrollable,
            text="Σημειώσεις:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=12, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.notes_text = ctk.CTkTextbox(
            scrollable,
            height=60,
            font=theme_config.get_font("input")
        )
        self.notes_text.grid(row=13, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 20))

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
                font=theme_config.get_font("body", "bold"),
                **theme_config.get_button_style("danger")
            )
            delete_btn.pack(side="left", padx=(10, 0))

        # Initialize cascade selects (ΜΟΝΟ ΜΙΑ ΦΟΡΑ!)
        self.on_group_change(self.group_combo.get() if self.groups_dict else None)
        self.on_task_type_change(self.task_type_combo.get() if self.task_types_dict else None)


        # COMPACT CHAIN PREVIEW (μόνο σε edit mode) - ΣΤΟ ΤΕΛΟΣ!

        if self.is_edit_mode:
            self.add_compact_chain_preview(scrollable)

    def open_date_picker(self):
        """Άνοιγμα calendar picker"""
        current_date = self.created_date_entry.get()

        def on_date_selected(selected_date):
            # Unlock field temporarily
            self.created_date_entry.configure(state="normal")

            # Update value
            self.created_date_entry.delete(0, "end")
            self.created_date_entry.insert(0, selected_date)

            # Lock again
            self.created_date_entry.configure(state="readonly")

        # ← ΕΔΩ! Έξω από το callback!
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
    
    
    def open_completed_date_picker(self):
        """Open calendar for completed date"""
        from datetime import datetime
        from tkcalendar import Calendar
        
        theme = theme_config.get_current_theme()
        
        cal_window = ctk.CTkToplevel(self)
        cal_window.title("Επιλογή Ημερομηνίας Ολοκλήρωσης")
        cal_window.geometry("400x450")
        cal_window.resizable(False, False)
        cal_window.grab_set()
        
        # Center
        cal_window.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 400) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 450) // 3
        cal_window.geometry(f"+{x}+{y}")
        
        # Calendar
        current_date = self.completed_date_entry.get().strip()
        if current_date:
            try:
                db_date = utils_refactored.format_date_for_db(current_date)
                date_obj = datetime.strptime(db_date, "%Y-%m-%d")
                year, month, day = date_obj.year, date_obj.month, date_obj.day
            except:
                year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        else:
            year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        
        cal = Calendar(
            cal_window,
            selectmode='day',
            year=year,
            month=month,
            day=day,
            date_pattern='yyyy-mm-dd'
        )
        cal.pack(padx=20, pady=20, expand=True, fill="both")

        def select_date():
            calendar_date = cal.get_date()
            date_obj = datetime.strptime(calendar_date, '%Y-%m-%d')
            display_date = date_obj.strftime('%d/%m/%y')
            self.completed_date_entry.delete(0, 'end')
            self.completed_date_entry.insert(0, display_date)
            cal_window.destroy()
        
        ctk.CTkButton(
            cal_window,
            text="Επιλογή",
            command=select_date,
            **theme_config.get_button_style("success"),
            height=40
        ).pack(pady=(0, 20), padx=20, fill="x")

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
            # Set location if exists
            if self.task_data.get('location'):
                try:
                    self.location_combo.set(self.task_data['location'])
                except:
                    pass
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

        # Ημερομηνία - Convert from DB format to display format
        self.created_date_entry.delete(0, "end")
        display_date = utils_refactored.format_date_for_display(self.task_data['created_date'])
        self.created_date_entry.insert(0, display_date)
        

        
        # Σημειώσεις
        if self.task_data.get('notes'):
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", self.task_data['notes'])
    
    def save_task(self):
        """Αποθήκευση της εργασίας - Updated Phase 2.3"""
        
        # Validation
        if not self.description_text.get("1.0", "end-1c").strip():
            custom_dialogs.show_error("Σφάλμα", "Η περιγραφή είναι υποχρεωτική!")
            return
        
        # Validation: Είδος Εργασίας (REQUIRED)
        task_item_key = self.task_item_combo.get()
        if not task_item_key or task_item_key == "Κανένα είδος":
            custom_dialogs.show_error("Σφάλμα", "Το Είδος Εργασίας είναι υποχρεωτικό!")
            return
        
        # Παίρνουμε τα δεδομένα
        unit_key = self.unit_combo.get()
        unit_id = self.units_dict.get(unit_key)
        
        if not unit_id or unit_key == "Καμία μονάδα":
            custom_dialogs.show_error("Σφάλμα", "Η Μονάδα είναι υποχρεωτική!")
            return
        
        task_type_key = self.task_type_combo.get()
        task_type_id = self.task_types_dict.get(task_type_key)
        location = self.location_combo.get()
        task_item_id = self.task_items_dict.get(task_item_key)
        
        description = self.description_text.get("1.0", "end-1c").strip()
        status = self.status_var.get()
        
        priority_map = {"Χαμηλή (low)": "low", "Μεσαία (medium)": "medium", "Υψηλή (high)": "high"}
        priority = priority_map.get(self.priority_combo.get(), "medium")
        

        notes = self.notes_text.get("1.0", "end-1c").strip()

        # Convert date from display format (DD/MM/YY) to DB format (YYYY-MM-DD)
        created_date_display = self.created_date_entry.get().strip()
        created_date = utils_refactored.format_date_for_db(created_date_display)

        # Validation
        if not created_date:
            custom_dialogs.show_error("Σφάλμα", "Μη έγκυρη ημερομηνία! Χρησιμοποιήστε DD/MM/YY")
            return

        completed_date = created_date if status == "completed" else None
        
        # Αποθήκευση
        try:
            if self.is_edit_mode:
                # Update existing task
                database.update_task(
                    self.task_data['id'],
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, None,
                    notes if notes else None, task_item_id, location
                )
                
                # ═══ CHAIN SYNC ═══
                # If we're in a chain AND we're the last task, sync ALL
                if self.chain_info and self.is_last_in_chain:
                    try:
                        full_chain = utils_refactored.get_full_task_chain(self.task_data['id'])
                        
                        # Update ALL other tasks in chain to same status
                        conn = database.get_connection()
                        cursor = conn.cursor()
                        
                        for task in full_chain:
                            if task['id'] != self.task_data['id']:  # Skip current
                                cursor.execute(
                                    "UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?",
                                    (status, completed_date, task['id'])
                                )
                        
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Chain sync warning: {e}")
                
                custom_dialogs.show_success("Επιτυχία", "Η εργασία ενημερώθηκε με επιτυχία!")
            else:
                # Insert new task
                database.add_task(
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, None,
                    notes if notes else None, task_item_id, location
                )
                custom_dialogs.show_success("Επιτυχία", "Η εργασία αποθηκεύτηκε με επιτυχία!")
            
            self.on_save_callback()

        except Exception as e:
            import logger_config
            logger = logger_config.get_logger(__name__)
            logger.error(f"Failed to save task: {e}", exc_info=True)
            custom_dialogs.show_error("Σφάλμα", f"Αποτυχία αποθήκευσης: {str(e)}")


    def delete_task(self):
        """Διαγραφή εργασίας"""
        if not self.is_edit_mode:
            return

        result = custom_dialogs.ask_yes_no("Επιβεβαίωση",
                                     "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτή την εργασία?\n\n"
                                     "Η εργασία θα μεταφερθεί στον Κάδο Ανακύκλωσης.")

        if result:
            try:
                database.delete_task(self.task_data['id'])
                custom_dialogs.show_success("Επιτυχία", "Η εργασία διαγράφηκε!")
                self.on_save_callback()
            except Exception as e:
                import logger_config
                logger = logger_config.get_logger(__name__)
                logger.error(f"Failed to save task: {e}", exc_info=True)
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία αποθήκευσης: {str(e)}")

    def add_compact_chain_preview(self, parent):
        """Προσθήκη compact chain preview κάτω από τα buttons - Edit mode only"""

        theme = theme_config.get_current_theme()

        # Get full chain
        full_chain = utils_refactored.get_full_task_chain(self.task_data['id'])

        if len(full_chain) <= 1:
            return  # Δεν υπάρχει αλυσίδα, skip

        # Find current position
        current_position = next((i for i, t in enumerate(full_chain, 1) if t['id'] == self.task_data['id']), 1)
        total_in_chain = len(full_chain)



        # ═══════════════════════════════════════════════
        # SEPARATOR (ROW 20 - μακριά από τα buttons)
        # ═══════════════════════════════════════════════
        separator = ctk.CTkFrame(parent, height=2, fg_color=theme["card_border"])
        separator.grid(row=20, column=0, columnspan=2, sticky="ew", padx=10, pady=(30, 20))

        # ═══════════════════════════════════════════════
        # HEADER (ROW 21)
        # ═══════════════════════════════════════════════
        chain_header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        chain_header_frame.grid(row=21, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        # Left:  Title
        title_label = ctk.CTkLabel(
            chain_header_frame,
            text="🔗 Αλυσίδα Εργασιών",
            font=theme_config.get_font("heading", "bold"),
            text_color=theme["accent_blue"]
        )
        title_label.pack(side="left")

        # Right:  Info
        info_label = ctk.CTkLabel(
            chain_header_frame,
            text=f"📊 {total_in_chain} εργασίες  •  Θέση {current_position}/{total_in_chain}",
            font=theme_config.get_font("small", "bold"),
            text_color=theme["text_secondary"]
        )
        info_label.pack(side="right")

        # ═══════════════════════════════════════════════
        # COMPACT TIMELINE CONTAINER (ROW 22)
        # ═══════════════════════════════════════════════

        # Scrollable container για το timeline (για να χωράει)
        timeline_container = ctk.CTkScrollableFrame(
            parent,
            height=300,  # Fixed height
            fg_color=theme["card_bg"],
            corner_radius=10,
            border_color=theme["card_border"],
            border_width=1
        )
        timeline_container.grid(row=22, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 20))

        # Display tasks (μέσα στο scrollable timeline)
        for idx, chain_task in enumerate(full_chain, 1):
            is_current = (chain_task['id'] == self.task_data['id'])

            # Task row container
            task_container = ctk.CTkFrame(
                timeline_container,
                fg_color=theme["bg_secondary"] if is_current else "transparent",
                corner_radius=6
            )
            task_container.pack(fill="x", padx=8, pady=2)

            # Content frame
            content_frame = ctk.CTkFrame(task_container, fg_color="transparent")
            content_frame.pack(fill="x", padx=8, pady=6)

            # Left:   Position + Icon
            left_section = ctk.CTkFrame(content_frame, fg_color="transparent")
            left_section.pack(side="left")

            # Position badge
            pos_color = theme["accent_orange"] if is_current else theme["text_disabled"]
            ctk.CTkLabel(
                left_section,
                text=f"[{idx}]",
                font=theme_config.get_font("small", "bold"),
                text_color=pos_color,
                width=35
            ).pack(side="left")

            # Icon
            if idx < current_position:
                icon_text = "🔵"
            elif is_current:
                icon_text = "🟡"
            else:
                icon_text = "🟢"

            ctk.CTkLabel(
                left_section,
                text=icon_text,
                font=theme_config.get_font("body")
            ).pack(side="left", padx=3)

            # Middle:   Task info
            info_section = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_section.pack(side="left", fill="x", expand=True, padx=8)

            # Build info text
            task_info = f"📅 {utils_refactored.format_date_for_display(chain_task['created_date'])}  •  {chain_task['task_type_name']}"
            if chain_task.get('task_item_name'):
                task_info += f" → {chain_task['task_item_name']}"

            # Short description
            if chain_task.get('description'):
                desc = chain_task['description'][:35] + "..." if len(chain_task['description']) > 35 else chain_task[
                    'description']
                task_info += f"  •  {desc}"

            text_color = theme["text_primary"] if is_current else theme["text_secondary"]
            font_style = "bold" if is_current else "normal"

            ctk.CTkLabel(
                info_section,
                text=task_info,
                font=theme_config.get_font("small", font_style),
                text_color=text_color,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            # Right:  Current indicator
            if is_current:
                ctk.CTkLabel(
                    content_frame,
                    text="◄ ΤΡΕΧΟΥΣΑ",
                    font=theme_config.get_font("tiny", "bold"),
                    text_color=theme["accent_orange"],
                    width=90
                ).pack(side="right", padx=5)

            # Arrow (except last)
            if idx < total_in_chain:
                arrow_label = ctk.CTkLabel(
                    timeline_container,
                    text="        ↓",
                    font=theme_config.get_font("small"),
                    text_color=theme["text_disabled"]
                )
                arrow_label.pack(anchor="w", padx=20, pady=0)

    def _get_full_chain_simple(self, task_id):
        """Helper για να πάρει ολόκληρη την αλυσίδα (simplified για TaskForm)"""
        chain = []
        visited_parents = set()
        visited_children = set()

        # Get all tasks
        all_tasks = database.get_all_tasks()
        task_dict = {t['id']: t for t in all_tasks}

        def get_parents(tid):
            if tid in visited_parents:
                return
            visited_parents.add(tid)
            rels = database.get_related_tasks(tid)
            for parent in rels['parents']:
                parent_id = parent['id']
                if parent_id not in [c['id'] for c in chain]:
                    chain.insert(0, parent)
                    get_parents(parent_id)

        def get_children(tid):
            if tid in visited_children:
                return
            visited_children.add(tid)
            rels = database.get_related_tasks(tid)
            for child in rels['children']:
                child_id = child['id']
                if child_id not in [c['id'] for c in chain]:
                    chain.append(child)
                    get_children(child_id)

        # Build chain
        get_parents(task_id)

        # Add current task
        if task_id in task_dict:
            chain.append(task_dict[task_id])

        get_children(task_id)

        return chain






