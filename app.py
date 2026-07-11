import joblib
import sqlite3
from flask import Flask, render_template, request, redirect, session

# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)
app.secret_key = "student_dropout_secret_key"

# ==========================================
# DATABASE
# ==========================================

DATABASE = "students.db"

# ==========================================
# LOAD AI MODEL
# ==========================================

model = joblib.load("model/dropout_model.pkl")

# ==========================================
# CREATE DATABASE
# ==========================================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS students(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        usn TEXT NOT NULL,

        department TEXT NOT NULL,

        semester TEXT NOT NULL,

        attendance REAL,

        cgpa REAL,

        internal_marks REAL,

        backlogs INTEGER,

        assignments INTEGER,

        behavior INTEGER,

        risk TEXT,

        risk_score INTEGER

    )

    """)

    conn.commit()

    conn.close()


init_db()

# ==========================================
# LOGIN USERS
# ==========================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

STUDENT_USERNAME = "student"
STUDENT_PASSWORD = "student123"
# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    # User already logged in
    if "user" in session:

        # Admin
        if session.get("role") == "admin":
            return redirect("/dashboard")

        # Student
        elif session.get("role") == "student":
            return redirect("/predict")

    # Not Logged In
    return redirect("/login")


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # -----------------------------
        # ADMIN LOGIN
        # -----------------------------
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session.clear()

            session["user"] = username
            session["role"] = "admin"

            return redirect("/dashboard")

        # -----------------------------
        # STUDENT LOGIN
        # -----------------------------
        elif username == STUDENT_USERNAME and password == STUDENT_PASSWORD:

            session.clear()

            session["user"] = username
            session["role"] = "student"

            return redirect("/predict")

        else:

            error = "Invalid Username or Password"

    return render_template(
        "login.html",
        error=error
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
# ==========================================
# STUDENT PREDICTION (AI MODEL)
# ==========================================

@app.route("/predict", methods=["GET", "POST"])
def predict():

    # Login Required
    if "user" not in session:
        return redirect("/login")

    # Student Only
    if session.get("role") != "student":
        return "Access Denied"

    if request.method == "POST":

        # -----------------------------
        # Student Details
        # -----------------------------

        name = request.form["name"]
        usn = request.form["usn"]
        department = request.form["department"]
        semester = request.form["semester"]

        # -----------------------------
        # Academic Details
        # -----------------------------

        attendance = float(request.form["attendance"])
        cgpa = float(request.form["cgpa"])
        internal = float(request.form["internal"])
        backlogs = int(request.form["backlogs"])
        assignments = int(request.form["assignments"])
        behavior = int(request.form["behavior"])

        # -----------------------------
        # AI MODEL PREDICTION
        # -----------------------------

        prediction = model.predict([[
            attendance,
            cgpa,
            internal,
            backlogs,
            assignments,
            behavior
        ]])

        risk = prediction[0]

        # -----------------------------
        # Display Score
        # -----------------------------

        if risk == "HIGH":
            score = 85
            reasons = [
                "High probability of dropout",
                "Immediate counselling required"
            ]

        elif risk == "MEDIUM":
            score = 55
            reasons = [
                "Needs regular monitoring",
                "Academic improvement recommended"
            ]

        else:
            score = 20
            reasons = [
                "Student performing well",
                "Continue current progress"
            ]

        # -----------------------------
        # Save Student
        # -----------------------------

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO students(

            name,
            usn,
            department,
            semester,
            attendance,
            cgpa,
            internal_marks,
            backlogs,
            assignments,
            behavior,
            risk,
            risk_score

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)

        """, (

            name,
            usn,
            department,
            semester,
            attendance,
            cgpa,
            internal,
            backlogs,
            assignments,
            behavior,
            risk,
            score

        ))

        conn.commit()

        conn.close()

        # -----------------------------
        # Save Result in Session
        # -----------------------------

        session["student"] = name
        session["usn"] = usn
        session["risk"] = risk
        session["score"] = score
        session["reasons"] = ", ".join(reasons)

        return redirect("/result")

    return render_template("predict.html")
# ==========================================
# STUDENT RESULT
# ==========================================

