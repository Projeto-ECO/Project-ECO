from time import localtime, strftime
import time
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file
from handlers.processing_handlers import *
from handlers.activity_handler import *
from handlers.financial_module import *
from flask_socketio import send, leave_room, join_room
from werkzeug.utils import secure_filename


views = Blueprint(__name__, "views")


@views.route("/")
def index():
    return render_template("index.html")



@views.route('/dados_saldo/<id>')
def get_dados_saldo(id):
    if last_activity_check(id):
        dic = get_date_balance(id)
        dados = []
        for data, saldo in dic.items():
            dados.append({
                'data': data,
                'saldo': saldo
            })

        return jsonify(dados)
    else:
        return redirect(url_for("views.index"))
    

@views.route('/save-graphic/<id>', methods=['POST'])
def save_graphic(id):
    if last_activity_check(id):
        image_url = request.json.get('imageUrl')
        save_image(image_url, id)
        return jsonify({'status': 'success'})
    else:
        return redirect(url_for("views.index"))



@views.route("/profile/<username>")
def profile(username):
    if not username:
        username = request.referrer.split("/")[-1]
    activity_status = check_if_online(username)
    if activity_status == True:
        id=get_id_by_username(username)
        if id is None:
            return redirect(url_for("views.index"))
        elif last_activity_check(id):
            if check_image_existence(id):
                return render_template("profile.html", name=username, id=id, activity_status=activity_status, image_number = id)
            else:
                return render_template("profile.html", name=username, id=id, activity_status=activity_status, image_number = "default")
        else:
            return redirect(url_for("views.index"))
    else:
        return redirect(url_for("views.index"))


@views.route("/data/<id>")
def get_data(id):
    if last_activity_check(id):
        return jsonify(read_json("/database/accounts/"+id+"\\"+id+".json"))
    else:
        return redirect(url_for("views.index"))


@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.index"))


@views.route("/calendar/<id>")
def calendar(id):
    dic = read_json("/database/accounts/"+id+"\\"+"loans.json")
    return dic


@views.route("/two-factor-auth-login/<username>", methods=["GET", "POST"])
def two_factor_auth_login(username):
    code = session.get("code")
    data = read_json("\\database\\users.json")
    for user in data["users"]:
        if user["username"] == username:
            if user["active"] == True and last_activity_check(user["id"]): # check if user is already authenticated
                return redirect(url_for("views.profile", username=username))
            else:
                if request.method == "POST":
                    entered_code = request.form.get("code")
                    if entered_code == code:
                        user["active"] = True
                        write_json("\\database\\users.json", data)
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
        if " " in username and len(username.split(" ")) == 2:
            username = username.replace(" ", "")
        if validate_login(username, password) is False:
            return render_template("login.html", message="User or password are incorrect.")
        else:
            if "@" in username:
                username = search_user_by_email(username)["username"]
            code = generate_two_factor_auth_code()
            session["code"] = code
            session["username"] = username
            session["id"] = get_id_by_username(username)
            if not last_activity_check(session["id"]):
                send_two_factor_auth_code(username, code, "login")
            return redirect(url_for("views.two_factor_auth_login", username = username))
    else:
        return render_template("login.html")


@views.route("/logout/<name>", methods=["POST", "GET"])
def logout(name):
    id = get_id_by_username(name)
    if last_activity_check(id):
        if inactivate_user(id):
            session.clear()
            return redirect(url_for("views.index"))
        else:
            return redirect(url_for("views.profile", username=name))
    else:
        return redirect(url_for("views.index"))


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
    if last_activity_check(get_id_by_username(name)) is False:
        return redirect(url_for("views.index"))
    else:
        coin = request.form.get("coin-deposit")
        if "," in coin:
            coin = coin.replace(",", ".")
        amount = request.form.get("amount-deposit")
        banking_operations(get_id_by_username(name), "deposit", coin, amount)
        
        return redirect(url_for("views.profile", username=name))


@views.route("/withdrawl/<name>", methods=["POST", "GET"])
def withdrawl(name):
    if last_activity_check(get_id_by_username(name)) is False:
        return redirect(url_for("views.index"))
    else:
        set_activity_timer(get_id_by_username(name))
        coin = request.form.get("coin-withdrawl")
        if "," in coin:
            coin = coin.replace(",", ".")
        amount = request.form.get("amount-withdrawl")
        banking_operations(get_id_by_username(name), "withdrawl", coin, amount)
        
        return redirect(url_for("views.profile", username=name))


