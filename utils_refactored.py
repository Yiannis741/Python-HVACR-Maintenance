"""
Utils Module - Reusable Helper Functions (Refactored)
Αυτό το module περιέχει όλες τις επαναχρησιμοποιήσιμες συναρτήσεις που χρησιμοποιούνται
σε πολλά σημεία του κώδικα. Αποφεύγει code duplication (DRY principle).
"""

from typing import List, Dict, Any, Set, Optional
import database_refactored as database


# ═══════════════════════════════════════════════════════════════════════════
# CHAIN UTILITIES - Αντικαθιστά το duplicate logic από TaskCard και TaskForm
# ═══════════════════════════════════════════════════════════════════════════

def get_full_task_chain(task_id: int, all_tasks: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Επιστρέφει ολόκληρη την αλυσίδα εργασιών για μία δοθείσα εργασία.
    
    Η αλυσίδα περιλαμβάνει:
    - Όλες τις parent εργασίες (προηγούμενες)
    - Την τρέχουσα εργασία
    - Όλες τις child εργασίες (επόμενες)
    
    Args:
        task_id: ID της εργασίας για την οποία θέλουμε την αλυσίδα
        all_tasks: Optional προ-φορτωμένες εργασίες (για performance)
    
    Returns:
        List[Dict]: Λίστα εργασιών σε χρονολογική σειρά (παλιές → νέες)
    
    ΣΗΜΕΙΩΣΗ: Αυτή η function αντικαθιστά το duplicate _get_full_chain_simple()
    που υπήρχε στο TaskCard και TaskForm.
    """
    chain: List[Dict[str, Any]] = []
    visited_parents: Set[int] = set()
    visited_children: Set[int] = set()
    
    # Φόρτωση όλων των εργασιών αν δεν δόθηκαν
    if all_tasks is None:
        all_tasks = database.get_all_tasks()
    
    # Δημιουργία lookup dictionary για γρήγορη αναζήτηση
    task_dict = {t['id']: t for t in all_tasks}
    
    # Βρίσκουμε την τρέχουσα εργασία
    current_task = task_dict.get(task_id)
    if not current_task:
        return []  # Η εργασία δεν βρέθηκε
    
    def get_parents(tid: int) -> None:
        """Recursive function για να βρει όλους τους parents"""
        if tid in visited_parents:
            return  # Avoid infinite loops
        
        visited_parents.add(tid)
        relations = database.get_related_tasks(tid)
        
        for parent in relations['parents']:
            parent_id = parent['id']
            
            # Προσθήκη parent στην αρχή της αλυσίδας (αν δεν υπάρχει ήδη)
            if parent_id not in [c['id'] for c in chain]:
                chain.insert(0, parent)
                get_parents(parent_id)  # Recursive για parents του parent
    
    def get_children(tid: int) -> None:
        """Recursive function για να βρει όλα τα children"""
        if tid in visited_children:
            return  # Avoid infinite loops
        
        visited_children.add(tid)
        relations = database.get_related_tasks(tid)
        
        for child in relations['children']:
            child_id = child['id']
            
            # Προσθήκη child στο τέλος της αλυσίδας (αν δεν υπάρχει ήδη)
            if child_id not in [c['id'] for c in chain]:
                chain.append(child)
                get_children(child_id)  # Recursive για children του child
    
    # Build the full chain
    get_parents(task_id)           # Βρίσκουμε όλους τους parents
    chain.append(current_task)     # Προσθέτουμε την τρέχουσα
    get_children(task_id)          # Βρίσκουμε όλα τα children
    
    return chain


def get_task_position_in_chain(task_id: int, chain: Optional[List[Dict[str, Any]]] = None) -> Optional[int]:
    """
    Επιστρέφει τη θέση μιας εργασίας μέσα στην αλυσίδα της.
    
    Args:
        task_id: ID της εργασίας
        chain: Optional προ-φορτωμένη αλυσίδα (για performance)
    
    Returns:
        int: Η θέση της εργασίας (1-indexed), ή None αν δεν βρεθεί
    """
    if chain is None:
        chain = get_full_task_chain(task_id)
    
    for idx, task in enumerate(chain, 1):
        if task['id'] == task_id:
            return idx
    
    return None


def get_chain_summary(task_id: int) -> Dict[str, Any]:
    """
    Επιστρέφει summary για την αλυσίδα μιας εργασίας.
    
    Returns:
        Dict με keys:
            - chain_length: Συνολικό μήκος αλυσίδας
            - position: Θέση της εργασίας στην αλυσίδα
            - has_parents: Boolean αν έχει parents
            - has_children: Boolean αν έχει children
            - chain: Η πλήρης αλυσίδα
    """
    chain = get_full_task_chain(task_id)
    position = get_task_position_in_chain(task_id, chain)
    
    return {
        'chain_length': len(chain),
        'position': position if position else 0,
        'has_parents': position is not None and position > 1,
        'has_children': position is not None and position < len(chain),
        'chain': chain
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEXT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Κόβει κείμενο σε συγκεκριμένο μήκος με suffix.
    
    Args:
        text: Το κείμενο προς κόψιμο
        max_length: Μέγιστο μήκος
        suffix: Το suffix να προστεθεί
    
    Returns:
        str: Το κομμένο κείμενο
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


# ═══════════════════════════════════════════════════════════════════════════
# DATE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def format_date_greek(date_str: str) -> str:
    """
    Μορφοποιεί μια ημερομηνία σε ελληνική μορφή.
    
    Args:
        date_str: Ημερομηνία σε μορφή YYYY-MM-DD
    
    Returns:
        str: Ημερομηνία σε μορφή DD/MM/YYYY
    """
    from datetime import datetime
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return date_str  # Return original αν δεν μπορεί να parse


def get_date_relative_text(date_str: str) -> str:
    """
    Επιστρέφει relative text για μια ημερομηνία.
    
    Args:
        date_str: Ημερομηνία σε μορφή YYYY-MM-DD
    
    Returns:
        str: Relative text (π.χ. "Σήμερα", "Χθες", "Πριν 3 ημέρες")
    """
    from datetime import datetime
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-% d').date()
        today = datetime.now().date()
        delta = (today - date_obj).days
        
        if delta == 0:
            return "Σήμερα"
        elif delta == 1:
            return "Χθες"
        elif delta == -1:
            return "Αύριο"
        elif 0 < delta < 7:
            return f"Πριν {delta} ημέρες"
        elif delta < 0 and delta > -7:
            return f"Σε {abs(delta)} ημέρες"
        else:
            return format_date_greek(date_str)
            
    except ValueError:
        return date_str


# ═══════════════════════════════════════════════════════════════════════════
# USAGE INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════

"""
ΧΡΗΣΗ ΣΤΑ UI COMPONENTS:

ΠΡΙΝ (στο TaskCard):
-----------------------
def _get_full_chain_simple(self, task_id):
    chain = []
    visited_parents = set()
    visited_children = set()
    # ... 75 γραμμές duplicate code ...
    return chain

# Στη create_card():
full_chain = self._get_full_chain_simple(self.task['id'])


ΜΕΤΑ (με το utils):
-----------------------
from utils_refactored import get_full_task_chain

# Διαγράψτε τη _get_full_chain_simple() method

# Στη create_card():
full_chain = get_full_task_chain(self.task['id'])


ΟΦΕΛΗ:
--------
1. Μείωση κώδικα από ~150 γραμμές (duplicate) σε ~5 γραμμές
2. Single source of truth - αλλαγές σε ένα μέρος
3. Easier testing
4. Consistent behavior παντού
"""

if __name__ == "__main__":
    print("Utils Module - Chain Utilities")
    print("=" * 50)
    print("\nΑυτό το module αντικαθιστά το duplicate chain logic")
    print("από το TaskCard και TaskForm.")
    print("\nΓια χρήση:")
    print("  from utils_refactored import get_full_task_chain")
    print("  chain = get_full_task_chain(task_id)")
