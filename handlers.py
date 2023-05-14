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
import pandas as pd
from converter import *
from decimal import Decimal
import matplotlib.pyplot as plt
import base64
import io
import numpy as np


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

def send_two_factor_auth_code(to, code, op):
    if op == "login":
        email = search_user_by_username(to)["email"]
    else:
        email = to["email"]
        to = to["username"]
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
                <p>Hello, {to}</p>
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
    file_dir = file.split("\\")[0]
    if not os.path.exists(directory+file_dir):
        os.makedirs(directory+file_dir)
        print("Created file: ", directory+file_dir)
    with open(directory+file, "w+") as f:
        json.dump(data, f, indent=4)
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
    name = user["username"]
    password = user["password"]
    if user is None:
        return False
    else:
        pythoncom.CoInitialize()
        outlook = win32.Dispatch("outlook.application")
        email = outlook.CreateItem(0)
        email.To = user["email"]
        email.Subject = "Recover your password"
        email.HTMLBody = f"""
                            <html>
                            <head>
                                <style>
                                body {{
                                    font-family: Arial, sans-serif;
                                    font-size: 14px;
                                    color: #333;
                                }}
                                h1 {{
                                    color: #007bff;
                                }}
                                p {{
                                    margin-bottom: 10px;
                                }}
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
    elif operation == "withdrawl":
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
        with open(directory+f"\\accounts\\{id}\\{id}.csv", "w+", newline="", encoding="utf8") as file:
            csv_writer = csv.writer(file, delimiter=";")
            csv_writer.writerow(["Data", "Descrição", "Montante", "Saldo Contabilístico"])
    return True


def register_operation(id, operation, coin, amount):
    accountBalance = get_account_balance(id)
    try:
        if check_statement_existence(id):
            directory = os.getcwd()
            total = float(coin) * float(amount)
            if operation == "deposit":
                accountBalance += total
            elif operation == "withdrawl":
                accountBalance -= total
                total = -total
            else:
                return False
            statement_row = [datetime.now().strftime('%d-%m-%Y'), operation.title(), "{:.2f}".format(total)+" €", "{:.2f}".format(accountBalance)+" €"]
            with open(directory+f"\\accounts\\{id}\\{id}.csv", "r", newline="", encoding="utf8") as file:
                csv_reader = csv.reader(file, delimiter=";")
                existing_rows = [row for row in csv_reader]
            with open(directory+f"\\accounts\\{id}\\{id}.csv", "w", newline="", encoding="utf8") as file:
                csv_writer = csv.writer(file, delimiter=";")
                csv_writer.writerows([existing_rows[0], statement_row] + existing_rows[1:])
            return True
    except:
        return False


def get_statement(id):
    with open(os.getcwd()+f"\\accounts\\{id}\\{id}.csv", "r") as file:
        csv_reader = csv.reader(file, delimiter=";")
        return list(csv_reader)


def get_account_balance(id):
    data = read_json("\\accounts\\"+id+"\\"+id+".json")
    total = 0
    for coin_ in data["coins"]:
        total += float(data["coinAmounts"][coin_["name"]]) * float(coin_["value"])
    return total


def csv_to_pdf(csv_path, id):

    if not check_statement_existence(id):
        return False
    
    # Set up input and output paths
    input_path = csv_path
    output_path = csv_path[:-3] + "pdf"

    # Read the CSV file and convert it to a list of rows
    with open(input_path, "r", encoding="utf8") as f:
        rows = [row.strip().split(";") for row in f]

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
    doc = SimpleDocTemplate(output_path, pagesize=letter, encoding = "utf-8")

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
            print(difference)
            print(difference.total_seconds())
            if difference.total_seconds() > 600: # 10 minutes
                inactivate_user(id)
                return False
            else:
                set_activity_timer(id)
                return True
    return False


def get_image_path(id):
    return f"\\accounts\\{id}\\{id}.png"


def create_user(username, password, email):
    id = str(generate_random_id())
    data_to_add = {"username": username, "password": password, "email": email, "id" : id, "active" : False, "last_activity" : None}
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
    create_user_folder(id)
    write_json("\\accounts\\"+id+"\\"+id+".json", json_coins)
    return


def store_statement(file, filename, ext, id):
    # Salvar arquivo no disco
    file_path = os.path.join(os.getcwd(), "accounts", id, "uploads", filename)
    if not os.path.exists(os.path.join(os.getcwd(), "accounts", id, "uploads")):
        os.makedirs(os.path.join(os.getcwd(), "accounts", id, "uploads"))
    file.save(file_path)
    # Ler arquivo Excel ou CSV
    if ext == ".xlsx" or ext == ".xls":
        convert_excel_to_csv(file_path)
        os.remove(file_path)
        file_path = os.path.splitext(file_path)[0] + ".csv"
    clean_csv_file(file_path)
    # Identificar banco
    bank = get_statement_bank(file_path)
    # Extrair dados
    lst = get_statement_data(file_path)
    if lst != []:
        store_external_statement_data(lst, file_path, bank)


def get_statement_bank(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if "Consultar saldos e movimentos" in row[0]:
                return "CGD"
            elif "Listagem de Movimentos" in row[0]:
                return "Santander"


def get_statement_data(filepath):
    lst = []
    if not os.path.exists(filepath):
        return lst
    with open(filepath, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            lst.append(row)
    return lst


def store_external_statement_data(lst,filepath, bank):
    with open(filepath, 'w+', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        if bank == "CGD":
            writer.writerow(["Data", "Descrição", "Montante", "Saldo Contabilístico"])
            lst = lst[7:-1]
            for element in lst:
                if element[3] != "":
                    element[3] = "-" + element[3]
                else:
                    element[3] = element[4]
                new_lst=[element[1], element[2], element[3], element[6]]
                writer.writerow(new_lst)
        elif bank == "Santander":
            writer.writerow(["Data", "Descrição", "Montante", "Saldo Contabilístico"])
            lst = lst[7:]
            for element in lst:
                element = element[1:]
                writer.writerow(element)


def clean_platform_csv(id):
    if not os.path.exists(os.getcwd()+f"\\accounts\\{id}\\{id}.csv"):
        return []
    with open(os.getcwd()+f"\\accounts\\{id}\\{id}.csv", "r", encoding="utf8") as file:
        reader = csv.reader(file)
        lst = []
        for row in reader:
            lst.append([row[0], row[1], row[-2], row[-1]])
    if lst != []:
        lst.pop(0)
    return lst


def foreign_statement(bank, id):
    with open(os.getcwd()+f"\\accounts\\{id}\\uploads\\{bank}.csv") as file:
        reader = csv.reader(file)
        lst = []
        for row in reader:
            lst.append(row)
    return lst


def calculate_bank_expenses(lst):
    dic = {}
    expenses = 0
    for element in lst:
        if element[2] != "" and float(element[2]) < 0:
            expenses += round(float(element[2]) * -1, 2)
            if element[1] not in dic:
                dic[element[1]] = round(float(element[2]) * -1, 2)
            else:
                dic[element[1]] += round(float(element[2]) * -1, 2)
    return round(expenses, 2), dic


def calculate_bank_profits(lst):
    dic = {}
    profits = Decimal('0')
    for element in lst:
        if element[2] != "" and float(element[2]) > 0:
            profit = Decimal(element[2]).quantize(Decimal('0.01'))
            profits += profit
            if element[1] not in dic:
                dic[element[1]] = profit
            else:
                dic[element[1]] += profit
    return round(profits, 2), dic



def read_csv_statement_file(filepath):
    lst = []
    with open(filepath, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            lst.append(row)
    return lst[1:]

def get_expenses(id):
    if check_bank_statement_exists("CGD", id):
        cgd = read_csv_statement_file(os.getcwd()+f"\\accounts\\{id}\\uploads\\CGD.csv")
    else:
        cgd = []
    if check_bank_statement_exists("Santander", id):
        santander = read_csv_statement_file(os.getcwd()+f"\\accounts\\{id}\\uploads\\Santander.csv")
    else:
        santander = []
    eco_statement = get_statement_data(os.getcwd()+f"\\accounts\\{id}\\{id}.csv")
    for element in eco_statement:
        element[-1] = element[-1].replace("€", "").strip()
        element[-2] = element[-2].replace("€", "").strip()
    eco_expenses, eco_dic_expenses = calculate_bank_expenses(eco_statement[1:])
    expenses_cgd, expenses_dic_cgd = calculate_bank_expenses(cgd)
    expenses_santander, expenses_dic_santander = calculate_bank_expenses(santander)
    expenses = round(expenses_cgd + expenses_santander + eco_expenses, 2)
    expenses_dic = expenses_dic_cgd | expenses_dic_santander | eco_dic_expenses # Merge dictionaries
    expenses_dic = filter_operations(expenses_dic)
    return str(expenses) + " €", expenses_dic


def get_profits(id):
    if check_bank_statement_exists("CGD", id):
        cgd = read_csv_statement_file(os.getcwd()+f"\\accounts\\{id}\\uploads\\CGD.csv")
    else:
        cgd = []
    if check_bank_statement_exists("Santander", id):
        santander = read_csv_statement_file(os.getcwd()+f"\\accounts\\{id}\\uploads\\Santander.csv")
    else:
        santander = []
    eco_statement = get_statement_data(os.getcwd()+f"\\accounts\\{id}\\{id}.csv")
    for element in eco_statement:
        element[-1] = element[-1].replace("€", "").strip()
        element[-2] = element[-2].replace("€", "").strip()
    eco_profits, eco_dic_profits = calculate_bank_profits(eco_statement[1:])
    profits_cgd, profits_dic_cgd = calculate_bank_profits(cgd)
    profits_santander, profits_dic_santander = calculate_bank_profits(santander)
    profits = round(profits_cgd + profits_santander + eco_profits, 2)
    profits_dic = profits_dic_cgd | profits_dic_santander | eco_dic_profits # Merge dictionaries
    profits_dic = filter_operations(profits_dic)
    return str(profits) + " €", profits_dic


def check_bank_statement_exists(bank, id):
    if os.path.exists(os.getcwd()+f"\\accounts\\{id}\\uploads\\{bank}.csv"):
        return True
    else:
        return False


def filter_operations(dic):
    dic_operations = {
        "Compras" : 0,
        "Transferências" : 0,
        "Levantamentos" : 0,
        "Depósitos" : 0,
        "Anulações" : 0,
        "Comissões" : 0,
        "Carregamentos" : 0,
        "Impostos" : 0,
        "Transportes" : 0,
        "Telecomunicações" : 0,
        "Outros" : 0
    }

    dic_options = {
        "Compras" : ["COMPRA", "COMPRAS", "PAGAMENTO"],
        "Transferências" : ["TRANSFERÊNCIA", "TRF"],
        "Levantamentos" : ["LEVANTAMENTO", "WITHDRAWL"],
        "Depósitos" : ["Deposit", "DEPOSITO", "DEPOSIT"],
        "Anulações" : ["Anulação", "ANULAÇÃO"],
        "Comissões" : ["Comissão", "COMISSÃO", "COMISSAO"],
        "Carregamentos" : ["Carregamento", "CARREGAMENTO"],
        "Impostos": ["IMPOSTO", "IMPOSTOS"],
        "Transportes": ["TRANSPORTE", "TRANSPORTES", "UBER", "BOLT", "TAXI", "AVEIROBUS", "TRANSDEV", "CP", "COMBOIOS", "METRO", "METRO DO PORTO", "METRO DO PORTO, S.A."],
        "Telecomunicações": ["VODAFONE", "NOS", "MEO", "NOWO", "NOWO - COMUNICAÇÕES, S.A.", "VODAFONE.PT"],
    }
    new_dic = {}
    for element in dic:
        valor = Decimal(dic[element]).quantize(Decimal('0.01'))
        element = element.split(" ")[0]
        upper_element = element.upper()
        if upper_element in dic_options["Compras"]:
            dic_operations["Compras"] += valor
        elif upper_element in dic_options["Transferências"]:
            dic_operations["Transferências"] += valor
        elif upper_element in dic_options["Levantamentos"]:
            dic_operations["Levantamentos"] += valor
        elif upper_element in dic_options["Depósitos"]:
            dic_operations["Depósitos"] += valor
        elif upper_element in dic_options["Anulações"]:
            dic_operations["Anulações"] += valor
        elif upper_element in dic_options["Comissões"]:
            dic_operations["Comissões"] += valor
        elif upper_element in dic_options["Carregamentos"]:
            dic_operations["Carregamentos"] += valor
        elif upper_element in dic_options["Impostos"]:
            dic_operations["Impostos"] += valor
        elif upper_element in dic_options["Transportes"]:
            dic_operations["Transportes"] += valor
        elif upper_element in dic_options["Telecomunicações"]:
            dic_operations["Telecomunicações"] += valor
        else:
            dic_operations["Outros"] += valor

    for element in dic_operations:
        if dic_operations[element] != 0:
            new_dic[element] = dic_operations[element]
    return new_dic


def get_pizza_info(dic, id, page):
    # Cria listas com as chaves e valores do dicionário
    keys = list(dic.keys())
    values = list(dic.values())
    values = [float(Decimal(str(value))) for value in values]

    # Define o limite mínimo para o tamanho da fatia
    min_size = 1

    # Remove valores menores que o limite mínimo
    values, keys = zip(*filter(lambda x: 100 * x[0] / sum(values) >= min_size, zip(values, keys)))

    # Cria um gráfico de pizza com as informações do dicionário
    fig, ax = plt.subplots()
    wedges, _, autotexts = ax.pie(values, autopct='%1.1f%%', textprops={'color': 'black'})

    # Adiciona texto com os nomes das fatias
    total = sum(values)
    for i, val in enumerate(values):
        angle = 2 * np.pi * (sum(values[:i]) + val / 2) / sum(values)
        x, y = np.cos(angle), np.sin(angle)
        text = '{}'.format(keys[i])
        # Adiciona o nome da fatia com uma linha apontando para ela
        ax.annotate(text, xy=(x, y), xytext=(x*1.34, y*1.34), fontsize=10,
                    ha='center', va='center', arrowprops=dict(arrowstyle='-', color=(77/255, 155/255, 75/255)))
        # Reduz o tamanho da fonte das percentagens da fatia
        autotexts[i].set_fontsize(8)
    
    # Define a cor da linha e do texto
    for w in wedges:
        w.set_edgecolor("none")
    for t in ax.texts:
        if t not in autotexts:
            t.set_color("white")
    
    plt.axis('equal')

    # Cria o diretório se ele não existir
    dir_path = os.path.join(os.getcwd(), f"accounts/{id}/analysis")
    os.makedirs(dir_path, exist_ok=True)

    # Salva a figura no diretório
    filename = f"{page}.png"
    filepath = os.path.join(dir_path, filename)
    plt.savefig(filepath, format='png', transparent=True)
    # Limpa o plot para liberar memória
    plt.clf()
    return filepath
