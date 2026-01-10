"""
HVACR Maintenance System - Phase 2
Σύστημα Διαχείρισης Συντηρήσεων HVACR για Νοσοκομείο
"""
import os

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import ui_components
import theme_config
import utils_refactored
import logger_config
import backup_manager
import custom_dialogs


class HVACRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ✨ Initialize logging FIRST
        logger_config.setup_logging()
        self.logger = logger_config.get_logger(__name__)
        try:
            self.logger.info("=" * 70)
            self.logger.info("HVAC Maintenance App Starting...")
            self.logger.info("=" * 70)
            # Φόρτωση theme
            self.theme = theme_config.get_current_theme()

            # ✨ NEW: Debounce timer για search (για FIX 2.1)
            self.search_timer = None
            # ✨ NEW: Tab tracking
            self.current_tab = None


            # Ρυθμίσεις παραθύρου
            self.title("HVACR Maintenance System - Σύστημα Συντήρησης v2.0")

            self.minsize(1200, 700)
            self.configure(fg_color=self.theme["bg_primary"])

            # Αρχικοποίηση database
            self.logger.info("Initializing database...")
            try:
                database.init_database()
                self.logger.info("Database initialized successfully")
            except Exception as e:
                self.logger.error(f"Database initialization failed: {e}", exc_info=True)
                raise

            # ✨ AUTO BACKUP
            self.logger.info("Creating automatic backup...")
            backup_file = backup_manager.create_backup("Auto backup on startup")
            if backup_file:
                self.logger.info(f"✅ Backup created: {backup_file}")
            else:
                self.logger.warning("⚠️  Backup failed (app will continue)")


            # Δημιουργία UI layout
            self.logger.info("Creating UI layout...")
            self.create_layout()
            self.logger.info("UI layout created successfully")

            # Φόρτωση αρχικών δεδομένων
            self.logger.info("Loading initial data...")
            self.load_initial_data()
            self.logger.info("Initial data loaded successfully")

            # Maximize window (μετά το UI setup)
            self.after(10, lambda: self.state('zoomed'))

            # ✨ Log app ready
            self.logger.info("=" * 70)
            self.logger.info("HVAC Maintenance App is READY!")
            self.logger.info("=" * 70)
        except Exception as e:
            self.logger.critical(f"❌ FATAL: App initialization failed: {e}", exc_info=True)

            # Show error to user
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Κρίσιμο Σφάλμα",
                f"Το app δεν μπόρεσε να ξεκινήσει:\n\n{str(e)}\n\nΕλέγξτε το log file για λεπτομέρειες."
            )

            # Exit gracefully
            raise

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
            text=f"Σήμερα: {datetime.now().strftime('%d/%m/%y')} | Phase 2 - Ενημερωμένη Έκδοση",
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
        all_tasks = database.get_recent_tasks(20)  # Φέρνουμε περισσότερα για να φιλτράρουμε
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
        scrollable = ctk.CTkScrollableFrame(self.main_frame, height=600)
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
        """Εμφάνιση ιστορικού εργασιών - Uses TaskHistoryView component"""
        self.clear_main_frame()

        # Use the TaskHistoryView component
        history_view = ui_components.TaskHistoryView(
            self.main_frame,
            on_task_select=self.show_task_detail
        )
        history_view.pack(fill="both", expand=True)

    def filter_by_unit(self, unit_id=None, group_id=None):
        """Filter tasks by unit or group"""
        self.current_unit_filter = unit_id
        self.current_group_filter = group_id
        self.update_filter_visuals()  # ← ΝΕΟ!
        self.load_history_tasks()

    def update_filter_visuals(self):
        """Update visual indicators for active filters"""

        active_color = self.theme["accent_green"]  # Πράσινο
        inactive_color = self.theme["card_border"]  # Default

        # 1. Search Entry
        if hasattr(self, 'history_search_entry'):
            has_text = bool(self.history_search_entry.get().strip())
            self.history_search_entry.configure(
                border_color=active_color if has_text else inactive_color,
                border_width=2 if has_text else 1
            )

        # 2. Status Combo
        if hasattr(self, 'history_status_combo'):
            is_active = self.history_status_combo.get() != "Όλες"
            self.history_status_combo.configure(
                border_color=active_color if is_active else inactive_color,
                border_width=2 if is_active else 1
            )

        # 3. Type Combo
        if hasattr(self, 'history_type_combo'):
            is_active = self.history_type_combo.get() != "Όλα"
            self.history_type_combo.configure(
                border_color=active_color if is_active else inactive_color,
                border_width=2 if is_active else 1
            )

        # 4. Location Combo
        if hasattr(self, 'history_location_combo'):
            is_active = self.history_location_combo.get() != "Όλες"
            self.history_location_combo.configure(
                border_color=active_color if is_active else inactive_color,
                border_width=2 if is_active else 1
            )

        # 5. Unit/Group Dropdowns
        if hasattr(self, 'unit_filter_buttons'):
            for group_id, dropdown in self.unit_filter_buttons.items():
                current = dropdown.get()
                groups = database.get_all_groups()
                group_names = [g['name'] for g in groups]

                is_active = current not in group_names

                dropdown.configure(
                    border_color=active_color if is_active else inactive_color,
                    border_width=2 if is_active else 1
                )

        # 6. "Όλες" Button
        if hasattr(self, 'all_units_btn'):
            all_filters_off = (
                                      not hasattr(self, 'current_unit_filter') or self.current_unit_filter is None
                              ) and (
                                      not hasattr(self, 'current_group_filter') or self.current_group_filter is None
                              )

            if all_filters_off:
                self.all_units_btn.configure(
                    border_color=active_color,
                    border_width=2
                )
            else:
                self.all_units_btn.configure(
                    border_color=theme_config.get_button_style("primary")["border_color"],
                    border_width=theme_config.get_button_style("primary")["border_width"]
                )

    def reset_all_filters(self):
        """Reset ALL filters to default state"""

        # 1. Clear search
        if hasattr(self, 'history_search_entry'):
            self.history_search_entry.delete(0, "end")

        # 2. Reset Status
        if hasattr(self, 'history_status_combo'):
            self.history_status_combo.set("Όλες")

        # 3. Reset Type
        if hasattr(self, 'history_type_combo'):
            self.history_type_combo.set("Όλα")

        # 4. Reset Location
        if hasattr(self, 'history_location_combo'):
            self.history_location_combo.set("Όλες")

        # 5. Reset Unit/Group dropdowns to group name
        if hasattr(self, 'unit_filter_buttons'):
            groups = database.get_all_groups()
            group_map = {g['id']: g['name'] for g in groups}

            for group_id, dropdown in self.unit_filter_buttons.items():
                group_name = group_map.get(group_id, "")
                if group_name:
                    dropdown.set(group_name)

        # 6. Clear internal filters
        self.current_unit_filter = None
        self.current_group_filter = None

        # 7. Update visuals and reload
        self.update_filter_visuals()
        self.load_history_tasks()

    def on_search_keypress(self, event):
        """Debounced search handler - Περιμένει 500ms μετά το τελευταίο keystroke"""

        # Cancel previous timer
        if self.search_timer is not None:
            self.after_cancel(self.search_timer)

        # Show/hide clear button (instant feedback)
        if self.history_search_entry.get().strip():
            self.search_clear_btn.place(in_=self.history_search_entry, relx=0.95, rely=0.5, anchor="center")
        else:
            self.search_clear_btn.place_forget()

        # Start new timer (500ms delay)
        self.search_timer = self.after(500, self.on_search_change)

    def on_search_change(self):
        """Actual search execution (called after 500ms delay)"""
        self.search_timer = None
        self.apply_history_filters()

    def clear_search(self):
        """Clear search entry"""
        self.history_search_entry.delete(0, "end")
        self.search_clear_btn.place_forget()
        self.apply_history_filters()

    def reset_status_filter(self):
        """Reset status filter to default"""
        self.history_status_combo.set("Όλες")
        self.apply_history_filters()

    def reset_type_filter(self):
        """Reset type filter to default"""
        self.history_type_combo.set("Όλα")
        self.apply_history_filters()

    def reset_location_filter(self):
        """Reset location filter to default"""
        self.history_location_combo.set("Όλες")
        self.apply_history_filters()

    def apply_history_filters(self):
        """Apply search filters to history view"""
        self.update_filter_visuals()  # ← ΝΕΟ!
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
        location_filter = self.history_location_combo.get() if hasattr(self, 'history_location_combo') else "Όλες"

        # Apply filters
        filtered_tasks = database.filter_tasks(
            status=status,
            unit_id=self.current_unit_filter,
            task_type_id=task_type_id,
            search_text=search_text
        )

        # Filter by group (client-side) if group selected
        if hasattr(self, 'current_group_filter') and self.current_group_filter:
            filtered_tasks = [t for t in filtered_tasks if t.get('group_id') == self.current_group_filter]



        # Filter by location (client-side since DB doesn't support it yet)
        if location_filter != "Όλες":
            filtered_tasks = [t for t in filtered_tasks if t.get('location') == location_filter]
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
        scrollable = ctk.CTkScrollableFrame(details_frame, height=500)
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
        ])
        
        # Add location if available
        if task.get('location'):
            details.append(("🏢 Τοποθεσία:", task['location']))
        
        details.extend([
            ("📝 Περιγραφή:", task['description']),
            ("📊 Κατάσταση:", "✅ Ολοκληρωμένη" if task['status'] == 'completed' else "⏳ Εκκρεμής"),
            ("⚠️ Προτεραιότητα:", task.get('priority', 'medium').upper()),
            ("📅 Ημερομηνία Δημιουργίας:", utils_refactored.format_date_for_display(task['created_date'])),
            ("✔️ Ημερομηνία Ολοκλήρωσης:",
             utils_refactored.format_date_for_display(task.get('completed_date', ''))
             if task.get('completed_date') else 'N/A'),
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
            task_info = f"📅 {utils_refactored.format_date_for_display(chain_task['created_date'])}  •  {chain_task['task_type_name']}"
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

        settings_container = ctk.CTkScrollableFrame(
            self.main_frame,
            height=600,  # ← ΠΡΟΣΘΕΣΕ αυτό!
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

        # ═══════════════════════════════════════════════════════════════
        # ✨ NEW: Database Backups Section
        # ═══════════════════════════════════════════════════════════════

        backup_section = ctk.CTkFrame(
            settings_container,
            fg_color=self.theme["card_bg"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["card_border"]
        )
        backup_section.pack(fill="x", padx=40, pady=20)

        # Section title
        ctk.CTkLabel(
            backup_section,
            text="🗄️ Αντίγραφα Ασφαλείας (Backups)",
            font=theme_config.get_font("heading", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Info
        info_text = (
            "Το σύστημα δημιουργεί αυτόματα backup κάθε φορά που ανοίγει η εφαρμογή.\n"
            "Κρατούνται τα τελευταία 7 backups."
        )
        ctk.CTkLabel(
            backup_section,
            text=info_text,
            font=theme_config.get_font("body"),
            text_color=self.theme["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 10))

        # Backup stats
        stats = backup_manager.get_backup_stats()
        if stats and stats['count'] > 0:
            stats_text = (
                f"📊 Διαθέσιμα backups: {stats['count']} "
                f"(Συνολικό μέγεθος: {stats['total_size_mb']:.1f} MB)"
            )
            ctk.CTkLabel(
                backup_section,
                text=stats_text,
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(anchor="w", padx=20, pady=(0, 15))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(backup_section, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Create manual backup button
        ctk.CTkButton(
            buttons_frame,
            text="💾 Δημιουργία Backup Τώρα",
            command=self.create_manual_backup,
            **theme_config.get_button_style("primary"),
            width=200,
            height=40
        ).pack(side="left", padx=(0, 10))

        # Restore from backup button
        ctk.CTkButton(
            buttons_frame,
            text="♻️ Επαναφορά από Backup",
            command=self.show_restore_dialog,
            **theme_config.get_button_style("warning"),
            width=200,
            height=40
        ).pack(side="left", padx=(0, 10))

        # Open backups folder button
        ctk.CTkButton(
            buttons_frame,
            text="📁 Άνοιγμα Φακέλου Backups",
            command=self.open_backups_folder,
            **theme_config.get_button_style("secondary"),
            width=200,
            height=40
        ).pack(side="left")

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

    # ═══════════════════════════════════════════════════════════════
    # BACKUP MANAGEMENT METHODS
    # ═══════════════════════════════════════════════════════════════

    def create_manual_backup(self):
        """Δημιουργία manual backup"""

        self.logger.info("User requested manual backup")

        backup_file = backup_manager.create_backup("Manual backup")

        if backup_file:
            custom_dialogs.show_success(
                "Επιτυχία",
                f"Το backup δημιουργήθηκε επιτυχώς!\n\n{os.path.basename(backup_file)}"
            )
            # Refresh settings to update stats
            self.show_settings()
        else:
            custom_dialogs.show_error(
                "Σφάλμα",
                "Το backup απέτυχε! Ελέγξτε το log file."
            )

    def show_restore_dialog(self):
        """Εμφάνιση dialog για επιλογή backup προς επαναφορά"""

        backups = backup_manager.list_backups()

        if not backups:
            custom_dialogs.show_error(
                "Σφάλμα",
                "Δεν υπάρχουν διαθέσιμα backups!"
            )
            return

        # Create dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επαναφορά από Backup")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()

        # Title
        ctk.CTkLabel(
            dialog,
            text="♻️ Επιλέξτε Backup για Επαναφορά",
            font=theme_config.get_font("heading", "bold")
        ).pack(pady=20)

        # Warning
        warning = ctk.CTkLabel(
            dialog,
            text="⚠️  ΠΡΟΣΟΧΗ: Αυτή η ενέργεια θα αντικαταστήσει την τρέχουσα βάση δεδομένων!\n"
                 "Θα δημιουργηθεί backup ασφαλείας πριν την επαναφορά.",
            font=theme_config.get_font("body"),
            text_color=self.theme["warning"],
            justify="center"
        )
        warning.pack(pady=(0, 20))

        # Backups list
        list_frame = ctk.CTkScrollableFrame(dialog, height=250)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        selected_backup = {'value': None}

        for backup in backups:
            backup_frame = ctk.CTkFrame(list_frame, fg_color=self.theme["card_bg"])
            backup_frame.pack(fill="x", pady=5)

            # Backup info
            backup_name = backup_manager.format_backup_name(backup)

            def select_backup(b=backup):
                selected_backup['value'] = b
                dialog.destroy()
                self.confirm_restore(b)

            ctk.CTkButton(
                backup_frame,
                text=backup_name,
                command=select_backup,
                **theme_config.get_button_style("secondary"),
                anchor="w"
            ).pack(fill="x", padx=10, pady=10)

        # Cancel button
        ctk.CTkButton(
            dialog,
            text="❌ Ακύρωση",
            command=dialog.destroy,
            **theme_config.get_button_style("secondary"),
            width=150
        ).pack(pady=(0, 20))

    def confirm_restore(self, backup):
        """Επιβεβαίωση και εκτέλεση restore"""

        backup_name = backup_manager.format_backup_name(backup)

        result = custom_dialogs.ask_yes_no(
            "Τελική Επιβεβαίωση",
            f"Είστε ΣΙΓΟΥΡΟΙ ότι θέλετε να επαναφέρετε από:\n\n"
            f"{backup_name}\n\n"
            f"Η τρέχουσα βάση θα αντικατασταθεί!\n"
            f"(Θα δημιουργηθεί backup ασφαλείας)"
        )

        if result:
            self.logger.warning(f"User confirmed restore from: {backup['filename']}")

            success = backup_manager.restore_backup(backup['path'])

            if success:
                custom_dialogs.show_success(
                    "Επιτυχία",
                    "Η βάση δεδομένων επαναφέρθηκε επιτυχώς!\n\n"
                    "Η εφαρμογή θα κλείσει. Παρακαλώ ανοίξτε την ξανά."
                )

                # Exit app (user needs to restart)
                self.logger.info("App closing after restore - user must restart")
                self.quit()
            else:
                custom_dialogs.show_error(
                    "Σφάλμα",
                    "Η επαναφορά απέτυχε! Ελέγξτε το log file.\n\n"
                    "Η βάση δεδομένων δεν άλλαξε."
                )

    def open_backups_folder(self):
        """Άνοιγμα του φακέλου backups"""

        import subprocess
        import platform

        backup_dir = "backups"

        # Create if not exists
        from pathlib import Path
        Path(backup_dir).mkdir(exist_ok=True)

        try:
            if platform.system() == "Windows":
                os.startfile(backup_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", backup_dir])
            else:  # Linux
                subprocess.run(["xdg-open", backup_dir])

            self.logger.info(f"Opened backups folder: {backup_dir}")

        except Exception as e:
            self.logger.error(f"Failed to open backups folder: {e}")
            custom_dialogs.show_error(
                "Σφάλμα",
                f"Δεν μπόρεσε να ανοίξει ο φάκελος:\n{backup_dir}"
            )


if __name__ == "__main__":
    app = HVACRApp()
    app.mainloop()