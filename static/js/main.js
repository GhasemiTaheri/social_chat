let userId = null;
window.addEventListener('popstate', (event) => {
    if (event.state.type === 'chat-active') {
        $('#message-container').empty();
        getConversationInformation(event.state.id);
        getConversationMessage(event.state.id);
    }
});
window.addEventListener('SocketEvent', (event) => {
    const payload = event.detail;
    if ('event_type' in payload) {
        if (payload.event_type === 'new_message') {
            // reorder chat list section
            $(`[data-conversationId="${payload.data.conversation}"]`).prependTo("#chats");
            $(`[data-conversationId="${payload.data.conversation} p"]`).text(payload.data.text.slice(0, 15));
            if (window.history.state.id === payload.data.conversation) {
                addMessageToConversation(payload.data);
                return
            }
            const unreadMessageCounter = $(`[data-conversationId="${payload.data.conversation}"] .new span`);
            if (unreadMessageCounter)
                unreadMessageCounter.text(parseInt(unreadMessageCounter.text()) + 1)
            else
                $(`[data-conversationId="${payload.data.conversation}"] img`)
                    .after('<div class="new bg-primary"><span>1</span></div>')


        } else if (payload.event_type === 'conversation_add') {
            addNewConversation(payload.data);
        }
    }

});

$(document).ready(() => {
    getConversations();
    userId = window.sessionStorage.getItem('user-id');
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
        success: (conversationInfo) => {
            const conversationImg = $("#conversation-image");
            conversationImg.attr('src', conversationInfo.avatar);
            conversationImg.attr('title', conversationInfo.title);

            let information = `<h5><a href="#">${conversationInfo.title}</a></h5>`;
            if (conversationInfo.conversation_type === 'gr')
                information = information + `<span>${conversationInfo.member_count} members</span>`
            $('#conversation-data').html(information);
        }
    });
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
    const messageContainer = $("#message-container");
    const dateTemplate = `<div class="date">
                                    <hr>
                                    <span>#DATE</span>
                                    <hr>
                                 </div>`;

    for (const [date, messages] of Object.entries(messageGroup)) {

        for (const message of messages)
            addMessageToConversation(message, true);

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

function addMessageToConversation(message, prepend = false) {

    const messageContainer = $("#message-container");
    const messageDate = new Date(message.create_at);

    const othersMessagesTemplate = `<div class="message">
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
        .replace("#AVATAR", message.sender.get_avatar)
        .replace('#TITLE', message.sender.display_name)
        .replace("#TEXT", message.text)
        .replace('#EXTRA', `${message.sender.display_name} | ${messageDate.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        })}`);

    const myMessageTemplate =
        `<div class="message me">
                <div class="text-main">
                    <div class="text-group me">
                        <div class="text me">
                            <p>#TEXT</p>
                        </div>
                    </div>
                    <span>#EXTRA</span>
                </div>
          </div>`.replace('#TEXT', message.text)
            .replace('#EXTRA', `${messageDate.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            })}`)

    let finalMessage = null;

    if (String(message.sender.id) === String(userId))
        finalMessage = myMessageTemplate;
    else
        finalMessage = othersMessagesTemplate;

    if (prepend)
        messageContainer.prepend(finalMessage);
    else
        messageContainer.append(finalMessage);

}