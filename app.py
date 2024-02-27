import sqlite3

from flask import Flask, redirect, flash, render_template, request, session
from flask_session import Session
from datetime import datetime, timedelta
from helpers import renderclimbing, renderrunning, renderreading, ontrack, initiateDB, closeDB, login_required
from werkzeug.security import check_password_hash, generate_password_hash


# Configure app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method =="POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Invalid username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Invalid password")
            return redirect("/login")

        username = request.form.get("username")
        # Query database for username
        # initiate db
        con, db = initiateDB()

        # Set up dict formatting
        con.row_factory = sqlite3.Row
        db = con.cursor()

        users = db.execute("""
                             SELECT *
                             FROM users
                             WHERE username = ?
                             """, (username, ) ).fetchall()

        # Ensure username exists and password is correct
        print(type(users))
        print(users)

        if len(users) != 1 or not check_password_hash(
            users[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = users[0]["id"]

        # Close db
        con.commit() # Commit db transaction
        closeDB(db, con)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/")
@login_required
def index():
    #get climbing variables
    climbs, ayy, bee, toClimbGoal = renderclimbing()
    climbProgressColor = ontrack(toClimbGoal)

    #get running variables
    runs, miles, pace, avgmiles, cals, toRunGoal = renderrunning()
    runProgressColor = ontrack(toRunGoal)

    #get reading variables
    books, days, pages, toReadGoal = renderreading()
    readProgressColor = ontrack(toReadGoal)

    #get total progress variables
    totalProgress = (toClimbGoal + toReadGoal + toRunGoal) / 3
    totalProgressColor = ontrack(totalProgress)

    return render_template("index.html",
                            #climbing variables
                            ayy=ayy,
                            bee=bee,
                            toclimbgoal=toClimbGoal,
                            climbProgressColor=climbProgressColor,

                            #running variables
                            miles=miles,
                            pace=pace,
                            avgmiles=avgmiles,
                            cals=cals,
                            torungoal=toRunGoal,
                            runProgressColor=runProgressColor,

                            #reading variables
                            days=days,
                            pages=pages,
                            toreadgoal=toReadGoal,
                            readProgressColor=readProgressColor,

                            #total progress variables
                            totalProgress=totalProgress,
                            totalProgressColor=totalProgressColor
                           )

@app.route("/climbing", methods=["GET", "POST"])
@login_required
def climb():
    # If user submits form
    if request.method == "POST":
        # TO DO: Need to add validation for form fields

        # Validate form values are present
        if (not request.form.get("name") or
            not request.form.get("grade") or
            not request.form.get("date") or
            not request.form.get("location") or
            not request.form.get("type")):
            flash("Error: Please enter all required fields")
            return redirect("/climbing")

        # Set form responses as variables
        name = request.form.get("name")
        grade = request.form.get("grade")
        date = request.form.get("date")
        location = request.form.get("location")
        type = request.form.get("type")
        comment = request.form.get("comment")
        data = [name,
                grade,
                date,
                location,
                type,
                comment]

        # Initiate db
        con, db = initiateDB()

        # db transaction
        db.execute("""
                   INSERT INTO climbing(
                   name,
                   grade,
                   date,
                   location,
                   type,
                   comment)
                   VALUES(?, ?, ?, ?, ?, ?)
                   """, data)

        # Close db
        con.commit() # Commit db transaction
        closeDB(db, con)

        return redirect("/climbing")

    # If user goes to page
    else:
        climbs, ayy, bee, toClimbGoal = renderclimbing()
        climbProgressColor = ontrack(toClimbGoal)
        return render_template("climbing.html",
                               climbs=climbs,
                               ayy=ayy,
                               bee=bee,
                               toclimbgoal=toClimbGoal,
                               climbProgressColor=climbProgressColor)


@app.route("/running", methods=["GET", "POST"])
@login_required
def run():
    # If user submits form
    if request.method == "POST":
        # Validation for form fields
        if (not request.form.get("distance") or
            not request.form.get("duration") or
            not request.form.get("location") or
            not request.form.get("date") or
            not request.form.get("calories") or
            not request.form.get("heart")):
            flash("Error: Please enter all required fields")
            return redirect("/running")

        # Set form responses as variables
        distance = float(request.form.get("distance"))

        #calculate seconds of duration
        duration = request.form.get("duration")
        h, m, s = duration.split(':')
        duration = int(h) * 3600 + int(m) * 60 + int(s)

        pace = int(round(duration / distance))
        location = request.form.get("location")
        date = request.form.get("date")
        calories = int(request.form.get("calories"))
        heart = int(request.form.get("heart"))
        data = [distance,
                duration,
                pace,
                location,
                date,
                calories,
                heart]

        # Initiative db
        con, db = initiateDB()

        # db transaction
        db.execute("""
                   INSERT INTO running(
                   distance,
                   duration,
                   pace,
                   location,
                   date,
                   calories,
                   heart)
                   VALUES(?, ?, ?, ?, ?, ?, ?)
                   """, data)

        # Close db
        con.commit() # Commit db transaction
        closeDB(db, con)

        return redirect("/running")

    # If user goes to page
    else:
        runs, miles, pace, avgmiles, cals, toRunGoal = renderrunning()
        runProgressColor = ontrack(toRunGoal)
        return render_template("running.html",
                               runs=runs,
                               miles=miles,
                               pace=pace,
                               avgmiles=avgmiles,
                               cals=cals,
                               torungoal=toRunGoal,
                               runProgressColor=runProgressColor)


@app.route("/reading", methods=["GET", "POST"])
@login_required
def read():
    if request.method == "POST":
        # Validation for form fields
        if (not request.form.get("title") or
            not request.form.get("author") or
            not request.form.get("start") or
            not request.form.get("end") or
            not request.form.get("pages")):
            flash("Error: Please enter all required fields")
            return redirect("/reading")


        # Set form responses as variables
        title = request.form.get("title")
        author = request.form.get("author")
        start = request.form.get("start")
        end = request.form.get("end")
        duration = ((datetime.strptime(request.form.get("end"), '%Y-%m-%d')) -
                    (datetime.strptime(request.form.get("start"), '%Y-%m-%d'))).days
        pages = request.form.get("pages")
        data = [title,
                author,
                start,
                end,
                duration,
                pages]

        # Initiate db
        con, db = initiateDB()

        # db transaction
        db.execute("""
                   INSERT INTO reading(
                   title,
                   author,
                   start,
                   end,
                   duration,
                   pages)
                   VALUES(?, ?, ?, ?, ?, ?)
                   """, data)

        # Close db
        con.commit() # Commit db transaction
        closeDB(db, con)

        return redirect("/reading")

    else:
        books, days, pages, toReadGoal = renderreading()
        readProgressColor = ontrack(toReadGoal)
        return render_template("reading.html",
                               books=books,
                               days=days,
                               pages=pages,
                               toreadgoal=toReadGoal,
                               readProgressColor=readProgressColor)

# @app.route("/delete", methods=["POST"]
# def delete():
# TO DO: create a route and function to delete selected entries

# @app.route("/update", methods=["POST"])
# def update():
# TO DO: create a route and function to update existing entries with new values
