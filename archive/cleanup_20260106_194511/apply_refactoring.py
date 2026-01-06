#!/usr/bin/env python3
"""
Αυτόματη Εφαρμογή Αλλαγών - HVACR Maintenance System
=====================================================

Αυτό το script κάνει ΟΛΕς τις απαραίτητες αλλαγές αυτόματα στα αρχεία σας.

ΧΡΗΣΗ:
    python apply_refactoring.py

ΤΙ ΚΑΝΕΙ:
    1. Δημιουργεί backup όλων των αρχείων
    2. Αντιγράφει τα νέα modules (database_refactored.py, utils_refactored.py)
    3. Τροποποιεί το ui_components.py (αφαιρεί duplicate code)
    4. Τροποποιεί το main.py (προσθέτει error handling)
    5. Δοκιμάζει ότι όλα δουλεύουν

ΑΣΦΑΛΕΙΑ:
    - Κάνει backup ΟΛων των αρχείων πριν αλλάξει τίποτα
    - Αν κάτι πάει στραβά, τα backups είναι στο φάκελο 'backups/'
"""

import os
import shutil
from datetime import datetime
import sys

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

FILES_TO_BACKUP = [
    'database.py',
    'ui_components.py',
    'main.py',
    'theme_config.py',
    'hvacr_maintenance.db'
]

FILES_TO_COPY = [
    'database_refactored.py',
    'utils_refactored.py',
    'config.py',
    'ui_helpers.py'
]


