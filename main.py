"""
HVACR Maintenance System - Prototype v1.0
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
        self.title("HVACR Maintenance System - Σύστημα Συντήρησης")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        database.init_database()
        self.create_layout()
        self.load_initial_data()
        
    def create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.top_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.top_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.create_top_bar()
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#2b2b2b")
        self.sidebar.grid(row=1, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        self.create_sidebar()
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.show_dashboard()
        
    def create_top_bar(self):
        label = ctk.CTkLabel(self.top_frame, text="ΟΜΑΔΕΣ ΜΟΝΑΔΩΝ:", font=ctk.CTkFont(size=14, weight="bold"))
        label.grid(row=0, column=0, padx=20, pady=25, sticky="w")
        groups = database.get_all_groups()
        self.group_dropdowns = {}
        for idx, group in enumerate(groups[:4]):
            frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
            frame.grid(row=0, column=idx+1, padx=10, pady=15)
            group_label = ctk.CTkLabel(frame, text=group['name'], font=ctk.CTkFont(size=11, weight="bold"))
            group_label.pack(anchor="w")
            units = database.get_units_by_group(group['id'])
            unit_names = [unit['name'] for unit in units] if units else ["Καμία μονάδα"]
            dropdown = ctk.CTkComboBox(frame, values=unit_names, width=180, state="readonly")
            dropdown.pack()
            dropdown.set(unit_names[0] if unit_names else "Καμία μονάδα")
            self.group_dropdowns[group['id']] = dropdown
            
    def create_sidebar(self):
        title_label = ctk.CTkLabel(self.sidebar, text="HVACR\nMAINTENANCE", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1f6aa5")
        title_label.pack(pady=(30, 40))
        buttons_config = [
            ("🏠 Αρχική", self.show_dashboard, "#1f6aa5"),
            ("➕ Νέα Εργασία", self.show_new_task, "#2fa572"),
            ("📋 Συνολικό Ιστορικό", self.show_history, "#1f6aa5"),
            ("✏️ Επεξεργασία Εγγραφής", self.show_edit, "#1f6aa5"),
            ("⚙️ Διαχείριση Μονάδων", self.show_units_management, "#1f6aa5"),
            ("📅 Πρόγραμμα Βαρδιών", self.show_shifts, "#1f6aa5"),
            ("📤 Εξαγωγή", self.show_export, "#1f6aa5"),
            ("🗑️ Κάδος Ανακύκλωσης", self.show_recycle_bin, "#c94242"),
        ]
        self.sidebar_buttons = {}
        for btn_text, command, color in buttons_config:
            btn = ctk.CTkButton(self.sidebar, text=btn_text, command=command, width=200, height=45, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"), fg_color=color, hover_color=self.adjust_color(color, -20))
            btn.pack(pady=8, padx=10)
            self.sidebar_buttons[btn_text] = btn
            
    def adjust_color(self, hex_color, adjustment):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r, g, b = max(0, min(255, r + adjustment)), max(0, min(255, g + adjustment)), max(0, min(255, b + adjustment))
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    def show_dashboard(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="🏥 Καλώς ήρθατε στο Σύστημα HVACR Maintenance", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(40, 20))
        subtitle = ctk.CTkLabel(self.main_frame, text=f"Σήμερα: {datetime.now().strftime('%d/%m/%Y')}", font=ctk.CTkFont(size=16))
        subtitle.pack(pady=10)
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(pady=40, padx=40, fill="x")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        stats = database.get_dashboard_stats()
        self.create_stat_card(stats_frame, "Σύνολο Μονάδων", stats['total_units'], 0)
        self.create_stat_card(stats_frame, "Εκκρεμείς Εργασίες", stats['pending_tasks'], 1)
        self.create_stat_card(stats_frame, "Εργασίες Σήμερα", stats['today_tasks'], 2)
        recent_label = ctk.CTkLabel(self.main_frame, text="📌 Πρόσφατες Εργασίες", font=ctk.CTkFont(size=20, weight="bold"))
        recent_label.pack(pady=(40, 20))
        self.show_recent_tasks()
        
    def create_stat_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid(row=0, column=column, padx=15, pady=20, sticky="ew")
        value_label = ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=48, weight="bold"), text_color="#1f6aa5")
        value_label.pack(pady=(20, 5))
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        title_label.pack(pady=(5, 20))
        
    def show_recent_tasks(self):
        tasks = database.get_recent_tasks(5)
        if not tasks:
            no_tasks = ctk.CTkLabel(self.main_frame, text="Δεν υπάρχουν πρόσφατες εργασίες", font=ctk.CTkFont(size=14))
            no_tasks.pack(pady=20)
            return
        scrollable = ctk.CTkScrollableFrame(self.main_frame, height=250)
        scrollable.pack(fill="both", expand=True, padx=40, pady=10)
        for task in tasks:
            task_card = ui_components.TaskCard(scrollable, task)
            task_card.pack(fill="x", pady=5, padx=10)
            
    def show_new_task(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="➕ Νέα Εργασία", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=20, padx=100, fill="both", expand=True)
        ui_components.TaskForm(form_frame, self.on_task_saved)
        
    def on_task_saved(self):
        self.show_dashboard()
        
    def show_history(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="📋 Συνολικό Ιστορικό Εργασιών", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        label = ctk.CTkLabel(self.main_frame, text="Εδώ θα εμφανίζεται το πλήρες ιστορικό με φίλτρα\n(Υλοποιείται στην επόμενη φάση)", font=ctk.CTkFont(size=14))
        label.pack(pady=50)
        
    def show_edit(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="✏️ Επεξεργασία Εγγραφής", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        label = ctk.CTkLabel(self.main_frame, text="Επιλέξτε μια εργασία για επεξεργασία\n(Υλοποιείται στην επόμενη φάση)", font=ctk.CTkFont(size=14))
        label.pack(pady=50)
        
    def show_units_management(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="⚙️ Διαχείριση Μονάδων & Εργασιών", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        ui_components.UnitsManagement(self.main_frame, self.refresh_top_bar)
        
    def show_shifts(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="📅 Πρόγραμμα Βαρδιών", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        label = ctk.CTkLabel(self.main_frame, text="Εδώ θα εμφανίζεται το μηνιαίο πρόγραμμα βαρδιών\n(Υλοποιείται στην επόμενη φάση)", font=ctk.CTkFont(size=14))
        label.pack(pady=50)
        
    def show_export(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="📤 Εξαγωγή Δεδομένων", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        label = ctk.CTkLabel(self.main_frame, text="Εδώ θα μπορείτε να εξάγετε αναφορές σε PDF/Excel\n(Υλοποιείται στην επόμενη φάση)", font=ctk.CTkFont(size=14))
        label.pack(pady=50)
        
    def show_recycle_bin(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="🗑️ Κάδος Ανακύκλωσης", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        label = ctk.CTkLabel(self.main_frame, text="Εδώ θα εμφανίζονται οι διαγραμμένες εγγραφές\n(Υλοποιείται στην επόμενη φάση)", font=ctk.CTkFont(size=14))
        label.pack(pady=50)
        
    def refresh_top_bar(self):
        for widget in self.top_frame.winfo_children():
            widget.destroy()
        self.create_top_bar()
        
    def load_initial_data(self):
        database.load_sample_data()


if __name__ == "__main__":
    app = HVACRApp()
    app.mainloop()
