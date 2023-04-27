from time import localtime, strftime
import time
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file
from handlers import *
from flask_socketio import send, leave_room, join_room


views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/profile/<username>")
def profile(username):
    if not username:
        username = request.referrer.split("/")[-1]
        print("USERNAME------------------------ "+ username)
    activity_status = check_if_online(username)
    if activity_status == True:
        id=get_id_by_username(username)
        print("ID----------->"+id)
        if id is None:
            return redirect(url_for("views.home"))
        elif last_activity_check(id):
            if check_image_existence(id):
                return render_template("profile.html", name=username, id=id, activity_status=activity_status, image_number = id)
            else:
                return render_template("profile.html", name=username, id=id, activity_status=activity_status, image_number = "default")
        else:
            return redirect(url_for("views.home"))
    else:
        return redirect(url_for("views.home"))


@views.route("db_handler/users.json")
def get_users():
    return jsonify(read_json("\\db_handler\\users.json"))


@views.route("/data/<id>")
def get_data(id):
    return jsonify(read_json("/accounts/"+id+"\\"+id+".json"))


@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.home"))


@views.route("/two-factor-auth-login/<username>", methods=["GET", "POST"])
def two_factor_auth_login(username):
    code = session.get("code")
    data = read_json("\\db_handler\\users.json")
    for user in data["users"]:
        if user["username"] == username:
            if user["active"] == True and last_activity_check(user["id"]): # check if user is already authenticated
                return redirect(url_for("views.profile", username=username))
            else:
                if request.method == "POST":
                    entered_code = request.form.get("code")
                    if entered_code == code:
                        user["active"] = True
                        write_json("\\db_handler\\users.json", data)
                        set_activity_timer(user["id"])
                        session["username"] = username
                        session["id"] = get_id_by_username(username)
                        return redirect(url_for("views.profile", username=username))
                return render_template("two-factor-auth-login.html", username=username)
    return redirect(url_for("views.login"))


@views.route("/two-factor-auth-signup/", methods=["GET", "POST"])
def two_factor_auth_signup():
    code = session.get("code_signup")
    password = session.get("password_signup")
    username = session.get("username_signup")
    email = session.get("email_signup")
    if request.method == "POST":
        entered_code = request.form.get("code_signup")
        if entered_code == code:
            create_user(username, password, email)
            return redirect(url_for("views.login", username=username))
    return render_template("two-factor-auth-signup.html")


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
            send_two_factor_auth_code(username, code, "login")
            return redirect(url_for("views.two_factor_auth_login", username = username))
    else:
        return render_template("login.html")

@views.route("/logout", methods=["POST"])
def logout():
    if inactivate_user( session.get("id")):
        session.clear()
        return redirect(url_for("views.home"))
    else:
        return redirect(url_for("views.profile", username=session.get("username")))


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
            code = generate_two_factor_auth_code()
            session["code_signup"] = code
            session["username_signup"] = username
            session["email_signup"] = email
            session["password_signup"] = password
            content = {"username": username, "email": email}
            send_two_factor_auth_code(content, code, "signup")
            return redirect(url_for("views.two_factor_auth_signup"))
    else:
        return render_template("signup.html")


@views.route("/deposit/<name>", methods=["POST", "GET"])
def deposit(name):
    print("entrou")
    coin = request.form.get("coin-deposit")
    if "," in coin:
        coin = coin.replace(",", ".")
    amount = request.form.get("amount-deposit")
    banking_operations(get_id_by_username(name), "deposit", coin, amount)
    set_activity_timer(get_id_by_username(name))
    return redirect(url_for("views.profile", username=name))


@views.route("/withdrawl/<name>", methods=["POST", "GET"])
def withdrawl(name):
    coin = request.form.get("coin-withdrawl")
    if "," in coin:
        coin = coin.replace(",", ".")
    amount = request.form.get("amount-withdrawl")
    banking_operations(get_id_by_username(name), "withdraw", coin, amount)
    set_activity_timer(get_id_by_username(name))
    return redirect(url_for("views.profile", username=name))


@views.route("/download_pdf/<id>")
def download_pdf(id):
    username = search_user_by_id(id)["username"]
    csv_to_pdf(os.getcwd()+f"\\accounts\\{id}\\{id}.csv", id)
    filename = os.getcwd()+f"\\accounts\\{id}\\{id}.pdf"
    response = send_file(filename, as_attachment=True)
    response.headers['Content-Disposition'] = f'attachment; filename=ECO_Statement_{username}.pdf'
    set_activity_timer(id)
    return response


@views.route("/account/<username>")
def account(username):
    if last_activity_check(get_id_by_username(username)) == False:
        return redirect(url_for("views.login"))
    set_activity_timer(get_id_by_username(username))
    return render_template("account.html", username=username, id=get_id_by_username(username))

@views.route("/accounts/<id>/<image>", methods=["POST", "GET"])
def account_image(id, image):
    return send_file(os.getcwd()+f"/accounts/{id}/{image}", mimetype='image/png')


