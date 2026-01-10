"""
Task History View Component
============================
Προβολή ιστορικού εργασιών

Extracted από ui_components.py για καλύτερη οργάνωση.
"""

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import theme_config
import utils_refactored
from .task_card import TaskCard

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

