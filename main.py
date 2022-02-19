from web3 import Web3
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

print("GAS PRICE:", w3.eth.generate_gas_price())