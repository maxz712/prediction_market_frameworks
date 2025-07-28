import hashlib
import hmac
import time

try:
    from eth_account import Account
    from eth_account.messages import encode_defunct
    from web3 import Web3

    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False


class RequestSigner:
    """
    Handles request signing for Polymarket API calls using HMAC-SHA256.
    Provides secure authentication for API requests.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        private_key: str | None = None,
        chain_id: int = 137,
    ) -> None:
        """
        Initialize the request signer.

        Args:
            api_key: CLOB API key for HMAC signing
            api_secret: CLOB API secret for HMAC signing
            api_passphrase: CLOB API passphrase for HMAC signing
            private_key: Ethereum private key (for future EIP-712 support)
            chain_id: Blockchain chain ID (default: 137 for Polygon)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.private_key = private_key
        self.chain_id = chain_id

        # Initialize account if private key is provided
        self.account = None
        if private_key and WEB3_AVAILABLE:
            try:
                self.account = Account.from_key(private_key)
            except Exception:
                self.account = None

    def sign_request_hmac(
        self, method: str, path: str, body: str = "", timestamp: str | None = None
    ) -> dict[str, str]:
        """
        Sign a request using HMAC-SHA256 for API key authentication.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (JSON string)
            timestamp: Unix timestamp (auto-generated if None)

        Returns:
            Dictionary containing signature headers

        Raises:
            ValueError: If API credentials are not configured
        """
        if not all([self.api_key, self.api_secret, self.api_passphrase]):
            msg = "API key, secret, and passphrase are required for HMAC signing"
            raise ValueError(msg)

        if timestamp is None:
            timestamp = str(int(time.time()))

        # Create the signature payload
        message = f"{timestamp}{method.upper()}{path}{body}"

        # Generate HMAC signature
        signature = hmac.new(
            self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return {
            "L2-API-KEY": self.api_key,
            "L2-API-SIGNATURE": signature,
            "L2-API-TIMESTAMP": timestamp,
            "L2-API-PASSPHRASE": self.api_passphrase,
        }

    def create_auth_headers(
        self, method: str, path: str, body: str = ""
    ) -> dict[str, str]:
        """
        Create authentication headers for a request.

        Args:
            method: HTTP method
            path: Request path
            body: Request body

        Returns:
            Dictionary of authentication headers
        """
        return self.sign_request_hmac(method, path, body)

    def verify_hmac_signature(
        self, signature: str, method: str, path: str, body: str, timestamp: str
    ) -> bool:
        """
        Verify an HMAC signature for request authentication.

        Args:
            signature: The signature to verify
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: Request timestamp

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.api_secret:
            return False

        try:
            # Recreate the message that should have been signed
            message = f"{timestamp}{method.upper()}{path}{body}"

            # Generate expected signature
            expected_signature = hmac.new(
                self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            # Compare signatures using constant time comparison
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

    def create_auth_signature(
        self, address: str, timestamp: str | None = None, nonce: int | None = None
    ) -> str:
        """
        Create an EIP-712 authentication signature.

        Args:
            address: Ethereum address to sign for
            timestamp: Unix timestamp (auto-generated if None)
            nonce: Nonce value (auto-generated if None)

        Returns:
            Hex-encoded signature

        Raises:
            ValueError: If private key is not configured
        """
        if not self.private_key:
            msg = "Private key is required for EIP-712 signing"
            raise ValueError(msg)

        if not WEB3_AVAILABLE:
            msg = "web3 package is required for EIP-712 signing"
            raise ValueError(msg)

        if timestamp is None:
            timestamp = str(int(time.time()))
        if nonce is None:
            nonce = int(time.time() * 1000000)

        # Simple message signing for now - in production this would be proper EIP-712
        message = f"This message attests that I control the given wallet {address} at {timestamp} with nonce {nonce}"

        try:
            # Sign the message
            message_to_sign = encode_defunct(text=message)
            signed_message = self.account.sign_message(message_to_sign)
            signature_hex = signed_message.signature.hex()
            if not signature_hex.startswith("0x"):
                signature_hex = "0x" + signature_hex
            return signature_hex
        except Exception as e:
            msg = f"Failed to create signature: {e}"
            raise ValueError(msg) from e

    def get_signing_address(self) -> str | None:
        """
        Get the Ethereum address for the configured private key.

        Returns:
            Ethereum address or None if no private key configured
        """
        if self.account:
            return self.account.address
        return None
