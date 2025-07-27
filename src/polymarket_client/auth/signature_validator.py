import hashlib
import hmac
import time
from typing import Dict, Optional


class SignatureValidator:
    """
    Validates request signatures for Polymarket API authentication.
    Supports validation of HMAC signatures with security checks.
    """

    def __init__(self, chain_id: int = 137) -> None:
        """
        Initialize the signature validator.

        Args:
            chain_id: Blockchain chain ID (default: 137 for Polygon)
        """
        self.chain_id = chain_id

    def validate_hmac_signature(
        self,
        signature: str,
        api_secret: str,
        method: str,
        path: str,
        body: str,
        timestamp: str
    ) -> bool:
        """
        Validate an HMAC signature for API key authentication.

        Args:
            signature: The signature to validate
            api_secret: API secret for signature verification
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: Request timestamp

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Recreate the message that should have been signed
            message = f"{timestamp}{method.upper()}{path}{body}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Compare signatures using constant time comparison
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

    def validate_timestamp(
        self,
        timestamp: str,
        max_age_seconds: int = 300
    ) -> bool:
        """
        Validate that a timestamp is recent enough.

        Args:
            timestamp: Unix timestamp string
            max_age_seconds: Maximum age in seconds (default: 5 minutes)

        Returns:
            True if timestamp is valid, False otherwise
        """
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            age = current_time - request_time
            
            # Check if timestamp is not too old and not in the future
            return 0 <= age <= max_age_seconds
        except (ValueError, TypeError):
            return False

    def validate_nonce(
        self,
        nonce: int,
        used_nonces: set,
        max_nonce_age_seconds: int = 3600
    ) -> bool:
        """
        Validate that a nonce hasn't been used before and isn't too old.

        Args:
            nonce: Nonce value to validate
            used_nonces: Set of previously used nonces
            max_nonce_age_seconds: Maximum nonce age in seconds

        Returns:
            True if nonce is valid, False otherwise
        """
        # Check if nonce was already used
        if nonce in used_nonces:
            return False
        
        # Check if nonce is not too old (assuming nonce is timestamp-based)
        current_time = int(time.time() * 1000000)  # Microseconds
        nonce_age = (current_time - nonce) / 1000000  # Convert to seconds
        
        return 0 <= nonce_age <= max_nonce_age_seconds

    def validate_request_headers(
        self,
        headers: Dict[str, str],
        required_headers: Optional[set] = None
    ) -> bool:
        """
        Validate that all required authentication headers are present.

        Args:
            headers: Request headers dictionary
            required_headers: Set of required header names

        Returns:
            True if all required headers are present, False otherwise
        """
        if required_headers is None:
            required_headers = {
                "L2-API-KEY",
                "L2-API-SIGNATURE", 
                "L2-API-TIMESTAMP",
                "L2-API-PASSPHRASE"
            }
        
        return all(header in headers for header in required_headers)

    def validate_api_key_format(self, api_key: str) -> bool:
        """
        Validate the format of an API key.

        Args:
            api_key: API key to validate

        Returns:
            True if format is valid, False otherwise
        """
        # Basic validation - adjust based on actual Polymarket API key format
        return (
            isinstance(api_key, str) and
            len(api_key) >= 32 and
            all(c.isalnum() or c in '-_' for c in api_key)
        )

    def validate_signature_format(self, signature: str) -> bool:
        """
        Validate the format of a signature.

        Args:
            signature: Signature to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            # Remove 0x prefix if present
            if signature.startswith('0x'):
                signature = signature[2:]
            
            # Check if it's valid hex and proper length
            int(signature, 16)
            return len(signature) in [64, 128, 130]  # Different signature lengths
        except ValueError:
            return False

    def validate_address_format(self, address: str) -> bool:
        """
        Validate the format of an Ethereum address.

        Args:
            address: Address to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            # Basic Ethereum address validation
            if not address.startswith('0x'):
                return False
            
            # Check length and hex format
            address_hex = address[2:]
            if len(address_hex) != 40:
                return False
            
            int(address_hex, 16)
            return True
        except ValueError:
            return False