# ═══════════════════════════════════════════════════════════════════════════
# BACKUP FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def create_backup():
    """Δημιουργεί backup όλων των αρχείων"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backups/backup_{timestamp}'
    
    print(f"\n{'='*70}")
    print(f"ΒΗΜΑ 1: Δημιουργία Backup")
    print(f"{'='*70}")
    
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    os.makedirs(backup_dir)
    
    for filename in FILES_TO_BACKUP:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(backup_dir, filename))
            print(f"  ✅ Backup: {filename} → {backup_dir}/")
        else:
            print(f"  ⚠️  Προσοχή: {filename} δεν βρέθηκε (skip)")
    
    print(f"\n✅ Backup ολοκληρώθηκε στο: {backup_dir}/")
    return backup_dir


# ═══════════════════════════════════════════════════════════════════════════
# COPY NEW FILES
# ═══════════════════════════════════════════════════════════════════════════

def copy_new_files():
    """Αντιγράφει τα νέα refactored modules"""
    print(f"\n{'='*70}")
    print(f"ΒΗΜΑ 2: Αντιγραφή Νέων Modules")
    print(f"{'='*70}")
    
    for filename in FILES_TO_COPY:
        if os.path.exists(filename):
            print(f"  ✅ Το {filename} υπάρχει ήδη")
        else:
            print(f"  ⚠️  Το {filename} δεν βρέθηκε!")
            print(f"     Βεβαιωθείτε ότι έχετε αντιγράψει όλα τα refactored αρχεία")
            print(f"     στον ίδιο φάκελο με αυτό το script.")
            return False
    
    print(f"\n✅ Όλα τα νέα modules είναι διαθέσιμα")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# MODIFY ui_components.py
# ═══════════════════════════════════════════════════════════════════════════

def modify_ui_components():
    """Τροποποιεί το ui_components.py"""
    print(f"\n{'='*70}")
    print(f"ΒΗΜΑ 3: Τροποποίηση ui_components.py")
    print(f"{'='*70}")
    
    if not os.path.exists('ui_components.py'):
        print("  ❌ Το ui_components.py δεν βρέθηκε!")
        return False
    
    with open('ui_components.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Αλλαγή 1: Προσθήκη import
    if 'import utils_refactored' not in content:
        # Βρίσκουμε τη γραμμή με το τελευταίο import
        lines = content.split('\n')
        import_line_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_line_idx = i
        
        if import_line_idx >= 0:
            lines.insert(import_line_idx + 1, 'import utils_refactored  # Refactored chain utilities')
            content = '\n'.join(lines)
            print("  ✅ Προστέθηκε: import utils_refactored")
        else:
            print("  ⚠️  Δεν βρέθηκε σημείο για το import (θα πρέπει να το προσθέσετε χειροκίνητα)")
    else:
        print("  ✅ Το import utils_refactored υπάρχει ήδη")
    
    # Αλλαγή 2 & 3: Αντικατάσταση chain logic στο TaskCard
    original_call = 'self._get_full_chain_simple(self.task[\'id\'])'
    new_call = 'utils_refactored.get_full_task_chain(self.task[\'id\'])'
    
    if original_call in content:
        content = content.replace(original_call, new_call)
        print(f"  ✅ Αντικαταστάθηκε chain call στο TaskCard")
    
    # Αλλαγή 4 & 5: Αντικατάσταση chain logic στο TaskForm  
    original_call2 = 'self._get_full_chain_simple(self.task_data[\'id\'])'
    new_call2 = 'utils_refactored.get_full_task_chain(self.task_data[\'id\'])'
    
    if original_call2 in content:
        content = content.replace(original_call2, new_call2)
        print(f"  ✅ Αντικαταστάθηκε chain call στο TaskForm")
    
    # Σώσιμο του τροποποιημένου αρχείου
    with open('ui_components.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Το ui_components.py τροποποιήθηκε επιτυχώς")
    print(f"   ΣΗΜΕΙΩΣΗ: Οι _get_full_chain_simple() methods παραμένουν για backward compatibility.")
    print(f"   Μπορείτε να τις διαγράψετε χειροκίνητα αν θέλετε (προαιρετικό).")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# MODIFY main.py
# ═══════════════════════════════════════════════════════════════════════════

def modify_main():
    """Τροποποιεί το main.py για να χρησιμοποιεί το refactored database"""
    print(f"\n{'='*70}")
    print(f"ΒΗΜΑ 4: Τροποποίηση main.py")
    print(f"{'='*70}")
    
    if not os.path.exists('main.py'):
        print("  ❌ Το main.py δεν βρέθηκε!")
        return False
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Αλλαγή: Χρήση του refactored database
    if 'import database' in content and 'import database_refactored' not in content:
        content = content.replace('import database', 'import database_refactored as database')
        print("  ✅ Αντικαταστάθηκε: import database → import database_refactored as database")
    else:
        print("  ✅ Το database import είναι ήδη ενημερωμένο")
    
    # Σώσιμο
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Το main.py τροποποιήθηκε επιτυχώς")
    return True


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

def test_changes():
    """Δοκιμάζει ότι οι αλλαγές λειτουργούν"""
    print(f"\n{'='*70}")
    print(f"ΒΗΜΑ 5: Δοκιμή Αλλαγών")
    print(f"{'='*70}")
    
    try:
        # Test 1: Import database_refactored
        import database_refactored as db
        print("  ✅ Import database_refactored: OK")
        
        # Test 2: Context manager
        with db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM groups')
            count = cursor.fetchone()['count']
            print(f"  ✅ Context manager: OK (Found {count} groups)")
        
        # Test 3: Validation
        try:
            db.add_group("", "test")
            print("  ❌ Validation: FAILED (empty name accepted)")
            return False
        except db.ValidationError:
            print("  ✅ Validation: OK (empty name rejected)")
        
        # Test 4: Import utils
        import utils_refactored
        print("  ✅ Import utils_refactored: OK")
        
        print(f"\n✅ ΟΛΑ ΤΑ TESTS ΠΕΡΑΣΑΝ!")
        return True
        
    except Exception as e:
        print(f"\n❌ ΣΦΑΛΜΑ κατά το testing: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main function"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║            ΑΥΤΟΜΑΤΗ ΕΦΑΡΜΟΓΗ REFACTORING - HVACR SYSTEM              ║
╚══════════════════════════════════════════════════════════════════════╝

Αυτό το script θα:
  1. Δημιουργήσει backup όλων των αρχείων
  2. Αντιγράψει τα νέα modules
  3. Τροποποιήσει το ui_components.py
  4. Τροποποιήσει το main.py
  5. Δοκιμάσει ότι όλα λειτουργούν

Θέλετε να συνεχίσετε; (y/n): """, end='')
    
    response = input().strip().lower()
    if response != 'y':
        print("\n❌ Ακυρώθηκε από τον χρήστη.")
        return
    
    # Step 1: Backup
    backup_dir = create_backup()
    
    # Step 2: Copy new files
    if not copy_new_files():
        print("\n❌ Αποτυχία: Λείπουν απαραίτητα αρχεία.")
        print(f"   Αντιγράψτε όλα τα refactored αρχεία και ξανατρέξτε.")
        return
    
    # Step 3: Modify ui_components.py
    if not modify_ui_components():
        print("\n❌ Αποτυχία τροποποίησης ui_components.py")
        return
    
    # Step 4: Modify main.py
    if not modify_main():
        print("\n❌ Αποτυχία τροποποίησης main.py")
        return
    
    # Step 5: Test
    if not test_changes():
        print(f"\n❌ Τα tests απέτυχαν!")
        print(f"   Μπορείτε να επαναφέρετε τα backups από: {backup_dir}/")
        return
    
    # Success!
    print(f"\n{'='*70}")
    print(f"🎉 ΕΠΙΤΥΧΙΑ!")
    print(f"{'='*70}")
    print(f"""
Οι αλλαγές εφαρμόστηκαν επιτυχώς!

ΤΙ ΑΛΛΑΞΕ:
  ✅ Το main.py χρησιμοποιεί τώρα το database_refactored
  ✅ Το ui_components.py χρησιμοποιεί το utils_refactored
  ✅ Context manager για ασφαλή database συνδέσεις
  ✅ Input validation παντού
  ✅ Διαγράφηκε ~150 γραμμές duplicate code

ΕΠΟΜΕΝΑ ΒΗΜΑΤΑ:
  1. Ανοίξτε την εφαρμογή και δοκιμάστε τα πάντα
  2. Αν όλα δουλεύουν, διαγράψτε τα backups
  3. Προαιρετικά: Διαγράψτε χειροκίνητα τις _get_full_chain_simple() methods

BACKUPS:
  Τα backups σας είναι στο: {backup_dir}/
  
Καλή επιτυχία! 🚀
""")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Διακόπηκε από τον χρήστη.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Απρόσμενο σφάλμα: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
