# CRUD API with SQLite

A Python/Flask REST API for managing tasks, backed by a **SQLite** database. Data persists across server restarts.

## Why SQLite?

| Reason | Detail |
|---|---|
| **Zero setup** | SQLite is bundled with Python — no separate database server to install or configure. |
| **Single file** | The entire database lives in one file (`tasks.db`), making it easy to inspect, back up, or reset. |
| **Perfect for learning** | It supports full SQL (SELECT, INSERT, UPDATE, DELETE) so every concept transfers directly to PostgreSQL, MySQL, etc. |

## Where is the database?

The database file is automatically created at:

```
w3-sqlite-crud/tasks.db
```

The first time the server starts it will:
1. Create the file if it doesn't exist.
2. Create the `tasks` table if it doesn't exist.
3. Seed three example tasks **only** if the table is empty.

## How to Run

```bash
# 1. Navigate into the project folder
cd w3-sqlite-crud

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python app.py
```

The API will be available at **http://localhost:5000**.

## API Endpoints

| Method | URL | Description | Success | Error |
|--------|-----|-------------|---------|-------|
| `GET` | `/tasks` | List all tasks | `200` | — |
| `GET` | `/tasks/<id>` | Get one task | `200` | `404` |
| `POST` | `/tasks` | Create a task | `201` | `400` |
| `PUT` | `/tasks/<id>` | Update a task | `200` | `400` / `404` |
| `DELETE` | `/tasks/<id>` | Delete a task | `200` | `404` |
| `GET` | `/stats` | Task statistics | `200` | — |

### Optional query parameters on `GET /tasks`

| Parameter | Example | Effect |
|-----------|---------|--------|
| `search` | `/tasks?search=milk` | Filter titles containing substring (SQL `LIKE`) |
| `done` | `/tasks?done=true` | Filter by completion status |
| `sort` | `/tasks?sort=title` | Sort alphabetically by title |

## Example SQL Queries

You can open `tasks.db` in any SQLite viewer (e.g. **DB Browser for SQLite**) and run queries directly:

```sql
-- List every task
SELECT * FROM tasks;

-- Show only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- Count all tasks
SELECT COUNT(*) FROM tasks;

-- Mark every task as completed
UPDATE tasks SET done = 1;

-- Delete all completed tasks
DELETE FROM tasks WHERE done = 1;
```

Changes made directly in the database are **immediately** reflected by the API.

## Project Structure

```
w3-sqlite-crud/
├── app.py              # Flask routes (API layer)
├── database.py         # SQLite logic (data layer)
├── requirements.txt    # Python dependencies
├── tasks.db            # SQLite database (auto-created)
└── README.md           # This file
```


---
