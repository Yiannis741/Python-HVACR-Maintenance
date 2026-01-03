"""
UI Components - Επαναχρησιμοποιήσιμα components - Phase 2
"""

import customtkinter as ctk
from datetime import datetime
import database
from tkinter import messagebox


class TaskCard(ctk.CTkFrame):
    """Καρτέλα εργασίας για προβολή"""
    
    def __init__(self, parent, task_data, on_click=None):
        super().__init__(parent, corner_radius=10, fg_color="#f0f0f0")
        
        self.task = task_data
        self.on_click = on_click
        self.create_card()
        
        # Clickable
        if on_click:
            self. configure(cursor="hand2")
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
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        )
        status_label. pack(side="left")
        
        priority_label = ctk.CTkLabel(
            header_frame,
            text=f"  •  {self.task. get('priority', 'medium').upper()}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=priority_color
        )
        priority_label.pack(side="left")
        
        # Task type
        type_label = ctk.CTkLabel(
            self,
            text=f"🔧 {self.task['task_type_name']}",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        type_label.grid(row=1, column=0, sticky="w", padx=15, pady=2)
        
        # Description
        desc_text = self.task['description'][: 80] + "..." if len(self.task['description']) > 80 else self.task['description']
        desc_label = ctk.CTkLabel(
            self,
            text=desc_text,
            font=ctk. CTkFont(size=12),
            wraplength=500,
            justify="left"
        )
        desc_label.grid(row=2, column=0, sticky="w", padx=15, pady=2)
        
        # Unit and date
        info_text = f"📍 {self.task['unit_name']} ({self.task['group_name']}) | 📅 {self.task['created_date']}"
        if self.task. get('technician_name'):
            info_text += f" | 👤 {self.task['technician_name']}"
        
        info_label = ctk. CTkLabel(
            self,
            text=info_text,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.grid(row=3, column=0, sticky="w", padx=15, pady=(2, 10))
        
        # Bind click to all widgets
        if self.on_click:
            for widget in [self, header_frame, status_label, priority_label, type_label, desc_label, info_label]: 
                widget.bind("<Button-1>", lambda e: self.on_click(self.task))
                widget.configure(cursor="hand2")


class TaskForm(ctk.CTkFrame):
    """Φόρμα για προσθήκη/επεξεργασία εργασίας"""
    
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
        """Δημιουργία της φόρμας"""
        
        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.pack(fill="both", expand=True)
        
        # Μονάδα
        ctk.CTkLabel(scrollable, text="Μονάδα:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        units = database.get_all_units()
        self.units_dict = {f"{u['name']} - {u['group_name']}": u['id'] for u in units}
        
        self.unit_combo = ctk.CTkComboBox(
            scrollable,
            values=list(self.units_dict. keys()),
            width=400,
            state="readonly"
        )
        self.unit_combo.pack(anchor="w", pady=(0, 15))
        if self.units_dict:
            self.unit_combo.set(list(self.units_dict.keys())[0])
        
        # Είδος

