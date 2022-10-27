from django.test import TestCase
from django.utils import timezone

from wallets.models import WalletUser
from .models import Account, Transaction, TxType, AssetAddress


class AccountModelTests(TestCase):

    def test_send_to_address_in_database(self):
        user1 = WalletUser.objects.create_user(username="user1", password="pass")
        user2 = WalletUser.objects.create_user(username="user2", password="pass")
        Transaction.objects.create(created_at=timezone.now(), asset=user1.btc_account.asset,
                                   to_account=user1.btc_account, amount=10000, tx_type=TxType.DEPOSIT)
        user1.btc_account.balance = 10000
        user1.btc_account.save()

        addr_str = "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3"
        addr = AssetAddress.objects.create(created_at=timezone.now(), asset=user2.btc_account.asset, address=addr_str,
                                           account=user2.btc_account)

        user1.btc_account.send_to_address(1000, addr_str)

        account1 = Account.objects.get(id=user1.btc_account.id)
        account2 = Account.objects.get(id=user2.btc_account.id)
        self.assertEqual(account1.balance, 9000)
        self.assertEqual(account2.balance, 1000)

        tx = Transaction.objects.get(amount=1000)
        self.assertEqual(tx.asset, account1.asset)
        self.assertEqual(tx.from_account, account1)
        self.assertEqual(tx.to_account, account2)
        self.assertEqual(tx.tx_type, TxType.TRANSFER)
        self.assertEqual(tx.from_balance_before_tx, 10000)
        self.assertEqual(tx.to_balance_before_tx, 0)
        self.assertEqual(tx.to_internal_address, addr)

    def test_send_to_account_smoke(self):
        user1 = WalletUser.objects.create_user(username="user1", password="pass")
        user2 = WalletUser.objects.create_user(username="user2", password="pass")
        Transaction.objects.create(created_at=timezone.now(), asset=user1.btc_account.asset,
                                   to_account=user1.btc_account, amount=10000, tx_type=TxType.DEPOSIT)
        user1.btc_account.balance = 10000
        user1.btc_account.save()

        user1.btc_account.send_to_account(user2.btc_account, 1000, TxType.TRANSFER)

        account1 = Account.objects.get(id=user1.btc_account.id)
        account2 = Account.objects.get(id=user2.btc_account.id)
        self.assertEqual(account1.balance, 9000)
        self.assertEqual(account2.balance, 1000)

        tx = Transaction.objects.get(amount=1000)
        self.assertEqual(tx.asset, account1.asset)
        self.assertEqual(tx.from_account, account1)
        self.assertEqual(tx.to_account, account2)
        self.assertEqual(tx.tx_type, TxType.TRANSFER)
        self.assertEqual(tx.from_balance_before_tx, 10000)
        self.assertEqual(tx.to_balance_before_tx, 0)
        self.assertEqual(tx.to_internal_address, None)
