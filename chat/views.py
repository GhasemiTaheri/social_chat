import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from chat.forms import GroupCreate
from chat.models import Group, Message


@login_required
def dashboard(request):
    return render(request, 'chat/dashborad.html', {
        'profile': request.user,
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
                             f'Group Create successfully, send your invite link to your friends '
                             f'"http://127.0.0.1:8000/chat/{group_obj.unique_id}"')
        else:
            messages.error(request, "Name or image size may be has problem, please change it", extra_tags='danger')

        return redirect(reverse('chat:create_group'))
    else:
        create_group_form = GroupCreate()
    return render(request, 'chat/create_group.html', {
        'profile': request.user,
        'group_form': create_group_form
    })


@csrf_exempt
def get_all_chat(request):
    all_chat = Group.objects.filter(owner_id=request.user.id)
    all_chat |= request.user.group_member.all()
    return JsonResponse([chats.serializer() for chats in all_chat], safe=False)


def get_chat_message(request, chat_id):
    all_message = Message.objects.filter(to_group__unique_id=chat_id).order_by('create_at')
    return JsonResponse([message.serializer() for message in all_message], safe=False)


@csrf_exempt
def find_chat_room(request):
    if request.method == 'POST':
        term = request.POST.get('search')
        if term:
            filtered_group = Group.objects.filter(name__contains=term)
            res = JsonResponse({'results': [group.serializer() for group in filtered_group]}, safe=False)
            return res

    return JsonResponse(json.dumps('Nothing'), safe=False)
