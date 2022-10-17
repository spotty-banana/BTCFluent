import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Account, Asset, Transaction, TxType


class AccountModelTests(TestCase):

    def test_calculate_total_balance_smoke(self):
        btc = Asset(ticker="BTC", atomic_unit="satoshi", base_unit="bitcoin")
        btc.save()
        account1 = Account(id=1, created_at=timezone.now(), balance=10, asset=btc)
        account2 = Account(id=2, created_at=timezone.now(), balance=20, asset=btc)
        account1.save()
        account2.save()
        Transaction.objects.create(created_at=timezone.now(), asset=btc,
                                   from_account=account1, to_account=account2,
                                   amount=56, tx_type=TxType.TRANSFER)
        self.assertEqual(account2.calculate_total_balance(), 56)
