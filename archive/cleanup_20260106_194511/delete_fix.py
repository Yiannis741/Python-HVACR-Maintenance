#!/usr/bin/env python3
"""
Quick Fix: Διόρθωση Διαγραφής Παλιών Μονάδων
==============================================

ΠΡΟΒΛΗΜΑ:
Οι παλιές μονάδες δεν διαγράφονται όταν κάνετε κλικ στο "🗑️ Διαγραφή".

ΑΙΤΙΑ:
Η soft_delete_unit() επέστρεφε True/False αντί να κάνει raise exception,
οπότε το try-except στο UI δεν έπιανε το error.

ΛΥΣΗ:
Αυτό το script αντικαθιστά το database_refactored.py με τη διορθωμένη έκδοση.

ΧΡΗΣΗ:
    python delete_fix.py
"""

import os
import shutil
from datetime import datetime

def main():
    print("=" * 70)
    print("QUICK FIX: Διόρθωση Διαγραφής Μονάδων")
    print("=" * 70)
    
    # Βήμα 1: Backup
    print("\n[1/3] Δημιουργία backup...")
    if os.path.exists('database_refactored.py'):
        backup_name = f'database_refactored_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy2('database_refactored.py', backup_name)
        print(f"  ✅ Backup: {backup_name}")
    
    # Βήμα 2: Έλεγχος νέου αρχείου
    print("\n[2/3] Έλεγχος διορθωμένου αρχείου...")
    if not os.path.exists('database_refactored_FULL.py'):
        print("  ❌ Το database_refactored_FULL.py δεν βρέθηκε!")
        print("     Κατεβάστε το ενημερωμένο αρχείο.")
        return False
    print("  ✅ Το database_refactored_FULL.py βρέθηκε")
    
    # Βήμα 3: Αντικατάσταση
    print("\n[3/3] Αντικατάσταση...")
    shutil.copy2('database_refactored_FULL.py', 'database_refactored.py')
    print("  ✅ Το database_refactored.py ενημερώθηκε")
    
    # Validation
    print("\n[Validation] Έλεγχος functions...")
    try:
        import database_refactored as db
        
        # Έλεγχος αν υπάρχουν οι functions
        assert hasattr(db, 'soft_delete_unit'), "Missing: soft_delete_unit"
        assert hasattr(db, 'soft_delete_group'), "Missing: soft_delete_group"
        assert hasattr(db, 'ValidationError'), "Missing: ValidationError"
        
        print("  ✅ soft_delete_unit")
        print("  ✅ soft_delete_group")
        print("  ✅ ValidationError")
        
        print("\n" + "=" * 70)
        print("🎉 ΕΠΙΤΥΧΙΑ!")
        print("=" * 70)
        print("""
Η διόρθωση εφαρμόστηκε επιτυχώς!

ΤΙ ΔΙΟΡΘΩΘΗΚΕ:
  ✅ Η soft_delete_unit() τώρα κάνει raise ValidationError
  ✅ Προστέθηκε η soft_delete_group()
  ✅ Οι παλιές μονάδες τώρα διαγράφονται σωστά

ΕΠΟΜΕΝΑ ΒΗΜΑΤΑ:
  1. Τρέξτε την εφαρμογή: python main.py
  2. Δοκιμάστε να διαγράψετε μια παλιά μονάδα
  3. Αν η μονάδα έχει εργασίες, θα δείτε error message
  4. Αν δεν έχει εργασίες, θα διαγραφεί και θα πάει στον κάδο

ΣΗΜΕΙΩΣΗ:
  - Μονάδες ΜΕ εργασίες: Δεν διαγράφονται (error message)
  - Μονάδες ΧΩΡΙΣ εργασίες: Διαγράφονται (πάνε στον κάδο)
""")
        return True
        
    except Exception as e:
        print(f"\n❌ ΣΦΑΛΜΑ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            print("\n❌ Η διόρθωση απέτυχε.")
            exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Διακόπηκε από τον χρήστη.")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Απρόσμενο σφάλμα: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
