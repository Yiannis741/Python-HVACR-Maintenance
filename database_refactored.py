"""
Database module - Διαχείριση SQLite database - Phase 2 (Refactored)
Βελτιώσεις: Context Manager, Input Validation, Better Error Handling
"""

import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import os

DB_NAME = "hvacr_maintenance.db"


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS (ΝΕΟ!)
# ═══════════════════════════════════════════════════════════════════════════

class DatabaseError(Exception):
    """Custom exception για database errors"""
    pass


class ValidationError(Exception):
    """Custom exception για validation errors"""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION MANAGEMENT (ΝΕΟ! - ΠΡΟΤΕΙΝΕΤΑΙ)
# ═══════════════════════════════════════════════════════════════════════════

@contextmanager
def get_db_connection():
    """
    Context manager για ασφαλή διαχείριση database συνδέσεων.
    
    Οφέλη:
        - Αυτόματο commit on success
        - Αυτόματο rollback on error
        - Αυτόματο close της σύνδεσης
        - Thread-safe
    
    Χρήση:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
            return cursor.fetchall()
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION HELPERS (ΝΕΟ!)
# ═══════════════════════════════════════════════════════════════════════════

def validate_not_empty(value: str, field_name: str) -> str:
    """Validates ότι ένα string δεν είναι κενό"""
    if not value or not value.strip():
        raise ValidationError(f"Το πεδίο '{field_name}' δεν μπορεί να είναι κενό")
    return value.strip()


def validate_string_length(value: str, field_name: str, min_length: int = 0, 
                          max_length: Optional[int] = None) -> str:
    """Validates το μήκος ενός string"""
    value = value.strip()
    
    if len(value) < min_length:
        raise ValidationError(
            f"Το πεδίο '{field_name}' πρέπει να έχει τουλάχιστον {min_length} χαρακτήρες"
        )
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"Το πεδίο '{field_name}' δεν μπορεί να υπερβαίνει τους {max_length} χαρακτήρες"
        )
    
    return value


# ═══════════════════════════════════════════════════════════════════════════
# ORIGINAL FUNCTIONS (Κρατάμε ΟΛΑ για backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════

"""
Database module - Διαχείριση SQLite database - Phase 2
"""

import sqlite3
from datetime import datetime, timedelta
import os

DB_NAME = "hvacr_maintenance.db"


def get_connection():
    """Δημιουργία σύνδεσης με τη database"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Αρχικοποίηση της database με τους πίνακες"""

    conn = get_connection()
    cursor = conn.cursor()

    # Πίνακας Ομάδων Μονάδων
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS groups
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       description
                       TEXT,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # Πίνακας Μονάδων
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS units
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL,
                       group_id
                       INTEGER
                       NOT
                       NULL,
                       location
                       TEXT,
                       model
                       TEXT,
                       serial_number
                       TEXT,
                       installation_date
                       DATE,
                       is_active
                       BOOLEAN
                       DEFAULT
                       1,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       group_id
                   ) REFERENCES groups
                   (
                       id
                   )
                       )
                   ''')

    # Πίνακας Ειδών Εργασιών
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS task_types
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       description
                       TEXT,
                       is_predefined
                       BOOLEAN
                       DEFAULT
                       0,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # Πίνακας Ειδών Εργασιών (Task Items) - Phase 2. 3
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS task_items
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL,
                       task_type_id
                       INTEGER
                       NOT
                       NULL,
                       description
                       TEXT,
                       is_active
                       BOOLEAN
                       DEFAULT
                       1,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       task_type_id
                   ) REFERENCES task_types
                   (
                       id
                   ),
                       UNIQUE
                   (
                       name,
                       task_type_id
                   )
                       )
                   ''')

    # Πίνακας Εργασιών
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS tasks
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       unit_id
                       INTEGER
                       NOT
                       NULL,
                       task_type_id
                       INTEGER
                       NOT
                       NULL,
                       description
                       TEXT
                       NOT
                       NULL,
                       status
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       status
                       IN
                   (
                       'pending',
                       'completed'
                   )),
                       priority TEXT CHECK
                   (
                       priority
                       IN
                   (
                       'low',
                       'medium',
                       'high'
                   )),
                       created_date DATE NOT NULL,
                       completed_date DATE,
                       technician_name TEXT,
                       notes TEXT,
                       is_deleted BOOLEAN DEFAULT 0,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       unit_id
                   ) REFERENCES units
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       task_type_id
                   ) REFERENCES task_types
                   (
                       id
                   )
                       )
                   ''')

    # Migration:  Add task_item_id column if it doesn't exist
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'task_item_id' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN task_item_id INTEGER REFERENCES task_items(id)')
        # Migration: Add location column if it doesn't exist
    if 'location' not in columns:
        cursor.execute('ALTER TABLE tasks ADD COLUMN location TEXT')

    # Πίνακας Συνδέσεων Εργασιών (π.χ.  Βλάβη → Επισκευή)
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS task_relationships
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       parent_task_id
                       INTEGER
                       NOT
                       NULL,
                       child_task_id
                       INTEGER
                       NOT
                       NULL,
                       relationship_type
                       TEXT,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       parent_task_id
                   ) REFERENCES tasks
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       child_task_id
                   ) REFERENCES tasks
                   (
                       id
                   )
                       )
                   ''')

    # ═══════════════════════════════════════════════════════════
    # Migration: ADD is_deleted COLUMN to task_relationships
    # ═══════════════════════════════════════════════════════════
    cursor.execute("PRAGMA table_info(task_relationships)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'is_deleted' not in columns:
        cursor.execute('ALTER TABLE task_relationships ADD COLUMN is_deleted INTEGER DEFAULT 0')
        print("✅ Added is_deleted column to task_relationships")

    conn.commit()
    conn.close()


def load_default_task_items():
    """Φόρτωση προκαθορισμένων ειδών εργασιών - Phase 2.3"""

    conn = get_connection()
    cursor = conn.cursor()

    # Έλεγχος αν υπάρχουν ήδη δεδομένα
    cursor.execute("SELECT COUNT(*) as count FROM task_items")
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return

    # Παίρνουμε τα IDs των τύπων εργασιών
    cursor.execute("SELECT id, name FROM task_types WHERE is_predefined = 1")
    task_types = {row['name']: row['id'] for row in cursor.fetchall()}

    # Προκαθορισμένα είδη ανά τύπο
    task_items = {
        'Service': [
            ('Ετήσιο Service', 'Πλήρης ετήσια συντήρηση'),
            ('Εξαμηνιαίο Service', 'Συντήρηση κάθε 6 μήνες'),
            ('Τριμηνιαίο Service', 'Συντήρηση κάθε 3 μήνες'),
            ('Μηνιαίο Service', 'Μηνιαία συντήρηση'),
            ('Καθαρισμός Φίλτρων', 'Αφαίρεση και καθαρισμός φίλτρων'),
            ('Έλεγχος Ψυκτικού Υγρού', 'Έλεγχος στάθμης και πιέσεων'),
            ('Καθαρισμός Εσωτερικών Στοιχείων', 'Καθαρισμός εσωτερικών μονάδων'),
            ('Καθαρισμός Εξωτερικών Στοιχείων', 'Καθαρισμός εξωτερικών μονάδων'),
            ('Έλεγχος Πιέσεων', 'Μέτρηση και έλεγχος πιέσεων συστήματος'),
        ],
        'Βλάβη': [
            ('Διαρροή Ψυκτικού', 'Διαρροή ψυκτικού υγρού'),
            ('Πρόβλημα Compressor', 'Βλάβη συμπιεστή'),
            ('Πρόβλημα Ανεμιστήρα Εσωτερικού', 'Βλάβη ανεμιστήρα εσωτερικής μονάδας'),
            ('Πρόβλημα Ανεμιστήρα Εξωτερικού', 'Βλάβη ανεμιστήρα εξωτερικής μονάδας'),
            ('Μη Λειτουργία', 'Η μονάδα δεν λειτουργεί'),
            ('Θόρυβος Λειτουργίας', 'Ασυνήθιστοι θόρυβοι'),
            ('Πρόβλημα Πλακέτας', 'Βλάβη ηλεκτρονικής πλακέτας'),
            ('Πρόβλημα Αισθητήρα', 'Βλάβη αισθητήρα θερμοκρασίας'),
            ('Διαρροή Νερού', 'Διαρροή συμπυκνώματος'),
            ('Πρόβλημα Αποστράγγισης', 'Πρόβλημα αποστράγγισης νερού'),
        ],
        'Επισκευή': [
            ('Αντικατάσταση Compressor', 'Αντικατάσταση συμπιεστή'),
            ('Αντικατάσταση Πλακέτας', 'Αντικατάσταση ηλεκτρονικής πλακέτας'),
            ('Συγκόλληση Διαρροής', 'Επισκευή διαρροής με συγκόλληση'),
            ('Αντικατάσταση Ανεμιστήρα', 'Αντικατάσταση ανεμιστήρα'),
            ('Φόρτιση Ψυκτικού', 'Προσθήκη ψυκτικού υγρού'),
            ('Αντικατάσταση Αισθητήρα', 'Αντικατάσταση αισθητήρα θερμοκρασίας'),
            ('Επισκευή Αποστράγγισης', 'Επισκευή συστήματος αποστράγγισης'),
            ('Αντικατάσταση Φίλτρου', 'Αντικατάσταση φίλτρου'),
            ('Καθαρισμός Αποφράξεων', 'Καθαρισμός αποφραγμένων σωλήνων'),
        ],
        'Απλός Έλεγχος': [
            ('Οπτικός Έλεγχος', 'Γενικός οπτικός έλεγχος'),
            ('Έλεγχος Λειτουργίας', 'Έλεγχος κανονικής λειτουργίας'),
            ('Μετρήσεις Πίεσης', 'Μέτρηση πιέσεων συστήματος'),
            ('Έλεγχος Θερμοκρασίας', 'Έλεγχος θερμοκρασιών'),
            ('Έλεγχος Ηλεκτρικών', 'Έλεγχος ηλεκτρικών συνδέσεων'),
            ('Έλεγχος Στάθμης Ψυκτικού', 'Έλεγχος επάρκειας ψυκτικού'),
        ]
    }

    # Εισαγωγή ειδών στη βάση
    for task_type_name, items in task_items.items():
        if task_type_name in task_types:
            task_type_id = task_types[task_type_name]
            for item_name, item_desc in items:
                try:
                    cursor.execute('''
                                   INSERT INTO task_items (name, task_type_id, description)
                                   VALUES (?, ?, ?)
                                   ''', (item_name, task_type_id, item_desc))
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass

    conn.commit()
    conn.close()


def load_sample_data():
    """Φόρτωση δεδομένων δοκιμών"""

    conn = get_connection()
    cursor = conn.cursor()

    # Έλεγχος αν υπάρχουν ήδη δεδομένα
    cursor.execute("SELECT COUNT(*) as count FROM groups")
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return

    # Προσθήκη Ομάδων
    groups = [
        ("Κλιματιστικά", "Μονάδες κλιματισμού"),
        ("Ψυκτικά Συστήματα", "Ψυγεία και καταψύκτες"),
        ("Αερισμός", "Συστήματα εξαερισμού"),
        ("Καυστήρες", "Συστήματα θέρμανσης"),
    ]

    for name, desc in groups:
        cursor.execute("INSERT INTO groups (name, description) VALUES (?, ?)", (name, desc))

    # Προσθήκη προκαθορισμένων ειδών εργασιών
    task_types = [
        ("Service", "Προγραμματισμένη συντήρηση", 1),
        ("Βλάβη", "Αναφορά βλάβης", 1),
        ("Επισκευή", "Επισκευή βλάβης", 1),
        ("Απλός Έλεγχος", "Έλεγχος ρουτίνας", 1),
    ]

    for name, desc, predefined in task_types:
        cursor.execute("INSERT INTO task_types (name, description, is_predefined) VALUES (?, ?, ?)",
                       (name, desc, predefined))

    # Προσθήκη Μονάδων
    units = [
        ("VRV-A101", 1, "Πτέρυγα A - 1ος Όροφος", "Daikin VRV", "DK2023001", "2023-01-15"),
        ("VRV-A201", 1, "Πτέρυγα A - 2ος Όροφος", "Daikin VRV", "DK2023002", "2023-01-20"),
        ("Split-B105", 1, "Πτέρυγα B - Γραφείο", "Mitsubishi Electric", "ME2022045", "2022-06-10"),
        ("Ψυγείο-Φαρμ", 2, "Φαρμακείο", "Liebherr Medical", "LH2021033", "2021-03-15"),
        ("Καταψύκτης-Εργ", 2, "Εργαστήριο", "Thermo Scientific", "TS2020012", "2020-11-22"),
        ("AHU-01", 3, "Κεντρικό Σύστημα", "Systemair", "SY2022018", "2022-04-10"),
    ]

    for name, group_id, location, model, serial, install_date in units:
        cursor.execute('''INSERT INTO units (name, group_id, location, model, notes, installation_date)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (name, group_id, location, model, serial, install_date))

    # Προσθήκη μερικών εργασιών δοκιμής
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    tasks_sample = [
        (1, 1, "Ετήσιο Service VRV A101", "completed", "medium", yesterday, yesterday, "Γιάννης Π.", "Όλα εντάξει"),
        (4, 2, "Ψυγείο φαρμακείου δεν ψύχει", "pending", "high", today, None, "Μαρία Κ.", None),
        (2, 4, "Έλεγχος λειτουργίας VRV A201", "completed", "low", today, today, "Γιάννης Π.", "Κανονική λειτουργία"),
        (3, 2, "Split B105 κάνει θόρυβο", "pending", "medium", week_ago, None, "Νίκος Α.", "Χρειάζεται επισκευή"),
        (5, 1, "Service καταψύκτη εργαστηρίου", "completed", "medium", week_ago, week_ago, "Μαρία Κ.",
         "Αλλαγή φίλτρων"),
    ]

    for unit_id, task_type_id, desc, status, priority, created, completed, tech, notes in tasks_sample:
        cursor.execute('''INSERT INTO tasks (unit_id, task_type_id, description, status, priority,
                                             created_date, completed_date, technician_name, notes)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (unit_id, task_type_id, desc, status, priority, created, completed, tech, notes))

    conn.commit()
    conn.close()

    # Load default task items after sample data
    load_default_task_items()


# ----- FUNCTIONS ΓΙΑ QUERIES -----

def get_all_groups():
    """Επιστρέφει όλες τις ομάδες μονάδων"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups ORDER BY name")
    groups = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return groups


def get_units_by_group(group_id):
    """Επιστρέφει τις μονάδες μιας ομάδας"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM units WHERE group_id = ? AND is_active = 1 ORDER BY name", (group_id,))
    units = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return units


