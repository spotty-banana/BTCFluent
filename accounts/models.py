from django.db import models
from django.db.models import Sum

from django.db.models import F, Q
from decimal import Decimal
from django.conf import settings
import coinaddrvalidator

class TxType(models.IntegerChoices):
    DEPOSIT = 1
    WITHDRAW = 2
    TRANSFER = 3
    INTERNAL_FEE = 4
    ERROR_REVERSAL = 5

class Asset(models.Model):
    """
    Description: Model Description
    """

    ticker = models.CharField(max_length=10, unique=True)
    atomic_unit = models.CharField(max_length=50)
    base_unit = models.CharField(max_length=50, default=None)

    description = models.TextField()

    # account where fees from transactions are credited
    blockchain_fee_account = models.ForeignKey('Account', on_delete=models.PROTECT, null=True, default=None, 
        related_name="fee_account_asset")

    custody_billing_account = models.ForeignKey('Account', on_delete=models.PROTECT, null=True, default=None, 
        related_name="custody_billing_account")

    # the fee for outgoing blockchain transactions
    outgoing_tx_fee_amount = models.DecimalField(max_digits=65, decimal_places=0, default=5000)

    #Blockheight for checking purposes  
    blockheight = models.IntegerField(default=702398)

    #boolean for securing singular execution of tracing
    scan_started_at = models.DateTimeField(default=None, null=True)

    def validate_address(self, address):
        validation_result = coinaddrvalidator.validate(self.ticker,address)
        return validation_result.valid


    def __str__(self):
        return str(self.id) + " " + self.ticker + " " + self.description

    class Meta:
        pass

# ID, Ticker, atomic unit, base unit, description
DEFAULT_ASSETS = (
    (1, 'BTC', 'sats', 'BTC', ''),
    (2, 'USD', 'cents', 'USD', ''),
    (3, 'EUR', 'cents', 'EUR', ''),
    (4, 'CHF', 'rappen', 'CHF', ''),
)

def asset_identifier(asset_id):
    for ass in DEFAULT_ASSETS:
        if asset_id == ass[0]:
            return ass[1]
    raise Exception("asset_id %d not found" % (asset_id,))

def asset_unit(asset_id):
    for ass in DEFAULT_ASSETS:
        if asset_id == ass[0]:
            return ass[2]
    raise Exception("asset_id %d not found" % (asset_id,))

class Transaction(models.Model):
    """
    Transaction between accounts
    """
    
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)

    from_account = models.ForeignKey('Account', null=True, default=None, related_name="from_transactions", on_delete=models.PROTECT)
    to_account = models.ForeignKey('Account', null=True, default=None, related_name="to_transactions", on_delete=models.PROTECT)

    # via smallest possible precision
    amount = models.DecimalField(max_digits=65, decimal_places=0, default=0)
    
    incomingtx = models.ForeignKey("IncomingTransaction", null=True, on_delete=models.PROTECT, 
        verbose_name="Related incoming transaction", related_name="related_transactions")

    #balances before tx
    from_balance_before_tx = models.DecimalField(max_digits=65, decimal_places=0, default=0)
    to_balance_before_tx = models.DecimalField(max_digits=65, decimal_places=0, default=0)

    tx_type = models.IntegerField(choices=TxType.choices)

    # if internal transaction via address lookup, add foreign key to the assetaddress
    to_internal_address = models.ForeignKey('AssetAddress', null=True, default=None, on_delete=models.PROTECT)

    def get_account_balance_after_tx(self, account):
        if self.to_account == account:
            return self.to_balance_before_tx + self.amount
        elif self.from_account == account:
            return self.from_balance_before_tx - self.amount
        else:
            raise Exception("Account_id %s not related to this transaction" % (account,))

    def __str__(self):
        desc = ""
        if self.from_account_id and self.to_account_id:
            if self.to_internal_address_id:
                desc = "Internal from %d to %d, through %s" % (self.from_account_id, self.to_account_id, self.to_internal_address.address)
            else:
                desc = "Internal from %d to %d" % (self.from_account_id, self.to_account_id)
        elif self.from_account_id:
            desc = "Withdraw from %d" % (self.from_account_id)
        elif self.to_account_id:
            desc = "Deposit to %d" % (self.to_account_id)

        return "%s: %s, %d %s %s" % (asset_identifier(self.asset_id), self.created_at, 
            self.amount, asset_unit(self.asset_id), desc)

    class Meta:
        pass

