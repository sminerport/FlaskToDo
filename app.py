from itertools import groupby
import sqlite3
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the secret key from the environment, or raise an error
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")

app.config['SECRET_KEY'] = secret_key

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    with get_db_connection() as conn:
        try:
            todos = conn.execute(
                """
                SELECT i.id, i.done, i.content, l.title
                FROM items i
                JOIN lists l ON i.list_id = l.id
                ORDER BY l.title;
            """
            ).fetchall()
        except sqlite3.Error as e:
            flash(f"Database error: {e}")
            return render_template("error.html")

        lists = {}
        if not todos:
            flash("No tasks found. Please add new tasks or lists.")
        else:
            for k, g in groupby(todos, key=lambda t: t["title"]):
                lists[k] = list(g)

    return render_template("index.html", lists=lists)


@app.route("/create/", methods=("GET", "POST"))
def create():
    with get_db_connection() as conn:  # Using context manager to handle connection automatically
        if request.method == "POST":
            content = request.form["content"]
            list_title = request.form["list"]
            new_list = request.form["new_list"]

            if not content:
                flash("Content is required!")
                return redirect(url_for("index"))

            # If a new list title is submitted, add it to the database
            if list_title == "New List" and new_list:
                try:
                    conn.execute("INSERT INTO lists (title) VALUES (?)", (new_list,))
                    conn.commit()
                    # Get the id of the newly added list in one query
                    list_id = conn.execute("SELECT last_insert_rowid();").fetchone()[0]
                except sqlite3.Error as e:
                    flash(f"Error creating new list: {e}")
                    return redirect(url_for("index"))
            else:
                # Fetch the existing list's id
                try:
                    list_id = conn.execute(
                        "SELECT id FROM lists WHERE title = ?;", (list_title,)
                    ).fetchone()["id"]
                except sqlite3.Error as e:
                    flash(f"Error fetching list: {e}")
                    return redirect(url_for("index"))

            try:
                # Insert the new to-do item
                conn.execute(
                    "INSERT INTO items (content, list_id) VALUES (?, ?)",
                    (content, list_id),
                )
                conn.commit()
            except sqlite3.Error as e:
                flash(f"Error creating new item: {e}")
                return redirect(url_for("index"))

            return redirect(url_for("index"))

        # Fetch lists for the dropdown in the create form
        try:
            lists = conn.execute("SELECT title FROM lists;").fetchall()
        except sqlite3.Error as e:
            flash(f"Error fetching lists: {e}")
            return redirect(url_for("index"))

    return render_template("create.html", lists=lists)


@app.route("/<int:id>/do/", methods=("POST",))
def do(id):
    try:
        with get_db_connection() as conn:
            conn.execute("UPDATE items SET done = 1 WHERE id = ?", (id,))
            conn.commit()
            flash("Task marked as done!")
    except sqlite3.Error as e:
        flash(f"Error updating task: {e}")
        return redirect(url_for("index"))

    return redirect(url_for("index"))


@app.route("/<int:id>/undo", methods=("POST",))
def undo(id):
    try:
        with get_db_connection() as conn:
            conn.execute("UPDATE items SET done = 0 WHERE id = ?", (id,))
            conn.commit()
            flash("Task marked as incomplete!")
    except sqlite3.Error as e:
        flash(f"Error updating task: {e}")
        return redirect(url_for("index"))

    return redirect(url_for("index"))


@app.route("/<int:id>/edit/", methods=("GET", "POST"))
def edit(id):
    try:
        with get_db_connection() as conn:
            # Fetch the task (todo) to be edited
            todo = conn.execute(
                """
                SELECT i.id, i.list_id, i.done, i.content, l.title
                FROM items i
                JOIN lists l ON i.list_id = l.id
                WHERE i.id = ?
            """,
                (id,),
            ).fetchone()

            if todo is None:
                flash("Task not found.")
                return redirect(url_for("index"))

            # Fetch all lists for the dropdown
            lists = conn.execute("SELECT title FROM lists;").fetchall()

            if request.method == "POST":
                content = request.form["content"]
                list_title = request.form["list"]

                if not content:
                    flash("Content is required!")
                    return redirect(url_for("edit", id=id))

                # Fetch the selected list's ID
                list_id = conn.execute(
                    "SELECT id FROM lists WHERE title = ?;", (list_title,)
                ).fetchone()

                if list_id is None:
                    flash("List not found.")
                    return redirect(url_for("edit", id=id))

                # Update the task
                conn.execute(
                    """
                    UPDATE items
                    SET content = ?, list_id = ?
                    WHERE id = ?
                """,
                    (content, list_id["id"], id),
                )

                conn.commit()

                flash("Task updated successfully!")
                return redirect(url_for("index"))

    except sqlite3.Error as e:
        flash(f"Database error: {e}")
        return redirect(url_for("index"))

    return render_template("edit.html", todo=todo, lists=lists)


@app.route("/<int:id>/delete/", methods=("POST",))
def delete(id):
    try:
        with get_db_connection() as conn:
            # Check if the task exists before attempting to delete
            task = conn.execute("SELECT id FROM items WHERE id = ?", (id,)).fetchone()

            if task is None:
                flash("Task not found.")
                return redirect(url_for("index"))

            # Delete the task
            conn.execute("DELETE FROM items WHERE id = ?", (id,))
            conn.commit()

            flash("Task deleted successfully!")

    except sqlite3.Error as e:
        flash(f"Error deleting task: {e}")
        return redirect(url_for("index"))

    return redirect(url_for("index"))
