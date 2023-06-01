from flask import Flask, request
from views import views, new_message, on_connect, on_disconnect
from flask_socketio import SocketIO


app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")
app.config['SECRET_KEY'] = 'Projeto-ECO'
socketio = SocketIO(app)


@socketio.on("connect")
def connect(auth):
    place = request.referrer.split("/")[-2]
    if "chat" in place:
        on_connect(auth, place)
    elif place == "profile":
        place += "/" + request.referrer.split("/")[-1]
        on_connect(auth, place)
        place = place.split("/")[-1]



@socketio.on("message")
def message(data):
    new_message(data)



@socketio.on("disconnect")
def disconnect():
    place = request.referrer.split("/")[-2]
    if place == "profile":
        place += "/" + request.referrer.split("/")[-1]
    on_disconnect(place)


if __name__ == "__main__":
    socketio.run(app, debug=True, host = "127.0.0.1", port=6070)

# Portas
# 6070 - Desktop-Tiago
# 7070 - Laptop-Tiago

# Portas Abertas
# 6000 - 6100 - Desktop-Tiago
# 7000 - 7100 - Laptop-Tiago

# Desktop-Tiago
# 192.168.1.64:6070

# Laptop-Tiago
# 192.168.1.156:7070

# IP Público
# 5.249.29.20:6070 - Desktop-Tiago
# 5.249.29.20:7070 - Laptop-Tiago


# Links
# http://financialtipeco.online:5070/
# http://www.financialtipeco.online:5070/