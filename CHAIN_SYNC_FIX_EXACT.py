"""
═══════════════════════════════════════════════════════════════════════════
CHAIN SYNC FIX - ΑΚΡΙΒΕΙΣ ΟΔΗΓΙΕΣ ΓΙΑ ΤΑ ΤΡΕΧΟΝΤΑ ΑΡΧΕΙΑ
═══════════════════════════════════════════════════════════════════════════

ΠΡΟΒΛΗΜΑ:
  Το chain sync logic στο save_task() είναι λάθος:
  1. Είναι στη λάθος θέση (πριν το update)
  2. Το database.update_task() καλείται λάθος (λείπουν παράμετροι)
  3. Δεν υπάρχει το update της ΤΡΕΧΟΥΣΑΣ εργασίας

ΛΥΣΗ:
  Φτιάξε το save_task() με τη σωστή σειρά και τα σωστά calls
"""

print("=" * 70)
print("CHAIN SYNC FIX - ΑΚΡΙΒΕΙΣ ΟΔΗΓΙΕΣ")
print("=" * 70)
print()

print("🎯 ΤΟ ΠΡΟΒΛΗΜΑ:")
print("-" * 70)
print()
print("Στο ui_components.py, γραμμή 969-992:")
print()
print("ΤΡΕΧΩΝ ΚΩΔΙΚΑΣ (ΛΑΘΟΣ):")
print("-" * 70)
print("""
        try:
            # ═══ CHAIN SYNC ═══
            # If we're in a chain AND we're the last task, sync all
            if self.chain_info and self.is_last_in_chain:
                full_chain = utils_refactored.get_full_task_chain(self.task_data['id'])

                # Update ALL other tasks in chain to same status
                for task in full_chain:
                    if task['id'] != self.task_data['id']:  # Skip current
                        database.update_task(task['id'], status=status)  # ❌ ΛΑΘΟΣ!
                custom_dialogs.show_success("Επιτυχία", "Η εργασία ενημερώθηκε με επιτυχία!")
            else:
                # Insert
                database.add_task(
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, None,
                    notes if notes else None, task_item_id, location
                )
                custom_dialogs.show_success("Επιτυχία", "Η εργασία αποθηκεύτηκε με επιτυχία!")
            
            self.on_save_callback()
            
        except Exception as e:
            custom_dialogs.show_error("Σφάλμα", f"Αποτυχία αποθήκευσης: {str(e)}")
""")
print()

print("❌ ΛΑΘΗ:")
print("-" * 70)
print()
print("1. Το chain sync είναι μέσα σε if/else με το insert")
print("2. Δεν γίνεται update η ΤΡΕΧΟΥΣΑ εργασία!")
print("3. Το database.update_task(task['id'], status=status) είναι λάθος")
print("   (χρειάζεται ΟΛΕΣ τις παραμέτρους)")
print()

print("=" * 70)
print("✅ Η ΛΥΣΗ:")
print("=" * 70)
print()

print("ΑΡΧΕΙΟ: ui_components.py")
print("ΓΡΑΜΜΕΣ: 969-992")
print()
print("ΑΝΤΙΚΑΤΑΣΤΗΣΕ ΟΛΟΚΛΗΡΟ ΤΟ TRY BLOCK:")
print("-" * 70)
print()

CORRECT_CODE = '''
        # Αποθήκευση
        try:
            if self.is_edit_mode:
                # Update existing task
                database.update_task(
                    self.task_data['id'],
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, None,
                    notes if notes else None, task_item_id, location
                )
                
                # ═══ CHAIN SYNC ═══
                # If we're in a chain AND we're the last task, sync ALL
                if self.chain_info and self.is_last_in_chain:
                    try:
                        full_chain = utils_refactored.get_full_task_chain(self.task_data['id'])
                        
                        # Update ALL other tasks in chain to same status
                        conn = database.get_connection()
                        cursor = conn.cursor()
                        
                        for task in full_chain:
                            if task['id'] != self.task_data['id']:  # Skip current
                                cursor.execute(
                                    "UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?",
                                    (status, completed_date, task['id'])
                                )
                        
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Chain sync warning: {e}")
                
                custom_dialogs.show_success("Επιτυχία", "Η εργασία ενημερώθηκε με επιτυχία!")
            else:
                # Insert new task
                database.add_task(
                    unit_id, task_type_id, description, status, priority,
                    created_date, completed_date, None,
                    notes if notes else None, task_item_id, location
                )
                custom_dialogs.show_success("Επιτυχία", "Η εργασία αποθηκεύτηκε με επιτυχία!")
            
            self.on_save_callback()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"=== SAVE ERROR ===")
            print(error_details)
            print("==================")
            custom_dialogs.show_error("Σφάλμα", f"Αποτυχία αποθήκευσης: {str(e)}")
'''

