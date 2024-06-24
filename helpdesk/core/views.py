from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.user.is_staff:
        message = "Welcome Staff"
    else:
        message = "Welcome"

    return render(request, 'home.html', {'username': request.user.username, 'message': message})