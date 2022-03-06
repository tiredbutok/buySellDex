import time
import sys

# For coloring of terminal output
from colorama import init
from colorama import Fore, Back, Style
init()

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
from config import *

# Text styling
yelloBright = Fore.YELLOW + Style.BRIGHT
cyanBright = Fore.CYAN + Style.BRIGHT
blueBright = Fore.BLUE + Style.BRIGHT
greenBright = Fore.GREEN + Style.BRIGHT
redBright = Fore.RED + Style.BRIGHT
resetStyle = Style.RESET_ALL

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


    # Check if provided address is a valid address
    if not w3.isAddress(SENDER_ADDRESS):
        print(redBright + "*==================* !!! WRONG WALLET ADDRESS !!! *==================*")
        sys.exit(1)
    
    balance = w3.eth.get_balance(SENDER_ADDRESS)
    readable_balance = w3.fromWei(balance, 'ether')
    print(greenBright, "BALANCE:", str(readable_balance), resetStyle, "\n")

    # Set amount of native token for txn
    amountInMessage = f"{blueBright}Amount of {native_token_symbol} in: {resetStyle}"
    amountInInput = input(amountInMessage)
    amountInWei = w3.toWei(amountInInput, 'ether')

    # Set slippage
    slippage = setSlippage()

    # Get contract address of token we want to buy 
    token_to_buy_input = input("Enter TokenAddress: ")
    while(not w3.isAddress(token_to_buy_input)): 
        print(Fore.RED + Style.BRIGHT + "WRONG CONTRACT ADDRESS, PLEASE TRY AGAIN" + resetStyle)
        token_to_buy_input = input("Enter TokenAddress: ")
    token_to_buy = w3.toChecksumAddress(token_to_buy_input)
   
    # Transaction count
    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

    # Get transaction
    transaction = createTransaction(w3, token_to_buy, amountInWei, slippage, nonce, chain)
    
    # Get gasLimit and gasPrice in array
    gas_result = changeGasPrice(transaction, amountInWei, w3)
    
    # Build transaction
    readyTransaction = transaction.buildTransaction({
        "from": SENDER_ADDRESS,
        "value": amountInWei,
        "gas": gas_result[0],
        "gasPrice": gas_result[1],
        "nonce": nonce
    })

    # print(readyTransaction)
    # Sign transaction
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
        print(f"{yelloBright}<chain_symbol>{resetStyle}: bsc, ftm, avax")
        print("-------------------------------")
        sys.exit(1)
    print(f"{redBright}PICKED CHAIN:{resetStyle} {chainSymbol}")
    native_token_symbol = chain["NATIVE_TOKEN_SYMBOL"]
    return chain

def createTransaction(w3, token_to_buy, amountInWei, slippage, nonce, chain):
    """Returns tx for pancakeswap"""
    native_token_ca = w3.toChecksumAddress(chain["WRAPPED_NATIVE_TOKEN_CA"])
    contract = w3.eth.contract(address=chain["ROUTER_CA"], abi=chain["ROUTER_CA_ABI"])
    
    loop = True
    while loop:
        # Rn have no other idea how to listen for liquidity added event
        time.sleep(0.25)
        try:
            amountOutMin = calculateMinAmountOfTokens(slippage, contract, w3, native_token_ca, token_to_buy, amountInWei)
            loop = False
        except:
            print("Waiting for liquidity.")
    
    # Set dedline to 25 minutes
    deadline = int(time.time()) + 1500

    # Seems to be okay but im not sure if it's the best way to find gasLimit and gasPrice
    txn = contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        # Amount Out Min
        amountOutMin,
        # Path,
        [native_token_ca, token_to_buy],
        # To
        SENDER_ADDRESS,
        # Deadline
        deadline
    )
    
    return txn
    
    
def changeGasPrice(txn, amountInWei, w3):
    """Dispaly user current gasPrice and gasLimit and ask if they want to pay approximate fees"""
    # Get gasLimit
    gasLimit = txn.estimateGas({'value': amountInWei})
    print("\n|===|GAS LIMIT:", blueBright, gasLimit, resetStyle)
    
    # Get gasPrice using rpc_gas_price_strategy
    gasPrice = w3.eth.generate_gas_price()
    print("|===|GAS PRICE:", blueBright, w3.fromWei(gasPrice, 'gwei'), "Gwei", resetStyle)
    
    askForGasPrice = 'n'
    while askForGasPrice != 'y':
        print("\n|=============|")
        # Show approximate fees using current gasPrice
        print("|===|Approximate fees:", redBright, w3.fromWei(gasLimit*gasPrice, 'ether'), resetStyle, native_token_symbol)

        # Ask if user wants to use this gasPrice considering approximate fees
        askForGasPrice = input("|===|Accept gas price?(y/n): ").lower()

        # If user doesn't agree prompt them for appropriate gasPrice
        if askForGasPrice == "n":
            gasPrice = input("|===|YOUR GAS PRICE (gwei): ")
            gasPrice = w3.toWei(gasPrice, 'gwei')

    return [gasLimit, gasPrice]
        

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
    
def calculateMinAmountOfTokens(slippage, contract, w3, native_token_ca, token_to_buy, amountInWei):
    
    # Figure out amount of tokens
    amountsOut = contract.functions.getAmountsOut(amountInWei, [native_token_ca, token_to_buy]).call()
    amountOfTokenOutEther = w3.fromWei(amountsOut[1], 'ether')

    amountOutMin = int(amountsOut[1] - (amountsOut[1] * slippage))

    print(f"{blueBright}Amount of tokens out: {resetStyle}{amountOfTokenOutEther}")
    print(f"{redBright}Amount of tokens out min: {resetStyle}{w3.fromWei(amountOutMin, 'ether')}")

    return amountOutMin

# print("GAS PRICE:", w3.eth.generate_gas_price())
# print(os.environ['PRIVETE_KEY'])

if __name__ == '__main__':
    main()