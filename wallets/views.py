from django.shortcuts import render
from django.http import HttpResponse
import hashlib
import os
import base64
from wallets.models import WalletUser
from accounts.models import Account, Asset
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages


def index(request):
    if request.user.is_authenticated:
        user = WalletUser.objects.get(username=request.user.username)

        return render(request, 'wallet.html', {
                'user': user
            })

    return render(request, 'nonlogged_index.html')


def create(request):
    generated_password = base64.urlsafe_b64encode(os.urandom(16)).replace(b'=', b'')
    generated_username = b"satoshi-" + base64.urlsafe_b64encode(os.urandom(5)).replace(b'=', b'')
    new_user = WalletUser.objects.create_user(username=generated_username, 
        password=generated_password)
    new_user.save()

    user = authenticate(username=new_user.username, password=generated_password)
    if user is not None:
        login(request, user)

        messages.add_message(request, messages.INFO, 'Username %s Password %s' % (new_user.username, generated_password))

        return redirect("/")

    return HttpResponse("Failed to create wallet")
