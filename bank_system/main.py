import os
import json
import csv
import getpass
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text

from models.customer import Customer
from models.account import SavingsAccount, CurrentAccount, hash_pin
from models.transaction import Transaction, TransactionType

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

DATA_FILE = "data/accounts.json"
TRANSACTIONS_FILE = "data/transactions.json"

console = Console()

def display_logo():
    logo = """
    ███████╗██╗   ██╗███████╗██╗  ██╗ ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗
    ██╔════╝██║   ██║██╔════╝██║  ██║██╔═══██╗██║   ██║██╔══██╗████╗  ██║
    ███████╗██║   ██║███████╗███████║██║   ██║██║   ██║███████║██╔██╗ ██║
    ╚════██║██║   ██║╚════██║██╔══██║██║   ██║╚██╗ ██╔╝██╔══██║██║╚██╗██║
    ███████║╚██████╔╝███████║██║  ██║╚██████╔╝ ╚████╔╝ ██║  ██║██║ ╚████║
    ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝
    """
    tagline = Text("💰  SECURE  •  TRUSTED  •  RELIABLE  💰", style="bold green")
    panel = Panel(Align.center(Text(logo, style="bold cyan") + "\n" + tagline), title="[bold yellow]Welcome to NextGen Banking[/bold yellow]", border_style="cyan")
    console.print(panel)


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

def authenticate(account_num, accounts):
    """Returns the account dict if authenticated, else None."""
    acc = next((a for a in accounts if a["account_number"] == account_num), None)
    if not acc:
        console.print("[bold red]❌ Account not found.[/bold red]")
        return None
    
    pin = getpass.getpass("Enter 4-digit PIN: ")
    if acc.get("pin_hash") == hash_pin(pin):
        return acc
    else:
        console.print("[bold red]❌ Incorrect PIN.[/bold red]")
        return None

def create_account():
    console.print(Panel("[bold green]--- CREATE NEW ACCOUNT ---[/bold green]"))
    name = Prompt.ask("Enter Full Name")
    phone = Prompt.ask("Enter Phone Number")
    email = Prompt.ask("Enter Email")
    address = Prompt.ask("Enter Address (optional)")

    console.print("\n[bold cyan]Account Types:[/bold cyan]")
    console.print("1. Savings (Minimum balance: ₹100, 4% Interest)")
    console.print("2. Current (Overdraft up to ₹500)")
    acc_type = Prompt.ask("Choose account type", choices=["1", "2"])

    while True:
        pin = getpass.getpass("Set a 4-digit PIN: ")
        pin2 = getpass.getpass("Confirm PIN: ")
        if pin == pin2 and len(pin) >= 4:
            break
        console.print("[bold red]❌ PINs do not match or too short. Try again.[/bold red]")

    try:
        initial_deposit = float(Prompt.ask("Enter Initial Deposit Amount (₹)"))
    except ValueError:
        console.print("[bold red]❌ Invalid amount.[/bold red]")
        return

    customer = Customer(name, phone, email, address)

    if acc_type == "1":
        account = SavingsAccount(customer_id=customer.name, initial_deposit=initial_deposit, pin=pin)
        if initial_deposit < 100:
            console.print("[bold red]❌ Savings account requires a minimum deposit of ₹100.[/bold red]")
            return
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

    success_panel = Panel(f"[bold green]✅ ACCOUNT CREATED SUCCESSFULLY![/bold green]\n"
                          f"📌 Account Number: [bold cyan]{account.account_number}[/bold cyan]\n"
                          f"💰 Current Balance: [bold green]₹{account.balance}[/bold green]\n"
                          f"📅 Opening Date: {account.opening_date}")
    console.print(success_panel)


