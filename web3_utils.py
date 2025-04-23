import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Connect to the Truffle Ganache development network
TRUFFLE_NETWORK_URL = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(TRUFFLE_NETWORK_URL))

if not web3.is_connected():
    print("❌ Failed to connect to Truffle Network. Start Ganache CLI or GUI.")
    exit(1)
else:
    print("✅ Connected to Truffle Network")

# Load compiled contract from Truffle build folder
CONTRACT_PATH = os.path.join(os.getcwd(), "build", "contracts", "CertificateRegistry.json")
if not os.path.exists(CONTRACT_PATH):
    print("❌ Contract JSON not found! Run `truffle compile`.")
    exit(1)

with open(CONTRACT_PATH) as f:
    contract_data = json.load(f)
    contract_abi = contract_data["abi"]
    contract_address = "0x822B4Cc181B642fEBadEc35D4c2C2549f8D85192"  # Ensure this is correct

# Connect to contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Load account details from environment
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

if not ACCOUNT_ADDRESS or not PRIVATE_KEY:
    print("⚠️ Warning: ACCOUNT_ADDRESS or PRIVATE_KEY missing from .env")
    exit(1)

def register_certificate(student_name, course_name, issue_date, certificate_hash):
    """Registers a certificate on the blockchain"""
    try:
        nonce = web3.eth.get_transaction_count(ACCOUNT_ADDRESS)

        txn = contract.functions.registerCertificate(
            student_name, course_name, issue_date, certificate_hash
        ).build_transaction({
            "from": ACCOUNT_ADDRESS,
            "nonce": nonce,
            "gas": 6721975,
            "gasPrice": web3.to_wei("20", "gwei")
        })

        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        raw_tx = signed_txn.raw_transaction
        tx_hash = web3.eth.send_raw_transaction(raw_tx)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"✅ Certificate registered successfully! Tx Hash: {tx_hash.hex()}")
        return receipt
    except Exception as e:
        print(f"❌ Error registering certificate: {e}")
        return None

def verify_certificate(certificate_hash):
    """Verifies if a certificate exists on the blockchain"""
    return contract.functions.verifyCertificate(certificate_hash).call()

def get_certificate_data(certificate_hash):
    """Retrieves certificate details from the blockchain"""
    return contract.functions.getCertificate(certificate_hash).call()

def get_certificate_registered_events():
    """Retrieves CertificateRegistered events from the blockchain"""
    try:
        event_filter = contract.events.CertificateRegistered.create_filter(from_block=0, to_block='latest')
        events = event_filter.get_all_entries()
        return events
    except Exception as e:
        print(f"❌ Error fetching events: {e}")
        return []

def get_debug_events():
    """Retrieves Debug events from the blockchain"""
    try:
        event_filter = contract.events.Debug.create_filter(from_block=0, to_block='latest')
        events = event_filter.get_all_entries()
        return events
    except Exception as e:
        print(f"❌ Error fetching debug events: {e}")
        return []