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
        user = mongo.db.users.insert_one(register)
        # put the new user into 'session' cookie
        session["user"] = request.form.get("username")
        session['user_id'] = str(user.inserted_id)
        return redirect(url_for("logs"))
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
                session['user_id'] = str(exitsing_user['_id'])
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
    if "user" in session:
        logs = list(mongo.db.logs.find())
        return render_template("logs.html", logs=logs)
    return redirect(url_for("login"))


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    logs = list(mongo.db.logs.find({"$text": {"$search": query}}))
    return render_template("logs.html", logs=logs)


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
            "trail_conditions": request.form.get("trail_conditions"),
            "distance": request.form.get("distance"),
            "elevation": request.form.get("elevation"),
            "bike_used": request.form.get("bike_used"),
            "ride_again": ride_again,
            "user_id": ObjectId(session['user_id']),
            "created_by": session['user']
        }
        mongo.db.logs.insert_one(log)
        flash('Log Successfully Added')
        return redirect(url_for("logs"))
    disciplines = mongo.db.discipline.find().sort("discipline_name", 1)
    conditions = mongo.db.conditions.find().sort("condition_name", 1)
    return render_template(
        "add_log.html",
        disciplines=disciplines,
        conditions=conditions
     )


@app.route("/edit_log/<log_id>", methods=["GET", "POST"])
def edit_log(log_id):
    if request.method == "POST":
        ride_again = "Yes" if request.form.get("ride_again") else "No"
        edit = {
            "name": request.form.get("name_of_ride"),
            "description": request.form.get("description"),
            "date": request.form.get("date_of_ride"),
            "location": request.form.get("location"),
            "discipline": request.form.get("discipline"),
            "grade": request.form.get("grade"),
            "weather": request.form.get("weather"),
            "trail_conditions": request.form.get("trail_conditions"),
            "distance": request.form.get("distance"),
            "elevation": request.form.get("elevation"),
            "bike_used": request.form.get("bike_used"),
            "ride_again": ride_again,
            "created_by": session['user']
        }
        mongo.db.logs.update({"_id": ObjectId(log_id)}, edit)
        flash('Log Successfully Edited')
        return redirect(url_for("logs"))
    log = mongo.db.logs.find_one({"_id": ObjectId(log_id)})
    disciplines = mongo.db.discipline.find().sort("discipline_name", 1)
    conditions = mongo.db.conditions.find().sort("condition_name", 1)
    return render_template(
        "edit_log.html",
        log=log,
        disciplines=disciplines,
        conditions=conditions
     )


@app.route("/delete_log/<log_id>")
def delete_log(log_id):
    mongo.db.logs.remove({"_id": ObjectId(log_id)})
    flash("Log Deleted")
    return redirect(url_for("logs"))


@app.route("/admin")
def admin():
    disciplines = list(mongo.db.discipline.find().sort("discipline_name", 1))
    conditions = list(mongo.db.conditions.find().sort("condition_name", 1))
    return render_template(
                        "admin.html",
                        disciplines=disciplines,
                        conditions=conditions
                    )


@app.route("/add_discipline", methods=["GET", "POST"])
def add_discipline():
    if request.method == "POST":
        add = {
            "discipline_name": request.form.get("discipline").lower()
        }
    mongo.db.discipline.insert_one(add)
    flash('Discipline Successfully Added')
    return redirect(url_for("admin"))


@app.route("/add_condition", methods=["GET", "POST"])
def add_condition():
    if request.method == "POST":
        add = {
            "condition_name": request.form.get("condition").lower()
        }
    mongo.db.conditions.insert_one(add)
    flash('Condition Successfully Added')
    return redirect(url_for("admin"))


@app.route("/delete_discipline/<discipline_id>")
def delete_discipline(discipline_id):
    mongo.db.discipline.remove({"_id": ObjectId(discipline_id)})
    flash('Discipline Successfully Deleted')
    return redirect(url_for("admin"))


@app.route("/delete_condition/<condition_id>")
def delete_condition(condition_id):
    mongo.db.conditions.remove({"_id": ObjectId(condition_id)})
    flash('Condition Successfully Deleted')
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
