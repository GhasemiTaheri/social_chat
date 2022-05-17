document.addEventListener("DOMContentLoaded", function () {
    get_all_chat();
});

function get_all_chat() {
    fetch('/chat/get_all_chat')
        .then(response => response.json())
        .then(data => {
            for (let i in data) {
                console.log(data[i])
                add_chat_to_dashboard(data[i])
            }
        })
}

function add_chat_to_dashboard(d) {
    let chat_section = $('.chat_list');
    chat_section.append(`<div onclick="get_chat_message(this)" data-chatid="${d['unique_id']}" class="row chat border-bottom py-1">
                        <div class="col-2 px-1 h-100">
                            <div class="custom-thumbnail">
                                #AVATAR#
                            </div>
                        </div>
                        <div class="col-10 py-1 h-100">
                            <div class="contact-name">
                                <h6 style="display: inline;">#CHATNAME#</h6>
                                <small class="last-message-date"
                                       style="float: right;">#LASTMESSAGETIME#</small>
                            </div>
                            <div class="contact-content">
                                <p>#LASTMESSAGETEXT#</p>
                            </div>
                        </div>
                    </div>`
        .replace('#AVATAR#', d['avatar'] !== "" ? `<img src="/media/${d['avatar']}" alt="Image" class="img-fluid">` : `<div class="logo m-0"><span>${d['name'][0]}</span></div>`)
        .replace('#CHATNAME#', d['name'])
        .replace('#LASTMESSAGETIME#', d['last_message'] != null ? d['last_message']['create_at'] : "")
        .replace("#LASTMESSAGETEXT#", d['last_message'] != null ? d['last_message']['text'] : "")
    );

}

function get_chat_message(chat) {

    alert(chat.dataset.chatid)
    console.log(chat)
}