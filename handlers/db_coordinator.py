import os
import json


def read_json(filename):
    directory = os.getcwd()

    # Check if the file exists and handle specific cases
    if not os.path.exists(directory + filename):
        if filename == "\\database\\users.json":
            # Create a new file and initialize it with an empty "users" list
            write_json(filename, {"users": []})
        elif filename == "\\database\\rooms.json":
            # Create a new file and initialize it with an empty "rooms" list
            write_json(filename, {"rooms": []})

        # Set the data to None since the file was just created
        data = None
    else:
        # Read the file and load its content as JSON
        with open(directory + filename) as file:
            data = json.load(file)

    return data


def write_json(file, data):
    directory = os.getcwd()
    file_dir = file.split("\\")[0]

    # Check if the directory exists, create it if it doesn't
    if not os.path.exists(directory + file_dir):
        os.makedirs(directory + file_dir)
        print("Created directory:", directory + file_dir)

    # Write the JSON data to the file with proper indentation
    with open(directory + file, "w+") as f:
        json.dump(data, f, indent=4)

    return True