@views.route("/download_pdf/<id>")
def download_pdf(id):
    if last_activity_check(id) is False:
        return redirect(url_for("views.index"))
    else:
        set_activity_timer(id)
        username = search_user_by_id(id)["username"]
        csv_to_pdf(os.getcwd()+f"\\database/accounts\\{id}\\{id}.csv", id)
        filename = os.getcwd()+f"\\database/accounts\\{id}\\{id}.pdf"
        response = send_file(filename, as_attachment=True)
        response.headers['Content-Disposition'] = f'attachment; filename=ECO_Statement_{username}.pdf'
        return response


@views.route("/statement/<name>", methods=["POST", "GET"])
def statement(name):
    id = get_id_by_username(name)
    if last_activity_check(id) is False:
        return redirect(url_for("views.index"))
    else:
        set_activity_timer(id)
        if request.method == "POST":
            # Obter arquivo do formulário
            file = request.files["file"]
            # Obter nome do arquivo
            filename = secure_filename(file.filename)
            # Verificar se o arquivo é Excel ou CSV
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".xlsx" or ext == ".csv" or ext == ".xls":
                store_status = store_statement(file, filename, ext, id)
                if not store_status:
                    return jsonify({"status": "error", "message": "Erro ao armazenar arquivo. Só são aceites extratos do Santander e Caixa Geral de Depósitos."})
            else:
                return jsonify({"status": "error", "message": "Por favor, selecione um arquivo Excel ou CSV."})
            # Return a success response
            return jsonify({"status": "success", "message": "Arquivo submetido com sucesso!"})

        # Code for GET request here
        expenses, expenses_dic = get_expenses(id)
        profits, profits_dic = get_profits(id)
        dic = {"Despesas": Decimal(expenses.split("€")[0]).quantize(Decimal('0.01')), "Receitas": Decimal(profits.split("€")[0]).quantize(Decimal('0.01'))}
        image_base64 = get_pizza_info(dic, id, "statement")
        return render_template("statement.html", username=name, id=get_id_by_username(name), image_base64_profits_expenses=image_base64)


@views.route("/download_economic_report/<id>")
def download_economic_report(id):
    if last_activity_check(id) is False:
        return redirect(url_for("views.index"))
    else:
        set_activity_timer(id)
        output = os.getcwd()+f"\\database/accounts\\{id}\\analysis\\economic_report.pdf"
        chart_dir = os.getcwd()+f"\\database\\accounts\\{id}\\analysis\\ECO_chart.png"
        if not os.path.exists(chart_dir):
            chart_dir = None
        image_paths = [os.getcwd()+f"\\database/accounts\\{id}\\analysis\\expenses.png", os.getcwd()+f"\\database/accounts\\{id}\\analysis\\profits.png", os.getcwd()+f"\\database/accounts\\{id}\\analysis\\statement.png", chart_dir]
        expenses, expenses_dic = get_expenses(id)
        profits, profits_dic = get_profits(id)
        get_pizza_info(profits_dic, id, "profits") 
        get_pizza_info(expenses_dic, id, "expenses") 
        dic_profits_expenses = {"Despesas": Decimal(expenses.split("€")[0]).quantize(Decimal('0.01')), "Receitas": Decimal(profits.split("€")[0]).quantize(Decimal('0.01'))}
        chart_dir = os.getcwd()+f"\\database\\accounts\\{id}\\analysis\\ECO_chart.png"
        if not os.path.exists(chart_dir):
            chart_dir = None
        generate_economic_report(output, image_paths, id, dic_profits_expenses, expenses_dic, profits_dic)
        response = send_file(os.getcwd()+f"\\database/accounts\\{id}\\analysis\\economic_report.pdf", as_attachment=True)
        response.headers['Content-Disposition'] = f'attachment; filename=economic_report.pdf'
        return response


