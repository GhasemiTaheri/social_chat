from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from chat.forms import GroupCreate


@login_required
def dashboard(request):
    return render(request, 'chat/dashborad.html', {
        'profile': request.user
    })


@login_required
def create_group(request):
    if request.method == "POST":
        create_group_form = GroupCreate(request.POST, request.FILES)
        if create_group_form.is_valid():
            group_obj = create_group_form.save(commit=False)
            group_obj.owner = request.user
            group_obj.save()
            messages.success(request,
                             f'Group Create successfully, send your invite link to your friends "http://127.0.0.1:8000/chat/{group_obj.unique_id}"')
        else:
            messages.error(request, "Name or image size may be has problem, please change it", extra_tags='danger')

        return redirect(reverse('chat:create_group'))
    else:
        create_group_form = GroupCreate()
    return render(request, 'chat/create_group.html', {
        'profile': request.user,
        'group_form': create_group_form
    })
