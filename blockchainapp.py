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
st.success(" Connected to sepolia via Alchemy")

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
#session state is a section that bugged me for a while, as streamlit naturally juyst keeps constantly refreshing after every interaction 
#and gettng rid of your input otherwise 
if "tx_log" not in st.session_state:
    st.session_state.tx_log = []

#this converts a timestamp into a human readable date and time, the provider can see how long they have access to the data the patient has given them
def format_expiration(timestamp):
    if timestamp == 0:
        return "Never/Denied"
    if timestamp < w3.eth.get_block('latest').timestamp:
        return f"Expired ({datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')})"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

#this part compiles together the complex steps of an ethereum transaction, and accepts the desired contract function as the main argument (ie registerPatient)
def send_transaction(function_call, action_name="Unknown Action"):
    try:
        txn = function_call.build_transaction({ #build_transaction prepares the sender address, a unique transaction nonce, gas limits, gas price, and the chain id, and then creates the unsighend transation 
            "from": w3.to_checksum_address(SENDER_ADDRESS),
            "nonce": w3.eth.get_transaction_count(SENDER_ADDRESS),
            "gas": 300_000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "chainId": 11155111
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY) #signs the transaction using the patients PRIVATE key (in this case i used the one from my metamask wallet)proof of ownership 
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
    st.header("PATIENT DASHBOARD") 
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

    if st.button("Grant Access"): #this checks at least one of the sections from  the dropdown menu are selected. 
        if not provider_address or not selected_sections:
            st.error("Please provide a Provider Address and select sections to grant access.")
        else:
            try:
                provider_addr_checksum = w3.to_checksum_address(provider_address) #converts the provider address into a case senstive checksum address format -- this is required by web3 and eth protocol 
                for section_name in selected_sections: # this is a loop through the selected sections -- a seperate blockchain transaction for each section, which you can see on streamlit
                    section_index = sections.index(section_name) #indexxing
                    receipt = send_transaction( #calling send_transaction functionf from earlier, passes the grantTimedaccess function 
                        contract.functions.grantTimedAccess(
                            provider_addr_checksum, section_index, 3600 #parameters -- provides access for a fixed duration (one hour), this could of course be modified with further dev
                        ),
                        action_name=f"Grant Access to {provider_address} ({section_name})" #creates a label for the transaction log 
                    )
                st.success(f"Access granted to {', '.join(selected_sections)}! Last Tx Hash: {receipt.transactionHash.hex()}") #using streamlits imbedded sucess message, then the f string for displaying eth address, sections, and the tx hash for checking on etherscan 
            except Exception as e:
                st.error(f"Transaction failed: {str(e)}")

    st.subheader("Transaction Log (Current  session)") #a section/subheader for transactions in current session, i dont know if streamlit can hold data over many different sessions, but this shows all current session activity 
    if st.session_state.tx_log:
        for tx in reversed(st.session_state.tx_log): #reversed transactions displayed, (newest displayed at the top otherwise itd be the opposite)
            tx_link = f"https://sepolia.etherscan.io/tx/{tx['tx_hash']}" #this builds a url so u can just click on it, taking you straight to an etherscan confirmation (on the sepolia testnet)
            st.markdown(f"**{tx['action']}** → Tx Hash: [`{tx['tx_hash'][:10]}...` ({tx['tx_hash']})]({tx_link})") # using streamlits markdown to display the action name, and the clickable hash
    else:
        st.write("No transactions yet.")

elif role == "Provider": #the provider side dashboard! 
    st.header("PROVIDER DASHBOARD") #heading display 
    
    msg_placeholder = st.empty() #area for messages to pop up, later used for access messaging 

    patient_address_input = st.text_input("Patient ethereum Address", help="The patient whose data you want to access.")  #box used for patients eth address
    provider_wallet_input = st.text_input("Your Provider Ethereum Address", help="Your wallet address, used as msg.sender for the permission check.") #for providers eth address, both of these using help argument to display a question mark, then showing a help message 

    if st.button("Check Access"): #this block executes when the button is clicked (st.button)
        
        if not patient_address_input or not provider_wallet_input: #checks if either field is missing 
            msg_placeholder.error("Please enter both the patient and your Provider Ethereum addresses.")
            st.stop() #exits 

        try: #try except block, uses web3's function to confert the raw string input into the checksummed eth address. the smart contract needs it in this format
            patient_address = w3.to_checksum_address(patient_address_input) 
            provider_wallet = w3.to_checksum_address(provider_wallet_input)
        except ValueError: 
            msg_placeholder.error("One of the addresses entered is not a valid  address.") #throws exception if a non valid address is entered 
            st.stop() 
        
        st.subheader("Detailed Permissions") #this is an area where the provider can open to check the details of what they have access to
        access_data = [] 

        try:
            try:
                contract.functions.viewPatientInfo(patient_address).call() #a gas-free read only call to the smart contract. gas-free functions should be in all blockchain based webfaces to stop overconsumption of gas 
            except Exception as e:
                msg_placeholder.error("Failed: Patient record is not registered on the contract. You must register the patient first.") # this will revert if the patient hasnt already been registered 
                st.stop()

            for i, section_name in enumerate(sections): #checks index in the sections list, using enumerate to get the readable section name and the index number, which is required by the solidity contract 
                has_access, expires_at = contract.functions.accessPermissions( #displays the boolean value (T/F) for sections accessible, and when they expire 
                    provider_wallet, 
                    i 
                ).call() 

                is_active = has_access and (expires_at > w3.eth.get_block('latest').timestamp or expires_at == 0) #access considered active if two conditions met, smart contract reports has_access is true, and the expires_at timestamp is greater than current time

                access_data.append({ #this section formats the detailed access  on the provider dashbopard, forming a dictionary containing section name, yes or no access status, an d the formatted expiration time
                    "Section": section_name,
                    "Has Access": " Yes" if is_active else "No",
                    "Expires At": format_expiration(expires_at)
                })

            granted_sections = [d["Section"] for d in access_data if d["Has Access"] == " Yes"] #uses a list comprehension to filter the access_data list and creates a new list containing only the section names that are actually currentlu active
            granted_count = len(granted_sections) #count of ative sessions 

            if granted_count > 0: # if the granted_count is more than 0, it will display the access message, saying how many section(S) are granted, otherwise access denied/expiered
                msg_placeholder.success(
                    f"Access verified: {granted_count} section(s) are currently active." 
                )
            else:
                msg_placeholder.error(
                    "Access denied, or all current access has expired."
                )
                
            
            st.table(access_data) #shows the access_data list as a clean formatted table 

        except Exception as e:
            msg_placeholder.error(
                "ERROR, something went wrong whilst checking the contract, please refresh page and try again"
            )
