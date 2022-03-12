import time
import sys

# For creating txn object
from txnClass import Txn

# For coloring of terminal output
from terminalTextStyling import *

# For loading env variables
import os
from dotenv import load_dotenv

load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
SENDER_ADDRESS = os.getenv('SENDER_ADDRESS')

# For web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from config import chains

native_token_symbol = ''

def main():        
    # Get chain info
    chain = pickChain()
    
    # Setup web3
    w3 = Web3(Web3.HTTPProvider(chain["RPC"]))
    w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)

    if w3.isConnected():
        print(greenBright, "\n|IS CONNECTED|:", 'True', resetStyle)
    else:
        print(redBright, "\n|IS CONNECTED|:", 'Fales', resetStyle)
        sys.exit(1)

    # Contract - dex router
    contract = w3.eth.contract(address=chain["ROUTER_CA"], abi=chain["ROUTER_CA_ABI"])
    native_token_ca = w3.toChecksumAddress(chain["WRAPPED_NATIVE_TOKEN_CA"])

    # Check if user wants to use -f (fast) option
    # It allows to define gasPrice at the beginning making process faster
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    fastGasPrice = None
    if "-f" in opts:
        fastGasPrice = input("|===|YOUR GAS PRICE (gwei): ")
        fastGasPrice = w3.toWei(fastGasPrice, 'gwei')

    # Check if provided address is a valid address
    if not w3.isAddress(SENDER_ADDRESS):
        print(redBright + "*==================* !!! WRONG WALLET ADDRESS !!! *==================*")
        sys.exit(1)
    
    # Native token Balance
    balance = w3.eth.get_balance(SENDER_ADDRESS)
    readable_balance = w3.fromWei(balance, 'ether')
    print(greenBright, "BALANCE:", str(readable_balance), resetStyle, chain['NATIVE_TOKEN_SYMBOL'],"\n")

    # Set amount of native token for txn
    amountInMessage = f"{blueBright}Amount of {native_token_symbol} in: {resetStyle}"
    amountInInput = input(amountInMessage)
    amountInWei = w3.toWei(amountInInput, 'ether')

    # Set slippage
    slippage = setSlippage()

    # Get contract address of token we want to buy 
    token_to_buy_input = input("Enter TokenAddress: ")
    while(not w3.isAddress(token_to_buy_input)): 
        print(redBright + "WRONG CONTRACT ADDRESS, PLEASE TRY AGAIN" + resetStyle)
        token_to_buy_input = input("Enter TokenAddress: ")
    token_to_buy = w3.toChecksumAddress(token_to_buy_input)
   
    # Transaction count
    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

    # Create txn object:
    txn_object = Txn(
        chain, w3, amountInWei, contract, token_to_buy,
        native_token_ca, slippage, SENDER_ADDRESS, fastGasPrice
    )
    
    # Build transaction
    readyTransaction = txn_object.txn.buildTransaction({
        "from": SENDER_ADDRESS,
        "value": txn_object.amountInWei,
        "gas": txn_object._gasLimit,
        "gasPrice": txn_object._gasPrice,
        "nonce": nonce
    })

    # # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(readyTransaction, private_key=PRIVATE_KEY)
    txn_send = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_hash = w3.toHex(txn_send)
    print(f"{chain['SCAN_URL']}{tx_hash}")


def pickChain():
    """Return chain object that consists of NATIVE_TOKEN_SYMBOL, WRAPPED_NATIVE_TOKEN_CA, RPC etc."""
    global native_token_symbol
    try:
        chainSymbol = sys.argv[1].lower()
        chain = chains[chainSymbol]
    except (IndexError, KeyError) as e:
        print("ERROR:")
        print(f"{cyanBright}{' ':6}|=====|Usage|=====|{resetStyle}")
        print("-------------------------------")
        print(f"python3 main.py {yelloBright}<chain_symbol>{resetStyle}")
        print(f"{yelloBright}<chain_symbol>{resetStyle}: bsc, ftm, ropsten")
        print("-------------------------------")
        sys.exit(1)
    print(f"{redBright}PICKED CHAIN:{resetStyle} {chainSymbol}")
    native_token_symbol = chain["NATIVE_TOKEN_SYMBOL"]
    return chain
        
def setSlippage():
    """Set slippage"""
    slippageMessage = f"{blueBright}Set slippage between 0.01 - 1: {resetStyle}"
    slippageInput = float(input(slippageMessage))
    if slippageInput < 0.01:
        slippageInput = 0.01
    elif slippageInput > 1:
        slippageInput = 1
    print(f"{redBright}\n|=========| Slippage set to {slippageInput*100}%! |=========|{resetStyle}\n")
    return slippageInput
    
if __name__ == '__main__':
    main()