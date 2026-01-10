"""
Components Package
==================
UI Components για το HVAC Maintenance System

Αυτό το package περιέχει όλα τα επαναχρησιμοποιήσιμα UI components
που ήταν στο ui_components.py (3,798 lines).

Components:
-----------
- TaskCard: Καρτέλα εργασίας (197 lines)
- DatePickerDialog: Επιλογέας ημερομηνίας (138 lines)
- TaskForm: Φόρμα εργασιών (909 lines)
- LocationsManagement: Διαχείριση τοποθεσιών (373 lines)
- UnitsManagement: Διαχείριση μονάδων (753 lines)
- TaskManagement: Διαχείριση εργασιών (471 lines)
- TaskHistoryView: Ιστορικό εργασιών (157 lines)
- RecycleBinView: Κάδος ανακύκλωσης (162 lines)
- TaskRelationshipsView: Σχέσεις εργασιών (624 lines)

Usage:
------
    from components import TaskCard, TaskForm, UnitsManagement
    
    # Ή:
    import components
    card = components.TaskCard(...)
"""

# Import όλα τα components
from .task_card import TaskCard
from .date_picker import DatePickerDialog
from .task_form import TaskForm
from .locations_mgmt import LocationsManagement
from .units_mgmt import UnitsManagement
from .tasks_mgmt import TaskManagement
from .history_view import TaskHistoryView
from .recycle_bin import RecycleBinView
from .relationships import TaskRelationshipsView

# Export list για "from components import *"
__all__ = [
    'TaskCard',
    'DatePickerDialog',
    'TaskForm',
    'LocationsManagement',
    'UnitsManagement',
    'TaskManagement',
    'TaskHistoryView',
    'RecycleBinView',
    'TaskRelationshipsView',
]

# Version info
__version__ = '2.0.0'
__author__ = 'HVAC Maintenance System'
