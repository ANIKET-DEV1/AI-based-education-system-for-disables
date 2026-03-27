from flask import Blueprint, render_template, request, redirect, session, url_for
from models import Helper

view = Blueprint('view', __name__)
auth = Blueprint('auth', __name__)

db = Helper()



@view.route('/')
def home():
    return render_template("login.html")


@auth.route('/login', methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_id = db.auth_user(username, password)

        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("view.home"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@auth.route('/register', methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            error = "Passwords do not match"
            return render_template("login.html", error=error)

        result = db.insert_user(username, email, password)

        if result == 2:
            error = "Username or email already exists"
        elif result == False:
            error = "Registration failed"
        else:
            return redirect(url_for("auth.login"))

    return render_template("login.html", error=error)



@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("view.home"))