var socketio = io();
const messages = document.getElementById("messages");

socketio.on("message", (data) => {
    createMessage(data.name, data.message, imagePath);
});

const createMessage = (name, msg, imgSrc) => {
    const content = `
    <div class="message">
        <div class="sender">
            <img src="${imgSrc}" alt="${name}'s image" class="sender-image">
            ${name}
        </div>
        <div class="text">${msg.replace(/\n/g, "<br>")}</div>
        <div class="muted">${new Date().toLocaleString()}</div>
        <br>
    </div>
    `;
    messages.insertAdjacentHTML("beforeend", content);
    messages.scrollTop = messages.scrollHeight;
};

const sendMessage = (id_, name_) => {
    const message = document.getElementById("message");
    if (message.value == "") return;
    socketio.emit("message", { name: id_, message: message.value });
    message.value = "";
};

var messageInput = document.getElementById("message");
var id = messageInput.getAttribute("data-id");
var username = messageInput.getAttribute("data-name");
messageInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage(id, username);
    } else if (event.key === "Enter" && event.shiftKey) {
        event.preventDefault();
        event.target.value += "\r\n";
    }
});


const scrollToBottom = () => {
    messages.scrollTop = messages.scrollHeight;
    document.getElementById('scroll-to-bottom').style.display = 'none';
};
