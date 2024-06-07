$(document).ready(() => {
    // new conversation modal
    const newChatModal = $("#startnewchat");

    const searchSelect = $('#search-group-input');
    searchSelect.select2({
        dropdownParent: newChatModal,
        width: 'resolve',
        placeholder: 'Search for conversation...',
        ajax: {
            url: 'conversation/search/',
            delay: 250,
            data: (params) => {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            }
        },
        templateResult: (state) => {
            if (state.id)
                return $(`<div data-conversationId="${state.id}">
                        <img class="avatar-sm mr-2" src="${state.avatar}" alt="avatar">
                        <span>${state.title}</span>
                    </div>`)

            return state.text
        }
    });
    searchSelect.on('select2:select', function (e) {
        const csrf_token = $('[name="csrfmiddlewaretoken"]').attr('value');

        if (confirm("Do you want to join this group?"))
            $.ajax({
                headers: {
                    'X-CSRFToken': csrf_token,
                },
                url: `conversation/${e.params.data.id}/join/`,
                method: 'post',
                success: () => {
                    alert('welcome')
                },
                error: () => {
                    alert('problem')
                }
            })

        searchSelect.val(null).trigger('change');
    });

    // group member select
    const groupMemberSelect = $('#group-member-select');
    groupMemberSelect.select2({
        dropdownParent: newChatModal,
        width: 'resolve',
        placeholder: 'Search for people...',
        ajax: {
            url: `${window.location.protocol}//${window.location.host}/profile/user/search/`,
            delay: 250,
            data: (params) => {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            }
        },
        templateResult: (state) => {
            if (state.id)
                return $(`<span data-userId="${state.id}">
                        <img class="avatar-sm mr-2" src="${state.get_avatar}" alt="avatar">
                        <span>${state.display_name}</span>
                    </span>`)
            return state.text
        },
        templateSelection: (state) => {
            if (state.id !== '')
                return $(`<span data-userId="${state.id}">
                    <img class="avatar-sm mr-2" src="${state.get_avatar}" alt="avatar">
                    <span>${state.display_name}</span>
                </span>`)

            return state.text
        }
    });

    // new friend select
    const newFriendSelect = $('#new-friend-select');
    newFriendSelect.select2({
        dropdownParent: newChatModal,
        width: 'resolve',
        placeholder: 'Search for people...',
        ajax: {
            url: `${window.location.protocol}//${window.location.host}/profile/user/search/`,
            delay: 250,
            data: (params) => {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            }
        },
        templateResult: (state) => {
            if (state.id)
                return $(`<span data-userId="${state.id}">
                        <img class="avatar-sm mr-2" src="${state.get_avatar}" alt="avatar">
                        <span>${state.display_name}</span>
                    </span>`)
            return state.text
        },
        templateSelection: (state) => {
            if (state.id !== '')
                return $(`<span data-userId="${state.id}">
                    <img class="avatar-sm mr-2" src="${state.get_avatar}" alt="avatar">
                    <span>${state.display_name}</span>
                </span>`)

            return state.text
        }
    });
    newFriendSelect.on('select2:select', function (e) {
        const csrf_token = $('[name="csrfmiddlewaretoken"]').attr('value');

        if (confirm("Do you want to start a conversation with this person?"))
            $.ajax({
                headers: {
                    'X-CSRFToken': csrf_token,
                },
                url: `conversation/`,
                method: 'post',
                data: {
                    conversation_type: 'si',
                    members: e.params.data.id
                },
                success: () => {
                    alert('welcome')
                },
                error: (e) => {
                    console.log(e)
                }
            })

        newFriendSelect.val(null).trigger('change');
    })
})