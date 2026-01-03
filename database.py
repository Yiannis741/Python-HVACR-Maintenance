"""
Database module - Διαχείριση SQLite database
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
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Πίνακας Μονάδων
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            group_id INTEGER NOT NULL,
            location TEXT,
            model TEXT,
            serial_number TEXT,
            installation_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id)
        )
    ''')
    
    # Πίνακας Ειδών Εργασιών
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            is_predefined BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Πίνακας Εργασιών
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            task_type_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pending', 'completed')),
            priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
            created_date DATE NOT NULL,
            completed_date DATE,
            technician_name TEXT,
            notes TEXT,
            is_deleted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id),
            FOREIGN KEY (task_type_id) REFERENCES task_types(id)
        )
    ''')
    
    # Πίνακας Συνδέσεων Εργασιών (π.χ. Βλάβη -> Επισκευή)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_task_id INTEGER NOT NULL,
            child_task_id INTEGER NOT NULL,
            relationship_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_task_id) REFERENCES tasks(id),
            FOREIGN KEY (child_task_id) REFERENCES tasks(id)
        )
    ''')
    
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
        cursor.execute('''INSERT INTO units (name, group_id, location, model, serial_number, installation_date)
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      (name, group_id, location, model, serial, install_date))
    
    # Προσθήκη μερικών εργασιών δοκιμής
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    tasks_sample = [
        (1, 1, "Ετήσιο Service VRV A101", "completed", "medium", yesterday, yesterday, "Γιάννης Π.", "Όλα εντάξει"),
        (4, 2, "Ψυγείο φαρμακείου δεν ψύχει", "pending", "high", today, None, "Μαρία Κ.", None),
        (2, 4, "Έλεγχος λειτουργίας VRV A201", "completed", "low", today, today, "Γιάννης Π.", "Κανονική λειτουργία"),
    ]
    
    for unit_id, task_type_id, desc, status, priority, created, completed, tech, notes in tasks_sample:
        cursor.execute('''INSERT INTO tasks (unit_id, task_type_id, description, status, priority, 
                         created_date, completed_date, technician_name, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (unit_id, task_type_id, desc, status, priority, created, completed, tech, notes))
    
    conn.commit()
    conn.close()


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
    """Επιστρέφει τις πιο πρόσφατες εργασίες"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, u.name as unit_name, tt.name as task_type_name, g.name as group_name
        FROM tasks t
        JOIN units u ON t.unit_id = u.id
        JOIN task_types tt ON t.task_type_id = tt.id
        JOIN groups g ON u.group_id = g.id
        WHERE t.is_deleted = 0
        ORDER BY t.created_at DESC
        LIMIT ?
    ''', (limit,))
    
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks


def add_task(unit_id, task_type_id, description, status, priority, created_date, 
             completed_date, technician_name, notes):
    """Προσθήκη νέας εργασίας"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (unit_id, task_type_id, description, status, priority,
                          created_date, completed_date, technician_name, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (unit_id, task_type_id, description, status, priority, created_date,
          completed_date, technician_name, notes))
    
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


def add_unit(name, group_id, location, model, serial_number, installation_date):
    """Προσθήκη νέας μονάδας"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO units (name, group_id, location, model, serial_number, installation_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, group_id, location, model, serial_number, installation_date))
    
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
