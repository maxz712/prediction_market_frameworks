"""
USDC Allowance Setting for Polymarket Trading

This script sets ERC-20 allowances for USDC to enable trading on Polymarket.
You need to set your wallet address and private key before running this script.

IMPORTANT: Never commit your private key to version control!
"""

import os
from web3 import Web3
from dotenv import load_dotenv
from src.polymarket_client.polymarket_client import PolymarketClient
from src.polymarket_client.configs.polymarket_configs import PolymarketConfig

# Load environment variables
load_dotenv()

def set_usdc_allowance(target_allowance_usdc: float = 50.0):
    """
    Set USDC allowance for Polymarket trading.

    Args:
        target_allowance_usdc: Amount of USDC to approve (in USDC units, not wei)
    """

    # Configuration
    print("=== Setting USDC Allowance for Polymarket ===")
    print(f"Target allowance: {target_allowance_usdc} USDC")

    # Get your private key from environment variables
    private_key = os.getenv('POLYMARKET_PRIVATE_KEY')

    if not private_key:
        print("❌ Error: POLYMARKET_PRIVATE_KEY environment variable not set")
        print("   Please set your private key in .env file:")
        print("   POLYMARKET_PRIVATE_KEY=0x...")
        return

    # Connect to Polygon
    polygon_rpc_url = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
    w3 = Web3(Web3.HTTPProvider(polygon_rpc_url))

    # Check connection
    if not w3.is_connected():
        print(f"❌ Error: Could not connect to Polygon RPC at {polygon_rpc_url}")
        return

    print(f"✅ Connected to Polygon network")
    print(f"   Chain ID: {w3.eth.chain_id}")

    # Derive EOA address from private key (for signing transactions)
    try:
        account = w3.eth.account.from_key(private_key)
        eoa_address = account.address
        print(f"✅ EOA address derived from private key: {eoa_address}")
    except Exception as e:
        print(f"❌ Error deriving EOA address from private key: {e}")
        print("   Please check that your POLYMARKET_PRIVATE_KEY is valid")
        return

    # Get proxy wallet address from environment
    proxy_address = os.getenv('POLYMARKET_WALLET_PROXY_ADDRESS')
    if not proxy_address:
        print("❌ Error: POLYMARKET_WALLET_PROXY_ADDRESS environment variable not set")
        print("   Please set your proxy address in .env file:")
        print("   POLYMARKET_WALLET_PROXY_ADDRESS=0x...")
        return
    
    wallet_address = proxy_address
    print(f"✅ Using proxy wallet address: {wallet_address}")

    # Get exchange address from Polymarket client
    try:
        config = PolymarketConfig.from_env()
        client = PolymarketClient(config)
        exchange_address = client.clob.py_client.get_exchange_address()
        print(f"✅ Polymarket exchange address: {exchange_address}")
    except Exception as e:
        print(f"❌ Error getting exchange address: {e}")
        return

    # USDC contract on Polygon
    usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
    print(f"✅ USDC contract address: {usdc_address}")

    # USDC contract ABI (minimal for approve and allowance)
    usdc_abi = [
        {
            'inputs': [
                {'name': 'spender', 'type': 'address'},
                {'name': 'amount', 'type': 'uint256'}
            ],
            'name': 'approve',
            'outputs': [{'name': '', 'type': 'bool'}],
            'type': 'function'
        },
        {
            'inputs': [
                {'name': 'owner', 'type': 'address'},
                {'name': 'spender', 'type': 'address'}
            ],
            'name': 'allowance',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'type': 'function'
        },
        {
            'inputs': [{'name': 'account', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'type': 'function'
        }
    ]

    # Create contract instance
    usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)

    # Check current allowance and balance
    try:
        current_allowance_wei = usdc_contract.functions.allowance(wallet_address, exchange_address).call()
        current_allowance_usdc = current_allowance_wei / 1_000_000  # USDC has 6 decimals

        balance_wei = usdc_contract.functions.balanceOf(wallet_address).call()
        balance_usdc = balance_wei / 1_000_000

        # Check MATIC balance for gas fees (from EOA address)
        matic_balance_wei = w3.eth.get_balance(eoa_address)
        matic_balance = w3.from_wei(matic_balance_wei, 'ether')

        print(f"\n📊 Current Status:")
        print(f"   Proxy Wallet: {wallet_address}")
        print(f"   EOA Address: {eoa_address}")
        print(f"   MATIC Balance (EOA): {matic_balance:.6f} MATIC")
        print(f"   USDC Balance (Proxy): {balance_usdc:.6f} USDC")
        print(f"   Current Allowance: {current_allowance_usdc:.6f} USDC")
        print(f"   Target Allowance: {target_allowance_usdc:.6f} USDC")

        if current_allowance_usdc >= target_allowance_usdc:
            print(f"✅ Current allowance ({current_allowance_usdc:.6f} USDC) is already sufficient!")
            print(f"   No transaction needed.")
            return

    except Exception as e:
        print(f"❌ Error checking current allowance: {e}")
        return

    # Convert target allowance to wei (USDC has 6 decimals)
    amount_wei = int(target_allowance_usdc * 1_000_000)

    # Get current gas price
    try:
        gas_price = w3.eth.gas_price
        print(f"\n⛽ Current gas price: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei")
    except Exception as e:
        print(f"⚠️  Could not get gas price: {e}")
        gas_price = w3.to_wei('30', 'gwei')  # Fallback

    # Build transaction
    try:
        print(f"\n🔧 Building transaction...")
        txn = usdc_contract.functions.approve(exchange_address, amount_wei).build_transaction({
            'from': wallet_address,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(wallet_address)
        })

        print(f"   Transaction details:")
        print(f"   - From: {wallet_address}")
        print(f"   - To: {usdc_address}")
        print(f"   - Gas: {txn['gas']}")
        print(f"   - Gas Price: {w3.from_wei(txn['gasPrice'], 'gwei'):.2f} Gwei")
        print(f"   - Nonce: {txn['nonce']}")

        # Estimate transaction cost
        tx_cost_eth = w3.from_wei(txn['gas'] * txn['gasPrice'], 'ether')
        print(f"   - Estimated cost: {tx_cost_eth:.6f} MATIC")

        # Check if we have enough MATIC for gas
        if matic_balance < tx_cost_eth:
            print(f"\n❌ Insufficient MATIC for gas fees!")
            print(f"   Required: {tx_cost_eth:.6f} MATIC")
            print(f"   Available: {matic_balance:.6f} MATIC")
            print(f"   Shortfall: {tx_cost_eth - matic_balance:.6f} MATIC")
            print(f"\n💡 To fix this:")
            print(f"   1. Add MATIC to your EOA address: {eoa_address}")
            print(f"   2. You can get MATIC from:")
            print(f"      - Polygon Bridge: https://wallet.polygon.technology/bridge")
            print(f"      - Centralized exchanges (Coinbase, Binance, etc.)")
            print(f"      - Polygon faucets (for small amounts)")
            print(f"   3. You need at least {tx_cost_eth:.6f} MATIC for this transaction")
            return

    except Exception as e:
        print(f"❌ Error building transaction: {e}")
        return

    # Sign and send transaction
    try:
        print(f"\n📝 Signing transaction...")
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)

        print(f"🚀 Sending transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()

        print(f"✅ Transaction sent!")
        print(f"   Transaction hash: {tx_hash_hex}")
        print(f"   Polygonscan URL: https://polygonscan.com/tx/{tx_hash_hex}")

        # Wait for transaction receipt
        print(f"\n⏳ Waiting for transaction confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

        if tx_receipt.status == 1:
            print(f"✅ Transaction confirmed!")
            print(f"   Block number: {tx_receipt.blockNumber}")
            print(f"   Gas used: {tx_receipt.gasUsed}")

            # Verify the new allowance
            new_allowance_wei = usdc_contract.functions.allowance(wallet_address, exchange_address).call()
            new_allowance_usdc = new_allowance_wei / 1_000_000
            print(f"   New allowance: {new_allowance_usdc:.6f} USDC")

        else:
            print(f"❌ Transaction failed!")
            print(f"   Status: {tx_receipt.status}")

    except Exception as e:
        print(f"❌ Error sending transaction: {e}")
        return

if __name__ == "__main__":
    # Set allowance for 50 USDC (you can change this amount)
    set_usdc_allowance(50.0)