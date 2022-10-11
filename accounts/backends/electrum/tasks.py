import os
import asyncio
import sys

import requests
import pprint
import datetime
from django.conf import settings
import json
from celery import shared_task


# first look how to set up rpc here: https://electrum.readthedocs.io/en/latest/jsonrpc.html

pp = pprint.PrettyPrinter(indent=4)


#TODO: move paths and urls to settings
wallet_path = settings.ELECTRUM_WALLET_PATH
electrum_rpc_url = settings.ELECTRUM_RPC_URL



def electrum_command(command, params):
    # Example echo method
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": command,
        "params": params,
    }   
    response = requests.post(electrum_rpc_url, json=payload).json()
    output = pp.pprint(response)
    return response["result"]



@shared_task
def electrum_refill_address_queue():
    from accounts.models import AssetAddress, Asset
    # TODO: move daemon connection string to settings!
    # try to keep always 1000 address objects ready
    addresses_needed = 50
    free_address_count = AssetAddress.objects.filter(account=None).count()
    for i in range(free_address_count, addresses_needed):
        address_string = electrum_command("createnewaddress", {"wallet": wallet_path})
        print(address_string)

        # TODO: validate address, raise Exception if daemon returrns something that is not excepted
        # TODO: Add address to the database and validate address.
        if Asset.objects.get(id=1, ticker="BTC").validate_address(address_string):
            AssetAddress.objects.create(address=address_string, account=None, asset_id=1)
        else:
            raise Exception



def refill_address_queue():
    # fetch new addresses here from the daemon
    electrum_refill_address_queue()




@shared_task
def electrum_check_incoming_txs():
    from accounts.models import Account, Asset, AssetAddress, IncomingTransaction, Transaction, TxType

    old_blockcheight = Asset.objects.get(ticker="BTC").blockheight


    recent_transactions = electrum_command("onchain_history", {"wallet": wallet_path, "from_height": old_blockcheight - 5})["transactions"]
    
    for tx in recent_transactions:
        tx_id = tx["txid"]
        serialized_tx = electrum_command("gettransaction", [tx_id])
        txinfo = electrum_command("deserialize", [serialized_tx])["outputs"]
        vout = 0
        new_blockheight = max(tx["height"], old_blockcheight)

        for i in txinfo:

            satoshi_amount = i["value_sats"]
            #Electrum doesnt output vout in onchain_history 
            TXidentifier = str(tx_id) + ":" + str(vout)
            txaddress = i["address"]

            # first look if Assetaddress is in our addresslist
            if AssetAddress.objects.filter(address=txaddress, account__isnull=False).exists() == True:
                incoming_address = AssetAddress.objects.get(address=txaddress)

                # try to look for incoming transaction, if not found create one
                incoming_txs = IncomingTransaction.objects.filter(tx_identifier = TXidentifier)
                if incoming_txs.count() < 1:
                    inc_tx = IncomingTransaction.objects.create(asset_id=1, 
                        address=incoming_address, 
                        amount=satoshi_amount, 
                        confirmations=tx["confirmations"], 
                        tx_identifier=TXidentifier,
                        transaction=None,
                        )
                else:
                    inc_tx = incoming_txs.first()

                # and finally, if incoming transaction has enough confirmations credit it to the account

                if tx["confirmations"]>=2 and inc_tx.transaction == None and inc_tx.confirmed_at == None:



                    # get relevan address and account object.
                    accountid = incoming_address.account_id

                    account = Account.objects.get(id = accountid)

                    #check database integrity for account
                    if account.balance != account.calculate_total_balance():
                        raise Exception("Balance mismatch, Account %d" % (account.id))

                    # First, mark the incoming transaction as confirmed to avoid double spend. Also adds confirmations. Atomic update.
                    rows_updated_2 = IncomingTransaction.objects.filter(id=inc_tx.id, tx_identifier=TXidentifier, 
                        confirmed_at=None).update(confirmed_at=datetime.datetime.now(), confirmations=tx["confirmations"])
                    if rows_updated_2 < 1:
                        raise Exception("Problem initiating tx, IncomingTransaction %d" % (inc_tx.id))


                    #add incoming address
                    IncomingTransaction.objects.filter(id=inc_tx.id, tx_identifier=TXidentifier, address=None).update(address=incoming_address)
                    old_balance = account.balance 
                    new_balance = account.balance + satoshi_amount

                    rows_updated = Account.objects.filter(id = accountid, balance=account.balance).update(balance=new_balance)
                    #check if this transaction is already done
                    if rows_updated == 1:

                        txcreate = Transaction.objects.create(
                            asset=Asset.objects.get(id=1),
                            from_account=None,
                            to_account=account,
                            incomingtx=inc_tx,
                            amount=satoshi_amount, 
                            tx_type=TxType.DEPOSIT, 
                            to_balance_before_tx=old_balance
                            )

                        rows_updated_2 = IncomingTransaction.objects.filter(tx_identifier=TXidentifier, 
                            transaction=None).update(transaction=txcreate)

                        if rows_updated_2 < 1:
                            raise Exception("Concurrency, IncomingTransaction %d update" % (inc_tx.id))


                    else:
                        print("error")
                else:
                    print("AssetAddress doesnt exist or account is null")
            else:
                print("Not our address")
                #not in our addressbook
            vout += 1
    Asset.objects.filter(ticker="BTC").update(blockheight=new_blockheight)

