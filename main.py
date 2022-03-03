import time

#For coloring of terminal output
from colorama import init
from colorama import Fore, Back, Style
init()

#For loading env variables
import os
from dotenv import load_dotenv

load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
SENDER_ADDRESS = os.getenv('SENDER_ADDRESS')

#For web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from config import *

blueBright = Fore.BLUE + Style.BRIGHT
greenBright = Fore.GREEN + Style.BRIGHT
redBright = Fore.RED + Style.BRIGHT
resetStyle = Style.RESET_ALL

def main():
    w3 = pickChainAndSetProvider()
    w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
    # w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    if w3.isConnected():
        print(greenBright, "\n|IS CONNECTED|:", 'True', resetStyle)
    else:
        print(redBright, "\n|IS CONNECTED|:", 'Fales', resetStyle)
        return 1


    # Check if provided address is a valid address
    if not w3.isAddress(SENDER_ADDRESS):
        print(redBright + "*==================* @ WRONG WALLET ADDRESS @ *==================*")
        return 1
    
    balance = w3.eth.get_balance(SENDER_ADDRESS)
    readable_balance = w3.fromWei(balance, 'ether')
    print(greenBright, "BALANCE:", str(readable_balance), resetStyle, "\n")

    # Set amount of BNB for txn
    amountInMessage = f"{blueBright}Amount of BNB in: {resetStyle}"
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
    transaction = pancakeswapCreateTransaction(w3, token_to_buy, amountInWei, slippage)


def pickChainAndSetProvider():
    """Returns web3 provider based on provided chain"""

    web3 = Web3(Web3.HTTPProvider(BSC["RPC"]))
    return web3

def pancakeswapCreateTransaction(w3, token_to_buy, amountInWei, slippage):
    """Returns tx for pancakeswap"""
    wbnb_ca = w3.toChecksumAddress(BSC["WRAPPED_NATIVE_TOKEN_CA"])
    contract = w3.eth.contract(address=BSC["ROUTER_CA"], abi=BSC["ROUTER_CA_ABI"])
    
    amountOutMin = calculateMinAmountOfTokens(slippage, contract, w3, wbnb_ca, token_to_buy, amountInWei)
    
    # Set dedline to 25 minutes
    deadline = int(time.time()) + 1500

    # Seems to be okay but im not usre if it's the best way to find gasLimit and gasPrice
    gasLimit = contract.functions.swapExactETHForTokens(
        # Amount Out Min
        amountOutMin,
        # Path,
        [wbnb_ca, token_to_buy],
        # To
        SENDER_ADDRESS,
        # Deadline
        deadline
    ).estimateGas({'value': amountInWei})
    print("GAS LIMIT:", gasLimit)
    # .buildTransaction({
    #     'from': SENDER_ADDRESS,
    #     'value': w3.toWei(amountInInput, 'ether'),
    gasPrice = w3.fromWei(w3.eth.generate_gas_price(), 'gwei')
    # })
    # console.log(pcs_txn)
    # return pcs_txn


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
    
def calculateMinAmountOfTokens(slippage, contract, w3, wbnb_ca, token_to_buy, amountInWei):
    
    # Figure out amount of tokens
    amountsOut = contract.functions.getAmountsOut(amountInWei, [wbnb_ca, token_to_buy]).call()
    amountOfTokenOutEther = w3.fromWei(amountsOut[1], 'ether')

    amountOutMin = int(amountsOut[1] - (amountsOut[1] * slippage))

    print(f"{blueBright}Amount of tokens out: {resetStyle}{amountOfTokenOutEther}")
    print(f"{redBright}Amount of tokens out min: {resetStyle}{w3.fromWei(amountOutMin, 'ether')}")

    return amountOutMin

# print("GAS PRICE:", w3.eth.generate_gas_price())
# print(os.environ['PRIVETE_KEY'])

main()