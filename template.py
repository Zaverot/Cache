import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session
from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd


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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
database = sqlite3.connect('tripleh.db')
db = database.cursor()


# Returns the landing page of Harvard House Hunting
@app.route("/")
def index():


    database = sqlite3.connect('tripleh.db')
    db = database.cursor()
    # Returns default landing page if user is not logged in
    if session.get("user_id") is None:
        return render_template("landing.html")
    # Returns signed in index page if user is logged in
    else:
        userName = (db.execute("SELECT * FROM users WHERE id = ?", session["user_id"]))[0]["username"]
        houses = (db.execute(
            "SELECT * FROM houses JOIN history ON history.house_id = houses.id JOIN users ON history.user_id = users.id WHERE users.id = ? LIMIT 5", session["user_id"]))
        return render_template("index.html", userName=userName, houses=houses)


# Allows the user to log in after registering.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    database = sqlite3.connect('tripleh.db')
    db = database.cursor()

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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

    database = sqlite3.connect('tripleh.db')
    db = database.cursor()

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


# Allows user to find friends
@app.route("/find_friends", methods=["GET", "POST"])
@login_required
def find_friends():
    database = sqlite3.connect('tripleh.db')
    db = database.cursor()
    if request.method == "POST":

        # Checks the submissions of user in the form
        criteria = request.form.get("criteria")
        if not criteria:
            return apology("Must have search terms for friends", 400)

        # Search for list of qualified users and removes duplicates
        qualified_users = []
        query = criteria.split(", ")
        for crit in query:
            qualified_users.extend(db.execute("SELECT * FROM users WHERE about_you LIKE ? ", '%' + crit + '%'))
        qu = []
        [qu.append(x) for x in qualified_users if x not in qu]

        # Returns the users based on submitted query
        return render_template("friends_found.html", qu=qu)

    else:
        return render_template("find_friends.html")


# Allows new users to register
@app.route("/register", methods=["GET", "POST"])
def register():
    database = sqlite3.connect('tripleh.db')
    db = database.cursor()
    if request.method == "POST":

        # Get user form input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure confirmation password was submitted
        elif not confirmation:
            return apology("must provide confirmation password", 400)

        # Ensure both passwords match
        elif confirmation != password:
            return apology("Passwords must match!", 400)

        if (db.execute("SELECT COUNT(*) FROM users WHERE username = ?", username))[0]['COUNT(*)'] != 0:
            return apology("that username is taken already", 400)

        # Insert into database
        db.execute("INSERT INTO users (username, hash) VALUES( ?, ?)", username, generate_password_hash(password))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
