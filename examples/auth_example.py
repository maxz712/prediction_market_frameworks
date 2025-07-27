#!/usr/bin/env python3
"""
Enhanced Authentication Example for Polymarket Client

This example demonstrates the new request signing and authentication validation
features added to the Polymarket client.

Features demonstrated:
- Request signing using HMAC and EIP-712
- Signature validation
- Authentication middleware
- Custom authentication sessions
- Security best practices
"""

import os
import time
from typing import Dict, Any

from polymarket_client import (
    PolymarketClient,
    PolymarketConfig,
    AuthMiddleware,
    RequestSigner,
    SignatureValidator
)


def main():
    """Main demonstration function."""
    print("Polymarket Client - Enhanced Authentication Demo")
    print("=" * 50)
    
    # Load configuration from environment variables
    try:
        config = PolymarketConfig.from_env()
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        print("\nMake sure to set the following environment variables:")
        print("- POLYMARKET_API_KEY")
        print("- POLYMARKET_API_SECRET")  
        print("- POLYMARKET_API_PASSPHRASE")
        print("- POLYMARKET_PRIVATE_KEY")
        return

    # Demo 1: Basic client with enhanced authentication
    print("\n1. Basic Client with Enhanced Authentication")
    print("-" * 40)
    
    client = PolymarketClient(config)
    print(f"✓ Client initialized with chain ID: {config.chain_id}")
    print(f"✓ Signature validation: {'enabled' if config.enable_signature_validation else 'disabled'}")
    print(f"✓ Default signature method: {config.signature_method}")
    
    # Demo 2: Request Signing Examples
    print("\n2. Request Signing Examples")
    print("-" * 40)
    
    # Initialize request signer
    signer = RequestSigner(
        api_key=config.api_key,
        api_secret=config.api_secret,
        api_passphrase=config.api_passphrase,
        private_key=config.pk,
        chain_id=config.chain_id
    )
    
    # HMAC signature example
    print("\nHMAC Signature Example:")
    try:
        hmac_headers = signer.sign_request_hmac(
            method="GET",
            path="/markets",
            body=""
        )
        print("✓ HMAC signature generated successfully")
        for header, value in hmac_headers.items():
            # Truncate sensitive values for display
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  {header}: {display_value}")
    except Exception as e:
        print(f"✗ HMAC signature failed: {e}")
    
    # EIP-712 signature example
    print("\nEIP-712 Signature Example:")
    try:
        eip712_signature = signer.create_auth_signature(
            address=signer.get_signing_address()
        )
        print("✓ EIP-712 signature generated successfully")
        print(f"  Signing address: {signer.get_signing_address()}")
        print(f"  Signature: {eip712_signature[:20]}...")
    except Exception as e:
        print(f"✗ EIP-712 signature failed: {e}")

    # Demo 3: Signature Validation
    print("\n3. Signature Validation")
    print("-" * 40)
    
    validator = SignatureValidator(chain_id=config.chain_id)
    
    # Validate timestamp
    current_timestamp = str(int(time.time()))
    old_timestamp = str(int(time.time()) - 400)  # 400 seconds ago
    
    print(f"✓ Current timestamp valid: {validator.validate_timestamp(current_timestamp)}")
    print(f"✗ Old timestamp valid: {validator.validate_timestamp(old_timestamp)}")
    
    # Validate address format
    valid_address = signer.get_signing_address()
    invalid_address = "not_an_address"
    
    print(f"✓ Valid address format: {validator.validate_address_format(valid_address)}")
    print(f"✗ Invalid address format: {validator.validate_address_format(invalid_address)}")

    # Demo 4: Authentication Middleware
    print("\n4. Authentication Middleware")
    print("-" * 40)
    
    # Create authentication middleware
    auth_middleware = AuthMiddleware(
        validator=validator,
        max_timestamp_age=300,
        enable_nonce_tracking=True
    )
    
    # Create authenticated session
    auth_session = auth_middleware.create_auth_session(
        api_key=config.api_key,
        api_secret=config.api_secret,
        api_passphrase=config.api_passphrase,
        private_key=config.pk,
        signature_method="hmac"
    )
    
    print("✓ Authenticated session created with HMAC signing")
    print("✓ Authentication middleware configured")
    
    # Demo 5: Security Features
    print("\n5. Security Features")
    print("-" * 40)
    
    print(f"✓ Nonce tracking: {'enabled' if config.nonce_tracking_enabled else 'disabled'}")
    print(f"✓ Max signature age: {config.max_signature_age_seconds} seconds")
    print(f"✓ Request validation: {'enabled' if config.enable_signature_validation else 'disabled'}")
    
    # Demo nonce tracking
    used_nonces = set()
    test_nonce = int(time.time() * 1000000)
    
    print(f"✓ New nonce valid: {validator.validate_nonce(test_nonce, used_nonces)}")
    used_nonces.add(test_nonce)
    print(f"✗ Reused nonce valid: {validator.validate_nonce(test_nonce, used_nonces)}")

    # Demo 6: Integration with Existing Features
    print("\n6. Integration with Existing Features")
    print("-" * 40)
    
    try:
        # Test authenticated API call (if credentials are valid)
        user_address = client.get_user_address()
        print(f"✓ Authenticated API call successful")
        print(f"  User address: {user_address}")
    except Exception as e:
        print(f"ℹ Authenticated API call info: {e}")
        print("  (This is expected if using test credentials)")

    print("\n" + "=" * 50)
    print("Authentication Demo Complete!")
    print("\nKey Features Added:")
    print("• HMAC-SHA256 request signing")
    print("• EIP-712 wallet-based signatures")
    print("• Comprehensive signature validation")
    print("• Nonce tracking for replay protection")
    print("• Configurable authentication middleware")
    print("• Integration with existing client features")


if __name__ == "__main__":
    main()