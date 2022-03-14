import time
from terminalTextStyling import *

class Txn:
    def __init__(self, chain, w3, amountInWei, contract, token_to_buy,
            native_token_ca,slippage, sender_address, fastGasPrice=None):
            
        self.chain = chain
        self.w3 = w3
        self.amountInWei = amountInWei
        self.contract = contract
        self.token_to_buy = token_to_buy
        self.native_token_ca = native_token_ca
        self.slippage = slippage
        self.sender_address = sender_address
        self.fastGasPrice = fastGasPrice
        
        self.txn = None
        self.createTransaction()
        while True:
            time.sleep(0.15)
            try:
                self._gasLimit = self.txn.estimateGas({'value': self.amountInWei})
                break
            except:
                # ContractLogicError
                print(f"{yelloBright}|Trying to get _gasLimit|{resetStyle}")
        # Get gasPrice (using rpc_gas_price_strategy)
        self._gasPrice = self.w3.eth.generate_gas_price()
        self.setUpGasPrice()

    def __str__ (self):
        return f"TxnObject: {self.chain['name']}, token_to_buy:{self.token_to_buy}, \
            sender_address:{self.sender_address}"

    def createTransaction(self):
        """Creates transaction"""
        while True:
            # Rn have no idea how to listen for liquidity added event usint web3 py
            time.sleep(0.25)
            try:
                amountOutMin = self.calculateMinAmountOfTokens()
                break
            except:
                a = time.strftime("%H:%M:%S", time.localtime())
                print(f"{a} Waiting for liquidity.")
        
        # Set dedline to 25 minutes
        deadline = int(time.time()) + 1500
    
        self.txn = self.contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
            # Amount Out Min
            amountOutMin,
            # Path,
            [self.native_token_ca, self.token_to_buy],
            # To
            self.sender_address,
            # Deadline
            deadline
        )

    def calculateMinAmountOfTokens(self): 
        """Returns minimum amount of tokens to get from swap"""   
        # Figure out amount of tokens
        amountsOut = self.contract.functions.getAmountsOut(self.amountInWei, [self.native_token_ca, self.token_to_buy]).call()
            
        amountOfTokenOutEther = self.w3.fromWei(amountsOut[1], 'ether')
        amountOutMin = int(amountsOut[1] - (amountsOut[1] * self.slippage))

        print(f"{blueBright}Amount of tokens out: {resetStyle}{amountOfTokenOutEther}")
        print(f"{redBright}Amount of tokens out min: {resetStyle}{self.w3.fromWei(amountOutMin, 'ether')}")

        return amountOutMin

    def setUpGasPrice(self):
        """Dispaly to user current gasPrice and gasLimit and ask if they want to pay approximate fees"""

        print("\n|===|GAS LIMIT:", blueBright, self._gasLimit, resetStyle)

        if self.fastGasPrice:
            self._gasPrice = self.fastGasPrice
            print("|===|Approximate fees:", redBright, self.w3.fromWei(self._gasLimit*self._gasPrice, 'ether'),
                resetStyle, self.chain['NATIVE_TOKEN_SYMBOL'])
            return None

        print("|===|GAS PRICE:", blueBright, self.w3.fromWei(self._gasPrice, 'gwei'), "Gwei", resetStyle)
        
        askForGasPrice = 'n'
        while askForGasPrice != 'y':
            print("\n|=============|")
            # Show approximate fees using current gasPrice
            print("|===|Approximate fees:", redBright, self.w3.fromWei(self._gasLimit*self._gasPrice, 'ether'),
                resetStyle, self.chain['NATIVE_TOKEN_SYMBOL'])

            # Ask if user wants to use this gasPrice considering approximate fees
            askForGasPrice = input("|===|Accept gas price?(y/n): ").lower()

            # If user doesn't agree prompt them for appropriate gasPrice
            if askForGasPrice == "n":
                gasPriceUser = input("\n|===|YOUR GAS PRICE (gwei): ")
                self._gasPrice = self.w3.toWei(gasPriceUser, 'gwei')