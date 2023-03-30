import json
import os
import win32com.client as win32
import pythoncom
import random


def send_email(to, subject, body):
    pythoncom.CoInitialize()
    outlook = win32.Dispatch("outlook.application")
    email = outlook.CreateItem(0)
    email.To = to
    email.Subject = subject
    email.SentOnBehalfOfName = "t.fonseca@ua.pt"  # add this line to set the "From" field
    email.HTMLBody = body
    email.Send()
    pythoncom.CoUninitialize()
    return True

def send_two_factor_code(to, code):
    send_email(to, "Two Factor Authentication Code",
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


def generate_two_factor_code():
    return str(random.randint(100000, 999999))


def read_json():
    directory = os.getcwd()
    if os.path.exists(directory+"/db_handler/users.json") is False:
        write_json("db_handler/users.json", {"users": []})
        data = None
    else:
        with open("db_handler/users.json") as file:
            data = json.load(file)
    return data


def write_json(file, data):
    with open(file, "w") as file:
            json.dump(data, file, indent=4)


def search_user(email):
    data = read_json()
    if data is None:
        return None
    for user in data["users"]:
        if user["email"] == email:
            return user
    return None


def search_user_by_username(username):
    data = read_json()
    if data is None:
        return None
    for user in data["users"]:
        if user["username"] == username:
            return user
    return None


def validate_login(username, password):
    user = search_user_by_username(username)
    if user is None:
        return False
    else:
        if user["password"] == password:
            return True
        else:
            return False


def send_recovery_password(email):
    user = search_user(email)
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
        email.SentOnBehalfOfName = "t.fonseca@ua.pt"  # add this line to set the "From" field
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


def random_id():
    random_id = random.randint(100000, 999999)
    while check_id_exists(random_id):
        random_id = random.randint(100000, 999999)
    return random_id


def check_id_exists(id):
    data = read_json()
    if data is None:
        return False
    for user in data["users"]:
        if user["id"] == id:
            return True
    return False


def get_id(username):
    data = read_json()
    if data is None:
        return None
    for user in data["users"]:
        if user["username"] == username:
            return user["id"]
    return None

def get_json_data(id):
    with open("accounts/"+id+".json") as ficheiro:
        data = json.load(ficheiro)
    return data