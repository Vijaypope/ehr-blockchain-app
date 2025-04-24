import os
import streamlit as st
import hashlib
import json
from datetime import datetime

# Filenames
USERS_FILE = "users.json"
BLOCKCHAIN_FILE = "blockchain.json"

# Error-safe file loaders
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE, "r") as f:
                data = json.load(f)
                return [Block(**block) for block in data]
        except json.JSONDecodeError:
            pass
    return [Block(0, str(datetime.now()), {"message": "Genesis Block"}, "0")]

def save_blockchain(chain):
    with open(BLOCKCHAIN_FILE, "w") as f:
        json.dump([block.__dict__ for block in chain], f, indent=4)

# Blockchain classes
class Block:
    def __init__(self, index, timestamp, data, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = load_blockchain()

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), str(datetime.now()), data, latest_block.hash)
        self.chain.append(new_block)
        save_blockchain(self.chain)

# Authentication
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

# Session init
if 'ehr_blockchain' not in st.session_state:
    st.session_state.ehr_blockchain = Blockchain()

# UI
st.title("Blockchain-Based EHR Simulation")

menu = ["Sign Up", "Sign In"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Sign Up":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_password):
            st.success("User registered successfully! Please Sign In.")
        else:
            st.warning("Username already exists.")

elif choice == "Sign In":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success(f"Welcome {username}")
            st.session_state.logged_in = True
            st.session_state.current_user = username
        else:
            st.error("Invalid credentials.")

# Dashboard
if st.session_state.get("logged_in", False):
    st.subheader("EHR Dashboard")
    patient = st.text_input("Patient Name")
    diagnosis = st.text_input("Diagnosis")
    treatment = st.text_input("Treatment")
    if st.button("Add EHR Record"):
        data = {
            "doctor": st.session_state.current_user,
            "patient": patient,
            "diagnosis": diagnosis,
            "treatment": treatment
        }
        st.session_state.ehr_blockchain.add_block(data)
        st.success("Record added to blockchain!")

    if st.button("Show Blockchain"):
        for block in st.session_state.ehr_blockchain.chain:
            st.write(f"Index: {block.index}")
            st.write(f"Timestamp: {block.timestamp}")
            st.write(f"Data: {block.data}")
            st.write(f"Hash: {block.hash}")
            st.write(f"Previous Hash: {block.previous_hash}")
            st.markdown("---")
