#!/usr/bin/env python3
"""
Cleanup Script - Καθαρισμός Φακέλου Project
============================================

Αυτό το script καθαρίζει τον φάκελο από:
- Backup αρχεία (.backup_*, _backup_*)
- Fix scripts (hotfix_*, delete_fix.py, ui_patch.py, etc)
- Temporary/redundant αρχεία (database_refactored_FULL.py, etc)
- README αρχεία που δεν χρειάζονται πια

ΑΣΦΑΛΕΙΑ:
- Δείχνει ΤΙ θα διαγράψει ΠΡΙΝ το κάνει
- Ζητάει επιβεβαίωση
- Μετακινεί σε φάκελο "archive/" αντί να διαγράφει (safer)

ΧΡΗΣΗ:
    python cleanup_project.py
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Αρχεία που ΚΡΑΤAΜΕ (Core Project Files)
KEEP_FILES = {
    # Core Python files
    'main.py',
    'database_refactored.py',  # Το refactored (ΟΧΙ το _FULL)
    'ui_components.py',
    'theme_config.py',
    'utils_refactored.py',
    'config.py',
    'ui_helpers.py',
    
    # Database
    'hvacr_maintenance.db',
    
    # Git/Project files (αν υπάρχουν)
    '.gitignore',
    'README.md',
    'requirements.txt',
    
    # Python project files
    '__init__.py',
    'setup.py',
    'pyproject.toml',
}

# Patterns για αρχεία προς ΔΙΑΓΡΑΦΗ
DELETE_PATTERNS = [
    # Backup files
    '*.backup_*',
    '*_backup_*',
    '*.bak',
    
    # Fix/Patch scripts
    '*fix*.py',
    '*patch*.py',
    'hotfix*.py',
    'apply_refactoring.py',
    'test_new_db.py',
    'run_tests.py',
    
    # Redundant database files
    'database.py',  # Το παλιό (αν υπάρχει)
    'database_old.py',
    'database_refactored_FULL.py',  # Το FULL δεν χρειάζεται πια
    'database_improved.py',
    
    # README/Documentation που δεν χρειάζονται πια
    '*README*.md',
    '*GUIDE*.md',
    '*INSTRUCTIONS*.md',
    'HOTFIX*.md',
    'DELETE_FIX*.md',
    'ΔΙΑΓΝΩΣΗ*.md',
    'ΑΥΤΟΜΑΤΗ*.md',
    'MIGRATION*.md',
    
    # Temporary/Test files
    'test_*.py',
    'temp_*.py',
    '*_temp.py',
    
    # Analysis files (από το code review)
    'code_review*.md',
    'implementation*.md',
    'utils.py',  # Αν υπάρχει παλιό utils (όχι το utils_refactored)
    
    # Old UI helpers
    'ui_helpers_Version*.py',
]

# Φάκελοι προς ΔΙΑΓΡΑΦΗ
DELETE_FOLDERS = [
    'backups',
    '__pycache__',
    '*.egg-info',
    '.pytest_cache',
    'build',
    'dist',
]


# ═══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_files_to_delete():
    """Βρίσκει όλα τα αρχεία που θα διαγραφούν"""
    import fnmatch
    
    files_to_delete = []
    
    # Scan current directory
    for item in os.listdir('.'):
        # Skip directories (τα χειριζόμαστε ξεχωριστά)
        if os.path.isdir(item):
            continue
        
        # Skip core files
        if item in KEEP_FILES:
            continue
        
        # Check against delete patterns
        should_delete = False
        for pattern in DELETE_PATTERNS:
            if fnmatch.fnmatch(item, pattern):
                should_delete = True
                break
        
        if should_delete:
            files_to_delete.append(item)
    
    return sorted(files_to_delete)


def get_folders_to_delete():
    """Βρίσκει όλους τους φακέλους που θα διαγραφούν"""
    import fnmatch
    
    folders_to_delete = []
    
    for item in os.listdir('.'):
        if not os.path.isdir(item):
            continue
        
        # Check against delete patterns
        for pattern in DELETE_FOLDERS:
            if fnmatch.fnmatch(item, pattern):
                folders_to_delete.append(item)
                break
    
    return sorted(folders_to_delete)


def format_size(size_bytes):
    """Μορφοποίηση μεγέθους σε human-readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_size(filepath):
    """Επιστρέφει το μέγεθος ενός αρχείου"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0


def get_folder_size(folder):
    """Επιστρέφει το συνολικό μέγεθος ενός φακέλου"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total += get_file_size(filepath)
    except:
        pass
    return total


