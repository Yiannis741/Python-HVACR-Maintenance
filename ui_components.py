"""
UI Components - Επαναχρησιμοποιήσιμα components
"""

import customtkinter as ctk
from datetime import datetime
import database
from tkinter import messagebox


class TaskCard(ctk.CTkFrame):
    """Καρτέλα εργασίας για προβολή"""
    
    def __init__(self, parent, task_data):
        super().__init__(parent, corner_radius=10, fg_color="#f0f0f0")
        
        self.task = task_data
        self.create_card()
        
    def create_card(self):
        """Δημιουργία της καρτέλας"""
        
        # Status indicator
        status_color = "#2fa572" if self.task['status'] == 'completed' else "#ff9800"
        status_text = "✓ Ολοκληρωμένη" if self.task['status'] == 'completed' else "⏳ Εκκρεμής"
        
        status_label = ctk.CTkLabel(
            self,
            text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        )
        status_label. grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        # Task type
        type_label = ctk.CTkLabel(
            self,
            text=f"🔧 {self.task['task_type_name']}",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        type_label.grid(row=1, column=0, sticky="w", padx=15, pady=2)
        
        # Description
        desc_label = ctk.CTkLabel(
            self,
            text=self.task['description'][:60] + "..." if len(self.task['description']) > 60 else self.task['description'],
            font=ctk.CTkFont(size=12)
        )
        desc_label.grid(row=2, column=0, sticky="w", padx=15, pady=2)
        
        # Unit and date
        info_text = f"📍 {self.task['unit_name']} ({self.task['group_name']}) | 📅 {self.task['created_date']}"
        info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.grid(row=3, column=0, sticky="w", padx=15, pady=(2, 10))


class TaskForm(ctk.CTkFrame):
    """Φόρμα για προσθήκη νέας εργασίας"""
    
    def __init__(self, parent, on_save_callback):
        super().__init__(parent, fg_color="transparent")
        
        self.on_save_callback = on_save_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_form()
        
    def create_form(self):
        """Δημιουργία της φόρμας"""
        
        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self)
        scrollable.pack(fill="both", expand=True)
        
        # Μονάδα
        ctk.CTkLabel(scrollable, text="Μονάδα:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        units = database.get_all_units()
        self.units_dict = {f"{u['name']} - {u['group_name']}": u['id'] for u in units}
        
        self.unit_combo = ctk. CTkComboBox(
            scrollable,
            values=list(self.units_dict. keys()),
            width=400,
            state="readonly"
        )
        self.unit_combo.pack(anchor="w", pady=(0, 15))
        if self.units_dict:
            self.unit_combo.set(list(self.units_dict. keys())[0])
        
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
        self.priority_combo.pack(anchor="w", pady=(0, 15))
        self.priority_combo.set("Μεσαία (medium)")
        
        # Τεχνικός
        ctk.CTkLabel(scrollable, text="Όνομα Τεχνικού:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.technician_entry = ctk.CTkEntry(scrollable, width=400)
        self.technician_entry. pack(anchor="w", pady=(0, 15))
        
        # Σημειώσεις
        ctk.CTkLabel(scrollable, text="Σημειώσεις:", font=ctk. CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.notes_text = ctk.CTkTextbox(scrollable, width=400, height=80)
        self.notes_text.pack(anchor="w", pady=(0, 20))
        
        # Κουμπιά
        buttons_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        buttons_frame.pack(anchor="w", pady=10)
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Αποθήκευση",
            command=self.save_task,
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#2fa572",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk. CTkButton(
            buttons_frame,
            text="✖ Ακύρωση",
            command=self.on_save_callback,
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#666",
            font=ctk. CTkFont(size=14, weight="bold")
        )
        cancel_btn.pack(side="left")
        
    def save_task(self):
        """Αποθήκευση της εργασίας"""
        
        # Validation
        if not self.description_text.get("1.0", "end-1c").strip():
            messagebox.showerror("Σφάλμα", "Η περιγραφή είναι υποχρεωτική!")
            return
            
        # Παίρνουμε τα δεδομένα
        unit_key = self.unit_combo.get()
        unit_id = self.units_dict.get(unit_key)
        
        task_type_key = self.task_type_combo.get()
        task_type_id = self.task_types_dict.get(task_type_key)
        
        description = self.description_text.get("1.0", "end-1c").strip()
        status = self.status_var.get()
        
        priority_map = {"Χαμηλή (low)": "low", "Μεσαία (medium)": "medium", "Υψηλή (high)": "high"}
        priority = priority_map.get(self.priority_combo.get(), "medium")
        
        technician = self.technician_entry.get().strip()
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        created_date = datetime.now().strftime("%Y-%m-%d")
        completed_date = created_date if status == "completed" else None
        
        # Αποθήκευση
        try:
            database.add_task(
                unit_id, task_type_id, description, status, priority,
                created_date, completed_date, technician if technician else None,
                notes if notes else None
            )
            
            messagebox.showinfo("Επιτυχία", "Η εργασία αποθηκεύτηκε με επιτυχία!")
            self.on_save_callback()
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αποθήκευσης: {str(e)}")


class UnitsManagement(ctk.CTkFrame):
    """Διαχείριση Μονάδων και Ομάδων"""
    
    def __init__(self, parent, refresh_callback):
        super().__init__(parent, fg_color="transparent")
        
        self.refresh_callback = refresh_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        
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
        scrollable. pack(fill="both", expand=True, padx=10, pady=10)
        
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
            
    def add_unit_dialog(self):
        """Dialog για προσθήκη μονάδας"""
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Προσθήκη Νέας Μονάδας")
        dialog.geometry("500x600")
        dialog.grab_set()
        
        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Μονάδας:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450)
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Ομάδα
        ctk. CTkLabel(dialog, text="Ομάδα:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        groups = database.get_all_groups()
        groups_dict = {g['name']: g['id'] for g in groups}
        group_combo = ctk.CTkComboBox(dialog, values=list(groups_dict.keys()), width=450, state="readonly")
        group_combo.pack(padx=20, pady=(0, 15))
        if groups_dict:
            group_combo.set(list(groups_dict.keys())[0])
        
        # Τοποθεσία
        ctk.CTkLabel(dialog, text="Τοποθεσία:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        location_entry = ctk.CTkEntry(dialog, width=450)
        location_entry.pack(padx=20, pady=(0, 15))
        
        # Μοντέλο
        ctk.CTkLabel(dialog, text="Μοντέλο:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        model_entry = ctk.CTkEntry(dialog, width=450)
        model_entry.pack(padx=20, pady=(0, 15))
        
        # Serial Number
        ctk.CTkLabel(dialog, text="Σειριακός Αριθμός:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        serial_entry = ctk.CTkEntry(dialog, width=450)
        serial_entry.pack(padx=20, pady=(0, 15))
        
        # Ημερομηνία εγκατάστασης
        ctk.CTkLabel(dialog, text="Ημερομηνία Εγκατάστασης (YYYY-MM-DD):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        install_entry = ctk.CTkEntry(dialog, width=450)
        install_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        install_entry.pack(padx=20, pady=(0, 20))
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox. showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return
            
            group_id = groups_dict.get(group_combo.get())
            location = location_entry.get().strip()
            model = model_entry.get().strip()
            serial = serial_entry.get().strip()
            install_date = install_entry.get().strip()
            
            try:
                database.add_unit(name, group_id, location, model, serial, install_date)
                messagebox.showinfo("Επιτυχία", "Η μονάδα προστέθηκε με επιτυχία!")
                dialog.destroy()
                self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αποτυχία:  {str(e)}")
        
        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, fg_color="#2fa572", height=40).pack(pady=10)
        
    def add_group_dialog(self):
        """Dialog για προσθήκη ομάδας"""
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Προσθήκη Νέας Ομάδας")
        dialog.geometry("500x350")
        dialog.grab_set()
        
        # Όνομα
        ctk. CTkLabel(dialog, text="Όνομα Ομάδας:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk. CTkEntry(dialog, width=450)
        name_entry. pack(padx=20, pady=(0, 15))
        
        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100)
        desc_text.pack(padx=20, pady=(0, 20))
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return
            
            desc = desc_text.get("1.0", "end-1c").strip()
            
            result = database.add_group(name, desc)
            if result: 
                messagebox.showinfo("Επιτυχία", "Η ομάδα προστέθηκε με επιτυχία!")
                dialog.destroy()
                self.refresh_callback()
            else:
                messagebox.showerror("Σφάλμα", "Το όνομα υπάρχει ήδη!")
        
        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, fg_color="#2fa572", height=40).pack(pady=10)
