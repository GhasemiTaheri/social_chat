export class ConversationManagement {
    #elementId = '';
    conversationList = []

    constructor(elementId) {
        this.#elementId = elementId;
    }

    getAllConversation() {
        fetch('/chat/conversation/')
            .then(response => response.json())
            .then(({results}) => {
                console.log(results);
            });
    }
}