def get_all_task_types():
    """Επιστρέφει όλα τα είδη εργασιών"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM task_types ORDER BY is_predefined DESC, name")
    types = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return types


def get_dashboard_stats():
    """Επιστρέφει στατιστικά για το dashboard"""
    conn = get_connection()
    cursor = conn.cursor()

    # Σύνολο μονάδων
    cursor.execute("SELECT COUNT(*) as count FROM units WHERE is_active = 1")
    total_units = cursor.fetchone()['count']

    # Εκκρεμείς εργασίες
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'pending' AND is_deleted = 0")
    pending_tasks = cursor.fetchone()['count']

    # Εργασίες σήμερα
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE created_date = ? AND is_deleted = 0", (today,))
    today_tasks = cursor.fetchone()['count']

    conn.close()

    return {
        'total_units': total_units,
        'pending_tasks': pending_tasks,
        'today_tasks': today_tasks
    }


def get_recent_tasks(limit=5):
    """Επιστρέφει τις πιο πρόσφατες εργασίες - Updated Phase 2. 3"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT t.*,
                          u.name  as unit_name,
                          tt.name as task_type_name,
                          g.name  as group_name,
                          ti.name as task_item_name
                   FROM tasks t
                            JOIN units u ON t.unit_id = u.id
                            JOIN task_types tt ON t.task_type_id = tt.id
                            JOIN groups g ON u.group_id = g.id
                            LEFT JOIN task_items ti ON t.task_item_id = ti.id
                   WHERE t.is_deleted = 0
                   ORDER BY t.created_at DESC LIMIT ?
                   ''', (limit,))

    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks


def add_task(unit_id, task_type_id, description, status, priority, created_date,
             completed_date, technician_name, notes, task_item_id=None, location=None):
    """Προσθήκη νέας εργασίας - Updated Phase 2.3"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   INSERT INTO tasks (unit_id, task_type_id, task_item_id, description, status, priority,
                                      created_date, completed_date, technician_name, notes, location)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (unit_id, task_type_id, task_item_id, description, status, priority, created_date,
                         completed_date, technician_name, notes, location))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def get_all_units():
    """Επιστρέφει όλες τις μονάδες"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT u.*, g.name as group_name
                   FROM units u
                            JOIN groups g ON u.group_id = g.id
                   WHERE u.is_active = 1
                   ORDER BY g.name, u.name
                   ''')
    units = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return units


