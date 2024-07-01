let userId;

class EventManager {
    constructor() {
        this.eventHandlers = {};
    }

    addEventListener(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    removeEventListener(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
        }
    }

    dispatchEvent(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }
}

class NotificationManager {
    static notify(message) {
        if (Notification.permission === "granted") {
            new Notification(message);
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then((permission) => {
                if (permission === "granted") {
                    new Notification("message");
                }
            });
        }
    }
}

class ConversationAPI {
    static getConversations() {
        return $.ajax({url: 'conversation/'});
    }

    static getConversationInformation(conversationId) {
        return $.ajax({url: `conversation/${conversationId}/`});
    }

    static getConversationMessages(conversationId, lastMessageId = 0) {
        return $.ajax({
            url: `conversation/${conversationId}/get_messages/?last_message_id=${lastMessageId}`
        });
    }

    static deleteConversation(conversationId) {
        const csrfToken = $('[name="csrfmiddlewaretoken"]').attr('value');
        return $.ajax({
            headers: {'X-CSRFToken': csrfToken},
            url: `conversation/${conversationId}/leave_conversation/`,
            method: 'delete'
        });
    }
}

class ConversationUI {
    static addNewConversation(conversation) {
        $('#chats').prepend(`
            <a class="filterDiscussions all single ${conversation.unread_messages > 0 ? 'unread' : 'read'}"
               data-toggle="list" data-conversationId="${conversation.id}" role="tab"
               onclick="conversationOnClick(this)">
                <img class="avatar-md" src="${conversation.avatar}"
                     data-toggle="tooltip" data-placement="top" title="${conversation.title}" alt="avatar">
                ${conversation.unread_messages > 0 ? `<div class="new bg-primary"><span>${conversation.unread_messages}</span></div>` : ''}
                <div class="data">
                    <h5>${conversation.title}</h5>
                    <p>${conversation.last_message}</p>
                </div>
            </a>
        `);
    }

    static removeConversation(conversationId) {
        $(`[data-conversationid=${conversationId}]`).remove();
        if (window.history.state.id === conversationId) window.history.back();
    }

    static updateConversationInfo(conversationInfo) {
        const conversationImg = $("#conversation-image");
        conversationImg.attr('src', conversationInfo.avatar);
        conversationImg.attr('title', conversationInfo.title);

        let information = `<h5><a href="#">${conversationInfo.title}</a></h5>`;
        const conversationActionsMenu = $('#conversation-action');

        const groupActionList = `
            <button class="dropdown-item">
                <i class="material-icons">info</i>
                About
            </button>
            <button class="dropdown-item" onclick="deleteConversation()">
                <i class="material-icons">exit_to_app</i>
                Leave and delete
            </button>`;

        const singleActionList = `
            <button class="dropdown-item" onclick="deleteConversation()">
                <i class="material-icons">delete</i>
                Delete Conversation
            </button>`;

        if (conversationInfo.conversation_type === 'gr') {
            information += `<span>${conversationInfo.member_count} members</span>`;
            conversationActionsMenu.html(groupActionList);
        } else {
            conversationActionsMenu.html(singleActionList);
        }

        $('#conversation-data').html(information);
    }

    static addMessageToConversation(message, prepend = false) {
        const messageContainer = $("#message-container");
        const messageDate = new Date(message.create_at);

        const othersMessagesTemplate = `<div class="message" data-id="#ID">
            <img class="avatar-md" src="#AVATAR" data-toggle="tooltip" data-placement="top" title="#TITLE" alt="avatar">
            <div class="text-main">
                <div class="text-group">
                    <div class="text">
                        <p>#TEXT</p>
                    </div>
                </div>
                <span>#EXTRA</span>
            </div>
        </div>`
            .replace('#ID', message.id)
            .replace("#AVATAR", message.sender.get_avatar)
            .replace('#TITLE', message.sender.display_name)
            .replace("#TEXT", message.text)
            .replace('#EXTRA', `${message.sender.display_name} | ${messageDate.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            })}`);

        const myMessageTemplate = `<div class="message me" data-id="#ID">
            <div class="text-main">
                <div class="text-group me">
                    <div class="text me">
                        <p>#TEXT</p>
                    </div>
                </div>
                <span>#EXTRA</span>
            </div>
        </div>`
            .replace('#ID', message.id)
            .replace('#TEXT', message.text)
            .replace('#EXTRA', `${messageDate.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`);

        const finalMessage = (String(message.sender.id) === String(userId)) ? myMessageTemplate : othersMessagesTemplate;

        if (prepend) {
            messageContainer.prepend(finalMessage);
        } else {
            messageContainer.append(finalMessage);
        }
    }