def check_balance():
    console.print("\n[bold blue]--- CHECK BALANCE ---[/bold blue]")
    acc_num = Prompt.ask("Enter your Account Number")
    accounts = load_accounts()
    
    acc = authenticate(acc_num, accounts)
    if acc:
        table = Table(title="Account Details", show_header=True, header_style="bold magenta")
        table.add_column("Attribute", style="dim", width=20)
        table.add_column("Value")
        
        table.add_row("Customer", acc['customer']['name'])
        table.add_row("Account Type", acc['account_type'])
        table.add_row("Current Balance", f"[bold green]₹{acc['balance']:,.2f}[/bold green]")
        table.add_row("Opened on", acc['opening_date'])
        
        console.print(table)


def deposit():
    console.print("\n[bold blue]--- DEPOSIT MONEY ---[/bold blue]")
    acc_num = Prompt.ask("Enter your Account Number")
    accounts = load_accounts()
    
    acc = authenticate(acc_num, accounts)
    if not acc: return

    try:
        amount = float(Prompt.ask("Enter amount to deposit (₹)"))
        if amount <= 0: raise ValueError
    except ValueError:
        console.print("[bold red]❌ Invalid amount.[/bold red]")
        return

    acc["balance"] += amount
    save_accounts(accounts)

    txn = Transaction(account_number=acc_num, transaction_type=TransactionType.DEPOSIT,
                      amount=amount, balance_after=acc["balance"], description="Cash deposit")
    transactions = load_transactions()
    transactions.append(txn.to_dict())
    save_transactions(transactions)

    console.print(f"[bold green]✅ DEPOSIT SUCCESSFUL! New Balance: ₹{acc['balance']:,.2f}[/bold green]")


def withdraw():
    console.print("\n[bold blue]--- WITHDRAW MONEY ---[/bold blue]")
    acc_num = Prompt.ask("Enter your Account Number")
    accounts = load_accounts()
    
    acc = authenticate(acc_num, accounts)
    if not acc: return

    try:
        amount = float(Prompt.ask("Enter amount to withdraw (₹)"))
        if amount <= 0: raise ValueError
    except ValueError:
        console.print("[bold red]❌ Invalid amount.[/bold red]")
        return

    if acc["account_type"] == "SavingsAccount":
        if acc["balance"] - amount < 100.0:
            console.print(f"[bold red]❌ Cannot withdraw. Minimum balance of ₹100 required.[/bold red]")
            return
    else:
        if acc["balance"] - amount < -500.0:
            console.print(f"[bold red]❌ Insufficient balance. Overdraft limit exceeded.[/bold red]")
            return

    acc["balance"] -= amount
    save_accounts(accounts)

    txn = Transaction(account_number=acc_num, transaction_type=TransactionType.WITHDRAWAL,
                      amount=amount, balance_after=acc["balance"], description="Cash withdrawal")
    transactions = load_transactions()
    transactions.append(txn.to_dict())
    save_transactions(transactions)

    console.print(f"[bold green]✅ WITHDRAWAL SUCCESSFUL! New Balance: ₹{acc['balance']:,.2f}[/bold green]")


def transfer():
    console.print("\n[bold blue]--- TRANSFER FUNDS ---[/bold blue]")
    sender_acc_num = Prompt.ask("Enter your Account Number (Sender)")
    accounts = load_accounts()
    
    sender = authenticate(sender_acc_num, accounts)
    if not sender: return

    receiver_acc_num = Prompt.ask("Enter receiver's Account Number")
    if sender_acc_num == receiver_acc_num:
        console.print("[bold red]❌ Cannot transfer to the same account.[/bold red]")
        return
        
    receiver = next((a for a in accounts if a["account_number"] == receiver_acc_num), None)
    if not receiver:
        console.print("[bold red]❌ Receiver account not found.[/bold red]")
        return

    try:
        amount = float(Prompt.ask("Enter amount to transfer (₹)"))
        if amount <= 0: raise ValueError
    except ValueError:
        console.print("[bold red]❌ Invalid amount.[/bold red]")
        return

    if sender["account_type"] == "SavingsAccount" and sender["balance"] - amount < 100.0:
        console.print("[bold red]❌ Transfer failed. Savings minimum balance rule.[/bold red]")
        return
    elif sender["account_type"] == "CurrentAccount" and sender["balance"] - amount < -500.0:
        console.print("[bold red]❌ Transfer failed. Overdraft limit exceeded.[/bold red]")
        return

    sender["balance"] -= amount
    receiver["balance"] += amount
    save_accounts(accounts)

    transactions = load_transactions()
    transactions.append(Transaction(sender_acc_num, TransactionType.TRANSFER_SENT, amount, sender["balance"], description=f"To {receiver_acc_num}", related_account=receiver_acc_num).to_dict())
    transactions.append(Transaction(receiver_acc_num, TransactionType.TRANSFER_RECEIVED, amount, receiver["balance"], description=f"From {sender_acc_num}", related_account=sender_acc_num).to_dict())
    save_transactions(transactions)

    console.print(f"[bold green]✅ TRANSFER SUCCESSFUL! Your New Balance: ₹{sender['balance']:,.2f}[/bold green]")

