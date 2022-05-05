from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

@login_required
def index(request):
    return render(request, 'shared/base.html', {
        'profile': request.user
    })
