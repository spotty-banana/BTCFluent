from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from accounts.models import Account, Outgoingtransaction, Transaction
from django.forms import ModelForm
from datetime import datetime

# Create your models here.

class WalletUser(AbstractBaseUser):
    """
    An individual signing in to the system. Might be customer, an employee or both
    """

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)

    username = models.CharField(max_length=50, unique=True)

    btc_account = models.ForeignKey(Account, on_delete=models.PROTECT,)

    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = ["username"]

    class Meta:
        pass