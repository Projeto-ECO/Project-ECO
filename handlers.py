import json
import os
import win32com.client as win32
import pythoncom
import random
from flask import jsonify
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import shutil
from string import ascii_uppercase
import bleach


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
    elif not os.path.exists(directory+filename) and filename == "\\db_handler\\rooms.json":
        write_json(filename, {"rooms": []})
        data = None
    else:
        with open(directory+filename) as file:
            data = json.load(file)
    return data


def write_json(file, data):
    directory = os.getcwd()
    if not os.path.exists(directory+file[1:file.rfind("\\")]):
        os.makedirs(directory+file[1:file.rfind("\\")])
    with open(directory+file, "w+") as file:
            json.dump(data, file, indent=4)
    return True

def search_user_by_id(id):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return None
    for user in data["users"]:
        if user["id"] == id:
            return user


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

def get_username_by_id(id):
    data = read_json("\\db_handler\\users.json")
    if data is None:
        return None
    for user in data["users"]:
        if user["id"] == id:
            return user["username"]
    return None


def check_if_online(username):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["username"] == username:
            return user["active"]
    return

def check_image_existence(id):
    directory = os.getcwd()
    if not os.path.exists(directory+f"\\accounts\\{id}\\{id}.png"):
        return False
    else:
        return True

def banking_operations(id, operation, coin, amount):
    amount = int(amount)
    coin = "{:.2f}".format(float(coin))
    data = read_json("\\accounts\\"+id+"\\"+id+".json")
    if operation == "deposit":
        for coin_ in data["coins"]:
            if str(coin_["name"]) == str(coin):
                boolean = register_operation(id, operation, coin, amount)
                if boolean:
                    data["coinAmounts"][coin] = data["coinAmounts"][coin] + amount
                    write_json("\\accounts\\"+id+"\\"+id+".json", data)
                    break
                else:
                    return False
    elif operation == "withdraw":
        for coin_ in data["coins"]:
            if str(coin_["name"]) == str(coin) and data["coinAmounts"][coin] >= amount and amount > 0:
                if register_operation(id, operation, coin, amount):
                    data["coinAmounts"][coin] = data["coinAmounts"][coin] - amount
                    write_json("\\accounts\\"+id+"\\"+id+".json", data)
                    break
                else:
                    return False
    return True



def inactivate_user(id):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["active"] = False
            write_json("\\db_handler\\users.json", data)
            print(f"User {id} has been inactivated")
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

def check_statement_existence(id):
    directory = os.getcwd()
    if not os.path.exists(directory+f"\\accounts\\{id}\\{id}.csv"):
        with open(directory+f"\\accounts\\{id}\\{id}.csv", "w+", newline="") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(["Date", "Operation", "Coin", "Amount", "Total", "Account Balance"])
    return True


def register_operation(id, operation, coin, amount):
    accountBalance = get_account_balance(id)
    try:
        if check_statement_existence(id):
            directory = os.getcwd()
            total = float(coin) * float(amount)
            if operation == "deposit":
                accountBalance += total
            elif operation == "withdraw":
                accountBalance -= total
                total = -total
            else:
                return False
            statement_row = [datetime.now().strftime('%d-%m-%Y %H:%M:%S'), operation.title(), coin+" €", amount, "{:.2f}".format(total)+" €", "{:.2f}".format(accountBalance)+" €"]
            with open(directory+f"\\accounts\\{id}\\{id}.csv", "a+", newline="") as file:
                csv_reader = csv.reader(file)
                existing_rows = [row for row in csv_reader]
                if statement_row not in existing_rows:
                    csv_writer = csv.writer(file)
                    csv_writer.writerow(statement_row)
                return True
    except:
        return False


def get_statement(id):
    with open(os.getcwd()+f"\\accounts\\{id}\\{id}.csv", "r") as file:
        csv_reader = csv.reader(file)
        return list(csv_reader)


def get_account_balance(id):
    data = read_json("\\accounts\\"+id+"\\"+id+".json")
    total = 0
    for coin_ in data["coins"]:
        total += float(data["coinAmounts"][coin_["name"]]) * float(coin_["value"])
    with open("cenas.txt", "a+") as file:
        file.write(str(total))
    return total


