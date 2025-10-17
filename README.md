# blockchainfrontend
Streamlit for blockchain assignment front end
The system operates across three layers:

**Contract Layer (Solidity):** The MedicalDataAccess.sol contract acts as an immutable ledger, storing who owns the data (the Patient) and what permissions have been granted (the Provider's address and an expiration timestamp for specific data sections).


Connection Layer (Python web3.py): The Python code uses the web3.py library and the contract_abi.json to communicate with the deployed contract on Sepolia.

**Application Layer (Streamlit):** The frontend provides two dashboards, one for write, and one for read operations 

Patient Dashboard: Used for write operations (requires a private key to sign transactions for registration and granting access).

Provider Dashboard: Used for read operations (gas-free calls to check current access status).

**2. Prerequisites**
You must have the following tools installed:

Node.js & npm: (For Hardhat setup and dependency management).

Python 3+ (For running the Streamlit application).

MetaMask Wallet: Connected to the Sepolia Testnet with some test ETH for transaction fees (Gas).
**
**3. Setup and Installation****
A. Contract Environment Setup
This section verifies the environment used to compile and deploy the contract.

Install Dependencies: Open your terminal in the project root directory and install all Node.js packages specified in package.json:

**Bash**
npm install

Review Contract Files:

**MedicalDataAccess.sol**: The core smart contract logic.

hardhat.config.cjs: Defines compiler settings and network configuration.

deploy.cjs: The script used to deploy the contract to Sepolia.

**B. Frontend Environment Setup**
Install Python Packages: Install the required libraries, including web3 for interacting with blockcain, python-dotenv for the secure reading of the .env file, and streamlit for the interface:

Bash

pip install web3 python-dotenv streamlit

**4. Configuration: Creating the .env File**
Before running the application, you must create a configuration file named .env in the root directory. This file holds your sensitive credentials and is explicitly ignored by Git (via .gitignore).

Create the .env file and fill it out using the template below:

Variable	Example Value	Description
ALCHEMY_RPC	https://eth-sepolia.g.alchemy.com/v2/...	Your personal Sepolia RPC URL for connecting to the network.
CONTRACT_ADDRESS	0x123...	The public address of the contract you deployed on Sepolia.
SENDER_ADDRESS	0xAbC...	The public address of the wallet that signs transactions (the Patient's wallet in this demo).
PRIVATE_KEY	[YOUR 64-CHARACTER PRIVATE KEY]	CRITICAL: The private key corresponding to the SENDER_ADDRESS, used to pay gas and sign transactions. Since it was done on the sepolia testnet, you can use sepolia faucet and just give yourself a bunch of fake eth

5. How to Run and Demonstrate the Application
The main application is split across two Streamlit files: the connector and the UI logic.

Execute the Application: Run the application from your terminal:

Bash

streamlit run blockchainapp.py
Demonstration Steps:

Step	Role	Action	Verification
1. Register	Patient	Fill out all personal data fields and click "Register Patient."	A Transaction Hash will appear, confirming the patient record was written to the contract.
2. Grant Access	Patient	Enter a Provider Address (use your second MetaMask wallet) and select sections. Click "Grant Access."	A separate Transaction Hash will appear for each section, writing the permission to the blockchain.
3. Check	Provider	Switch roles. Enter the Patient's Address and the Provider's Address. Click "Check Access."	A table will display the granted sections with a Yes status and the expiration time (set to 1 hour).

**6. Key Files for Review**
File Name	Functional Role
blockchainapp.py	Contains the core Streamlit UI components, state management, and the send_transaction wrapper function.
connect_contract.py	The Main Entry Point that handles web3 setup, ABI loading, and contract instance initialization.
MedicalDataAccess.sol	The complete Solidity source code for the governance contract.
contract_abi.json	The JSON interface required for web3.py to correctly call the contract functions.