def add_unit(name, group_id, location, model, notes, installation_date):
    """Προσθήκη νέας μονάδας"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   INSERT INTO units (name, group_id, location, model, notes, installation_date)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (name, group_id, location, model, notes, installation_date))

    unit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return unit_id


def add_group(name, description):
    """Προσθήκη νέας ομάδας"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', (name, description))
        group_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return group_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


# ----- PHASE 2:  NEW FUNCTIONS -----

def get_all_tasks(include_deleted=False):
    """Επιστρέφει όλες τις εργασίες με πλήρεις πληροφορίες - Updated Phase 2.3"""
    conn = get_connection()
    cursor = conn.cursor()

    deleted_filter = "" if include_deleted else "WHERE t.is_deleted = 0"

    cursor.execute(f'''
        SELECT t.*, u.name as unit_name, tt.name as task_type_name, g.name as group_name,
               ti.name as task_item_name
        FROM tasks t
        JOIN units u ON t.unit_id = u.id
        JOIN task_types tt ON t.task_type_id = tt.id
        JOIN groups g ON u.group_id = g.id
        LEFT JOIN task_items ti ON t.task_item_id = ti.id
        {deleted_filter}
        ORDER BY t.created_date DESC, t.created_at DESC
    ''')

    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks


def get_task_by_id(task_id):
    """Επιστρέφει μία εργασία με βάση το ID - Updated Phase 2.3"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT t.*,
                          u.name  as unit_name,
                          tt.name as task_type_name,
                          g.name  as group_name,
                          ti.name as task_item_name
                   FROM tasks t
                            JOIN units u ON t.unit_id = u.id
                            JOIN task_types tt ON t.task_type_id = tt.id
                            JOIN groups g ON u.group_id = g.id
                            LEFT JOIN task_items ti ON t.task_item_id = ti.id
                   WHERE t.id = ?
                   ''', (task_id,))

    task = cursor.fetchone()
    conn.close()
    return dict(task) if task else None


def update_task(task_id, unit_id, task_type_id, description, status, priority,
                created_date, completed_date, technician_name, notes, task_item_id=None, location=None):
    """Ενημέρωση υπάρχουσας εργασίας - Updated Phase 2.3"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   UPDATE tasks
                   SET unit_id         = ?,
                       task_type_id    = ?,
                       task_item_id    = ?,
                       description     = ?,
                       status          = ?,
                       priority        = ?,
                       created_date    = ?,
                       completed_date  = ?,
                       technician_name = ?,
                       notes           = ?,
                       location        = ?
                   WHERE id = ?
                   ''', (unit_id, task_type_id, task_item_id, description, status, priority, created_date,
                         completed_date, technician_name, notes, location, task_id))

    conn.commit()
    conn.close()
    return True


def delete_task(task_id):
    """Smart delete με auto-reconnect (bypass) - FIXED"""
    conn = get_connection()
    cursor = conn.cursor()

    # ═════════════════════════════════════════════════
    # STEP 1: Get relationships before delete
    # ═════════════════════════════════════════════════
    relations = get_related_tasks(task_id)
    parents = relations['parents']
    children = relations['children']

    # ═════════════════════════════════════════════════
    # STEP 2: Create bypass (ONLY if 1 parent + 1 child)
    # ═════════════════════════════════════════════════
    if len(parents) == 1 and len(children) == 1:
        parent = parents[0]
        child = children[0]

        # Create bypass:  parent → child (skip deleted task)
        try:
            cursor.execute("""
                           INSERT
                           OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
                VALUES (?, ?, 'related', 0)
                           """, (parent['id'], child['id']))
        except:
            pass  # Relationship already exists

    # ═════════════════════════════════════════════════
    # STEP 3: Mark task as deleted
    # ═════════════════════════════════════════════════
    cursor.execute("""
                   UPDATE tasks
                   SET is_deleted = 1
                   WHERE id = ?
                   """, (task_id,))

    # ═════════════════════════════════════════════════
    # STEP 4: Mark task's relationships as deleted (backup)
    # ═════════════════════════════════════════════════
    cursor.execute("""
                   UPDATE task_relationships
                   SET is_deleted = 1
                   WHERE parent_task_id = ?
                      OR child_task_id = ?
                   """, (task_id, task_id))

    conn.commit()
    conn.close()


def restore_task(task_id):
    """Smart restore - DEBUG VERSION"""
    conn = get_connection()
    cursor = conn.cursor()

    print(f"\n🔍 DEBUG: Restoring task_id={task_id}")

    # Check manually removed status
    cursor.execute("""
                   SELECT COUNT(*) as count
                   FROM task_relationships
                   WHERE (parent_task_id = ?
                      OR child_task_id = ?)
                     AND is_deleted = 2
                   """, (task_id, task_id))

    was_manually_removed = cursor.fetchone()['count'] > 0
    print(f"   was_manually_removed = {was_manually_removed}")

    # Restore task
    cursor.execute("UPDATE tasks SET is_deleted = 0 WHERE id = ?", (task_id,))

    # Get task details
    cursor.execute("""
                   SELECT t.*, u.name as unit_name
                   FROM tasks t
                            JOIN units u ON t.unit_id = u.id
                   WHERE t.id = ?
                   """, (task_id,))

    restored_task = dict(cursor.fetchone())
    unit_id = restored_task['unit_id']
    restored_date = restored_task['created_date']

    print(f"   unit_id={unit_id}, date={restored_date}")

    # Get ALL relationships for this unit (including is_deleted)
    cursor.execute("""
                   SELECT tr.id,
                          tr.parent_task_id,
                          tr.child_task_id,
                          tr.is_deleted,
                          t1.created_date as parent_date,
                          t2.created_date as child_date
                   FROM task_relationships tr
                            JOIN tasks t1 ON tr.parent_task_id = t1.id
                            JOIN tasks t2 ON tr.child_task_id = t2.id
                   WHERE (t1.unit_id = ? OR t2.unit_id = ?)
                   """, (unit_id, unit_id))

    all_rels = cursor.fetchall()
    print(f"\n   All relationships in unit {unit_id}:")
    for rel in all_rels:
        print(f"      {rel['parent_task_id']}→{rel['child_task_id']} | is_deleted={rel['is_deleted']}")

    # If manually removed, check for bypass
    if was_manually_removed:
        print(f"\n   🔍 Checking for bypass...")

        # Find bypass relationships
        bypass_found = False
        for rel in all_rels:
            if rel['is_deleted'] == 0:  # Active relationship
                print(f"      Active:  {rel['parent_task_id']}→{rel['child_task_id']}")
                bypass_found = True

        if bypass_found:
            print(f"   ✅ Bypass found! Will do chronological insert.")
            # Delete old markers
            cursor.execute("""
                           DELETE
                           FROM task_relationships
                           WHERE (parent_task_id = ? OR child_task_id = ?)
                             AND is_deleted = 2
                           """, (task_id, task_id))
        else:
            print(f"   ❌ No bypass found!  Task stays standalone.")
            cursor.execute("""
                           DELETE
                           FROM task_relationships
                           WHERE (parent_task_id = ? OR child_task_id = ?)
                             AND is_deleted = 2
                           """, (task_id, task_id))
            conn.commit()
            conn.close()
            return

    # Get active tasks for chronological insert
    cursor.execute("""
                   SELECT t.id, t.created_date, t.created_at
                   FROM tasks t
                   WHERE t.unit_id = ?
                     AND t.is_deleted = 0
                     AND t.id != ?
                   ORDER BY t.created_date ASC, t.created_at ASC
                   """, (unit_id, task_id))

    unit_tasks = [dict(row) for row in cursor.fetchall()]
    print(f"\n   Active tasks in unit:  {[t['id'] for t in unit_tasks]}")

    # Find insertion point
    insert_after = None
    insert_before = None

    for task in unit_tasks:
        if task['created_date'] < restored_date:
            insert_after = task
        elif task['created_date'] > restored_date and insert_before is None:
            insert_before = task
            break

    print(f"   insert_after = {insert_after['id'] if insert_after else None}")
    print(f"   insert_before = {insert_before['id'] if insert_before else None}")

    # Rebuild relationships
    if insert_after and insert_before:
        print(f"\n   🔧 MIDDLE INSERT: {insert_after['id']}→{task_id}→{insert_before['id']}")

        # Remove bypass
        cursor.execute("""
                       DELETE
                       FROM task_relationships
                       WHERE parent_task_id = ?
                         AND child_task_id = ?
                        """, (insert_after['id'], insert_before['id']))
        print(f"      Removed bypass: {insert_after['id']}→{insert_before['id']}")

        # Create new relationships
        cursor.execute("""
                       INSERT
                       OR IGNORE INTO task_relationships 
            (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
                       """, (insert_after['id'], task_id))
        print(f"      Created:  {insert_after['id']}→{task_id}")

        cursor.execute("""
                       INSERT
                       OR IGNORE INTO task_relationships 
            (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
                       """, (task_id, insert_before['id']))
        print(f"      Created: {task_id}→{insert_before['id']}")

    elif insert_after and not insert_before:
        print(f"\n   🔧 APPEND TO END: {insert_after['id']}→{task_id}")
        cursor.execute("""
                       INSERT
                       OR IGNORE INTO task_relationships 
            (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
                       """, (insert_after['id'], task_id))

    elif not insert_after and insert_before:
        print(f"\n   🔧 PREPEND TO START: {task_id}→{insert_before['id']}")
        cursor.execute("""
                       INSERT
                       OR IGNORE INTO task_relationships 
            (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
                       """, (task_id, insert_before['id']))

    conn.commit()
    conn.close()
    print(f"✅ Restore complete!\n")


def permanent_delete_task(task_id):
    """Οριστική διαγραφή εργασίας"""
    conn = get_connection()
    cursor = conn.cursor()

    # Βρίσκουμε τους "γειτονικούς" κόμβους της εργασίας που διαγράφεται
    cursor.execute("""
                   SELECT parent_task_id, child_task_id
                   FROM task_relationships
                   WHERE (parent_task_id = ? OR child_task_id = ?)
                     AND is_deleted = 0
                     AND relationship_type = 'related'
                   """, (task_id, task_id))

    relationships = cursor.fetchall()

    # Αναγνωρίζουμε τον "γονέα" (parent_id) και το "παιδί" (child_id) της task_id
    parent_id = None
    child_id = None

    for relationship in relationships:
        if relationship['child_task_id'] == task_id:
            parent_id = relationship['parent_task_id']
        if relationship['parent_task_id'] == task_id:
            child_id = relationship['child_task_id']

    # Δημιουργούμε τη σχέση Task1 → Task3 (γονέας → παιδί) αν υπάρχουν
    if parent_id and child_id:
        cursor.execute("""
                       INSERT
                       OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
                       """, (parent_id, child_id))

    # Διαγράφουμε τις σχέσεις που περιλαμβάνουν το task_id
    cursor.execute("""
                   DELETE
                   FROM task_relationships
                   WHERE parent_task_id = ?
                      OR child_task_id = ?
                   """, (task_id, task_id))

    # Διαγραφή της ίδιας της εργασίας
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()
    return True


def get_deleted_tasks():
    """Επιστρέφει διαγραμμένες εργασίες - Updated Phase 2.3"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT t.*,
                          u.name  as unit_name,
                          tt.name as task_type_name,
                          g.name  as group_name,
                          ti.name as task_item_name
                   FROM tasks t
                            JOIN units u ON t.unit_id = u.id
                            JOIN task_types tt ON t.task_type_id = tt.id
                            JOIN groups g ON u.group_id = g.id
                            LEFT JOIN task_items ti ON t.task_item_id = ti.id
                   WHERE t.is_deleted = 1
                   ORDER BY t.created_at DESC
                   ''')

    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks


