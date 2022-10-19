from django.test import TestCase
from django.utils import timezone

from .models import Account, Asset, Transaction, TxType, AssetAddress


class AccountModelTests(TestCase):

    def test_calculate_total_balance_smoke(self):
        btc = Asset.objects.filter(ticker="BTC").first()
        account1 = Account(id=1, created_at=timezone.now(), balance=10, asset=btc)
        account2 = Account(id=2, created_at=timezone.now(), balance=20, asset=btc)
        account1.save()
        account2.save()
        Transaction.objects.create(created_at=timezone.now(), asset=btc,
                                   from_account=account1, to_account=account2,
                                   amount=56, tx_type=TxType.TRANSFER)
        self.assertEqual(account2.calculate_total_balance(), 56)

    def test_send_to_address_in_database(self):
        btc = Asset.objects.filter(ticker="BTC").first()
        account1 = Account.objects.create(id=1, created_at=timezone.now(), balance=10000, asset=btc)
        account2 = Account.objects.create(id=2, created_at=timezone.now(), balance=10000, asset=btc)
        account3 = Account.objects.create(id=3, created_at=timezone.now(), balance=10000, asset=btc)
        Transaction.objects.create(created_at=timezone.now(), asset=btc,
                                   from_account=account3, to_account=account1,
                                   amount=10000, tx_type=TxType.TRANSFER)
        addr = "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3"
        AssetAddress.objects.create(created_at=timezone.now(), asset=btc, address=addr, account=account2)
        account1.send_to_address(1000, addr)
        account1 = Account.objects.filter(id=1).first()
        account2 = Account.objects.filter(id=2).first()
        self.assertEqual(account1.balance, 9000)
        self.assertEqual(account2.balance, 11000)