def csv_to_pdf(csv_path, id):
    
    # Set up input and output paths
    input_path = csv_path
    output_path = csv_path[:-3] + "pdf"

    # Read the CSV file and convert it to a list of rows
    with open(input_path, "r") as f:
        rows = [row.strip().split(",") for row in f]

    # Define the table style
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(77/255, 155/255, 75/255)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.Color(102/255, 102/255, 102/255)),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.whitesmoke),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ])

    # Create the table object
    table = Table(rows)

    # Apply the table style
    table.setStyle(style)

    # Create the PDF document and add the table to it
    doc = SimpleDocTemplate(output_path, pagesize=letter)

    # Create the logo image object
    logo_path = os.getcwd()+f"\\static\\images\\Eco.png"
    logo = Image(logo_path, width=1.5*inch, height=1*inch)

    # Create the username and ID paragraph
    username_style = ParagraphStyle(
        name='UsernameStyle',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.black,
        alignment=TA_CENTER
    )
    username = search_user_by_id(id)["username"]
    username_text = f"Username: {username} ({id})"
    username_para = Paragraph(username_text, username_style)

    # Create the date and time paragraph
    datetime_style = ParagraphStyle(
        name='DateTimeStyle',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.black,
        alignment=TA_CENTER
    )
    now = datetime.now()
    datetime_text = f"Date: {now.strftime('%d-%m-%Y %H:%M:%S')}"
    datetime_para = Paragraph(datetime_text, datetime_style)

    # Add the logo, spacer, and username/ID paragraph to the PDF document
    elements = [logo, Spacer(width=0, height=0.5*inch), username_para, Spacer(width=0, height=0.2*inch),table, Spacer(width=0, height=0.2*inch), datetime_para]

    doc.build(elements)
    return True


def update_username(id, username):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["username"] = username
            write_json("\\db_handler\\users.json", data)
            return True
    return False


def update_email(id, email):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["email"] = email
            write_json("\\db_handler\\users.json", data)
            return True
    return False


def update_password(id, password):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["password"] = password
            write_json("\\db_handler\\users.json", data)
            return True
    return False


def check_username_exists(username):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["username"] == username:
            return True
    return False


def check_email_exists(email):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["email"] == email:
            return True
    return False


def create_user_folder(id):
    directory = os.getcwd()
    os.mkdir(directory+f"\\accounts\\{id}")
    # Set the paths for the source and destination files
    src_path = directory+f"\\static\\images\\default.png"
    dst_path = directory+f"\\accounts\\{id}\\{id}.png"

    # Copy the source file to the destination file
    shutil.copy(src_path, dst_path)


def create_room():
    room_code = generate_unique_code(4)
    data = read_json("\\db_handler\\rooms.json")
    data["rooms"].append({"code": room_code, "members": [], "messages": []})
    write_json("\\db_handler\\rooms.json", data)
    return room_code


def get_rooms():
    data = read_json("\\db_handler\\rooms.json")
    return data


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if check_room_code_exists(code) == False:
            break
    
    return code


def check_room_code_exists(code):
    data = read_json("\\db_handler\\rooms.json")
    if data["rooms"] == []:
        return False
    for room in data["rooms"]:
        if room["code"] == code:
            return True
    return False


def get_room_messages(code):
    data = read_json("\\db_handler\\rooms.json")
    for room in data["rooms"]:
        if room["code"] == code:
            messages = room["messages"]
            # Sanitize each message using bleach and add HTML line breaks
            for message in messages:
                message["name"] = bleach.clean(message["name"], tags=[], attributes={})
                message["message"] = bleach.clean(message["message"], tags=["a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li", "ol", "strong", "ul"], attributes={"a": ["href", "title"]})
                message["message"] = message["message"].replace('\n', '<br>')
            return messages
    return False



def get_room_members(code):
    data = read_json("\\db_handler\\rooms.json")
    for room in data["rooms"]:
        if room["code"] == code:
            return room["members"]
    return False

def add_room_member(code, name, id):
    data = read_json("\\db_handler\\rooms.json")
    members = get_room_members(code)
    for member in members:
        if member["id"] == id or member["name"] == name:
            return False
    for room in data["rooms"]:
        if room["code"] == code:
            room["members"].append({"name": name, "id": id})
            write_json("\\db_handler\\rooms.json", data)
            return True
    return False

def add_room_message(code, message):
    data = read_json("\\db_handler\\rooms.json")
    for room in data["rooms"]:
        if room["code"] == code:
            room["messages"].append(message)
            write_json("\\db_handler\\rooms.json", data)
            return True
    return False

def get_number_of_room_members(code):
    data = read_json("\\db_handler\\rooms.json")
    rooms = data["rooms"]
    number = 0
    for room in rooms:
        if room["code"] == code:
            number = len(room["members"])
    return number

def delete_room(id):
    data = read_json("\\db_handler\\rooms.json")
    rooms = data["rooms"]
    for room in rooms:
        if room["code"] == id:
            rooms.remove(room)
            write_json("\\db_handler\\rooms.json", data)
            return True
    return False

def set_activity_timer(id):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id:
            user["last_activity"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            write_json("\\db_handler\\users.json", data)
            return True
    return False


def last_activity_check(id):
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["id"] == id and user["last_activity"] != None:
            last_activity = datetime.strptime(user["last_activity"], "%d-%m-%Y %H:%M:%S")
            now = datetime.now()
            difference = now - last_activity
            if difference.total_seconds() > 300: # 5 minutes
                inactivate_user(id)
                return False
            else:
                return True
    return False