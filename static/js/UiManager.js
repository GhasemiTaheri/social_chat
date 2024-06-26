const initialState = {
    type: 'chat-inactive',
}
window.history.replaceState(initialState, '', '');
window.addEventListener("popstate", (event) => {
    if (event.state) {
        if (event.state.type === 'chat-inactive') {
            $('#list-chat').removeClass('active show');
            $('#list-empty').addClass('active show');
            $(".list-group a").removeClass("active");
        }
        if (event.state.type === 'chat-active') {
            $('#list-empty').removeClass('active show');
            $('#list-chat').addClass('active show');
        }

    }
});
document.addEventListener('keydown', (function (e) {
    if (e.key === "Escape" || e.key === "Esc")
        if (window.history.state.type === 'chat-active')
            window.history.back();
}));

$(".menu a i").on("click", function () {
    $(".menu a i").removeClass("active");
    $(this).addClass("active")
});

$(document).ready(function () {
    $(".filterDiscussions").not(".all").hide("3000");
    $(".filterDiscussionsBtn").click(function () {
        const t = $(this).attr("data-filter");
        $(".filterDiscussions").not("." + t).hide("3000");
        $(".filterDiscussions").filter("." + t).show("3000")
    });
    $("#conversations").on("keyup", function () {
        const t = $(this).val().toLowerCase();
        $("#chats a").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(t) > -1)
        })
    })

    $('[data-toggle="tooltip"]').tooltip();
});

function conversationOnClick(element) {
    const clickedElement = $(element);

    if (clickedElement.children('.new').length) {
        $.ajax({
            headers: {
                'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').attr('value'),
            },
            url: `conversation/${clickedElement.data('conversationid')}/read_message/`,
            method: 'post',
            success: () => {
                clickedElement.children('.new').remove();
            }
        })
    }

    const state = {
        type: 'chat-active',
        id: element.dataset.conversationid
    }
    if (window.history.state && window.history.state.type === 'chat-active')
        window.history.replaceState(state,
            '',
            '');
    else
        window.history.pushState(state,
            '',
            '');

    // In this section, we must dispatch popstate event manually, because by default this event is not dispatched
    // in the pushState and replaceState functions.
    window.dispatchEvent(new PopStateEvent('popstate', {state}));
}