import json
import os
import win32com.client as win32
import pythoncom
import random
from flask import jsonify


def send_email(to, subject, body):
    pythoncom.CoInitialize()
    outlook = win32.Dispatch("outlook.application")
    email = outlook.CreateItem(0)
    email.To = to
    email.Subject = subject
    email.HTMLBody = body
    email.Send()
    pythoncom.CoUninitialize()
    return True

def send_two_factor_auth_code(to, code):
    email = search_user_by_username(to)["email"]
    send_email(email, "Two Factor Authentication Code",
        """
            <html>
            <head>
                <style>
                body {
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    color: #333;
                }
                h1 {
                    color: #007bff;
                }
                p {
                    margin-bottom: 10px;
                }
                </style>
        """
        +
        f"""
            </head>
            <body>
                <h1>Two Factor Authentication Code</h1>
                <p>Hello, Tiago</p>
                <p>Your login code is: <strong>{code}</strong></p>
            </body>
            </html>
        """
    )


def generate_two_factor_auth_code():
    return str(random.randint(100000, 999999))


def read_json(filename):
    directory = os.getcwd()
    if not os.path.exists(directory+filename) and filename == "\\db_handler\\users.json":
        write_json(filename, {"users": []})
        data = None
    else:
        with open(directory+filename) as file:
            data = json.load(file)
    return data


def write_json(file, data):
    directory = os.getcwd()
    with open(directory+file, "w+") as file:
            json.dump(data, file, indent=4)


def search_user_by_email(email):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return None
    for user in data["users"]:
        if user["email"] == str(email):
            return user


def search_user_by_username(username):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return None
    for user in data.get("users"):
        if user["username"] == username:
            return user
    return None


def validate_login(username, password):
    if ("@" in username):
        user = search_user_by_email(username)
    else:
        user = search_user_by_username(username)

    if user is None:
        return False
    else:
        if user["password"] == password:
            return True
        else:
            return False


def send_recovery_password(email):
    user = search_user_by_email(email)
    password = user["password"]
    name = user["name"]
    if user is None:
        return False
    else:
        pythoncom.CoInitialize()
        outlook = win32.Dispatch("outlook.application")
        email = outlook.CreateItem(0)
        email.To = user["email"]
        email.Subject = "Recover your password"
        email.HTMLBody = """
                            <html>
                            <head>
                                <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    font-size: 14px;
                                    color: #333;
                                }
                                h1 {
                                    color: #007bff;
                                }
                                p {
                                    margin-bottom: 10px;
                                }
                                </style>
                            </head>
                            <body>
                                <h1>Recover Password</h1>
                                <p>Hello, {name}</p>
                                <p>Your password is: <strong>{password}</strong></p>
                            </body>
                            </html>
                        """
        email.Send()
        pythoncom.CoUninitialize()
        return True


def generate_random_id():
    random_id = random.randint(100000, 999999)
    while check_id_existence(random_id):
        random_id = random.randint(100000, 999999)
    return random_id


def check_id_existence(id):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return False
    for user in data["users"]:
        if user["id"] == id:
            return True
    return False


def get_id_by_username(username):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return None
    for user in data["users"]:
        if user["username"] == username:
            return user["id"]
    return None


def check_if_online(username):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["username"] == username:
            return user["active"]

def check_image_existence(id):
    directory = os.getcwd()
    if not os.path.exists(directory+f"\\static\\images\\{id}.png"):
        return False
    else:
        return True

def banking_operations(id, operation,coin, amount):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return None
    amount = int(amount)
    coin = "{:.2f}".format(float(coin))
    data = read_json("\\accounts\\"+id+".json")
    if operation == "deposit":
        for coin_ in data["coins"]:
            if str(coin_["name"]) == str(coin) and data["coinAmounts"][coin] >= amount and amount > 0:
                data["coinAmounts"][coin] = data["coinAmounts"][coin] - amount
                write_json("\\accounts\\"+id+".json", data)
                return True
    elif operation == "withdraw":
        for coin_ in data["coins"]:
            if str(coin_["name"]) == str(coin) and data["coinAmounts"][coin] >= amount and amount > 0:
                data["coinAmounts"][coin] = data["coinAmounts"][coin] + amount
                write_json("\\accounts\\"+id+".json", data)
                return True
    return False


def inactivate_user(id):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["active"] = False
            write_json("\\db_handler\\users.json", data)
            return True
    return False


def activate_user(id):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["active"] = True
            write_json("\\db_handler\\users.json", data)
            return True
    return False