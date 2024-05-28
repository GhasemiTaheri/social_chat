window.addEventListener('popstate', (event) => {
    if (event.state.type === 'chat-active') {
        $('#message-container').empty();
        getConversationInformation(event.state.id);
        getConversationMessage(event.state.id);
    }
});

$(document).ready(() => {
    getConversations();
})

function getConversations() {
    $.ajax({
        url: 'conversation/',
        success: ({results}) => {
            for (const conversation of results) addNewConversation(conversation);
        },
    });
}

function addNewConversation(conversation) {
    $('#chats').prepend(`
        <a class="filterDiscussions all single ${conversation.unread_messages > 0 ? 'unread' : 'read'}"
         data-toggle="list" data-conversationId="${conversation.id}" role="tab"
         onclick="conversationOnClick(this)">
            <img class="avatar-md" src="${conversation.avatar}"
                 data-toggle="tooltip" data-placement="top" title="${conversation.title}" alt="avatar">
            ${conversation.unread_messages > 0 ?
        `<div class="new bg-primary"><span>${conversation.unread_messages}</span></div>` : ''}
                  
            <div class="data">
                <h5>${conversation.title}</h5>
                <p>${conversation.last_message}</p>
            </div>
            
        </a>
    `)
}

function getConversationInformation(conversationId) {
    $.ajax({
        url: `conversation/${conversationId}/`,
        success: (results) => {
            setupConversationPage(results);
        }
    });
}

function setupConversationPage(conversationInfo) {
    const conversationImg = $("#conversation-image");
    conversationImg.attr('src', conversationInfo.avatar);
    conversationImg.attr('title', conversationInfo.title);

    const conversationTitle = $("#conversation-title");
    conversationTitle.text(conversationInfo.title);
}

function getConversationMessage(conversionId) {
    $.ajax({
        url: `conversation/${conversionId}/get_messages/`,
        success: ({results}) => {
            const groupedMessage = groupMessageByDate(results);
            createArchiveMessage(groupedMessage);
        }
    })
}

function groupMessageByDate(messageList) {
    const result = {};

    for (const message of messageList) {
        const localDate = new Date(message.create_at).toLocaleDateString();
        if (!result[localDate])
            result[localDate] = [];

        result[localDate].push(message);
    }
    return result;
}

function createArchiveMessage(messageGroup, scrollToBottom = true) {
    const othersMessagesTemplate = `
    <div class="message">
        <img class="avatar-md" src="#AVATAR" data-toggle="tooltip" data-placement="top" title="Keith" alt="avatar">
        <div class="text-main">
            <div class="text-group">
                <div class="text">
                <p>#TEXT</p>
                </div>
            </div>
        <span>#EXTRA</span>
        </div>
    </div>`
    const dateTemplate = `<div class="date">
                                    <hr>
                                    <span>#DATE</span>
                                    <hr>
                                 </div>`;

    const messageContainer = $("#message-container");
    for (const [date, messages] of Object.entries(messageGroup)) {

        for (const message of messages) {
            const messageDate = new Date(message.create_at);
            messageContainer.prepend(
                othersMessagesTemplate
                    .replace("#AVATAR", message.sender.get_avatar)
                    .replace("#TEXT", message.text)
                    .replace('#EXTRA', `${message.sender.display_name} | ${messageDate.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    })}`)
            );
        }
        const currentDate = new Date();
        const groupDate = new Date(date);
        const timeDifference = Math.abs(currentDate - groupDate);
        const dayDifference = Math.floor(timeDifference / (1000 * 60 * 60 * 24));

        if (dayDifference === 0)
            messageContainer.prepend(dateTemplate.replace("#DATE", 'Today'));
        else if (dayDifference === 1)
            messageContainer.prepend(dateTemplate.replace("#DATE", 'Yesterday'));
        else
            messageContainer.prepend(dateTemplate.replace("#DATE", `${date}`));
    }

    if (scrollToBottom)
        $('#content').animate({scrollTop: $('#content').prop("scrollHeight")}, 500);
}