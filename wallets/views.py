from django.shortcuts import render
from django.http import HttpResponse
import hashlib
import os
import base64
from wallets.models import WalletUser
from accounts.models import Account, Asset
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
    generated_password = base64.urlsafe_b64encode(os.urandom(16)).replace(b'=', b'')
    generated_username = b"satoshi-" + base64.urlsafe_b64encode(os.urandom(5)).replace(b'=', b'')
    btc_account = Account.objects.create(asset=Asset.objects.get(id=1, ticker="BTC"))
    new_user = WalletUser.objects.create_user(username=generated_username, 
        password=generated_password, btc_account=btc_account)
    new_user.save()

    user = authenticate(username=new_user.username, password=generated_password)

    messages.add_message(request, messages.INFO, 'Username %s Password %s' % (new_user.username, generated_password))

    return redirect("/")
