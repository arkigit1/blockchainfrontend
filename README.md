# blockchainfrontend


Streamlit for blockchain assignment front end

It comprises of a Solidity Smart Contract deployed on testnet, with a Streamlit front end developed using python code 
The system operates across three layers:

**Contract Layer (Solidity):** The MedicalDataAccess.sol contract acts as an immutable ledger, storing who owns the data (the Patient) and what permissions have been granted (the Provider's address and an expiration timestamp for specific data sections).


**Connection Layer** connect_contract.py: The Python code uses the web3.py library and the contract_abi.json to communicate with the deployed contract on Sepolia.

**Application Layer (Streamlit):** The frontend provides two dashboards, one for write (patient side), and one for read (provider side)operations 

Patient Dashboard: Used for write operations (requires a private key to sign transactions for registration and granting access).

Provider Dashboard: Used for read operations (gas-free calls to check current access status).

** Prerequisites**
You must have the following tools installed:

Node.js & npm: (For Hardhat setup and dependency management).

Python 3+ (For running the Streamlit application).

MetaMask Wallet: Connected to the Sepolia Testnet with some test ETH for transaction fees (Gas).

Alchemy account to generate a sepolia rpc url 
**
**Setup and Installation**
1. Contract Environment Setup: create a new python virtual environment or make sure you activate your existing one (conda activate [environmentname])

2. install needed python packages 
pip install -r requirements.txt

** Configuration: Creating the .env File**
Before running the application, you must create a configuration file named .env in the root directory. This file holds your sensitive credentials and is explicitly ignored by Git (via .gitignore).

Create the .env file and fill it out using the template below:
Variable	Example Value	Description
ALCHEMY_RPC	https://eth-sepolia.g.alchemy.com/v2/...	**REQUIRED, it will NOT work without:** Your personal Sepolia RPC URL. This must be generated from a free service like Alchemy or Infura to allow your Python script to connect to the Ethereum network.
CONTRACT_ADDRESS =	0x9637fc9Fc7445d91553971B7A24f63bc87A70eB8
SENDER_ADDRESS = 0x4197d3AC950A9Bafec2A77EE04CceBC457faA638
PRIVATE_KEY	[YOUR 64-CHARACTER PRIVATE KEY]	CRITICAL: The private key cor0x9637fc9Fc7445d91553971B7A24f63bc87A70eB8responding to the SENDER_ADDRESS, used to pay gas and sign transactions. Since it was done on the sepolia testnet, you can use sepolia faucet and just give yourself a bunch of fake eth

**Hardhat environment setup**
npm install

Review Contract Files:
 package.json: Lists Node.js dependencies.

 hardhat.config.cjs: Defines Solidity compiler and network settings.

 deploy.cjs: The deployment script used to send the contract to Sepolia networks.


**MedicalDataAccess.sol**: The core smart contract logic. 




**5. How to Run and Demonstrate the Application**
The main application is split across two Streamlit files: the connector and the UI main logic.

Execute the Application: Run the application from your terminal:

in Anaconda Prompt

# If using Conda:
conda activate blockchain

# OR, if using a standard Python virtual environment:
source .venv/bin/activate

conda activate blockchain
cd "path to your file"
streamlit run blockchainapp.py

Demonstration Steps:

Steps
1. Register	Patient:	Fill out all personal data fields and click "Register Patient."	A Transaction Hash will appear, confirming the patient record was written to the smart contract.
2. Grant Access: Enter a Provider Address (any metamask wallet will do) and select sections. Click "Grant Access."	A separate transaction Hash will appear for each section, writing the permission to the blockchain.
3. Check Provider's access:	Switch roles. Enter the Patient's Address (the sender address) and the Provider's Address (hwichever wallet you just gave permissions to). Click "Check Access."	A table will display the granted sections with a Yes status and the expiration time (set to 1 hour).

**6. Key Files for Review**
File Name	Functional Role
blockchainapp.py	Contains the core Streamlit UI components, state management, and the send_transaction wrapper function. (**This file imports the w3 and contract objects from connect_contract.py).**
connect_contract.py	 handles web3 setup, ABI loading, and contract instance initialization.
MedicalDataAccess.sol	The complete Solidity source code for the smart contract.
contract_abi.json	The JSON interface required for web3.py to correctly call the contract functions.
