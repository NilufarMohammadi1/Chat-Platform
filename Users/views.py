from django.contrib.auth.hashers import check_password
from django.shortcuts import render

from Chats.models import Thread, ThreadMember
from .forms import RegistrationForm
from Users.models import Users
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import login, authenticate


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            nickname = form.cleaned_data['nickname']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = Users.objects.create_user(nickname=nickname, username=username, password=password)
            user.save()
            main_thread = ThreadMember.objects.create(
                thread=Thread.objects.get(id=1),
                user=user,
                is_grp_admin=False
            )
            main_thread.save()
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/messages/')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }

    return render(request, 'register.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = Users.objects.get(username=username)
            if check_password(password, user.password):
                login(request, user)
                if 'next' in request.GET:
                    return redirect(request.GET.get('next'))
                return redirect('/messages/')
            else:
                messages.error(request, "invalid username or password.")
        except Users.DoesNotExist:
            print("error")

    return render(request, 'login.html')



def logout_user(request):
    logout(request)
    return redirect('login')