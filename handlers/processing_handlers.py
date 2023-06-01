import json
import os
import win32com.client as win32
import pythoncom
import random
import csv
import shutil
import bleach
import matplotlib.pyplot as plt
import numpy as np
from handlers.converter import *
from handlers.db_coordinator import *
from decimal import Decimal
from datetime import datetime
from string import ascii_uppercase
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Image, Paragraph, Spacer, PageBreak


def send_email(to, subject, body):
    # Initialize the COM library
    pythoncom.CoInitialize()

    # Create an instance of the Outlook application
    outlook = win32.Dispatch("outlook.application")

    # Create a new email item
    email = outlook.CreateItem(0)

    # Set the recipient, subject, and body of the email
    email.To = to
    email.Subject = subject
    email.HTMLBody = body

    # Send the email
    email.Send()

    # Uninitialize the COM library
    pythoncom.CoUninitialize()

    # Return True to indicate the email was sent successfully
    return True


def send_two_factor_auth_code(to, code, op):

    # Determine the email address based on the operation type
    if op == "login":
        email = search_user_by_username(to)["email"]
    else:
        email = to["email"]
        to = to["username"]

    # Compose the email body with HTML formatting
    email_body = """
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
    email_body += f"""
        </head>
        <body>
            <h1>Two Factor Authentication Code</h1>
            <p>Hello, {to}</p>
            <p>Your login code is: <strong>{code}</strong></p>
        </body>
        </html>
    """

    # Send the email with the composed body
    send_email(email, "Two Factor Authentication Code", email_body)


def generate_two_factor_auth_code():
    # Generate a random 6-digit code
    return str(random.randint(100000, 999999))


def search_user_by_id(id):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # If data is None, return None
    if data is None:
        return None

    # Search for the user with the given ID
    for user in data["users"]:
        if user["id"] == id:
            return user


def search_user_by_email(email):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # If data is None, return None
    if data is None:
        return None

    # Search for the user with the given email
    for user in data["users"]:
        if user["email"] == str(email):
            return user


def search_user_by_username(username):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # If data is None, return None
    if data is None:
        return None

    # Search for the user with the given username
    for user in data.get("users"):
        if user["username"] == username:
            return user

    # If no user is found, return None
    return None


def validate_login(username, password):
    # Check if the username contains "@", indicating an email login
    if "@" in username:
        user = search_user_by_email(username)
    else:
        user = search_user_by_username(username)

    # If user is None, return False (user not found)
    if user is None:
        return False
    else:
        # Check if the provided password matches the user's password
        if user["password"] == password:
            return True
        else:
            return False


def send_recovery_password(email):
    # Search for the user with the given email
    user = search_user_by_email(email)

    # If user is None, return False (user not found)
    if user is None:
        return False
    else:
        # Extract the username and password from the user
        name = user["username"]
        password = user["password"]

        # Initialize the COM library
        pythoncom.CoInitialize()

        # Create an instance of the Outlook application
        outlook = win32.Dispatch("outlook.application")

        # Create a new email item
        email = outlook.CreateItem(0)

        # Set the recipient, subject, and body of the email
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

        # Send the email
        email.Send()

        # Uninitialize the COM library
        pythoncom.CoUninitialize()

        # Return True to indicate the email was sent successfully
        return True


def generate_random_id():
    # Generate a random ID
    random_id = random.randint(100000, 999999)

    # Check if the generated ID already exists, regenerate if necessary
    while check_id_existence(random_id):
        random_id = random.randint(100000, 999999)

    return random_id


def check_id_existence(id):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # If data is None, return False
    if data is None:
        return False

    # Check if the given ID exists in the user data
    for user in data["users"]:
        if user["id"] == id:
            return True

    # If the ID is not found, return False
    return False


def get_id_by_username(username):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # If data is None, return None
    if data is None:
        return None

    # Search for the user with the given username
    for user in data["users"]:
        if user["username"] == username:
            return user["id"]

    # If no user is found, return None
    return None



def get_username_by_id(id):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # If data is None, return None
    if data is None:
        return None

    # Search for the user with the given ID
    for user in data["users"]:
        if user["id"] == id:
            return user["username"]

    # If no user is found, return None
    return None


def check_image_existence(id):
    directory = os.getcwd()

    # Check if the image file exists
    if not os.path.exists(directory + f"\\database\\accounts\\{id}\\{id}.png"):
        return False
    else:
        return True


def check_statement_existence(id):
    directory = os.getcwd()

    # Check if the statement file exists
    if not os.path.exists(directory + f"\\database\\accounts\\{id}\\{id}.csv"):
        # Create a new statement file and write the header row
        with open(directory + f"\\database\\accounts\\{id}\\{id}.csv", "w+", newline="", encoding="utf8") as file:
            csv_writer = csv.writer(file, delimiter=";")
            csv_writer.writerow(["Data", "Descrição", "Montante", "Saldo Contabilístico"])

    # Return True to indicate the existence of the statement file
    return True


def csv_to_pdf(csv_path, id):
    # Check if the statement exists, if not, return False
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
        # Header row style
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(77/255, 155/255, 75/255)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        # Data rows style
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
    doc = SimpleDocTemplate(output_path, pagesize=letter, encoding="utf-8")

    # Create the logo image object
    logo_path = os.getcwd() + f"\\static\\images\\Eco.png"
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
    username_text = f"{username} ({id})"
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

    # Add the logo, spacer, username/ID paragraph, table, and datetime paragraph to the PDF document
    elements = [
        logo,
        Spacer(width=0, height=0.5*inch),
        username_para,
        Spacer(width=0, height=0.2*inch),
        table,
        Spacer(width=0, height=0.2*inch),
        datetime_para
    ]

    doc.build(elements)
    return True


def update_username(id, username):
    # Read user data from the JSON file
    data = read_json("\\database\\users.json")
    
    # Iterate over each user in the data
    for user in data["users"]:
        # Check if the user ID matches the given ID
        if user["id"] == id:
            # Update the username for the matching user
            user["username"] = username
            # Write the modified data back to the JSON file
            write_json("\\database\\users.json", data)
            # Return True to indicate successful username update
            return True
    
    # If no user with the given ID is found, return False
    return False


def update_email(id, email):
    # Read user data from the JSON file
    data = read_json("\\database\\users.json")
    
    # Iterate over each user in the data
    for user in data["users"]:
        # Check if the user ID matches the given ID
        if user["id"] == id:
            # Update the email for the matching user
            user["email"] = email
            # Write the modified data back to the JSON file
            write_json("\\database\\users.json", data)
            # Return True to indicate successful email update
            return True
    
    # If no user with the given ID is found, return False
    return False


def update_password(id, password):
    # Read user data from the JSON file
    data = read_json("\\database\\users.json")
    
    # Iterate over each user in the data
    for user in data["users"]:
        # Check if the user ID matches the given ID
        if user["id"] == id:
            # Update the password for the matching user
            user["password"] = password
            # Write the modified data back to the JSON file
            write_json("\\database\\users.json", data)
            # Return True to indicate successful password update
            return True
    
    # If no user with the given ID is found, return False
    return False


def check_username_exists(username):
    # Read user data from the JSON file
    data = read_json("\\database\\users.json")
    
    # Iterate over each user in the data
    for user in data["users"]:
        # Check if the username matches the given username
        if user["username"] == username:
            # Return True to indicate that the username exists
            return True
    
    # If no matching username is found, return False
    return False


def check_email_exists(email):
    # Read user data from the JSON file
    data = read_json("\\database\\users.json")
    
    # Iterate over each user in the data
    for user in data["users"]:
        # Check if the email matches the given email
        if user["email"] == email:
            # Return True to indicate that the email exists
            return True
    
    # If no matching email is found, return False
    return False


def create_user_folder(id):
    # Get the current working directory
    directory = os.getcwd()

    # Create a directory for the user using their ID
    os.mkdir(directory+f"\\database\\accounts\\{id}")

    # Set the paths for the source and destination files
    src_path = directory+f"\\static\\images\\default.png"
    dst_path = directory+f"\\database\\accounts\\{id}\\{id}.png"

    # Copy the source file to the destination file
    shutil.copy(src_path, dst_path)


def create_room():
    # Generate a unique room code
    room_code = generate_unique_code(4)
    
    # Read the rooms data from JSON file
    data = read_json("\\database\\rooms.json")
    
    # Add the new room to the data
    data["rooms"].append({"code": room_code, "members": [], "messages": []})
    
    # Write the updated data back to the JSON file
    write_json("\\database\\rooms.json", data)
    
    # Return the generated room code
    return room_code


def get_rooms():
    # Read the rooms data from JSON file
    data = read_json("\\database\\rooms.json")
    
    # Return the data containing all the rooms
    return data


def generate_unique_code(length):
    while True:
        code = ""
        # Generate a code with the specified length
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        # Check if the generated code already exists
        if not check_room_code_exists(code):
            # If the code does not exist, break out of the loop
            break
    
    # Return the unique code
    return code


def check_room_code_exists(code):
    data = read_json("\\database\\rooms.json")
    
    # Check if the rooms list is empty
    if data["rooms"] == []:
        return False
    
    # Iterate over each room in the data
    for room in data["rooms"]:
        # Check if the room code matches the provided code
        if room["code"] == code:
            return True
    
    # If no matching room code is found, return False
    return False


def get_room_messages(code):
    data = read_json("\\database\\rooms.json")
    
    # Iterate over each room in the data
    for room in data["rooms"]:
        # Check if the room code matches the provided code
        if room["code"] == code:
            messages = room["messages"]
            
            # Sanitize each message using bleach and add HTML line breaks
            for message in messages:
                message["name"] = bleach.clean(message["name"], tags=[], attributes={})
                message["message"] = bleach.clean(message["message"], tags=["a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li", "ol", "strong", "ul"], attributes={"a": ["href", "title"]})
                message["message"] = message["message"].replace('\n', '<br>')
            
            return messages
    
    # If no matching room is found, return False
    return False


def get_room_members(code):
    data = read_json("\\database\\rooms.json")
    
    # Iterate over each room in the data
    for room in data["rooms"]:
        # Check if the room code matches the provided code
        if room["code"] == code:
            # Return the members of the matched room
            return room["members"]
    
    # If no matching room is found, return False
    return False


def add_room_member(code, name, id):
    data = read_json("\\database\\rooms.json")
    
    # Get the current members of the room
    members = get_room_members(code)
    
    # Check if the member with the same ID or name already exists
    for member in members:
        if member["id"] == id or member["name"] == name:
            return False
    
    # Iterate over each room in the data
    for room in data["rooms"]:
        # Check if the room code matches the provided code
        if room["code"] == code:
            # Add the new member to the room
            room["members"].append({"name": name, "id": id})
            write_json("\\database\\rooms.json", data)
            return True
    
    # If no matching room is found, return False
    return False


def add_room_message(code, message):
    data = read_json("\\database\\rooms.json")
    
    # Iterate over each room in the data
    for room in data["rooms"]:
        # Check if the room code matches the provided code
        if room["code"] == code:
            # Add the message to the room's messages
            room["messages"].append(message)
            write_json("\\database\\rooms.json", data)
            return True
    
    # If no matching room is found, return False
    return False


def get_number_of_room_members(code):
    data = read_json("\\database\\rooms.json")
    rooms = data["rooms"]
    number = 0
    
    # Iterate over each room in the data
    for room in rooms:
        # Check if the room code matches the provided code
        if room["code"] == code:
            # Get the number of members in the room
            number = len(room["members"])
    
    return number


def delete_room(id):
    data = read_json("\\database\\rooms.json")
    rooms = data["rooms"]
    
    # Iterate over each room in the data
    for room in rooms:
        # Check if the room code matches the provided id
        if room["code"] == id:
            # Remove the room from the list
            rooms.remove(room)
            write_json("\\database\\rooms.json", data)
            return True
    
    return False


def get_image_path(id):
    # Construct the image path based on the provided user id
    return f"\\database\\accounts\\{id}\\{id}.png"


def create_user(username, password, email):
    # Generate a unique user id
    id = str(generate_random_id())

    # Prepare the data to add to the users.json file
    data_to_add = {
        "username": username,
        "password": password,
        "email": email,
        "id": id,
        "active": False,
        "last_activity": None
    }

    # Read the existing users data
    data = read_json("\\database\\users.json")

    # Append the new user data to the existing users list
    data["users"].append(data_to_add)

    # Write the updated users data back to the users.json file
    write_json("\\database\\users.json", data)

    # Define the initial coin data for the user
    json_coins = {
        "coins": [
            {"name": "0.01", "value": 0.01},
            {"name": "0.02", "value": 0.02},
            {"name": "0.05", "value": 0.05},
            {"name": "0.10", "value": 0.10},
            {"name": "0.20", "value": 0.20},
            {"name": "0.50", "value": 0.00},
            {"name": "1.00", "value": 1.00},
            {"name": "2.00", "value": 2.00},
            {"name": "5.00", "value": 0.00},
            {"name": "10.00", "value": 10.00},
            {"name": "20.00", "value": 20.00},
            {"name": "50.00", "value": 50.00},
            {"name": "100.00", "value": 100.00},
            {"name": "200.00", "value": 200.00}
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

    # Create a folder for the user
    create_user_folder(id)

    # Write the initial coin data to the user's JSON file
    write_json("\\database\\accounts\\" + id + "\\" + id + ".json", json_coins)
    # Write the initial bank loan data to the user's JSON file
    write_json("\\database\\accounts\\" + id + "\\" + "loans.json", {})

    # Return the created user
    return id


def store_statement(file, filename, ext, id):
    # Save the file to disk
    file_path = os.path.join(os.getcwd(), "database\\accounts", id, "uploads", filename)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(os.path.join(os.getcwd(), "database\\accounts", id, "uploads")):
        os.makedirs(os.path.join(os.getcwd(), "database\\accounts", id, "uploads"))
    
    # Save the file
    file.save(file_path)
    
    # Read the file as Excel or CSV
    if ext == ".xlsx" or ext == ".xls":
        # Convert Excel to CSV
        convert_status = convert_excel_to_csv(file_path)
        os.remove(file_path)
        if convert_status == None:
            return False
        file_path = os.path.splitext(file_path)[0] + ".csv"
    
    # Clean the CSV file
    clean_csv_file(file_path)
    
    # Identify the bank from the statement
    bank = get_statement_bank(file_path)
    if bank != "Santander" and bank != "CGD":
        # Remove the file
        os.remove(file_path)
        return False
    
    # Extract statement data
    lst = get_statement_data(file_path)
    
    # Define the path for storing bank-specific statement data
    file_path_bank = os.path.join(os.getcwd(), "database\\accounts", id, "uploads", bank + ".csv")
    
    if lst != []:
        # Store the statement data in a bank-specific file
        store_external_statement_data(lst, file_path_bank, bank)
    
    if os.path.splitext(file_path)[0] != os.path.splitext(file_path_bank)[0]:
        # Remove the original file
        os.remove(file_path)
    
    # Return statement processing result
    return True


def get_statement_bank(filepath):
    # Open the file as CSV
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        
        # Iterate over each row in the CSV
        for row in reader:
            # Check for specific keywords to identify the bank
            if "Consultar saldos e movimentos" in row[0]:
                return "CGD"  # If the keyword is found, the bank is CGD
            elif "Listagem de Movimentos" in row[0]:
                return "Santander"  # If the keyword is found, the bank is Santander
    
    # If no bank is identified, return None
    return None


def get_statement_data(filepath):
    lst = []
    
    # Check if the file exists
    if not os.path.exists(filepath):
        return lst
    
    # Open the file as CSV
    with open(filepath, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        
        # Iterate over each row in the CSV and append it to the list
        for row in reader:
            lst.append(row)
    
    return lst


def store_external_statement_data(lst, filepath, bank):
    # Check if the file exists and remove it if it does
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Open the file in write mode and create a CSV writer
    with open(filepath, 'w+', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        
        # Write the header row based on the bank
        if bank == "CGD":
            writer.writerow(["Data", "Descrição", "Montante", "Saldo Contabilístico"])
            lst = lst[7:-1]  # Skip the first 7 rows and the last row
            for element in lst:
                if element[3] != "":
                    element[3] = "-" + element[3]
                else:
                    element[3] = element[4]
                new_lst = [element[1], element[2], element[3], element[6]]
                writer.writerow(new_lst)
        elif bank == "Santander":
            writer.writerow(["Data", "Descrição", "Montante", "Saldo Contabilístico"])
            lst = lst[7:]  # Skip the first 7 rows
            for element in lst:
                element = element[1:]  # Skip the first column
                writer.writerow(element)


def clean_platform_csv(id):
    csv_file_path = os.path.join(os.getcwd(), "database\\accounts", id, f"{id}.csv")
    
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        return []
    
    with open(csv_file_path, "r", encoding="utf8") as file:
        reader = csv.reader(file)
        lst = []
        
        # Iterate through each row in the CSV file
        for row in reader:
            # Append only the necessary columns to the list
            lst.append([row[0], row[1], row[-2], row[-1]])
    
    if lst != []:
        lst.pop(0)  # Remove the header row
    
    return lst


def foreign_statement(bank, id):
    csv_file_path = os.path.join(os.getcwd(), "database\\accounts", id, "uploads", f"{bank}.csv")
    
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        return []
    
    with open(csv_file_path, "r") as file:
        reader = csv.reader(file)
        lst = []
        
        # Iterate through each row in the CSV file
        for row in reader:
            lst.append(row)
    
    return lst

def insert_char(string, char, index):
    return string[:index] + char + string[index:]

def calculate_bank_expenses(lst):
    dic = {}  # Dictionary to store expense totals for each description
    expenses = 0  # Total expenses

    for element in lst:
        if "." in element[2] and len(element[2]) > 6:
            element[2] = element[2].replace(".", "")
            element[2] = insert_char(element[2], ".", -2)
        if element[2] != "" and float(element[2]) < 0:
            expense = round(float(element[2]) * -1, 2)  # Convert the expense amount to positive value
            expenses += expense  # Add the expense to the total expenses

            # Update the dictionary with the expense amount for the description
            if element[1] not in dic:
                dic[element[1]] = expense
            else:
                dic[element[1]] += expense

    return round(expenses, 2), dic


def calculate_bank_profits(lst):
    dic = {}  # Dictionary to store profit totals for each description
    profits = Decimal('0')  # Total profits

    for element in lst:
        if "." in element[2] and len(element[2]) > 6:
            element[2] = element[2].replace(".", "")
            element[2] = insert_char(element[2], ".", -2)
        if element[2] != "" and float(element[2]) > 0:
            profit = Decimal(element[2]).quantize(Decimal('0.01'))  # Convert the profit amount to decimal with two decimal places
            profits += profit  # Add the profit to the total profits

            # Update the dictionary with the profit amount for the description
            if element[1] not in dic:
                dic[element[1]] = profit
            else:
                dic[element[1]] += profit

    return round(profits, 2), dic


def read_csv_statement_file(filepath):
    lst = []  # List to store the statement rows

    with open(filepath, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            lst.append(row)

    return lst[1:]  # Return all rows except the header (skipping the first row)


def get_expenses(id):
    # Check if CGD bank statement exists for the given ID
    if check_bank_statement_exists("CGD", id):
        cgd = read_csv_statement_file(os.getcwd()+f"\\database\\accounts\\{id}\\uploads\\CGD.csv")
    else:
        cgd = []

    # Check if Santander bank statement exists for the given ID
    if check_bank_statement_exists("Santander", id):
        santander = read_csv_statement_file(os.getcwd()+f"\\database\\accounts\\{id}\\uploads\\Santander.csv")
    else:
        santander = []

    # Get statement data from the eco statement file
    eco_statement = get_statement_data(os.getcwd()+f"\\database\\accounts\\{id}\\{id}.csv")

    # Remove currency symbols and spaces from the statement data
    for element in eco_statement:
        element[-1] = element[-1].replace("€", "").strip()
        element[-2] = element[-2].replace("€", "").strip()

    # Calculate expenses for each bank and the eco statement
    eco_expenses, eco_dic_expenses = calculate_bank_expenses(eco_statement[1:])
    expenses_cgd, expenses_dic_cgd = calculate_bank_expenses(cgd)
    expenses_santander, expenses_dic_santander = calculate_bank_expenses(santander)

    # Calculate the total expenses
    expenses = round(expenses_cgd + expenses_santander + eco_expenses, 2)

    # Merge dictionaries of expenses
    expenses_dic = expenses_dic_cgd | expenses_dic_santander | eco_dic_expenses

    # Filter and sort the dictionary of expenses
    expenses_dic = filter_operations(expenses_dic)
    expenses_dic = dict(sorted(expenses_dic.items(), key=lambda x: x[1], reverse=True))

    return str(expenses) + " €", expenses_dic


def get_profits(id):
    # Check if CGD bank statement exists for the given ID
    if check_bank_statement_exists("CGD", id):
        cgd = read_csv_statement_file(os.getcwd()+f"\\database\\accounts\\{id}\\uploads\\CGD.csv")
    else:
        cgd = []

    # Check if Santander bank statement exists for the given ID
    if check_bank_statement_exists("Santander", id):
        santander = read_csv_statement_file(os.getcwd()+f"\\database\\accounts\\{id}\\uploads\\Santander.csv")
    else:
        santander = []

    # Get statement data from the eco statement file
    eco_statement = get_statement_data(os.getcwd()+f"\\database\\accounts\\{id}\\{id}.csv")

    # Remove currency symbols and spaces from the statement data
    for element in eco_statement:
        element[-1] = element[-1].replace("€", "").strip()
        element[-2] = element[-2].replace("€", "").strip()

    # Calculate profits for each bank and the eco statement
    eco_profits, eco_dic_profits = calculate_bank_profits(eco_statement[1:])
    profits_cgd, profits_dic_cgd = calculate_bank_profits(cgd)
    profits_santander, profits_dic_santander = calculate_bank_profits(santander)

    # Calculate the total profits
    profits = round(profits_cgd + profits_santander + eco_profits, 2)

    # Merge dictionaries of profits
    profits_dic = profits_dic_cgd | profits_dic_santander | eco_dic_profits

    # Filter and sort the dictionary of profits
    profits_dic = filter_operations(profits_dic)
    profits_dic = dict(sorted(profits_dic.items(), key=lambda x: x[1], reverse=True))

    return str(profits) + " €", profits_dic


def check_bank_statement_exists(bank, id):
    filepath = os.getcwd() + f"\\database\\accounts\\{id}\\uploads\\{bank}.csv"
    return os.path.exists(filepath)


def filter_operations(dic):
    # Read the JSON file
    with open(os.getcwd()+"\\database\\categories.json", "r", encoding="utf8") as f:
        data = json.load(f)

    # Get the dictionaries from the JSON data
    dic_operations = data['dic_operations']
    dic_options = data['dic_options']

    # Initialize a new dictionary to store the categorized operation values
    new_dic = {}

    # Iterate over each element in the input dictionary
    for element in dic:
        # Convert the value to decimal with two decimal places
        valor = Decimal(dic[element]).quantize(Decimal('0.01'))

        # Extract the first two words from the element
        element = element.split(" ")[:2]

        # Convert the first word to uppercase
        upper_element_1 = element[0].upper()

        # Join the words back into a string
        element = " ".join(element)

        # Convert the joined element to uppercase
        upper_element_join = element.upper()

        # Check if the element matches any of the keywords for each category
        for category in dic_options:
            if upper_element_1 in dic_options[category] or upper_element_join in dic_options[category]:
                # If a match is found, add the value to the corresponding category
                dic_operations[category] += valor
                break
        else:
            # If no match is found, add the value to the "Outros" category
            dic_operations["Outros"] += valor

    # Iterate over each element in the categorized operation dictionary
    for element in dic_operations:
        if dic_operations[element] != 0:
            # If the value is not zero, add it to the new dictionary
            new_dic[element] = dic_operations[element]

    # Return the new dictionary with categorized operation values
    return new_dic


def get_pizza_info(dic, id, page):
    # Extract keys and values from the dictionary
    keys = list(dic.keys())
    values = list(dic.values())
    
    # Convert values to floats using Decimal
    values = [float(Decimal(str(value))) for value in values]

    # Define the minimum size for a slice
    min_size = 1

    # Filter out values below the minimum size
    total_sum = sum(values)
    if total_sum != 0:
        filtered_values, filtered_keys = zip(*filter(lambda x: 100 * x[0] / total_sum >= min_size, zip(values, keys)))
    else:
        # If all values are zero, create a slice with default values
        filtered_values = [1]
        filtered_keys = ["Sem dados"]

    # Create a pie chart with the dictionary information
    fig, ax = plt.subplots()
    wedges, _, autotexts = ax.pie(filtered_values, autopct='%1.1f%%', textprops={'color': 'black'})

    # Add labels for each slice
    for i, val in enumerate(filtered_values):
        angle = 2 * np.pi * (sum(filtered_values[:i]) + val / 2) / sum(filtered_values)
        x, y = np.cos(angle), np.sin(angle)
        text = '{}'.format(filtered_keys[i])
        # Add the label with a line pointing to the slice
        ax.annotate(text, xy=(x, y), xytext=(x*1.34, y*1.34), fontsize=10,
                    ha='center', va='center', arrowprops=dict(arrowstyle='-', color=(77/255, 155/255, 75/255)))
        # Reduce the font size of the slice percentages
        autotexts[i].set_fontsize(8)

    # Set the color of the lines and text
    for w in wedges:
        w.set_edgecolor("none")
    for t in ax.texts:
        if t not in autotexts:
            t.set_color("white")

    plt.axis('equal')

    # Create the directory if it doesn't exist
    dir_path = os.path.join(os.getcwd(), f"database\\accounts/{id}/analysis")
    os.makedirs(dir_path, exist_ok=True)

    # Save the figure in the directory
    filename = f"{page}.png"
    filepath = os.path.join(dir_path, filename)
    plt.savefig(filepath, format='png', transparent=True)
    # Clear the plot to free up memory
    plt.clf()
    return filepath


def generate_economic_report(output_path, image_paths, id, dic_profits_expenses, expenses_dic, profits_dic):

    image_paths = image_paths[::-1]

    for element in dic_profits_expenses:
        dic_profits_expenses[element] = str(dic_profits_expenses[element]) + " €"
    
    for element in expenses_dic:
        expenses_dic[element] = str(expenses_dic[element]) + " €"
    
    for element in profits_dic:
        profits_dic[element] = str(profits_dic[element]) + " €"

    # Create the PDF document and add the table to it

    # Definir as margens da página
    left_margin = 0.2 * inch  # Margem esquerda em polegadas
    right_margin = 0.2 * inch  # Margem direita em polegadas
    top_margin = 0.2 * inch  # Margem superior em polegadas
    bottom_margin = 0.2 * inch  # Margem inferior em polegadas

    # Criar o objeto SimpleDocTemplate com as margens personalizadas
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
        encoding="utf-8"
    )


    # Create the username and ID paragraph
    username_style = ParagraphStyle(
        name='UsernameStyle',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.black,
        leading=inch * 2,  # Espaçamento entre linhas
        alignment=1  # Valor 1 para centralizar o texto
    )

    datetime_style = ParagraphStyle(
        name='DateTimeStyle',
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.black,
        alignment=1  # Valor 1 para centralizar o texto
    )

    # Add the username/ID paragraph to the PDF document
    username = search_user_by_id(id)["username"]
    username_text = f"{username} ({id})"
    username_para = Paragraph(username_text, username_style)

    elements = []

    # PRIMEIRA PÁGINA

    # Calculate the vertical position for centering horizontally
    cover_text_height = username_para.wrapOn(doc, doc.width, doc.height)[1]
    vertical_position = (doc.height - cover_text_height) / 2

    # Add vertical spacing to position the text in the center
    elements.append(Spacer(width=0, height=vertical_position))

    # Create the logo image object
    logo_path = os.getcwd() + "\\static\\images\\Eco.png"
    logo = Image(logo_path, width=1.5*inch, height=1*inch)

    elements.append(logo)
    elements.append(Spacer(width=0, height=2.5*inch))
    elements.append(username_para)

    # Create the date and time paragraph
    now = datetime.now()
    datetime_text = f"{now.strftime('%d-%m-%Y')}"
    datetime_para = Paragraph(datetime_text, datetime_style)
    elements.append(datetime_para)

    # PAGINAS SEGINTES
    dic_names = {"Expenses": "Despesas", "Profits": "Receitas", "Statement": "Geral"}
    # Create the logo image objects with colored background
    for path in image_paths:
        name = os.path.splitext(os.path.basename(path))[0].title()

        # Create the image and apply the colored background to the table cell
        image = Image(path, width=6.5*inch, height=5*inch)
        image_data = [[image]]

        # Define a colored background for the image cell
        bg_color = Color(52/255, 53/255, 65/255, alpha=1)
        image_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ])
        image_table = Table(image_data, style=image_style)

        elements.append(PageBreak())
        # Add custom cover page

        # Add text to cover page
        cover_text = dic_names[name]
        cover_text_style = ParagraphStyle(
            name='CoverTextStyle',
            fontName='Helvetica',
            fontSize=24,
            textColor=colors.black,
            leading=inch * 2,  # Espaçamento entre linhas
            alignment=1  # Centralizar horizontalmente
        )
        cover_text_para = Paragraph(cover_text, cover_text_style)

        # Calculate the vertical position for centering horizontally
        cover_text_height = cover_text_para.wrapOn(doc, doc.width, doc.height)[1]
        vertical_position = (doc.height - cover_text_height) / 2

        # Add vertical spacing to position the text in the center
        elements.append(Spacer(width=0, height=vertical_position))
        elements.append(cover_text_para)
        elements.append(PageBreak())

        if name == "Statement":
            # Create the table for the first dictionary data
            elements.append(Spacer(width=0, height=1*inch))
            table_data1 = [[str(key), str(value)] for key, value in dic_profits_expenses.items()]
            table1 = Table(table_data1, colWidths=[200, 200])
            table1.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (0, -1), (77/255, 155/255, 75/255)),  # Define a coluna da esquerda com uma cor de fundo
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centraliza os dados e o cabeçalho
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Define a fonte do cabeçalho
                ('FONTSIZE', (0, 0), (0, -1), 12),  # Define o tamanho da fonte do cabeçalho
            ]))
            elements.append(Spacer(width=0, height=vertical_position-250))
            elements.append(table1)
            #elements.append(PageBreak())
        elif name == "Expenses":
            # Create the table for the second dictionary data
            elements.append(Spacer(width=0, height=1*inch))
            table_data2 = [["Despesa", "Montante"]] + [[str(key), str(value)] for key, value in expenses_dic.items()]
            table2 = Table(table_data2, colWidths=[200, 200])
            table2.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), (77/255, 155/255, 75/255)),  # Define o cabeçalho com uma cor de fundo
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centraliza os dados e o cabeçalho
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Define a fonte do cabeçalho
                ('FONTSIZE', (0, 0), (-1, 0), 12),  # Define o tamanho da fonte do cabeçalho
            ]))
            elements.append(Spacer(width=0, height=vertical_position-200))
            elements.append(table2)
            elements.append(Spacer(width=0, height=0.1*inch))
            elements.append(PageBreak())
        elif name == "Profits":
            # Create the table for the third dictionary data
            elements.append(Spacer(width=0, height=1*inch))
            table_data3 = [["Receita", "Montante"]] + [[str(key), str(value)] for key, value in profits_dic.items()]
            table3 = Table(table_data3, colWidths=[200, 200])
            table3.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), (77/255, 155/255, 75/255)),  # Define o cabeçalho com uma cor de fundo
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centraliza os dados e o cabeçalho
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Define a fonte do cabeçalho
                ('FONTSIZE', (0, 0), (-1, 0), 12),  # Define o tamanho da fonte do cabeçalho
            ]))
            elements.append(Spacer(width=0, height=vertical_position-200))
            elements.append(table3)
            elements.append(Spacer(width=0, height=0.1*inch))
            elements.append(PageBreak())

        if path != image_paths[0]:
            # Add vertical spacing to position the image in the center
            elements.append(Spacer(width=0, height=vertical_position-150))
        elements.append(Spacer(width=0, height=0.3*inch))
        elements.append(image_table)

    doc.build(elements)
    return True
