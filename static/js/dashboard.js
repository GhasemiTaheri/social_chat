var _udata;
var socket;

$(document).ready(function () {
    _udata = JSON.parse(document.getElementById('uid').textContent);
    $(document).keydown(function (e) {
        if (e.key === "Escape" || e.key === "Esc") {
            $('.select-chat').removeClass('d-none');
            $('.select-chat').addClass('d-flex');
            $('.card').css('display', 'none');
            $('.chat').removeClass('active');
            $('#message_box_text').val('')
            socket.close();
            setup_base_screen_width(true)
        }
    });

    get_all_chat();

});


function get_all_chat() {
    fetch('/chat/get_all_chat')
        .then(response => response.json())
        .then(data => {
            for (let i in data) {
                add_chat_to_dashboard(data[i])
            }
        })
}

function add_chat_to_dashboard(d) {
    let chat_section = $('.chat_list');
    chat_section.append(`<div onclick="get_chat_message(this)" data-chatid="${d['unique_id']}" data-member="${d['member_count']}" class="row chat border-bottom py-1">
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
        .replace('#LASTMESSAGETIME#', d['last_message'] != null ? new Date(d['last_message']['create_at']).getHours() + ':' + new Date(d['last_message']['create_at']).getMinutes() : "")
        .replace("#LASTMESSAGETEXT#", d['last_message'] != null ? d['last_message']['text'] : "")
    );

}

function get_chat_message(chat) {
    setup_conversation(chat);

    $('.chat').removeClass('active');
    $(chat).addClass('active');
    const chat_id = chat.dataset ? chat.dataset.chatid : chat.unique_id;
    fetch(`get_chat_message/${chat_id}`)
        .then(response => response.json())
        .then(data => {
            add_chat_to_message_box(data)
        })

    if (socket) {
        socket.close()
    }
    socket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + chat_id + '/');
    socket.onmessage = function (e) {
        let message = JSON.parse(e.data);
        add_chat_to_message_box(message, true);
    };

}

$(window).resize(function () {
    setup_base_screen_width();
});

function setup_conversation(chat) {
    setup_base_screen_width(false, true);

    $('.select-chat').removeClass('d-flex');
    $('.select-chat').addClass('d-none');
    $('.card').css('display', 'flex');

    $('.all-message').html("");

    let chat_img;
    let chat_name;
    if ($(chat).children().length > 0) {
        chat_img = $(chat).children('.col-2').children().children('img').attr('src') !== undefined ? $(chat).children('.col-2').children().children('img').attr('src') : "";
        chat_name = $(chat).children('.col-10').children('.contact-name').children('h6').text();
    } else {
        chat_img = "/media/" + chat.avatar
        chat_name = chat.name
    }

    $('.conversation_name').text(chat_name);
    $('.member-count').text(chat.dataset ? chat.dataset.member + " member" : chat.member_count + " member")

    if (chat_img !== "")
        $('.conversation_img').html(`<img src="${chat_img}" alt="Image" class="img-fluid">`)
    else
        $('.conversation_img').html(`<div class="logo m-0"><span>${chat_name[0]}</span></div>`)

}

function add_chat_to_message_box(message_obj, new_msg = false) {
    for (let item in message_obj) {
        const message = message_obj[item];
        if (message.sender.id === _udata) {
            $('.all-message').append(`<li class="right-message">
                            <div class="text-wrapper">
                                <div>#MESSAGE#<br></div>
                                <div class="float-right"><small>#TIME#</small></div>
                            </div>
                        </li>`
                .replace('#MESSAGE#', message.text)
                .replace('#TIME#', new Date(message.create_at).toLocaleString()));
        } else {
            $('.all-message').append(`<li class="left-message">
                            <div class="custom-thumbnail float-left">#AVATAR#</div>
                            <div class="text-wrapper">
                                <div><small>#NAME#</small><br></div>
                                <div>#MESSAGE#<br></div>
                                <div class="float-right"><small>#TIME#</small></div>
                            </div>
                        </li>`
                .replace("#AVATAR#", message.sender.avatar !== "" ? `<img src="/media/${message.sender.avatar}">` : `<div class="logo m-0"><span>${message.sender.username[0]}</span></div>`)
                .replace('#NAME#', message.sender.first_name !== "" ? message.sender.first_name : message.sender.username)
                .replace('#MESSAGE#', message.text)
                .replace('#TIME#', new Date(message.create_at).toLocaleString()));

            if (new_msg) {
                var audio = new Audio('https://androidzoom.ir/wp-content/uploads/2018/05/FadeIn.mp3');
                audio.play();
            }
        }

        $('.active .contact-content p').text(message.text.substr(0, 15) + '...');

    }

    $('.msg_card_body').scrollTop($('.msg_card_body').prop("scrollHeight"));

}

function send_message() {
    const message_box = $('#message_box_text')
    if (message_box.val().trim() !== "") {
        socket.send(JSON.stringify({'text': message_box.val()}))
        message_box.val('')
    }
}

function setup_base_screen_width(back_btn = false, active_chat = false) {
    if (window.matchMedia('(max-width: 767px)').matches && !back_btn) {
        if ($('div.row .active').length >= 1 || active_chat) {
            $('.chat_list').addClass('d-none')
            $('.chat-content').removeClass('d-none')
            $('.sidebar').addClass('d-none')
            $('.site-section').css('padding-left', '0')
            $('#back-to-chat-list').removeClass('d-none')
        }
    } else {
        $('.chat_list').removeClass('d-none')
        $('.chat-content').addClass('d-none')
        $('.sidebar').removeClass('d-none')
        $('.site-section').css('padding-left', '4.4rem')
        $('#back-to-chat-list').addClass('d-none')
        $('.chat').removeClass('active');
    }
}