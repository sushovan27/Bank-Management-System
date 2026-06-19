"""
Custom Exceptions for the banking system.
"""

class InsufficientFundsError(Exception):
    pass

class AccountNotFoundError(Exception):
    pass