"""
Task Card Component
===================
Καρτέλα εργασίας για προβολή - Compact Design με Link Indicators

Extracted από ui_components.py για καλύτερη οργάνωση.
"""

import customtkinter as ctk
import theme_config
import database_refactored as database
import utils_refactored


class TaskCard(ctk.CTkFrame):
    """Καρτέλα εργασίας για προβολή - Compact Design με Link Indicators"""

    def __init__(self, parent, task_data, on_click=None, show_relations=True):
        theme = theme_config.get_current_theme()
        super().__init__(
            parent,
            corner_radius=8,
            fg_color=theme["card_bg"],
            border_color=theme["card_border"],
            border_width=1,
            height=100
        )

        self.task = task_data
        self.on_click = on_click
        self.theme = theme
        self.show_relations = show_relations

        self.pack_propagate(False)

        self.create_card()

        # Clickable
        if on_click:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda e: on_click(task_data))

    def create_card(self):
        """Δημιουργία της καρτέλας - 3 Row Layout με Location - Theme Aware"""

        # Status & Priority colors
        status_color = self.theme["accent_green"] if self.task['status'] == 'completed' else self.theme["accent_orange"]
        status_icon = "✓" if self.task['status'] == 'completed' else "⏳"
        status_text = "Ολοκληρωμένη" if self.task['status'] == 'completed' else "Εκκρεμής"

        priority_colors = {
            "low": self.theme["accent_green"],
            "medium": self.theme["accent_orange"],
            "high": self.theme["accent_red"]
        }
        priority_color = priority_colors.get(self.task.get('priority', 'medium'), self.theme["accent_orange"])
        priority_icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        priority_icon = priority_icons.get(self.task.get('priority', 'medium'), "🟡")

        # ===== ROW 0: Μονάδα - Τοποθεσία - Ημερ/νία =====
        row0_frame = ctk.CTkFrame(self, fg_color="transparent")
        row0_frame.pack(fill="x", padx=12, pady=(8, 2))

        # Build text parts
        row0_parts = [f"📍 {self.task['unit_name']}"]

        if self.task.get('location'):
            row0_parts.append(f"🏢 {self.task['location']}")

        row0_parts.append(f"📅 {utils_refactored.format_date_for_display(self.task['created_date'])}")

        row0_text = " - ".join(row0_parts)

        row0_label = ctk.CTkLabel(
            row0_frame,
            text=row0_text,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        row0_label.pack(side="left", fill="x", expand=True)

        # ===== ROW 1: Τύπος Εργασίας - Είδος Εργασίας | Status | Priority =====
        row1_frame = ctk.CTkFrame(self, fg_color="transparent")
        row1_frame.pack(fill="x", padx=12, pady=2)

        # LEFT: Type and Item
        left_section = ctk.CTkFrame(row1_frame, fg_color="transparent")
        left_section.pack(side="left", fill="x", expand=True)

        type_text = f"🔧 {self.task['task_type_name']}"
        if self.task.get('task_item_name'):
            type_text += f" - {self.task['task_item_name']}"

        type_label = ctk.CTkLabel(
            left_section,
            text=type_text,
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        type_label.pack(side="left")

        # RIGHT: Priority + Status
        priority_label = ctk.CTkLabel(
            row1_frame,
            text=f"{priority_icon} {self.task.get('priority', 'medium').upper()}",
            font=theme_config.get_font("small", "bold"),
            text_color=priority_color
        )
        priority_label.pack(side="right", padx=(10, 0))

        status_label = ctk.CTkLabel(
            row1_frame,
            text=f"{status_icon} {status_text}",
            font=theme_config.get_font("small", "bold"),
            text_color=status_color
        )
        status_label.pack(side="right", padx=(0, 10))

        # ===== ROW 2: Chain • Περιγραφή =====
        row2_frame = ctk.CTkFrame(self, fg_color="transparent")
        row2_frame.pack(fill="x", padx=12, pady=(2, 8))

        # Chain indicator FIRST (if exists)
        # ✅ OPTIMIZED: Use utils_refactored instead of duplicate code
        if self.show_relations:
            full_chain = utils_refactored.get_full_task_chain(self.task['id'])
            if len(full_chain) > 1:
                position = next((i for i, t in enumerate(full_chain, 1) if t['id'] == self.task['id']), 1)
                chain_length = len(full_chain)

                chain_widget = ctk.CTkLabel(
                    row2_frame,
                    text=f"🔗 {position}/{chain_length}",
                    font=theme_config.get_font("small", "bold"),
                    text_color=self.theme["accent_blue"],
                    anchor="w"
                )
                chain_widget.pack(side="left", padx=(0, 5))

                # Separator
                ctk.CTkLabel(
                    row2_frame,
                    text="•",
                    font=theme_config.get_font("small"),
                    text_color=self.theme["text_disabled"]
                ).pack(side="left", padx=(0, 5))

        # Description
        desc_text = self.task['description'][:60] + "..." if len(self.task['description']) > 60 else self.task[
            'description']

        desc_label = ctk.CTkLabel(
            row2_frame,
            text=desc_text,
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"],
            anchor="w"
        )
        desc_label.pack(side="left", fill="x", expand=True)

        # Bind click to all widgets
        if self.on_click:
            task_ref = self.task

            widgets = [
                self, row0_frame, row0_label,
                row1_frame, left_section, type_label, priority_label, status_label,
                row2_frame, desc_label
            ]

            for widget in widgets:
                widget.configure(cursor="hand2")
                widget.bind("<Button-1>", lambda e, t=task_ref: self.on_click(t))
