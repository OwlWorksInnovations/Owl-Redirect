# IMPORTS
import os
import flask
from flask import session, request, redirect, url_for
import sqlite3
import string
import random

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
    
    # Check columns and add if they don't exist
    cursor.execute("PRAGMA table_info(urls)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'views' not in column_names:
        cursor.execute("ALTER TABLE urls ADD COLUMN views INTEGER DEFAULT 0")
    
    if 'name' not in column_names:
        cursor.execute("ALTER TABLE urls ADD COLUMN name TEXT")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, code TEXT, views INTEGER DEFAULT 0, name TEXT)")
    
    conn.commit()
    conn.close()

initialize_db()

# FUNCTIONS
def check_password_and_user(password, user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE password = ? AND username = ?", (password, user))
    if cursor.fetchone() is None:
        return False
    return True

# ROUTES
@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM urls")
        urls = cursor.fetchall()
        conn.close()
        
        # Generate full shortened URLs
        full_urls = []
        for url in urls:
            full_url = f"{request.host_url}url/{url['code']}"
            full_urls.append({
                'original_url': url['url'],
                'shortened_url': full_url,
                'name': url['name'] or '',
                'views': url['views']
            })
        
        return flask.render_template("dashboard.html", urls=full_urls)
    return "You are not logged in <br><a href = '/login'>click here to log in</a>"

@app.route("/dashboard/create-url", methods=["POST"])
def create_url():
    if 'username' in session:
        url = request.form['url']
        name = request.form.get('name', '')  # Optional name field
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        if url != "":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO urls (url, code) VALUES (?, ?)", (url, code))
            conn.commit()
            conn.close()
            return redirect("/dashboard")
        return "Invalid URL"
    return "You are not logged in <br><a href = '/login'>click here to log in</a>"

@app.route("/url/<code>", methods=["GET"])
def redirect_url(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url, views FROM urls WHERE code = ?", (code,))
    url_row = cursor.fetchone()
    
    if url_row:
        # Extract values safely
        original_url = url_row['url']
        current_views = url_row['views'] if url_row['views'] is not None else 0
        
        # Increment views
        new_views = current_views + 1
        cursor.execute("UPDATE urls SET views = ? WHERE code = ?", (new_views, code))
        conn.commit()
        conn.close()
        
        return redirect(original_url)
    
    conn.close()
    return flask.Response(
        "Not Found The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
        status=404,
    )
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




