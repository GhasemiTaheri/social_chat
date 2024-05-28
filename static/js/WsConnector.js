const socket = new WebSocket('ws://' + window.location.host + '/ws/chat/');
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    const socketEvent = new CustomEvent('SocketEvent', {
        detail: data
    });
    window.dispatchEvent(socketEvent);
}

function sendMessage() {
    const messageInput = $('#message-input');
    const message = messageInput.val();
    if (message === '' || message === null)
        return

    const data = {
        conversation: window.history.state.id,
        message,
    }
    socket.send(JSON.stringify(data));
    messageInput.val('');
}