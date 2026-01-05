"""
UI Components - Επαναχρησιμοποιήσιμα components - Phase 2
"""

import customtkinter as ctk
from datetime import datetime
import database
import theme_config
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta

class TaskCard(ctk.CTkFrame):
    """Καρτέλα εργασίας για προβολή - Compact Design με Link Indicators"""

    def __init__(self, parent, task_data, on_click=None, show_relations=True):
        theme = theme_config.get_current_theme()
        super().__init__(
            parent,
            corner_radius=8,
            fg_color=theme["card_bg"],
            border_color=theme["card_border"],
            border_width=1,
            height=65
        )

        self.task = task_data
        self.on_click = on_click
        self.theme = theme
        self.show_relations = show_relations

        self.pack_propagate(False)

        self.create_card()

        # Clickable
        if on_click:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda e: on_click(task_data))

    def _get_full_chain_simple(self, task_id):
        """Lightweight chain calculation για το badge"""
        chain = []
        visited_parents = set()
        visited_children = set()

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

        # Build full chain
        get_parents(task_id)
        chain.append(self.task)  # Current task
        get_children(task_id)

        return chain

    def create_card(self):
        """Δημιουργία της καρτέλας - Compact Layout"""

        # Status & Priority colors
        status_color = self.theme["accent_green"] if self.task['status'] == 'completed' else self.theme["accent_orange"]
        status_icon = "✓" if self.task['status'] == 'completed' else "⏳"
        status_text = "Ολοκληρωμένη" if self.task['status'] == 'completed' else "Εκκρεμής"

        priority_colors = {
            "low": self.theme["accent_green"],
            "medium": self.theme["accent_orange"],
            "high": self.theme["accent_red"]
        }
        priority_color = priority_colors.get(self.task.get('priority', 'medium'), self.theme["accent_orange"])
        priority_icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        priority_icon = priority_icons.get(self.task.get('priority', 'medium'), "🟡")

        # ===== ROW 1: Header Line =====
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(8, 4))

        # LEFT SECTION: Task Type → Task Item → Unit
        left_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_section.pack(side="left", fill="x", expand=True)

        # Task Type → Task Item → Unit
        type_text = f"🔧 {self.task['task_type_name']}"
        if self.task.get('task_item_name'):
            type_text += f" → {self.task['task_item_name']}"
        type_text += f" → 📍 {self.task['unit_name']}"

        type_label = ctk.CTkLabel(
            left_section,
            text=type_text,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        type_label.pack(side="left")

        # RIGHT SECTION:  Priority + Status (pack από δεξιά)

        # Priority (pack first = farthest right)
        priority_label = ctk.CTkLabel(
            header_frame,
            text=f"{priority_icon} {self.task.get('priority', 'medium').upper()}",
            font=theme_config.get_font("small", "bold"),
            text_color=priority_color
        )
        priority_label.pack(side="right", padx=(10, 0))

        # Status (pack second = left of priority)
        status_label = ctk.CTkLabel(
            header_frame,
            text=f"{status_icon} {status_text}",
            font=theme_config.get_font("small", "bold"),
            text_color=status_color
        )
        status_label.pack(side="right", padx=(0, 10))

        # ===== ROW 2: Info Line (Chain + Description + Date + Technician) =====
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=(2, 8))

        # Chain indicator FIRST (if exists) - με ΜΠΛΕ χρώμα
        chain_widget = None
        if self.show_relations:
            full_chain = self._get_full_chain_simple(self.task['id'])
            if len(full_chain) > 1:
                position = next((i for i, t in enumerate(full_chain, 1) if t['id'] == self.task['id']), 1)
                chain_length = len(full_chain)

                chain_widget = ctk.CTkLabel(
                    info_frame,
                    text=f"🔗 {position}/{chain_length}",
                    font=theme_config.get_font("small", "bold"),
                    text_color="#3B8ED0",  # ← Hardcoded ΜΠΛΕ!
                    anchor="w"
                )
                chain_widget.pack(side="left", padx=(0, 5))

                # Separator
                ctk.CTkLabel(
                    info_frame,
                    text="•",
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_disabled"]
                ).pack(side="left", padx=(0, 5))

        # Rest of info (Description + Date + Technician)
        info_parts = []

        # Description
        desc_text = self.task['description'][:45] + "..." if len(self.task['description']) > 45 else self.task[
            'description']
        info_parts.append(desc_text)

        # Date
        info_parts.append(f"📅 {self.task['created_date']}")

        # Technician
        if self.task.get('technician_name'):
            info_parts.append(f"👤 {self.task['technician_name']}")

        info_text = " • ".join(info_parts)

        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        info_label.pack(side="left", fill="x", expand=True)

        # Bind click to all widgets
        # Bind click to all widgets
        if self.on_click:
            # Capture self.task EARLY to avoid reference issues
            task_ref = self.task

            widgets = [
                self, header_frame, left_section, type_label,
                status_label, priority_label,
                info_frame, info_label
            ]

            for widget in widgets:
                # Use task_ref instead of self.task in lambda
                widget.bind("<Button-1>", lambda e, t=task_ref: self.on_click(t))
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
            command=self.on_group_change,
            font=theme_config.get_font("input")
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
        ).grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(10, 5))

        self.units_dict = {}
        self.unit_combo = ctk.CTkComboBox(
            scrollable,
            values=[],
            width=300,
            state="readonly",
            font=theme_config.get_font("input")
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
            state="readonly",
            font=theme_config.get_font("input")
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

        self.created_date_entry = ctk.CTkEntry(
            date_entry_frame,
            width=220,
            font=theme_config.get_font("input")
        )
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

        self.technician_entry = ctk.CTkEntry(
            scrollable,
            width=300,
            font=theme_config.get_font("input")
        )
        self.technician_entry.grid(row=7, column=1, sticky="ew", padx=(5, 10), pady=(0, 15))

        # ===== ROW 8: Περιγραφή (FULL WIDTH) =====

        ctk.CTkLabel(
            scrollable,
            text="Περιγραφή Εργασίας:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.description_text = ctk.CTkTextbox(
            scrollable,
            height=80,
            font=theme_config.get_font("input")
        )
        self.description_text.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))

        # ===== ROW 10: Σημειώσεις (FULL WIDTH) =====

        ctk.CTkLabel(
            scrollable,
            text="Σημειώσεις:",
            font=theme_config.get_font("body", "bold")
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.notes_text = ctk.CTkTextbox(
            scrollable,
            height=60,
            font=theme_config.get_font("input")
        )
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

        # ═══════════════════════════════════════════════════════
        # COMPACT CHAIN PREVIEW (μόνο σε edit mode) - ΣΤΟ ΤΕΛΟΣ!
        # ═══════════════════════════════════════════════════════
        if self.is_edit_mode:
            self.add_compact_chain_preview(scrollable)

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
                                     "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτή την εργασία?\n\n"
                                     "Η εργασία θα μεταφερθεί στον Κάδο Ανακύκλωσης.")

        if result:
            try:
                database.delete_task(self.task_data['id'])
                messagebox.showinfo("Επιτυχία", "Η εργασία διαγράφηκε!")
                self.on_save_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής: {str(e)}")

    def add_compact_chain_preview(self, parent):
        """Προσθήκη compact chain preview κάτω από τα buttons - Edit mode only"""

        theme = theme_config.get_current_theme()

        # Get full chain
        full_chain = self._get_full_chain_simple(self.task_data['id'])

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
            task_info = f"📅 {chain_task['created_date']}  •  {chain_task['task_type_name']}"
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
        self.tab3 = self.tabview.add("Κάδος")
        self.create_recycle_tab(self.tab3)
        
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
            self.expanded_groups = {group['id']: False for group in groups}  # Όλα κλειστά by default

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
        dialog.geometry("500x700")
        dialog.grab_set()
        
        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Μονάδας:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Ομάδα
        ctk.CTkLabel(dialog, text="Ομάδα:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        groups = database.get_all_groups()
        groups_dict = {g['name']: g['id'] for g in groups}
        group_combo = ctk.CTkComboBox(dialog, values=list(groups_dict.keys()), width=450, state="readonly", font=theme_config. get_font("input"))
        group_combo.pack(padx=20, pady=(0, 15))
        if groups_dict:
            group_combo.set(list(groups_dict.keys())[0])
        
        # Τοποθεσία
        ctk.CTkLabel(dialog, text="Τοποθεσία:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        location_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        location_entry.pack(padx=20, pady=(0, 15))
        
        # Μοντέλο
        ctk.CTkLabel(dialog, text="Μοντέλο:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        model_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        model_entry.pack(padx=20, pady=(0, 15))
        
        # Serial Number
        ctk.CTkLabel(dialog, text="Σειριακός Αριθμός:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        serial_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        serial_entry.pack(padx=20, pady=(0, 15))
        
        # Ημερομηνία εγκατάστασης
        ctk.CTkLabel(dialog, text="Ημερομηνία Εγκατάστασης (YYYY-MM-DD):", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        install_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
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

            ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                          height=40).pack(pady=10)
            def confirm_soft_delete():
                from tkinter import messagebox
                if messagebox.askyesno("Διαγραφή",
                                       "Θέλετε να διαγράψετε τη μονάδα; Η ενέργεια είναι αναστρέψιμη από τον κάδο."):
                    res = database.soft_delete_unit(unit_data['id'])
                    if res.get('success'):
                        messagebox.showinfo("Επιτυχία", "Η μονάδα μεταφέρθηκε στον κάδο!")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    else:
                        messagebox.showerror("Σφάλμα", res.get('error', 'Αποτυχία διαγραφής.'))

            ctk.CTkButton(dialog, text="🗑️ Διαγραφή", command=confirm_soft_delete,
                          **theme_config.get_button_style("danger"), height=36).pack(pady=10)

            # Set group
            for group_name, group_id in groups_dict.items():
                if group_id == unit_data['group_id']:
                    group_combo.set(group_name)
                    break



    
    def edit_unit_dialog(self, unit):
        """Wrapper για επεξεργασία μονάδας"""
        self.add_unit_dialog(unit_data=unit)
        
    def add_group_dialog(self, group_data=None):
        """Dialog για προσθήκη/επεξεργασία ομάδας"""
        
        is_edit_mode = group_data is not None
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Ομάδας" if is_edit_mode else "Προσθήκη Νέας Ομάδας")
        dialog.geometry("500x550")
        dialog.grab_set()
        
        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Ομάδας:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100, font=theme_config.get_font("input"))
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

        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                      height=40).pack(pady=10)

        def confirm_soft_delete():
            from tkinter import messagebox
            if messagebox.askyesno("Διαγραφή",
                                   "Θέλετε να διαγράψετε την ομάδα και τις μονάδες της; Η ενέργεια είναι αναστρέψιμη από τον κάδο."):
                res = database.soft_delete_group(group_data['id'])
                if res.get('success'):
                    messagebox.showinfo("Επιτυχία", "Η ομάδα μεταφέρθηκε στον κάδο!")
                    dialog.destroy()
                    self.refresh_callback()
                    self.refresh_ui()
                else:
                    messagebox.showerror("Σφάλμα", res.get('error', 'Αποτυχία διαγραφής.'))

        ctk.CTkButton(dialog, text="🗑️ Διαγραφή", command=confirm_soft_delete,
                      **theme_config.get_button_style("danger"), height=36).pack(pady=10)


        

    
    def edit_group_dialog(self, group):
        """Wrapper για επεξεργασία ομάδας"""
        self.add_group_dialog(group_data=group)

    def manage_unit_ui(unit_id):
        """
        Επεξεργασία και διαγραφή Μονάδας UI
        Εδώ προστίθεται επιλογή διαγραφής μονάδας.
        """
        print(f"Επεξεργασία Μονάδας με ID: {unit_id}")

        # Κώδικας για εμφάνιση των στοιχείων της μονάδας
        # (π.χ. φόρμες, text fields, dropdowns)
        print("Φόρτωση δεδομένων μονάδας για επεξεργασία...")

        print("\n[UI]: Προσθήκη κουμπιού 'Αποθήκευση αλλαγών μονάδας'")
        print("[UI]: Προσθήκη κουμπιού 'Διαγραφή μονάδας'")

        print(f"Για το ID μονάδας {unit_id}, εμφανίζεται το UI.")

        def delete_unit_button_handler():
            """
            Διαχείριση: Διαγραφή Μονάδας
            """
            print(f"[System]: Επιλογή για Διαγραφή Μονάδας με ID {unit_id}")
            # Προσθήκη λογικής για ερώτηση επιβεβαίωσης
            confirmation = input(f"Είστε σίγουροι ότι θέλετε να διαγράψετε τη μονάδα {unit_id}; (y/n): ").lower()
            if confirmation == 'y':
                print(f"[System]: Η μονάδα {unit_id} διαγράφηκε επιτυχώς.")
                # Εκτέλεση διαγραφής από τη βάση δεδομένων
            else:
                print("[System]: Η διαγραφή ακυρώθηκε.")

        # Κλήση του 'delete_unit_button_handler' αν ο χρήστης διαλέξει "Διαγραφή Μονάδας".
        delete_unit_button_handler()

    def manage_group_ui(group_id):
        """
        Επεξεργασία και διαγραφή Ομάδας UI
        Εδώ προστίθεται επιλογή διαγραφής ομάδας.
        """
        print(f"Επεξεργασία Ομάδας με ID: {group_id}")

        # Κώδικας για εμφάνιση των στοιχείων της ομάδας
        # (π.χ. φόρμες, text fields, dropdowns)
        print("Φόρτωση δεδομένων ομάδας για επεξεργασία...")

        print("\n[UI]: Προσθήκη κουμπιού 'Αποθήκευση αλλαγών ομάδας'")
        print("[UI]: Προσθήκη κουμπιού 'Διαγραφή ομάδας'")

        print(f"Για το ID ομάδας {group_id}, εμφανίζεται το UI.")

        def delete_group_button_handler():
            """
            Διαχείριση: Διαγραφή Ομάδας
            """
            print(f"[System]: Επιλογή για Διαγραφή Ομάδας με ID {group_id}")
            # Προσθήκη λογικής για ερώτηση επιβεβαίωσης
            confirmation = input(f"Είστε σίγουροι ότι θέλετε να διαγράψετε την ομάδα {group_id}; (y/n): ").lower()
            if confirmation == 'y':
                print(f"[System]: Η ομάδα {group_id} διαγράφηκε επιτυχώς.")
                # Εκτέλεση διαγραφής από τη βάση δεδομένων
            else:
                print("[System]: Η διαγραφή ακυρώθηκε.")

        # Κλήση του 'delete_group_button_handler' αν ο χρήστης διαλέξει "Διαγραφή Ομάδας".
        delete_group_button_handler()

    def create_recycle_tab(self, parent):
        """Κάδος διαγραμμένων"""
        for w in parent.winfo_children():
            w.destroy()
        theme = theme_config.get_current_theme()
        ctk.CTkLabel(parent, text="🗑️ Κάδος Μονάδων & Ομάδων", font=theme_config.get_font("title", "bold"),
                     text_color=theme["accent_blue"]).pack(pady=20)

        # Ομάδες Κάδου
        groups = database.get_deleted_groups()
        if groups:
            ctk.CTkLabel(parent, text="Διαγραμμένες Ομάδες", font=theme_config.get_font("body", "bold"),
                         text_color=theme["accent_orange"]).pack(anchor="w", padx=20, pady=(10, 5))
            for group in groups:
                frm = ctk.CTkFrame(parent, fg_color=theme["card_bg"], border_color=theme["card_border"], border_width=1)
                frm.pack(fill="x", padx=20, pady=4)
                ctk.CTkLabel(frm, text=f"📂 {group['name']}", font=theme_config.get_font("body"),
                             text_color=theme["text_primary"]).pack(side="left", padx=10, pady=8)
                restore_btn = ctk.CTkButton(frm, text="🔄 Επαναφορά", width=110, height=30,
                                            command=lambda gid=group['id']: self.restore_group_ui(gid),
                                            **theme_config.get_button_style("success"))
                restore_btn.pack(side="right", padx=14, pady=8)
        else:
            ctk.CTkLabel(parent, text="Δεν υπάρχουν διαγραμμένες ομάδες.", font=theme_config.get_font("small"),
                         text_color=theme["text_disabled"]).pack(anchor="w", padx=26, pady=0)

        # Μονάδες Κάδου
        units = database.get_deleted_units()
        if units:
            ctk.CTkLabel(parent, text="Διαγραμμένες Μονάδες", font=theme_config.get_font("body", "bold"),
                         text_color=theme["accent_orange"]).pack(anchor="w", padx=20, pady=(26, 7))
            for unit in units:
                frm = ctk.CTkFrame(parent, fg_color=theme["card_bg"], border_color=theme["card_border"], border_width=1)
                frm.pack(fill="x", padx=20, pady=3)
                label = f"🔧 {unit['name']} ({unit['group_name']})"
                ctk.CTkLabel(frm, text=label, font=theme_config.get_font("small"),
                             text_color=theme["text_primary"]).pack(side="left", padx=10, pady=6)
                restore_btn = ctk.CTkButton(frm, text="🔄 Επαναφορά", width=110, height=30,
                                            command=lambda uid=unit['id']: self.restore_unit_ui(uid),
                                            **theme_config.get_button_style("success"))
                restore_btn.pack(side="right", padx=14, pady=6)
        else:
            ctk.CTkLabel(parent, text="Δεν υπάρχουν διαγραμμένες μονάδες.", font=theme_config.get_font("small"),
                         text_color=theme["text_disabled"]).pack(anchor="w", padx=26, pady=(7, 0))

    def restore_unit_ui(self, unit_id):
        database.restore_unit(unit_id)
        from tkinter import messagebox
        messagebox.showinfo("Επαναφορά", "Η μονάδα επανήλθε από τον κάδο!")
        self.refresh_ui()

    def restore_group_ui(self, group_id):
        database.restore_group(group_id)
        from tkinter import messagebox
        messagebox.showinfo("Επαναφορά", "Η ομάδα και οι μονάδες της επανήλθαν από τον κάδο!")
        self.refresh_ui()

    def refresh_ui(self):
        """Ανανέωση του UI - Phase 2.3"""
        # Clear and recreate tabs
        self.create_units_tab(self.tab1)
        self.create_groups_tab(self.tab2)
        self.create_recycle_tab(self.tab3)


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
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))

        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                 pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100, font=theme_config. get_font("input"))
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
            variable=self.selected_type_var,
            font=theme_config.get_font("input")
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
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))

        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή (προαιρετική):", font=theme_config.get_font("body", "bold")).pack(
            anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100, font=theme_config.get_font("input"))
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
        self.search_entry = ctk.CTkEntry(
            row1,
            width=200,
            placeholder_text="Περιγραφή, σημειώσεις, μονάδα...",
            font=theme_config.get_font("input")
        )
        self.search_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Κατάσταση:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(20, 5))
        self.status_combo = ctk.CTkComboBox(
            row1,
            values=["Όλες", "Εκκρεμείς", "Ολοκληρωμένες"],
            width=150,
            state="readonly",
            font=theme_config.get_font("input")
        )
        self.status_combo.set("Όλες")
        self.status_combo.pack(side="left", padx=5)
        
        # Row 2: Unit, Task Type, Dates
        row2 = ctk.CTkFrame(filters_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(row2, text="Μονάδα:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(0, 5))
        units = database.get_all_units()
        unit_names = ["Όλες"] + [f"{u['name']} - {u['group_name']}" for u in units]
        self.units_dict = {f"{u['name']} - {u['group_name']}": u['id'] for u in units}
        self.unit_combo = ctk.CTkComboBox(
            row2,
            values=unit_names,
            width=200,
            state="readonly",
            font=theme_config.get_font("input")
        )
        self.unit_combo.set("Όλες")
        self.unit_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Είδος:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(20, 5))
        task_types = database.get_all_task_types()
        type_names = ["Όλα"] + [tt['name'] for tt in task_types]
        self.types_dict = {tt['name']: tt['id'] for tt in task_types}
        self.type_combo = ctk.CTkComboBox(
            row2,
            values=type_names,
            width=150,
            state="readonly",
            font=theme_config.get_font("input")
        )
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
    """
    Recycle Bin view - lists soft-deleted tasks with options to Restore or Permanently Delete.
    Uses compact, less-dangerous Delete button (small, with confirmation).
    """

    def __init__(self, parent, on_change_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.theme = theme_config.get_current_theme()

        self.pack(fill="both", expand=True, padx=40, pady=10)

        # Header
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=self.theme["bg_secondary"])
        header_frame.pack(fill="x", pady=(0, 12))
        header_frame.pack_propagate(False)
        header_frame.configure(height=60)

        title = ctk.CTkLabel(
            header_frame,
            text="🗑️ Κάδος Ανακύκλωσης - Διαγραμμένες Εργασίες",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["accent_blue"]
        )
        title.pack(side="left", padx=15)

        info = ctk.CTkLabel(
            header_frame,
            text="Εδώ μπορείτε να επαναφέρετε ή να διαγράψετε οριστικά εργασίες.",
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"]
        )
        info.pack(side="right", padx=15)

        # Scrollable list container
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=(8, 0))

        # Load content
        self.load_deleted_tasks()

    def _make_button(self, parent, text, command, style_type="primary", width=100, height=32):
        """
        Small helper to create buttons using theme_config.get_button_style safely.
        Avoids passing duplicate keyword args that cause CTkButton TypeError.
        """
        style = theme_config.get_button_style(style_type) or {}
        # Ensure we don't accidentally pass duplicates of common args
        # We'll pass style dict entirely and also provide width/height/text/command explicitly.
        btn = ctk.CTkButton(parent, text=text, command=command, width=width, height=height, **style)
        return btn

    def load_deleted_tasks(self):
        """Load soft-deleted tasks from DB and render them."""
        # Clear list
        for w in self.list_frame.winfo_children():
            w.destroy()

        deleted = database.get_deleted_tasks()

        if not deleted:
            empty_lbl = ctk.CTkLabel(
                self.list_frame,
                text="Δεν υπάρχουν διαγραμμένες εργασίες στον κάδο.",
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"]
            )
            empty_lbl.pack(pady=40)
            return

        # Count header
        count_lbl = ctk.CTkLabel(
            self.list_frame,
            text=f"Βρέθηκαν {len(deleted)} εργασίες στον κάδο",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        )
        count_lbl.pack(anchor="w", padx=8, pady=(8, 12))

        for task in deleted:
            self._render_deleted_task(task)

    def _render_deleted_task(self, task):
        """Render a single deleted task row with Restore + Delete buttons."""
        row = ctk.CTkFrame(self.list_frame, fg_color=self.theme["card_bg"],
                           border_color=self.theme["card_border"], border_width=1, corner_radius=8)
        row.pack(fill="x", padx=8, pady=6)

        # Left info: basic summary
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=8)

        title_text = f"#{task['id']}  •  {task['task_type_name']} — {task['unit_name']}"
        lbl_title = ctk.CTkLabel(left, text=title_text, font=theme_config.get_font("body", "bold"),
                                 text_color=self.theme["text_primary"], anchor="w")
        lbl_title.pack(fill="x")

        subtitle = task.get('task_item_name') or task.get('description') or ""
        lbl_sub = ctk.CTkLabel(left, text=f"{task.get('created_date')}  •  {subtitle}",
                               font=theme_config.get_font("small"), text_color=self.theme["text_secondary"], anchor="w")
        lbl_sub.pack(fill="x", pady=(3, 0))

        # Right actions: Restore + Permanent Delete (compact)
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="right", padx=12, pady=8)

        # Restore button (green/success)
        restore_cmd = lambda t=task: self._on_restore(t)
        restore_btn = self._make_button(actions, "Επαναφορά", restore_cmd, style_type="success", width=110, height=30)
        restore_btn.pack(side="right", padx=(6, 0))

        # Permanent delete button (small, danger). Confirm before deleting.
        delete_cmd = lambda t=task: self._on_permanent_delete(t)
        delete_btn = self._make_button(actions, "Διάγρ. Οριστικά", delete_cmd, style_type="danger", width=120, height=30)
        delete_btn.pack(side="right", padx=(0, 6))

    def _on_restore(self, task):
        """Restore a soft-deleted task."""
        from tkinter import messagebox
        result = messagebox.askyesno("Επαναφορά Εργασίας", f"Θέλετε να επαναφέρετε την εργασία #{task['id']};")
        if not result:
            return

        try:
            database.restore_task(task['id'])
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την επαναφορά: {e}")
            return

        # refresh list and notify caller
        self.load_deleted_tasks()
        if callable(self.on_change_callback):
            self.on_change_callback()

    def _on_permanent_delete(self, task):
        """Permanently delete task after confirmation."""
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Οριστική Διαγραφή",
            f"Η εργασία #{task['id']} θα διαγραφεί οριστικά. Η ενέργεια δεν μπορεί να αναιρεθεί.\n\nΘέλετε να συνεχίσετε?"
        )
        if not result:
            return

        try:
            database.permanent_delete_task(task['id'])
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την οριστική διαγραφή: {e}")
            return

        # refresh list and notify caller
        self.load_deleted_tasks()
        if callable(self.on_change_callback):
            self.on_change_callback()




