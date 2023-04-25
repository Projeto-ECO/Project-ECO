from flask import Flask
from views import views, new_message, on_connect, on_disconnect
from flask_socketio import SocketIO


app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")
app.config['SECRET_KEY'] = 'Projeto-ECO'
socketio = SocketIO(app)


@socketio.on("connect")
def connect(auth):
    print("conectou")
    on_connect(auth)



@socketio.on("message")
def message(data):
    print(data)
    new_message(data)



@socketio.on("disconnect")
def disconnect():
    print("desconectou")
    on_disconnect()



if __name__ == "__main__":
    socketio.run(app, debug=True, host = "192.168.1.64", port=6050)