@shared_task
def electrum_process_outgoing_transactions():
    from accounts.models import Outgoingtransaction, Transaction, Asset
    from decimal import Decimal

    #lista jossa kaikki kyseisen assetin ulospäinmenevät transaktiot joilla ei ole vielä transaktiota.
    txorders = Outgoingtransaction.objects.filter(asset=Asset.objects.get(ticker="BTC"),
        transaction_base64=None)

    for tx in txorders:

        #convert satoshis to BTC
        BTC_amount = str(Decimal(tx.amount) / Decimal(10**8))

        #get base64 tx string from electrum
        transaction_base64 = electrum_command("payto",{"wallet": wallet_path, "amount":BTC_amount, "destination": tx.to_address, "unsigned": "true"})

        #update Outgoingtransaction base64
        Outgoingtransaction.objects.filter(id=tx.id, transaction_base64=None).update(transaction_base64=transaction_base64)


@shared_task
def electrum_process_fees():
    from accounts.models import Outgoingtransaction, Transaction, Asset
    from decimal import Decimal

    recent_transactions = electrum_command("onchain_history", {"wallet": wallet_path, "from_height": scanned_to_height})["transactions"]
    
    for tx in recent_transactions:
        tx_id = tx["txid"]
        serialized_tx = electrum_command("gettransaction", [tx_id])
        txinfo = electrum_command("deserialize", [serialized_tx])["outputs"]
        for i in txinfo:
            txaddress = i["address"]
            if Outgoingtransaction.objects.filter(to_address=txaddress).exists() == True:
                outgoing_transaction = Outgoingtransaction.objects.get(to_address=txaddress)

                if tx["incoming"] == "false" and outgoing_transaction.fees_processed == False and tx["confirmations"] > 0:

                    #Take actual fees out of feeaccount balance
                    fee_old_balance = Asset.objects.get(ticker="BTC").fee_account.balance
                    rows_updated = Account.objects.filter(asset=Asset.objects.get(ticker="BTC"), is_fee_account=True, balance = fee_old_balance).update(balance = old_balance - tx["fee_sat"])

                    if rows_updated == 1:
                        outgoing_transaction.fees_processed = False
                        outgoing_transaction.save()
                    else:
                        #alert admin
                        pass
                else:
                    return "not incoming or already processed or not enough confirmations"
            else:
                return "no Outgoingtransaction found"
            

def check_incoming_transactions():
    # fetch new addresses here from the daemon
    electrum_check_incoming_txs()

















