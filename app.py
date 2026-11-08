
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "students.db"

# Create database and table
def create_table():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

create_table()

# Home / Health check
@app.route("/")
def home():
    return jsonify({"message": "Student API is running"})

# GET - Fetch all students
@app.route("/students", methods=["GET"])
def get_students():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM students").fetchall()
    con.close()
    return jsonify([dict(row) for row in rows])

# GET - Fetch one student
@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT * FROM students WHERE id=?", (id,)
    ).fetchone()
    con.close()

    if row is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(row))

# POST - Add a student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}
    name, email = data.get("name"), data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    con = sqlite3.connect(DB)
    cur = con.execute(
        "INSERT INTO students(name,email) VALUES(?,?)",
        (name, email)
    )
    con.commit()
    sid = cur.lastrowid
    con.close()

    return jsonify({"message": "Student added", "id": sid}), 201

# PUT - Update a student
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True) or {}
    name, email = data.get("name"), data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    con = sqlite3.connect(DB)
    cur = con.execute(
        "UPDATE students SET name=?, email=? WHERE id=?",
        (name, email, id)
    )
    con.commit()
    con.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student updated"})

# DELETE - Remove a student
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    con = sqlite3.connect(DB)
    cur = con.execute("DELETE FROM students WHERE id=?", (id,))
    con.commit()
    con.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted"})

if __name__ == "__main__":
    app.run(debug=True)
