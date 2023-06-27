from handlers.processing_handlers import *


def set_activity_timer(id):
    data = read_json("\\database\\users.json")
    for user in data["users"]:
        # Check if the user id matches the provided id
        if user["id"] == id:
            # Update the last activity timestamp with the current date and time
            user["last_activity"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            write_json("\\database\\users.json", data)
            return True
    
    return False


def last_activity_check(id):
    data = read_json("\\database\\users.json")
    username = get_username_by_id(id)
    for user in data["users"]:
        # Check if the user id matches the provided id and if last_activity is not None
        if user["id"] == id and user["last_activity"] is not None:
            last_activity = datetime.strptime(user["last_activity"], "%d-%m-%Y %H:%M:%S")
            now = datetime.now()
            difference = now - last_activity
            if difference.total_seconds() > 60 and check_if_online(username):  # 10 minutes
                inactivate_user(id)
                return False
            elif not check_if_online(username):
                return False
            else:
                set_activity_timer(id)
                return True
    
    return False


def check_if_online(username):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # Search for the user with the given username
    for user in data["users"]:
        if user["username"] == username:
            return user["active"]

    # If no user is found, return None
    return None


def inactivate_user(id):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # Search for the user with the given ID
    for user in data["users"]:
        if user["id"] == id:
            # Set the user's active status to False
            user["active"] = False

            # Write the updated data back to users.json
            write_json("\\database\\users.json", data)

            # Return True to indicate successful inactivation
            return True

    # If no user is found, return False
    return False


def activate_user(id):
    # Read the users.json file
    data = read_json("\\database\\users.json")

    # Search for the user with the given ID
    for user in data["users"]:
        if user["id"] == id:
            # Set the user's active status to True
            user["active"] = True

            # Write the updated data back to users.json
            write_json("\\database\\users.json", data)

            # Return True to indicate successful activation
            return True

    # If no user is found, return False
    return False