class AssetAddress(models.Model):

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    first_used_at = models.DateTimeField(null=True, default=None)
    expired_at = models.DateTimeField(null=True, default=None)

    received = models.DecimalField(max_digits=65, decimal_places=0, default=0)

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)

    address = models.CharField(default="", unique=True, max_length=128, db_index=True)

    account = models.ForeignKey('Account', null=True, default=None, on_delete=models.PROTECT)


    def __str__(self):
        return "%s: %s, atomic unit received: %s" % (asset_identifier(self.asset_id), self.address, self.received)


class IncomingTransaction(models.Model):
    """
    Incoming transaction
    """
    
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, default=None)

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)

    address = models.ForeignKey('AssetAddress', on_delete=models.PROTECT)

    # via smallest possible precision
    amount = models.DecimalField(max_digits=65, decimal_places=0, default=0)

    confirmations = models.IntegerField(default=0)

    # unique identifier for transaction, for example for bitcoin txid:vout
    tx_identifier = models.CharField(max_length=500, unique=True)

    # once transaction is credited to account, transaction object is created and this is set.
    transaction = models.ForeignKey('Transaction', null=True, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return "%s: %s %d %s To: %s..." % (asset_identifier(self.asset_id), self.tx_identifier, 
            self.amount, asset_unit(self.asset_id),
            self.address.address[:6])

    class Meta:
        pass


# Create your models here.

class Account(models.Model):
    """
    Account which has assets, transactions in and out and balance
    """
    
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    balance = models.DecimalField(max_digits=65, decimal_places=0, default=0)

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)

    def get_incoming_in_timeframe(self, from_date, to_date):
        return (Transaction.objects.filter(to_account=self, created_at__range=[from_date, to_date]).aggregate(Sum('amount'))['amount__sum'] or 0)

    def get_outcoming_in_timeframe(self, from_date, to_date):
        return (Transaction.objects.filter(from_account=self, created_at__range=[from_date, to_date]).aggregate(Sum('amount'))['amount__sum'] or 0)

    def get_balance_before_date(self, from_date):
        latest_tx_before_date = Transaction.objects.filter(Q(from_account = self, created_at__lt = from_date) | Q(to_account = self, created_at__lt = from_date)).last()
        #if there is no tx before this date return 0
        if not latest_tx_before_date == None:
            #if to_account is self, it must be incoming tx so add the amount to balance before tx, otherwise substract from balance before tx
            if latest_tx_before_date.to_account == self:
                return latest_tx_before_date.to_balance_before_tx + latest_tx_before_date.amount
            else:
                return latest_tx_before_date.from_balance_before_tx - latest_tx_before_date.amount
        else:
            return 0

    def get_txlist_data_in_timeframe(self, from_date, to_date):
        txlist = []

        #fetch all tramsactions related to this account in date range
        txs = Transaction.objects.filter(Q(to_account=self, created_at__range=[from_date, to_date]) | Q(from_account=self, created_at__range=[from_date, to_date])).order_by("created_at")

        for i in txs:
            txlist.append(i)

        return txlist

    def getbalance(self):
        return self.balance

    def getasset(self):
        return self.asset

    def calculate_total_balance(self):
        return (self.to_transactions.aggregate(Sum('amount'))['amount__sum'] or 0) - \
            (self.from_transactions.aggregate(Sum('amount'))['amount__sum'] or 0)

    def sendable_amount(self):
        return self.balance + self.asset.outgoing_tx_fee_amount

    def send_to_address(self, amount, to_address):
        if amount <= 0:
            raise Exception("Account %d wrong amount %d %s" %
                (self.id, amount, self.asset.unit))

        if self.balance < amount + self.asset.outgoing_tx_fee_amount:
            raise Exception("Account %d insufficient balance to send %d %s" %
                (self.id, amount, self.asset.unit))

        # Extra check that we aren't having wrong balance in database
        sendable_balance_db = self.calculate_total_balance()
        if self.balance != sendable_balance_db:
            raise Exception("Account %d balance mismatch, in cache %d, should be %d" %
                (self.id, self.balance, sendable_balance_db))

        if not self.asset.validate_address(to_address):
            raise Exception("Address not valid " + str(to_address))

        # Search if the address is already in our database and do transaction accordingly
        asset_address = AssetAddress.objects.filter(address=to_address, asset=self.asset).first()
        if asset_address:
            self.send_to_account(asset_address.account, amount, TxType.TRANSFER, asset_address)
            return

        #take the balance and fee out of the account
        from_balance_before_tx = self.balance
        new_balance = self.balance - amount
        rows_updated = Account.objects.filter(id=self.id, balance=from_balance_before_tx).update(balance=new_balance)

        if rows_updated == 1:
            self.balance = new_balance
            tx = Transaction.objects.create(
                asset=self.asset,
                from_account=self,
                to_account=None,
                amount=amount,
                tx_type=TxType.WITHDRAW,
                from_balance_before_tx=from_balance_before_tx
                )

            Outgoingtransaction.objects.create(
                from_account=self,
                to_address=to_address,
                transaction=tx,
                amount=amount,
                asset=self.asset,
                transaction_base64=None)



            # after that, generate the fee transaction

            fee_account = self.asset.blockchain_fee_account

            after_fee_balance = self.balance - self.asset.outgoing_tx_fee_amount
            rows_updated = Account.objects.filter(id=self.id, balance=self.balance).update(balance=after_fee_balance)
            if rows_updated == 1:
                self.balance = after_fee_balance

                # Create fee transaction
                fee_tx = Transaction.objects.create(
                    asset=self.asset,
                    from_account=self,
                    to_account=fee_account,
                    amount=self.asset.outgoing_tx_fee_amount,
                    tx_type=TxType.INTERNAL_FEE,
                    from_balance_before_tx=self.balance,
                    to_balance_before_tx=fee_account.balance
                    )


            else:
                #raise exception in case rows didnt update
                raise ("Account %d balance not updated" % (self.id))



            
            rows_updated_2 = Account.objects.filter(id=fee_account.id, 
                balance=fee_account.balance).update(balance=F('balance') + self.asset.outgoing_tx_fee_amount)
            fee_account.balance = fee_account.balance + self.asset.outgoing_tx_fee_amount
            if rows_updated_2 != 1:
                raise Exception(" %s feeaccount balance not updated" % (self.asset.ticker))
                

            return tx

        else:
            raise Exception(" %d feeaccount balance not updated" % (self.asset.ticker))

    def send_to_account(self, other_account, amount, txtype, internal_address=None):
        if other_account.asset_id != self.asset_id:
            raise Exception("Mismatching assets")
        if amount <= 0:
            raise Exception("Can't send negative amount")
        if amount > self.balance:
            raise Exception("not enough balance")
        sendable_balance = self.calculate_total_balance()
        if amount > sendable_balance:
            raise Exception("not enough balance")

        new_balance = self.balance - amount
        rows_updated = Account.objects.filter(id=self.id, balance=self.balance).update(balance=new_balance)
        if rows_updated == 1:
            self.balance = new_balance
            tx = Transaction.objects.create(asset=self.asset, from_account=self, to_account=other_account,
                                            amount=amount, tx_type=txtype, from_balance_before_tx=new_balance + amount,
                                            to_balance_before_tx=other_account.balance)
            if internal_address:
                tx.to_internal_address = internal_address
                tx.save()
            rows_updated_2 = Account.objects.filter(id=other_account.id).update(balance=F('balance') + amount)
            if rows_updated_2 < 1:
                # TODO: log this error somewhere
                pass

        elif rows_updated > 1:
            raise Exception("multiple rows were updated")
        elif rows_updated < 1:
            raise Exception("no rows updated")

    def get_new_address(self):
        address = AssetAddress.objects.filter(asset=self.asset, account=None, incomingtransaction=None).order_by('created_at').first()
        if AssetAddress.objects.filter(asset=self.asset, account=None, incomingtransaction=None).count() < 1:
            # TODO: maybe generate new addresses on fly?
            raise Exception("No free addresses")
        rows_updated = AssetAddress.objects.filter(id=address.id, account=None).update(account_id=self.id)
        if rows_updated == 1:
            return address

    def get_unused_address(self):
        address = AssetAddress.objects.filter(asset_id=self.asset, account_id=self.id, incomingtransaction=None, first_used_at=None).order_by('created_at').first()
        if not address:
            return self.get_new_address()
        return address

    def __str__(self):
        return "%s Account %d, balance %d" % (asset_identifier(self.asset_id), self.id, self.balance)

    class Meta:
        pass

class Outgoingtransaction(models.Model):
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    broadcasted_at = models.DateTimeField(null=True, default=None)

    canceled_at = models.DateTimeField(null=True, default=None)

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)

    from_account = models.ForeignKey(Account, on_delete=models.PROTECT)

    to_address = models.TextField(null=True, default=None)


    # via smallest possible precision
    amount = models.DecimalField(max_digits=65, decimal_places=0, default=0)

    # Transaction in base64 format
    transaction_base64 = models.TextField(null=True, default=None)

    # transaction id after broadcasted
    txid = models.TextField(null=True, default=None)

    # transaction object is created before any action
    transaction = models.ForeignKey(Transaction, null=True, default=None, on_delete=models.PROTECT)

    class Meta:
        pass

    def __str__(self):
        return ("To address:" + self.to_address + ", Amount:" + str(self.amount) + " Created at : " +  str(self.created_at)) + " id: " + str(self.id)







