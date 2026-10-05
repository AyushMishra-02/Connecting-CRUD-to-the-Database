"""
app.py — Flask CRUD API backed by SQLite.

Endpoints
---------
GET    /tasks          List all tasks  (optional: ?search=..., ?done=true|false, ?sort=title)
GET    /tasks/<id>     Get a single task
POST   /tasks          Create a new task   { "title": "..." }
PUT    /tasks/<id>     Update a task        { "title": "...", "done": true|false }
DELETE /tasks/<id>     Delete a task
GET    /stats          Aggregate task statistics
"""

from flask import Flask, request, jsonify
from database import init_db, get_all_tasks, get_task_by_id, create_task, update_task, delete_task, get_stats

app = Flask(__name__)

# Initialize the database (create table + seed) on startup
init_db()


# ---------------------------------------------------------------------------
# Stage 1 — READ
# ---------------------------------------------------------------------------

@app.route("/tasks", methods=["GET"])
def list_tasks():
    """Return all tasks.  Supports optional query parameters:

    • ?search=<substring>   — filter by title (SQL LIKE)
    • ?done=true|false      — filter by completion status
    • ?sort=title           — sort alphabetically
    """
    search = request.args.get("search")
    done_param = request.args.get("done")
    sort_param = request.args.get("sort")

    done = None
    if done_param is not None:
        done = done_param.lower() == "true"

    sort_by_title = sort_param is not None and sort_param.lower() == "title"

    tasks = get_all_tasks(search=search, done=done, sort_by_title=sort_by_title)
    return jsonify(tasks), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_single_task(task_id):
    """Return a single task or 404."""
    task = get_task_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200


# ---------------------------------------------------------------------------
# Stage 2 — CREATE
# ---------------------------------------------------------------------------

@app.route("/tasks", methods=["POST"])
def create_new_task():
    """Create a new task.  Expects JSON body with at least `title`."""
    data = request.get_json(silent=True)

    if data is None or "title" not in data:
        return jsonify({"error": "Missing title"}), 400

    title = data["title"]
    if not isinstance(title, str) or title.strip() == "":
        return jsonify({"error": "Title must be a non-empty string"}), 400

    task = create_task(title.strip())
    return jsonify(task), 201


# ---------------------------------------------------------------------------
# Stage 3 — UPDATE & DELETE
# ---------------------------------------------------------------------------

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_existing_task(task_id):
    """Update a task's title and/or done status."""
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    title = data.get("title")
    done = data.get("done")

    # Validate title if provided
    if title is not None and (not isinstance(title, str) or title.strip() == ""):
        return jsonify({"error": "Title must be a non-empty string"}), 400

    # Validate done if provided
    if done is not None and not isinstance(done, bool):
        return jsonify({"error": "done must be a boolean"}), 400

    if title is not None:
        title = title.strip()

    task = update_task(task_id, title=title, done=done)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_existing_task(task_id):
    """Delete a task by id."""
    deleted = delete_task(task_id)
    if not deleted:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted"}), 200


# ---------------------------------------------------------------------------
# ★ Optional — Statistics
# ---------------------------------------------------------------------------

@app.route("/stats", methods=["GET"])
def task_stats():
    """Return aggregate counts computed via SQL COUNT()."""
    stats = get_stats()
    return jsonify(stats), 200


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Task API running at http://localhost:5000")
    app.run(debug=True, port=5000)
