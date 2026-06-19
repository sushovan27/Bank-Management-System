import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

from models.customer import Customer
from models.account import SavingsAccount, CurrentAccount, hash_pin
from models.transaction import Transaction, TransactionType

# Configure Streamlit page
st.set_page_config(page_title="NextGen Banking UI", page_icon="🏦", layout="wide")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
DATA_FILE = "data/accounts.json"
TRANSACTIONS_FILE = "data/transactions.json"

# --- HELPER FUNCTIONS ---
def load_accounts():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_accounts(accounts):
    with open(DATA_FILE, 'w') as f:
        json.dump(accounts, f, indent=4)

def load_transactions():
    try:
        with open(TRANSACTIONS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(transactions, f, indent=4)

def authenticate(account_num, pin):
    accounts = load_accounts()
    acc = next((a for a in accounts if a["account_number"] == account_num), None)
    if acc and acc.get("pin_hash") == hash_pin(pin):
        return acc
    return None

# --- UI STYLING ---
st.title("🏦 NextGen Banking System")
st.markdown("💰 **SECURE • TRUSTED • RELIABLE** 💰")
st.divider()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to:", [
    "Home", 
    "Create Account", 
    "Check Balance", 
    "Deposit", 
    "Withdraw", 
    "Transfer Funds", 
    "Transaction History",
    "Admin Controls"
])

# --- HOME ---
if menu == "Home":
    st.markdown("## Welcome to the Future of Banking 🚀")
    st.markdown("Manage your finances seamlessly with **NextGen Banking System**. Explore the global dashboard below.")
    st.divider()
    
    accounts = load_accounts()
    transactions = load_transactions()
    
    # Calculate Metrics
    total_accounts = len(accounts)
    total_balance = sum(acc.get('balance', 0) for acc in accounts)
    total_transactions = len(transactions)
    savings_count = sum(1 for a in accounts if a.get("account_type") == "SavingsAccount")
    current_count = total_accounts - savings_count
    
    # Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Active Accounts", total_accounts, delta="Growing 📈" if total_accounts > 0 else None)
    with col2:
        st.metric("Total Bank Assets", f"₹{total_balance:,.2f}")
    with col3:
        st.metric("Total Transactions", total_transactions)
    with col4:
        avg_bal = total_balance / total_accounts if total_accounts > 0 else 0
        st.metric("Avg Account Balance", f"₹{avg_bal:,.2f}")
        
    st.divider()
    
    # Charts Section
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Account Distribution")
        if total_accounts > 0:
            # Create a simple dataframe for the bar chart
            acc_df = pd.DataFrame({
                "Account Type": ["Savings", "Current"],
                "Count": [savings_count, current_count]
            })
            st.bar_chart(acc_df.set_index("Account Type"), color="#00ff00")
        else:
            st.info("No accounts available to display data.")
            
    with col_chart2:
        st.subheader("📈 Transaction Volume")
        if total_transactions > 0:
            txn_df = pd.DataFrame(transactions)
            txn_counts = txn_df['transaction_type'].value_counts().reset_index()
            txn_counts.columns = ['Transaction Type', 'Count']
            st.bar_chart(txn_counts.set_index("Transaction Type"), color="#00ffff")
        else:
            st.info("No transactions available yet.")
            
    st.divider()
    
    # Recent Activity Log
    st.subheader("🔔 Recent System Activity")
    if total_transactions > 0:
        # Get the 5 most recent transactions
        recent_txns = sorted(transactions, key=lambda x: x['timestamp'], reverse=True)[:5]
        for t in recent_txns:
            # Determine color and symbol based on transaction nature
            is_positive = t['transaction_type'] in ['deposit', 'opening_deposit', 'transfer_received', 'interest']
            color = "green" if is_positive else "red"
            symbol = "+" if is_positive else "-"
            
            # Format text
            txn_type_formatted = t['transaction_type'].replace('_', ' ').title()
            st.markdown(f"**{t['timestamp']}** | Account `{t['account_number']}`: {txn_type_formatted} | :{color}[{symbol}₹{t['amount']:,.2f}]")
    else:
        st.write("No recent activity.")

