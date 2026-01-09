"""
Units Management Component
===========================
Διαχείριση Μονάδων (Units)

Extracted από ui_components.py για καλύτερη οργάνωση.
Ένα από τα μεγαλύτερα components (753 lines).
"""

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import theme_config
import custom_dialogs
import utils_refactored
from .locations_mgmt import LocationsManagement

class UnitsManagement(ctk.CTkFrame):
    """Διαχείριση Μονάδων και Ομάδων - Phase 2.3 Updated"""
    
    def __init__(self, parent, refresh_callback):
        super().__init__(parent, fg_color="transparent")
        
        self.refresh_callback = refresh_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_ui()
        
    def create_ui(self):
        """Δημιουργία UI - Phase 2.3: Only Units and Groups"""
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)
        
        self.tab1 = self.tabview.add("Μονάδες")
        self.tab2 = self.tabview.add("Ομάδες")
        self.tab3 = self.tabview.add("Τοποθεσία")
        self.tab4 = self.tabview.add("Κάδος")
        
        # Tab Μονάδες
        self.create_units_tab(self.tab1)
        
        # Tab Ομάδες
        self.create_groups_tab(self.tab2)
        
        # Tab Τοποθεσία
        locations_widget = LocationsManagement(self.tab3, refresh_callback=self.refresh_ui)
        locations_widget.pack(fill="both", expand=True)
        
        # Tab Κάδος
        self.create_recycle_tab(self.tab4)
        

    def create_units_tab(self, parent):
        """Tab για διαχείριση μονάδων - Grouped by Category"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        theme = theme_config.get_current_theme()

        # Header με κουμπί προσθήκης
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=15, padx=10)

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Προσθήκη Νέας Μονάδας",
            command=self.add_unit_dialog,
            height=40,
            font=theme_config.get_font("body", "bold"),
            **theme_config.get_button_style("success")
        )
        add_btn.pack(side="left")

        # Info label
        info_label = ctk.CTkLabel(
            header_frame,
            text="💡 Οι μονάδες είναι οργανωμένες ανά ομάδα.  Κλικ στο βέλος για άνοιγμα/κλείσιμο.",
            font=theme_config.get_font("small"),
            text_color=theme["text_secondary"]
        )
        info_label.pack(side="right", padx=20)

        # Scrollable frame για τις ομάδες
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Παίρνουμε όλες τις ομάδες
        groups = database.get_all_groups()

        if not groups:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν ομάδες.  Προσθέστε μία στην καρτέλα 'Ομάδες'.",
                font=theme_config.get_font("body"),
                text_color=theme["text_secondary"]
            ).pack(pady=50)
            return

        # Dictionary για να κρατάμε τα expanded states
        if not hasattr(self, 'expanded_groups'):
            self.expanded_groups = {group['id']: False for group in groups}  # Όλα κλειστά by default

        # Δημιουργία collapsible section για κάθε ομάδα
        for group in groups:
            self.create_group_section(scrollable, group, theme)

    def create_group_section(self, parent, group, theme):
        """Δημιουργία collapsible section για μία ομάδα"""

        # Container για την ομάδα
        group_container = ctk.CTkFrame(parent, fg_color="transparent")
        group_container.pack(fill="x", pady=5, padx=5)

        # Παίρνουμε τις μονάδες της ομάδας
        units = database.get_units_by_group(group['id'])
        units_count = len(units)

        # Header της ομάδας (clickable)
        header_frame = ctk.CTkFrame(
            group_container,
            corner_radius=10,
            fg_color=theme["card_bg"],
            border_color=theme["accent_blue"],
            border_width=2,
            cursor="hand2"
        )
        header_frame.pack(fill="x", pady=(0, 5))

        # Expand/Collapse state
        is_expanded = self.expanded_groups.get(group['id'], True)

        # Header label με arrow, όνομα ομάδας και count
        arrow_var = ctk.StringVar(value="▼" if is_expanded else "▶")

        header_label = ctk.CTkLabel(
            header_frame,
            textvariable=arrow_var,
            font=theme_config.get_font("body", "bold"),
            text_color=theme["accent_blue"],
            cursor="hand2"
        )
        header_label.pack(side="left", padx=(15, 5), pady=12)

        name_label = ctk.CTkLabel(
            header_frame,
            text=f"{group['name']} ({units_count} μονάδες)",
            font=theme_config.get_font("body", "bold"),
            text_color=theme["accent_blue"],
            cursor="hand2"
        )
        name_label.pack(side="left", padx=0, pady=12)

        # Description αν υπάρχει
        if group.get('description'):
            desc_label = ctk.CTkLabel(
                header_frame,
                text=f"• {group['description']}",
                font=theme_config.get_font("small"),
                text_color=theme["text_secondary"]
            )
            desc_label.pack(side="left", padx=10)

        # Units container (collapsible)
        units_container = ctk.CTkFrame(group_container, fg_color="transparent")

        # Δημιουργία του περιεχομένου των μονάδων
        if units:
            for unit in units:
                unit_frame = ctk.CTkFrame(
                    units_container,
                    corner_radius=8,
                    fg_color=theme["card_bg"],
                    border_color=theme["card_border"],
                    border_width=1
                )
                unit_frame.pack(fill="x", pady=3, padx=5)

                # Unit info
                info_parts = [
                    f"🔧 {unit['name']}",
                    f"📍 {unit['location']}",
                    f"🏷️ {unit['model']}"
                ]

                if unit.get('serial_number'):
                    info_parts.append(f"S/N: {unit['serial_number']}")

                info_text = " | ".join(info_parts)

                label = ctk.CTkLabel(
                    unit_frame,
                    text=info_text,
                    font=theme_config.get_font("small"),
                    text_color=theme["text_primary"],
                    anchor="w"
                )
                label.pack(side="left", padx=15, pady=10, fill="x", expand=True)

                # Edit button
                edit_btn = ctk.CTkButton(
                    unit_frame,
                    text="✏️",
                    command=lambda u=unit: self.edit_unit_dialog(u),
                    width=40,
                    height=30,
                    **theme_config.get_button_style("primary")
                )
                edit_btn.pack(side="right", padx=10, pady=10)
        else:
            # Άδεια ομάδα
            empty_label = ctk.CTkLabel(
                units_container,
                text="Δεν υπάρχουν μονάδες σε αυτή την ομάδα.",
                font=theme_config.get_font("small"),
                text_color=theme["text_disabled"]
            )
            empty_label.pack(pady=10, padx=20)

        # Αρχική κατάσταση (show/hide)
        if is_expanded:
            units_container.pack(fill="x", padx=20)

        # Toggle function - LOCAL UPDATE ΜΟΝΟ!
        def toggle_group(event=None):
            # Get current state (with default False for new groups)
            current_state = self.expanded_groups.get(group['id'], False)
            new_state = not current_state
            self.expanded_groups[group['id']] = new_state

            # Update arrow
            arrow_var.set("▼" if new_state else "▶")

            # Show/Hide container (NO FULL REFRESH!)
            if new_state:
                units_container.pack(fill="x", padx=20)
            else:
                units_container.pack_forget()

        # Bind click events
        header_frame.bind("<Button-1>", toggle_group)
        header_label.bind("<Button-1>", toggle_group)
        name_label.bind("<Button-1>", toggle_group)

    def create_groups_tab(self, parent):
        """Tab για διαχείριση ομάδων - Compact View"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        theme = theme_config.get_current_theme()

        # Header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=15, padx=10)

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Προσθήκη Νέας Ομάδας",
            command=self.add_group_dialog,
            height=40,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        add_btn.pack(side="left")

        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        groups = database.get_all_groups()

        if not groups:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν ομάδες.",
                font=theme_config.get_font("body"),
                text_color=theme["text_secondary"]
            ).pack(pady=50)
            return

        # Grid configuration για 2 στήλες
        scrollable.grid_columnconfigure(0, weight=1)
        scrollable.grid_columnconfigure(1, weight=1)

        for idx, group in enumerate(groups):
            row = idx // 2
            col = idx % 2

            # Group card
            group_frame = ctk.CTkFrame(
                scrollable,
                corner_radius=10,
                fg_color=theme["card_bg"],
                border_color=theme["accent_blue"],
                border_width=2
            )
            group_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)

            # Content frame
            content_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=12)

            # Group name
            name_label = ctk.CTkLabel(
                content_frame,
                text=f"📂 {group['name']}",
                font=theme_config.get_font("body", "bold"),
                text_color=theme["accent_blue"],
                anchor="w"
            )
            name_label.pack(anchor="w")

            # Description
            if group.get('description'):
                desc_label = ctk.CTkLabel(
                    content_frame,
                    text=group['description'],
                    font=theme_config.get_font("small"),
                    text_color=theme["text_secondary"],
                    anchor="w",
                    wraplength=250
                )
                desc_label.pack(anchor="w", pady=(5, 0))

            # Units count
            units = database.get_units_by_group(group['id'])
            count_label = ctk.CTkLabel(
                content_frame,
                text=f"🔧 {len(units)} μονάδες",
                font=theme_config.get_font("small"),
                text_color=theme["text_disabled"],
                anchor="w"
            )
            count_label.pack(anchor="w", pady=(5, 0))

            # Edit button
            edit_btn = ctk.CTkButton(
                group_frame,
                text="✏️ Επεξεργασία",
                command=lambda g=group: self.edit_group_dialog(g),
                width=120,
                height=30,
                **theme_config.get_button_style("primary")
            )
            edit_btn.pack(pady=(0, 10))

    def add_unit_dialog(self, unit_data=None):
        """Dialog για προσθήκη/επεξεργασία μονάδας"""

        is_edit_mode = unit_data is not None

        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Μονάδας" if is_edit_mode else "Προσθήκη Νέας Μονάδας")
        dialog.geometry("500x700")
        dialog.grab_set()

        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Μονάδας:", font=theme_config.get_font("body", "bold")).pack(anchor="w",
                                                                                                     padx=20,
                                                                                                     pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))

        # Ομάδα
        ctk.CTkLabel(dialog, text="Ομάδα:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                             pady=(10, 5))
        groups = database.get_all_groups()
        groups_dict = {g['name']: g['id'] for g in groups}
        group_combo = ctk.CTkComboBox(dialog, values=list(groups_dict.keys()), width=450, state="readonly",
                                      font=theme_config.get_font("input"))
        group_combo.pack(padx=20, pady=(0, 15))
        
        # Set default group
        if groups_dict:
            if is_edit_mode and 'group_id' in unit_data:
                # EDITING: Find and set current group
                current_group_id = unit_data['group_id']
                for group_name, group_id in groups_dict.items():
                    if group_id == current_group_id:
                        group_combo.set(group_name)
                        break
            else:
                # NEW: Set first group
                group_combo.set(list(groups_dict.keys())[0])

        # Τοποθεσία (Dropdown)
        ctk.CTkLabel(dialog, text="Τοποθεσία:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                 pady=(10, 5))
        
        # Get locations for dropdown
        try:
            locations = database.get_all_locations()
            location_names = [loc['name'] for loc in locations]
        except:
            location_names = []
        
        if not location_names:
            location_names = ["Δεν υπάρχουν τοποθεσίες"]
        
        location_entry = ctk.CTkComboBox(
            dialog, 
            width=450, 
            font=theme_config.get_font("input"),
            values=location_names,
            state="normal"  # Allow typing new locations
        )
        location_entry.pack(padx=20, pady=(0, 15))

        # Μοντέλο
        ctk.CTkLabel(dialog, text="Μοντέλο:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                               pady=(10, 5))
        model_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        model_entry.pack(padx=20, pady=(0, 15))

        # Σημειώσεις (αντικατέστησε Serial Number)
        ctk.CTkLabel(dialog, text="Σημειώσεις:", font=theme_config.get_font("body", "bold")).pack(anchor="w",
                                                                                                   padx=20,
                                                                                                   pady=(10, 5))
        notes_entry = ctk.CTkTextbox(dialog, width=450, height=80, font=theme_config.get_font("input"))
        notes_entry.pack(padx=20, pady=(0, 15))

        # Ημερομηνία εγκατάστασης
        ctk.CTkLabel(dialog, text="Ημερομηνία Εγκατάστασης (DD/MM/YY):",
                     font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        install_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        install_entry.pack(padx=20, pady=(0, 20))

        # Populate fields if editing
        if is_edit_mode:
            name_entry.insert(0, unit_data['name'])
            location_entry.set(unit_data.get('location', ''))
            model_entry.insert(0, unit_data.get('model') or '')
            notes_entry.insert('1.0', unit_data.get('notes') or '')
            # Set installation date
            display_date = utils_refactored.format_date_for_display(unit_data.get('installation_date', ''))
            install_entry.insert(0, display_date)

        # -------- BUTTONS --------
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(padx=20, pady=10, fill="x", expand=True)

        def save():
            name = name_entry.get().strip()
            if not name:
                custom_dialogs.show_error("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return

            group_id = groups_dict.get(group_combo.get())
            location = location_entry.get().strip()
            model = model_entry.get().strip()
            notes = notes_entry.get('1.0', 'end-1c').strip()
            install_date = install_entry.get().strip()

            try:
                if is_edit_mode:
                    database.update_unit(unit_data['id'], name, group_id, location, model, notes, install_date)
                    custom_dialogs.show_success("Επιτυχία", "Η μονάδα ενημερώθηκε με επιτυχία!")
                else:
                    database.add_unit(name, group_id, location, model, notes, install_date)
                    custom_dialogs.show_success("Επιτυχία", "Η μονάδα προστέθηκε με επιτυχία!")
                dialog.destroy()
                self.refresh_callback()
                self.refresh_ui()
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία: {str(e)}")

        save_btn = ctk.CTkButton(buttons_frame, text="💾 Αποθήκευση", command=save,
                                 **theme_config.get_button_style("success"), height=40)
        save_btn.pack(side="left", padx=10)

        if is_edit_mode:
            def delete():
                result = custom_dialogs.ask_yes_no("Επιβεβαίωση", "Θέλετε να διαγράψετε αυτή τη μονάδα;")
                if result:
                    try:
                        database.soft_delete_unit(unit_data['id'])
                        custom_dialogs.show_success("Επιτυχία", "Η μονάδα διαγράφηκε με επιτυχία.")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    except Exception as e:
                        custom_dialogs.show_error("Σφάλμα", f"Aποτυχία: {str(e)}")

            delete_btn = ctk.CTkButton(buttons_frame, text="🗑️ Διαγραφή", command=delete,
                                       **theme_config.get_button_style("danger"), height=40)
            delete_btn.pack(side="right", padx=10)

        cancel_btn = ctk.CTkButton(buttons_frame, text="✖ Ακύρωση", command=dialog.destroy,
                                   **theme_config.get_button_style("secondary"), height=40)
        cancel_btn.pack(side="right", padx=10)



    
    def edit_unit_dialog(self, unit):
        """Wrapper για επεξεργασία μονάδας"""
        self.add_unit_dialog(unit_data=unit)
        
    def add_group_dialog(self, group_data=None):
        """Dialog για προσθήκη/επεξεργασία ομάδας"""
        
        is_edit_mode = group_data is not None
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Ομάδας" if is_edit_mode else "Προσθήκη Νέας Ομάδας")
        dialog.geometry("500x550")
        dialog.grab_set()
        
        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Ομάδας:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))
        
        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100, font=theme_config.get_font("input"))
        desc_text.pack(padx=20, pady=(0, 20))
        
        # Populate fields if editing
        if is_edit_mode:
            name_entry.insert(0, group_data['name'])
            desc_text.insert("1.0", group_data.get('description', ''))

        def save():
            name = name_entry.get().strip()
            if not name:
                custom_dialogs.show_error("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return

            desc = desc_text.get("1.0", "end-1c").strip()

            try:
                if is_edit_mode:
                    result = database.update_group(group_data['id'], name, desc)
                    if result:
                        custom_dialogs.show_success("Επιτυχία", "Η ομάδα ενημερώθηκε με επιτυχία!")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    else:
                        custom_dialogs.show_error("Σφάλμα", "Το όνομα υπάρχει ήδη!")
                else:
                    result = database.add_group(name, desc)
                    if result:
                        custom_dialogs.show_success("Επιτυχία", "Η ομάδα προστέθηκε με επιτυχία!")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    else:
                        custom_dialogs.show_error("Σφάλμα", "Το όνομα υπάρχει ήδη!")
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία: {str(e)}")

        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                      height=40).pack(pady=10)

        def confirm_soft_delete():
            import custom_dialogs
            if custom_dialogs.ask_yes_no("Διαγραφή",
                                   "Θέλετε να διαγράψετε την ομάδα και τις μονάδες της; Η ενέργεια είναι αναστρέψιμη από τον κάδο."):
                try:
                    res = database.soft_delete_group(group_data['id'])
                    # soft_delete_group returns True on success
                    if res:
                        custom_dialogs.show_success("Επιτυχία", "Η ομάδα διαγράφηκε!")
                        dialog.destroy()
                        self.refresh_callback()
                        self.refresh_ui()
                    else:
                        custom_dialogs.show_error("Σφάλμα", "Αποτυχία διαγραφής.")
                except Exception as e:
                    custom_dialogs.show_error("Σφάλμα", str(e))

        ctk.CTkButton(dialog, text="🗑️ Διαγραφή", command=confirm_soft_delete,
                      **theme_config.get_button_style("danger"), height=36).pack(pady=10)


        

    
    def edit_group_dialog(self, group):
        """Wrapper για επεξεργασία ομάδας"""
        self.add_group_dialog(group_data=group)

    def manage_unit_ui(unit_id):
        """
        Επεξεργασία και διαγραφή Μονάδας UI
        Εδώ προστίθεται επιλογή διαγραφής μονάδας.
        """
        print(f"Επεξεργασία Μονάδας με ID: {unit_id}")

        # Κώδικας για εμφάνιση των στοιχείων της μονάδας
        # (π.χ. φόρμες, text fields, dropdowns)
        print("Φόρτωση δεδομένων μονάδας για επεξεργασία...")

        print("\n[UI]: Προσθήκη κουμπιού 'Αποθήκευση αλλαγών μονάδας'")
        print("[UI]: Προσθήκη κουμπιού 'Διαγραφή μονάδας'")

        print(f"Για το ID μονάδας {unit_id}, εμφανίζεται το UI.")

        def delete_unit_button_handler():
            """
            Διαχείριση: Διαγραφή Μονάδας
            """
            print(f"[System]: Επιλογή για Διαγραφή Μονάδας με ID {unit_id}")
            # Προσθήκη λογικής για ερώτηση επιβεβαίωσης
            confirmation = input(f"Είστε σίγουροι ότι θέλετε να διαγράψετε τη μονάδα {unit_id}; (y/n): ").lower()
            if confirmation == 'y':
                print(f"[System]: Η μονάδα {unit_id} διαγράφηκε επιτυχώς.")
                # Εκτέλεση διαγραφής από τη βάση δεδομένων
            else:
                print("[System]: Η διαγραφή ακυρώθηκε.")

        # Κλήση του 'delete_unit_button_handler' αν ο χρήστης διαλέξει "Διαγραφή Μονάδας".
        delete_unit_button_handler()

    def manage_group_ui(group_id):
        """
        Επεξεργασία και διαγραφή Ομάδας UI
        Εδώ προστίθεται επιλογή διαγραφής ομάδας.
        """
        print(f"Επεξεργασία Ομάδας με ID: {group_id}")

        # Κώδικας για εμφάνιση των στοιχείων της ομάδας
        # (π.χ. φόρμες, text fields, dropdowns)
        print("Φόρτωση δεδομένων ομάδας για επεξεργασία...")

        print("\n[UI]: Προσθήκη κουμπιού 'Αποθήκευση αλλαγών ομάδας'")
        print("[UI]: Προσθήκη κουμπιού 'Διαγραφή ομάδας'")

        print(f"Για το ID ομάδας {group_id}, εμφανίζεται το UI.")

        def delete_group_button_handler():
            """
            Διαχείριση: Διαγραφή Ομάδας
            """
            print(f"[System]: Επιλογή για Διαγραφή Ομάδας με ID {group_id}")
            # Προσθήκη λογικής για ερώτηση επιβεβαίωσης
            confirmation = input(f"Είστε σίγουροι ότι θέλετε να διαγράψετε την ομάδα {group_id}; (y/n): ").lower()
            if confirmation == 'y':
                print(f"[System]: Η ομάδα {group_id} διαγράφηκε επιτυχώς.")
                # Εκτέλεση διαγραφής από τη βάση δεδομένων
            else:
                print("[System]: Η διαγραφή ακυρώθηκε.")

        # Κλήση του 'delete_group_button_handler' αν ο χρήστης διαλέξει "Διαγραφή Ομάδας".
        delete_group_button_handler()

    def create_recycle_tab(self, parent):
        """Κάδος διαγραμμένων"""
        for w in parent.winfo_children():
            w.destroy()
        theme = theme_config.get_current_theme()
        ctk.CTkLabel(parent, text="🗑️ Κάδος Μονάδων & Ομάδων", font=theme_config.get_font("title", "bold"),
                     text_color=theme["accent_blue"]).pack(pady=20)

        # Ομάδες Κάδου
        groups = database.get_deleted_groups()
        if groups:
            ctk.CTkLabel(parent, text="Διαγραμμένες Ομάδες", font=theme_config.get_font("body", "bold"),
                         text_color=theme["accent_orange"]).pack(anchor="w", padx=20, pady=(10, 5))
            for group in groups:
                frm = ctk.CTkFrame(parent, fg_color=theme["card_bg"], border_color=theme["card_border"], border_width=1)
                frm.pack(fill="x", padx=20, pady=4)
                ctk.CTkLabel(frm, text=f"📂 {group['name']}", font=theme_config.get_font("body"),
                             text_color=theme["text_primary"]).pack(side="left", padx=10, pady=8)
                # Buttons container
                btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
                btn_frame.pack(side="right", padx=14, pady=8)
                
                restore_btn = ctk.CTkButton(btn_frame, text="🔄 Επαναφορά", width=110, height=30,
                                            command=lambda gid=group['id']: self.restore_group_ui(gid),
                                            **theme_config.get_button_style("success"))
                restore_btn.pack(side="left", padx=5)
                
                delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Οριστική", width=110, height=30,
                                           command=lambda gid=group['id']: self.permanent_delete_group_ui(gid),
                                           **theme_config.get_button_style("danger"))
                delete_btn.pack(side="left", padx=5)
        else:
            ctk.CTkLabel(parent, text="Δεν υπάρχουν διαγραμμένες ομάδες.", font=theme_config.get_font("small"),
                         text_color=theme["text_disabled"]).pack(anchor="w", padx=26, pady=0)

        # Μονάδες Κάδου
        units = database.get_deleted_units()
        if units:
            ctk.CTkLabel(parent, text="Διαγραμμένες Μονάδες", font=theme_config.get_font("body", "bold"),
                         text_color=theme["accent_orange"]).pack(anchor="w", padx=20, pady=(26, 7))
            for unit in units:
                frm = ctk.CTkFrame(parent, fg_color=theme["card_bg"], border_color=theme["card_border"], border_width=1)
                frm.pack(fill="x", padx=20, pady=3)
                label = f"🔧 {unit['name']} ({unit['group_name']})"
                ctk.CTkLabel(frm, text=label, font=theme_config.get_font("small"),
                             text_color=theme["text_primary"]).pack(side="left", padx=10, pady=6)
                # Buttons container
                btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
                btn_frame.pack(side="right", padx=14, pady=6)
                
                restore_btn = ctk.CTkButton(btn_frame, text="🔄 Επαναφορά", width=110, height=30,
                                            command=lambda uid=unit['id']: self.restore_unit_ui(uid),
                                            **theme_config.get_button_style("success"))
                restore_btn.pack(side="left", padx=5)
                
                delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Οριστική", width=110, height=30,
                                           command=lambda uid=unit['id']: self.permanent_delete_unit_ui(uid),
                                           **theme_config.get_button_style("danger"))
                delete_btn.pack(side="left", padx=5)
        else:
            ctk.CTkLabel(parent, text="Δεν υπάρχουν διαγραμμένες μονάδες.", font=theme_config.get_font("small"),
                         text_color=theme["text_disabled"]).pack(anchor="w", padx=26, pady=(7, 0))

    def restore_unit_ui(self, unit_id):
        database.restore_unit(unit_id)
        # from tkinter import messagebox  # ← Replaced with custom dialogs
        import custom_dialogs
        custom_dialogs.show_success("Επαναφορά", "Η μονάδα επανήλθε από τον κάδο!")
        self.refresh_ui()

    def restore_group_ui(self, group_id):
        database.restore_group(group_id)
        # from tkinter import messagebox  # ← Replaced with custom dialogs
        import custom_dialogs
        custom_dialogs.show_success("Επαναφορά", "Η ομάδα και οι μονάδες της επανήλθαν από τον κάδο!")
        self.refresh_ui()

    def permanent_delete_unit_ui(self, unit_id):
        """Οριστική διαγραφή μονάδας"""
        result = custom_dialogs.ask_yes_no(
            "Οριστική Διαγραφή",
            "Θέλετε να διαγράψετε ΟΡΙΣΤΙΚΑ αυτή τη μονάδα;\n\nΑυτή η ενέργεια ΔΕΝ μπορεί να αναιρεθεί!"
        )
        if result:
            try:
                database.permanent_delete_unit(unit_id)
                custom_dialogs.show_success("Επιτυχία", "Η μονάδα διαγράφηκε οριστικά.")
                self.create_recycle_tab(self.tab4)
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", str(e))

    def permanent_delete_group_ui(self, group_id):
        """Οριστική διαγραφή ομάδας"""
        result = custom_dialogs.ask_yes_no(
            "Οριστική Διαγραφή",
            "Θέλετε να διαγράψετε ΟΡΙΣΤΙΚΑ αυτή την ομάδα;\n\nΑυτή η ενέργεια ΔΕΝ μπορεί να αναιρεθεί!"
        )
        if result:
            try:
                database.permanent_delete_group(group_id)
                custom_dialogs.show_success("Επιτυχία", "Η ομάδα διαγράφηκε οριστικά.")
                self.create_recycle_tab(self.tab4)
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", str(e))


    def refresh_ui(self):
        """Ανανέωση του UI - Phase 2.3"""
        # Clear and recreate tabs
        self.create_units_tab(self.tab1)
        self.create_groups_tab(self.tab2)


# ----- PHASE 2.3: NEW TASK MANAGEMENT COMPONENT -----

