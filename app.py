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
    logs = mongo.db.logs.find()
    return render_template("home.html", logs=logs)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if the email already exists in the database
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})
        if existing_user:
            flash("Email already in user")
            return redirect(url_for("register"))

        register = {
            "email": request.form.get("email"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("email")
        flash("Registraion Succsessful")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in database
        exitsing_user = mongo.db.users.find_one(
             {"email": request.form.get("email")})

        if exitsing_user:
            # ensure hashed password matches user input
            if check_password_hash(exitsing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("email")
                return render_template("logs.html")
            else:
                # invalid password
                flash("Email and/or Password is incorrect")
                return redirect(url_for("login"))
        else:
            # email does not exist
            flash("Email and/or Password is incorrect")
            return redirect(url_for("login"))
    return render_template("login.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
