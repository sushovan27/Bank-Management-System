# Python Practice - Bank System

A simple console-based banking system written in Python to practice Object-Oriented Programming (OOP) and File I/O.

## Features Included
1. **Create Account**: Open a Savings or Current account.
2. **Deposit**: Add money to your account.
3. **Withdraw**: Take money out, with account-specific rules (minimum balance for savings, overdraft for current).
4. **Transfer Funds**: Move money between two accounts.
5. **Check Balance**: View current balance and account details.
6. **Transaction History**: View full history of deposits, withdrawals, and transfers with timestamps.

## Project Structure
- `bank_system/main.py`: Entry point and main CLI application.
- `bank_system/models/`: Contains data models (`Account`, `Customer`, `Transaction`).
- `bank_system/services/`: Directory for extracting business logic (extensible).
- `data/`: Auto-generated folder containing JSON storage for accounts and transactions.

## How to Run
Navigate to the `bank_system` directory and execute `main.py`:

```bash
cd bank_system
python main.py
```

## Data Storage
The system automatically creates a `data` directory and stores `accounts.json` and `transactions.json` persistently.
