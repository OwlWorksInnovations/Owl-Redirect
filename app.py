# IMPORTS
import os
import flask
from flask import session, request, redirect, url_for

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(1024)

# GLOBAL VARIABLES

# FUNCTIONS

# ROUTES
@app.route("/")
# INDEX
def index():
    return flask.render_template("index.html")

@app.route("/dashboard")
# DASHBOARD
def dashboard():
    if 'username' in session:
        username = session['username'] = 'admin'
        return flask.render_template("dashboard.html")
    else:
        return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"

@app.route("/login", methods = ["GET", "POST"])
# LOGIN
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect("/")
    return flask.render_template("login.html")

@app.route('/logout')
# LOGOUT
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
