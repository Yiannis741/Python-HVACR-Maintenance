"""
Database Backup Manager
=======================

Automatic backup and restore system για το HVAC database.

Features:
---------
- Automatic backups on app startup
- Keep last N backups (configurable)
- One-click restore from backup
- Backup before critical operations
- Timestamped backup files

Usage:
------
    from backup_manager import create_backup, restore_backup, list_backups
    
    # Auto backup on startup
    create_backup()
    
    # List available backups
    backups = list_backups()
    
    # Restore from backup
    restore_backup(backup_file)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import logger_config

logger = logger_config.get_logger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

DB_FILE = "hvacr_maintenance.db"
BACKUP_DIR = "backups"
MAX_BACKUPS = 7  # Keep last 7 backups
BACKUP_PREFIX = "hvacr_backup_"


# ═══════════════════════════════════════════════════════════════════════════
# BACKUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def create_backup(description="Auto backup"):
    """
    Δημιουργία backup του database.
    
    Args:
        description (str): Περιγραφή του backup (προαιρετικό)
        
    Returns:
        str: Path του backup file ή None αν απέτυχε
        
    Example:
        backup_file = create_backup("Before critical operation")
    """
    
    try:
        # Create backups directory
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        
        # Check if database exists
        if not os.path.exists(DB_FILE):
            logger.warning(f"Database file not found: {DB_FILE}")
            return None
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{BACKUP_PREFIX}{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Copy database file
        logger.info(f"Creating backup: {backup_filename}")
        shutil.copy2(DB_FILE, backup_path)
        
        # Get file size
        size_kb = os.path.getsize(backup_path) / 1024
        logger.info(f"✅ Backup created successfully: {backup_filename} ({size_kb:.1f} KB)")
        
        # Cleanup old backups
        cleanup_old_backups()
        
        return backup_path
        
    except Exception as e:
        logger.error(f"❌ Failed to create backup: {e}", exc_info=True)
        return None


def restore_backup(backup_path):
    """
    Επαναφορά database από backup.
    
    Args:
        backup_path (str): Path του backup file
        
    Returns:
        bool: True αν επιτυχής, False αν απέτυχε
        
    Example:
        success = restore_backup("backups/hvacr_backup_20250110_120000.db")
    """
    
    try:
        # Validate backup file exists
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Create safety backup of current database
        if os.path.exists(DB_FILE):
            logger.info("Creating safety backup of current database before restore...")
            safety_backup = f"{DB_FILE}.before_restore"
            shutil.copy2(DB_FILE, safety_backup)
            logger.info(f"Safety backup created: {safety_backup}")
        
        # Restore from backup
        logger.warning(f"⚠️  Restoring database from: {backup_path}")
        shutil.copy2(backup_path, DB_FILE)
        
        logger.info(f"✅ Database restored successfully from: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to restore backup: {e}", exc_info=True)
        return False


def list_backups():
    """
    Λίστα όλων των διαθέσιμων backups.
    
    Returns:
        list: List of dicts με backup info (path, timestamp, size)
        
    Example:
        backups = list_backups()
        for backup in backups:
            print(f"{backup['timestamp']} - {backup['size_kb']:.1f} KB")
    """
    
    try:
        # Create backups directory if not exists
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        
        # Get all backup files
        backup_files = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith(BACKUP_PREFIX) and filename.endswith(".db"):
                filepath = os.path.join(BACKUP_DIR, filename)
                
                # Get file info
                stat = os.stat(filepath)
                size_kb = stat.st_size / 1024
                mtime = datetime.fromtimestamp(stat.st_mtime)
                
                backup_files.append({
                    'path': filepath,
                    'filename': filename,
                    'timestamp': mtime,
                    'size_kb': size_kb,
                    'size_mb': size_kb / 1024
                })
        
        # Sort by timestamp (newest first)
        backup_files.sort(key=lambda x: x['timestamp'], reverse=True)
        
        logger.debug(f"Found {len(backup_files)} backup(s)")
        return backup_files
        
    except Exception as e:
        logger.error(f"Failed to list backups: {e}", exc_info=True)
        return []


def cleanup_old_backups():
    """
    Διαγραφή παλιών backups (κρατάει μόνο τα MAX_BACKUPS πιο πρόσφατα).
    
    Example:
        cleanup_old_backups()  # Keeps last 7 backups
    """
    
    try:
        backups = list_backups()
        
        if len(backups) <= MAX_BACKUPS:
            logger.debug(f"Backup count ({len(backups)}) within limit ({MAX_BACKUPS})")
            return
        
        # Delete oldest backups
        backups_to_delete = backups[MAX_BACKUPS:]
        
        logger.info(f"Cleaning up {len(backups_to_delete)} old backup(s)...")
        
        for backup in backups_to_delete:
            try:
                os.remove(backup['path'])
                logger.debug(f"Deleted old backup: {backup['filename']}")
            except Exception as e:
                logger.warning(f"Failed to delete backup {backup['filename']}: {e}")
        
        logger.info(f"✅ Cleanup complete. Kept {MAX_BACKUPS} most recent backups.")
        
    except Exception as e:
        logger.error(f"Failed to cleanup old backups: {e}", exc_info=True)


def get_backup_stats():
    """
    Στατιστικά για backups.
    
    Returns:
        dict: Backup statistics
        
    Example:
        stats = get_backup_stats()
        print(f"Total backups: {stats['count']}")
        print(f"Total size: {stats['total_size_mb']:.1f} MB")
    """
    
    try:
        backups = list_backups()
        
        if not backups:
            return {
                'count': 0,
                'total_size_kb': 0,
                'total_size_mb': 0,
                'oldest': None,
                'newest': None
            }
        
        total_size_kb = sum(b['size_kb'] for b in backups)
        
        return {
            'count': len(backups),
            'total_size_kb': total_size_kb,
            'total_size_mb': total_size_kb / 1024,
            'oldest': backups[-1]['timestamp'] if backups else None,
            'newest': backups[0]['timestamp'] if backups else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get backup stats: {e}", exc_info=True)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def format_backup_name(backup):
    """
    Format backup name για display.
    
    Args:
        backup (dict): Backup info από list_backups()
        
    Returns:
        str: Formatted name
        
    Example:
        "10/01/2025 12:00:00 (2.5 MB)"
    """
    
    timestamp_str = backup['timestamp'].strftime("%d/%m/%Y %H:%M:%S")
    size_str = f"{backup['size_mb']:.2f} MB"
    
    return f"{timestamp_str} ({size_str})"


def is_backup_valid(backup_path):
    """
    Έλεγχος αν το backup file είναι valid SQLite database.
    
    Args:
        backup_path (str): Path του backup file
        
    Returns:
        bool: True αν valid, False αν όχι
    """
    
    try:
        import sqlite3
        
        # Try to open as SQLite database
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Try a simple query
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        
        logger.debug(f"Backup validation: {backup_path} has {table_count} tables")
        return table_count > 0
        
    except Exception as e:
        logger.warning(f"Backup validation failed for {backup_path}: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def init_backup_system():
    """
    Αρχικοποίηση backup system.
    Καλείται στο startup του app.
    """
    
    logger.info("Initializing backup system...")
    
    # Create backups directory
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    
    # Get stats
    stats = get_backup_stats()
    
    if stats:
        logger.info(f"Backup system initialized: {stats['count']} existing backup(s), "
                   f"{stats['total_size_mb']:.1f} MB total")
    
    logger.info("✅ Backup system ready")


# ═══════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test the backup system
    logger_config.setup_logging()
    
    print("Testing backup system...")
    
    # Create backup
    backup = create_backup("Test backup")
    print(f"Created backup: {backup}")
    
    # List backups
    backups = list_backups()
    print(f"\nAvailable backups ({len(backups)}):")
    for b in backups:
        print(f"  - {format_backup_name(b)}")
    
    # Stats
    stats = get_backup_stats()
    print(f"\nStats: {stats['count']} backups, {stats['total_size_mb']:.1f} MB")
