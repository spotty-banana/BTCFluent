from django.shortcuts import render
from django.http import HttpResponse
import hashlib
import os
import base64
from wallets.models import WalletUser
from accounts.models import Account
from django.shortcuts import redirect, render
from django.urls import reverse


def index(request):
    if request.user.is_authenticated:
        user = WalletUser.objects.get(username=request.user.username)

        return render(request, 'wallet.html', {
                'user': user
            })

    return render(request, 'nonlogged_index.html')


def create(request):
    generated_password = base64.b32encode(os.urandom(16))
    new_user = WalletUser.objects.create_user(username="u" + base64.b32encode(os.urandom(8)), password=generated_password)
    new_user.btc_account = Account.objects.create(asset=Asset.objects.get(id=1, ticker="BTC"))
    new_user.save()

    user = authenticate(username=new_user.username, password=generated_password)

    messages.add_message(request, messages.INFO, 'Username %s Password %s' % (new_user.username, generated_password))

    return redirect("/")