def filter_tasks(status=None, unit_id=None, task_type_id=None, date_from=None, date_to=None, search_text=None):
    """Φιλτράρισμα εργασιών με πολλαπλά κριτήρια - FIXED: Comprehensive Search"""
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
            SELECT t.*,
                   u.name  as unit_name,
                   tt.name as task_type_name,
                   g.name  as group_name,
                   g.id    as group_id,
                   ti.name as task_item_name
            FROM tasks t
        JOIN units u ON t.unit_id = u.id
        JOIN task_types tt ON t.task_type_id = tt.id
        JOIN groups g ON u.group_id = g.id
        LEFT JOIN task_items ti ON t.task_item_id = ti.id
        WHERE t.is_deleted = 0
    '''

    params = []

    if status:
        query += " AND t.status = ?"
        params.append(status)

    if unit_id:
        query += " AND t.unit_id = ?"
        params.append(unit_id)

    if task_type_id:
        query += " AND t.task_type_id = ?"
        params.append(task_type_id)

    if date_from:
        query += " AND t.created_date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND t.created_date <= ?"
        params.append(date_to)

    # ✅ FIXED: Comprehensive search across ALL relevant fields
    if search_text:
        query += """ AND (
            LOWER(t.description) LIKE LOWER(?) OR 
            LOWER(t.notes) LIKE LOWER(?) OR 
            LOWER(u.name) LIKE LOWER(?) OR
            LOWER(g.name) LIKE LOWER(?) OR
            LOWER(tt.name) LIKE LOWER(?) OR
            LOWER(ti.name) LIKE LOWER(?) OR
            LOWER(t.technician_name) LIKE LOWER(?) OR
            CAST(t.id AS TEXT) LIKE ?
        )"""
        search_param = f"%{search_text}%"
        # Add 8 parameters (one for each field)
        params.extend([search_param] * 8)

    query += " ORDER BY t.created_date DESC, t.created_at DESC"

    cursor.execute(query, params)
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks


def add_task_relationship(parent_task_id, child_task_id, relationship_type="related"):
    """Δημιουργία σχέσης μεταξύ δύο εργασιών - SMART VERSION"""
    conn = get_connection()
    cursor = conn.cursor()

    # ═════════════════════════════════════════════════
    # STEP 1: Check if child was manually removed from chain
    # ═════════════════════════════════════════════════
    cursor.execute("""
                   SELECT COUNT(*) as count
                   FROM task_relationships
                   WHERE (parent_task_id = ?
                      OR child_task_id = ?)
                     AND is_deleted = 2
                   """, (child_task_id, child_task_id))

    child_was_removed = cursor.fetchone()['count'] > 0

    if child_was_removed:
        print(f"🔍 Child task {child_task_id} was manually removed - cleaning up...")

        # Delete old manually-removed markers
        cursor.execute("""
                       DELETE
                       FROM task_relationships
                       WHERE (parent_task_id = ? OR child_task_id = ?)
                         AND is_deleted = 2
                        """, (child_task_id, child_task_id))

    # ═════════════════════════════════════════════════
    # STEP 2: Check if parent already has a child (bypass scenario)
    # ═════════════════════════════════════════════════
    cursor.execute("""
                   SELECT child_task_id
                   FROM task_relationships
                   WHERE parent_task_id = ?
                     AND is_deleted = 0
                     AND relationship_type = 'related'
                   """, (parent_task_id,))

    existing_child = cursor.fetchone()

    if existing_child:
        old_child_id = existing_child['child_task_id']

        print(f"🔍 Parent {parent_task_id} already has child {old_child_id}")
        print(f"   Checking if {child_task_id} should be inserted between...")

        # Get created_date for chronological check
        cursor.execute("""
                       SELECT id, created_date, created_at
                       FROM tasks
                       WHERE id IN (?, ?)
                       """, (child_task_id, old_child_id))

        # ✅ FIX: Convert to dict properly
        rows = cursor.fetchall()
        dates = {}
        for row in rows:
            task_id = row['id']
            dates[task_id] = (row['created_date'], row['created_at'])

        print(f"   Task {child_task_id}:  {dates.get(child_task_id)}")
        print(f"   Task {old_child_id}:  {dates.get(old_child_id)}")

        # If child_task_id is OLDER than old_child_id, it should be inserted before
        if child_task_id in dates and old_child_id in dates:
            if dates[child_task_id] < dates[old_child_id]:
                print(f"   ✅ Inserting {child_task_id} BETWEEN {parent_task_id} and {old_child_id}")

                # Remove old bypass:  parent → old_child
                cursor.execute("""
                               DELETE
                               FROM task_relationships
                               WHERE parent_task_id = ?
                                 AND child_task_id = ?
                               """, (parent_task_id, old_child_id))

                # Create new chain: parent → child → old_child
                cursor.execute("""
                               INSERT INTO task_relationships
                                   (parent_task_id, child_task_id, relationship_type, is_deleted)
                               VALUES (?, ?, ?, 0)
                               """, (parent_task_id, child_task_id, relationship_type))

                cursor.execute("""
                               INSERT
                               OR IGNORE INTO task_relationships 
                    (parent_task_id, child_task_id, relationship_type, is_deleted)
                    VALUES (?, ?, 'related', 0)
                               """, (child_task_id, old_child_id))

                conn.commit()
                conn.close()
                print(f"✅ Relationship created: {parent_task_id}→{child_task_id}→{old_child_id}")
                return True
            else:
                print(f"   ℹ️ Task {child_task_id} is NEWER than {old_child_id} - not inserting between")

    # ═════════════════════════════════════════════════
    # STEP 3: Normal insert (no bypass to handle)
    # ═════════════════════════════════════════════════
    print(f"   Creating normal relationship: {parent_task_id}→{child_task_id}")

    cursor.execute('''
                   INSERT INTO task_relationships (parent_task_id, child_task_id, relationship_type)
                   VALUES (?, ?, ?)
                   ''', (parent_task_id, child_task_id, relationship_type))

    conn.commit()
    conn.close()
    print(f"✅ Relationship created: {parent_task_id}→{child_task_id}")
    return True


def get_related_tasks(task_id):
    """Παίρνει τις συνδεδεμένες εργασίες (parents & children)"""
    conn = get_connection()
    cursor = conn.cursor()

    # Parents
    cursor.execute("""
                   SELECT t.*,
                          u.name  as unit_name,
                          tt.name as task_type_name,
                          ti.name as task_item_name,
                          g.name  as group_name
                   FROM tasks t
                            JOIN task_relationships tr ON t.id = tr.parent_task_id
                            JOIN units u ON t.unit_id = u.id
                            JOIN groups g ON u.group_id = g.id
                            JOIN task_types tt ON t.task_type_id = tt.id
                            LEFT JOIN task_items ti ON t.task_item_id = ti.id
                   WHERE tr.child_task_id = ?
                     AND t.is_deleted = 0
                     AND tr.is_deleted = 0
                   """, (task_id,))

    parents = [dict(row) for row in cursor.fetchall()]

    # Children
    cursor.execute("""
                   SELECT t.*,
                          u.name  as unit_name,
                          tt.name as task_type_name,
                          ti.name as task_item_name,
                          g.name  as group_name
                   FROM tasks t
                            JOIN task_relationships tr ON t.id = tr.child_task_id
                            JOIN units u ON t.unit_id = u.id
                            JOIN groups g ON u.group_id = g.id
                            JOIN task_types tt ON t.task_type_id = tt.id
                            LEFT JOIN task_items ti ON t.task_item_id = ti.id
                   WHERE tr.parent_task_id = ?
                     AND t.is_deleted = 0
                     AND tr.is_deleted = 0
                   """, (task_id,))

    children = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'parents': parents,
        'children': children
    }


def remove_task_relationship(parent_task_id, child_task_id):
    """Αφαίρεση σχέσης μεταξύ εργασιών"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   DELETE
                   FROM task_relationships
                   WHERE parent_task_id = ?
                     AND child_task_id = ?
                   ''', (parent_task_id, child_task_id))

    conn.commit()
    conn.close()
    return True