@views.route('/get_image/<path:filename>')
def get_image(filename):
    return send_file(filename, mimetype='image/png')


@views.route("/update_account/<id>", methods=["POST"])
def update_account(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.login"))
    # create the file path
    file_path = os.getcwd()+f"/accounts/{id}/{id}.png"

    # save the uploaded file
    profile_photo = request.files.get("profile_photo")
    if profile_photo:
        profile_photo.save(file_path)

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("psw")
    if username != "":
        update_username(id, username)
        session["username"] = username
    else:
        username = search_user_by_id(id)["username"]
    if email != "":
        update_email(id, email)
    if password != "":
        update_password(id, password)
    set_activity_timer(id)
    return redirect(url_for("views.profile", username=get_username_by_id(id)))


@views.route('/check_username', methods=['POST'])
def check_username():
    username = request.form.get('username')
    exists = check_username_exists(username)
    response = {'exists': exists}
    return jsonify(response)


@views.route('/check_email', methods=['POST'])
def check_email():
    email = request.form.get('email')
    exists = check_email_exists(email)
    response = {'exists': exists}
    return jsonify(response)



@views.route("/chat_home/<id>", methods=["POST", "GET"])
def chat_home(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.login"))
    session.clear()
    if request.method == "POST":
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        with open("cenas.txt", "w+") as f:
                f.write("code-" + str(code) + " join-" + str(join) + " create-" + str(create))

        if join != False and not code:
            with open("cenas.txt", "a+") as f:
                f.write("\nentrou")
            return render_template("chat_home.html", error="Please enter a room code.", code=code, name=id)
        

        room_code = code
        if create != False:
            room_code = create_room()
        elif check_room_code_exists(code) == False:
            return render_template("chat_home.html", error="Room does not exist.", code=code, name=id)
        
        session["room"] = room_code
        session["name"] = get_username_by_id(id)
        set_activity_timer(id)
        return redirect(url_for("views.chat_room", id = id, name  = session.get("name")))

    return render_template("chat_home.html")


@views.route("/chat_room/<id>")
def chat_room(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.login"))
    room = session.get("room")
    if room is None or check_room_code_exists(room) == False:
        return redirect(url_for("views.chat_home", id=id))
    messages = get_room_messages(room)
    for element in messages:
        element["image"] = element["image"].replace("\\", "/")
    print(messages)
    return render_template("chat_room.html", code=room, messages=messages, id=id, name=get_username_by_id(id))


def new_message(data):
    room = session.get("room")
    with(open("cenas.txt", "a+")) as f:
        f.write("\nentrou-" + str(room) + " " + str(data))
    
    if check_room_code_exists(room) == False:
        return
    
    name = get_username_by_id(data["name"])

    content = {
        "name": name,
        "id" : data["name"],
        "message": data["message"],
        "time": strftime("%d-%m-%Y %H:%M", localtime()),
        "image": get_image_path(data["name"])
    }
    send(content, to=room)
    add_room_message(room, content)
    print(f"{name} said: {data['message']}")


def on_connect(auth, place):
    print("PLACE------------------", place)
    if "profile" in place:
        name = place.split("/")[-1]
        id = get_id_by_username(name)
        session["username"] = name
        session["id"] = id
        activate_user(id)
        return
    elif "chat_room" in place:
        room = session.get("room")
        name = session.get("name")
        print(f"{name} connected to room {room}")
        if not room or not name:
            print("Room or name not found")
            return
        if check_room_code_exists(room) == False:
            print(f"Room {room} does not exist")
            leave_room(room)
            return
        
        join_room(room)
        print(f"{name} joined room {room}")
        send({"name": name, "id": get_id_by_username(name), "message": name+" has entered the room", "time": strftime("%d-%m-%Y %H:%M", localtime()), "image":get_image_path(get_id_by_username(name))}, to=room)
        add_room_member(room, name, get_id_by_username(name))
        print(f"{name} joined room {room}")



def on_disconnect(place):
    if "profile" in place:
        name = place.split("/")[-1]
        id = get_id_by_username(name)
        inactivate_account(id)
        return
    elif "chat_room" in place:
        room = session.get("room")
        name = session.get("name")

        if check_room_code_exists(room):
            data = read_json("\\db_handler\\rooms.json")
            for room in data["rooms"]:
                if room["code"] == session.get("room"):
                    room["members"].remove({"name": name, "id": get_id_by_username(name)})
                    write_json("\\db_handler\\rooms.json", data)
                    break
            room = session.get("room")
            time.sleep(5)
            if get_number_of_room_members(room) <= 0:
                print(f"Room {room} has no members")
                delete_room(room)
        send({"name": name, "id": get_id_by_username(name), "message": name+" has left the room", "time": strftime("%d-%m-%Y %H:%M", localtime()), "image":get_image_path(get_id_by_username(name))}, to=room)
        print(f"{name} has left the room {room}")
        leave_room(room)
    else:
        print("Place not found - ", place)
        return


def inactivate_account(id):
    inactivate_user(id)
    session.clear()

def activate_account(name):
    id = get_id_by_username(name)
    activate_user(id)
