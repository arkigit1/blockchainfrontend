# -*- coding: utf-8 -*-
"""

Created on Tue Oct 14 07:42:31 2025
@author: arkij
"""

from web3 import Web3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ALCHEMY_RPC = os.getenv("ALCHEMY_RPC")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Connect to Sepolia via Alchemy
w3 = Web3(Web3.HTTPProvider(ALCHEMY_RPC))
print("Connected:", w3.is_connected())

if not w3.is_connected():
    raise Exception("Web3 connection failed — check your Alchemy RPC URL and internet connection.")

# Load contract ABI
abi_path = os.path.join(os.getcwd(), "contract_abi.json")
with open(abi_path, "r") as f:
    abi = json.load(f)

# Create contract instance
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
print("Contract loaded successfully!")
print("Available functions:", [fn for fn in contract.functions])