def remove_task_from_chain(task_id):
    """Smart remove - αφαίρεση από αλυσίδα με bypass"""
    conn = get_connection()
    cursor = conn.cursor()

    # Get relationships
    relations = get_related_tasks(task_id)
    parents = relations['parents']
    children = relations['children']

    # ═════════════════════════════════════════════════
    # BYPASS LOGIC:  If task has 1 parent + 1 child, connect them
    # ═════════════════════════════════════════════════
    if len(parents) == 1 and len(children) == 1:
        parent_id = parents[0]['id']
        child_id = children[0]['id']

        # Create bypass: parent → child (skip removed task)
        try:
            cursor.execute("""
                           INSERT
                           OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
                VALUES (?, ?, 'related', 0)
                           """, (parent_id, child_id))
        except:
            pass

    # ═════════════════════════════════════════════════
    # Mark relationships as MANUALLY REMOVED (is_deleted = 2)
    # ═════════════════════════════════════════════════
    cursor.execute("""
                   UPDATE task_relationships
                   SET is_deleted = 2
                   WHERE parent_task_id = ?
                      OR child_task_id = ?
                   """, (task_id, task_id))

    conn.commit()
    conn.close()





def mark_relationship_manually_removed(parent_task_id, child_task_id):
    """Mark relationship as manually removed by user (not auto-delete)"""
    conn = get_connection()
    cursor = conn.cursor()

    # Set is_deleted = 2 (manual removal) instead of 1 (soft delete)
    cursor.execute("""
                   UPDATE task_relationships
                   SET is_deleted = 2
                   WHERE parent_task_id = ?
                     AND child_task_id = ?
                   """, (parent_task_id, child_task_id))

    conn.commit()
    conn.close()
    return True


