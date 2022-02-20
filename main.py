import os
from dotenv import load_dotenv

load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import *

def main():
    w3 = Web3(Web3.HTTPProvider(BSC_RPC))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print("IS CONNECTED:", w3.isConnected())


panc0x10ED43C718714eb63d5aA57B78B54704E256024E

# print("GAS PRICE:", w3.eth.generate_gas_price())
# print(os.environ['PRIVETE_KEY'])

main()