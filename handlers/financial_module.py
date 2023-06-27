import csv
from handlers.db_coordinator import *
from handlers.processing_handlers import *
from datetime import datetime, timedelta


def banking_operations(id, operation, coin, amount):
    # Convert amount to integer and coin to a formatted string with 2 decimal places
    amount = int(amount)
    coin = "{:.2f}".format(float(coin))

    # Read the account data from the JSON file
    data = read_json("\\database\\accounts\\" + id + "\\" + id + ".json")

    if operation == "deposit":
        # Perform deposit operation
        for coin_ in data["coins"]:
            if str(coin_["name"]) == str(coin):
                if register_operation(id, operation, coin, amount):
                    data["coinAmounts"][coin] = data["coinAmounts"][coin] + amount
                    write_json("\\database\\accounts\\" + id + "\\" + id + ".json", data)
                    break
                else:
                    return False
    elif operation == "withdrawl":
        # Perform withdrawal operation
        for coin_ in data["coins"]:
            if str(coin_["name"]) == str(coin) and data["coinAmounts"][coin] >= amount and amount > 0:
                if register_operation(id, operation, coin, amount):
                    data["coinAmounts"][coin] = data["coinAmounts"][coin] - amount
                    write_json("\\database\\accounts\\" + id + "\\" + id + ".json", data)
                    break
                else:
                    return False

    # Return True to indicate the operation was successful
    return True


def register_operation(id, operation, coin, amount):
    # Get the current account balance
    accountBalance = get_account_balance(id)

    try:
        # Check if the statement file exists and create it if necessary
        if check_statement_existence(id):
            directory = os.getcwd()
            total = float(coin) * float(amount)

            if operation == "deposit":
                # Update account balance for a deposit
                accountBalance += total
            elif operation == "withdrawl":
                # Update account balance for a withdrawal
                accountBalance -= total
                total = -total
            else:
                # Invalid operation
                return False

            # Create a new statement row
            statement_row = [
                datetime.now().strftime('%d-%m-%Y'),
                operation.title(),
                "{:.2f}".format(total) + " €",
                "{:.2f}".format(accountBalance) + " €"
            ]

            # Read existing rows from the statement file
            with open(directory + f"\\database\\accounts\\{id}\\{id}.csv", "r", newline="", encoding="utf8") as file:
                csv_reader = csv.reader(file, delimiter=";")
                existing_rows = [row for row in csv_reader]

            # Write the new statement row along with the existing rows to the statement file
            with open(directory + f"\\database\\accounts\\{id}\\{id}.csv", "w", newline="", encoding="utf8") as file:
                csv_writer = csv.writer(file, delimiter=";")
                csv_writer.writerows([existing_rows[0], statement_row] + existing_rows[1:])

            # Return True to indicate successful operation registration
            return True

    except:
        # An error occurred
        return False


def get_statement(id):
    # Open the statement file for reading
    with open(os.getcwd() + f"\\database\\accounts\\{id}\\{id}.csv", "r") as file:
        # Read the CSV content using the CSV reader
        csv_reader = csv.reader(file, delimiter=";")
        # Convert the CSV reader object to a list and return it
        return list(csv_reader)


def get_account_balance(id):
    # Read the JSON data from the account file
    data = read_json("\\database\\accounts\\" + id + "\\" + id + ".json")

    # Initialize the total balance
    total = 0

    # Calculate the total balance by multiplying the coin amounts with their respective values
    for coin_ in data["coins"]:
        total += float(data["coinAmounts"][coin_["name"]]) * float(coin_["value"])

    # Return the total account balance
    return total


def get_date_balance(id):
    
    with open(os.getcwd() + f"\\database\\accounts\\{id}\\{id}.csv", "r") as file:
        csv_reader = csv.reader(file, delimiter=";")
        data = list(csv_reader)
        data.pop(0)
        date = data[-1][0]
        dic = {}
        for row in data[::-1]:
            dic[row[0]] = row[3]
        return dic