# ----- PHASE 2.1: NEW FUNCTIONS FOR UNITS, GROUPS, AND TASK TYPES -----

def get_unit_by_id(unit_id):
    """Επιστρέφει μία μονάδα με βάση το ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT u.*, g.name as group_name
                   FROM units u
                            JOIN groups g ON u.group_id = g.id
                   WHERE u.id = ?
                   ''', (unit_id,))

    unit = cursor.fetchone()
    conn.close()
    return dict(unit) if unit else None


def get_group_by_id(group_id):
    """Επιστρέφει μία ομάδα με βάση το ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM groups WHERE id = ? ', (group_id,))

    group = cursor.fetchone()
    conn.close()
    return dict(group) if group else None


def update_unit(unit_id, name, group_id, location, model, notes, installation_date):
    """Ενημέρωση υπάρχουσας μονάδας"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   UPDATE units
                   SET name              = ?,
                       group_id          = ?,
                       location          = ?,
                       model             = ?,
                       serial_number     = ?,
                       installation_date = ?
                   WHERE id = ?
                   ''', (name, group_id, location, model, notes, installation_date, unit_id))

    conn.commit()
    conn.close()
    return True


def update_group(group_id, name, description):
    """Ενημέρωση υπάρχουσας ομάδας"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
                       UPDATE groups
                       SET name        = ?,
                           description = ?
                       WHERE id = ?
                       ''', (name, description, group_id))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def add_task_type(name, description):
    """Προσθήκη custom τύπου εργασίας"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
                       INSERT INTO task_types (name, description, is_predefined)
                       VALUES (?, ?, 0)
                       ''', (name, description))

        type_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return type_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def is_task_type_in_use(type_id):
    """Έλεγχος αν ένας τύπος εργασίας χρησιμοποιείται σε εργασίες"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT COUNT(*) as count
                   FROM tasks
                   WHERE task_type_id = ? AND is_deleted = 0
                   ''', (type_id,))

    count = cursor.fetchone()['count']
    conn.close()
    return count > 0


def delete_task_type(type_id):
    """Διαγραφή τύπου εργασίας (με validations)"""
    conn = get_connection()
    cursor = conn.cursor()

    # Έλεγχος αν είναι προκαθορισμένος
    cursor.execute('SELECT is_predefined FROM task_types WHERE id = ?', (type_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {'success': False, 'error': 'Ο τύπος δεν βρέθηκε'}

    if result['is_predefined']:
        conn.close()
        return {'success': False, 'error': 'Οι προκαθορισμένοι τύποι δεν μπορούν να διαγραφούν'}

    # Έλεγχος χρήσης
    if is_task_type_in_use(type_id):
        conn.close()
        return {'success': False, 'error': 'Ο τύπος χρησιμοποιείται σε εργασίες'}

    # Διαγραφή
    cursor.execute('DELETE FROM task_types WHERE id = ?', (type_id,))
    conn.commit()
    conn.close()

    return {'success': True}


# ----- PHASE 2.3: TASK ITEMS FUNCTIONS -----

def get_task_items_by_type(task_type_id):
    """Επιστρέφει τα είδη εργασιών ενός συγκεκριμένου τύπου"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT *
                   FROM task_items
                   WHERE task_type_id = ?
                     AND is_active = 1
                   ORDER BY name
                   ''', (task_type_id,))

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items


def get_all_task_items():
    """Επιστρέφει όλα τα είδη εργασιών"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT ti.*, tt.name as task_type_name
                   FROM task_items ti
                            JOIN task_types tt ON ti.task_type_id = tt.id
                   WHERE ti.is_active = 1
                   ORDER BY tt.name, ti.name
                   ''')

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items


