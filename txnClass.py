class Txn:
    def __init__(self, chain, web3, amountInWei, contract, token_to_buy, native_token_ca):
        self.chain = chain
        self.web3 = web3
        self.amountInWei = amountInWei
        self.contract = contract
        self.txnBody = {}
        
        self.data = {}
        self._gasLimit = txn.estimateGas({'value': amountWeiIn})
        self._gasPrice = web3.eth.generate_gas_price()

    def __str__ ():
        return f"{chain}{data}"

    @property
    def gasPrice(self):
        return self.gasPrice
    
    @gasPrice.getter
    def gasPrice(self):
        return self._gasPrice
    
    @gasPrice.setter
    def gasPrice(self, newGasPrice):
        self._gasPrice = newGasPrice