def apply_interest():
    console.print("\n[bold blue]--- APPLY INTEREST (Admin) ---[/bold blue]")
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
    console.print(f"[bold green]✅ Applied 4% interest to {count} Savings Account(s).[/bold green]")


def transaction_history():
    console.print("\n[bold blue]--- TRANSACTION HISTORY ---[/bold blue]")
    acc_num = Prompt.ask("Enter your Account Number")
    accounts = load_accounts()
    
    acc = authenticate(acc_num, accounts)
    if not acc: return

    transactions = load_transactions()
    acc_txns = [txn for txn in transactions if txn["account_number"] == acc_num]

    if not acc_txns:
        console.print("[bold yellow]No transactions found for this account.[/bold yellow]")
        return

    table = Table(title=f"Transaction History: {acc_num}", header_style="bold cyan")
    table.add_column("Date & Time", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Amount", justify="right")
    table.add_column("Balance", justify="right")

    for txn_data in acc_txns:
        txn = Transaction.from_dict(txn_data)
        color = "green" if txn.transaction_type in (TransactionType.DEPOSIT, TransactionType.OPENING_DEPOSIT, TransactionType.TRANSFER_RECEIVED, TransactionType.INTEREST) else "red"
        symbol = "+" if color == "green" else "-"
        table.add_row(txn.timestamp, txn.transaction_type.value.upper(), f"[{color}]{symbol}₹{txn.amount:,.2f}[/{color}]", f"₹{txn.balance_after:,.2f}")
    
    console.print(table)
    
    if Prompt.ask("Export Statement to CSV?", choices=["y", "n"], default="n") == "y":
        filename = f"statement_{acc_num}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
        filepath = os.path.join("data", filename)
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Transaction ID", "Type", "Amount", "Balance After", "Description"])
            for t in acc_txns:
                writer.writerow([t["timestamp"], t["transaction_id"], t["transaction_type"], t["amount"], t["balance_after"], t["description"]])
        console.print(f"[bold green]✅ Statement exported to {filepath}[/bold green]")


def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_logo()

        console.print("\n[bold]Main Menu[/bold]")
        console.print("1. [cyan]Create New Account[/cyan]")
        console.print("2. [cyan]Deposit[/cyan]")
        console.print("3. [cyan]Withdraw[/cyan]")
        console.print("4. [cyan]Transfer Funds[/cyan]")
        console.print("5. [cyan]Check Balance[/cyan]")
        console.print("6. [cyan]Transaction History & Export[/cyan]")
        console.print("7. [magenta]Admin: Apply Interest (Savings)[/magenta]")
        console.print("8. [red]Exit[/red]")

        choice = Prompt.ask("\n👉 Enter your choice", choices=[str(i) for i in range(1, 9)])

        if choice == "1":
            create_account()
        elif choice == "2":
            deposit()
        elif choice == "3":
            withdraw()
        elif choice == "4":
            transfer()
        elif choice == "5":
            check_balance()
        elif choice == "6":
            transaction_history()
        elif choice == "7":
            apply_interest()
        elif choice == "8":
            console.print("\n[bold green]Thank you for banking with NextGen! 🏦[/bold green]")
            break
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()