def add_task_item(name, task_type_id, description=None):
    """Προσθήκη νέου είδους εργασίας"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
                       INSERT INTO task_items (name, task_type_id, description)
                       VALUES (?, ?, ?)
                       ''', (name, task_type_id, description))

        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def update_task_item(item_id, name, description=None):
    """Ενημέρωση υπάρχοντος είδους εργασίας"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
                       UPDATE task_items
                       SET name        = ?,
                           description = ?
                       WHERE id = ?
                       ''', (name, description, item_id))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def delete_task_item(item_id):
    """Διαγραφή είδους εργασίας (με validation)"""
    conn = get_connection()
    cursor = conn.cursor()

    # Έλεγχος χρήσης σε εργασίες
    cursor.execute('''
                   SELECT COUNT(*) as count
                   FROM tasks
                   WHERE task_item_id = ? AND is_deleted = 0
                   ''', (item_id,))

    count = cursor.fetchone()['count']

    if count > 0:
        conn.close()
        return {'success': False, 'error': f'Το είδος χρησιμοποιείται σε {count} εργασίες'}

    # Soft delete
    cursor.execute('UPDATE task_items SET is_active = 0 WHERE id = ? ', (item_id,))
    conn.commit()
    conn.close()

    return {'success': True}


def get_task_item_by_id(item_id):
    """Επιστρέφει ένα είδος εργασίας με βάση το ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT ti.*, tt.name as task_type_name
                   FROM task_items ti
                            JOIN task_types tt ON ti.task_type_id = tt.id
                   WHERE ti.id = ?
                   ''', (item_id,))

    item = cursor.fetchone()
    conn.close()
    return dict(item) if item else None

# ═══════════════════════════════════════════════════════════════════════════
# RECYCLE BIN & SOFT DELETE FUNCTIONS (Προστέθηκαν για compatibility)
# ═══════════════════════════════════════════════════════════════════════════

