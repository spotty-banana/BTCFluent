from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from accounts.models import Account, Outgoingtransaction, Transaction, Asset
from django.forms import ModelForm
from datetime import datetime

# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, username, password=None):
        if not username:
            raise ValueError("You need an username")
        user= self.model(
            username=username,
            btc_account = Account.objects.create(asset=Asset.objects.get(id=1, ticker="BTC"))
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError("You need an email")
        if not username:
            raise ValueError("You need an username")
        user= self.create_user(
            email=email,
            username=username,
            password=password,
            )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_keyholder = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class WalletUser(AbstractBaseUser):
    """
    An individual user. Username and password are required. Other fields are optional.
    """

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)

    username = models.CharField(max_length=50, unique=True)

    btc_account = models.ForeignKey(Account, on_delete=models.PROTECT,)

    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        pass