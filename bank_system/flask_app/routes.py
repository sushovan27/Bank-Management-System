from flask import Blueprint, render_template, request, jsonify
from services.bank_service import BankService
from utils.exceptions import InsufficientFundsError, AccountNotFoundError

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/api/dashboard')
def dashboard_stats():
    stats = BankService.get_dashboard_stats()
    return jsonify(stats)


@main_bp.route('/api/create-account', methods=['POST'])
def create_account():
    data = request.get_json()
    try:
        result = BankService.create_account(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            address=data.get('address', ''),
            acc_type=data['account_type'],
            pin=data['pin'],
            initial_deposit=float(data['initial_deposit'])
        )
        return jsonify({"success": True, "account": result})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main_bp.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    acc = BankService.authenticate(data['account_number'], data['pin'])
    if acc:
        return jsonify({"success": True, "account": acc})
    return jsonify({"success": False, "error": "Invalid account number or PIN"}), 401


@main_bp.route('/api/balance', methods=['POST'])
def check_balance():
    data = request.get_json()
    acc = BankService.authenticate(data['account_number'], data['pin'])
    if acc:
        return jsonify({"success": True, "account": acc})
    return jsonify({"success": False, "error": "Invalid account number or PIN"}), 401


@main_bp.route('/api/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    acc = BankService.authenticate(data['account_number'], data['pin'])
    if not acc:
        return jsonify({"success": False, "error": "Invalid account number or PIN"}), 401
    try:
        result = BankService.deposit(data['account_number'], float(data['amount']))
        return jsonify({"success": True, **result})
    except (ValueError, AccountNotFoundError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main_bp.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    acc = BankService.authenticate(data['account_number'], data['pin'])
    if not acc:
        return jsonify({"success": False, "error": "Invalid account number or PIN"}), 401
    try:
        result = BankService.withdraw(data['account_number'], float(data['amount']))
        return jsonify({"success": True, **result})
    except (ValueError, AccountNotFoundError, InsufficientFundsError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main_bp.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    acc = BankService.authenticate(data['sender_account'], data['pin'])
    if not acc:
        return jsonify({"success": False, "error": "Invalid sender account number or PIN"}), 401
    try:
        result = BankService.transfer(
            data['sender_account'], data['receiver_account'], float(data['amount'])
        )
        return jsonify({"success": True, **result})
    except (ValueError, AccountNotFoundError, InsufficientFundsError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main_bp.route('/api/history', methods=['POST'])
def transaction_history():
    data = request.get_json()
    acc = BankService.authenticate(data['account_number'], data['pin'])
    if not acc:
        return jsonify({"success": False, "error": "Invalid account number or PIN"}), 401
    txns = BankService.get_transaction_history(data['account_number'])
    return jsonify({"success": True, "transactions": txns, "account": acc})


@main_bp.route('/api/apply-interest', methods=['POST'])
def apply_interest():
    data = request.get_json()
    try:
        count = BankService.apply_interest(data.get('admin_password', ''))
        return jsonify({"success": True, "count": count})
    except PermissionError:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