def get_deleted_groups():
    """Επιστρέφει διαγραμμένες ομάδες (placeholder - δεν έχουμε soft delete για groups)"""
    # Επειδή δεν έχουμε is_deleted στον πίνακα groups, επιστρέφουμε κενή λίστα
    return []


def get_deleted_units():
    """Επιστρέφει διαγραμμένες μονάδες (soft deleted με is_active = 0)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.*, g.name as group_name
        FROM units u
        LEFT JOIN groups g ON u.group_id = g.id
        WHERE u.is_active = 0
        ORDER BY u.name
    ''')
    
    units = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return units


def soft_delete_unit(unit_id):
    """Soft delete μονάδας (is_active = 0) - FIXED: Raise exception on error"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Έλεγχος αν η μονάδα έχει ενεργές εργασίες
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM tasks
        WHERE unit_id = ? AND is_deleted = 0
    ''', (unit_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        # FIXED: Raise exception αντί για return False
        raise ValidationError(f'Η μονάδα έχει {count} ενεργές εργασίες και δεν μπορεί να διαγραφεί')
    
    # Soft delete
    cursor.execute('UPDATE units SET is_active = 0 WHERE id = ?', (unit_id,))
    conn.commit()
    conn.close()
    return True


def restore_unit(unit_id):
    """Επαναφορά soft deleted μονάδας"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE units SET is_active = 1 WHERE id = ?', (unit_id,))
    conn.commit()
    conn.close()
    return True


def permanent_delete_unit(unit_id):
    """Μόνιμη διαγραφή μονάδας"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Έλεγχος αν η μονάδα έχει εργασίες
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM tasks
        WHERE unit_id = ?
    ''', (unit_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        return False  # Δεν μπορεί να διαγραφεί μόνιμα
    
    # Μόνιμη διαγραφή
    cursor.execute('DELETE FROM units WHERE id = ?', (unit_id,))
    conn.commit()
    conn.close()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# ΣΗΜΕΙΩΣΗ: Το delete_group() ΗΔΗ υπάρχει στο αρχικό αρχείο
# ═══════════════════════════════════════════════════════════════════════════



def permanent_delete_group(group_id):
    """Οριστική διαγραφή ομάδας από τη βάση"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if group has units
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM units
        WHERE group_id = ?
    """, (group_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        raise ValidationError(f'Η ομάδα έχει {count} μονάδες. Διαγράψτε πρώτα τις μονάδες.')
    
    # Permanent delete
    cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    
    conn.commit()
    conn.close()
    return True


def permanent_delete_location(location_id):
    """Οριστική διαγραφή τοποθεσίας από τη βάση"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if location is used
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM units
        WHERE location = (SELECT name FROM locations WHERE id = ?)
    """, (location_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        raise ValidationError(f'Η τοποθεσία χρησιμοποιείται από {count} μονάδες.')
    
    # Permanent delete
    cursor.execute("DELETE FROM locations WHERE id = ?", (location_id,))
    
    conn.commit()
    conn.close()
    return True

def delete_group(group_id):
    """
    Διαγραφή ομάδας με έλεγχο dependencies
    Επιστρέφει: {'success': bool, 'error': str (optional)}
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Έλεγχος αν η ομάδα έχει μονάδες
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM units
        WHERE group_id = ? AND is_active = 1
    ''', (group_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        return {
            'success': False,
            'error': f'Η ομάδα έχει {count} ενεργές μονάδες και δεν μπορεί να διαγραφεί'
        }
    
    # Διαγραφή
    try:
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}


def soft_delete_group(group_id):
    """
    Soft delete ομάδας (placeholder - δεν έχουμε is_deleted στον πίνακα groups)
    ΣΗΜΕΙΩΣΗ: Επειδή ο πίνακας groups δεν έχει is_deleted field, 
              κάνουμε απευθείας DELETE (hard delete)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Έλεγχος αν η ομάδα έχει μονάδες
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM units
        WHERE group_id = ? AND is_active = 1
    ''', (group_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        raise ValidationError(f'Η ομάδα έχει {count} ενεργές μονάδες και δεν μπορεί να διαγραφεί')
    
    # Hard delete (δεν έχουμε soft delete για groups)
    try:
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise DatabaseError(f'Αποτυχία διαγραφής ομάδας: {str(e)}')


# ═══════════════════════════════════════════════════════════════════════════
# LOCATIONS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def get_all_locations():
    """Retrieve all active locations"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, description, created_at
        FROM locations
        WHERE is_deleted = 0
        ORDER BY name
    """)
    
    locations = []
    for row in cursor.fetchall():
        locations.append(dict(row))
    
    conn.close()
    return locations

def add_location(name, description=''):
    """Add new location"""
    name = name.strip()
    
    if not name:
        raise ValidationError("Location name is required")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO locations (name, description)
            VALUES (?, ?)
        """, (name, description))
        
        conn.commit()
        location_id = cursor.lastrowid
        conn.close()
        return location_id
        
    except sqlite3.IntegrityError:
        conn.close()
        raise ValidationError(f"Location '{name}' already exists")

def update_location(location_id, name, description=''):
    """Update location"""
    name = name.strip()
    
    if not name:
        raise ValidationError("Location name is required")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE locations
            SET name = ?, description = ?
            WHERE id = ?
        """, (name, description, location_id))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.IntegrityError:
        conn.close()
        raise ValidationError(f"Location '{name}' already exists")

def soft_delete_location(location_id):
    """Soft delete location"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if used
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM units
        WHERE location = (SELECT name FROM locations WHERE id = ?)
        AND is_active = 1
    """, (location_id,))
    
    count = cursor.fetchone()['count']
    
    if count > 0:
        conn.close()
        raise ValidationError(f'Location is used by {count} units')
    
    cursor.execute("UPDATE locations SET is_deleted = 1 WHERE id = ?", (location_id,))
    
    conn.commit()
    conn.close()
    return True


def get_deleted_locations():
    """Επιστρέφει όλες τις διαγραμμένες τοποθεσίες"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, description, created_at
        FROM locations
        WHERE is_deleted = 1
        ORDER BY name
    """)
    
    locations = []
    for row in cursor.fetchall():
        locations.append(dict(row))
    
    conn.close()
    return locations

def restore_location(location_id):
    """Επαναφορά διαγραμμένης τοποθεσίας"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE locations SET is_deleted = 0 WHERE id = ?", (location_id,))
    
    conn.commit()
    conn.close()
    return True
