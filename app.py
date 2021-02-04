import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session 
from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required 

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Use filesystem for session
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Returns the landing page of Cache
@app.route("/")
def index():
    
    # Returns default landing page if user is not logged in
    if session.get("user_id") is None:
        return render_template("landing.html")
    # Returns signed in index page if user is logged in
    else:
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row

        db = database.cursor()
        db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]])
        userName = db.fetchone()
        db.execute(
            "SELECT * FROM users JOIN shipments ON shipments.user_id = users.id WHERE users.id = ? LIMIT 5", [session["user_id"]])
        shipments = db.fetchall()
        return render_template("index.html", userName=userName, shipments=shipments)


# Allows the user to log in after registering.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ask for username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect Database
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row

        db = database.cursor()
        db.execute("SELECT * FROM users WHERE username = ?", [username])
        rows = db.fetchall()

        # Ensure username and password exists, and password is correct
        if not username or not password or len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password", 'error')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Logs the user out
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Allows users to check their profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
    
        # Connect database
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row
        db = database.cursor()

        db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]])
        userInfo = db.fetchone()

        return render_template("update_profile.html", userInfo=userInfo)
    else:
        # Connect and query database
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row
        db = database.cursor()
        db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]])
        userInfo = db.fetchone()

        return render_template("profile.html", userInfo=userInfo)


# Allows users to update their profile
@app.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():

    # Gets user self and ideal roommate description from form.
    if request.method == "POST":
        description = request.form.get("description")
        contact = request.form.get("contact")

        # Connect to database
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row
        db = database.cursor()

        # Updates user database with new information
        db.execute("UPDATE users SET personalInfo = ?, contact = ? WHERE id = ?",
                   (description, contact, session["user_id"]))
        database.commit()

        # Retrieves newly updated user information
        db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]])
        userInfo = db.fetchone()

        # Returns user to their own profile page with all necessary info
        return render_template("profile.html", userInfo=userInfo)

    else:
        return render_template("update_profile.html")

# Allows user to find friends
@app.route("/find_friends", methods=["GET", "POST"])
@login_required
def find_friends():
    if request.method == "POST":

        # Checks the submissions of user in the form
        criteria = request.form.get("criteria")
        if not criteria:
            flash("Must have search terms for friends")
            return render_template("findOthers.html")

        # Connect to database
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row
        db = database.cursor()

        # Search for list of qualified users and removes duplicates
        qualified_users = []
        query = criteria.split(", ")
        for crit in query:
            qualified_users.extend(db.execute("SELECT * FROM users WHERE personalInfo LIKE ? ", ['%' + crit + '%']))
        qu = []
        [qu.append(x) for x in qualified_users if x not in qu]

        # Returns the users based on submitted query
        return render_template("othersFound.html", qu=qu)

    else:
        return render_template("findOthers.html")

# Allows new users to register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Get user form input
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        contact = request.form.get("contact")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure all fields are submitted
        if not username or not password or not confirmation or not firstName or not lastName or not contact:
            flash("Please fill in all fields!")
            return render_template("register.html") 

        # Ensure both passwords match
        elif confirmation != password:
            flash("Passwords must match!")
            return render_template("register.html")

        # Connect to database
        database = sqlite3.connect('cache.db')
        database.row_factory = sqlite3.Row
        db = database.cursor()

        db.execute("SELECT * FROM users WHERE username = ?", [username])
        rows = db.fetchall()

        # Check for duplicate username
        if len(rows) != 0:
            flash("That username is taken already.")
            return render_template("register.html")

        # Insert into database
        db.execute("INSERT INTO users (username, hash, firstName, lastName, contact) VALUES( ?, ?, ?, ?, ?)", (username, generate_password_hash(password), firstName, lastName, contact))
        database.commit()
        # Redirect user to home page
        return redirect("/")

    # Return empty register page
    else:
        return render_template("register.html")

# Handle Errors
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    flash(e.name + str(e.code))
    return redirect("/")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
