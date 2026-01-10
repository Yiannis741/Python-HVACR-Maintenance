"""
Task History View Component - FIXED FINAL
==========================================
Multi-select filtering - FIXED location filtering

BUG FIX: location is TEXT field matching location.name, not location_id!
"""

import customtkinter as ctk
import database_refactored as database
import theme_config
from components.task_card import TaskCard

class TaskHistoryView(ctk.CTkFrame):
    """Προβολή ιστορικού με multi-select filters"""
    
    def __init__(self, parent, on_task_select=None):
        super().__init__(parent, fg_color="transparent")
        
        self.on_task_select = on_task_select
        self.theme = theme_config.get_current_theme()
        
        # Filtering state - FIXED: Store location NAMES, not IDs
        self.selected_group_ids = set()
        self.selected_location_names = set()  # ← FIXED: names instead of IDs
        self.selected_unit_ids = set()
        
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        self.load_tasks()
        
    def create_ui(self):
        """Δημιουργία UI"""

        filters_frame = ctk.CTkFrame(
            self,
            height=100,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            border_width=2,
            border_color=self.theme.get("border_color", "#333333")
        )

        filters_frame.pack(fill="x", pady=(0, 10))
        filters_frame.pack_propagate(False)

        # ROW 1: LABEL


        # ROW 2: Search, Status, Task Type
        row2 = ctk.CTkFrame(filters_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(10, 8))

        ctk.CTkLabel(row2, text="Κατάσταση:", font=theme_config.get_font("small", "bold")).pack(side="left",
                                                                                                padx=(20, 5))
        self.status_combo = ctk.CTkComboBox(row2, values=["Όλες", "Εκκρεμείς", "Ολοκληρωμένες"], width=150,
                                            state="readonly", font=theme_config.get_font("input"),
                                            command=lambda e: self.apply_filters())
        self.status_combo.set("Όλες")
        self.status_combo.pack(side="left", padx=5)

        ctk.CTkLabel(row2, text="Είδος:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(20, 5))
        task_types = database.get_all_task_types()
        type_names = ["Όλα"] + [tt['name'] for tt in task_types]
        self.types_dict = {tt['name']: tt['id'] for tt in task_types}
        self.type_combo = ctk.CTkComboBox(row2, values=type_names, width=150, state="readonly",
                                          font=theme_config.get_font("input"), command=lambda e: self.apply_filters())
        self.type_combo.set("Όλα")
        self.type_combo.pack(side="left", padx=5)

        ctk.CTkLabel(row2, text="🔍 Αναζήτηση:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(row2, width=250, placeholder_text="Περιγραφή, σημειώσεις...", font=theme_config.get_font("input"))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        ctk.CTkButton(row2, text="🔍 Αναζήτηση", command=self.apply_filters, width=120,
                      **theme_config.get_button_style("primary")).pack(side="left", padx=5)
        ctk.CTkButton(row2, text="🔄 Καθαρισμός", command=self.clear_filters, width=120,
                      **theme_config.get_button_style("secondary")).pack(side="left", padx=5)
        

        
        # ROW 3: Groups + Locations
        row3 = ctk.CTkFrame(filters_frame, fg_color="transparent")
        row3.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(row3, text="Τοποθεσίες:", font=theme_config.get_font("small", "bold")).pack(side="left",
                                                                                                 padx=(20, 5))
        self.locations_button = ctk.CTkButton(row3, text="Επιλογή τοποθεσιών...", width=180,
                                              command=self.show_locations_selector,
                                              **theme_config.get_button_style("secondary"))
        self.locations_button.pack(side="left", padx=5)
        self.locations_label = ctk.CTkLabel(row3, text="(Όλες)", font=theme_config.get_font("small"),
                                            text_color=self.theme["text_secondary"])
        self.locations_label.pack(side="left", padx=5)

        ctk.CTkLabel(row3, text="Ομάδες:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(0, 5))
        self.groups_button = ctk.CTkButton(row3, text="Επιλογή ομάδων...", width=180, command=self.show_groups_selector, **theme_config.get_button_style("secondary"))
        self.groups_button.pack(side="left", padx=5)
        self.groups_label = ctk.CTkLabel(row3, text="(Όλες)", font=theme_config.get_font("small"), text_color=self.theme["text_secondary"])
        self.groups_label.pack(side="left", padx=5)

        ctk.CTkLabel(row3, text="Μονάδες:", font=theme_config.get_font("small", "bold")).pack(side="left", padx=(0, 5))
        self.units_button = ctk.CTkButton(row3, text="Επιλογή μονάδων...", width=180, command=self.show_units_selector,
                                          **theme_config.get_button_style("secondary"))
        self.units_button.pack(side="left", padx=5)
        self.units_label = ctk.CTkLabel(row3, text="(Όλες)", font=theme_config.get_font("small"),
                                        text_color=self.theme["text_secondary"])
        self.units_label.pack(side="left", padx=5)
        
        # ROW 3: Units
        ##row3.pack(fill="x", padx=15, pady=(0, 8))
        

        
        # ROW 4: Buttons
        ##row4.pack(fill="x", padx=15, pady=(0, 10))
        

        
        # TASKS LIST
        self.tasks_frame = ctk.CTkScrollableFrame(self, fg_color=self.theme["bg_primary"])
        self.tasks_frame.pack(fill="both", expand=True)
    
    # ═══════════════════════════════════════════════════════════════
    # GROUPS SELECTOR
    # ═══════════════════════════════════════════════════════════════
    
    def show_groups_selector(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επιλογή Ομάδων")
        dialog.geometry("500x400")
        dialog.grab_set()
        
        groups = database.get_all_groups()
        if not groups:
            ctk.CTkLabel(dialog, text="Δεν υπάρχουν ομάδες", font=theme_config.get_font("body")).pack(pady=50)
            return
        
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text=f"Επιλέξτε ομάδες ({len(groups)})", font=theme_config.get_font("heading", "bold")).pack(side="left")
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        checkboxes = {}
        
        def select_all():
            for cb in checkboxes.values():
                cb['var'].set(True)
        
        def deselect_all():
            for cb in checkboxes.values():
                cb['var'].set(False)
        
        ctk.CTkButton(btn_frame, text="✓ Όλες", command=select_all, width=70, **theme_config.get_button_style("secondary")).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✗ Καμία", command=deselect_all, width=70, **theme_config.get_button_style("secondary")).pack(side="left", padx=2)
        
        scroll = ctk.CTkScrollableFrame(dialog, height=220)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for group in groups:
            var = ctk.BooleanVar(value=group['id'] in self.selected_group_ids)
            cb = ctk.CTkCheckBox(scroll, text=group['name'], variable=var, font=theme_config.get_font("body"))
            cb.pack(anchor="w", padx=10, pady=3)
            checkboxes[group['id']] = {'var': var}
        
        def save():
            self.selected_group_ids.clear()
            for gid, cb in checkboxes.items():
                if cb['var'].get():
                    self.selected_group_ids.add(gid)
            self.update_groups_label()
            self.selected_unit_ids.clear()
            self.update_units_label()
            self.apply_filters()
            dialog.destroy()
        
        btn_container = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(10, 20))
        ctk.CTkButton(btn_container, text="💾 Εφαρμογή", command=save, width=140, height=40, **theme_config.get_button_style("success")).pack(side="right", padx=5)
        ctk.CTkButton(btn_container, text="❌ Ακύρωση", command=dialog.destroy, width=140, height=40, **theme_config.get_button_style("secondary")).pack(side="right", padx=5)
    
    def update_groups_label(self):
        if not self.selected_group_ids:
            self.groups_label.configure(text="(Όλες)")
        else:
            self.groups_label.configure(text=f"({len(self.selected_group_ids)} επιλεγμένες)")
    
    # ═══════════════════════════════════════════════════════════════
    # LOCATIONS SELECTOR - FIXED: Store names not IDs
    # ═══════════════════════════════════════════════════════════════
    
    def show_locations_selector(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επιλογή Τοποθεσιών")
        dialog.geometry("500x400")
        dialog.grab_set()
        
        locations = database.get_all_locations()
        if not locations:
            ctk.CTkLabel(dialog, text="Δεν υπάρχουν τοποθεσίες", font=theme_config.get_font("body")).pack(pady=50)
            return
        
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text=f"Επιλέξτε τοποθεσίες ({len(locations)})", font=theme_config.get_font("heading", "bold")).pack(side="left")
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        checkboxes = {}
        
        def select_all():
            for cb in checkboxes.values():
                cb['var'].set(True)
        
        def deselect_all():
            for cb in checkboxes.values():
                cb['var'].set(False)
        
        ctk.CTkButton(btn_frame, text="✓ Όλες", command=select_all, width=70, **theme_config.get_button_style("secondary")).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✗ Καμία", command=deselect_all, width=70, **theme_config.get_button_style("secondary")).pack(side="left", padx=2)
        
        scroll = ctk.CTkScrollableFrame(dialog, height=220)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for loc in locations:
            # FIXED: Check if location NAME is in selected set
            var = ctk.BooleanVar(value=loc['name'] in self.selected_location_names)
            cb = ctk.CTkCheckBox(scroll, text=loc['name'], variable=var, font=theme_config.get_font("body"))
            cb.pack(anchor="w", padx=10, pady=3)
            checkboxes[loc['name']] = {'var': var}  # ← Use NAME as key
        
        def save():
            self.selected_location_names.clear()
            for loc_name, cb in checkboxes.items():
                if cb['var'].get():
                    self.selected_location_names.add(loc_name)  # ← Store NAME
            self.update_locations_label()
            self.selected_unit_ids.clear()
            self.update_units_label()
            self.apply_filters()
            dialog.destroy()
        
        btn_container = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(10, 20))
        ctk.CTkButton(btn_container, text="💾 Εφαρμογή", command=save, width=140, height=40, **theme_config.get_button_style("success")).pack(side="right", padx=5)
        ctk.CTkButton(btn_container, text="❌ Ακύρωση", command=dialog.destroy, width=140, height=40, **theme_config.get_button_style("secondary")).pack(side="right", padx=5)
    
    def update_locations_label(self):
        if not self.selected_location_names:
            self.locations_label.configure(text="(Όλες)")
        else:
            self.locations_label.configure(text=f"({len(self.selected_location_names)} επιλεγμένες)")
    
    # ═══════════════════════════════════════════════════════════════
    # UNITS SELECTOR - FIXED: Filter by location NAME
    # ═══════════════════════════════════════════════════════════════
    
    def show_units_selector(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επιλογή Μονάδων")
        dialog.geometry("600x500")
        dialog.grab_set()
        
        all_units = database.get_all_units()
        units = []
        
        for unit in all_units:
            # Group filter
            if self.selected_group_ids:
                unit_in_selected_group = False
                for gid in self.selected_group_ids:
                    group_units = database.get_units_by_group(gid)
                    if any(u['id'] == unit['id'] for u in group_units):
                        unit_in_selected_group = True
                        break
                if not unit_in_selected_group:
                    continue
            
            # Location filter - FIXED: Compare with NAME
            if self.selected_location_names:
                unit_location = unit.get('location', '')
                if unit_location not in self.selected_location_names:
                    continue
            
            units.append(unit)
        
        if not units:
            ctk.CTkLabel(dialog, text="Δεν υπάρχουν διαθέσιμες μονάδες\n(βάσει επιλεγμένων ομάδων/τοποθεσιών)", font=theme_config.get_font("body")).pack(pady=50)
            return
        
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text=f"Επιλέξτε μονάδες ({len(units)} διαθέσιμες)", font=theme_config.get_font("heading", "bold")).pack(side="left")
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        checkboxes = {}
        
        def select_all():
            for cb in checkboxes.values():
                cb['var'].set(True)
        
        def deselect_all():
            for cb in checkboxes.values():
                cb['var'].set(False)
        
        ctk.CTkButton(btn_frame, text="✓ Όλες", command=select_all, width=70, **theme_config.get_button_style("secondary")).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✗ Καμία", command=deselect_all, width=70, **theme_config.get_button_style("secondary")).pack(side="left", padx=2)
        
        scroll = ctk.CTkScrollableFrame(dialog, height=300)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for unit in units:
            var = ctk.BooleanVar(value=unit['id'] in self.selected_unit_ids)
            display_name = f"{unit['name']} ({unit.get('group_name', '?')})"
            cb = ctk.CTkCheckBox(scroll, text=display_name, variable=var, font=theme_config.get_font("body"))
            cb.pack(anchor="w", padx=10, pady=3)
            checkboxes[unit['id']] = {'var': var}
        
        def save():
            self.selected_unit_ids.clear()
            for uid, cb in checkboxes.items():
                if cb['var'].get():
                    self.selected_unit_ids.add(uid)
            self.update_units_label()
            self.apply_filters()
            dialog.destroy()
        
        btn_container = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(10, 20))
        ctk.CTkButton(btn_container, text="💾 Εφαρμογή", command=save, width=140, height=40, **theme_config.get_button_style("success")).pack(side="right", padx=5)
        ctk.CTkButton(btn_container, text="❌ Ακύρωση", command=dialog.destroy, width=140, height=40, **theme_config.get_button_style("secondary")).pack(side="right", padx=5)
    
    def update_units_label(self):
        if not self.selected_unit_ids:
            self.units_label.configure(text="(Όλες)")
        else:
            self.units_label.configure(text=f"({len(self.selected_unit_ids)} επιλεγμένες)")
    
    # ═══════════════════════════════════════════════════════════════
    # FILTERING - FIXED: Compare location NAMES
    # ═══════════════════════════════════════════════════════════════
    
    def apply_filters(self):
        search_text = self.search_entry.get().strip() or None
        status_map = {"Όλες": None, "Εκκρεμείς": "pending", "Ολοκληρωμένες": "completed"}
        status = status_map.get(self.status_combo.get())
        type_key = self.type_combo.get()
        task_type_id = self.types_dict.get(type_key) if type_key != "Όλα" else None
        
        all_tasks = database.get_all_tasks()
        filtered_tasks = []
        
        for task in all_tasks:
            if status and task['status'] != status:
                continue
            
            if task_type_id and task['task_type_id'] != task_type_id:
                continue
            
            # Group filter
            if self.selected_group_ids:
                task_unit_id = task['unit_id']
                unit_in_group = False
                for gid in self.selected_group_ids:
                    group_units = database.get_units_by_group(gid)
                    if any(u['id'] == task_unit_id for u in group_units):
                        unit_in_group = True
                        break
                if not unit_in_group:
                    continue
            
            # Location filter - FIXED: Get unit's location NAME and compare
            if self.selected_location_names:
                all_units = database.get_all_units()
                task_unit = next((u for u in all_units if u['id'] == task['unit_id']), None)
                if not task_unit:
                    continue
                unit_location = task_unit.get('location', '')
                if unit_location not in self.selected_location_names:
                    continue
            
            # Unit filter
            if self.selected_unit_ids and task['unit_id'] not in self.selected_unit_ids:
                continue
            
            # Search text filter
            if search_text:
                search_lower = search_text.lower()
                searchable = f"{task['description']} {task.get('notes', '')} {task['unit_name']} {task['task_type_name']}".lower()
                if search_lower not in searchable:
                    continue
            
            filtered_tasks.append(task)
        
        self.load_tasks(filtered_tasks)
    
    def clear_filters(self):
        self.search_entry.delete(0, "end")
        self.status_combo.set("Όλες")
        self.type_combo.set("Όλα")
        
        self.selected_group_ids.clear()
        self.selected_location_names.clear()
        self.selected_unit_ids.clear()
        
        self.update_groups_label()
        self.update_locations_label()
        self.update_units_label()
        
        self.load_tasks()
    
    # ═══════════════════════════════════════════════════════════════
    # TASK DISPLAY
    # ═══════════════════════════════════════════════════════════════
    
    def load_tasks(self, tasks=None):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        
        if tasks is None:
            tasks = database.get_all_tasks()
        
        if not tasks:
            ctk.CTkLabel(self.tasks_frame, text="Δεν βρέθηκαν εργασίες", font=theme_config.get_font("body"), text_color=self.theme["text_secondary"]).pack(pady=50)
            return
        
        ctk.CTkLabel(self.tasks_frame, text=f"📊 Βρέθηκαν {len(tasks)} εργασίες", font=theme_config.get_font("body", "bold"), text_color=self.theme["text_primary"]).pack(anchor="w", padx=10, pady=10)
        
        for task in tasks:
            card = TaskCard(self.tasks_frame, task, on_click=self.on_task_click if self.on_task_select else None)
            card.pack(fill="x", pady=5, padx=10)
    
    def on_task_click(self, task):
        if self.on_task_select:
            self.on_task_select(task)
