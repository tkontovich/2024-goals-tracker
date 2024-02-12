import sqlite3

from datetime import timedelta, datetime
from functools import wraps
from flask import Flask, redirect, flash, render_template, request, session
from flask_session import Session

# Set global vars for goals
RUNGOAL = 365
READGOAL = 24


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def initiateDB():
    con = sqlite3.connect("goals.db", check_same_thread=False) # Connect to db
    db = con.cursor() # Create db cursor
    return con, db


def closeDB(db, con):
    db.close() # Close cursor
    con.close() # Close connection


def ontrack(toGoal):
        day = datetime.now().timetuple().tm_yday
        yearProgress = (day / 365) * 100
        progressColor = ""

        if toGoal > (yearProgress + 5):
            return "bg-success"
        elif toGoal < (yearProgress - 5):
            return "bg-danger"
        else:
            return "bg-warning"
        

def renderclimbing():
    # Initiate db
    #con = sqlite3.connect("goals.db", check_same_thread=False) # Connect to db
    #db = con.cursor() # Create db cursor
    con, db = initiateDB()
    
    # Get dict of values from climbing table
    con.row_factory = sqlite3.Row 
    climbs = db.execute("""
                        SELECT * FROM climbing 
                        ORDER BY date DESC
                        """).fetchall()

    # Determine if goals hit
    ayy, ayyBool = "static/no.png", False
    bee, beeBool = "static/no.png", False
    toClimbGoal = 0
    for row in climbs: 
        if row["grade"] == "5.13a":
            ayy, ayyBool = "static/yes.png", True
        elif row["grade"] == "5.13b":
            bee, beeBool = "static/yes.png", True
    if ayyBool == True:
        toClimbGoal = toClimbGoal + 50
    if beeBool == True:
        toClimbGoal = toClimbGoal + 50

    # Close db
    closeDB(db, con)

    return climbs, ayy, bee, toClimbGoal


def renderrunning():
    # Initiate db
    con, db = initiateDB()
    
    # Set up variables based on db data
    miles = db.execute("""
                       SELECT SUM(distance) 
                       FROM running
                       """).fetchone()[0]
    duration = db.execute("""
                          SELECT SUM(duration) 
                          FROM running
                          """).fetchone()[0]
    avgmiles = db.execute("""
                          SELECT AVG(distance) 
                          FROM running
                          """).fetchone()[0]
    cals = db.execute("""
                      SELECT SUM(calories) 
                      FROM running
                      """).fetchone()[0]
    pace = timedelta(seconds=(round(duration / miles))) #determine average pace

    # determine progress to goal
    toRunGoal = (miles / RUNGOAL) * 100

    # Get dict of values from db
    con.row_factory = sqlite3.Row #Enable dictionary
    db = con.cursor() # Create db cursor
    runs = db.execute("""
                      SELECT * 
                      FROM running 
                      ORDER BY date DESC
                      """).fetchall()

    # Close db
    closeDB(db, con)

    return runs, miles, pace, avgmiles, cals, toRunGoal


def renderreading():
    # Initiate db
    con, db = initiateDB()

    # Set up variables based on db data
    pages = db.execute("""
                       SELECT SUM(pages) 
                       FROM reading
                       """).fetchone()[0]
    days = db.execute("""
                      SELECT AVG(duration) 
                      FROM reading
                      """).fetchone()[0]
    books = db.execute("""
                       SELECT COUNT(title) 
                       FROM reading
                       """).fetchone()[0]

    # Determine progress to goal
    toReadGoal = (books / READGOAL) * 100

    # Get dict of values from db
    con.row_factory = sqlite3.Row #Enable dictionary
    db = con.cursor() # Reset cursor w RowFactory
    books = db.execute("""
                       SELECT * 
                       FROM reading 
                       ORDER BY end DESC
                       """).fetchall()
    
    # Close db
    closeDB(db, con)

    return books, days, pages, toReadGoal    