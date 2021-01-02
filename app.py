import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_log")
def get_log():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if the email already exists in the database
        existing_user_email = mongo.db.users.find_one(
            {"email": request.form.get("email")})
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})
        if existing_user_email:
            flash("Email already in user")
            return redirect(url_for("register"))
        if existing_user:
            flash("Username already in user")
            return redirect(url_for("register"))
        register = {
            "email": request.form.get("email"),
            "username": request.form.get("username"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username")
        flash("Registraion Succsessful")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in database
        exitsing_user = mongo.db.users.find_one(
             {"username": request.form.get("username")})

        if exitsing_user:
            # ensure hashed password matches user input
            if check_password_hash(
             exitsing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username")
                return redirect(url_for("logs"))
            else:
                # invalid password
                flash("Username and/or Password is incorrect")
                return redirect(url_for("login"))
        else:
            # username does not exist
            flash("Username and/or Password is incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logs")
def logs():
    if session["user"]:
        logs = mongo.db.logs.find()
        return render_template("logs.html", logs=logs)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_log", methods=["GET", "POST"])
def add_log():
    if request.method == "POST":
        ride_again = "Yes" if request.form.get("ride_again") else "No"
        log = {
            "name": request.form.get("name_of_ride"),
            "description": request.form.get("description"),
            "date": request.form.get("date_of_ride"),
            "location": request.form.get("location"),
            "discipline": request.form.get("discipline"),
            "grade": request.form.get("grade"),
            "weather": request.form.get("weather"),
            "trail_condtions": request.form.get("trail_condtions"),
            "bike_used": request.form.get("bike_used"),
            "ride_again": ride_again,
            "created_by": session['user']
        }
        mongo.db.logs.insert_one(log)
        flash('Task Successfully Added')
        return redirect(url_for("logs"))
    disciplines = mongo.db.discipline.find().sort("discipline_name", 1)
    conditions = mongo.db.conditions.find().sort("condition_name", 1)
    return render_template(
        "add_log.html",
        disciplines=disciplines,
        conditions=conditions
     )


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
