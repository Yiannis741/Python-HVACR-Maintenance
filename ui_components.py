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
        
        # Είδος Εργασίας
        ctk.CTkLabel(scrollable, text="Είδος Εργασίας:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        task_types = database.get_all_task_types()
        self.task_types_dict = {tt['name']: tt['id'] for tt in task_types}
        
        self.task_type_combo = ctk.CTkComboBox(
            scrollable,
            values=list(self.task_types_dict.keys()),
            width=400,
            state="readonly"
        )
        self.task_type_combo.pack(anchor="w", pady=(0, 15))
        if self.task_types_dict:
            self.task_type_combo.set(list(self.task_types_dict. keys())[0])
        
        # Περιγραφή
        ctk.CTkLabel(scrollable, text="Περιγραφή Εργασίας:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.description_text = ctk.CTkTextbox(scrollable, width=400, height=100)
        self.description_text.pack(anchor="w", pady=(0, 15))
        
        # Κατάσταση
        ctk.CTkLabel(scrollable, text="Κατάσταση:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.status_var = ctk.StringVar(value="pending")
        
        status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        status_frame.pack(anchor="w", pady=(0, 15))
        
        ctk.CTkRadioButton(
            status_frame,
            text="Εκκρεμής",
            variable=self.status_var,
            value="pending"
        ).pack(side="left", padx=(0, 20))
        
        ctk. CTkRadioButton(
            status_frame,
            text="Ολοκληρωμένη",
            variable=self.status_var,
            value="completed"
        ).pack(side="left")
        
        # Προτεραιότητα
        ctk.CTkLabel(scrollable, text="Προτεραιότητα:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.priority_combo = ctk.CTkComboBox(
            scrollable,
            values=["Χαμηλή (low)", "Μεσαία (medium)", "Υψηλή (high)"],
            width=400,
            state="readonly"
        )
        self.priority_combo. pack(anchor="w", pady=(0, 15))
        self.priority_combo.set("Μεσαία (medium)")
        
        # Ημερομηνία Δημιουργίας
        ctk.CTkLabel(scrollable, text="Ημερομηνία Δημιουργίας (YYYY-MM-DD):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.created_date_entry = ctk.CTkEntry(scrollable, width=400)
        self.created_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.created_date_entry. pack(anchor="w", pady=(0, 15))
        
        # Τεχνικός
        ctk.CTkLabel(scrollable, text="Όνομα Τεχνικού:", font=ctk. CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.technician_entry = ctk.CTkEntry(scrollable, width=400)
        self.technician_entry. pack(anchor="w", pady=(0, 15))
        
        # Σημειώσεις
        ctk.CTkLabel(scrollable, text="Σημειώσεις:", font=ctk. CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.notes_text = ctk.CTkTextbox(scrollable, width=400, height=80)
        self.notes_text.pack(anchor="w", pady=(0, 20))
        
        # Κουμπιά
        buttons_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        buttons_frame.pack(anchor="w", pady=10)
        
        save_text = "💾 Ενημέρωση" if self.is_edit_mode else "💾 Αποθήκευση"
        save_btn = ctk.CTkButton(
            buttons_frame,
            text=save_text,
            command=self.save_task,
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#2fa572",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✖ Ακύρωση",
            command=self.on_save_callback,
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#666",
            font=ctk.CTkFont(size=14, weight="bold")
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
                corner_radius=10,
                fg_color="#c94242",
                font=ctk. CTkFont(size=14, weight="bold")
            )
            delete_btn.pack(side="left", padx=(10, 0))
    
    def populate_form(self):
        """Γέμισμα της φόρμας με υπάρχοντα δεδομένα"""
        if not self.task_data:
            return
        
        # Βρίσκουμε το κλειδί της μονάδας
        for key, unit_id in self.units_dict.items():
            if unit_id == self.task_data['unit_id']:
                self. unit_combo.set(key)
                break
        
        # Βρίσκουμε το είδος εργασίας
        for key, type_id in self.task_types_dict.items():
            if type_id == self.task_data['task_type_id']: 
                self.task_type_combo.set(key)
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
        """Αποθήκευση της εργασίας"""
        
        # Validation
        if not self.description_text.get("1.0", "end-1c").strip():
            messagebox.showerror("Σφάλμα", "Η περιγραφή είναι υποχρεωτική!")
            return
        
        # Παίρνουμε τα δεδομένα
        unit_key = self.unit_combo.get()
        unit_id = self.units_dict. get(unit_key)
        
        task_type_key = self.task_type_combo.get()
        task_type_id = self.task_types_dict.get(task_type_key)
        
        description = self.description_text.get("1.0", "end-1c").strip()
        status = self.status_var.get()
        
        priority_map = {"Χαμηλή (low)": "low", "Μεσαία (medium)": "medium", "Υψηλή (high)": "high"}
        priority = priority_map.get(self.priority_combo.get(), "medium")
        
        technician = self.technician_entry.get().strip()
        notes = self. notes_text.get("1.0", "end-1c").strip()
        
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
                    notes if notes else None
                )
                messagebox.showinfo("Επιτυχία", "Η εργασία ενημερώθηκε με επιτυχία!")
            else:
                # Insert
                database.add_task(
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, technician if technician else None,
                    notes if notes else None
                )
                messagebox.showinfo("Επιτυχία", "Η εργασία αποθηκεύτηκε με επιτυχία!")
            
            self.on_save_callback()
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αποθήκευσης:  {str(e)}")
    
    def delete_task(self):
        """Διαγραφή εργασίας"""
        if not self.is_edit_mode:
            return
        
        result = messagebox.askyesno("Επιβεβαίωση", 
                                     "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτή την εργασία;\n\n"
                                     "Η εργασία θα μεταφερθεί στον Κάδο Ανακύκλωσης.")
        
        if result: 
            try:
                database.delete_task(self.task_data['id'])
                messagebox.showinfo("Επιτυχία", "Η εργασία διαγράφηκε!")
                self.on_save_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής: {str(e)}")


class UnitsManagement(ctk.CTkFrame):
    """Διαχείριση Μονάδων και Ομάδων"""
    
    def __init__(self, parent, refresh_callback):
        super().__init__(parent, fg_color="transparent")
        
        self. refresh_callback = refresh_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self. create_ui()
        
    def create_ui(self):
        """Δημιουργία UI"""
        
        # Tabs
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True)
        
        tab1 = tabview.add("Μονάδες")
        tab2 = tabview.add("Ομάδες")
        
        # Tab Μονάδες
        self.create_units_tab(tab1)
        
        # Tab Ομάδες
        self.create_groups_tab(tab2)
        
    def create_units_tab(self, parent):
        """Tab για διαχείριση μονάδων"""
        
        # Κουμπί προσθήκης
        add_btn = ctk.CTkButton(
            parent,
            text="➕ Προσθήκη Νέας Μονάδας",
            command=self.add_unit_dialog,
            height=40,
            fg_color="#2fa572",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(pady=15)
        
        # Λίστα μονάδων
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        units = database.get_all_units()
        
        for unit in units:
            unit_frame = ctk.CTkFrame(scrollable, corner_radius=10)
            unit_frame.pack(fill="x", pady=5, padx=10)
            
            info_text = f"🔧 {unit['name']} | 📂 {unit['group_name']} | 📍 {unit['location']} | 🏷️ {unit['model']}"
            
            label = ctk.CTkLabel(
                unit_frame,
                text=info_text,
                font=ctk.CTkFont(size=12)
            )
            label.pack(side="left", padx=15, pady=10)
            
    def create_groups_tab(self, parent):
        """Tab για διαχείριση ομάδων"""
        
        # Κουμπί προσθήκης
        add_btn = ctk.CTkButton(
            parent,
            text="➕ Προσθήκη Νέας Ομάδας",
            command=self.add_group_dialog,
            height=40,
            fg_color="#2fa572",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(pady=15)
        
        # Λίστα ομάδων
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        groups = database.get_all_groups()
        
        for group in groups:
            group_frame = ctk.CTkFrame(scrollable, corner_radius=10)
            group_frame.pack(fill="x", pady=5, padx=10)
            
            units = database.get_units_by_group(group['id'])
            units_count = len(units)
            
            info_text = f"📂 {group['name']} | {group['description']} | Μονάδες: {units_count}"
            
            label = ctk.CTkLabel(
                group_frame,
                text=info_text,
                font=ctk. CTkFont(size=12)
            )
            label.pack(side="left", padx=15, pady=10)
