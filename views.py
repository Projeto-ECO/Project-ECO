from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from handlers import *


views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/profile/<username>")
def profile(username):
    id = get_id(username)
    return render_template("profile.html", name=username, id=id)


@views.route("/json")
def get_json():
    coins = [
        {"name": "Bitcoin", "value": 60000},
        {"name": "Ethereum", "value": 2000},
        {"name": "Litecoin", "value": 250},
    ]
    return jsonify(coins)


@views.route("/data/<id>")
def get_data(id):
    data = get_json_data(id)
    return jsonify(data)


@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.home"))


@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        if validate_login(username, password) is False:
            return render_template("login.html", message="User or password are incorrect.")
        else:
            return redirect(url_for("views.profile", username=username))
    else:
        return render_template("login.html")
    

@views.route("/recover-password", methods=["GET", "POST"])
def recover_password():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        user = search_user(email)
        if user is None:
            return redirect(url_for("views.signup"))
        else:
            if user["email"] == email:
                send_recovery_password(email)
            return redirect(url_for("views.login"))
    else:
        return render_template("recover-password.html")


@views.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        if search_user(email) != None or search_user_by_username(username) != None:
            return render_template("signup.html", message="User already exists.")
        else:
            id = str(random_id())
            data = {"username": username, "password": password, "email": email, "id" : id}
            dados = read_json()
            dados["users"].append(data)
            write_json("db_handler/users.json", dados)
            json_coins = {
                            "coins": [
                                {
                                    "name": "0.01",
                                    "value": 0.01
                                },
                                {
                                    "name": "0.02",
                                    "value": 0.02
                                },
                                {
                                    "name": "0.05",
                                    "value": 0.05
                                },
                                {
                                    "name": "0.10",
                                    "value": 0.10
                                },
                                {
                                    "name": "0.20",
                                    "value": 0.20
                                },
                                {
                                    "name": "0.50",
                                    "value": 0.00
                                },
                                {
                                    "name": "1.00",
                                    "value": 1.00
                                },
                                {
                                    "name": "2.00",
                                    "value": 2.00
                                },
                                {
                                    "name": "5.00",
                                    "value": 0.00
                                },
                                {
                                    "name": "10.00",
                                    "value": 10.00
                                },
                                {
                                    "name": "20.00",
                                    "value": 20.00
                                },
                                {
                                    "name": "50.00",
                                    "value": 50.00
                                },
                                {
                                    "name": "100.00",
                                    "value": 100.00
                                },
                                {
                                    "name": "200",
                                    "value": 200.00
                                }
                            ],
                            "coinAmounts": {
                                "0.01": 0,
                                "0.02": 0,
                                "0.05": 0,
                                "0.10": 0,
                                "0.20": 0,
                                "0.50": 0,
                                "1.00": 0,
                                "2.00": 0,
                                "5.00": 0,
                                "10.00": 0,
                                "20.00": 0,
                                "50.00": 0,
                                "100.00": 0,
                                "200.00": 0 
                            }
                        }
            write_json("accounts/"+id+".json", json_coins)
            return redirect(url_for("views.login", username=username))
    else:
        return render_template("signup.html")