class TaskRelationshipsView(ctk.CTkFrame):
    """Διαχείριση σχέσεων εργασιών - Enhanced Timeline View"""

    def __init__(self, parent, task_data, refresh_callback):
        super().__init__(parent, fg_color="transparent")

        self.task_data = task_data
        self.refresh_callback = refresh_callback
        self.theme = theme_config.get_current_theme()
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_ui()
        self.load_relationships()

    def create_ui(self):
        """Δημιουργία UI"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # Title με unit info
        title_text = f"🔗 Αλυσίδα Εργασιών για {self.task_data['unit_name']}"
        ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(side="left")

        # Info button
        info_btn = ctk.CTkButton(
            header_frame,
            text="ℹ️ Βοήθεια",
            command=self.show_help,
            width=100,
            height=32,
            **theme_config.get_button_style("secondary")
        )
        info_btn.pack(side="right")

        # Scrollable timeline
        self.timeline_frame = ctk.CTkScrollableFrame(self)
        self.timeline_frame.pack(fill="both", expand=True)



    def show_help(self):
        """Εμφάνιση βοήθειας"""
        help_text = """
    🔗 Αλυσίδα Εργασιών - Πώς λειτουργεί: 
    ... 
        """
        messagebox.showinfo("Βοήθεια - Αλυσίδα Εργασιών", help_text)

    # ← ΕΔΩ προσθέτετε την get_full_chain()
    def get_full_chain(self, task_id):
        """Παίρνει ολόκληρη την αλυσίδα (parents + current + children recursively)"""

        chain = []
        visited_parents = set()  # Αποφυγή infinite loops στους parents
        visited_children = set()  # Αποφυγή infinite loops στα children

        # 1. Βρες όλους τους parents recursively
        def get_all_parents(tid):
            if tid in visited_parents:
                return
            visited_parents.add(tid)

            rels = database.get_related_tasks(tid)
            for parent in rels['parents']:
                parent_id = parent['id']
                if parent_id not in [c['id'] for c in chain]:
                    chain.insert(0, parent)  # Προσθήκη στην αρχή
                    get_all_parents(parent_id)  # Recursive

        # 2. Βρες όλα τα children recursively
        def get_all_children(tid):
            if tid in visited_children:
                return
            visited_children.add(tid)

            rels = database.get_related_tasks(tid)
            for child in rels['children']:
                child_id = child['id']
                if child_id not in [c['id'] for c in chain]:
                    chain.append(child)  # Προσθήκη στο τέλος
                    get_all_children(child_id)  # Recursive

        # Build chain:  parents + current + children
        get_all_parents(task_id)

        # Προσθήκη current task
        chain.append(self.task_data)

        get_all_children(task_id)

        return chain

    def load_relationships(self):
        """Φόρτωση και εμφάνιση αλυσίδας - Updated to show full chain"""

        # Clear
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()

        # Get FULL chain
        full_chain = self.get_full_chain(self.task_data['id'])

        # Find current position
        current_position = None
        for idx, task in enumerate(full_chain, 1):
            if task['id'] == self.task_data['id']:
                current_position = idx
                break

        if current_position is None:
            current_position = 1
            full_chain = [self.task_data]

        total_in_chain = len(full_chain)

        # Info banner
        info_frame = ctk.CTkFrame(
            self.timeline_frame,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        info_frame.pack(fill="x", padx=10, pady=(0, 20))

        info_text = f"📊 Αλυσίδα {total_in_chain} εργασιών  •  Θέση {current_position}/{total_in_chain}"
        if current_position == 1:
            info_text += "  •  🔵 Αυτή είναι η ΠΡΩΤΗ εργασία"
        if current_position == total_in_chain:
            info_text += "  •  🔚 Αυτή είναι η ΤΕΛΕΥΤΑΙΑ εργασία"

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(padx=20, pady=12)

        # Add parent button at top (if first in chain)
        if current_position == 1 and total_in_chain == 1:
            # Μόνος σου στην αλυσίδα
            self.create_add_button("parent", position=0)
            self.create_arrow("προκάλεσε", dashed=True)

        # Display all tasks in chain
        child_counter = 0  # Global counter για σωστή αρίθμηση children

        for idx, task in enumerate(full_chain, 1):
            # Determine type
            if idx < current_position:
                item_type = "parent"
                sequence_num = None
            elif idx == current_position:
                item_type = "current"
                sequence_num = None
            else:
                item_type = "child"
                child_counter += 1
                sequence_num = child_counter

            # ═══════════════════════════════════════════
            # FIX: Κουμπί ΜΟΝΟ για την τρέχουσα
            # ═══════════════════════════════════════════
            is_removable = (item_type == "current" and total_in_chain > 1)

            self.create_timeline_item(
                task,
                position=idx,
                item_type=item_type,
                sequence_num=sequence_num,
                is_removable=is_removable
            )

            # Arrow between tasks
            if idx < total_in_chain:
                self.create_arrow("ακολούθησε")

        # Add child button at bottom
        if current_position == total_in_chain:
            self.create_add_button("child", position=total_in_chain + 1)

    def create_timeline_item(self, task, position, item_type, sequence_num=None, is_removable=True):
        """Δημιουργία στοιχείου timeline"""

        # Container
        item_container = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        item_container.pack(fill="x", padx=10, pady=5)

        # Position badge + Type indicator
        badge_frame = ctk.CTkFrame(item_container, fg_color="transparent")
        badge_frame.pack(fill="x", pady=(0, 5))

        # Position number
        position_label = ctk.CTkLabel(
            badge_frame,
            text=f"[{position}]",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_disabled"],
            width=40
        )
        position_label.pack(side="left")

        # Type badge
        if item_type == "parent":
            badge_text = "🔵 Αρχική Εργασία"
            badge_color = self.theme["accent_blue"]
        elif item_type == "current":
            badge_text = "🟡 ΤΡΕΧΟΥΣΑ ΕΡΓΑΣΙΑ"
            badge_color = self.theme["accent_orange"]
        else:  # child
            badge_text = f"🟢 Συνέχεια {sequence_num}" if sequence_num else "🟢 Συνέχεια"
            badge_color = self.theme["accent_green"]

        badge = ctk.CTkLabel(
            badge_frame,
            text=badge_text,
            font=theme_config.get_font("body", "bold"),
            text_color=badge_color
        )
        badge.pack(side="left", padx=10)

        # Card container
        card_container = ctk.CTkFrame(item_container, fg_color="transparent")
        card_container.pack(fill="x")

        # Task card
        task_card_frame = ctk.CTkFrame(card_container, fg_color="transparent")
        task_card_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Enhanced task card - Bold border για current
        card = ctk.CTkFrame(
            task_card_frame,
            fg_color=self.theme["card_bg"],
            border_color=badge_color,
            border_width=4 if item_type == "current" else 2,
            corner_radius=10
        )
        card.pack(fill="x", padx=(40, 0))

        # ═══════════════════════════════════════════════════
        # REMOVE BUTTON - Μόνο για current, πάνω δεξιά
        # ═══════════════════════════════════════════════════

        if is_removable and item_type == "current":
            remove_container = ctk.CTkFrame(card, fg_color="transparent")
            remove_container.pack(fill="x", padx=12, pady=(10, 0))

            # Spacer (pushes button to right)
            ctk.CTkLabel(remove_container, text="").pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                remove_container,
                text="✖ Αφαίρεση από Αλυσίδα",
                command=lambda t=task, it=item_type: self.remove_relationship(t, it),
                width=180,
                height=30,
                fg_color=self.theme["accent_red"],
                hover_color="#8B0000",
                text_color="white",
                font=theme_config.get_font("small", "bold"),
                corner_radius=6
            ).pack(side="right")

        # Date badge (prominent)
        date_badge = ctk.CTkLabel(
            card,
            text=f"📅 {task['created_date']}",
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["accent_blue"],
            fg_color=self.theme["bg_secondary"],
            corner_radius=6,
            padx=10,
            pady=4
        )
        date_badge.pack(anchor="w", padx=12, pady=(10, 5))

        # Task info
        task_info = f"🔧 {task['task_type_name']}"
        if task.get('task_item_name'):
            task_info += f" → {task['task_item_name']}"

        info_label = ctk.CTkLabel(
            card,
            text=task_info,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        info_label.pack(anchor="w", padx=12, pady=(0, 5))

        # Description (truncated)
        desc_text = task['description'][: 80] + "..." if len(task['description']) > 80 else task['description']
        desc_label = ctk.CTkLabel(
            card,
            text=desc_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            anchor="w",
            wraplength=600
        )
        desc_label.pack(anchor="w", padx=12, pady=(0, 5))

        # Status + Technician
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.pack(fill="x", padx=12, pady=(0, 10))

        status_icon = "✅" if task['status'] == 'completed' else "⏳"
        status_text = "Ολοκληρωμένη" if task['status'] == 'completed' else "Εκκρεμής"

        ctk.CTkLabel(
            meta_frame,
            text=f"{status_icon} {status_text}",
            font=theme_config.get_font("tiny"),
            text_color=self.theme["text_disabled"]
        ).pack(side="left", padx=(0, 15))

        if task.get('technician_name'):
            ctk.CTkLabel(
                meta_frame,
                text=f"👤 {task['technician_name']}",
                font=theme_config.get_font("tiny"),
                text_color=self.theme["text_disabled"]
            ).pack(side="left")

    def create_arrow(self, label_text, dashed=False):
        """Δημιουργία βέλους σύνδεσης"""

        arrow_container = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        arrow_container.pack(fill="x", padx=10, pady=8)

        # Vertical line
        line_frame = ctk.CTkFrame(
            arrow_container,
            width=4,
            height=30,
            fg_color=self.theme["card_border"] if dashed else self.theme["accent_blue"],
            corner_radius=2
        )
        line_frame.pack(side="left", padx=(58, 10))  # Align with position badge

        # Label - FIX:   Remove "italic", use "normal"
        ctk.CTkLabel(
            arrow_container,
            text=f"↓ {label_text}",
            font=theme_config.get_font("small"),  # ← FIX:   Removed "italic"
            text_color=self.theme["text_disabled"] if dashed else self.theme["text_secondary"]
        ).pack(side="left")

    def create_add_button(self, relation_type, position):
        """Κουμπί προσθήκης στο timeline"""

        btn_container = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=10, pady=10)

        # Position badge
        ctk.CTkLabel(
            btn_container,
            text=f"[{position}]" if position > 0 else "[? ]",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_disabled"],
            width=40
        ).pack(side="left")

        # Add button
        if relation_type == "parent":
            btn_text = "➕ Προσθήκη Αρχικής Εργασίας"
            icon = "🔵"
        else:
            btn_text = "➕ Προσθήκη Νέας Συνέχειας"
            icon = "🟢"

        add_btn = ctk.CTkButton(
            btn_container,
            text=f"{icon} {btn_text}",
            command=lambda: self.add_relationship_dialog(relation_type),
            height=45,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        add_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def add_relationship_dialog(self, relation_type):
        """Dialog για προσθήκη σύνδεσης - Grouped by Unit"""

        dialog = ctk.CTkToplevel(self)

        if relation_type == "parent":
            title_text = "Προσθήκη Αρχικής Εργασίας"
            icon = "🔵"
            info_text = "Επιλέξτε την εργασία που προηγήθηκε/προκάλεσε την τρέχουσα"
        else:
            title_text = "Προσθήκη Συνέχειας Εργασίας"
            icon = "🟢"
            info_text = "Επιλέξτε την εργασία που ακολούθησε/προέκυψε από την τρέχουσα"

        dialog.title(title_text)
        dialog.geometry("850x750")
        dialog.grab_set()

        # Header με visual flow
        header_frame = ctk.CTkFrame(
            dialog,
            fg_color=self.theme["card_bg"],
            corner_radius=10
        )
        header_frame.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(
            header_frame,
            text=f"{icon} {title_text}",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header_frame,
            text=info_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"]
        ).pack(padx=20, pady=(0, 10))

        # Visual flow indicator
        flow_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        flow_frame.pack(fill="x", padx=20, pady=(0, 15))

        if relation_type == "parent":
            flow_text = "[ Επιλογή ] → προκάλεσε → [ Τρέχουσα Εργασία ]"
        else:
            flow_text = "[ Τρέχουσα Εργασία ] → ακολούθησε → [ Επιλογή ]"  # ← FIX:  Κλείσιμο string

        ctk.CTkLabel(
            flow_frame,
            text=flow_text,
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack()

        # Scrollable task list
        scrollable = ctk.CTkScrollableFrame(dialog, height=500)
        scrollable.pack(fill="both", expand=True, padx=20, pady=10)

        # Get available tasks (exclude current task and already linked)
        all_tasks = database.get_all_tasks()
        current_id = self.task_data['id']

        # Get existing relationships
        relations = database.get_related_tasks(current_id)

        # Filter out current task and already linked tasks
        linked_ids = {current_id}
        linked_ids.update([t['id'] for t in relations['parents']])
        linked_ids.update([t['id'] for t in relations['children']])

        available_tasks = [t for t in all_tasks if
                           t['id'] not in linked_ids and t['unit_id'] == self.task_data['unit_id']]

        if not available_tasks:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν διαθέσιμες εργασίες για σύνδεση.",
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=50)
            return

        # Display tasks
        for task in available_tasks:
            task_container = ctk.CTkFrame(
                scrollable,
                fg_color=self.theme["card_bg"],
                border_color=self.theme["card_border"],
                border_width=1,
                corner_radius=8
            )
            task_container.pack(fill="x", pady=3, padx=5)

            # Task info (left side)
            info_frame = ctk.CTkFrame(task_container, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            # Date badge
            ctk.CTkLabel(
                info_frame,
                text=f"📅 {task['created_date']}",
                font=theme_config.get_font("tiny", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(anchor="w")

            # Task type + item
            type_text = f"🔧 {task['task_type_name']}"
            if task.get('task_item_name'):
                type_text += f" → {task['task_item_name']}"

            ctk.CTkLabel(
                info_frame,
                text=type_text,
                font=theme_config.get_font("small", "bold"),
                text_color=self.theme["text_primary"],
                anchor="w"
            ).pack(anchor="w")

            # Description (truncated)
            desc = task['description'][: 60] + "..." if len(task['description']) > 60 else task['description']
            ctk.CTkLabel(
                info_frame,
                text=desc,
                font=theme_config.get_font("tiny"),
                text_color=self.theme["text_secondary"],
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))

            # Add button (right side)
            add_btn = ctk.CTkButton(
                task_container,
                text="➕ Προσθήκη",
                command=lambda t=task: self.link_task(t, relation_type, dialog),
                width=100,
                height=30,
                **theme_config.get_button_style("success")
            )
            add_btn.pack(side="right", padx=10, pady=8)

        # Cancel button at bottom
        ctk.CTkButton(
            dialog,
            text="✖ Ακύρωση",
            command=dialog.destroy,
            width=150,
            height=40,
            **theme_config.get_button_style("secondary")
        ).pack(pady=15)

    def link_task(self, selected_task, relation_type, dialog):
        """Link the selected task to current task"""

        if relation_type == "parent":
            parent_id = selected_task['id']
            child_id = self.task_data['id']
        else:
            parent_id = self.task_data['id']
            child_id = selected_task['id']

        try:
            database.add_task_relationship(parent_id, child_id, "related")
            messagebox.showinfo("Επιτυχία", f"Η σύνδεση προστέθηκε με επιτυχία!")
            dialog.destroy()
            self.load_relationships()
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία σύνδεσης: {str(e)}")

    def remove_relationship(self, task, item_type):
        """Remove current task from chain"""

        result = messagebox.askyesno(
            "Επιβεβαίωση Αφαίρεσης",
            "Είστε σίγουροι ότι θέλετε να αφαιρέσετε αυτή την εργασία από την αλυσίδα?\n\n"
            "Η εργασία θα παραμείνει ενεργή αλλά θα αποσυνδεθεί."
        )

        if result:
            try:
                current_id = self.task_data['id']

                # ✅ ΝΕΟ:  Χρήση του remove_task_from_chain με bypass logic!
                database.remove_task_from_chain(current_id)

                messagebox.showinfo("Επιτυχία", "Η εργασία αφαιρέθηκε από την αλυσίδα!")
                self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία αφαίρεσης: {str(e)}")