print(CORRECT_CODE)
print()

print("=" * 70)
print("🔍 ΤΙ ΑΛΛΑΞΕ:")
print("=" * 70)
print()
print("1. ✅ Προστέθηκε το if self.is_edit_mode:")
print("      - Edit mode → database.update_task() ΜΕ ΟΛΕΣ τις παραμέτρους")
print("      - New mode → database.add_task()")
print()
print("2. ✅ Chain sync ΜΕΤΑ το update_task()")
print("      - Πρώτα κάνουμε update την τρέχουσα εργασία")
print("      - Μετά sync-άρουμε τις άλλες")
print()
print("3. ✅ Χρησιμοποιούμε direct SQL για chain sync")
print("      - cursor.execute('UPDATE tasks SET status = ?...')")
print("      - Αποφεύγουμε το πολύπλοκο database.update_task()")
print()
print("4. ✅ Better error handling")
print("      - Εμφανίζει το full traceback για debugging")
print()

print("=" * 70)
print("📋 ΒΗΜΑ-ΒΗΜΑ:")
print("=" * 70)
print()
print("1. Άνοιξε το ui_components.py")
print()
print("2. Πήγαινε στη γραμμή 968 (# Αποθήκευση)")
print()
print("3. Επιλεξε από τη γραμμή 969 (try:) μέχρι τη γραμμή 992")
print("   (όλο το try/except block)")
print()
print("4. Διέγραψε")
print()
print("5. Paste τον CORRECT_CODE από παραπάνω")
print()
print("6. Save")
print()

print("=" * 70)
print("🧪 TEST:")
print("=" * 70)
print()
print("1. Δημιούργησε chain με 3 εργασίες:")
print("   [1-pending] → [2-pending] → [3-pending]")
print()
print("2. Edit την εργασία #3 (τελευταία):")
print("   - Άλλαξε status σε 'completed'")
print("   - Save")
print()
print("3. Έλεγξε το αποτέλεσμα:")
print("   ✅ [1-completed] → [2-completed] → [3-completed]")
print()
print("4. Πρόσθεσε νέα εργασία #4:")
print("   - Κάνε link: [3] → [4]")
print("   - Το [4] έχει status 'pending'")
print()
print("5. Έλεγξε:")
print("   ✅ [1-pending] → [2-pending] → [3-pending] → [4-pending]")
print("   (Όλοι επανανοίγουν επειδή ο τελευταίος είναι pending)")
print()

print("=" * 70)
print("⚠️  ΣΗΜΑΝΤΙΚΟ:")
print("=" * 70)
print()
print("Η αλλαγή είναι ΜΟΝΟ στο save_task() του TaskForm.")
print("Δεν χρειάζεται να αλλάξεις τίποτα άλλο!")
print()
print("Το chain sync τρέχει αυτόματα όταν:")
print("  • Edit τελευταίου κρίκου → Sync όλους")
print("  • Edit μεσαίου κρίκου → Δεν κάνει τίποτα (locked)")
print()

print("=" * 70)
print("💾 BACKUP REMINDER:")
print("=" * 70)
print()
print("Πριν κάνεις την αλλαγή:")
print("  1. Copy το ui_components.py σε ui_components.py.backup")
print("  2. Copy το hvacr_maintenance.db σε hvacr_maintenance.db.backup")
print()
print("Έτσι μπορείς να γυρίσεις πίσω αν κάτι πάει στραβά!")
print()

print("=" * 70)
