"""
HVACR Maintenance System - Phase 2
Σύστημα Διαχείρισης Συντηρήσεων HVACR για Νοσοκομείο
"""

import customtkinter as ctk
from datetime import datetime
import database
import ui_components
import theme_config

# Εφαρμογή theme πριν τη δημιουργία του app
theme_config.apply_theme()


class HVACRApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Φόρτωση theme
        self.theme = theme_config.get_current_theme()
        
        # Ρυθμίσεις παραθύρου
        self.title("HVACR Maintenance System - Σύστημα Συντήρησης v2.0")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        self.configure(fg_color=self.theme["bg_primary"])
        
        # Αρχικοποίηση database
        database.init_database()
        
        # Δημιουργία UI layout
        self.create_layout()
        
        # Φόρτωση αρχικών δεδομένων
        self.load_initial_data()
        
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
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
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
            ("📋 Συνολικό Ιστορικό", self.show_history, "primary"),
            ("✏️ Επεξεργασία Εγγραφής", self.show_edit, "primary"),
            ("🏢 Διαχείριση Μονάδων", self.show_units_management, "primary"),
            ("📋 Διαχείριση Εργασιών", self.show_task_management, "primary"),
            ("📅 Πρόγραμμα Βαρδιών", self.show_shifts, "primary"),
            ("📤 Εξαγωγή", self.show_export, "primary"),
            ("🗑️ Κάδος Ανακύκλωσης", self.show_recycle_bin, "danger"),
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
                corner_radius=10,
                font=theme_config.get_font("body", "bold"),
                fg_color=style["fg_color"],
                hover_color=style["hover_color"]
            )
            btn.pack(pady=8, padx=10)
            self.sidebar_buttons[btn_text] = btn
            
    def adjust_color(self, hex_color, adjustment):
        """Προσαρμογή χρώματος για hover effect"""
        return theme_config.adjust_color(hex_color, adjustment)
        
    def clear_main_frame(self):
        """Καθαρισμός της κεντρικής περιοχής"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
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

        # Stats Frame (με frame για να μην rebuild)
        stats_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_container.pack(pady=40, padx=40, fill="x")

        stats_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        stats_frame.pack(fill="x")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Στατιστικά
        stats = database.get_dashboard_stats()

        self.create_stat_card(stats_frame, "Σύνολο Μονάδων", stats['total_units'], 0)
        self.create_stat_card(stats_frame, "Εκκρεμείς Εργασίες", stats['pending_tasks'], 1)
        self.create_stat_card(stats_frame, "Εργασίες Σήμερα", stats['today_tasks'], 2)

        # Πρόσφατες εργασίες
        recent_label = ctk.CTkLabel(
            self.main_frame,
            text="📌 Πρόσφατες Εργασίες (Κλικ για επεξεργασία)",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        recent_label.pack(pady=(40, 20))

        # Scrollable frame για tasks (ΝΕΟ - με fixed height)
        self.dashboard_tasks_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            height=400,  # Fixed height να μην αλλάζει
            fg_color="transparent"
        )
        self.dashboard_tasks_frame.pack(fill="both", expand=True, padx=40, pady=10)

        self.load_dashboard_tasks()

    def load_dashboard_tasks(self):
        """Φόρτωση tasks για το dashboard - Separated για performance"""

        # Clear existing tasks only
        if hasattr(self, 'dashboard_tasks_frame'):
            for widget in self.dashboard_tasks_frame.winfo_children():
                widget.destroy()

        tasks = database.get_recent_tasks(10)  # Αύξησε από 5 σε 10 (επειδή είναι compact)

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
        """Εμφάνιση ιστορικού εργασιών με φίλτρα"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📋 Συνολικό Ιστορικό Εργασιών",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)
        
        # History view με φίλτρα
        ui_components.TaskHistoryView(self.main_frame, on_task_select=self.show_task_detail)
        
    def show_edit(self):
        """Επεξεργασία εγγραφής - Εμφάνιση λίστας εργασιών"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="✏️ Επεξεργασία Εγγραφής - Επιλέξτε Εργασία",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)
        
        # Task list για επιλογή
        ui_components.TaskHistoryView(self.main_frame, on_task_select=self.show_task_edit)
    
    def show_task_edit(self, task):
        """Εμφάνιση φόρμας επεξεργασίας εργασίας"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text=f"✏️ Επεξεργασία Εργασίας #{task['id']}",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        )
        title.pack(pady=20)
        
        # Edit form
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=20, padx=100, fill="both", expand=True)
        
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

        # Title με ΣΩΣΤΟ relationship indicator
        title_text = f"📋 Λεπτομέρειες Εργασίας #{task['id']}"
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
            command=self.show_dashboard,
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
        visited = set()

        # Get task data
        tasks = database.get_all_tasks()
        task_dict = {t['id']: t for t in tasks}

        def get_parents(tid):
            if tid in visited:
                return
            visited.add(tid)
            rels = database.get_related_tasks(tid)
            for parent in rels['parents']:
                parent_id = parent['id']
                if parent_id not in [c['id'] for c in chain]:
                    chain.insert(0, parent)
                    get_parents(parent_id)  # ← FIX:  Recursive με parent_id

        def get_children(tid):
            if tid in visited:
                return
            visited.add(tid)
            rels = database.get_related_tasks(tid)
            for child in rels['children']:
                child_id = child['id']  # ← FIX: Παίρνουμε το child_id
                if child_id not in [c['id'] for c in chain]:
                    chain.append(child)
                    get_children(child_id)  # ← FIX:  Recursive με child_id (ΟΧΙ parent['id']!)

        # Build chain
        get_parents(task_id)

        # Add current task
        if task_id in task_dict:
            chain.append(task_dict[task_id])

        # Remove task_id from visited so get_children can process it
        visited.discard(task_id)
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
        
    def load_initial_data(self):
        """Φόρτωση αρχικών δεδομένων δοκιμών"""
        database.load_sample_data()


if __name__ == "__main__": 
    app = HVACRApp()
    app.mainloop()