# --- CREATE ACCOUNT ---
elif menu == "Create Account":
    st.subheader("📝 Create New Account")
    
    with st.form("create_account_form"):
        name = st.text_input("Full Name*")
        phone = st.text_input("Phone Number*")
        email = st.text_input("Email*")
        address = st.text_area("Address (optional)")
        
        acc_type = st.selectbox("Account Type", ["Savings (Min ₹100, 4% Interest)", "Current (Overdraft up to ₹500)"])
        
        col1, col2 = st.columns(2)
        with col1:
            pin = st.text_input("Set 4-digit PIN*", type="password", max_chars=4)
        with col2:
            pin2 = st.text_input("Confirm PIN*", type="password", max_chars=4)
            
        initial_deposit = st.number_input("Initial Deposit Amount (₹)*", min_value=0.0, step=100.0)
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not name or not phone or not email or not pin:
                st.error("Please fill all required fields (*).")
            elif pin != pin2:
                st.error("PINs do not match.")
            elif len(pin) < 4:
                st.error("PIN must be 4 digits.")
            elif acc_type.startswith("Savings") and initial_deposit < 100:
                st.error("Savings account requires a minimum deposit of ₹100.")
            else:
                customer = Customer(name, phone, email, address)
                
                if acc_type.startswith("Savings"):
                    account = SavingsAccount(customer_id=customer.name, initial_deposit=initial_deposit, pin=pin)
                else:
                    account = CurrentAccount(customer_id=customer.name, initial_deposit=initial_deposit, pin=pin)

                account_data = account.to_dict()
                account_data["customer"] = customer.to_dict()

                accounts = load_accounts()
                accounts.append(account_data)
                save_accounts(accounts)

                txn = Transaction(
                    account_number=account.account_number,
                    transaction_type=TransactionType.OPENING_DEPOSIT,
                    amount=initial_deposit,
                    balance_after=initial_deposit,
                    description="Account opening deposit"
                )
                transactions = load_transactions()
                transactions.append(txn.to_dict())
                save_transactions(transactions)
                
                st.success("✅ Account Created Successfully!")
                st.info(f"**Your Account Number is:** `{account.account_number}`\nPlease save this number!")

# --- CHECK BALANCE ---
elif menu == "Check Balance":
    st.subheader("💳 Check Balance")
    
    acc_num = st.text_input("Account Number")
    pin = st.text_input("4-digit PIN", type="password", max_chars=4)
    
    if st.button("Check Balance"):
        acc = authenticate(acc_num, pin)
        if acc:
            st.success("Authentication Successful")
            
            col1, col2 = st.columns(2)
            col1.metric("Current Balance", f"₹{acc['balance']:,.2f}")
            col2.metric("Account Type", acc['account_type'].replace("Account", ""))
            
            st.write(f"**Customer Name:** {acc['customer']['name']}")
            st.write(f"**Opened On:** {acc['opening_date']}")
        else:
            st.error("❌ Invalid Account Number or PIN.")

# --- DEPOSIT ---
elif menu == "Deposit":
    st.subheader("📥 Deposit Money")
    
    acc_num = st.text_input("Account Number")
    pin = st.text_input("4-digit PIN", type="password", max_chars=4)
    amount = st.number_input("Amount to Deposit (₹)", min_value=1.0, step=100.0)
    
    if st.button("Deposit Funds"):
        acc = authenticate(acc_num, pin)
        if acc:
            accounts = load_accounts()
            # Find and update in the list
            for a in accounts:
                if a["account_number"] == acc_num:
                    a["balance"] += amount
                    save_accounts(accounts)
                    
                    txn = Transaction(account_number=acc_num, transaction_type=TransactionType.DEPOSIT,
                                      amount=amount, balance_after=a["balance"], description="Cash deposit via Web")
                    transactions = load_transactions()
                    transactions.append(txn.to_dict())
                    save_transactions(transactions)
                    
                    st.success(f"✅ Deposit Successful! New Balance: ₹{a['balance']:,.2f}")
                    break
        else:
            st.error("❌ Invalid Account Number or PIN.")

# --- WITHDRAW ---
elif menu == "Withdraw":
    st.subheader("📤 Withdraw Money")
    
    acc_num = st.text_input("Account Number")
    pin = st.text_input("4-digit PIN", type="password", max_chars=4)
    amount = st.number_input("Amount to Withdraw (₹)", min_value=1.0, step=100.0)
    
    if st.button("Withdraw Funds"):
        acc = authenticate(acc_num, pin)
        if acc:
            if acc["account_type"] == "SavingsAccount" and acc["balance"] - amount < 100.0:
                st.error("❌ Cannot withdraw. Minimum balance of ₹100 required.")
            elif acc["account_type"] == "CurrentAccount" and acc["balance"] - amount < -500.0:
                st.error("❌ Insufficient balance. Overdraft limit exceeded.")
            else:
                accounts = load_accounts()
                for a in accounts:
                    if a["account_number"] == acc_num:
                        a["balance"] -= amount
                        save_accounts(accounts)
                        
                        txn = Transaction(account_number=acc_num, transaction_type=TransactionType.WITHDRAWAL,
                                          amount=amount, balance_after=a["balance"], description="Cash withdrawal via Web")
                        transactions = load_transactions()
                        transactions.append(txn.to_dict())
                        save_transactions(transactions)
                        
                        st.success(f"✅ Withdrawal Successful! New Balance: ₹{a['balance']:,.2f}")
                        break
        else:
            st.error("❌ Invalid Account Number or PIN.")

