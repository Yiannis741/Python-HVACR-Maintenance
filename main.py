"""
HVACR Maintenance System - Phase 2
Σύστημα Διαχείρισης Συντηρήσεων HVACR για Νοσοκομείο
"""

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import ui_components
import theme_config


class HVACRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Φόρτωση theme
        self.theme = theme_config.get_current_theme()

        # Ρυθμίσεις παραθύρου
        self.title("HVACR Maintenance System - Σύστημα Συντήρησης v2.0")
        
        self.minsize(1200, 700)
        self.configure(fg_color=self.theme["bg_primary"])

        # Αρχικοποίηση database
        database.init_database()

        # Δημιουργία UI layout
        self.create_layout()

        # Φόρτωση αρχικών δεδομένων
        self.load_initial_data()
        
        # Maximize window (μετά το UI setup)
        self.after(10, lambda: self.state('zoomed'))

    def create_layout(self):
        """Δημιουργία του βασικού layout"""

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----- ΑΡΙΣΤΕΡΗ SIDEBAR -----
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.theme["bg_secondary"])
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        self.create_sidebar()

        # ----- ΚΕΝΤΡΙΚΗ ΠΕΡΙΟΧΗ -----
        # Main container for frame swapping (wrapper)


        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")


        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)


        self.main_container.grid_columnconfigure(0, weight=1)


        self.main_container.grid_rowconfigure(0, weight=1)


        


        # Content frame (swappable)


        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        

        self.main_frame.grid(row=0, column=0, sticky="nsew")


        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Αρχικό περιεχόμενο
        self.show_dashboard()

    def create_sidebar(self):
        """Δημιουργία της αριστερής sidebar με κουμπιά"""

        # Logo/Τίτλος
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="HVACR\nMAINTENANCE\nv2.0",
            font=theme_config.get_font("subtitle", "bold"),
            text_color=self.theme["accent_blue"]
        )
        title_label.pack(pady=(20, 30))

        # Κουμπιά με style types
        buttons_config = [
            ("🏠 Αρχική", self.show_dashboard, "primary"),
            ("➕ Νέα Εργασία", self.show_new_task, "success"),
            ("📋 Ιστορικό", self.show_history, "primary"),
            # ("✏️ Επεξεργασία Εγγραφής", self.show_edit, "primary"),  # REMOVED - Ο χρήστης μπορεί να επεξεργαστεί από το Ιστορικό
            ("🏢 Διαχείριση Μονάδων", self.show_units_management, "primary"),
            ("📋 Διαχείριση Εργασιών", self.show_task_management, "primary"),
            ("📅 Πρόγραμμα Βαρδιών", self.show_shifts, "primary"),
            ("📤 Εξαγωγή", self.show_export, "primary"),
            ("🗑️ Κάδος Ανακύκλωσης", self.show_recycle_bin, "danger"),
            ("⚙️ Ρυθμίσεις", self.show_settings, "secondary"),
        ]

        self.sidebar_buttons = {}

        for btn_text, command, style_type in buttons_config:
            style = theme_config.get_button_style(style_type)
            btn = ctk.CTkButton(
                self.sidebar,
                text=btn_text,
                command=command,
                width=200,
                height=45,
                font=theme_config.get_font("body", "bold"),
                **style  # ← 3D effect με border!
            )
            btn.pack(pady=8, padx=10)
            self.sidebar_buttons[btn_text] = btn

    def adjust_color(self, hex_color, adjustment):
        """Προσαρμογή χρώματος για hover effect"""
        return theme_config.adjust_color(hex_color, adjustment)

    def clear_main_frame(self):
        """
        Καθαρισμός της κεντρικής περιοχής - FRAME SWAPPING (NO FLICKER)
        
        Technique: Δημιουργία νέου frame + atomic swap αντί για in-place destroy
        """
        # 1. Δημιουργία νέου frame (κρυφό)
        new_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        new_frame.grid_columnconfigure(0, weight=1)
        new_frame.grid_rowconfigure(0, weight=1)
        
        # 2. Reference στο παλιό
        old_frame = self.main_frame
        
        # 3. ATOMIC SWAP
        self.main_frame = new_frame
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 4. Καταστροφή παλιού (μετά το swap - invisible)
        self.after(1, lambda: old_frame.destroy() if old_frame.winfo_exists() else None)

    def _finalize_view_render(self):
        """Helper: Finalize rendering μετά τη δημιουργία UI"""
        self.main_frame.update_idletasks()

    # ----- VIEWS -----

    def show_dashboard(self):
        """Εμφάνιση της αρχικής οθόνης"""
        self.clear_main_frame()

        # Τίτλος
        title = ctk.CTkLabel(
            self.main_frame,
            text="🏥 Καλώς ήρθατε στο Σύστημα HVACR Maintenance",
            font=theme_config.get_font("title_large", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=(40, 20))

        subtitle = ctk.CTkLabel(
            self.main_frame,
            text=f"Σήμερα: {datetime.now().strftime('%d/%m/%Y')} | Phase 2 - Ενημερωμένη Έκδοση",
            font=theme_config.get_font("heading"),
            text_color=self.theme["text_secondary"]
        )
        subtitle.pack(pady=10)

        # Stats removed για περισσότερο χώρο στις εργασίες

        # Εκκρεμείς εργασίες
        recent_label = ctk.CTkLabel(
            self.main_frame,
            text="⏳ Εκκρεμείς Εργασίες (Κλικ για επεξεργασία)",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        recent_label.pack(pady=(20, 20))  # Μειωμένο padding επειδή δεν έχουμε stats

        # Scrollable frame για tasks (ΝΕΟ - με fixed height)
        self.dashboard_tasks_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            height=400,  # Fixed height να μην αλλάζει
            fg_color="transparent"
        )
        self.dashboard_tasks_frame.pack(fill="both", expand=True, padx=40, pady=10)

        self.load_dashboard_tasks()

    def load_dashboard_tasks(self):
        """Φόρτωση ΜΟΝΟ εκκρεμών tasks για το dashboard"""

        # Clear existing tasks only
        if hasattr(self, 'dashboard_tasks_frame'):
            for widget in self.dashboard_tasks_frame.winfo_children():
                widget.destroy()

        # ΑΛΛΑΓΗ: Φέρνουμε ΜΟΝΟ εκκρεμείς εργασίες
        all_tasks = database.get_recent_tasks(50)  # Φέρνουμε περισσότερα για να φιλτράρουμε
        tasks = [t for t in all_tasks if t.get('status') == 'pending'][:15]  # Κρατάμε τις 15 πρώτες εκκρεμείς

        if not tasks:
            no_tasks = ctk.CTkLabel(
                self.dashboard_tasks_frame,
                text="Δεν υπάρχουν πρόσφατες εργασίες",
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"]
            )
            no_tasks.pack(pady=20)
            return

        for task in tasks:
            task_card = ui_components.TaskCard(
                self.dashboard_tasks_frame,
                task,
                on_click=self.on_task_click_from_dashboard
            )
            task_card.pack(fill="x", pady=3, padx=5)

    def create_stat_card(self, parent, title, value, column):
        """Δημιουργία καρτέλας στατιστικού"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"],
            border_width=1
        )
        card.grid(row=0, column=column, padx=15, pady=20, sticky="ew")

        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=theme_config.get_font("stat_value", "bold"),
            text_color=self.theme["accent_blue"]
        )
        value_label.pack(pady=(20, 5))

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=theme_config.get_font("body"),
            text_color=self.theme["text_secondary"]
        )
        title_label.pack(pady=(5, 20))

    def show_recent_tasks(self):
        """Εμφάνιση πρόσφατων εργασιών"""
        tasks = database.get_recent_tasks(5)

        if not tasks:
            no_tasks = ctk.CTkLabel(
                self.main_frame,
                text="Δεν υπάρχουν πρόσφατες εργασίες",
                font=ctk.CTkFont(size=14)
            )
            no_tasks.pack(pady=20)
            return

        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self.main_frame, height=250)
        scrollable.pack(fill="both", expand=True, padx=40, pady=10)

        for task in tasks:
            task_card = ui_components.TaskCard(scrollable, task, on_click=self.on_task_click_from_dashboard)
            task_card.pack(fill="x", pady=5, padx=10)

    def on_task_click_from_dashboard(self, task):
        """Callback όταν κάνεις κλικ σε εργασία από το dashboard"""
        self.show_task_detail(task)

    def show_new_task(self):
        """Εμφάνιση φόρμας νέας εργασίας"""
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="➕ Νέα Εργασία",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)

        # Form
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=20, padx=100, fill="both", expand=True)

        ui_components.TaskForm(form_frame, self.on_task_saved)

    def on_task_saved(self):
        """Callback όταν αποθηκευτεί μια εργασία"""

        # Αν είμαστε στο dashboard, κάνε μόνο reload των tasks (όχι rebuild όλου!)
        if hasattr(self, 'dashboard_tasks_frame') and self.dashboard_tasks_frame.winfo_exists():
            self.load_dashboard_tasks()  # Μόνο τα tasks, όχι όλο το dashboard
        else:
            self.show_dashboard()  # Full reload μόνο αν δεν είμαστε στο dashboard

    def show_history(self):
        """Εμφάνιση ιστορικού εργασιών με φίλτρα ανά μονάδα - FIXED"""
        self.clear_main_frame()

        # ═══════════════════════════════════════════════════════════
        # TITLE IN STYLED BOX
        # ═══════════════════════════════════════════════════════════
        title_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=self.theme["bg_secondary"],
            border_color=self.theme["accent_blue"],
            border_width=2,
            height=60
        )
        title_frame.pack(fill="x", padx=40, pady=(20, 10))
        title_frame.pack_propagate(False)

        title = ctk.CTkLabel(
            title_frame,
            text="📋 Ιστορικό Εργασιών",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["accent_blue"]
        )
        title.pack(expand=True)

        # ═══════════════════════════════════════════════════════════
        # UNIT DROPDOWNS ROW (Groups → Units) - FIXED
        # ═══════════════════════════════════════════════════════════
        units_filter_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            height=70
        )
        units_filter_frame.pack(fill="x", padx=40, pady=(0, 10))
        units_filter_frame.pack_propagate(False)

        # Content container
        units_content = ctk.CTkFrame(units_filter_frame, fg_color="transparent")
        units_content.pack(fill="x", padx=20, pady=15)

        # "Όλες" button (Removed "ΟΜΑΔΕΣ ΜΟΝΑΔΩΝ" label για περισσότερο χώρο)
        self.all_units_btn = ctk.CTkButton(
            units_content,
            text="Όλες",
            command=lambda: self.filter_by_unit(None),
            width=100,
            height=35,
            **theme_config.get_button_style("primary")
        )
        self.all_units_btn.pack(side="left", padx=5)

        # ✅ FIX: Get ALL groups and create dropdowns properly
        groups = database.get_all_groups()
        self.unit_filter_buttons = {}

        for group in groups:
            units = database.get_units_by_group(group['id'])

            if units:
                # Create dropdown per group
                unit_names = [u['name'] for u in units]
                unit_ids = {u['name']: u['id'] for u in units}

                # ✅ FIX: Proper closure to capture unit_ids
                def make_unit_filter(uid_map):
                    def handler(selected):
                        unit_id = uid_map.get(selected)
                        if unit_id is not None:
                            self.filter_by_unit(unit_id)

                    return handler

                dropdown = ctk.CTkComboBox(
                    units_content,
                    values=unit_names,
                    width=180,
                    height=35,
                    state="readonly",
                    command=make_unit_filter(unit_ids)
                )
                dropdown.set(group['name'])  # Show group name as placeholder
                dropdown.pack(side="left", padx=5)

                self.unit_filter_buttons[group['id']] = dropdown

        # ═══════════════════════════════════════════════════════════
        # COMPACT SEARCH ROW
        # ═══════════════════════════════════════════════════════════
        search_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            height=55
        )
        search_frame.pack(fill="x", padx=40, pady=(0, 10))
        search_frame.pack_propagate(False)

        search_content = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_content.pack(fill="x", padx=15, pady=10)

        # Search
        ctk.CTkLabel(
            search_content,
            text="🔍 Αναζήτηση:",
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(0, 5))

        self.history_search_entry = ctk.CTkEntry(
            search_content,
            width=250,  # ✅ FIX: Wider for better UX
            height=32,
            placeholder_text="ID, Περιγραφή, Μονάδα, Τεχνικός..."
        )
        self.history_search_entry.pack(side="left", padx=5)
        self.history_search_entry.bind("<KeyRelease>", lambda e: self.apply_history_filters())

        # Status
        ctk.CTkLabel(
            search_content,
            text="Κατάσταση:",
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(15, 5))

        self.history_status_combo = ctk.CTkComboBox(
            search_content,
            values=["Όλες", "Εκκρεμείς", "Ολοκληρωμένες"],
            width=150,
            height=32,
            state="readonly",
            command=lambda e: self.apply_history_filters()
        )
        self.history_status_combo.set("Όλες")
        self.history_status_combo.pack(side="left", padx=5)

        # Task Type
        ctk.CTkLabel(
            search_content,
            text="Είδος:",
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=(15, 5))

        task_types = database.get_all_task_types()
        type_names = ["Όλα"] + [tt['name'] for tt in task_types]
        self.history_types_dict = {tt['name']: tt['id'] for tt in task_types}

        self.history_type_combo = ctk.CTkComboBox(
            search_content,
            values=type_names,
            width=150,
            height=32,
            state="readonly",
            command=lambda e: self.apply_history_filters()
        )
        self.history_type_combo.set("Όλα")
        self.history_type_combo.pack(side="left", padx=5)

        # ═══════════════════════════════════════════════════════════
        # TASKS DISPLAY AREA
        # ═══════════════════════════════════════════════════════════
        self.history_tasks_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.history_tasks_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Initial load - Show ALL tasks
        self.current_unit_filter = None
        self.load_history_tasks()

    def filter_by_unit(self, unit_id):
        """Filter tasks by selected unit"""
        self.current_unit_filter = unit_id
        self.load_history_tasks()

    def apply_history_filters(self):
        """Apply search filters to history view"""
        self.load_history_tasks()

    def load_history_tasks(self):
        """Load and display filtered tasks"""

        # Clear existing
        for widget in self.history_tasks_frame.winfo_children():
            widget.destroy()

        # Get filter values (hasattr checks ensure we don't crash if called before UI init)
        search_text = self.history_search_entry.get().strip() or None if hasattr(self, 'history_search_entry') else None

        status_map = {"Όλες": None, "Εκκρεμείς": "pending", "Ολοκληρωμένες": "completed"}
        status = status_map.get(self.history_status_combo.get()) if hasattr(self, 'history_status_combo') else None

        type_key = self.history_type_combo.get() if hasattr(self, 'history_type_combo') else "Όλα"
        task_type_id = self.history_types_dict.get(type_key) if type_key != "Όλα" else None

        # Apply filters
        filtered_tasks = database.filter_tasks(
            status=status,
            unit_id=self.current_unit_filter,
            task_type_id=task_type_id,
            search_text=search_text
        )

        if not filtered_tasks:
            ctk.CTkLabel(
                self.history_tasks_frame,
                text="Δεν βρέθηκαν εργασίες με τα επιλεγμένα κριτήρια",
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=50)
            return

        # Count label
        count_label = ctk.CTkLabel(
            self.history_tasks_frame,
            text=f"📊 Βρέθηκαν {len(filtered_tasks)} εργασίες",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        )
        count_label.pack(anchor="w", padx=10, pady=10)

        # Display tasks
        for task in filtered_tasks:
            card = ui_components.TaskCard(
                self.history_tasks_frame,
                task,
                on_click=self.show_task_detail
            )
            card.pack(fill="x", pady=3, padx=5)


    def show_task_edit(self, task):
        """Εμφάνιση φόρμας επεξεργασίας εργασίας"""
        self.clear_main_frame()

        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=20, padx=40)

        # Get chain info για τον τίτλο μόνο
        full_chain = self._get_full_chain_for_preview(task['id'])
        current_position = next((i for i, t in enumerate(full_chain, 1) if t['id'] == task['id']), 1)
        chain_length = len(full_chain)
        has_chain = chain_length > 1

        # Title με chain indicator
        title_text = f"✏️ Επεξεργασία Εργασίας #{task['id']}"
        if has_chain:
            title_text += f"  🔗 ({current_position}/{chain_length})"

        title = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        relations_btn = ctk.CTkButton(
            btn_frame,
            text="🔗 Συνδέσεις",
            command=lambda: self.show_task_relationships(task),
            width=140,
            height=35,
            **theme_config.get_button_style("special")
        )
        relations_btn.pack(side="left", padx=5)

        back_btn = ctk.CTkButton(
            btn_frame,
            text="↩️ Πίσω",
            command=self.show_history,
            width=100,
            height=35,
            **theme_config.get_button_style("secondary")
        )
        back_btn.pack(side="left", padx=5)

        # ΧΩΡΙΣ chain preview εδώ - θα το προσθέσει το TaskForm!

        # Form
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=10, padx=100, fill="both", expand=True)

        ui_components.TaskForm(form_frame, self.on_task_saved, task_data=task)

    def show_task_detail(self, task):
        """Εμφάνιση λεπτομερειών εργασίας με επιλογές"""
        self.clear_main_frame()

        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=20, padx=40)

        # ═══════════════════════════════════════════════════════
        # FIX:   Υπολογισμός position με ΟΛΟΚΛΗΡΗ την αλυσίδα
        # ═══════════════════════════════════════════════════════

        # Get full chain για σωστό position
        full_chain = self._get_full_chain_for_preview(task['id'])
        current_position = next((i for i, t in enumerate(full_chain, 1) if t['id'] == task['id']), 1)
        chain_length = len(full_chain)
        has_relations = chain_length > 1

        # Title με unit name και relationship indicator
        unit_name = task.get('unit_name', 'Άγνωστη Μονάδα')
        title_text = f"📋 Λεπτομέρειες Εργασίας #{task['id']} - {unit_name}"
        if has_relations:
            title_text += f"  🔗 ({current_position}/{chain_length})"

        title = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Επεξεργασία",
            command=lambda: self.show_task_edit(task),
            width=140,
            height=35,
            **theme_config.get_button_style("primary")
        )
        edit_btn.pack(side="left", padx=5)

        relations_btn = ctk.CTkButton(
            btn_frame,
            text="🔗 Συνδέσεις",
            command=lambda: self.show_task_relationships(task),
            width=140,
            height=35,
            **theme_config.get_button_style("special")
        )
        relations_btn.pack(side="left", padx=5)

        back_btn = ctk.CTkButton(
            btn_frame,
            text="↩️ Πίσω",
            command=self.show_history,
            width=100,
            height=35,
            **theme_config.get_button_style("secondary")
        )
        back_btn.pack(side="left", padx=5)

        # Details frame
        details_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"],
            border_width=1
        )
        details_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Details content (scrollable)
        scrollable = ctk.CTkScrollableFrame(details_frame)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)

        # Relationship indicator at top (if exists) - FIX: Σωστό position
        if has_relations:
            chain_info = f"🔗 Συνδεδεμένη εργασία:   Θέση {current_position} από {chain_length} στην αλυσίδα"

            chain_frame = ctk.CTkFrame(
                scrollable,
                fg_color=self.theme["bg_secondary"],
                corner_radius=8
            )
            chain_frame.pack(fill="x", pady=(0, 15), padx=10)

            ctk.CTkLabel(
                chain_frame,
                text=chain_info,
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(padx=15, pady=10)

        # Task details
        details = [
            ("🔧 Τύπος Εργασίας:", task['task_type_name']),
        ]

        if task.get('task_item_name'):
            details.append(("📌 Είδος Εργασίας:", task['task_item_name']))

        details.extend([
            ("📍 Μονάδα:", f"{task['unit_name']} ({task['group_name']})"),
            ("📝 Περιγραφή:", task['description']),
            ("📊 Κατάσταση:", "✅ Ολοκληρωμένη" if task['status'] == 'completed' else "⏳ Εκκρεμής"),
            ("⚠️ Προτεραιότητα:", task.get('priority', 'medium').upper()),
            ("📅 Ημερομηνία Δημιουργίας:", task['created_date']),
            ("✔️ Ημερομηνία Ολοκλήρωσης:", task.get('completed_date', 'N/A')),
            ("👤 Τεχνικός:", task.get('technician_name', 'N/A')),
            ("📝 Σημειώσεις:", task.get('notes', 'Καμία')),
        ])

        for label, value in details:
            row_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            row_frame.pack(fill="x", pady=8, padx=10)

            label_widget = ctk.CTkLabel(
                row_frame,
                text=label,
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["text_primary"],
                anchor="w",
                width=250
            )
            label_widget.pack(side="left")

            value_widget = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"],
                anchor="w",
                wraplength=500
            )
            value_widget.pack(side="left", fill="x", expand=True)

        # ═══════════════════════════════════════════════════════
        # COMPACT CHAIN TIMELINE
        # ═══════════════════════════════════════════════════════

        if has_relations:
            separator = ctk.CTkFrame(scrollable, height=2, fg_color=self.theme["card_border"])
            separator.pack(fill="x", pady=20, padx=10)

            # Header
            chain_header_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
            chain_header_frame.pack(fill="x", pady=(10, 5), padx=10)

            ctk.CTkLabel(
                chain_header_frame,
                text="🔗 Αλυσίδα Εργασιών",
                font=theme_config.get_font("heading", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(side="left")

            ctk.CTkButton(
                chain_header_frame,
                text="📋 Πλήρης Προβολή",
                command=lambda: self.show_task_relationships(task),
                width=150,
                height=28,
                **theme_config.get_button_style("special")
            ).pack(side="right")

            # Compact Chain Timeline
            self.create_compact_chain_preview(scrollable, task)

    def create_compact_chain_preview(self, parent, task):
        """Compact preview της αλυσίδας - συμπτυγμένη εμφάνιση"""

        # Get full chain
        full_chain = self._get_full_chain_for_preview(task['id'])

        # Find current position
        current_position = next((i for i, t in enumerate(full_chain, 1) if t['id'] == task['id']), 1)
        total_in_chain = len(full_chain)

        # Info banner
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["bg_secondary"],
            corner_radius=8
        )
        info_frame.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(
            info_frame,
            text=f"📊 {total_in_chain} εργασίες  •  Θέση {current_position}/{total_in_chain}",
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(padx=15, pady=8)

        # Compact timeline
        timeline_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_color=self.theme["card_border"],
            border_width=1
        )
        timeline_frame.pack(fill="x", padx=20, pady=5)

        # Display tasks
        for idx, chain_task in enumerate(full_chain, 1):
            is_current = (chain_task['id'] == task['id'])

            # Task row container
            task_container = ctk.CTkFrame(
                timeline_frame,
                fg_color=self.theme["bg_secondary"] if is_current else "transparent",
                corner_radius=6
            )
            task_container.pack(fill="x", padx=8, pady=2)

            # Content frame
            content_frame = ctk.CTkFrame(task_container, fg_color="transparent")
            content_frame.pack(fill="x", padx=8, pady=6)

            # Left:  Position + Icon
            left_section = ctk.CTkFrame(content_frame, fg_color="transparent")
            left_section.pack(side="left")

            # Position
            pos_color = self.theme["accent_orange"] if is_current else self.theme["text_disabled"]
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

            # Middle: Task info (compact, single line)
            info_section = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_section.pack(side="left", fill="x", expand=True, padx=8)

            # Build compact one-liner
            task_info = f"📅 {chain_task['created_date']}  •  {chain_task['task_type_name']}"
            if chain_task.get('task_item_name'):
                task_info += f" → {chain_task['task_item_name']}"

            # Add short description
            if chain_task.get('description'):
                desc = chain_task['description'][:35] + "..." if len(chain_task['description']) > 35 else chain_task[
                    'description']
                task_info += f"  •  {desc}"

            text_color = self.theme["text_primary"] if is_current else self.theme["text_secondary"]
            font_style = "bold" if is_current else "normal"

            ctk.CTkLabel(
                info_section,
                text=task_info,
                font=theme_config.get_font("small", font_style),
                text_color=text_color,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            # Right: Current indicator
            if is_current:
                ctk.CTkLabel(
                    content_frame,
                    text="◄ ΤΡΕΧΟΥΣΑ",
                    font=theme_config.get_font("tiny", "bold"),
                    text_color=self.theme["accent_orange"],
                    width=90
                ).pack(side="right", padx=5)

            # Arrow (except last)
            if idx < total_in_chain:
                arrow_label = ctk.CTkLabel(
                    timeline_frame,
                    text="        ↓",
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_disabled"]
                )
                arrow_label.pack(anchor="w", padx=20, pady=0)

    def _get_full_chain_for_preview(self, task_id):
        """Helper για να πάρει ολόκληρη την αλυσίδα"""
        chain = []
        visited_parents = set()
        visited_children = set()

        # Get task data
        tasks = database.get_all_tasks()
        task_dict = {t['id']: t for t in tasks}

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

    def show_task_relationships(self, task):
        """Εμφάνιση διαχείρισης συνδέσεων εργασίας"""
        self.clear_main_frame()

        ui_components.TaskRelationshipsView(self.main_frame, task, self.on_task_saved)

    def show_units_management(self):
        """Διαχείριση μονάδων & ομάδων - Phase 2.3"""
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="🏢 Διαχείριση Μονάδων & Ομάδων",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)

        ui_components.UnitsManagement(self.main_frame, lambda: None)

    def show_task_management(self):
        """Διαχείριση Εργασιών - Τύποι & Είδη - Phase 2.3"""
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="📋 Διαχείριση Τύπων & Ειδών Εργασιών",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)

        ui_components.TaskManagement(self.main_frame)

    def show_shifts(self):
        """Πρόγραμμα βαρδιών"""
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="📅 Πρόγραμμα Βαρδιών",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)

        label = ctk.CTkLabel(
            self.main_frame,
            text="Εδώ θα εμφανίζεται το μηνιαίο πρόγραμμα βαρδιών\n(Υλοποιείται στην επόμενη φάση)",
            font=theme_config.get_font("body"),
            text_color=self.theme["text_secondary"]
        )
        label.pack(pady=50)

    def show_export(self):
        """Εξαγωγή δεδομένων"""
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="📤 Εξαγωγή Δεδομένων",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)

        label = ctk.CTkLabel(
            self.main_frame,
            text="Εδώ θα μπορείτε να εξάγετε αναφορές σε PDF/Excel\n(Υλοποιείται στην επόμενη φάση)",
            font=theme_config.get_font("body"),
            text_color=self.theme["text_secondary"]
        )
        label.pack(pady=50)

    def show_recycle_bin(self):
        """Κάδος ανακύκλωσης"""
        self.clear_main_frame()

        ui_components.RecycleBinView(self.main_frame, self.on_task_saved)

    def show_settings(self):
        """Settings page - Theme & Font Size"""
        self.clear_main_frame()

        # Title
        title_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=self.theme["bg_secondary"],
            border_color=self.theme["accent_blue"],
            border_width=2,
            height=60
        )
        title_frame.pack(fill="x", padx=40, pady=(20, 10))
        title_frame.pack_propagate(False)

        title = ctk.CTkLabel(
            title_frame,
            text="⚙️ Ρυθμίσεις Εφαρμογής",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["accent_blue"]
        )
        title.pack(expand=True)

        # Settings container
        settings_container = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent"
        )
        settings_container.pack(fill="both", expand=True, padx=40, pady=10)

        # ═══════════════════════════════════════════════
        # THEME SECTION
        # ═══════════════════════════════════════════════

        theme_frame = ctk.CTkFrame(
            settings_container,
            corner_radius=15,
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"],
            border_width=1
        )
        theme_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            theme_frame,
            text="🎨 Θέμα Εμφάνισης",
            font=theme_config.get_font("heading", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            theme_frame,
            text="Επιλέξτε το θέμα που προτιμάτε.  Η αλλαγή θα εφαρμοστεί μετά από επανεκκίνηση.",
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Theme buttons
        theme_buttons_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        current_theme = theme_config.get_current_theme_name()

        dark_btn = ctk.CTkButton(
            theme_buttons_frame,
            text="🌙 Σκούρο Θέμα" + (" ✓" if current_theme == "dark" else ""),
            command=lambda: self.change_theme("dark"),
            width=200,
            height=50,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("primary" if current_theme == "dark" else "secondary")
        )
        dark_btn.pack(side="left", padx=(0, 10))

        light_btn = ctk.CTkButton(
            theme_buttons_frame,
            text="☀️ Ανοιχτό Θέμα" + (" ✓" if current_theme == "light" else ""),
            command=lambda: self.change_theme("light"),
            width=200,
            height=50,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("primary" if current_theme == "light" else "secondary")
        )
        light_btn.pack(side="left")

        # ═══════════════════════════════════════════════
        # FONT SIZE SECTION
        # ═══════════════════════════════════════════════

        font_frame = ctk.CTkFrame(
            settings_container,
            corner_radius=15,
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"],
            border_width=1
        )
        font_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            font_frame,
            text="🔤 Μέγεθος Γραμματοσειράς",
            font=theme_config.get_font("heading", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            font_frame,
            text="Προσαρμόστε το μέγεθος των γραμμάτων στις προτιμήσεις σας (80% - 150%).",
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Slider container
        slider_container = ctk.CTkFrame(font_frame, fg_color="transparent")
        slider_container.pack(fill="x", padx=20, pady=(0, 20))

        current_scale = theme_config.get_font_scale()

        # Scale label
        scale_label = ctk.CTkLabel(
            slider_container,
            text=f"Τρέχον μέγεθος: {int(current_scale * 100)}%",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        )
        scale_label.pack(anchor="w", pady=(0, 10))

        # Preview text
        self.preview_label = ctk.CTkLabel(
            slider_container,
            text="Αυτό είναι ένα δείγμα κειμένου",
            font=ctk.CTkFont(family="Segoe UI", size=int(13 * current_scale)),
            text_color=self.theme["text_primary"]
        )
        self.preview_label.pack(anchor="w", pady=(0, 15))

        def on_scale_change(value):
            scale_label.configure(text=f"Νέο μέγεθος: {int(value * 100)}%")
            # Update preview
            self.preview_label.configure(
                font=ctk.CTkFont(family="Segoe UI", size=int(13 * value))
            )

        slider = ctk.CTkSlider(
            slider_container,
            from_=0.8,
            to=1.5,
            number_of_steps=14,
            command=on_scale_change,
            width=500
        )
        slider.set(current_scale)
        slider.pack(fill="x", pady=(0, 10))

        # Scale indicators
        indicators_frame = ctk.CTkFrame(slider_container, fg_color="transparent")
        indicators_frame.pack(fill="x")

        ctk.CTkLabel(
            indicators_frame,
            text="80%",
            font=theme_config.get_font("tiny"),
            text_color=self.theme["text_disabled"]
        ).pack(side="left")

        ctk.CTkLabel(
            indicators_frame,
            text="100%",
            font=theme_config.get_font("tiny"),
            text_color=self.theme["text_disabled"]
        ).pack(side="left", expand=True)

        ctk.CTkLabel(
            indicators_frame,
            text="150%",
            font=theme_config.get_font("tiny"),
            text_color=self.theme["text_disabled"]
        ).pack(side="right")

        # Apply font button
        apply_font_btn = ctk.CTkButton(
            font_frame,
            text="✔️ Εφαρμογή Μεγέθους",
            command=lambda: self.apply_font_scale(slider.get()),
            width=200,
            height=45,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("success")
        )
        apply_font_btn.pack(pady=(0, 20))

        # ═══════════════════════════════════════════════
        # RESTART INFO
        # ═══════════════════════════════════════════════

        info_frame = ctk.CTkFrame(
            settings_container,
            corner_radius=10,
            fg_color=self.theme["bg_secondary"],
            border_color=self.theme["accent_orange"],
            border_width=2
        )
        info_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Σημαντική Σημείωση",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_orange"]
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            info_frame,
            text="Οι αλλαγές στο θέμα και στο μέγεθος γραμματοσειράς απαιτούν επανεκκίνηση "
                 "της εφαρμογής για να εφαρμοστούν πλήρως.",
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            wraplength=650,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def change_theme(self, theme_name):
        """Αλλαγή θέματος"""
        if theme_config.set_theme(theme_name):
            from tkinter import messagebox

            result = messagebox.askyesno(
                "Επανεκκίνηση Απαιτείται",
                f"Το θέμα άλλαξε σε '{theme_name}'.\n\n"
                "Η εφαρμογή πρέπει να επανεκκινήσει για να εφαρμοστούν οι αλλαγές.\n\n"
                "Επανεκκίνηση τώρα;",
                icon='question'
            )

            if result:
                self.restart_app()
            else:
                messagebox.showinfo(
                    "Πληροφορία",
                    "Οι αλλαγές θα εφαρμοστούν στην επόμενη εκκίνηση."
                )

    def apply_font_scale(self, scale):
        """Εφαρμογή font scale"""
        if theme_config.set_font_scale(scale):
            from tkinter import messagebox

            result = messagebox.askyesno(
                "Επανεκκίνηση Απαιτείται",
                f"Το μέγεθος γραμματοσειράς άλλαξε σε {int(scale * 100)}%.\n\n"
                "Η εφαρμογή πρέπει να επανεκκινήσει για να εφαρμοστούν οι αλλαγές.\n\n"
                "Επανεκκίνηση τώρα;",
                icon='question'
            )

            if result:
                self.restart_app()
            else:
                messagebox.showinfo(
                    "Πληροφορία",
                    "Οι αλλαγές θα εφαρμοστούν στην επόμενη εκκίνηση."
                )

    def restart_app(self):
        """Επανεκκίνηση εφαρμογής"""
        import sys
        import os

        python = sys.executable
        os.execl(python, python, *sys.argv)

    def load_initial_data(self):
        """Φόρτωση αρχικών δεδομένων δοκιμών"""
        database.load_sample_data()
        
        # Maximize window μετά από rendering (100ms delay)
        self.after(100, lambda: self.state('zoomed'))


if __name__ == "__main__":
    app = HVACRApp()
    app.mainloop()