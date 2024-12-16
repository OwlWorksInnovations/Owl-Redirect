# IMPORTS
import os
import flask
from flask import session, request, redirect, url_for
import sqlite3

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(1024)

# DATABASE
def get_db_connection():
    conn = sqlite3.connect('owlredirect.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
    conn.commit()
    conn.close()

initialize_db()

# FUNCTIONS
def check_password_and_user(password, user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE password = ?", (password,))
    cursor2 = conn.cursor()
    cursor2.execute("SELECT * FROM users WHERE username = ?", (user,))
    if cursor.fetchone() is None:
        return False
    if cursor2.fetchone() is None:
        return False
    return True

# ROUTES
@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        return flask.render_template("dashboard.html")
    return "You are not logged in <br><a href = '/login'>click here to log in</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = request.form['username']
        session['username'] = user
        password = request.form['password']
        if check_password_and_user(password, user):
            return redirect("/")
        return "Incorrect password", 401
    return flask.render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return flask.render_template("register.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)

