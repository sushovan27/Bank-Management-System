from abc import ABC, abstractmethod
import uuid
import json
from datetime import datetime

class Account(ABC):
    def __init__(self, customer_id, initial_deposit=0):
        self.account_number = str(uuid.uuid4())[:8]  # Unique 8-digit ID
        self.customer_id = customer_id
        self.balance = float(initial_deposit)
        self.is_active = True
        self.opening_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def withdraw(self, amount):
        """Each account type has its own withdrawal rules"""
        pass

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "customer_id": self.customer_id,
            "balance": self.balance,
            "is_active": self.is_active,
            "opening_date": self.opening_date,
            "account_type": self.__class__.__name__  # Saves "SavingsAccount"
        }

class SavingsAccount(Account):
    def __init__(self, customer_id, initial_deposit=0):
        super().__init__(customer_id, initial_deposit)
        self.min_balance = 100.0  # Minimum balance rule

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        if self.balance - amount < self.min_balance:
            return False, f"Cannot withdraw. Minimum balance of ₹{self.min_balance} required."
        self.balance -= amount
        return True, "Withdrawal successful."

class CurrentAccount(Account):
    def __init__(self, customer_id, initial_deposit=0):
        super().__init__(customer_id, initial_deposit)
        self.overdraft_limit = 500.0  # Can go slightly negative

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        if self.balance - amount < -self.overdraft_limit:
            return False, f"Cannot withdraw. Overdraft limit of ₹{self.overdraft_limit} exceeded."
        self.balance -= amount
        return True, "Withdrawal successful."