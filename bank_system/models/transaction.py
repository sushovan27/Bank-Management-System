"""
Transaction Model Module

This module defines the Transaction class and related enums for tracking
all financial transactions in the banking system.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Optional, Dict, Any


class TransactionType(Enum):
    """Enumeration of transaction types."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_SENT = "transfer_sent"
    TRANSFER_RECEIVED = "transfer_received"
    INTEREST = "interest"
    FEE = "fee"
    OPENING_DEPOSIT = "opening_deposit"


class TransactionStatus(Enum):
    """Enumeration of transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


@dataclass
class Transaction:
    """
    Represents a single financial transaction.

    Attributes:
        transaction_id: Unique identifier for the transaction
        account_number: Account number involved in the transaction
        transaction_type: Type of transaction (deposit, withdrawal, etc.)
        amount: Transaction amount
        balance_after: Account balance after transaction
        status: Current status of the transaction
        timestamp: When the transaction occurred
        description: Optional description/memo
        related_account: For transfers, the other account number
        metadata: Additional data (fees, interest rate, etc.)
    """
    account_number: str
    transaction_type: TransactionType
    amount: float
    balance_after: float
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12].upper())
    status: TransactionStatus = TransactionStatus.COMPLETED
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    description: str = ""
    related_account: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate transaction data after initialization."""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for JSON serialization."""
        return {
            "transaction_id": self.transaction_id,
            "account_number": self.account_number,
            "transaction_type": self.transaction_type.value,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "description": self.description,
            "related_account": self.related_account,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create Transaction object from dictionary."""
        return cls(
            transaction_id=data["transaction_id"],
            account_number=data["account_number"],
            transaction_type=TransactionType(data["transaction_type"]),
            amount=data["amount"],
            balance_after=data["balance_after"],
            status=TransactionStatus(data.get("status", "completed")),
            timestamp=data["timestamp"],
            description=data.get("description", ""),
            related_account=data.get("related_account"),
            metadata=data.get("metadata", {})
        )

    def __str__(self) -> str:
        """Return formatted string representation."""
        type_symbol = {
            TransactionType.DEPOSIT: "+",
            TransactionType.WITHDRAWAL: "-",
            TransactionType.TRANSFER_SENT: "→",
            TransactionType.TRANSFER_RECEIVED: "←",
            TransactionType.INTEREST: "+",
            TransactionType.FEE: "-",
            TransactionType.OPENING_DEPOSIT: "+"
        }.get(self.transaction_type, "")

        return (f"[{self.timestamp}] {self.transaction_type.value.upper():<20} "
                f"{type_symbol}₹{self.amount:>10.2f} | Bal: ₹{self.balance_after:>10.2f} "
                f"| {self.transaction_id}")