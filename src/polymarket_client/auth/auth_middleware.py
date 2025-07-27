import time
from collections.abc import Callable

import requests
from requests.auth import AuthBase

from .request_signer import RequestSigner
from .signature_validator import SignatureValidator


class PolymarketAuth(AuthBase):
    """
    Requests authentication handler for Polymarket API.
    Automatically signs requests using configured credentials.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        private_key: str | None = None,
        chain_id: int = 137,
        signature_method: str = "hmac",
    ) -> None:
        """
        Initialize the authentication handler.

        Args:
            api_key: CLOB API key
            api_secret: CLOB API secret
            api_passphrase: CLOB API passphrase
            private_key: Ethereum private key
            chain_id: Blockchain chain ID
            signature_method: "hmac" or "eip712"
        """
        self.signer = RequestSigner(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            private_key=private_key,
            chain_id=chain_id,
        )
        self.signature_method = signature_method

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """
        Sign the request using the configured authentication method.

        Args:
            request: The request to sign

        Returns:
            The signed request
        """
        if self.signature_method == "hmac":
            self._sign_hmac(request)
        elif self.signature_method == "eip712":
            self._sign_eip712(request)

        return request

    def _sign_hmac(self, request: requests.PreparedRequest) -> None:
        """Sign request using HMAC method."""
        method = request.method or "GET"
        path = request.path_url or "/"
        body = request.body or ""

        if isinstance(body, bytes):
            body = body.decode("utf-8")

        headers = self.signer.sign_request_hmac(method, path, body)
        request.headers.update(headers)

    def _sign_eip712(self, request: requests.PreparedRequest) -> None:
        """Sign request using EIP-712 method."""
        if not self.signer.account:
            msg = "Private key required for EIP-712 signing"
            raise ValueError(msg)

        timestamp = str(int(time.time()))
        nonce = int(time.time() * 1000000)

        signature = self.signer.create_auth_signature(
            self.signer.account.address, timestamp, nonce
        )

        request.headers.update(
            {
                "POLY_ADDRESS": self.signer.account.address,
                "POLY_SIGNATURE": signature,
                "POLY_TIMESTAMP": timestamp,
                "POLY_NONCE": str(nonce),
            }
        )


class AuthMiddleware:
    """
    Middleware for handling request authentication and validation.
    Provides request/response interception for authentication purposes.
    """

    def __init__(
        self,
        validator: SignatureValidator | None = None,
        max_timestamp_age: int = 300,
        enable_nonce_tracking: bool = True,
    ) -> None:
        """
        Initialize the authentication middleware.

        Args:
            validator: Signature validator instance
            max_timestamp_age: Maximum age for timestamps in seconds
            enable_nonce_tracking: Whether to track nonces to prevent replay
        """
        self.validator = validator or SignatureValidator()
        self.max_timestamp_age = max_timestamp_age
        self.enable_nonce_tracking = enable_nonce_tracking
        self.used_nonces: set[int] = set()

    def validate_request(
        self, request: requests.PreparedRequest, api_secret: str | None = None
    ) -> bool:
        """
        Validate an incoming request's authentication.

        Args:
            request: The request to validate
            api_secret: API secret for HMAC validation

        Returns:
            True if request is valid, False otherwise
        """
        headers = dict(request.headers)

        # Check for HMAC authentication
        if self._has_hmac_headers(headers):
            return self._validate_hmac_request(request, headers, api_secret)

        # Check for EIP-712 authentication
        if self._has_eip712_headers(headers):
            return self._validate_eip712_request(request, headers)

        return False

    def _has_hmac_headers(self, headers: dict[str, str]) -> bool:
        """Check if request has HMAC authentication headers."""
        required_headers = {
            "L2-API-KEY",
            "L2-API-SIGNATURE",
            "L2-API-TIMESTAMP",
            "L2-API-PASSPHRASE",
        }
        return all(header in headers for header in required_headers)

    def _has_eip712_headers(self, headers: dict[str, str]) -> bool:
        """Check if request has EIP-712 authentication headers."""
        required_headers = {
            "POLY_ADDRESS",
            "POLY_SIGNATURE",
            "POLY_TIMESTAMP",
            "POLY_NONCE",
        }
        return all(header in headers for header in required_headers)

    def _validate_hmac_request(
        self,
        request: requests.PreparedRequest,
        headers: dict[str, str],
        api_secret: str | None,
    ) -> bool:
        """Validate HMAC-signed request."""
        if not api_secret:
            return False

        # Validate timestamp
        timestamp = headers.get("L2-API-TIMESTAMP", "")
        if not self.validator.validate_timestamp(timestamp, self.max_timestamp_age):
            return False

        # Validate signature
        signature = headers.get("L2-API-SIGNATURE", "")
        method = request.method or "GET"
        path = request.path_url or "/"
        body = request.body or ""

        if isinstance(body, bytes):
            body = body.decode("utf-8")

        return self.validator.validate_hmac_signature(
            signature, api_secret, method, path, body, timestamp
        )

    def _validate_eip712_request(
        self, request: requests.PreparedRequest, headers: dict[str, str]
    ) -> bool:
        """Validate EIP-712-signed request."""
        # Validate address format
        address = headers.get("POLY_ADDRESS", "")
        if not self.validator.validate_address_format(address):
            return False

        # Validate timestamp
        timestamp = headers.get("POLY_TIMESTAMP", "")
        if not self.validator.validate_timestamp(timestamp, self.max_timestamp_age):
            return False

        # Validate nonce
        try:
            nonce = int(headers.get("POLY_NONCE", "0"))
        except ValueError:
            return False

        if self.enable_nonce_tracking:
            if not self.validator.validate_nonce(nonce, self.used_nonces):
                return False
            self.used_nonces.add(nonce)

        # Validate signature
        signature = headers.get("POLY_SIGNATURE", "")
        message = "This message attests that I control the given wallet"

        return self.validator.validate_eip712_signature(
            signature, address, message, nonce, timestamp
        )

    def create_auth_session(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        private_key: str | None = None,
        signature_method: str = "hmac",
    ) -> requests.Session:
        """
        Create a requests session with authentication.

        Args:
            api_key: CLOB API key
            api_secret: CLOB API secret
            api_passphrase: CLOB API passphrase
            private_key: Ethereum private key
            signature_method: Authentication method ("hmac" or "eip712")

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Add authentication
        session.auth = PolymarketAuth(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            private_key=private_key,
            signature_method=signature_method,
        )

        # Add default headers
        session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "polymarket-client-python/1.0.0",
            }
        )

        return session

    def add_request_hook(
        self,
        session: requests.Session,
        hook_func: Callable[[requests.PreparedRequest], None],
    ) -> None:
        """
        Add a request hook to a session.

        Args:
            session: Session to add hook to
            hook_func: Function to call on each request
        """

        def request_hook(request: requests.PreparedRequest, *args, **kwargs):
            hook_func(request)
            return request

        session.hooks["request"] = [request_hook]

    def add_response_hook(
        self, session: requests.Session, hook_func: Callable[[requests.Response], None]
    ) -> None:
        """
        Add a response hook to a session.

        Args:
            session: Session to add hook to
            hook_func: Function to call on each response
        """

        def response_hook(response: requests.Response, *args, **kwargs):
            hook_func(response)
            return response

        session.hooks["response"] = [response_hook]

    def cleanup_nonces(self, max_age_seconds: int = 3600) -> None:
        """
        Clean up old nonces to prevent memory growth.

        Args:
            max_age_seconds: Maximum age for nonces in seconds
        """
        if not self.enable_nonce_tracking:
            return

        current_time = int(time.time() * 1000000)
        cutoff_time = current_time - (max_age_seconds * 1000000)

        # Remove nonces older than cutoff
        self.used_nonces = {nonce for nonce in self.used_nonces if nonce > cutoff_time}
