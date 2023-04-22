from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from handlers import *


views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/profile/<username>")
def profile(username):
    activity_status = check_if_online(username)
    if activity_status == True:
        id=get_id_by_username(username)
        if id is None:
            return redirect(url_for("views.home"))
        else:
            if check_image_existence(id):
                return render_template("profile.html", name=username, id=id, activity_status=activity_status, image_number = id)
            else:
                return render_template("profile.html", name=username, id=id, activity_status=activity_status, image_number = "default")
    else:
        return redirect(url_for("views.home"))


@views.route("/data/<id>")
def get_data(id):
    return jsonify(read_json("/accounts/"+id+".json"))


@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.home"))


@views.route("/two-factor-auth-login/<username>", methods=["GET", "POST"])
def two_factor_auth_login(username):
    code = session.get("code")
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["username"] == username:
            if user["active"] == True: # check if user is already authenticated
                return redirect(url_for("views.profile", username=username))
            else:
                if request.method == "POST":
                    entered_code = request.form.get("code")
                    if entered_code == code:
                        user["active"] = True
                        write_json("\\db_handler\\users.json", data)
                        session["username"] = username
                        return redirect(url_for("views.profile", username=username))
                return render_template("two-factor-auth-login.html", username=username)
    return redirect(url_for("views.login"))



@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if validate_login(username, password) is False:
            return render_template("login.html", message="User or password are incorrect.")
        else:
            if "@" in username:
                username = search_user_by_email(username)["username"]
            code = generate_two_factor_auth_code()
            session["code"] = code
            session["username"] = username
            session["id"] = get_id_by_username(username)
            send_two_factor_auth_code(username, code)
            return redirect(url_for("views.two_factor_auth_login", username = username))
    else:
        return render_template("login.html")

@views.route("/logout", methods=["POST"])
def logout():
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["username"] == session.get("username"):
            user["active"] = False
            write_json("\\db_handler\\users.json", data)
    session.clear()
    return redirect(url_for("views.home"))


@views.route("/recover-password", methods=["GET", "POST"])
def recover_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = search_user_by_email(email)
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
        if search_user_by_email(email) != None or search_user_by_username(username) != None:
            return render_template("signup.html", message="User already exists.")
        else:
            id = str(generate_random_id())
            data_to_add = {"username": username, "password": password, "email": email, "id" : id, "active" : False}
            data = read_json("\\db_handler\\users.json")
            data["users"].append(data_to_add)
            write_json("\\db_handler\\users.json", data)
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
                                    "name": "200.00",
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
            write_json("\\accounts\\"+id+".json", json_coins)
            return redirect(url_for("views.login", username=username))
    else:
        return render_template("signup.html")


@views.route("/deposit", methods=["POST", "GET"])
def deposit():
    coin = request.form.get("coin-deposit")
    amount = request.form.get("amount-deposit")
    amount = int(amount)
    coin = "{:.2f}".format(float(coin))
    data = read_json("\\accounts\\"+session.get("id")+".json")
    for coin_ in data["coins"]:
        if str(coin_["name"]) == str(coin):
            data["coinAmounts"][coin] = data["coinAmounts"][coin] + amount
            write_json("\\accounts\\"+session.get("id")+".json", data)
            return redirect(url_for("views.profile", username=session.get("username")))
    return redirect(url_for("views.profile", username=session.get("username")))


@views.route("/withdrawl", methods=["POST", "GET"])
def withdrawl():
    coin = request.form.get("coin-withdrawl")
    amount = request.form.get("amount-withdrawl")
    amount = int(amount)
    coin = "{:.2f}".format(float(coin))
    data = read_json("\\accounts\\"+session.get("id")+".json")
    for coin_ in data["coins"]:
        if str(coin_["name"]) == str(coin) and data["coinAmounts"][coin] >= amount and amount > 0:
            data["coinAmounts"][coin] = data["coinAmounts"][coin] - amount
            write_json("\\accounts\\"+session.get("id")+".json", data)
            return redirect(url_for("views.profile", username=session.get("username")))
    return redirect(url_for("views.profile", username=session.get("username")))