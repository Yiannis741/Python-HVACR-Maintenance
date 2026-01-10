"""
Recycle Bin View Component
===========================
Κάδος Ανακύκλωσης - Διαγραμμένες εργασίες

Extracted από ui_components.py για καλύτερη οργάνωση.
"""

import customtkinter as ctk
from datetime import datetime
import database_refactored as database
import theme_config
import custom_dialogs
import utils_refactored
from .task_card import TaskCard

class RecycleBinView(ctk.CTkFrame):
    """
    Recycle Bin view - lists soft-deleted tasks with options to Restore or Permanently Delete.
    Uses compact, less-dangerous Delete button (small, with confirmation).
    """

    def __init__(self, parent, on_change_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.theme = theme_config.get_current_theme()

        self.pack(fill="both", expand=True, padx=40, pady=10)

        # Header
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=self.theme["bg_secondary"])
        header_frame.pack(fill="x", pady=(0, 12))
        header_frame.pack_propagate(False)
        header_frame.configure(height=60)

        title = ctk.CTkLabel(
            header_frame,
            text="🗑️ Κάδος Ανακύκλωσης - Διαγραμμένες Εργασίες",
            font=theme_config.get_font("title", "bold"),
            text_color=self.theme["accent_blue"]
        )
        title.pack(side="left", padx=15)

        info = ctk.CTkLabel(
            header_frame,
            text="Εδώ μπορείτε να επαναφέρετε ή να διαγράψετε οριστικά εργασίες.",
            font=theme_config.get_font("small"),
            text_color=self.theme["text_secondary"]
        )
        info.pack(side="right", padx=15)

        # Scrollable list container
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=(8, 0))

        # Load content
        self.load_deleted_tasks()

    def _make_button(self, parent, text, command, style_type="primary", width=100, height=32):
        """
        Small helper to create buttons using theme_config.get_button_style safely.
        Avoids passing duplicate keyword args that cause CTkButton TypeError.
        """
        style = theme_config.get_button_style(style_type) or {}
        # Ensure we don't accidentally pass duplicates of common args
        # We'll pass style dict entirely and also provide width/height/text/command explicitly.
        btn = ctk.CTkButton(parent, text=text, command=command, width=width, height=height, **style)
        return btn

    def load_deleted_tasks(self):
        """Load soft-deleted tasks from DB and render them."""
        # Clear list
        for w in self.list_frame.winfo_children():
            w.destroy()

        deleted = database.get_deleted_tasks()

        if not deleted:
            empty_lbl = ctk.CTkLabel(
                self.list_frame,
                text="Δεν υπάρχουν διαγραμμένες εργασίες στον κάδο.",
                font=theme_config.get_font("body"),
                text_color=self.theme["text_secondary"]
            )
            empty_lbl.pack(pady=40)
            return

        # Count header
        count_lbl = ctk.CTkLabel(
            self.list_frame,
            text=f"Βρέθηκαν {len(deleted)} εργασίες στον κάδο",
            font=theme_config.get_font("body", "bold"),
            text_color=self.theme["accent_blue"]
        )
        count_lbl.pack(anchor="w", padx=8, pady=(8, 12))

        for task in deleted:
            self._render_deleted_task(task)

    def _render_deleted_task(self, task):
        """Render a single deleted task row with Restore + Delete buttons."""
        row = ctk.CTkFrame(self.list_frame, fg_color=self.theme["card_bg"],
                           border_color=self.theme["card_border"], border_width=1, corner_radius=8)
        row.pack(fill="x", padx=8, pady=6)

        # Left info: basic summary
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=8)

        title_text = f"#{task['id']}  •  {task['task_type_name']} — {task['unit_name']}"
        lbl_title = ctk.CTkLabel(left, text=title_text, font=theme_config.get_font("body", "bold"),
                                 text_color=self.theme["text_primary"], anchor="w")
        lbl_title.pack(fill="x")

        subtitle = task.get('task_item_name') or task.get('description') or ""
        lbl_sub = ctk.CTkLabel(left, text=f"{utils_refactored.format_date_for_display(task.get('created_date'))}  •  {subtitle}",
                               font=theme_config.get_font("small"), text_color=self.theme["text_secondary"], anchor="w")
        lbl_sub.pack(fill="x", pady=(3, 0))

        # Right actions: Restore + Permanent Delete (compact)
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="right", padx=12, pady=8)

        # Restore button (green/success)
        restore_cmd = lambda t=task: self._on_restore(t)
        restore_btn = self._make_button(actions, "Επαναφορά", restore_cmd, style_type="success", width=110, height=30)
        restore_btn.pack(side="right", padx=(6, 0))

        # Permanent delete button (small, danger). Confirm before deleting.
        delete_cmd = lambda t=task: self._on_permanent_delete(t)
        delete_btn = self._make_button(actions, "Διάγρ. Οριστικά", delete_cmd, style_type="danger", width=120, height=30)
        delete_btn.pack(side="right", padx=(0, 6))

    def _on_restore(self, task):
        """Restore a soft-deleted task."""
        # from tkinter import messagebox  # ← Replaced with custom dialogs
        import custom_dialogs
        result = custom_dialogs.ask_yes_no("Επαναφορά Εργασίας", f"Θέλετε να επαναφέρετε την εργασία #{task['id']};")
        if not result:
            return

        try:
            database.restore_task(task['id'])
        except Exception as e:
            custom_dialogs.show_error("Σφάλμα", f"Σφάλμα κατά την επαναφορά: {e}")
            return

        # refresh list and notify caller
        self.load_deleted_tasks()
        if callable(self.on_change_callback):
            self.on_change_callback()

    def _on_permanent_delete(self, task):
        """Permanently delete task after confirmation."""
        # from tkinter import messagebox  # ← Replaced with custom dialogs
        import custom_dialogs
        result = custom_dialogs.ask_yes_no(
            "Οριστική Διαγραφή",
            f"Η εργασία #{task['id']} θα διαγραφεί οριστικά. Η ενέργεια δεν μπορεί να αναιρεθεί.\n\nΘέλετε να συνεχίσετε?"
        )
        if not result:
            return

        try:
            database.permanent_delete_task(task['id'])
        except Exception as e:
            custom_dialogs.show_error("Σφάλμα", f"Σφάλμα κατά την οριστική διαγραφή: {e}")
            return

        # refresh list and notify caller
        self.load_deleted_tasks()
        if callable(self.on_change_callback):
            self.on_change_callback()




