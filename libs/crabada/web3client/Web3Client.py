import json
from web3 import Web3

class Web3Client:
    """Interact with a smart contract.
    
    Simple wrapper of the Web3 library."""

    contractAddress: str = None
    contractChecksumAddress: str = None
    abi: dict = None # contract's ABI, loaded from abi.json
    nodeUri: str = None # your node's URI
    w3: object = None # provider Web3, see https://web3py.readthedocs.io/en/stable/providers.html
    contract: object = None # the contract instance, see https://web3py.readthedocs.io/en/stable/examples.html#interacting-with-existing-contracts
    userAddress: str = None
    privateKey: str = None
    chainId: int = None

    ####################
    # Tx
    ####################

    def buildSignedTransaction(self, to: str, valueInEth: int, gas: int, gasPriceInGwei: int):
        """Send a simple transaction using the provided private key.
        
        This will send the blockchain token (e.g. ETH) to the given address:
            - valueInEth is expressed in the blockchain token (e.g. ETH).
            - gas is expressed as a unit
            - gasPriceInGwei is expressed in gwei

        Requires both credentials (setCredentials) and chain ID (setChainId)

        Sources:
         - https://web3py.readthedocs.io/en/stable/web3.eth.account.html#sign-a-contract-transaction
         - https://cryptomarketpool.com/send-a-transaction-to-the-ethereum-blockchain-using-python-and-web3-py/"""
        tx = {
            'chainId': self.chainId,
            'nonce': self.getTransactionCount(),
            'to': Web3.toChecksumAddress(to),
            'value': self.w3.toWei(valueInEth, 'ether'),
            'gas': gas,
            'gasPrice': self.w3.toWei(gasPriceInGwei, 'gwei')
        }
        signedTx = self.w3.eth.account.sign_transaction(tx, self.privateKey)
        return signedTx

    def sendSignedTransaction(self, signedTx: object):
        """Send a signed transaction and return the tx hash"""
        tx_hash = self.w3.eth.sendRawTransaction(signedTx.rawTransaction)
        return self.w3.toHex(tx_hash)

    def getTransactionCount(self):
        return self.w3.eth.get_transaction_count(self.userAddress)

    def getNonce(self):
        return self.getTransactionCount()

    ####################
    # Setters
    ####################

    def setContractAddress(self, contractAddress: str):
        self.contractAddress = contractAddress
        self.contractChecksumAddress = Web3.toChecksumAddress(contractAddress)
        return self

    def setNodeUri(self, nodeUri: str):
        self.nodeUri = nodeUri
        return self

    def setCredentials(self, userAddress: str, privateKey: str):
        self.userAddress = userAddress
        self.privateKey = privateKey
        return self

    def setAbi(self, fileName: str):
        """Read the contract's ABI from a JSON file"""
        self.abi = self.__loadAbi(fileName)
        return self

    def setChainId(self, chainId: int):
        self.chainId = int(chainId)
        return self

    def init(self):
        """Makes the contract ready to be used by the client.
        
        Run only after:
        - setting the node URI (setNodeUri)
        - set the contract's address (setContractAddress)
        - set the contract's ABI (setAbi)."""
        self.w3 = Web3(Web3.HTTPProvider(self.nodeUri))
        self.contract = self.w3.eth.contract(address=self.contractChecksumAddress, abi=self.abi)
        return self

    ####################
    # Private
    ####################

    def __loadAbi(self, fileName: str):
        with open(fileName) as file:
            return json.load(file)