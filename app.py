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

# Configure session to use filesystem (instead of signed cookies)
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
        #db.execute(
        #    "SELECT * FROM houses JOIN history ON history.house_id = houses.id JOIN users ON history.user_id = users.id WHERE users.id = ? LIMIT 5", [session["user_id"]])
        #houses = db.fetchall()
        # userName = (db.execute("SELECT * FROM users WHERE id = ?", session["user_id"]))[0]["username"]
        #houses = (db.execute(
         #   "SELECT * FROM houses JOIN history ON history.house_id = houses.id JOIN users ON history.user_id = users.id WHERE users.id = ? LIMIT 5", session["user_id"]))
        return render_template("index.html", userName=userName)


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
        print(rows)

        # Ensure username exists and password is correct
        
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

    database = sqlite3.connect('tripleh.db')
    db = database.cursor()

    if request.method == "POST":
        about_you = db.execute("SELECT about_you FROM users WHERE id = ?", session["user_id"])[0]
        roommate_preferences = db.execute("SELECT roommate_preferences FROM users WHERE id = ?", session["user_id"])[0]
        contact = db.execute("SELECT contact FROM users WHERE id = ?", session["user_id"])[0]
        return render_template("update_profile.html", about_you=about_you, roommate_preferences=roommate_preferences, contact=contact)
    else:
        username = (db.execute("SELECT username FROM users WHERE id = ?", session["user_id"]))[0]['username']
        self_description = db.execute("SELECT about_you FROM users WHERE id = ?", session["user_id"])
        roommate_description = db.execute("SELECT roommate_preferences FROM users WHERE id = ?", session["user_id"])
        contact = db.execute("SELECT contact FROM users WHERE id = ?", session["user_id"])
        return render_template("profile.html", s=self_description, r=roommate_description, c=contact, username=username)


# Allows users to update their profile
@app.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():

    database = sqlite3.connect('tripleh.db')
    db = database.cursor()

    # Gets user self and ideal roommate description from form.
    if request.method == "POST":
        description = request.form.get("description")
        rdescription = request.form.get("rdescription")
        contact = request.form.get("contact")

        # Updates user database with new information
        db.execute("UPDATE users SET about_you = ?, roommate_preferences = ?, contact = ? WHERE id = ?",
                   description, rdescription, contact, session["user_id"])
        self_description = db.execute("SELECT about_you FROM users WHERE id = ?", session["user_id"])
        roommate_description = db.execute("SELECT roommate_preferences FROM users WHERE id = ?", session["user_id"])
        contact = db.execute("SELECT contact FROM users WHERE id = ?", session["user_id"])

        # Retrieves username again
        username = (db.execute("SELECT username FROM users WHERE id = ?", session["user_id"]))[0]['username']

        # Returns user to their own profile page with all necessary info
        return render_template("profile.html", s=self_description, r=roommate_description, c=contact, username=username)

    else:
        return render_template("update_profile.html")


# Allows user to query for houses
@app.route("/check", methods=["GET", "POST"])
@login_required
def check():

    database = sqlite3.connect('tripleh.db')
    db = database.cursor()
    
    # Checks the submissions of user in the form
    if request.method == "POST":
        minprice = request.form.get("minprice")
        maxprice = request.form.get("maxprice")
        bathrooms = request.form.get("bathrooms")
        bedrooms = request.form.get("bedrooms")
        distance = request.form.get("distance")
        people = request.form.get("people")

        # If no input from user for a particular field, the most flexible conditions are assumed
        if minprice == '':
            minprice = 0
        if maxprice == '':
            maxprice = 10000000
        if bathrooms == '':
            bathrooms = 0
        if bedrooms == '':
            bedrooms = 0
        if distance == '':
            distance = 100000000
        if people == '':
            people = 1

        # Cast fields as ints for comparisons and arithmetic

        people = int(people)
        bathrooms = int(bathrooms)
        bedrooms = int(bedrooms)
        minprice = int(minprice)
        maxprice = int(maxprice)
        distance = int(distance)

        # Querying houses database for required or preferred attributes
        houses = (db.execute(
            "SELECT * FROM houses WHERE price BETWEEN ? AND ? AND bed >= ? AND bathroom >= ? AND Hdistance*20 <= ?",
            minprice*people, maxprice*people, bedrooms, bathrooms, distance))

        house_id = (db.execute(
            "SELECT id FROM houses WHERE price BETWEEN ? AND ? AND bed >= ? AND bathroom >= ? AND Hdistance*20 <= ?",
            minprice*people, maxprice*people, bedrooms, bathrooms, distance))

        for nums in house_id:
            print(nums)
            db.execute("INSERT INTO history VALUES (CURRENT_TIMESTAMP, ?, ?)", nums['id'], session["user_id"])

        # Returns the checked houses based on submitted query
        return render_template("checked.html", houses=houses, people=int(people))

    else:
        return render_template("check.html")


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


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    flash(e.name + e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
