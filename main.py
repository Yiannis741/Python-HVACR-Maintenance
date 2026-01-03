"""
HVACR Maintenance System - Phase 2
Σύστημα Διαχείρισης Συντηρήσεων HVACR για Νοσοκομείο
"""

import customtkinter as ctk
from datetime import datetime
import database
import ui_components

# Ρυθμίσεις CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class HVACRApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Ρυθμίσεις παραθύρου
        self.title("HVACR Maintenance System - Σύστημα Συντήρησης v2.0")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
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
        self.grid_rowconfigure(1, weight=1)
        
        # ----- ΠΑΝΩ ROW (Ομάδες Μονάδων) -----
        self.top_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        # Dynamic grid configuration will be set in create_top_bar()
        
        self.create_top_bar()
        
        # ----- ΑΡΙΣΤΕΡΗ SIDEBAR -----
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#2b2b2b")
        self.sidebar.grid(row=1, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        self.create_sidebar()
        
        # ----- ΚΕΝΤΡΙΚΗ ΠΕΡΙΟΧΗ -----
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Αρχικό περιεχόμενο
        self.show_dashboard()
        
    def create_top_bar(self):
        """Δημιουργία της πάνω μπάρας με τις ομάδες μονάδων"""
        
        # Label
        label = ctk.CTkLabel(
            self.top_frame, 
            text="ΟΜΑΔΕΣ ΜΟΝΑΔΩΝ:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=20, pady=25, sticky="w")
        
        # Παίρνουμε τις ομάδες από τη database
        groups = database.get_all_groups()
        
        # Dynamic grid column configuration
        num_groups = len(groups)
        for i in range(num_groups):
            self.top_frame.grid_columnconfigure(i + 1, weight=1)
        
        # Dropdown για κάθε ομάδα
        self.group_dropdowns = {}
        
        for idx, group in enumerate(groups):  # Εμφάνιση ΟΛΩΝ των ομάδων
            frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
            frame.grid(row=0, column=idx+1, padx=10, pady=15)
            
            group_label = ctk.CTkLabel(
                frame, 
                text=group['name'], 
                font=ctk.CTkFont(size=11, weight="bold")
            )
            group_label.pack(anchor="w")
            
            # Παίρνουμε τις μονάδες της ομάδας
            units = database.get_units_by_group(group['id'])
            unit_names = [unit['name'] for unit in units] if units else ["Καμία μονάδα"]
            
            dropdown = ctk.CTkComboBox(
                frame,
                values=unit_names,
                width=180,
                state="readonly"
            )
            dropdown.pack()
            dropdown.set(unit_names[0] if unit_names else "Καμία μονάδα")
            
            self.group_dropdowns[group['id']] = dropdown
            
    def create_sidebar(self):
        """Δημιουργία της αριστερής sidebar με κουμπιά"""
        
        # Logo/Τίτλος
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="HVACR\nMAINTENANCE\nv2.0",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1f6aa5"
        )
        title_label.pack(pady=(20, 30))
        
        # Κουμπιά - Phase 2.3 Updated
        buttons_config = [
            ("🏠 Αρχική", self.show_dashboard, "#1f6aa5"),
            ("➕ Νέα Εργασία", self.show_new_task, "#2fa572"),
            ("📋 Συνολικό Ιστορικό", self.show_history, "#1f6aa5"),
            ("✏️ Επεξεργασία Εγγραφής", self.show_edit, "#1f6aa5"),
            ("🏢 Διαχείριση Μονάδων", self.show_units_management, "#1f6aa5"),
            ("📋 Διαχείριση Εργασιών", self.show_task_management, "#1f6aa5"),
            ("📅 Πρόγραμμα Βαρδιών", self.show_shifts, "#1f6aa5"),
            ("📤 Εξαγωγή", self.show_export, "#1f6aa5"),
            ("🗑️ Κάδος Ανακύκλωσης", self.show_recycle_bin, "#c94242"),
        ]
        
        self.sidebar_buttons = {}
        
        for btn_text, command, color in buttons_config: 
            btn = ctk.CTkButton(
                self.sidebar,
                text=btn_text,
                command=command,
                width=200,
                height=45,
                corner_radius=10,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self.adjust_color(color, -20)
            )
            btn.pack(pady=8, padx=10)
            self.sidebar_buttons[btn_text] = btn
            
    def adjust_color(self, hex_color, adjustment):
        """Προσαρμογή χρώματος για hover effect"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, min(255, r + adjustment))
        g = max(0, min(255, g + adjustment))
        b = max(0, min(255, b + adjustment))
        return f'#{r:02x}{g: 02x}{b:02x}'
        
    def clear_main_frame(self):
        """Καθαρισμός της κεντρικής περιοχής"""
        for widget in self.main_frame. winfo_children():
            widget.destroy()
            
    # ----- VIEWS -----
    
    def show_dashboard(self):
        """Εμφάνιση της αρχικής οθόνης"""
        self.clear_main_frame()
        
        # Τίτλος
        title = ctk.CTkLabel(
            self.main_frame,
            text="🏥 Καλώς ήρθατε στο Σύστημα HVACR Maintenance",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(40, 20))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text=f"Σήμερα:  {datetime.now().strftime('%d/%m/%Y')} | Phase 2 - Ενημερωμένη Έκδοση",
            font=ctk.CTkFont(size=16)
        )
        subtitle.pack(pady=10)
        
        # Stats Frame
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(pady=40, padx=40, fill="x")
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
            font=ctk.CTkFont(size=20, weight="bold")
        )
        recent_label.pack(pady=(40, 20))
        
        self.show_recent_tasks()
        
    def create_stat_card(self, parent, title, value, column):
        """Δημιουργία καρτέλας στατιστικού"""
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid(row=0, column=column, padx=15, pady=20, sticky="ew")
        
        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#1f6aa5"
        )
        value_label.pack(pady=(20, 5))
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14)
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
        scrollable. pack(fill="both", expand=True, padx=40, pady=10)
        
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
            font=ctk. CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Form
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=20, padx=100, fill="both", expand=True)
        
        ui_components.TaskForm(form_frame, self.on_task_saved)
        
    def on_task_saved(self):
        """Callback όταν αποθηκευτεί μια εργασία"""
        self.refresh_top_bar()
        self.show_dashboard()
        
    def show_history(self):
        """Εμφάνιση ιστορικού εργασιών με φίλτρα"""
        self.clear_main_frame()
        
        title = ctk. CTkLabel(
            self. main_frame,
            text="📋 Συνολικό Ιστορικό Εργασιών",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # History view με φίλτρα
        ui_components.TaskHistoryView(self.main_frame, on_task_select=self.show_task_detail)
        
    def show_edit(self):
        """Επεξεργασία εγγραφής - Εμφάνιση λίστας εργασιών"""
        self.clear_main_frame()
        
        title = ctk. CTkLabel(
            self. main_frame,
            text="✏️ Επεξεργασία Εγγραφής - Επιλέξτε Εργασία",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Task list για επιλογή
        ui_components.TaskHistoryView(self.main_frame, on_task_select=self.show_task_edit)
    
    def show_task_edit(self, task):
        """Εμφάνιση φόρμας επεξεργασίας εργασίας"""
        self. clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text=f"✏️ Επεξεργασία Εργασίας #{task['id']}",
            font=ctk.CTkFont(size=24, weight="bold")
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
        
        title = ctk.CTkLabel(
            header_frame,
            text=f"📋 Λεπτομέρειες Εργασίας #{task['id']}",
            font=ctk.CTkFont(size=24, weight="bold")
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
            fg_color="#1f6aa5"
        )
        edit_btn.pack(side="left", padx=5)
        
        relations_btn = ctk.CTkButton(
            btn_frame,
            text="🔗 Συνδέσεις",
            command=lambda: self.show_task_relationships(task),
            width=140,
            fg_color="#9c27b0"
        )
        relations_btn.pack(side="left", padx=5)
        
        back_btn = ctk.CTkButton(
            btn_frame,
            text="↩️ Πίσω",
            command=self.show_dashboard,
            width=100,
            fg_color="#666"
        )
        back_btn.pack(side="left", padx=5)
        
        # Details frame
        details_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        details_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Details content
        scrollable = ctk.CTkScrollableFrame(details_frame)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Build details list - Phase 2.3 Updated
        details = [
            ("🔧 Τύπος Εργασίας:", task['task_type_name']),
        ]
        
        # Add task item if exists
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
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                width=250
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=13),
                anchor="w",
                wraplength=500
            )
            value_widget.pack(side="left", fill="x", expand=True)
        
        # Show related tasks if any
        relations = database.get_related_tasks(task['id'])
        if relations['parents'] or relations['children']:
            separator = ctk.CTkFrame(scrollable, height=2, fg_color="#ccc")
            separator.pack(fill="x", pady=20, padx=10)
            
            relations_label = ctk.CTkLabel(
                scrollable,
                text="🔗 Συνδεδεμένες Εργασίες",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            relations_label.pack(pady=10)
            
            if relations['parents']:
                for parent in relations['parents']:
                    rel_text = f"⬆️ Γονική:  {parent['task_type_name']} - {parent['description'][: 50]}..."
                    ctk.CTkLabel(scrollable, text=rel_text, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=3)
            
            if relations['children']:
                for child in relations['children']:
                    rel_text = f"⬇️ Παιδική: {child['task_type_name']} - {child['description'][:50]}..."
                    ctk.CTkLabel(scrollable, text=rel_text, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=3)
    
    def show_task_relationships(self, task):
        """Εμφάνιση διαχείρισης συνδέσεων εργασίας"""
        self.clear_main_frame()
        
        ui_components.TaskRelationshipsView(self.main_frame, task, self.on_task_saved)
        
    def show_units_management(self):
        """Διαχείριση μονάδων - Phase 2.3 Updated"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="🏢 Διαχείριση Μονάδων",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        ui_components.UnitsManagement(self.main_frame, self.refresh_top_bar)
    
    def show_task_management(self):
        """Διαχείριση Εργασιών - Τύποι & Είδη - Phase 2.3"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📋 Διαχείριση Τύπων & Ειδών Εργασιών",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        ui_components.TaskManagement(self.main_frame)
        
    def show_shifts(self):
        """Πρόγραμμα βαρδιών"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📅 Πρόγραμμα Βαρδιών",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        label = ctk.CTkLabel(
            self.main_frame,
            text="Εδώ θα εμφανίζεται το μηνιαίο πρόγραμμα βαρδιών\n(Υλοποιείται στην επόμενη φάση)",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=50)
        
    def show_export(self):
        """Εξαγωγή δεδομένων"""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📤 Εξαγωγή Δεδομένων",
            font=ctk. CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        label = ctk.CTkLabel(
            self.main_frame,
            text="Εδώ θα μπορείτε να εξάγετε αναφορές σε PDF/Excel\n(Υλοποιείται στην επόμενη φάση)",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=50)
        
    def show_recycle_bin(self):
        """Κάδος ανακύκλωσης"""
        self.clear_main_frame()
        
        ui_components.RecycleBinView(self.main_frame, self.on_task_saved)
        
    def refresh_top_bar(self):
        """Ανανέωση της πάνω μπάρας"""
        # Καθαρισμός
        for widget in self.top_frame.winfo_children():
            widget.destroy()
        # Επαναδημιουργία
        self. create_top_bar()
        
    def load_initial_data(self):
        """Φόρτωση αρχικών δεδομένων δοκιμών"""
        database.load_sample_data()


if __name__ == "__main__": 
    app = HVACRApp()
    app.mainloop()
