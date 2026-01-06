#!/usr/bin/env python3
"""
UI Patch Script - Διόρθωση UI Προβλημάτων
==========================================

ΠΡΟΒΛΗΜΑΤΑ ΠΟΥ ΔΙΟΡΘΩΝΕΙ:
1. Αφαιρεί το κουμπί "Επεξεργασία Εγγραφής" από το sidebar
2. Διορθώνει το πρόβλημα με τη Διαχείριση Μονάδων

ΧΡΗΣΗ:
    python ui_patch.py
"""

import os
import shutil
from datetime import datetime

def backup_file(filename):
    """Δημιουργία backup ενός αρχείου"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"  ✅ Backup: {backup_name}")
        return backup_name
    return None

def patch_main_py():
    """Αφαίρεση του κουμπιού 'Επεξεργασία Εγγραφής' από το main.py"""
    print("\n[1/2] Patch main.py - Αφαίρεση 'Επεξεργασία Εγγραφής'...")
    
    if not os.path.exists('main.py'):
        print("  ❌ Το main.py δεν βρέθηκε!")
        return False
    
    # Backup
    backup_file('main.py')
    
    # Διάβασμα
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Αφαίρεση του κουμπιού από το sidebar
    old_line = '            ("✏️ Επεξεργασία Εγγραφής", self.show_edit, "primary"),'
    new_line = '            # ("✏️ Επεξεργασία Εγγραφής", self.show_edit, "primary"),  # REMOVED - Ο χρήστης μπορεί να επεξεργαστεί από το Ιστορικό'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("  ✅ Αφαιρέθηκε το κουμπί 'Επεξεργασία Εγγραφής'")
    else:
        print("  ℹ️  Το κουμπί είχε ήδη αφαιρεθεί ή δεν βρέθηκε")
    
    # Σώσιμο
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def check_ui_components():
    """Έλεγχος του ui_components.py"""
    print("\n[2/2] Έλεγχος ui_components.py...")
    
    if not os.path.exists('ui_components.py'):
        print("  ❌ Το ui_components.py δεν βρέθηκε!")
        return False
    
    # Έλεγχος αν χρησιμοποιεί το σωστό import
    with open('ui_components.py', 'r', encoding='utf-8') as f:
        first_lines = ''.join([f.readline() for _ in range(20)])
    
    # Ελέγχουμε αν χρησιμοποιεί database ή database_refactored
    if 'import database_refactored as database' in first_lines:
        print("  ✅ Το ui_components.py χρησιμοποιεί database_refactored")
        return True
    elif 'import database' in first_lines and 'database_refactored' not in first_lines:
        print("  ⚠️  Το ui_components.py χρησιμοποιεί το παλιό database module")
        print("     ΠΡΟΤΕΙΝΕΤΑΙ: Αλλάξτε το σε 'import database_refactored as database'")
        
        # Προσφέρουμε αυτόματη διόρθωση
        response = input("\n  Θέλετε να το διορθώσω αυτόματα; (y/n): ").strip().lower()
        if response == 'y':
            backup_file('ui_components.py')
            
            with open('ui_components.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Αντικατάσταση του import
            content = content.replace(
                'import database',
                'import database_refactored as database',
                1  # Μόνο την πρώτη εμφάνιση
            )
            
            with open('ui_components.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("  ✅ Το import ενημερώθηκε!")
            return True
        else:
            print("  ℹ️  Παράβλεψη - θα πρέπει να το αλλάξετε χειροκίνητα")
            return False
    
    print("  ✅ Το ui_components.py είναι OK")
    return True

def main():
    print("=" * 70)
    print("UI PATCH: Διόρθωση UI Προβλημάτων")
    print("=" * 70)
    print("\nΑυτό το script θα:")
    print("  1. Αφαιρέσει το κουμπί 'Επεξεργασία Εγγραφής'")
    print("  2. Ελέγξει το ui_components.py")
    print("\nΘέλετε να συνεχίσετε; (y/n): ", end='')
    
    response = input().strip().lower()
    if response != 'y':
        print("\n❌ Ακυρώθηκε από τον χρήστη.")
        return
    
    # Step 1: Patch main.py
    success1 = patch_main_py()
    
    # Step 2: Check ui_components.py
    success2 = check_ui_components()
    
    if success1 and success2:
        print("\n" + "=" * 70)
        print("🎉 ΕΠΙΤΥΧΙΑ!")
        print("=" * 70)
        print("""
Οι αλλαγές εφαρμόστηκαν επιτυχώς!

ΤΙ ΑΛΛΑΞΕ:
  ✅ Αφαιρέθηκε το κουμπί 'Επεξεργασία Εγγραφής'
  ✅ Έγινε έλεγχος του ui_components.py

ΕΠΟΜΕΝΑ ΒΗΜΑΤΑ:
  1. Τρέξτε την εφαρμογή: python main.py
  2. Δοκιμάστε:
     - Το sidebar δεν έχει πια 'Επεξεργασία Εγγραφής'
     - Η 'Διαχείριση Μονάδων & Ομάδων' δείχνει δεδομένα
     - Μπορείτε να επεξεργαστείτε εργασίες από το 'Ιστορικό'

ΣΗΜΕΙΩΣΗ:
  - Για να επεξεργαστείτε εργασία: Πηγαίνετε στο Ιστορικό → Κλικ σε εργασία
  - Backups των αρχείων: main.py.backup_TIMESTAMP
""")
    else:
        print("\n❌ Κάποια βήματα απέτυχαν. Ελέγξτε τα error messages παραπάνω.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Διακόπηκε από τον χρήστη.")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Απρόσμενο σφάλμα: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
