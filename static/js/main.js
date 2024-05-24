$(document).ready(() => {
    getConversations();
})

function getConversations() {
    $.ajax({
        url: 'conversation/', success: ({results}) => {
            for (const conversation of results) addNewConversation(conversation);
        },
    });
}

function addNewConversation(conversation) {
    $('#chats').prepend(`
        <a class="filterDiscussions all single ${conversation.unread_messages > 0 ? 'unread' : 'read'}"
         data-toggle="list" data-conversationId="${conversation.id}" role="tab">
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