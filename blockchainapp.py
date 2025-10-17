'''this section below imports all the required python packages. json handles the contract, os for the environment avriables, streamlit for streamlit 
web3 is the necessary ethereum interactions, dotenv for to load the hidden keys (which are in my .env file, and datetime for timestamp handling)'''
import json
import os
import streamlit as st
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

#this part loads the file .env, which contains all these variables below (sepolia node url, contract address (this is current my own deployed contract, can use williams if 
#we deploy his on sepolia), sender address(this is from one of my metamask wallets, and so is the "provider address" i use later on
#the private key is a priavte key generated from my metamask wallet as well

load_dotenv()
ALCHEMY_RPC = os.getenv("ALCHEMY_RPC")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")

#this part starts web3, which is the main interface for ethereum interaction. it is using my alchemy url to talk to sepolia
#This has error handling, and displays either a error or success message via the inbuilt streamlit attributes. havent had a failure yet, the success message always displays in a nice 
#green banner up top
w3 = Web3(Web3.HTTPProvider(ALCHEMY_RPC))
if not w3.is_connected():
    st.error("Failed to connect to Sepolia. Check your RPC URL.")
    st.stop()
st.success(" Connected to Sepolia via Alchemy")

#error handling for loading the abi -- this is the abi i got from william, it tell pythn how to talk to the smart contract 
try:
    with open("contract_abi.json", "r") as f:
        abi = json.load(f)
except FileNotFoundError:
    st.error("contract_abi.json' not found. Please ensure it is in the same directory.")
    st.stop()
 
 #this creates a callable object that represents the smart contract, its how u can call the smart contract functions (like contract.functions.registerPatient,
#if it works itll display the contract address on the streamlit sidebar (which is also where u can pick the dashboard side
contract = w3.eth.contract(
    address=w3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)
st.sidebar.write("Contract loaded:", CONTRACT_ADDRESS)

#gathered from streamlit how-tos, some basic page configurations (titles, layouts)
st.set_page_config(page_title="Patient Data Governance", layout="wide")
st.title("Patient Data Governance on Blockchain")

#this part defines a list which shows some patient data the patients can grant access too their provider for
sections = ["Personal Information", "Blood Results", "Imaging", "Medications"]

#Session state is how Streamlit remembers variable values between user interactions (like clicking a button). 
#This initializes an empty list called tx_log to track all transactions made during the current session.
#session state is a section that bugged me for a while, as streamlit naturally juyst keeps constantly refreshing and gettng rid of your input otherwise 
if "tx_log" not in st.session_state:
    st.session_state.tx_log = []

#this converts a timestamp into a human readable date and time, the provider can see how long they have access to the data the patient has given them
def format_expiration(timestamp):
    if timestamp == 0:
        return "Never/Denied"
    if timestamp < w3.eth.get_block('latest').timestamp:
        return f"Expired ({datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')})"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

#this part compiles together the complex steps of an ethereum transaction, had to search git hub for this one
def send_transaction(function_call, action_name="Unknown Action"):
    try:
        txn = function_call.build_transaction({ #build_transaction prepares the sender address, a unique transaction nonce, gas limits, gas price, and the chain id
            "from": w3.to_checksum_address(SENDER_ADDRESS),
            "nonce": w3.eth.get_transaction_count(SENDER_ADDRESS),
            "gas": 300_000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "chainId": 11155111
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY) #signs the transaction using the patients private key (from my metamask wallet)proof of ownership 
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)#sends to sepolia network 
        
        with st.spinner(f"Sending transaction for '{action_name}'..."): #displays a loading spinner whilst waiting for transaction to go to the blockchain
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash) #this prints the transaction recipt

        st.session_state.tx_log.append({"action": action_name, "tx_hash": receipt.transactionHash.hex()})
        return receipt #this shows the receipt in the transaction log at the bottom of the page on streamlit, u can even click straight on the hex
    except Exception as e:
        raise e

role = st.sidebar.radio("Select Role", ["Patient", "Provider"]) #this is just for the button on the sidebar to pick either the patient or provider dashboard

