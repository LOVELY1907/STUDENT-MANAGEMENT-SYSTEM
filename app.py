from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
import json

app = Flask(__name__)
app.secret_key = "dev_secret_for_demo"

BASE = Path(__file__).parent
DATA_FILE = BASE / "students.json"

def load_students():
    if not DATA_FILE.exists():
        save_students([])
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_students(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

# Load into memory (we re-save after each write to ensure persistence)
students = load_students()

def find_by_index(idx):
    try:
        return students[idx]
    except Exception:
        return None

@app.route("/")
def index():
    q = request.args.get("q", "").strip().lower()
    if q:
        filtered = [s for s in students if q in s.get("name","").lower() or q in s.get("roll","").lower() or q in s.get("course","").lower()]
    else:
        filtered = students
    return render_template("index.html", students=filtered, q=q)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        roll = request.form.get("roll","").strip()
        course = request.form.get("course","").strip()
        if not name or not roll:
            flash("Name and Roll Number are required.", "error")
            return redirect(url_for("add"))
        students.insert(0, {"name": name, "roll": roll, "course": course})
        save_students(students)
        flash("Student added successfully.", "success")
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    student = find_by_index(index)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form.get("name","").strip()
        roll = request.form.get("roll","").strip()
        course = request.form.get("course","").strip()
        if not name or not roll:
            flash("Name and Roll Number are required.", "error")
            return redirect(url_for("edit", index=index))
        students[index] = {"name": name, "roll": roll, "course": course}
        save_students(students)
        flash("Student updated.", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", student=student, index=index)

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    if 0 <= index < len(students):
        students.pop(index)
        save_students(students)
        flash("Student deleted.", "success")
    else:
        flash("Invalid index.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
