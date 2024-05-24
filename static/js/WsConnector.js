const socket = new WebSocket('ws://' + window.location.host + '/ws/chat/');
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    const NewMessageEvent = new CustomEvent('NewMessageEvent', {
        detail: data
    });
    window.dispatchEvent(NewMessageEvent);
}