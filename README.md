# Python Practice - Bank System

A simple console-based banking system written in Python to practice Object-Oriented Programming (OOP) and File I/O.

## Features Included
1. **Flashy Terminal UI**: Powered by the `rich` library, featuring styled tables, colored panels, and a sleek logo layout.
2. **PIN Authentication**: Secure your account! Creating an account requires setting a 4-digit PIN. Deposits, withdrawals, and history checks are protected by SHA-256 hashed PINs.
3. **Advanced Transaction History**:
    - Print detailed, color-coded, tabular transaction logs.
    - **Export Statements**: Automatically generate and export account statements to CSV format.
4. **Apply Interest (Admin)**: Apply a configurable interest rate (e.g., 4%) to all Savings accounts in bulk.
5. **Create Account**: Open a Savings or Current account.
6. **Deposit & Withdraw**: Robust rule validation including overdraft and minimum balance protection.
7. **Transfer Funds**: Move money seamlessly across accounts with transactional integrity.

## Prerequisites & How to Run
This project uses the `rich` library for an advanced UI experience.

1. Install requirements:
```bash
pip install rich
```

2. Navigate to the `bank_system` directory and execute `main.py`:

```bash
cd bank_system
python main.py
```

## Data Storage
The system automatically creates a `data` directory and stores `accounts.json` and `transactions.json` persistently.