# --- TRANSFER FUNDS ---
elif menu == "Transfer Funds":
    st.subheader("🔄 Transfer Funds")
    
    st.write("**Sender Details**")
    sender_acc_num = st.text_input("Your Account Number (Sender)")
    pin = st.text_input("Your 4-digit PIN", type="password", max_chars=4)
    
    st.write("**Receiver Details**")
    receiver_acc_num = st.text_input("Receiver's Account Number")
    
    amount = st.number_input("Amount to Transfer (₹)", min_value=1.0, step=100.0)
    
    if st.button("Transfer"):
        if sender_acc_num == receiver_acc_num:
            st.error("❌ Cannot transfer to the same account.")
        else:
            sender = authenticate(sender_acc_num, pin)
            if not sender:
                st.error("❌ Invalid Sender Account Number or PIN.")
            else:
                accounts = load_accounts()
                receiver = next((a for a in accounts if a["account_number"] == receiver_acc_num), None)
                
                if not receiver:
                    st.error("❌ Receiver account not found.")
                elif sender["account_type"] == "SavingsAccount" and sender["balance"] - amount < 100.0:
                    st.error("❌ Transfer failed. Savings minimum balance rule.")
                elif sender["account_type"] == "CurrentAccount" and sender["balance"] - amount < -500.0:
                    st.error("❌ Transfer failed. Overdraft limit exceeded.")
                else:
                    # Update balances
                    for a in accounts:
                        if a["account_number"] == sender_acc_num:
                            a["balance"] -= amount
                            new_sender_bal = a["balance"]
                        if a["account_number"] == receiver_acc_num:
                            a["balance"] += amount
                            new_receiver_bal = a["balance"]
                            
                    save_accounts(accounts)
                    
                    # Log transactions
                    transactions = load_transactions()
                    transactions.append(Transaction(sender_acc_num, TransactionType.TRANSFER_SENT, amount, new_sender_bal, description=f"To {receiver_acc_num}", related_account=receiver_acc_num).to_dict())
                    transactions.append(Transaction(receiver_acc_num, TransactionType.TRANSFER_RECEIVED, amount, new_receiver_bal, description=f"From {sender_acc_num}", related_account=sender_acc_num).to_dict())
                    save_transactions(transactions)
                    
                    st.success(f"✅ Transfer Successful! Your New Balance: ₹{new_sender_bal:,.2f}")

# --- TRANSACTION HISTORY ---
elif menu == "Transaction History":
    st.subheader("📜 Transaction History")
    
    acc_num = st.text_input("Account Number")
    pin = st.text_input("4-digit PIN", type="password", max_chars=4)
    
    if st.button("View History"):
        acc = authenticate(acc_num, pin)
        if acc:
            transactions = load_transactions()
            acc_txns = [txn for txn in transactions if txn["account_number"] == acc_num]
            
            if not acc_txns:
                st.warning("No transactions found for this account.")
            else:
                # Convert to Pandas DataFrame for nice Streamlit rendering
                df = pd.DataFrame(acc_txns)
                
                # Format columns
                df = df[['timestamp', 'transaction_id', 'transaction_type', 'amount', 'balance_after', 'description']]
                df.columns = ['Date & Time', 'Transaction ID', 'Type', 'Amount (₹)', 'Balance (₹)', 'Description']
                
                # Render table
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # CSV Export button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Statement as CSV",
                    data=csv,
                    file_name=f'statement_{acc_num}_{datetime.now().strftime("%Y%m%d%H%M")}.csv',
                    mime='text/csv',
                )
        else:
            st.error("❌ Invalid Account Number or PIN.")

# --- ADMIN CONTROLS ---
elif menu == "Admin Controls":
    st.subheader("⚙️ Admin Controls")
    
    admin_pin = st.text_input("Enter Admin Password", type="password")
    
    if st.button("Apply 4% Interest to All Savings Accounts"):
        if admin_pin == "admin123": # Hardcoded simple admin pass for demo
            accounts = load_accounts()
            transactions = load_transactions()
            count = 0
            
            for acc in accounts:
                if acc["account_type"] == "SavingsAccount":
                    interest = acc["balance"] * 0.04
                    acc["balance"] += interest
                    count += 1
                    transactions.append(Transaction(acc["account_number"], TransactionType.INTEREST, interest, acc["balance"], description="Annual Interest 4%").to_dict())
                    
            save_accounts(accounts)
            save_transactions(transactions)
            st.success(f"✅ Successfully applied 4% interest to {count} Savings Account(s).")
        else:
            st.error("❌ Unauthorized.")