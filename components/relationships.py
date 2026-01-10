"""
Task Relationships View Component
==================================
Προβολή και διαχείριση σχέσεων εργασιών (chains)

Extracted από ui_components.py για καλύτερη οργάνωση.
Ένα από τα μεγαλύτερα components (624 lines).
"""

import customtkinter as ctk
import theme_config
import database_refactored as database
import custom_dialogs
import utils_refactored
from .task_card import TaskCard

class TaskRelationshipsView(ctk.CTkFrame):
    """Διαχείριση σχέσεων εργασιών - Enhanced Timeline View"""

    def __init__(self, parent, task_data, refresh_callback):
        super().__init__(parent, fg_color="transparent")

        self.task_data = task_data
        self.refresh_callback = refresh_callback
        self.theme = theme_config.get_current_theme()
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_ui()
        self.load_relationships()

    def create_ui(self):
        """Δημιουργία UI"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # Title με unit info
        title_text = f"🔗 Αλυσίδα Εργασιών για {self.task_data['unit_name']}"
        ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack(side="left")

        # Info button
        info_btn = ctk.CTkButton(
            header_frame,
            text="ℹ️ Βοήθεια",
            command=self.show_help,
            width=100,
            height=32,
            **theme_config.get_button_style("secondary")
        )
        info_btn.pack(side="right")

        # Scrollable timeline
        self.timeline_frame = ctk.CTkScrollableFrame(self)
        self.timeline_frame.pack(fill="both", expand=True)



    def show_help(self):
        """Εμφάνιση βοήθειας"""
        help_text = """
    🔗 Αλυσίδα Εργασιών - Πώς λειτουργεί: 
    ... 
        """
        custom_dialogs.show_success("Βοήθεια - Αλυσίδα Εργασιών", help_text)

    # ← ΕΔΩ προσθέτετε την get_full_chain()
    def get_full_chain(self, task_id):
        """Παίρνει ολόκληρη την αλυσίδα (parents + current + children recursively)"""

        chain = []
        visited_parents = set()  # Αποφυγή infinite loops στους parents
        visited_children = set()  # Αποφυγή infinite loops στα children

        # 1. Βρες όλους τους parents recursively
        def get_all_parents(tid):
            if tid in visited_parents:
                return
            visited_parents.add(tid)

            rels = database.get_related_tasks(tid)
            for parent in rels['parents']:
                parent_id = parent['id']
                if parent_id not in [c['id'] for c in chain]:
                    chain.insert(0, parent)  # Προσθήκη στην αρχή
                    get_all_parents(parent_id)  # Recursive

        # 2. Βρες όλα τα children recursively
        def get_all_children(tid):
            if tid in visited_children:
                return
            visited_children.add(tid)

            rels = database.get_related_tasks(tid)
            for child in rels['children']:
                child_id = child['id']
                if child_id not in [c['id'] for c in chain]:
                    chain.append(child)  # Προσθήκη στο τέλος
                    get_all_children(child_id)  # Recursive

        # Build chain:  parents + current + children
        get_all_parents(task_id)

        # Προσθήκη current task
        chain.append(self.task_data)

        get_all_children(task_id)

        return chain

    def load_relationships(self):
        """Φόρτωση και εμφάνιση αλυσίδας - Updated to show full chain"""

        # Clear
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()

        # Get FULL chain
        full_chain = self.get_full_chain(self.task_data['id'])

        # Find current position
        current_position = None
        for idx, task in enumerate(full_chain, 1):
            if task['id'] == self.task_data['id']:
                current_position = idx
                break

        if current_position is None:
            current_position = 1
            full_chain = [self.task_data]

        total_in_chain = len(full_chain)

        # Info banner
        info_frame = ctk.CTkFrame(
            self.timeline_frame,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10
        )
        info_frame.pack(fill="x", padx=10, pady=(0, 20))

        info_text = f"📊 Αλυσίδα {total_in_chain} εργασιών  •  Θέση {current_position}/{total_in_chain}"
        if current_position == 1:
            info_text += "  •  🔵 Αυτή είναι η ΠΡΩΤΗ εργασία"
        if current_position == total_in_chain:
            info_text += "  •  🔚 Αυτή είναι η ΤΕΛΕΥΤΑΙΑ εργασία"

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(padx=20, pady=12)

        # Add parent button at top (if first in chain)
        if current_position == 1 and total_in_chain == 1:
            # Μόνος σου στην αλυσίδα
            self.create_add_button("parent", position=0)
            self.create_arrow("προκάλεσε", dashed=True)

        # Display all tasks in chain
        child_counter = 0  # Global counter για σωστή αρίθμηση children

        for idx, task in enumerate(full_chain, 1):
            # Determine type
            if idx < current_position:
                item_type = "parent"
                sequence_num = None
            elif idx == current_position:
                item_type = "current"
                sequence_num = None
            else:
                item_type = "child"
                child_counter += 1
                sequence_num = child_counter

            # ═══════════════════════════════════════════
            # FIX: Κουμπί ΜΟΝΟ για την τρέχουσα
            # ═══════════════════════════════════════════
            is_removable = (item_type == "current" and total_in_chain > 1)

            self.create_timeline_item(
                task,
                position=idx,
                item_type=item_type,
                sequence_num=sequence_num,
                is_removable=is_removable
            )

            # Arrow between tasks
            if idx < total_in_chain:
                self.create_arrow("ακολούθησε")

        # Add child button at bottom
        if current_position == total_in_chain:
            self.create_add_button("child", position=total_in_chain + 1)

    def create_timeline_item(self, task, position, item_type, sequence_num=None, is_removable=True):
        """Δημιουργία στοιχείου timeline"""

        # Container
        item_container = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        item_container.pack(fill="x", padx=10, pady=5)

        # Position badge + Type indicator
        badge_frame = ctk.CTkFrame(item_container, fg_color="transparent")
        badge_frame.pack(fill="x", pady=(0, 5))

        # Position number
        position_label = ctk.CTkLabel(
            badge_frame,
            text=f"[{position}]",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_disabled"],
            width=40
        )
        position_label.pack(side="left")

        # Type badge
        if item_type == "parent":
            badge_text = "🔵 Αρχική Εργασία"
            badge_color = self.theme["accent_blue"]
        elif item_type == "current":
            badge_text = "🟡 ΤΡΕΧΟΥΣΑ ΕΡΓΑΣΙΑ"
            badge_color = self.theme["accent_orange"]
        else:  # child
            badge_text = f"🟢 Συνέχεια {sequence_num}" if sequence_num else "🟢 Συνέχεια"
            badge_color = self.theme["accent_green"]

        badge = ctk.CTkLabel(
            badge_frame,
            text=badge_text,
            font=theme_config.get_font("body", "bold"),
            text_color=badge_color
        )
        badge.pack(side="left", padx=10)

        # Card container
        card_container = ctk.CTkFrame(item_container, fg_color="transparent")
        card_container.pack(fill="x")

        # Task card
        task_card_frame = ctk.CTkFrame(card_container, fg_color="transparent")
        task_card_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Enhanced task card - Bold border για current
        card = ctk.CTkFrame(
            task_card_frame,
            fg_color=self.theme["card_bg"],
            border_color=badge_color,
            border_width=4 if item_type == "current" else 2,
            corner_radius=10
        )
        card.pack(fill="x", padx=(40, 0))

        # ═══════════════════════════════════════════════════
        # REMOVE BUTTON - Μόνο για current, πάνω δεξιά
        # ═══════════════════════════════════════════════════

        if is_removable and item_type == "current":
            remove_container = ctk.CTkFrame(card, fg_color="transparent")
            remove_container.pack(fill="x", padx=12, pady=(10, 0))

            # Spacer (pushes button to right)
            ctk.CTkLabel(remove_container, text="").pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                remove_container,
                text="✖ Αφαίρεση από Αλυσίδα",
                command=lambda t=task, it=item_type: self.remove_relationship(t, it),
                width=180,
                height=30,
                fg_color=self.theme["accent_red"],
                hover_color="#8B0000",
                text_color="white",
                font=theme_config.get_font("small", "bold"),
                corner_radius=6
            ).pack(side="right")

        # Date badge (prominent)
        date_badge = ctk.CTkLabel(
            card,
            text=f"📅 {utils_refactored.format_date_for_display(task['created_date'])}",
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["accent_blue"],
            fg_color=self.theme["bg_secondary"],
            corner_radius=6,
            padx=10,
            pady=4
        )
        date_badge.pack(anchor="w", padx=12, pady=(10, 5))

        # Task info
        task_info = f"🔧 {task['task_type_name']}"
        if task.get('task_item_name'):
            task_info += f" → {task['task_item_name']}"

        info_label = ctk.CTkLabel(
            card,
            text=task_info,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        info_label.pack(anchor="w", padx=12, pady=(0, 5))

        # Description (truncated)
        desc_text = task['description'][: 80] + "..." if len(task['description']) > 80 else task['description']
        desc_label = ctk.CTkLabel(
            card,
            text=desc_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            anchor="w",
            wraplength=600
        )
        desc_label.pack(anchor="w", padx=12, pady=(0, 5))

        # Status + Technician
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.pack(fill="x", padx=12, pady=(0, 10))

        status_icon = "✅" if task['status'] == 'completed' else "⏳"
        status_text = "Ολοκληρωμένη" if task['status'] == 'completed' else "Εκκρεμής"

        ctk.CTkLabel(
            meta_frame,
            text=f"{status_icon} {status_text}",
            font=theme_config.get_font("tiny"),
            text_color=self.theme["text_disabled"]
        ).pack(side="left", padx=(0, 15))

        if task.get('technician_name'):
            ctk.CTkLabel(
                meta_frame,
                text=f"👤 {task['technician_name']}",
                font=theme_config.get_font("tiny"),
                text_color=self.theme["text_disabled"]
            ).pack(side="left")

    def create_arrow(self, label_text, dashed=False):
        """Δημιουργία βέλους σύνδεσης"""

        arrow_container = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        arrow_container.pack(fill="x", padx=10, pady=8)

        # Vertical line
        line_frame = ctk.CTkFrame(
            arrow_container,
            width=4,
            height=30,
            fg_color=self.theme["card_border"] if dashed else self.theme["accent_blue"],
            corner_radius=2
        )
        line_frame.pack(side="left", padx=(58, 10))  # Align with position badge

        # Label - FIX:   Remove "italic", use "normal"
        ctk.CTkLabel(
            arrow_container,
            text=f"↓ {label_text}",
            font=theme_config.get_font("small"),  # ← FIX:   Removed "italic"
            text_color=self.theme["text_disabled"] if dashed else self.theme["text_secondary"]
        ).pack(side="left")

    def create_add_button(self, relation_type, position):
        """Κουμπί προσθήκης στο timeline"""

        btn_container = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=10, pady=10)

        # Position badge
        ctk.CTkLabel(
            btn_container,
            text=f"[{position}]" if position > 0 else "[? ]",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_disabled"],
            width=40
        ).pack(side="left")

        # Add button
        if relation_type == "parent":
            btn_text = "➕ Προσθήκη Αρχικής Εργασίας"
            icon = "🔵"
        else:
            btn_text = "➕ Προσθήκη Νέας Συνέχειας"
            icon = "🟢"

        add_btn = ctk.CTkButton(
            btn_container,
            text=f"{icon} {btn_text}",
            command=lambda: self.add_relationship_dialog(relation_type),
            height=45,
            **theme_config.get_button_style("success"),
            font=theme_config.get_font("body", "bold")
        )
        add_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def add_relationship_dialog(self, relation_type):
        """Dialog για προσθήκη σύνδεσης - Date-filtered by relation type"""

        dialog = ctk.CTkToplevel(self)

        if relation_type == "parent":
            title_text = "Προσθήκη Αρχικής Εργασίας"
            icon = "🔵"
            info_text = "Επιλέξτε την εργασία που προηγήθηκε/προκάλεσε την τρέχουσα (μόνο παλιότερες εργασίες)"
        else:
            title_text = "Προσθήκη Συνέχειας Εργασίας"
            icon = "🟢"
            info_text = "Επιλέξτε την εργασία που ακολούθησε/προέκυψε από την τρέχουσα (μόνο νεότερες εργασίες)"

        dialog.title(title_text)
        dialog.geometry("850x850")
        dialog.grab_set()

        # Header με visual flow
        header_frame = ctk.CTkFrame(
            dialog,
            fg_color=self.theme["card_bg"],
            corner_radius=10
        )
        header_frame.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(
            header_frame,
            text=f"{icon} {title_text}",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["text_primary"]
        ).pack(padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header_frame,
            text=info_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"]
        ).pack(padx=20, pady=(0, 10))

        # Visual flow indicator
        flow_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        flow_frame.pack(fill="x", padx=20, pady=(0, 15))

        if relation_type == "parent":
            flow_text = "[ Επιλογή ] → προκάλεσε → [ Τρέχουσα Εργασία ]"
        else:
            flow_text = "[ Τρέχουσα Εργασία ] → ακολούθησε → [ Επιλογή ]"

        ctk.CTkLabel(
            flow_frame,
            text=flow_text,
            font=theme_config.get_font("small", "bold"),
            text_color=self.theme["accent_blue"]
        ).pack()

        # Scrollable task list
        scrollable = ctk.CTkScrollableFrame(dialog, height=500)
        scrollable.pack(fill="both", expand=True, padx=20, pady=10)

        # ═══════════════════════════════════════════════════════════════
        # ✨ NEW: DATE-FILTERED TASK SELECTION
        # ═══════════════════════════════════════════════════════════════

        # Get available tasks (exclude current task and already linked)
        all_tasks = database.get_all_tasks()
        current_id = self.task_data['id']

        # Get existing relationships
        relations = database.get_related_tasks(current_id)

        # Filter out current task and already linked tasks
        linked_ids = {current_id}
        linked_ids.update([t['id'] for t in relations['parents']])
        linked_ids.update([t['id'] for t in relations['children']])

        # ✨ Get current task's date for comparison
        current_date = self.task_data['created_date']

        # ✨ Filter tasks based on relation type and date
        available_tasks = []
        for t in all_tasks:
            # Basic filters (not already linked, same unit)
            if t['id'] in linked_ids or t['unit_id'] != self.task_data['unit_id']:
                continue

            # ✨ Date filter based on relation type
            if relation_type == "parent":
                # For parent: only OLDER tasks (before current)
                if t['created_date'] < current_date:
                    available_tasks.append(t)
            else:
                # For child: only NEWER tasks (after current)
                if t['created_date'] > current_date:
                    available_tasks.append(t)

        # ✨ Sort by date (chronological for better UX)
        if relation_type == "parent":
            # Parents: newest first (closest to current task)
            available_tasks.sort(key=lambda x: x['created_date'], reverse=True)
        else:
            # Children: oldest first (closest to current task)
            available_tasks.sort(key=lambda x: x['created_date'])

        # ═══════════════════════════════════════════════════════════════

        if not available_tasks:
            # ✨ Updated message
            if relation_type == "parent":
                message = "Δεν υπάρχουν παλιότερες εργασίες για σύνδεση."
            else:
                message = "Δεν υπάρχουν νεότερες εργασίες για σύνδεση."

            ctk.CTkLabel(
                scrollable,
                text=message,
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"]
            ).pack(pady=50)
            return



        # Display tasks
        for task in available_tasks:
            task_container = ctk.CTkFrame(
                scrollable,
                fg_color=self.theme["card_bg"],
                border_color=self.theme["card_border"],
                border_width=1,
                corner_radius=8
            )
            task_container.pack(fill="x", pady=3, padx=5)

            # Task info (left side)
            info_frame = ctk.CTkFrame(task_container, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            # Date badge
            ctk.CTkLabel(
                info_frame,
                text=f"📅 {utils_refactored.format_date_for_display(task['created_date'])}",
                font=theme_config.get_font("tiny", "bold"),
                text_color=self.theme["accent_blue"]
            ).pack(anchor="w")

            # Task type + item
            type_text = f"🔧 {task['task_type_name']}"
            if task.get('task_item_name'):
                type_text += f" → {task['task_item_name']}"

            ctk.CTkLabel(
                info_frame,
                text=type_text,
                font=theme_config.get_font("small", "bold"),
                text_color=self.theme["text_primary"],
                anchor="w"
            ).pack(anchor="w")

            # Description (truncated)
            desc = task['description'][: 60] + "..." if len(task['description']) > 60 else task['description']
            ctk.CTkLabel(
                info_frame,
                text=desc,
                font=theme_config.get_font("tiny"),
                text_color=self.theme["text_secondary"],
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))

            # Add button (right side)
            add_btn = ctk.CTkButton(
                task_container,
                text="➕ Προσθήκη",
                command=lambda t=task: self.link_task(t, relation_type, dialog),
                width=100,
                height=30,
                **theme_config.get_button_style("success")
            )
            add_btn.pack(side="right", padx=10, pady=8)

        # Cancel button at bottom
        ctk.CTkButton(
            dialog,
            text="✖ Ακύρωση",
            command=dialog.destroy,
            width=150,
            height=40,
            **theme_config.get_button_style("secondary")
        ).pack(pady=15)

    def link_task(self, selected_task, relation_type, dialog):
        """Link the selected task to current task"""

        if relation_type == "parent":
            parent_id = selected_task['id']
            child_id = self.task_data['id']
        else:
            parent_id = self.task_data['id']
            child_id = selected_task['id']

        try:
            database.add_task_relationship(parent_id, child_id, "related")
            
            # ═══ CHAIN SYNC ═══
            # After adding relationship, sync entire chain to last task's status
            try:
                # Get full chain starting from either parent or child
                full_chain = utils_refactored.get_full_task_chain(parent_id)
                
                if len(full_chain) > 1:
                    # Get the LAST task's status
                    last_task = full_chain[-1]
                    target_status = last_task['status']
                    target_completed_date = last_task.get('completed_date')
                    
                    # Update ALL tasks in chain to match last task
                    conn = database.get_connection()
                    cursor = conn.cursor()
                    
                    for task in full_chain:
                        cursor.execute(
                            "UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?",
                            (target_status, target_completed_date, task['id'])
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    # Inform user if chain status changed
                    if target_status == 'pending':
                        custom_dialogs.show_success(
                            "Επιτυχία", 
                            f"Η σύνδεση προστέθηκε!\n\n"
                            f"ℹ️ Η αλυσίδα ({len(full_chain)} εργασίες) επανανοίγει αυτόματα\n"
                            f"επειδή η τελευταία εργασία είναι εκκρεμής."
                        )
                    else:
                        custom_dialogs.show_success("Επιτυχία", f"Η σύνδεση προστέθηκε με επιτυχία!")
                else:
                    custom_dialogs.show_success("Επιτυχία", f"Η σύνδεση προστέθηκε με επιτυχία!")
                    
            except Exception as e:
                print(f"Chain sync warning after relationship add: {e}")
                custom_dialogs.show_success("Επιτυχία", f"Η σύνδεση προστέθηκε με επιτυχία!")
            
            dialog.destroy()
            self.load_relationships()
            
        except Exception as e:
            custom_dialogs.show_error("Σφάλμα", f"Αποτυχία σύνδεσης: {str(e)}")

    def remove_relationship(self, task, item_type):
        """Remove current task from chain"""

        result = custom_dialogs.ask_yes_no(
            "Επιβεβαίωση Αφαίρεσης",
            "Είστε σίγουροι ότι θέλετε να αφαιρέσετε αυτή την εργασία από την αλυσίδα?\n\n"
            "Η εργασία θα παραμείνει ενεργή αλλά θα αποσυνδεθεί."
        )

        if result:
            try:
                current_id = self.task_data['id']

                # ✅ ΝΕΟ:  Χρήση του remove_task_from_chain με bypass logic!
                database.remove_task_from_chain(current_id)

                custom_dialogs.show_success("Επιτυχία", "Η εργασία αφαιρέθηκε από την αλυσίδα!")
                self.refresh_callback()
            except Exception as e:
                custom_dialogs.show_error("Σφάλμα", f"Αποτυχία αφαίρεσης: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# LOCATIONS MANAGEMENT COMPONENT
# ═══════════════════════════════════════════════════════════════════════════

