import hashlib
import hmac
import time
from unittest.mock import patch

import pytest

from polymarket_client.auth import (
    AuthMiddleware,
    RequestSigner,
    SignatureValidator,
)


class TestRequestSigner:
    """Test cases for RequestSigner class."""

    def setup_method(self):
        """Setup test environment."""
        self.api_key = "test_api_key"
        self.api_secret = "test_api_secret"
        self.api_passphrase = "test_passphrase"
        self.private_key = "0x" + "1" * 64  # Test private key
        self.chain_id = 137

    def test_init_with_api_credentials(self):
        """Test initialization with API credentials."""
        signer = RequestSigner(
            api_key=self.api_key,
            api_secret=self.api_secret,
            api_passphrase=self.api_passphrase,
            chain_id=self.chain_id,
        )

        assert signer.api_key == self.api_key
        assert signer.api_secret == self.api_secret
        assert signer.api_passphrase == self.api_passphrase
        assert signer.chain_id == self.chain_id
        assert signer.account is None

    def test_init_with_private_key(self):
        """Test initialization with private key."""
        signer = RequestSigner(private_key=self.private_key, chain_id=self.chain_id)

        assert signer.private_key == self.private_key
        assert signer.account is not None
        assert signer.chain_id == self.chain_id

    def test_sign_request_hmac(self):
        """Test HMAC request signing."""
        signer = RequestSigner(
            api_key=self.api_key,
            api_secret=self.api_secret,
            api_passphrase=self.api_passphrase,
        )

        method = "GET"
        path = "/test"
        body = ""
        timestamp = "1234567890"

        headers = signer.sign_request_hmac(method, path, body, timestamp)

        # Verify headers are present
        assert "L2-API-KEY" in headers
        assert "L2-API-SIGNATURE" in headers
        assert "L2-API-TIMESTAMP" in headers
        assert "L2-API-PASSPHRASE" in headers

        # Verify header values
        assert headers["L2-API-KEY"] == self.api_key
        assert headers["L2-API-TIMESTAMP"] == timestamp
        assert headers["L2-API-PASSPHRASE"] == self.api_passphrase

        # Verify signature
        message = f"{timestamp}{method.upper()}{path}{body}"
        expected_signature = hmac.new(
            self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        assert headers["L2-API-SIGNATURE"] == expected_signature

    def test_sign_request_hmac_missing_credentials(self):
        """Test HMAC signing with missing credentials."""
        signer = RequestSigner()

        with pytest.raises(
            ValueError, match="API key, secret, and passphrase are required"
        ):
            signer.sign_request_hmac("GET", "/test")

    def test_create_auth_signature(self):
        """Test EIP-712 authentication signature creation."""
        signer = RequestSigner(private_key=self.private_key, chain_id=self.chain_id)

        address = signer.get_signing_address()
        signature = signer.create_auth_signature(address)

        assert signature.startswith("0x")
        assert len(signature) in [130, 132]  # 65 or 66 bytes

    def test_create_auth_signature_no_private_key(self):
        """Test EIP-712 signing without private key."""
        signer = RequestSigner()

        with pytest.raises(ValueError, match="Private key is required"):
            signer.create_auth_signature("0x1234567890123456789012345678901234567890")

    def test_get_signing_address(self):
        """Test getting signing address."""
        signer = RequestSigner(private_key=self.private_key)
        address = signer.get_signing_address()

        assert address is not None
        assert address.startswith("0x")
        assert len(address) == 42

    def test_get_signing_address_no_key(self):
        """Test getting signing address without private key."""
        signer = RequestSigner()
        address = signer.get_signing_address()

        assert address is None


class TestSignatureValidator:
    """Test cases for SignatureValidator class."""

    def setup_method(self):
        """Setup test environment."""
        self.validator = SignatureValidator(chain_id=137)
        self.api_secret = "test_secret"

    def test_validate_hmac_signature_valid(self):
        """Test HMAC signature validation with valid signature."""
        method = "GET"
        path = "/test"
        body = ""
        timestamp = "1234567890"

        # Create valid signature
        message = f"{timestamp}{method.upper()}{path}{body}"
        valid_signature = hmac.new(
            self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        result = self.validator.validate_hmac_signature(
            valid_signature, self.api_secret, method, path, body, timestamp
        )

        assert result is True

    def test_validate_hmac_signature_invalid(self):
        """Test HMAC signature validation with invalid signature."""
        result = self.validator.validate_hmac_signature(
            "invalid_signature", self.api_secret, "GET", "/test", "", "1234567890"
        )

        assert result is False

    def test_validate_timestamp_valid(self):
        """Test timestamp validation with valid timestamp."""
        current_time = int(time.time())
        valid_timestamp = str(current_time - 100)  # 100 seconds ago

        result = self.validator.validate_timestamp(valid_timestamp, max_age_seconds=300)

        assert result is True

    def test_validate_timestamp_too_old(self):
        """Test timestamp validation with old timestamp."""
        old_timestamp = str(int(time.time()) - 400)  # 400 seconds ago

        result = self.validator.validate_timestamp(old_timestamp, max_age_seconds=300)

        assert result is False

    def test_validate_timestamp_future(self):
        """Test timestamp validation with future timestamp."""
        future_timestamp = str(int(time.time()) + 100)  # 100 seconds in future

        result = self.validator.validate_timestamp(future_timestamp)

        assert result is False

    def test_validate_timestamp_invalid_format(self):
        """Test timestamp validation with invalid format."""
        result = self.validator.validate_timestamp("not_a_timestamp")

        assert result is False

    def test_validate_nonce_valid(self):
        """Test nonce validation with valid nonce."""
        used_nonces = set()
        current_nonce = int(time.time() * 1000000)

        result = self.validator.validate_nonce(current_nonce, used_nonces)

        assert result is True

    def test_validate_nonce_already_used(self):
        """Test nonce validation with already used nonce."""
        current_nonce = int(time.time() * 1000000)
        used_nonces = {current_nonce}

        result = self.validator.validate_nonce(current_nonce, used_nonces)

        assert result is False

    def test_validate_address_format_valid(self):
        """Test address format validation with valid address."""
        valid_address = "0x1234567890123456789012345678901234567890"

        result = self.validator.validate_address_format(valid_address)

        assert result is True

    def test_validate_address_format_invalid(self):
        """Test address format validation with invalid address."""
        invalid_addresses = [
            "not_an_address",
            "0x123",  # Too short
            "1234567890123456789012345678901234567890",  # Missing 0x
            "0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # Invalid hex
        ]

        for address in invalid_addresses:
            result = self.validator.validate_address_format(address)
            assert result is False

    def test_validate_signature_format_valid(self):
        """Test signature format validation with valid signatures."""
        valid_signatures = [
            "0x" + "a" * 128,  # 64 bytes
            "0x" + "b" * 130,  # 65 bytes
            "c" * 128,  # Without 0x prefix
        ]

        for signature in valid_signatures:
            result = self.validator.validate_signature_format(signature)
            assert result is True

    def test_validate_signature_format_invalid(self):
        """Test signature format validation with invalid signatures."""
        invalid_signatures = [
            "not_a_signature",
            "0x123",  # Too short
            "0x" + "g" * 128,  # Invalid hex
        ]

        for signature in invalid_signatures:
            result = self.validator.validate_signature_format(signature)
            assert result is False


class TestAuthMiddleware:
    """Test cases for AuthMiddleware class."""

    def setup_method(self):
        """Setup test environment."""
        self.middleware = AuthMiddleware()
        self.api_secret = "test_secret"

    def test_create_auth_session(self):
        """Test creating authenticated session."""
        session = self.middleware.create_auth_session(
            api_key="test_key",
            api_secret="test_secret",
            api_passphrase="test_passphrase",
            signature_method="hmac",
        )

        assert session.auth is not None
        assert "Content-Type" in session.headers
        assert "User-Agent" in session.headers

    def test_cleanup_nonces(self):
        """Test nonce cleanup functionality."""
        # Add some test nonces
        current_time = int(time.time() * 1000000)
        old_nonce = current_time - (3700 * 1000000)  # > 1 hour old
        recent_nonce = current_time - (1800 * 1000000)  # 30 minutes old

        self.middleware.used_nonces = {old_nonce, recent_nonce}

        # Cleanup nonces older than 1 hour
        self.middleware.cleanup_nonces(max_age_seconds=3600)

        assert old_nonce not in self.middleware.used_nonces
        assert recent_nonce in self.middleware.used_nonces

    @patch("requests.PreparedRequest")
    def test_validate_request_missing_headers(self, mock_request):
        """Test request validation with missing headers."""
        mock_request.headers = {}

        result = self.middleware.validate_request(mock_request, self.api_secret)

        assert result is False

    def test_has_hmac_headers(self):
        """Test HMAC header detection."""
        headers_with_hmac = {
            "L2-API-KEY": "test",
            "L2-API-SIGNATURE": "test",
            "L2-API-TIMESTAMP": "test",
            "L2-API-PASSPHRASE": "test",
        }

        headers_without_hmac = {"L2-API-KEY": "test", "L2-API-SIGNATURE": "test"}

        assert self.middleware._has_hmac_headers(headers_with_hmac) is True
        assert self.middleware._has_hmac_headers(headers_without_hmac) is False

    def test_has_eip712_headers(self):
        """Test EIP-712 header detection."""
        headers_with_eip712 = {
            "POLY_ADDRESS": "test",
            "POLY_SIGNATURE": "test",
            "POLY_TIMESTAMP": "test",
            "POLY_NONCE": "test",
        }

        headers_without_eip712 = {"POLY_ADDRESS": "test", "POLY_SIGNATURE": "test"}

        assert self.middleware._has_eip712_headers(headers_with_eip712) is True
        assert self.middleware._has_eip712_headers(headers_without_eip712) is False
