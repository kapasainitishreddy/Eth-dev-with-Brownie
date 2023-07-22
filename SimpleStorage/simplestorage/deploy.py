from solcx import compile_standard
import json
from web3 import Web3

import os
#compile_standard is a function that takes in a dictionary of solidity code and compiles it
with open('./SimpleStorage.sol','r') as file:
    simple_storage_file = file.read()


#compiling solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}}, #this is a dictionary of the solidity code
        "settings": {
            "outputSelection": {
                "*": { # * means all the contracts
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] #this is the information we want to get back
                } #abi is the application binary interface which is a json representation of the smart contract
                #metadata is the metadata of the smart contract and bytecode is the bytecode of the smart contract and sourceMap is the sourceMap of the smart contract
                #metadata means the compiler version and the compiler settings
                #bytecode is the actual code that is deployed to the blockchain
                #sourceMap is the mapping between the solidity code and the bytecode
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file) #dumping the compiled_sol into the file


#get bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
#the above code walks through json to get the bytecode
#get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
#the above code walks through json to get the abi

#to deploy we use ganache which is a local blockchain that we can use to deploy our smart contract

#for connecting to ganache we use web3
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545")) #this is the url of ganache
chain_id = 1337 #this is the chain id of ganache
my_address = "0xC5BB589e5dA40A08186e63c73C98C0f59F4Db6b2"
private_key = "0x3e"


SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode) #this is the contract object
#w3.eth.contract is a function that takes in abi and bytecode and returns a contract object that we can use to deploy our smart contract

#transactions --> 1) build a transaction 2) sign a transaction 3) send a transaction
#nonce is the number of transactions sent from a given address to the network and it is used to prevent double spending which means spending the same money twice
#we can get the nonce by using w3.eth.getTransactionCount(my_address)

nonce = w3.eth.getTransactionCount(my_address) #this is the number of transactions sent from my_address to the network

#1) build a transaction
transaction = SimpleStorage.constructor().buildTransaction({"chainId":chain_id,"from":my_address,"nonce":nonce}) 

#2) sign a transaction
signed_txn = w3.eth.account.sign_transaction(transaction,private_key=private_key)

#3) send a transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction) #this is the transaction hash

#wait for the transaction to be mined
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash) #this is the transaction receipt
#waiting for the transaction to be mined means waiting for the transaction to be added to a block
#we need the transaction receipt to get the contract address
#the transaction receipt is a dictionary that contains the contract address eg: tx_receipt.contractAddress

#working with the contract
#1) contract address
#2) contract abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress,abi=abi) #this is the contract object
#we can use the contract object to interact with the smart contract

print(simple_storage.functions.retrieve().call()) #this is the initial value of the smart contract
#we can use the call() function to call a function of the smart contract and do not change the state of the smart contract
#just like blue button in remix
#we can use the transact() function to send a transaction to the smart contract and change the state of the smart contract
#just like orange button in remix
#state change means changing the value of the smart contract

store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId":chain_id,"from":my_address,"nonce":nonce+1
    })
#to build transaction we use the buildTransaction() function
#we can use the buildTransaction() function to build a transaction to send to the smart contract
signed_store_txn = w3.eth.account.sign_transaction(store_transaction,private_key=private_key)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)














