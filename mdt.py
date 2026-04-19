from flask import Flask, request, redirect, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------------- DB ----------------
def get_db():
    return sqlite3.connect("mdt.db")


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        rank TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS citizens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT,
        owner TEXT
    )""")

    try:
        c.execute("INSERT INTO users (username,password,role,rank) VALUES (?,?,?,?)",
                  ("admin", generate_password_hash("1234"), "ADMIN", "Chief"))
    except:
        pass

    conn.commit()
    conn.close()


init_db()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["user"]
        p = request.form["pass"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (u,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], p):
            session["user"] = user[1]
            session["role"] = user[3]
            session["rank"] = user[4]
            return redirect("/dashboard")

    return render_template_string("""
    <body style="background:#0b1220;color:white;font-family:sans-serif;text-align:center;">
    <h1>LAPD / CHP MDT</h1>
    <form method="post">
    <input name="user" placeholder="Username"><br><br>
    <input name="pass" type="password"><br><br>
    <button>Login</button>
    </form>
    </body>
    """)


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM citizens")
    citizens = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM vehicles")
    vehicles = c.fetchone()[0]

    conn.close()

    return render_template_string(f"""
    <body style="background:#0b1220;color:white;font-family:sans-serif;">
    <h1>Dashboard</h1>

    <p>User: {session['user']} ({session['role']} - {session['rank']})</p>

    <p>Citizens: {citizens}</p>
    <p>Vehicles: {vehicles}</p>

    <a href="/citizens">Citizens DB</a><br>
    <a href="/vehicles">Vehicles DB</a><br>
    <a href="/logout">Logout</a>
    </body>
    """)


# ---------------- CITIZENS ----------------
@app.route("/citizens")
def citizens():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM citizens")
    data = c.fetchall()
    conn.close()

    html = "<h2>Citizens</h2><form method='post' action='/add_citizen'>"
    html += "<input name='name' placeholder='Name'>"
    html += "<input name='dob' placeholder='DOB'>"
    html += "<button>Add</button></form><ul>"

    for c in data:
        html += f"<li>{c[1]} ({c[2]}) <a href='/delete_citizen/{c[0]}'>Delete</a></li>"

    html += "</ul><a href='/dashboard'>Back</a>"
    return html


@app.route("/add_citizen", methods=["POST"])
def add_citizen():
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO citizens (name,dob) VALUES (?,?)",
              (request.form["name"], request.form["dob"]))
    conn.commit()
    conn.close()
    return redirect("/citizens")


@app.route("/delete_citizen/<int:id>")
def delete_citizen(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM citizens WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/citizens")


# ---------------- VEHICLES ----------------
@app.route("/vehicles")
def vehicles():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM vehicles")
    data = c.fetchall()
    conn.close()

    html = "<h2>Vehicles</h2><form method='post' action='/add_vehicle'>"
    html += "<input name='plate' placeholder='Plate'>"
    html += "<input name='owner' placeholder='Owner'>"
    html += "<button>Add</button></form><ul>"

    for v in data:
        html += f"<li>{v[1]} ({v[2]}) <a href='/delete_vehicle/{v[0]}'>Delete</a></li>"

    html += "</ul><a href='/dashboard'>Back</a>"
    return html


@app.route("/add_vehicle", methods=["POST"])
def add_vehicle():
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO vehicles (plate,owner) VALUES (?,?)",
              (request.form["plate"], request.form["owner"]))
    conn.commit()
    conn.close()
    return redirect("/vehicles")


@app.route("/delete_vehicle/<int:id>")
def delete_vehicle(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM vehicles WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/vehicles")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
