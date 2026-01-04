def remove_task_from_chain(task_id):
    """Smart remove - αφαίρεση από αλυσίδα με bypass"""
    conn = get_connection()
    cursor = conn.cursor()

    # Get relationships
    relations = get_related_tasks(task_id)
    parents = relations['parents']
    children = relations['children']

    # ═════════════════════════════════════════════════
    # BYPASS LOGIC: If task has 1 parent + 1 child, connect them
    # ═════════════════════════════════════════════════
    if len(parents) == 1 and len(children) == 1:
        parent_id = parents[0]['id']
        child_id = children[0]['id']

        # Create bypass: parent → child (skip removed task)
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
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
        WHERE parent_task_id = ? OR child_task_id = ?
    """, (task_id, task_id))

    conn.commit()
    conn.close()


def restore_task(task_id):
    """Smart restore - τοποθετεί την εργασία χρονολογικά βάσει ημερομηνίας"""
    conn = get_connection()
    cursor = conn.cursor()

    # ═════════════════════════════════════════════════
    # STEP 1: Check if task was MANUALLY removed from chain
    # ═════════════════════════════════════════════════
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM task_relationships
        WHERE (parent_task_id = ? OR child_task_id = ?)
          AND is_deleted = 2
    """, (task_id, task_id))

    was_manually_removed = cursor.fetchone()['count'] > 0

    # ═════════════════════════════════════════════════
    # STEP 2: Restore task
    # ═════════════════════════════════════════════════
    cursor.execute("""
        UPDATE tasks
        SET is_deleted = 0
        WHERE id = ?
    """, (task_id,))

    # ═════════════════════════════════════════════════
    # STEP 3: If MANUALLY removed, DON'T restore to chain
    # ═════════════════════════════════════════════════
    if was_manually_removed:
        # Delete the manually-removed relationships permanently
        cursor.execute("""
            DELETE FROM task_relationships
            WHERE (parent_task_id = ? OR child_task_id = ?)
              AND is_deleted = 2
        """, (task_id, task_id))

        conn.commit()
        conn.close()
        return  # Exit - task is now standalone

    # ═════════════════════════════════════════════════
    # STEP 4: Otherwise, restore to chain CHRONOLOGICALLY
    # ═════════════════════════════════════════════════

    # Get the task being restored
    cursor.execute("""
        SELECT t.*, u.name as unit_name, tt.name as task_type_name,
               ti.name as task_item_name, g.name as group_name
        FROM tasks t
        JOIN units u ON t.unit_id = u.id
        JOIN groups g ON u.group_id = g.id
        JOIN task_types tt ON t.task_type_id = tt.id
        LEFT JOIN task_items ti ON t.task_item_id = ti.id
        WHERE t.id = ?
    """, (task_id,))

    restored_task = dict(cursor.fetchone())
    restored_date = restored_task['created_date']
    unit_id = restored_task['unit_id']

    # Get all active tasks for this unit (ordered by date)
    cursor.execute("""
        SELECT t.*, u.name as unit_name, tt.name as task_type_name,
               ti.name as task_item_name, g.name as group_name
        FROM tasks t
        JOIN units u ON t.unit_id = u.id
        JOIN groups g ON u.group_id = g.id
        JOIN task_types tt ON t.task_type_id = tt.id
        LEFT JOIN task_items ti ON t.task_item_id = ti.id
        WHERE t.unit_id = ?
          AND t.is_deleted = 0
          AND t.id != ?
        ORDER BY t.created_date ASC, t.created_at ASC
    """, (unit_id, task_id))

    unit_tasks = [dict(row) for row in cursor.fetchall()]

    if not unit_tasks:
        # Solo task - no relationships needed
        conn.commit()
        conn.close()
        return

    # Find correct insertion point by date
    insert_after = None
    insert_before = None

    for task in unit_tasks:
        if task['created_date'] < restored_date:
            insert_after = task
        elif task['created_date'] > restored_date and insert_before is None:
            insert_before = task
            break

    # ═════════════════════════════════════════════════
    # Rebuild relationships chronologically
    # ═════════════════════════════════════════════════

    if insert_after and insert_before:
        # MIDDLE INSERT
        # Remove bypass (if exists)
        cursor.execute("""
            DELETE FROM task_relationships
            WHERE parent_task_id = ? AND child_task_id = ?
        """, (insert_after['id'], insert_before['id']))

        # Create: insert_after → restored_task
        cursor.execute("""
            INSERT OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
        """, (insert_after['id'], task_id))

        # Create: restored_task → insert_before
        cursor.execute("""
            INSERT OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
        """, (task_id, insert_before['id']))

    elif insert_after and not insert_before:
        # APPEND TO END
        cursor.execute("""
            INSERT OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
        """, (insert_after['id'], task_id))

    elif not insert_after and insert_before:
        # PREPEND TO START
        cursor.execute("""
            INSERT OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
            VALUES (?, ?, 'related', 0)
        """, (task_id, insert_before['id']))

    conn.commit()
    conn.close()


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

        # Create bypass: parent → child (skip deleted task)
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO task_relationships (parent_task_id, child_task_id, relationship_type, is_deleted)
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
        WHERE parent_task_id = ? OR child_task_id = ?
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
        WHERE parent_task_id = ? AND child_task_id = ?
    """, (parent_task_id, child_task_id))

    conn.commit()
    conn.close()
    return True
