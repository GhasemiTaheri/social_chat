// submit user update form
$('#user_update_form').on('submit', function (e) {
    e.preventDefault();
    const csrf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    const data = new FormData();

    // validation data
    const formData = new FormData(this);
    if (formData.get('password') !== formData.get('password2')) {
        alert('Passwords are not the same!');
        return;
    }
    for (const fd of formData.entries()) {
        if (fd[0] === 'avatar' && fd[1].name !== '')
            data.append(fd[0], fd[1])

        if (['first_name', 'last_name', 'email', 'password', 'password2'].indexOf(fd[0]) > -1 && fd[1] !== '')
            data.append(fd[0], fd[1])
    }

    $.ajax({
        headers: {
            'X-CSRFToken': csrf_token,
        },
        url: '/profile/user-update/',
        method: "PATCH",
        contentType: false,
        processData: false,
        data: data,
        timeout: 10000, // 10 sec
        success: (e) => {
            alert('your account update successfully!')
        },
        error: ({responseJSON}) => {
            alert(Object.values(responseJSON).join('\r\n'));
        }
    });
});

// delete account
$('#collapseSeven').on('click', (e) => {
    const csrf_token = $('[name="csrfmiddlewaretoken"]').attr('value');

    if (confirm('Would you like to delete your account?\r\nWith this, your information will no longer be accessible.') === true) {
        $.ajax({
            headers: {
                'X-CSRFToken': csrf_token,
            },
            url: '/profile/user-update/',
            method: 'delete',
            success: () => {
                window.location.reload();
            },
            error: (e) => {
                console.log(e)
            }
        });
    } else
        console.log('No')
});