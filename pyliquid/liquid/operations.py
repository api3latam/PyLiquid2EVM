"""
Core components that represent objects inside Liquid node like a Wallet.
"""
from uuid import uuid4
from typing import Optional, Callable, Union

from bitcoinrpc.authproxy import AuthServiceProxy  # type: ignore
from mnemonic import Mnemonic  # type: ignore
from pyliquid.liquid.wrappers import rpc_exec


class Wallet():
    """
    Object representation for a unique wallet on the node.

    Attributes
    --------
    _proxy: AuthServiceProxy
        Authenticated Proxy Service to be used by the classmethods.
    _wallet: Dict
        Resulting metadata of the wallet at the node level.
    """

    _proxy: AuthServiceProxy
    _wallet: dict

    def __init__(self, proxy_service: AuthServiceProxy,
                 mode: Optional[str] = 'r',
                 wallet_label: Optional[str] = None,
                 with_address: bool = True) -> None:
        """
        Constructor for Wallet class.

        Parameters
        ---------
        proxy: AuthServiceProxy
            Authenticated Proxy Service to be used by troughout the class.
        with_address: bool, default = True
            If your wallet should have at least one address.
        """
        self._proxy = proxy_service
        if mode == 'c':
            self._wallet = self._create_wallet(label=wallet_label,
                                               address=with_address)
        elif mode == 'r':
            self._wallet = {}
        elif mode == 'l':
            self._wallet = self.load_wallet(wallet_label)
        else:
            raise NotImplementedError("Provide a valid Wallet mode!")

    @property
    def proxy(self) -> AuthServiceProxy:
        """
        Getter method for `proxy` attribute.
        """
        return self._proxy

    @property
    def wallet(self) -> dict:
        """
        Getter method for `wallet` attribute.
        """
        return self._wallet

    @classmethod
    @rpc_exec
    def _wrapper_executor(cls, _inst_func: Callable, *args):
        """
        Executor for wrapper functions to work withing instance methods.

        Parameters
        ---------
        _inst_func: Callable
            Instance function to be used.
        *args:
            Set of parameters to be passed down to the function.

        Returns
        -------
        dict
            Output of function execution.
        """
        if args:
            # Unpacks and unnest args before passing it down to function.
            return _inst_func(*args[0])
        else:
            return _inst_func()

    def _create_wallet(self, address: bool, 
                       label: Optional[str] = None) -> dict:
        """
        Create a wallet from a random name.

        Parameters
        ----------
        label: str
            Name for the wallet
        address: bool
            Either to create or not an address for this wallet.

        Returns
        ------
        dict
            Resulting metadata from Wallet creation process.
        """
        if not label:
            label = str(uuid4())
        creation = self._wrapper_executor(self.proxy.createwallet, label,
                                          False, False)
        if address:
            output = self._wrapper_executor(self.proxy.getnewaddress)
            return output
        else:
            return creation

    def _generate_mnemonic(self, strength: Optional[int] = 256,
                           language: Optional[str] = "english") -> str:
        """
        Generate a mnemonic for wallet creation.

        Parameters
        ----------
        strength: int, default = 256
            The length for the resulting phrase to be generated.
        language: str, default = "english"
            The language of the dictionary to be used.

        Returns
        -------
        str
            Resulting mnemonic phrase given its strenght.
        """
        mnemo = Mnemonic(language)
        return mnemo.generate(strength=strength)

    def list_wallets(self) -> list:
        """
        Get all saved wallets at node directory.

        Returns
        -------
        dict
            Dictionary with a lists of wallets.
        """
        return self._wrapper_executor(self.proxy.listwalletdir)

    def load_wallet(self, name: str) -> dict:
        """
        Load a wallet with a given filename.

        Parameters
        ----------
        label: str
            Label of the wallet to be loaded.

        Returns
        -------
        dict
            Dictionary with the wallet details
        """
        return self._wrapper_executor(self.proxy.loadwallet, name)

    def get_balance(self) -> dict:
        """
        Get the balance of the current wallet.

        Returns
        -------
        dict
            Dictionary with a lists of wallets
        """
        return self._wrapper_executor(self.proxy.getbalance)

    def get_address(self) -> str:
        """
        Get the current address of the wallet.

        Returns
        -------
        str
            Current address of the wallet.
        """
        return self._wrapper_executor(self.proxy.getaddress)

    def get_private_key(self) -> str:
        """
        Get the current private key of the wallet.

        Returns
        -------
        str
            Current private key of the wallet.
        """
        return self._wrapper_executor(self.proxy.dumpprivkey)

    def get_public_key(self) -> str:
        """
        Get the current public key of the wallet.

        Returns
        -------
        str
            Current public key of the wallet.
        """
        return self._wrapper_executor(self.proxy.getpubkey)

    def get_wallet_info(self) -> dict:
        """
        Get the current wallet information.

        Returns
        -------
        dict
            Current wallet information.
        """
        return self._wrapper_executor(self.proxy.getwalletinfo)

    def send_to_address(self, address: str, amount: float) -> str:
        """
        Send a transaction to a given address.
        TODO: Validate the input address.

        Parameters
        ---------
        address: str
            Address to send the transaction to.
        amount: float
            Amount to send.

        Returns
        -------
        str
            Transaction ID.
        """
        return self._wrapper_executor(self.proxy.sendtoaddress, 
            address, amount)


class Pool:
    """
    Object representing a unique pool of a token class.

    Attributes
    ----------
    _vault_wallet: Wallet
        Wallet owner of this Pool.
    """

    _vault_wallet: Wallet

    def __init__(self, input_wallet: Wallet):
        """
        Constructor for Pool class.

        Parameters
        ----------
        input_wallet: Wallet
            Wallet to own the Pool and safeguard the tokens.

        TO DO: Verify wether the one Pool corresponds to just one wallet.
        """
        self._vault_wallet = input_wallet

    @property
    def vaul_wallet(self) -> Wallet:
        """
        Getter method for `vault_wallet` attribute.
        """
        return self._vault_wallet

    def issue_token(self, amount: Union[str, float], 
                    reissue: Union[str, float]) -> dict:
        """
        Issue a token from the pool wallet.

        Parameters
        ----------
        amount: Union[str, float]
            Initial amount of tokens to be available.
        reissue: Union[str, float]
            Amount of reissuance tokens to generate.

        Returns
        -------
        dict
            Token metadata result.
        """
        return self._vault_wallet._wrapper_executor(
            self._vault_wallet.proxy.issueasset, amount, reissue)