@app.route("/result")
def result():

    # User must login
    if "user" not in session:
        return redirect("/login")

    # Student only
    if session.get("role") != "student":
        return "Access Denied"

    return render_template(

        "result.html",

        student=session.get("student"),

        usn=session.get("usn"),

        risk=session.get("risk"),

        score=session.get("score"),

        reasons=session.get("reasons")

    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    # Login Required
    if "user" not in session:
        return redirect("/login")

    # Admin Only
    if session.get("role") != "admin":
        return "Access Denied"

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # High Risk
    cursor.execute("SELECT COUNT(*) FROM students WHERE risk='HIGH'")
    high_risk = cursor.fetchone()[0]

    # Medium Risk
    cursor.execute("SELECT COUNT(*) FROM students WHERE risk='MEDIUM'")
    medium_risk = cursor.fetchone()[0]

    # Low Risk
    cursor.execute("SELECT COUNT(*) FROM students WHERE risk='LOW'")
    low_risk = cursor.fetchone()[0]

    # Latest Students
    cursor.execute("""

        SELECT

            id,

            name,

            usn,

            department,

            semester,

            attendance,

            cgpa,

            risk,

            risk_score

        FROM students

        ORDER BY id DESC

        LIMIT 10

    """)

    recent_students = cursor.fetchall()

    conn.close()

    return render_template(

        "dashboard.html",

        admin=session.get("user"),

        total_students=total_students,

        high_risk=high_risk,

        medium_risk=medium_risk,

        low_risk=low_risk,

        recent_students=recent_students

    )
    # ==========================================
# STUDENTS MANAGEMENT
# ==========================================

@app.route("/students")
def students():

    # Login Required
    if "user" not in session:
        return redirect("/login")

    # Admin Only
    if session.get("role") != "admin":
        return "Access Denied"

    search = request.args.get("search", "").strip()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search:

        cursor.execute("""

        SELECT *

        FROM students

        WHERE

        name LIKE ?

        OR usn LIKE ?

        OR department LIKE ?

        ORDER BY id DESC

        """,

        (

            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"

        ))

    else:

        cursor.execute("""

        SELECT *

        FROM students

        ORDER BY id DESC

        """)

    students = cursor.fetchall()

    conn.close()

    return render_template(

        "students.html",

        students=students,

        search=search

    )


# ==========================================
# DELETE STUDENT
# ==========================================

@app.route("/delete/<int:id>")
def delete_student(id):

    # Login Required
    if "user" not in session:
        return redirect("/login")

    # Admin Only
    if session.get("role") != "admin":
        return "Access Denied"

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM students WHERE id=?",

        (id,)

    )

    conn.commit()

    conn.close()

    return redirect("/students")
# ==========================================
# ANALYTICS
# ==========================================

@app.route("/analytics")
def analytics():

    # Login Required
    if "user" not in session:
        return redirect("/login")

    # Admin Only
    if session.get("role") != "admin":
        return "Access Denied"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # -----------------------------
    # Total Students
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # -----------------------------
    # High Risk
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM students WHERE risk='HIGH'")
    high_risk = cursor.fetchone()[0]

    # -----------------------------
    # Medium Risk
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM students WHERE risk='MEDIUM'")
    medium_risk = cursor.fetchone()[0]

    # -----------------------------
    # Low Risk
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM students WHERE risk='LOW'")
    low_risk = cursor.fetchone()[0]

    conn.close()

    # -----------------------------
    # Calculate Percentage
    # -----------------------------

    if total_students > 0:

        high_percentage = round((high_risk / total_students) * 100, 2)

        medium_percentage = round((medium_risk / total_students) * 100, 2)

        low_percentage = round((low_risk / total_students) * 100, 2)

    else:

        high_percentage = 0

        medium_percentage = 0

        low_percentage = 0

    return render_template(

        "analytics.html",

        total_students=total_students,

        high_risk=high_risk,

        medium_risk=medium_risk,

        low_risk=low_risk,

        high_percentage=high_percentage,

        medium_percentage=medium_percentage,

        low_percentage=low_percentage

    )
    # ==========================================
# REPORTS
# ==========================================

@app.route("/reports")
def reports():

    # Login Required
    if "user" not in session:
        return redirect("/login")

    # Admin Only
    if session.get("role") != "admin":
        return "Access Denied"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            id,
            name,
            usn,
            department,
            semester,
            attendance,
            cgpa,
            internal_marks,
            backlogs,
            assignments,
            behavior,
            risk,
            risk_score

        FROM students

        ORDER BY id DESC

    """)

    students = cursor.fetchall()

    conn.close()

    return render_template(

        "reports.html",

        students=students

    )
    # ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
    if __name__ == "__main__":
      app.run(host="0.0.0.0", port=5000, debug=True)