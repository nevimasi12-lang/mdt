from flask import Flask, render_template_string, request, redirect, session
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
app.secret_key = "mdtsecret"
socketio = SocketIO(app)

# DB INIT
def init_db():
    conn = sqlite3.connect("mdt.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS citizens (name TEXT, dob TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS vehicles (plate TEXT, owner TEXT)")

    # default user
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin','1234','admin')")
    conn.commit()
    conn.close()

init_db()

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["user"]
        p = request.form["pass"]

        conn = sqlite3.connect("mdt.db")
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (u,p))
        res = c.fetchone()
        conn.close()

        if res:
            session["user"] = u
            session["role"] = res[0]
            return redirect("/dashboard")

    return """
    <body style="background:#0b1220;color:white;font-family:sans-serif;text-align:center;">
    <h1>ERZE MDT LOGIN</h1>
    <form method="post">
    <input name="user" placeholder="username"><br><br>
    <input name="pass" type="password"><br><br>
    <button>Login</button>
    </form>
    </body>
    """

# DASHBOARD
@app.route("/dashboard")
def dash():
    if "user" not in session:
        return redirect("/")

    return """
    <html>
    <head>
    <style>
    body {
        margin:0;
        background:#0b1220;
        color:white;
        font-family:sans-serif;
        display:flex;
    }

    .sidebar {
        width:250px;
        background:#111827;
        height:100vh;
        padding:20px;
    }

    .sidebar h2 {
        color:#4f9cff;
    }

    .sidebar a {
        display:block;
        margin:10px 0;
        color:white;
        text-decoration:none;
    }

    .main {
        flex:1;
        padding:20px;
    }

    .card {
        background:#1f2937;
        padding:20px;
        margin:10px;
        border-radius:10px;
    }
    </style>
    </head>

    <body>

    <div class="sidebar">
        <h2>LSPD MDT</h2>
        <a href="#">Dashboard</a>
        <a href="#">Citizens</a>
        <a href="#">Vehicles</a>
        <a href="#">Warrants</a>
    </div>

    <div class="main">
        <h1>Dashboard</h1>

        <div class="card">
            Citizen count: 57
        </div>

        <div class="card">
            Vehicle count: 1022
        </div>

    </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)