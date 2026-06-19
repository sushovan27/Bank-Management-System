const API = {
    async get(url) {
        const res = await fetch(url);
        return res.json();
    },
    async post(url, data) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const json = await res.json();
        if (!res.ok && !json.success) throw new Error(json.error || 'Request failed');
        return json;
    }
};

const Toast = {
    container: null,
    init() {
        this.container = document.getElementById('toast-container');
    },
    show(message, type = 'info') {
        const el = document.createElement('div');
        el.className = `toast ${type}`;
        const icons = { success: '✅', error: '❌', info: 'ℹ️' };
        el.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span><button class="toast-close" onclick="this.parentElement.remove()">&times;</button>`;
        this.container.appendChild(el);
        setTimeout(() => { el.remove(); }, 5000);
    },
    success(m) { this.show(m, 'success'); },
    error(m) { this.show(m, 'error'); },
    info(m) { this.show(m, 'info'); }
};

function $(id) { return document.getElementById(id); }

function navTo(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const section = $(sectionId);
    if (section) section.classList.add('active');
    const nav = document.querySelector(`.nav-item[data-section="${sectionId}"]`);
    if (nav) nav.classList.add('active');
}

async function loadDashboard() {
    try {
        const data = await API.get('/api/dashboard');
        $('stat-total-accounts').textContent = data.total_accounts;
        $('stat-total-balance').textContent = `₹${Number(data.total_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        $('stat-total-transactions').textContent = data.total_transactions;
        $('stat-avg-balance').textContent = `₹${Number(data.avg_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        $('recent-activity').innerHTML = data.recent_transactions.length
            ? data.recent_transactions.map(t => {
                const isCredit = ['deposit', 'opening_deposit', 'transfer_received', 'interest'].includes(t.transaction_type);
                const cls = isCredit ? 'credit' : 'debit';
                const sym = isCredit ? '+' : '-';
                const label = t.transaction_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                return `<div class="activity-item ${cls}">
                    <span class="activity-time">${t.timestamp}</span>
                    <span class="activity-account">${t.account_number}</span>
                    <span class="activity-type">${label}</span>
                    <span class="activity-amount ${cls}">${sym}₹${Number(t.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>`;
            }).join('')
            : '<div class="empty-state"><p>No recent activity</p></div>';
        if (data.total_accounts > 0) {
            renderAccountChart(data.savings_count, data.current_count);
        }
        if (data.total_transactions > 0) {
            renderTxnTypeChart(data.recent_transactions);
        }
    } catch (e) {
        Toast.error('Failed to load dashboard: ' + e.message);
    }
}

function renderAccountChart(savings, current) {
    const canvas = $('chart-accounts');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);
    const w = rect.width, h = rect.height;
    const total = savings + current;
    const savingsPct = total ? savings / total : 0;
    const currentPct = total ? current / total : 0;
    const cx = w / 2, cy = h / 2, r = Math.min(w, h) / 2 - 30;
    ctx.clearRect(0, 0, w, h);
    if (total === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No data', cx, cy + 5);
        return;
    }
    const colors = ['#10b981', '#f59e0b'];
    const labels = [`Savings (${savings})`, `Current (${current})`];
    const pcts = [savingsPct, currentPct];
    let startAngle = -Math.PI / 2;
    const gap = 0.02;
    const totalAngle = 2 * Math.PI - gap * pcts.filter(p => p > 0).length;
    pcts.forEach((pct, i) => {
        if (pct === 0) return;
        const angle = pct * totalAngle;
        ctx.beginPath();
        ctx.arc(cx, cy, r, startAngle, startAngle + angle - gap);
        ctx.strokeStyle = colors[i];
        ctx.lineWidth = 24;
        ctx.lineCap = 'round';
        ctx.stroke();
        const midAngle = startAngle + (angle - gap) / 2;
        const lx = cx + Math.cos(midAngle) * (r + 18);
        const ly = cy + Math.sin(midAngle) * (r + 18);
        ctx.fillStyle = colors[i];
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.textAlign = lx > cx ? 'left' : 'right';
        ctx.fillText(labels[i], lx, ly + 4);
        const valX = cx + Math.cos(midAngle) * (r * 0.55);
        const valY = cy + Math.sin(midAngle) * (r * 0.55) + 4;
        ctx.fillText(`${(pct * 100).toFixed(1)}%`, valX, valY);
        startAngle += angle;
    });
    ctx.fillStyle = '#f1f5f9';
    ctx.font = 'bold 22px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(total, cx, cy + 8);
    ctx.font = '10px Inter, sans-serif';
    ctx.fillStyle = '#64748b';
    ctx.fillText('Total', cx, cy + 22);
}

function renderTxnTypeChart(txns) {
    const canvas = $('chart-transactions');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);
    const w = rect.width, h = rect.height;
    const counts = {};
    txns.forEach(t => { const k = t.transaction_type; counts[k] = (counts[k] || 0) + 1; });
    const entries = Object.entries(counts);
    ctx.clearRect(0, 0, w, h);
    if (!entries.length) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No data', w / 2, h / 2 + 5);
        return;
    }
    const colors = { deposit: '#10b981', withdrawal: '#ef4444', transfer_sent: '#f59e0b', transfer_received: '#3b82f6', interest: '#8b5cf6', opening_deposit: '#06b6d4' };
    const maxVal = Math.max(...entries.map(e => e[1]));
    const barWidth = Math.min(36, (w - 60) / entries.length);
    const gap = 12;
    const totalBarsWidth = entries.length * barWidth + (entries.length - 1) * gap;
    let startX = (w - totalBarsWidth) / 2;
    const chartH = h - 60;
    entries.forEach(([type, count]) => {
        const barH = (count / maxVal) * chartH;
        const x = startX;
        const y = h - 40 - barH;
        ctx.fillStyle = colors[type] || '#94a3b8';
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barH, [4, 4, 0, 0]);
        ctx.fill();
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(count, x + barWidth / 2, y - 6);
        const label = type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        ctx.save();
        ctx.translate(x + barWidth / 2, h - 14);
        ctx.rotate(-0.4);
        ctx.fillStyle = '#64748b';
        ctx.font = '9px Inter, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(label, 0, 0);
        ctx.restore();
        startX += barWidth + gap;
    });
}

document.querySelectorAll('.nav-item[data-section]').forEach(item => {
    item.addEventListener('click', () => {
        const sectionId = item.dataset.section;
        navTo(sectionId);
        if (sectionId === 'section-home') loadDashboard();
    });
});

// Create Account
$('create-account-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: $('ca-name').value.trim(),
        phone: $('ca-phone').value.trim(),
        email: $('ca-email').value.trim(),
        address: $('ca-address').value.trim(),
        account_type: $('ca-type').value,
        pin: $('ca-pin').value,
        initial_deposit: $('ca-deposit').value
    };
    if (!data.name || !data.phone || !data.email || !data.pin || !data.initial_deposit) {
        return Toast.error('Please fill all required fields');
    }
    if (data.pin !== $('ca-pin2').value) return Toast.error('PINs do not match');
    if (data.pin.length < 4 || !/^\d+$/.test(data.pin)) return Toast.error('PIN must be at least 4 digits');
    if (data.account_type === 'SavingsAccount' && parseFloat(data.initial_deposit) < 100) {
        return Toast.error('Savings account needs minimum ₹100 deposit');
    }
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    btn.textContent = 'Creating...';
    try {
        const res = await API.post('/api/create-account', data);
        Toast.success('Account created successfully!');
        const acc = res.account;
        $('ca-success').classList.remove('hidden');
        $('ca-success-acc').textContent = acc.account_number;
        $('ca-success-name').textContent = data.name;
        $('ca-success-type').textContent = data.account_type === 'SavingsAccount' ? 'Savings' : 'Current';
        $('ca-success-balance').textContent = `₹${Number(acc.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        e.target.reset();
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
    btn.textContent = '🚀 Create Account';
});

// Check Balance
$('balance-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = { account_number: $('b-acc').value.trim(), pin: $('b-pin').value };
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    try {
        const res = await API.post('/api/balance', data);
        const a = res.account;
        $('b-result').classList.remove('hidden');
        $('b-balance').textContent = `₹${Number(a.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        $('b-type').textContent = a.account_type.replace('Account', '');
        $('b-name').textContent = a.customer.name;
        $('b-date').textContent = a.opening_date;
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
});

// Deposit
$('deposit-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = { account_number: $('d-acc').value.trim(), pin: $('d-pin').value, amount: $('d-amount').value };
    if (parseFloat(data.amount) <= 0) return Toast.error('Amount must be positive');
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    try {
        const res = await API.post('/api/deposit', data);
        Toast.success(`Deposit successful! New balance: ₹${Number(res.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`);
        e.target.reset();
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
});

// Withdraw
$('withdraw-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = { account_number: $('w-acc').value.trim(), pin: $('w-pin').value, amount: $('w-amount').value };
    if (parseFloat(data.amount) <= 0) return Toast.error('Amount must be positive');
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    try {
        const res = await API.post('/api/withdraw', data);
        Toast.success(`Withdrawal successful! New balance: ₹${Number(res.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`);
        e.target.reset();
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
});

// Transfer
$('transfer-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        sender_account: $('t-sender').value.trim(),
        pin: $('t-pin').value,
        receiver_account: $('t-receiver').value.trim(),
        amount: $('t-amount').value
    };
    if (parseFloat(data.amount) <= 0) return Toast.error('Amount must be positive');
    if (data.sender_account === data.receiver_account) return Toast.error('Cannot transfer to same account');
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    try {
        const res = await API.post('/api/transfer', data);
        Toast.success(`Transfer successful! Your balance: ₹${Number(res.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`);
        e.target.reset();
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
});

// Transaction History
$('history-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = { account_number: $('h-acc').value.trim(), pin: $('h-pin').value };
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    try {
        const res = await API.post('/api/history', data);
        const txns = res.transactions;
        const container = $('h-result');
        container.classList.remove('hidden');
        if (!txns.length) {
            container.innerHTML = '<div class="empty-state"><p>No transactions found</p></div>';
        } else {
            let html = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <span style="color:var(--text-secondary);font-size:13px;">${txns.length} transaction(s) found</span>
                <button class="btn btn-secondary" onclick="exportCSV('${data.account_number}')">📥 Export CSV</button>
            </div>`;
            html += '<div class="table-wrapper"><table><thead><tr><th>Date & Time</th><th>Transaction ID</th><th>Type</th><th>Amount</th><th>Balance</th><th>Description</th></tr></thead><tbody>';
            txns.forEach(t => {
                const isCredit = ['deposit', 'opening_deposit', 'transfer_received', 'interest'].includes(t.transaction_type);
                const sym = isCredit ? '+' : '-';
                const color = isCredit ? 'var(--accent-green)' : 'var(--accent-red)';
                const label = t.transaction_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                html += `<tr>
                    <td style="white-space:nowrap">${t.timestamp}</td>
                    <td style="font-family:monospace;font-size:12px">${t.transaction_id}</td>
                    <td>${label}</td>
                    <td style="color:${color};font-weight:600">${sym}₹${Number(t.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td>₹${Number(t.balance_after).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td>${t.description || ''}</td>
                </tr>`;
            });
            html += '</tbody></table></div>';
            container.innerHTML = html;
            window._historyTxns = txns;
            window._historyAccount = data.account_number;
        }
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
});

function exportCSV(accountNum) {
    const txns = window._historyTxns || [];
    if (!txns.length) return;
    const headers = ['Date', 'Transaction ID', 'Type', 'Amount', 'Balance After', 'Description'];
    const rows = txns.map(t => [t.timestamp, t.transaction_id, t.transaction_type, t.amount, t.balance_after, t.description || '']);
    let csv = headers.join(',') + '\n' + rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `statement_${accountNum}_${new Date().toISOString().slice(0,10).replace(/-/g,'')}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
    Toast.success('CSV downloaded');
}

// Admin
$('admin-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const password = $('admin-password').value;
    const btn = e.target.querySelector('.btn');
    btn.disabled = true;
    try {
        const res = await API.post('/api/apply-interest', { admin_password: password });
        Toast.success(`Interest applied to ${res.count} savings account(s)`);
    } catch (e) {
        Toast.error(e.message);
    }
    btn.disabled = false;
});

// Init
document.addEventListener('DOMContentLoaded', () => {
    Toast.init();
    navTo('section-home');
    loadDashboard();
});
