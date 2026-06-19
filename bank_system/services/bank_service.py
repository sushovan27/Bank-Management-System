import json
import os
from typing import Optional
from datetime import datetime

from models.customer import Customer
from models.account import SavingsAccount, CurrentAccount, hash_pin
from models.transaction import Transaction, TransactionType, TransactionStatus
from utils.exceptions import InsufficientFundsError, AccountNotFoundError

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

os.makedirs(DATA_DIR, exist_ok=True)


class BankService:

    @staticmethod
    def load_accounts():
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_accounts(accounts):
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=4)

    @staticmethod
    def load_transactions():
        try:
            with open(TRANSACTIONS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_transactions(transactions):
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump(transactions, f, indent=4)

    @staticmethod
    def authenticate(account_num: str, pin: str) -> Optional[dict]:
        accounts = BankService.load_accounts()
        acc = next((a for a in accounts if a["account_number"] == account_num), None)
        if acc and acc.get("pin_hash") == hash_pin(pin):
            return acc
        return None

    @staticmethod
    def find_account(account_num: str) -> Optional[dict]:
        accounts = BankService.load_accounts()
        return next((a for a in accounts if a["account_number"] == account_num), None)

    @staticmethod
    def create_account(name: str, phone: str, email: str, address: str,
                       acc_type: str, pin: str, initial_deposit: float) -> dict:
        if len(pin) < 4 or not pin.isdigit():
            raise ValueError("PIN must be at least 4 digits")

        customer = Customer(name, phone, email, address)

        if acc_type == "SavingsAccount":
            if initial_deposit < 100:
                raise ValueError("Savings account requires a minimum deposit of ₹100")
            account = SavingsAccount(customer_id=customer.name, initial_deposit=initial_deposit, pin=pin)
        else:
            account = CurrentAccount(customer_id=customer.name, initial_deposit=initial_deposit, pin=pin)

        account_data = account.to_dict()
        account_data["customer"] = customer.to_dict()

        accounts = BankService.load_accounts()
        accounts.append(account_data)
        BankService.save_accounts(accounts)

        txn = Transaction(
            account_number=account.account_number,
            transaction_type=TransactionType.OPENING_DEPOSIT,
            amount=initial_deposit,
            balance_after=initial_deposit,
            description="Account opening deposit"
        )
        transactions = BankService.load_transactions()
        transactions.append(txn.to_dict())
        BankService.save_transactions(transactions)

        return account_data

    @staticmethod
    def deposit(account_num: str, amount: float) -> dict:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        accounts = BankService.load_accounts()
        acc = next((a for a in accounts if a["account_number"] == account_num), None)
        if not acc:
            raise AccountNotFoundError(f"Account {account_num} not found")

        acc["balance"] += amount
        BankService.save_accounts(accounts)

        txn = Transaction(
            account_number=account_num,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            balance_after=acc["balance"],
            description="Cash deposit"
        )
        transactions = BankService.load_transactions()
        transactions.append(txn.to_dict())
        BankService.save_transactions(transactions)

        return {"balance": acc["balance"], "transaction_id": txn.transaction_id}

    @staticmethod
    def withdraw(account_num: str, amount: float) -> dict:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        accounts = BankService.load_accounts()
        acc = next((a for a in accounts if a["account_number"] == account_num), None)
        if not acc:
            raise AccountNotFoundError(f"Account {account_num} not found")

        if acc["account_type"] == "SavingsAccount":
            if acc["balance"] - amount < 100.0:
                raise InsufficientFundsError("Minimum balance of ₹100 required")
        elif acc["account_type"] == "CurrentAccount":
            if acc["balance"] - amount < -500.0:
                raise InsufficientFundsError("Overdraft limit of ₹500 exceeded")
        else:
            if acc["balance"] - amount < 0:
                raise InsufficientFundsError("Insufficient balance")

        acc["balance"] -= amount
        BankService.save_accounts(accounts)

        txn = Transaction(
            account_number=account_num,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            balance_after=acc["balance"],
            description="Cash withdrawal"
        )
        transactions = BankService.load_transactions()
        transactions.append(txn.to_dict())
        BankService.save_transactions(transactions)

        return {"balance": acc["balance"], "transaction_id": txn.transaction_id}

    @staticmethod
    def transfer(sender_num: str, receiver_num: str, amount: float) -> dict:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if sender_num == receiver_num:
            raise ValueError("Cannot transfer to the same account")

        accounts = BankService.load_accounts()
        sender = next((a for a in accounts if a["account_number"] == sender_num), None)
        receiver = next((a for a in accounts if a["account_number"] == receiver_num), None)

        if not sender:
            raise AccountNotFoundError(f"Sender account {sender_num} not found")
        if not receiver:
            raise AccountNotFoundError(f"Receiver account {receiver_num} not found")

        if sender["account_type"] == "SavingsAccount":
            if sender["balance"] - amount < 100.0:
                raise InsufficientFundsError("Savings minimum balance rule")
        elif sender["account_type"] == "CurrentAccount":
            if sender["balance"] - amount < -500.0:
                raise InsufficientFundsError("Overdraft limit exceeded")
        else:
            if sender["balance"] - amount < 0:
                raise InsufficientFundsError("Insufficient balance")

        for a in accounts:
            if a["account_number"] == sender_num:
                a["balance"] -= amount
                new_sender_bal = a["balance"]
            if a["account_number"] == receiver_num:
                a["balance"] += amount
                new_receiver_bal = a["balance"]

        BankService.save_accounts(accounts)

        transactions = BankService.load_transactions()
        txn_sent = Transaction(
            sender_num, TransactionType.TRANSFER_SENT, amount, new_sender_bal,
            description=f"To {receiver_num}", related_account=receiver_num
        )
        txn_recv = Transaction(
            receiver_num, TransactionType.TRANSFER_RECEIVED, amount, new_receiver_bal,
            description=f"From {sender_num}", related_account=sender_num
        )
        transactions.append(txn_sent.to_dict())
        transactions.append(txn_recv.to_dict())
        BankService.save_transactions(transactions)

        return {"balance": new_sender_bal, "sender_txn_id": txn_sent.transaction_id}

    @staticmethod
    def apply_interest(admin_password: str) -> int:
        if admin_password != "admin123":
            raise PermissionError("Unauthorized")

        accounts = BankService.load_accounts()
        transactions = BankService.load_transactions()
        count = 0

        for acc in accounts:
            if acc["account_type"] == "SavingsAccount":
                interest = acc["balance"] * 0.04
                acc["balance"] += interest
                count += 1
                transactions.append(Transaction(
                    acc["account_number"], TransactionType.INTEREST, interest, acc["balance"],
                    description="Annual Interest 4%"
                ).to_dict())

        BankService.save_accounts(accounts)
        BankService.save_transactions(transactions)
        return count

    @staticmethod
    def get_transaction_history(account_num: str) -> list:
        transactions = BankService.load_transactions()
        return [txn for txn in transactions if txn["account_number"] == account_num]

    @staticmethod
    def get_dashboard_stats() -> dict:
        accounts = BankService.load_accounts()
        transactions = BankService.load_transactions()

        total_accounts = len(accounts)
        total_balance = sum(a.get('balance', 0) for a in accounts)
        total_transactions = len(transactions)
        savings_count = sum(1 for a in accounts if a.get("account_type") == "SavingsAccount")
        current_count = total_accounts - savings_count
        avg_balance = total_balance / total_accounts if total_accounts > 0 else 0

        recent_txns = sorted(transactions, key=lambda x: x['timestamp'], reverse=True)[:10]

        return {
            "total_accounts": total_accounts,
            "total_balance": total_balance,
            "total_transactions": total_transactions,
            "savings_count": savings_count,
            "current_count": current_count,
            "avg_balance": avg_balance,
            "recent_transactions": recent_txns,
        }