if role == "Patient": #The PATIENT DASHBOARD. displays the patients address (one of my metamask wallets -- the demo just uses both of my wallets to show 
    #interaction between wallets is possible in this ui, a more fledged out front end would have a full login portal, and would display other things based of the user login etc etc 
    st.header("Patient Dashboard") 
    st.write("Your Ethereum Address (Sender):", SENDER_ADDRESS) 
    #this displays a bunch of boxes to right patient personal data in, the user must fill all sections out to register a patient-- uses st.text_input or st.number_input to create field for data entry 
    patient_id = st.text_input("Patient ID / MRN")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, value=0) 
    gender = st.text_input("Gender")
    physical_address = st.text_input("Physical Address")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    
    #the flow here is a but funky, but this is where u enter the providers eth address (in this case, my other metamask wallet, and then a dropdown menu with the options from the list ealier that you want to give 
    #to the provider i.e. personal info, imaging)
    provider_address = st.text_input("Provider Ethereum Address to Grant Access")
    selected_sections = st.multiselect("Sections to grant access", sections)

    #the register patient button once pressed runs validation checks (checks for empty fields), if all satify requirements, it trys to send a transaction on the blockchain and 
    #writes the patients information to the smart contract 
    if st.button("Register Patient"):
        if not patient_id.strip() or not name.strip() or age is None or age < 0 or not gender.strip() or not physical_address.strip() or not phone.strip() or not email.strip():
            st.error("ERROR: All text fields (MRN, Name, Gender, Address, Phone, Email) must be filled, and Age must be 0 or greater.")
        else:
            try:
                receipt = send_transaction( #this is actually calling web3.py functions, and sends the data from contract.functions.registerPatient()
                    contract.functions.registerPatient(
                        patient_id, name, int(age), gender, physical_address, phone, email
                    ),
                    action_name="Register Patient"
                )
                st.success(f" Patient registered! Tx Hash: {receipt.transactionHash.hex()}") #this provides a success message and/or failure
            except Exception as e:
                st.error(f"Transaction failed: {str(e)}")

    if st.button("Grant Access"): #this checks at least one of the sections from  the dropdown menu are selected 
        if not provider_address or not selected_sections:
            st.error("Please provide a Provider Address and select sections to grant access.")
        else:
            try:
                provider_addr_checksum = w3.to_checksum_address(provider_address)
                for section_name in selected_sections:
                    section_index = sections.index(section_name)
                    receipt = send_transaction(
                        contract.functions.grantTimedAccess(
                            provider_addr_checksum, section_index, 3600
                        ),
                        action_name=f"Grant Access to {provider_address} ({section_name})"
                    )
                st.success(f"Access granted to {', '.join(selected_sections)}! Last Tx Hash: {receipt.transactionHash.hex()}")
            except Exception as e:
                st.error(f"Transaction failed: {str(e)}")

    st.subheader("Transaction Log (Current  session)")
    if st.session_state.tx_log:
        for tx in reversed(st.session_state.tx_log):
            tx_link = f"https://sepolia.etherscan.io/tx/{tx['tx_hash']}"
            st.markdown(f"**{tx['action']}** → Tx Hash: [`{tx['tx_hash'][:10]}...` ({tx['tx_hash']})]({tx_link})")
    else:
        st.write("No transactions yet.")

elif role == "Provider":
    st.header("Provider Dashboard")
    
    msg_placeholder = st.empty() 

    patient_address_input = st.text_input("Patient Ethereum Address", help="The patient whose data you want to access.")
    provider_wallet_input = st.text_input("Your Provider Ethereum Address", help="Your wallet address, used as msg.sender for the permission check.")

    if st.button("Check Access"):
        
        if not patient_address_input or not provider_wallet_input:
            msg_placeholder.error("Please enter both the Patient and your Provider Ethereum Addresses.")
            st.stop() 

        try:
            patient_address = w3.to_checksum_address(patient_address_input) 
            provider_wallet = w3.to_checksum_address(provider_wallet_input)
        except ValueError:
            msg_placeholder.error("One of the addresses entered is not a valid Ethereum address.")
            st.stop() 
        
        st.subheader("Detailed Permissions")
        access_data = []

        try:
            try:
                contract.functions.viewPatientInfo(patient_address).call()
            except Exception as e:
                msg_placeholder.error("Failed: Patient record is not registered on the contract. You must register the patient first.")
                st.stop()

            for i, section_name in enumerate(sections):
                has_access, expires_at = contract.functions.accessPermissions(
                    provider_wallet, 
                    i 
                ).call() 

                is_active = has_access and (expires_at > w3.eth.get_block('latest').timestamp or expires_at == 0)

                access_data.append({
                    "Section": section_name,
                    "Has Access": " Yes" if is_active else "No",
                    "Expires At": format_expiration(expires_at)
                })

            granted_sections = [d["Section"] for d in access_data if d["Has Access"] == "Yes"]

            if granted_sections:
                msg_placeholder.success(f"Access granted to sections: {', '.join(granted_sections)}")
            else:
                msg_placeholder.info("Access denied for all sections, or all access has expired.")

            st.table(access_data)

        except Exception as e:
            error_message = f"Failed to read from contract. Underlying error: {str(e)}\n\n"
            error_message += f" **CRITICAL STEP MISSED:** Since you just deployed a new contract (address: `{CONTRACT_ADDRESS}`), "
            error_message += "all previous data was lost. You **MUST** complete these steps again on the Patient Dashboard:\n"
            error_message += "1. **Register Patient** (to create the patient record on the new contract).\n"
            error_message += "2. **Grant Access** (to write the permissions on the new contract)."
            msg_placeholder.error(error_message)