    static createArchiveMessage(messageGroup, scrollToBottom) {
        const messageContainer = $("#message-container");
        const dateTemplate = `<div class="date">
            <hr>
            <span>#DATE</span>
            <hr>
        </div>`;

        Object.entries(messageGroup).forEach(([date, messages]) => {
            messages.forEach(message => this.addMessageToConversation(message, true));

            const currentDate = new Date();
            const groupDate = new Date(date);
            const timeDifference = Math.abs(currentDate - groupDate);
            const dayDifference = Math.floor(timeDifference / (1000 * 60 * 60 * 24));

            if (dayDifference === 0) {
                messageContainer.prepend(dateTemplate.replace("#DATE", 'Today'));
            } else if (dayDifference === 1) {
                messageContainer.prepend(dateTemplate.replace("#DATE", 'Yesterday'));
            } else {
                messageContainer.prepend(dateTemplate.replace("#DATE", `${date}`));
            }
        });

        if (scrollToBottom) {
            $('#content').animate({scrollTop: $('#content').prop("scrollHeight")}, 500);
        }
    }
}

class ConversationManager {
    constructor() {
        this.eventManager = new EventManager();
        userId = window.sessionStorage.getItem('user-id');
        this.initEventListeners();
    }

    initEventListeners() {
        window.addEventListener('popstate', this.handlePopState.bind(this));
        window.addEventListener('SocketEvent', this.handleSocketEvent.bind(this));

        $(document).ready(() => {
            this.getConversations();
        });
    }

    handlePopState(event) {
        if (event.state.type === 'chat-active') {
            $('#message-container').empty();
            this.getConversationInformation(event.state.id);
            this.getConversationMessage(event.state.id);
            $('#content').on('scroll', this.handleScroll.bind(this));
        }
    }

    handleSocketEvent(event) {
        const payload = event.detail;
        if ('event_type' in payload) {
            switch (payload.event_type) {
                case 'new_message':
                    this.handleNewMessage(payload.data);
                    break;
                case 'conversation_add':
                    ConversationUI.addNewConversation(payload.data);
                    break;
                case 'conversation_remove':
                    ConversationUI.removeConversation(payload.data.id);
                    break;
            }
        }
    }

    handleNewMessage(data) {
        $(`[data-conversationId="${data.conversation}"]`).prependTo("#chats");
        $(`[data-conversationId="${data.conversation} p"]`).text(data.text.slice(0, 15));
        if (window.history.state.id === data.conversation) {
            ConversationUI.addMessageToConversation(data);
            return;
        }

        const unreadMessageCounter = $(`[data-conversationId="${data.conversation}"] .new span`);
        if (unreadMessageCounter.length) {
            unreadMessageCounter.text(parseInt(unreadMessageCounter.text()) + 1);
        } else {
            $(`[data-conversationId="${data.conversation}"] img`).after('<div class="new bg-primary"><span>1</span></div>');
        }

        NotificationManager.notify(`${data.sender.display_name}: ${data.text}`);
    }

    handleScroll(event) {
        if (event.target.scrollTop === 0) {
            console.log('im runn mojtaba')
            const lastFetchId = $("#message-container").children('.message').first().data('id');
            const scrollTopBefore = event.target.scrollHeight;

            this.getConversationMessage(window.history.state.id, lastFetchId, false).then(() => {
                const scrollTopAfter = event.target.scrollHeight;
                event.target.scrollTop = scrollTopAfter - scrollTopBefore;
            });
        }
    }

    getConversations() {
        ConversationAPI.getConversations().then(({results}) => {
            results.forEach(conversation => ConversationUI.addNewConversation(conversation));
        });
    }

    getConversationInformation(conversationId) {
        ConversationAPI.getConversationInformation(conversationId).then(conversationInfo => {
            ConversationUI.updateConversationInfo(conversationInfo);
        });
    }

    getConversationMessage(conversationId, lastMessageId = 0, scrollToBottom = true) {
        return ConversationAPI.getConversationMessages(conversationId, lastMessageId).then(({results}) => {
            const groupedMessage = this.groupMessageByDate(results);
            ConversationUI.createArchiveMessage(groupedMessage, scrollToBottom);
        });
    }

    groupMessageByDate(messageList) {
        const result = {};

        messageList.forEach(message => {
            const localDate = new Date(message.create_at).toLocaleDateString();
            if (!result[localDate]) result[localDate] = [];
            result[localDate].push(message);
        });

        return result;
    }
}

// Initialize the ConversationManager
new ConversationManager();
