"""
Tasks Management Component
===========================
Διαχείριση Εργασιών με Filtering

Extracted από ui_components.py για καλύτερη οργάνωση.
"""

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import theme_config
import custom_dialogs
import utils_refactored
from .task_card import TaskCard

class TaskManagement(ctk.CTkFrame):
    """Διαχείριση Τύπων και Ειδών Εργασιών - Phase 2. 3"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.theme = theme_config.get_current_theme()
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.search_timer = None
        self.create_ui()

    def create_ui(self):
        """Δημιουργία UI"""

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        self.tab1 = self.tabview.add("Τύποι Εργασιών")
        self.tab2 = self.tabview.add("Είδη Εργασιών")

        # Tab Τύποι Εργασιών
        self.create_task_types_tab(self.tab1)

        # Tab Είδη Εργασιών
        self.create_task_items_tab(self.tab2)

    def refresh_ui(self):
        """Ανανέωση του UI"""
        # Clear and recreate tabs
        self.create_task_types_tab(self.tab1)
        self.create_task_items_tab(self.tab2)

    def create_task_types_tab(self, parent):
        """Tab για διαχείριση τύπων εργασιών"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        # Info label
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_color=self.theme["accent_blue"],
            border_width=1
        )
        info_frame.pack(fill="x", pady=10, padx=10)

        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Οι προκαθορισμένοι τύποι (Service, Βλάβη, Επισκευή, Απλός Έλεγχος) προστατεύονται και δεν μπορούν να διαγραφούν.  Μπορείτε να προσθέσετε δικούς σας custom τύπους.",
            font=theme_config.get_font("small"),
            wraplength=800,
            text_color=self.theme["accent_blue"]
        )
        info_label.pack(padx=15, pady=10)

        # Κουμπί προσθήκης
        add_btn = ctk.CTkButton(
            parent,
            text="➕ Προσθήκη Custom Τύπου Εργασίας",
            command=self.add_task_type_dialog,
            height=40,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        add_btn.pack(pady=15)

        # Λίστα τύπων εργασιών
        scrollable = ctk.CTkScrollableFrame(parent)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        task_types = database.get_all_task_types()

        # Separate predefined and custom
        predefined_types = [tt for tt in task_types if tt['is_predefined']]
        custom_types = [tt for tt in task_types if not tt['is_predefined']]

        # Predefined types section
        if predefined_types:
            ctk.CTkLabel(
                scrollable,
                text="📌 Προκαθορισμένοι Τύποι",
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(anchor="w", padx=10, pady=(10, 5))

            for task_type in predefined_types:
                type_frame = ctk.CTkFrame(
                    scrollable,
                    corner_radius=10,
                    fg_color=self.theme["card_bg"],
                    border_color=self.theme["accent_blue"],
                    border_width=2
                )
                type_frame.pack(fill="x", pady=5, padx=10)

                info_text = f"🔧 {task_type['name']}"
                if task_type.get('description'):
                    info_text += f" - {task_type['description']}"

                label = ctk.CTkLabel(
                    type_frame,
                    text=info_text,
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_primary"]
                )
                label.pack(side="left", padx=15, pady=10)

        # Custom types section
        if custom_types:
            ctk.CTkLabel(
                scrollable,
                text="⚙️ Custom Τύποι",
                font=theme_config.get_font("body", "bold"),
                text_color=self.theme["accent_green"]
            ).pack(anchor="w", padx=10, pady=(20, 5))

            for task_type in custom_types:
                type_frame = ctk.CTkFrame(
                    scrollable,
                    corner_radius=10,
                    fg_color=self.theme["card_bg"],
                    border_color=self.theme["card_border"],
                    border_width=1
                )
                type_frame.pack(fill="x", pady=5, padx=10)

                info_text = f"🔧 {task_type['name']}"
                if task_type.get('description'):
                    info_text += f" - {task_type['description']}"

                label = ctk.CTkLabel(
                    type_frame,
                    text=info_text,
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_primary"]
                )
                label.pack(side="left", padx=15, pady=10, fill="x", expand=True)

                # Delete button
                delete_btn = ctk.CTkButton(
                    type_frame,
                    text="🗑️",
                    command=lambda tt=task_type: self.delete_task_type(tt),
                    width=40,
                    height=30,
                    **theme_config.get_button_style("danger")
                )
                delete_btn.pack(side="right", padx=10, pady=10)

        if not custom_types:
            ctk.CTkLabel(
                scrollable,
                text="Δεν υπάρχουν custom τύποι.  Προσθέστε έναν! ",
                font=theme_config.get_font("small"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=20)

    def add_task_type_dialog(self):
        """Dialog για προσθήκη custom τύπου εργασίας"""

        dialog = ctk.CTkToplevel(self)
        dialog.title("Προσθήκη Custom Τύπου Εργασίας")
        dialog.geometry("500x350")
        dialog.grab_set()

        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Τύπου:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                   pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))

        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                 pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100, font=theme_config. get_font("input"))
        desc_text.pack(padx=20, pady=(0, 20))

        def save():
            name = name_entry.get().strip()
            if not name:
                custom_dialogs.show_error("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return

            desc = desc_text.get("1.0", "end-1c").strip()

            try:
                result = database.add_task_type(name, desc)
                if result:
                    custom_dialogs.show_success("Επιτυχία", "Ο τύπος εργασίας προστέθηκε με επιτυχία!")
                    dialog.destroy()
                    self.refresh_ui()
                else:
                    custom_dialogs.show_error("Σφάλμα", "Το όνομα υπάρχει ήδη!")
            except Exception as e:
                import logger_config
                logger = logger_config.get_logger(__name__)
                logger.error(f"Failed to add task type: {e}", exc_info=True)
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία προσθήκης: {str(e)}")

        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                      height=40).pack(pady=10)

    def delete_task_type(self, task_type):
        """Διαγραφή custom τύπου εργασίας"""

        result = custom_dialogs.ask_yes_no(
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον τύπο '{task_type['name']}';"
        )

        if result:
            try:
                delete_result = database.delete_task_type(task_type['id'])

                if delete_result:
                    custom_dialogs.show_success("Επιτυχία", "Ο τύπος εργασίας διαγράφηκε!")
                    self.refresh_ui()
                else:
                    custom_dialogs.show_error("Σφάλμα",
                                              "Ο τύπος δεν μπορεί να διαγραφεί (είτε είναι προκαθορισμένος, είτε χρησιμοποιείται σε εργασίες).")
            except Exception as e:
                import logger_config
                logger = logger_config.get_logger(__name__)
                logger.error(f"Failed to delete task type {task_type['id']}: {e}", exc_info=True)
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία διαγραφής: {str(e)}")

    def create_task_items_tab(self, parent):
        """Tab για διαχείριση ειδών εργασιών - Phase 2.3"""

        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()

        # Info label
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card_bg"],
            corner_radius=10,
            border_color=self.theme["accent_green"],
            border_width=1
        )
        info_frame.pack(fill="x", pady=10, padx=10)

        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Τα είδη εργασιών είναι υποκατηγορίες των τύπων. Επιλέξτε έναν τύπο για να δείτε τα είδη του.  Μπορείτε να προσθέσετε, επεξεργαστείτε ή αφαιρέσετε είδη.",
            font=theme_config.get_font("small"),
            wraplength=800,
            text_color=self.theme["accent_green"]
        )
        info_label.pack(padx=15, pady=10)

        # Επιλογή Τύπου Εργασίας
        selector_frame = ctk.CTkFrame(parent, fg_color="transparent")
        selector_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            selector_frame,
            text="Τύπος Εργασίας:",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(side="left", padx=10)

        task_types = database.get_all_task_types()
        self.task_types_dict = {tt['name']: tt['id'] for tt in task_types}

        self.selected_type_var = ctk.StringVar()
        self.type_selector = ctk.CTkComboBox(
            selector_frame,
            values=list(self.task_types_dict.keys()),
            width=250,
            state="readonly",
            command=self.on_type_selected,
            variable=self.selected_type_var,
            font=theme_config.get_font("input")
        )
        self.type_selector.pack(side="left", padx=10)
        if self.task_types_dict:
            self.type_selector.set(list(self.task_types_dict.keys())[0])

        # Κουμπί προσθήκης
        self.add_item_btn = ctk.CTkButton(
            selector_frame,
            text="➕ Προσθήκη Είδους",
            command=self.add_task_item_dialog,
            height=35,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        self.add_item_btn.pack(side="right", padx=10)

        # Λίστα ειδών
        self.items_scrollable = ctk.CTkScrollableFrame(parent)
        self.items_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial load
        self.load_items_for_selected_type()

    def on_type_selected(self, selected_type):
        """Callback όταν επιλέγεται τύπος - Phase 2.3"""
        self.load_items_for_selected_type()

    def load_items_for_selected_type(self):
        """Φόρτωση ειδών για τον επιλεγμένο τύπο - Phase 2.3"""

        # Clear existing items
        for widget in self.items_scrollable.winfo_children():
            widget.destroy()

        selected_type = self.type_selector.get()
        type_id = self.task_types_dict.get(selected_type)

        if not type_id:
            return

        items = database.get_task_items_by_type(type_id)

        if not items:
            ctk.CTkLabel(
                self.items_scrollable,
                text="Δεν υπάρχουν είδη για αυτόν τον τύπο.  Προσθέστε ένα!",
                font=theme_config.get_font("small"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=30)
            return

        # Count label
        ctk.CTkLabel(
            self.items_scrollable,
            text=f"📊 {len(items)} είδη για τον τύπο '{selected_type}'",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # Display items
        for item in items:
            item_frame = ctk.CTkFrame(
                self.items_scrollable,
                corner_radius=10,
                fg_color=self.theme["card_bg"],
                border_color=self.theme["card_border"],
                border_width=1
            )
            item_frame.pack(fill="x", pady=5, padx=10)

            info_text = f"📌 {item['name']}"
            if item.get('description'):
                info_text += f"\n   {item['description']}"

            label = ctk.CTkLabel(
                item_frame,
                text=info_text,
                font=theme_config.get_font("small"),
                text_color=self.theme["text_primary"],
                justify="left"
            )
            label.pack(side="left", padx=15, pady=10, fill="x", expand=True)

            # Action buttons
            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)

            # Edit button
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️",
                command=lambda i=item: self.edit_task_item_dialog(i),
                width=35,
                height=30,
                **theme_config.get_button_style("primary")
            )
            edit_btn.pack(side="left", padx=2)

            # Delete button
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️",
                command=lambda i=item: self.delete_task_item(i),
                width=35,
                height=30,
                **theme_config.get_button_style("danger")
            )
            delete_btn.pack(side="left", padx=2)

    def add_task_item_dialog(self, item_data=None):
        """Dialog για προσθήκη/επεξεργασία είδους - Phase 2.3"""

        is_edit_mode = item_data is not None

        dialog = ctk.CTkToplevel(self)
        dialog.title("Επεξεργασία Είδους" if is_edit_mode else "Προσθήκη Νέου Είδους Εργασίας")
        dialog.geometry("500x400")
        dialog.grab_set()

        # Current type
        selected_type = self.type_selector.get()
        type_id = self.task_types_dict.get(selected_type)

        ctk.CTkLabel(
            dialog,
            text=f"Τύπος: {selected_type}",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(pady=(20, 10))

        # Όνομα
        ctk.CTkLabel(dialog, text="Όνομα Είδους:", font=theme_config.get_font("body", "bold")).pack(anchor="w", padx=20,
                                                                                                    pady=(10, 5))
        name_entry = ctk.CTkEntry(dialog, width=450, font=theme_config.get_font("input"))
        name_entry.pack(padx=20, pady=(0, 15))

        # Περιγραφή
        ctk.CTkLabel(dialog, text="Περιγραφή (προαιρετική):", font=theme_config.get_font("body", "bold")).pack(
            anchor="w", padx=20, pady=(10, 5))
        desc_text = ctk.CTkTextbox(dialog, width=450, height=100, font=theme_config.get_font("input"))
        desc_text.pack(padx=20, pady=(0, 20))

        # Populate if editing
        if is_edit_mode:
            name_entry.insert(0, item_data['name'])
            if item_data.get('description'):
                desc_text.insert("1.0", item_data['description'])

        def save():
            name = name_entry.get().strip()
            if not name:
                custom_dialogs.show_error("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                return

            desc = desc_text.get("1.0", "end-1c").strip()

            try:
                if is_edit_mode:
                    result = database.update_task_item(item_data['id'], name, desc)
                    if result:
                        custom_dialogs.show_success("Επιτυχία", "Το είδος ενημερώθηκε με επιτυχία!")
                        dialog.destroy()
                        self.load_items_for_selected_type()
                    else:
                        custom_dialogs.show_error("Σφάλμα", "Το όνομα υπάρχει ήδη για αυτόν τον τύπο!")
                else:
                    result = database.add_task_item(name, type_id, desc)
                    if result:
                        custom_dialogs.show_success("Επιτυχία", "Το είδος προστέθηκε με επιτυχία!")
                        dialog.destroy()
                        self.load_items_for_selected_type()
                    else:
                        custom_dialogs.show_error("Σφάλμα", "Το όνομα υπάρχει ήδη για αυτόν τον τύπο!")

            except Exception as e:
                import logger_config
                logger = logger_config.get_logger(__name__)
                logger.error(f"Failed to save task item: {e}", exc_info=True)
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία: {str(e)}")


        ctk.CTkButton(dialog, text="💾 Αποθήκευση", command=save, **theme_config.get_button_style("success"),
                      height=40).pack(pady=10)

    def edit_task_item_dialog(self, item):
        """Wrapper για επεξεργασία είδους - Phase 2.3"""
        self.add_task_item_dialog(item_data=item)

    def delete_task_item(self, item):
        """Διαγραφή είδους εργασίας - Phase 2.3"""

        result = custom_dialogs.ask_yes_no(
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε το είδος '{item['name']}'?\n\nΑυτή η ενέργεία θα είναι δυνατή μόνο αν δεν χρησιμοποιείται σε υπάρχουσες εργασίες."
        )

        if result:
            try:
                delete_result = database.delete_task_item(item['id'])

                if delete_result:
                    custom_dialogs.show_success("Επιτυχία", "Το είδος διαγράφηκε!")
                    self.load_items_for_selected_type()
                else:
                    custom_dialogs.show_error("Σφάλμα",
                                              "Το είδος δεν μπορεί να διαγραφεί (χρησιμοποιείται σε εργασίες).")
            except Exception as e:
                import logger_config
                logger = logger_config.get_logger(__name__)
                logger.error(f"Failed to delete task item {item['id']}: {e}", exc_info=True)
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία διαγραφής: {str(e)}")

# ----- PHASE 2: NEW COMPONENTS -----

