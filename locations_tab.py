"""
Locations Tab Component
=======================

Standalone component για διαχείριση τοποθεσιών.
Προσθέστε το στο ui_components.py ή χρησιμοποιήστε standalone.
"""

import customtkinter as ctk
import theme_config
import database_refactored as database
import custom_dialogs

class LocationsManagement(ctk.CTkFrame):
    """Διαχείριση Τοποθεσιών"""
    
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        
        self.refresh_callback = refresh_callback
        self.theme = theme_config.get_current_theme()
        
        self.create_ui()
        self.refresh_ui()
    
    def create_ui(self):
        """Create UI"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="📍 Διαχείριση Τοποθεσιών",
            font=theme_config.get_font("heading", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="➕ Νέα Τοποθεσία",
            command=self.add_location_dialog,
            **theme_config.get_button_style("primary"),
            height=35
        ).pack(side="right")
        
        # Scrollable list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.theme["bg_secondary"]
        )
        self.scroll_frame.pack(fill="both", expand=True)
    
    def refresh_ui(self):
        """Refresh locations list"""
        
        # Clear
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Load locations
        try:
            locations = database.get_all_locations()
        except:
            locations = []
        
        if not locations:
            ctk.CTkLabel(
                self.scroll_frame,
                text="Δεν υπάρχουν τοποθεσίες.\nΠατήστε '➕ Νέα Τοποθεσία' για προσθήκη.",
                font=theme_config.get_font("body"),
                text_color=self.theme["text_disabled"]
            ).pack(pady=50)
            return
        
        # Show locations
        for location in locations:
            self.create_location_card(location)
    
    def create_location_card(self, location):
        """Create location card"""
        
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_width=1,
            border_color=self.theme["card_border"]
        )
        card.pack(fill="x", padx=10, pady=5)
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)
        
        # Name
        ctk.CTkLabel(
            content,
            text=f"📍 {location['name']}",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left")
        
        # Description
        if location.get('description'):
            ctk.CTkLabel(
                content,
                text=f"  •  {location['description']}",
                font=theme_config.get_font("small"),
                text_color=self.theme["text_secondary"]
            ).pack(side="left", padx=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="✏️",
            command=lambda: self.edit_location_dialog(location),
            width=40,
            **theme_config.get_button_style("secondary")
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️",
            command=lambda: self.delete_location(location),
            width=40,
            **theme_config.get_button_style("danger")
        ).pack(side="left", padx=2)
    
    def add_location_dialog(self, location_data=None):
        """Add/Edit location dialog"""
        
        is_edit = location_data is not None
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Τοποθεσίας" if is_edit else "Νέα Τοποθεσία")
        dialog.geometry("500x300")
        dialog.grab_set()
        
        # Name
        ctk.CTkLabel(
            dialog,
            text="Όνομα Τοποθεσίας:",
            font=theme_config.get_font("body", "bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Description
        ctk.CTkLabel(
            dialog,
            text="Περιγραφή (προαιρετικό):",
            font=theme_config.get_font("body", "bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        desc_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        desc_entry.pack(padx=20, pady=(0, 20))
        
        # Populate if editing
        if is_edit:
            name_entry.insert(0, location_data['name'])
            desc_entry.insert(0, location_data.get('description', ''))
        
        # Save function
        def save():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name:
                custom_dialogs.show_error("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return
            
            try:
                if is_edit:
                    database.update_location(location_data['id'], name, description)
                    custom_dialogs.show_success("Επιτυχία", "Η τοποθεσία ενημερώθηκε!")
                else:
                    database.add_location(name, description)
                    custom_dialogs.show_success("Επιτυχία", "Η τοποθεσία προστέθηκε!")
                
                dialog.destroy()
                self.refresh_ui()
                if self.refresh_callback:
                    self.refresh_callback()
            
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", str(e))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Αποθήκευση",
            command=save,
            **theme_config.get_button_style("success"),
            height=40
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Ακύρωση",
            command=dialog.destroy,
            **theme_config.get_button_style("secondary"),
            height=40
        ).pack(side="right", expand=True, padx=5)
    
    def edit_location_dialog(self, location):
        """Edit location"""
        self.add_location_dialog(location)
    
    def delete_location(self, location):
        """Delete location"""
        
        if custom_dialogs.ask_yes_no(
            "Διαγραφή Τοποθεσίας",
            f"Θέλετε να διαγράψετε την τοποθεσία '{location['name']}';\n\nΗ ενέργεια είναι αναστρέψιμη."
        ):
            try:
                database.soft_delete_location(location['id'])
                custom_dialogs.show_success("Επιτυχία", "Η τοποθεσία διαγράφηκε!")
                self.refresh_ui()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", str(e))
