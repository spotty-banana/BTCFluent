import requests
import pprint

# first look how to set up rpc here: https://electrum.readthedocs.io/en/latest/jsonrpc.html

pp = pprint.PrettyPrinter(indent=4)

wallet_path = "~/electrum_wallet.dat"

electrum_rpc_url = "http://user:password==@127.0.0.1:7777"

scanned_to_height = 694019

def electrum_command(command, params):
    # Example echo method
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": command,
        "params": params,    
    }
    response = requests.post(electrum_rpc_url, json=payload)
    response_json = response.json()

    pp.pprint(response)

serialized_zx = "xxx"

electrum_command("load_wallet", {"wallet_path": wallet_path})
electrum_command("getbalance", {"wallet": wallet_path})
electrum_command("onchain_history", {"wallet": wallet_path})

electrum_command("onchain_history", {"wallet": wallet_path, "from_height": scanned_to_height})
electrum_command("gettransaction", ["zzz"])
electrum_command("deserialize", [serialized_zx])


electrum_command("getunusedaddress", {"wallet": wallet_path})

electrum_command("getunusedaddress", {"wallet": wallet_path})


"""
electrum commands: 
"addrequest",
"addtransaction",
"broadcast",
"clearrequests",
"commands",
"create",
"createmultisig",
"createnewaddress",
"decrypt",
"deserialize",
"dumpprivkeys",
"encrypt",
"freeze",
"getaddressbalance",
"getaddresshistory",
"getaddressunspent",
"getalias",
"getbalance",
"getconfig",
"getfeerate",
"getmasterprivate",
"getmerkle",
"getmpk",
"getprivatekeys",
"getpubkeys",
"getrequest",
"getseed",
"getservers",
"gettransaction",
"getunusedaddress",
"help",
"history",
"importprivkey",
"is_synchronized",
"ismine",
"listaddresses",
"listcontacts",
"listrequests",
"listunspent",
"make_seed",
"notify",
"password",
"payto",
"paytomany",
"restore",
"rmrequest",
"searchcontacts",
"serialize",
"setconfig",
"setlabel",
"signmessage",
"signrequest",
"signtransaction",
"sweep",
"unfreeze",
"validateaddress",
"verifymessage",
"version"
"""