def archive_items(files, folders):
    """Μετακινεί αρχεία/φακέλους σε archive αντί να τα διαγράφει"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_dir = f'archive/cleanup_{timestamp}'
    
    if not files and not folders:
        return
    
    os.makedirs(archive_dir, exist_ok=True)
    
    print(f"\n📦 Μετακίνηση στο: {archive_dir}/")
    
    # Move files
    for file in files:
        try:
            shutil.move(file, os.path.join(archive_dir, file))
            print(f"  ✅ {file}")
        except Exception as e:
            print(f"  ❌ {file}: {e}")
    
    # Move folders
    for folder in folders:
        try:
            shutil.move(folder, os.path.join(archive_dir, folder))
            print(f"  ✅ {folder}/")
        except Exception as e:
            print(f"  ❌ {folder}/: {e}")


def delete_items(files, folders):
    """Διαγράφει αρχεία/φακέλους ΜΟΝΙΜΑ (επικίνδυνο!)"""
    print(f"\n🗑️  ΜΟΝΙΜΗ Διαγραφή...")
    
    # Delete files
    for file in files:
        try:
            os.remove(file)
            print(f"  ✅ {file}")
        except Exception as e:
            print(f"  ❌ {file}: {e}")
    
    # Delete folders
    for folder in folders:
        try:
            shutil.rmtree(folder)
            print(f"  ✅ {folder}/")
        except Exception as e:
            print(f"  ❌ {folder}/: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("CLEANUP: Καθαρισμός Φακέλου Project")
    print("=" * 70)
    
    # Scan
    files_to_delete = get_files_to_delete()
    folders_to_delete = get_folders_to_delete()
    
    if not files_to_delete and not folders_to_delete:
        print("\n✨ Ο φάκελος είναι ήδη καθαρός! Δεν βρέθηκαν περιττά αρχεία.")
        return
    
    # Display files
    print(f"\n📄 ΑΡΧΕΙΑ ΓΙΑ ΔΙΑΓΡΑΦΗ ({len(files_to_delete)}):")
    print("-" * 70)
    
    total_file_size = 0
    for file in files_to_delete:
        size = get_file_size(file)
        total_file_size += size
        print(f"  • {file:<50} {format_size(size):>10}")
    
    # Display folders
    if folders_to_delete:
        print(f"\n📁 ΦΑΚΕΛΟΙ ΓΙΑ ΔΙΑΓΡΑΦΗ ({len(folders_to_delete)}):")
        print("-" * 70)
        
        total_folder_size = 0
        for folder in folders_to_delete:
            size = get_folder_size(folder)
            total_folder_size += size
            print(f"  • {folder:<50} {format_size(size):>10}")
    else:
        total_folder_size = 0
    
    # Summary
    total_size = total_file_size + total_folder_size
    total_items = len(files_to_delete) + len(folders_to_delete)
    
    print(f"\n" + "=" * 70)
    print(f"ΣΥΝΟΛΟ: {total_items} items, {format_size(total_size)}")
    print("=" * 70)
    
    # Options
    print(f"\nΕΠΙΛΟΓΕΣ:")
    print("  [1] Μετακίνηση σε archive/ (ΑΣΦΑΛΕΣ - Συνιστάται)")
    print("  [2] Μόνιμη διαγραφή (ΕΠΙΚΙΝΔΥΝΟ - Δεν μπορεί να επαναφερθεί)")
    print("  [3] Ακύρωση")
    
    choice = input("\nΕπιλογή (1/2/3): ").strip()
    
    if choice == '1':
        # Archive (safe)
        print("\n📦 Μετακίνηση σε archive (ασφαλές)...")
        archive_items(files_to_delete, folders_to_delete)
        
        print("\n" + "=" * 70)
        print("✅ ΟΛΟΚΛΗΡΩΘΗΚΕ!")
        print("=" * 70)
        print(f"""
Τα αρχεία μετακινήθηκαν στο archive/.

ΤΙ ΕΓΙΝΕ:
  • {len(files_to_delete)} αρχεία μετακινήθηκαν
  • {len(folders_to_delete)} φάκελοι μετακινήθηκαν
  • Συνολικό μέγεθος: {format_size(total_size)}

Ο φάκελος σας είναι τώρα καθαρός!

ΣΗΜΕΙΩΣΗ:
  - Τα αρχεία είναι στο archive/cleanup_TIMESTAMP/
  - Μπορείτε να τα επαναφέρετε αν χρειαστεί
  - Μπορείτε να διαγράψετε το archive/ αργότερα με ασφάλεια
""")
    
    elif choice == '2':
        # Permanent delete (dangerous)
        print("\n⚠️  ΠΡΟΣΟΧΗ: ΜΟΝΙΜΗ ΔΙΑΓΡΑΦΗ!")
        print("Τα αρχεία ΔΕΝ θα μπορούν να επαναφερθούν!")
        confirm = input("\nΕίστε ΣΙΓΟΥΡΟΙ; Πληκτρολογήστε 'DELETE' για επιβεβαίωση: ").strip()
        
        if confirm == 'DELETE':
            delete_items(files_to_delete, folders_to_delete)
            
            print("\n" + "=" * 70)
            print("✅ ΟΛΟΚΛΗΡΩΘΗΚΕ!")
            print("=" * 70)
            print(f"""
Τα αρχεία διαγράφηκαν ΜΟΝΙΜΑ.

ΤΙ ΕΓΙΝΕ:
  • {len(files_to_delete)} αρχεία διαγράφηκαν
  • {len(folders_to_delete)} φάκελοι διαγράφηκαν
  • Ελευθερώθηκε χώρος: {format_size(total_size)}

Ο φάκελος σας είναι τώρα καθαρός!
""")
        else:
            print("\n❌ Ακυρώθηκε - Δεν πληκτρολογήθηκε 'DELETE'")
    
    elif choice == '3':
        print("\n❌ Ακυρώθηκε από τον χρήστη.")
    
    else:
        print("\n❌ Μη έγκυρη επιλογή.")


if __name__ == '__main__':
    try:
        # Έλεγχος ότι είμαστε στο σωστό directory
        if not os.path.exists('main.py'):
            print("❌ ΣΦΑΛΜΑ: Δεν βρέθηκε το main.py")
            print("   Τρέξτε αυτό το script από τον φάκελο του project σας.")
            exit(1)
        
        main()
        
    except KeyboardInterrupt:
        print("\n\n❌ Διακόπηκε από τον χρήστη.")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Απρόσμενο σφάλμα: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
