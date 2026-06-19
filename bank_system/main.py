import os
import json
from models.customer import Customer
from models.account import SavingsAccount, CurrentAccount
from models.transaction import Transaction, TransactionType

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# File to store all accounts
DATA_FILE = "data/accounts.json"
TRANSACTIONS_FILE = "data/transactions.json"


def display_logo():
    print("""
    ███████╗██╗   ██╗███████╗██╗  ██╗ ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗
    ██╔════╝██║   ██║██╔════╝██║  ██║██╔═══██╗██║   ██║██╔══██╗████╗  ██║
    ███████╗██║   ██║███████╗███████║██║   ██║██║   ██║███████║██╔██╗ ██║
    ╚════██║██║   ██║╚════██║██╔══██║██║   ██║╚██╗ ██╔╝██╔══██║██║╚██╗██║
    ███████║╚██████╔╝███████║██║  ██║╚██████╔╝ ╚████╔╝ ██║  ██║██║ ╚████║
    ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝

    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    💰  SECURE  •  TRUSTED  •  RELIABLE  💰
    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    """)


def load_accounts():
    """Load accounts from JSON file. Returns empty list if file doesn't exist."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_accounts(accounts):
    """Save accounts list to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(accounts, f, indent=4)


def load_transactions():
    """Load transactions from JSON file. Returns empty list if file doesn't exist."""
    try:
        with open(TRANSACTIONS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_transactions(transactions):
    """Save transactions list to JSON file."""
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(transactions, f, indent=4)


def create_account():
    print("\n--- CREATE NEW ACCOUNT ---")

    # Get customer details
    name = input("Enter Full Name: ")
    phone = input("Enter Phone Number: ")
    email = input("Enter Email: ")
    address = input("Enter Address (optional): ")

    # Get account type
    print("\nAccount Types:")
    print("1. Savings (Minimum balance: ₹100)")
    print("2. Current (Overdraft up to ₹500)")
    acc_type = input("Choose account type (1 or 2): ")

    # Get initial deposit
    try:
        initial_deposit = float(input("Enter Initial Deposit Amount: ₹"))
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    # Create the objects
    customer = Customer(name, phone, email, address)

    if acc_type == "1":
        account = SavingsAccount(customer_id=customer.name, initial_deposit=initial_deposit)
        if initial_deposit < 100:
            print("❌ Savings account requires a minimum deposit of ₹100.")
            return
    elif acc_type == "2":
        account = CurrentAccount(customer_id=customer.name, initial_deposit=initial_deposit)
    else:
        print("❌ Invalid account type.")
        return

    # Combine data and save
    account_data = account.to_dict()
    account_data["customer"] = customer.to_dict()  # Embed customer inside account

    accounts = load_accounts()
    accounts.append(account_data)
    save_accounts(accounts)

    # Log transaction
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

    print("\n✅ ACCOUNT CREATED SUCCESSFULLY!")
    print(f"📌 Account Number: {account.account_number}")
    print(f"💰 Current Balance: ₹{account.balance}")
    print(f"📅 Opening Date: {account.opening_date}")


def check_balance():
    print("\n--- CHECK BALANCE ---")
    acc_num = input("Enter your Account Number: ")

    accounts = load_accounts()

    for acc in accounts:
        if acc["account_number"] == acc_num:
            print("\n✅ ACCOUNT FOUND")
            print(f"👤 Customer: {acc['customer']['name']}")
            print(f"🏦 Account Type: {acc['account_type']}")
            print(f"💰 Current Balance: ₹{acc['balance']}")
            print(f"📅 Opened on: {acc['opening_date']}")
            return

    print("❌ Account not found. Please check the account number.")

def deposit():
    print("\n--- DEPOSIT MONEY ---")
    acc_num = input("Enter your Account Number: ")

    try:
        amount = float(input("Enter amount to deposit: ₹"))
        if amount <= 0:
            print("❌ Amount must be greater than zero.")
            return
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    accounts = load_accounts()

    for acc in accounts:
        if acc["account_number"] == acc_num:
            # Update the balance
            acc["balance"] += amount

            # Save back to file
            save_accounts(accounts)

            # Log transaction
            txn = Transaction(
                account_number=acc_num,
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                balance_after=acc["balance"],
                description="Cash deposit"
            )
            transactions = load_transactions()
            transactions.append(txn.to_dict())
            save_transactions(transactions)

            print("\n✅ DEPOSIT SUCCESSFUL!")
            print(f"💰 New Balance: ₹{acc['balance']}")
            return

    print("❌ Account not found. Please check the account number.")


def withdraw():
    print("\n--- WITHDRAW MONEY ---")
    acc_num = input("Enter your Account Number: ")

    try:
        amount = float(input("Enter amount to withdraw: ₹"))
        if amount <= 0:
            print("❌ Amount must be greater than zero.")
            return
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    accounts = load_accounts()

    for acc in accounts:
        if acc["account_number"] == acc_num:
            # Check if it's a Savings Account with minimum balance
            if acc["account_type"] == "SavingsAccount":
                min_balance = 100.0
                if acc["balance"] - amount < min_balance:
                    print(f"❌ Cannot withdraw. Savings account must maintain a minimum balance of ₹{min_balance}.")
                    print(f"   Current balance: ₹{acc['balance']}")
                    print(f"   Maximum withdrawable: ₹{acc['balance'] - min_balance}")
                    return

            # Check regular sufficient balance
            if acc["balance"] < amount:
                print(f"❌ Insufficient balance. Current balance: ₹{acc['balance']}")
                return

            # Perform the withdrawal
            acc["balance"] -= amount
            save_accounts(accounts)

            # Log transaction
            txn = Transaction(
                account_number=acc_num,
                transaction_type=TransactionType.WITHDRAWAL,
                amount=amount,
                balance_after=acc["balance"],
                description="Cash withdrawal"
            )
            transactions = load_transactions()
            transactions.append(txn.to_dict())
            save_transactions(transactions)

            print("\n✅ WITHDRAWAL SUCCESSFUL!")
            print(f"💰 New Balance: ₹{acc['balance']}")
            return

    print("❌ Account not found. Please check the account number.")


def transfer():
    print("\n--- TRANSFER FUNDS ---")
    sender_acc_num = input("Enter your Account Number (Sender): ")
    receiver_acc_num = input("Enter receiver's Account Number: ")

    if sender_acc_num == receiver_acc_num:
        print("❌ Cannot transfer to the same account.")
        return

    try:
        amount = float(input("Enter amount to transfer: ₹"))
        if amount <= 0:
            print("❌ Amount must be greater than zero.")
            return
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    accounts = load_accounts()
    
    sender = next((acc for acc in accounts if acc["account_number"] == sender_acc_num), None)
    receiver = next((acc for acc in accounts if acc["account_number"] == receiver_acc_num), None)

    if not sender:
        print("❌ Sender account not found.")
        return
    if not receiver:
        print("❌ Receiver account not found.")
        return

    # Check sender balance based on account type
    if sender["account_type"] == "SavingsAccount":
        if sender["balance"] - amount < 100.0:
            print("❌ Transfer failed. Savings account must maintain a minimum balance of ₹100.0.")
            return
    else: # CurrentAccount
        if sender["balance"] - amount < -500.0:
            print("❌ Transfer failed. Overdraft limit exceeded.")
            return

    # Perform transfer
    sender["balance"] -= amount
    receiver["balance"] += amount
    save_accounts(accounts)

    # Log transactions
    transactions = load_transactions()
    
    # Sender transaction
    txn_out = Transaction(
        account_number=sender_acc_num,
        transaction_type=TransactionType.TRANSFER_SENT,
        amount=amount,
        balance_after=sender["balance"],
        description=f"Transfer to {receiver_acc_num}",
        related_account=receiver_acc_num
    )
    transactions.append(txn_out.to_dict())

    # Receiver transaction
    txn_in = Transaction(
        account_number=receiver_acc_num,
        transaction_type=TransactionType.TRANSFER_RECEIVED,
        amount=amount,
        balance_after=receiver["balance"],
        description=f"Transfer from {sender_acc_num}",
        related_account=sender_acc_num
    )
    transactions.append(txn_in.to_dict())

    save_transactions(transactions)

    print("\n✅ TRANSFER SUCCESSFUL!")
    print(f"💰 Your New Balance: ₹{sender['balance']}")


def transaction_history():
    print("\n--- TRANSACTION HISTORY ---")
    acc_num = input("Enter your Account Number: ")

    accounts = load_accounts()
    if not any(acc["account_number"] == acc_num for acc in accounts):
        print("❌ Account not found.")
        return

    transactions = load_transactions()
    acc_txns = [txn for txn in transactions if txn["account_number"] == acc_num]

    if not acc_txns:
        print("No transactions found for this account.")
        return

    print(f"\nTransaction History for Account: {acc_num}")
    print("-" * 75)
    print(f"{'Date & Time':<22} | {'Type':<18} | {'Amount':<12} | {'Balance':<12}")
    print("-" * 75)
    
    for txn_data in acc_txns:
        txn = Transaction.from_dict(txn_data)
        # Assuming transaction format: [2023-01-01 12:00:00] TYPE +₹100 | Bal: ₹500
        # Instead, I'll print manually to make it tabular
        
        type_symbol = "+" if txn.transaction_type in (TransactionType.DEPOSIT, TransactionType.OPENING_DEPOSIT, TransactionType.TRANSFER_RECEIVED, TransactionType.INTEREST) else "-"
        
        print(f"{txn.timestamp:<22} | {txn.transaction_type.value.upper():<18} | {type_symbol}₹{txn.amount:<10.2f} | ₹{txn.balance_after:<10.2f}")
    
    print("-" * 75)


def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_logo()

        print("\n1. Create New Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer Funds")
        print("5. Check Balance")
        print("6. Transaction History")
        print("7. Exit")

        choice = input("\n👉 Enter your choice: ")

        if choice == "1":
            create_account()
            input("\nPress Enter to continue...")
        elif choice == "2":
            deposit()
            input("\nPress Enter to continue...")
        elif choice == "3":
            withdraw()
            input("\nPress Enter to continue...")
        elif choice == "4":
            transfer()
            input("\nPress Enter to continue...")
        elif choice == "5":
            check_balance()
            input("\nPress Enter to continue...")
        elif choice == "6":
            transaction_history()
            input("\nPress Enter to continue...")
        elif choice == "7":
            print("\nThank you for banking with Sushovan! 🏦")
            break
        else:
            print("❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()