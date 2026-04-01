import secrets

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.contrib.auth.forms import AuthenticationForm
from wallets.forms import WalletRegistrationForm
from wallets.models import WalletUser


def index(request):
    if request.user.is_authenticated:
        user = WalletUser.objects.get(username=request.user.username)

        return render(request, 'wallet.html', {
            'user': user
        })

    if request.method == 'POST':
        authentication_form = AuthenticationForm(request=request, data=request.POST)
        if authentication_form.is_valid():
            username = authentication_form.cleaned_data.get('username')
            password = authentication_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}")
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        authentication_form = AuthenticationForm()


    return render(request, 'nonlogged_index.html', {
        'authentication_form': authentication_form
    })


def create(request):
    if request.method == 'POST':
        form = WalletRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            user = authenticate(username=new_user.username, password=form.cleaned_data["password1"])
            if user is not None:
                login(request, user)
                messages.success(request, "Wallet created. You are now logged in.")
                return redirect("/")
            messages.error(request, "Registration succeeded but automatic login failed.")
            return redirect("/")
    else:
        form = WalletRegistrationForm()

    return render(request, 'register.html', {'form': form})


def create_auto(request):
    generated_password = secrets.token_urlsafe(16)
    generated_username = "satoshi-" + secrets.token_urlsafe(5)
    new_user = WalletUser.objects.create_user(
        username=generated_username,
        password=generated_password
    )
    new_user.save()

    user = authenticate(username=new_user.username, password=generated_password)
    if user is not None:
        login(request, user)
        messages.add_message(
            request,
            messages.INFO,
            'Username %s Password %s' % (new_user.username, generated_password)
        )
        return redirect("/")

    return HttpResponse("Failed to create wallet")
