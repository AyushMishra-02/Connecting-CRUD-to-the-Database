"""
database.py — SQLite database layer for the Tasks CRUD API.

This module handles all direct interaction with the SQLite database:
  • Creating / connecting to tasks.db
  • Creating the `tasks` table if it doesn't exist
  • Seeding three example tasks on first run
  • CRUD helper functions used by the Flask routes
"""

import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")


def get_connection():
    """Return a new connection to the SQLite database.
    
    Rows are returned as sqlite3.Row objects so they can be
    accessed by column name (like a dictionary).
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the tasks table if it doesn't exist and seed example data.

    Called once when the application starts.
    • The table is created with IF NOT EXISTS so it's safe to call repeatedly.
    • Example tasks are inserted **only** when the table is empty.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Stage 0: create the table ------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT    NOT NULL,
            done  INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Seed example tasks only if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        example_tasks = [
            ("Buy groceries", 0),
            ("Read a book", 0),
            ("Complete Week 3 assignment", 1),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            example_tasks,
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row):
    """Convert a sqlite3.Row to a plain dict with `done` as a boolean."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def get_all_tasks(search=None, done=None, sort_by_title=False):
    """Return every task, with optional filtering and sorting.

    Parameters
    ----------
    search : str | None
        If provided, filter tasks whose title contains this substring (LIKE).
    done : bool | None
        If provided, filter by completion status.
    sort_by_title : bool
        If True, results are ordered alphabetically by title.
    """
    conn = get_connection()
    query = "SELECT * FROM tasks"
    params = []
    conditions = []

    if search is not None:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_by_title:
        query += " ORDER BY title ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_task_by_id(task_id):
    """Return a single task dict or None if not found."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def create_task(title):
    """Insert a new task and return it as a dict (with its new id)."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, 0)", (title,)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, "title": title, "done": False}


def update_task(task_id, title=None, done=None):
    """Update an existing task.  Returns the updated dict, or None if not found."""
    conn = get_connection()

    # Check existence first
    existing = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if existing is None:
        conn.close()
        return None

    # Build dynamic SET clause
    fields = []
    params = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if done is not None:
        fields.append("done = ?")
        params.append(1 if done else 0)

    if fields:
        params.append(task_id)
        conn.execute(
            f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params
        )
        conn.commit()

    # Return the updated row
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()
    return _row_to_dict(row)


def delete_task(task_id):
    """Delete a task.  Returns True if a row was deleted, False otherwise."""
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_stats():
    """Return aggregate statistics about tasks."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 1"
    ).fetchone()[0]
    pending = total - completed
    conn.close()
    return {"total": total, "completed": completed, "pending": pending}
