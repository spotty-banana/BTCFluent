from django.test import TestCase
from django.utils import timezone

from wallets.models import WalletUser
from .models import Account, Transaction, TxType, AssetAddress


class AccountModelTests(TestCase):

    def test_calculate_total_balance_smoke(self):
        user1 = WalletUser.objects.create_user(username="user1", password="pass")
        user2 = WalletUser.objects.create_user(username="user2", password="pass")
        Transaction.objects.create(created_at=timezone.now(), asset=user1.btc_account.asset,
                                   from_account=user1.btc_account, to_account=user2.btc_account,
                                   amount=56, tx_type=TxType.TRANSFER)
        self.assertEqual(user2.btc_account.calculate_total_balance(), 56)

    # def test_send_to_address_in_database_transaction_fields(self):
    #     # btc = Asset.objects.filter(ticker="BTC").first()
    #     # account1 = Account.objects.create(id=1, created_at=timezone.now(), balance=10000, asset=btc)
    #     # account2 = Account.objects.create(id=2, created_at=timezone.now(), balance=10000, asset=btc)
    #     # account3 = Account.objects.create(id=3, created_at=timezone.now(), balance=10000, asset=btc)
    #     # Transaction.objects.create(created_at=timezone.now(), asset=btc,
    #     #                            from_account=account3, to_account=account1,
    #     #                            amount=10000, tx_type=TxType.TRANSFER)
    #     user1 = WalletUser.objects.create_user(username="user1", password="pass")
    #     user2 = WalletUser.objects.create_user(username="user2", password="pass")
    #     Transaction.objects.create(created_at=timezone.now(), asset=user1.btc_account.asset,
    #                                to_account=user1.btc_account, amount=10000, tx_type=TxType.DEPOSIT)
    #     user1.btc_account.balance = 10000
    #     addr = "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3"
    #     AssetAddress.objects.create(created_at=timezone.now(), asset=user2.btc_account.asset, address=addr,
    #                                 account=user2.btc_account)
    #     user1.btc_account.send_to_address(1000, addr)
    #     # account1 = Account.objects.filter(id=1).first()
    #     # account2 = Account.objects.filter(id=2).first()
    #     # self.assertEqual(user1.btc_account.balance, 9000)
    #     # self.assertEqual(user2.btc_account.balance, 1000)
    #     print("start")
    #     for t in Transaction.objects.all():
    #         print(t)
    #     print("end")
    #
    #     # tx = Transaction.objects.get(amount=1000)
    #     # self.assertEqual(tx.asset, user1.btc_account.asset)

    def test_send_to_account_smoke(self):
        user1 = WalletUser.objects.create_user(username="user1", password="pass")
        user2 = WalletUser.objects.create_user(username="user2", password="pass")
        Transaction.objects.create(created_at=timezone.now(), asset=user1.btc_account.asset,
                                   to_account=user1.btc_account, amount=10000, tx_type=TxType.DEPOSIT)
        user1.btc_account.balance = 10000
        user1.btc_account.send_to_account(user2.btc_account, 1000, TxType.TRANSFER)




