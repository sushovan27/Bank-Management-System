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
This project uses the `rich` library for the CLI UI and `streamlit` for the Web UI.

1. Install requirements:
```bash
pip install rich streamlit pandas
```

2. To run the Terminal CLI Application:
```bash
cd bank_system
python main.py
```

3. To run the Web UI Application:
```bash
cd bank_system
streamlit run app.py
```

## Data Storage
The system automatically creates a `data` directory and stores `accounts.json` and `transactions.json` persistently.