@views.route('/expenses/<id>')
def expenses(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.index"))
    else:
        expenses, expenses_dic = get_expenses(id)
        image_base64 = get_pizza_info(expenses_dic, id, "expenses")
        name = search_user_by_id(id)["username"]
        return render_template('expenses.html', expenses=expenses, expenses_dic=expenses_dic, image_base64=image_base64, id=id, username = name)


@views.route('/profits/<id>')
def profits(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.index"))
    else:
        profits, profits_dic = get_profits(id)
        image_base64 = get_pizza_info(profits_dic, id, "profits")
        name = search_user_by_id(id)["username"]
        return render_template('profits.html', profits=profits, profits_dic=profits_dic, image_base64_profits=image_base64, id=id, username = name)


@views.route("/account/<username>")
def account(username):
    if last_activity_check(get_id_by_username(username)) == False:
        return redirect(url_for("views.login"))
    else:
        return render_template("account.html", username=username, id=get_id_by_username(username))

@views.route("/database/accounts/<id>/<image>", methods=["POST", "GET"])
def account_image(id, image):
    if last_activity_check(id) == False:
        return redirect(url_for("views.login"))
    else:
        return send_file(os.getcwd()+f"/database/accounts/{id}/{image}", mimetype='image/png')


@views.route('/get_image/<path:filename>')
def get_image(filename):
    return send_file(filename, mimetype='image/png')


@views.route("/update_account/<id>", methods=["POST"])
def update_account(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.index"))
    else:
        # create the file path
        file_path = os.getcwd()+f"/database/accounts/{id}/{id}.png"

        # save the uploaded file
        profile_photo = request.files.get("profile_photo")
        if profile_photo:
            profile_photo.save(file_path)

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("psw")
        if username != "" and not check_username_exists(username):
            update_username(id, username)
            session["username"] = username
        else:
            username = search_user_by_id(id)["username"]
        if email != "" and not check_email_exists(email):
            update_email(id, email)
        else:
            email = search_user_by_id(id)["email"]
        if password != "":
            update_password(id, password)
        
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
        return redirect(url_for("views.index"))
    else:
        session.clear()
        if request.method == "POST":
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)

            if join != False and not code:
                username = get_username_by_id(id)
                return render_template("chat_home.html", error="Please enter a room code.", code=code, name=id, username=username)
            

            room_code = code
            if create != False:
                room_code = create_room()
            elif check_room_code_exists(code) == False:
                username = get_username_by_id(id)
                return render_template("chat_home.html", error="Room does not exist.", code=code, name=id, username=username)
            
            session["room"] = room_code
            session["name"] = get_username_by_id(id)
            set_activity_timer(id)
            return redirect(url_for("views.chat_room", id = id, name  = session.get("name")))

        username = get_username_by_id(id)
        return render_template("chat_home.html", code="", name=id, username=username)


@views.route("/chat_room/<id>")
def chat_room(id):
    if last_activity_check(id) == False:
        return redirect(url_for("views.index"))
    else:
        room = session.get("room")
        if room is None or check_room_code_exists(room) == False:
            return redirect(url_for("views.chat_home", id=id))
        messages = get_room_messages(room)
        for element in messages:
            element["image"] = element["image"].replace("\\", "/")
        return render_template("chat_room.html", code=room, messages=messages, id=id, name=get_username_by_id(id))


def new_message(data):
    room = session.get("room")
    
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


def on_connect(auth, place):
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
        if not room or not name: return
        if check_room_code_exists(room) == False:
            leave_room(room)
            return
        join_room(room)
        send({"name": name, "id": get_id_by_username(name), "message": name+" has entered the room", "time": strftime("%d-%m-%Y %H:%M", localtime()), "image":get_image_path(get_id_by_username(name))}, to=room)
        add_room_member(room, name, get_id_by_username(name))



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
            data = read_json("\\database\\rooms.json")
            for room in data["rooms"]:
                if room["code"] == session.get("room"):
                    room["members"].remove({"name": name, "id": get_id_by_username(name)})
                    write_json("\\database\\rooms.json", data)
                    break
            room = session.get("room")
            time.sleep(5)
            if get_number_of_room_members(room) <= 0:
                delete_room(room)
        send({"name": name, "id": get_id_by_username(name), "message": name+" has left the room", "time": strftime("%d-%m-%Y %H:%M", localtime()), "image":get_image_path(get_id_by_username(name))}, to=room)
        leave_room(room)
    else: return


def inactivate_account(id):
    inactivate_user(id)
    session.clear()

def activate_account(name):
    id = get_id_by_username(name)
    activate_user(id)
