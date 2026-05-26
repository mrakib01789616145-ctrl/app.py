from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_final_master_v4"

# ১. ডাটাবেজ সেটআপ
def init_db():
    conn = sqlite3.connect('applex_v4.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      first_name TEXT, last_name TEXT, email TEXT UNIQUE, 
                      phone TEXT, password TEXT, 
                      refer_bal REAL DEFAULT 0.0, salary_bal REAL DEFAULT 0.0,
                      job_bal REAL DEFAULT 0.0, total_earn REAL DEFAULT 0.0,
                      total_withdraw REAL DEFAULT 0.0, free_earn REAL DEFAULT 0.0,
                      level TEXT DEFAULT 'Free')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS deposits 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, trxid TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS withdraws 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, number TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ২. ডিজাইন টেমপ্লেট
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Earning Site</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .header { background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 24px; font-weight: bold; }
        .logo i { color: var(--primary); }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        .card { background: white; border-radius: 15px; padding: 20px; margin-top: 15px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        
        .balance-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px; }
        .bal-box { background: white; padding: 12px 5px; border-radius: 12px; text-align: center; border: 1px solid #ddd; }
        .bal-box b { font-size: 13px; color: #333; }
        .bal-box p { margin: 5px 0 0; color: var(--blue); font-weight: bold; font-size: 11px; }

        .input-field { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; outline: none; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }

        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #ddd; z-index: 100; }
        .nav-item { text-align: center; color: #666; text-decoration: none; font-size: 11px; flex: 1; }
        .nav-item i { font-size: 20px; margin-bottom: 3px; }
        .nav-item.active { color: var(--blue); }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-apple-alt"></i> APPLEX</div>
        <div><i class="fas fa-search"></i> &nbsp; <i class="fas fa-bell"></i></div>
    </div>
    <div class="container">
        <h3>Dashboard</h3>
        <p style="font-size:13px; margin-top:-10px;">Welcome, <b>{{ user[1] }}</b> | Level: <span style="color:green;">{{ user[12] }}</span></p>
        <div class="balance-grid">
            <div class="bal-box"><b>Tk. {{ user[6] }}</b><p>Refer</p></div>
            <div class="bal-box"><b>Tk. {{ user[7] }}</b><p>Salary</p></div>
            <div class="bal-box"><b>Tk. {{ user[8] }}</b><p>Job</p></div>
            <div class="bal-box"><b>Tk. {{ user[9] }}</b><p>Total Earn</p></div>
            <div class="bal-box"><b>Tk. {{ user[10] }}</b><p>Withdraw</p></div>
            <div class="bal-box"><b>Tk. {{ user[11] }}</b><p>Free Earn</p></div>
        </div>
        <div class="card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
            <h4>True Level (৳ ১০০)</h4>
            <p style="font-size:13px;">প্রতিদিন ৫টি টাস্ক এবং মাসিক ইনকাম সুবিধা পান।</p>
            <a href="/deposit" style="text-decoration:none;"><button style="background:white; color:#764ba2; border:none; padding:10px 20px; border-radius:20px; font-weight:bold; cursor:pointer;">Upgrade Now</button></a>
        </div>
    </div>

{% elif page == 'deposit' %}
    <div class="header"><div class="logo">Deposit Money</div><a href="/dashboard" style="color:black;"><i class="fas fa-times"></i></a></div>
    <div class="container">
        <div class="card" style="text-align:center;">
            <p>বিকাশ/নগদ (Personal): <b style="color:var(--primary); font-size:18px;">01601616145</b></p>
            <p style="font-size:12px; color:#666;">উপরের নম্বরে টাকা <b>Send Money</b> করার পর নিচের ফর্মটি পূরণ করুন।</p>
            <form method="POST">
                <input type="number" name="amount" class="input-field" placeholder="টাকার পরিমাণ (100/300)" required>
                <select name="method" class="input-field">
                    <option>Bkash</option>
                    <option>Nagad</option>
                </select>
                <input type="text" name="trxid" class="input-field" placeholder="Transaction ID (TrxID)" required>
                <button type="submit" class="btn-primary">Submit Deposit</button>
            </form>
        </div>
    </div>

{% elif page == 'withdraw' %}
    <div class="header"><div class="logo">Withdraw</div></div>
    <div class="container">
        <div class="card">
            <h4>টাকা উত্তোলন করুন</h4>
            <p style="font-size:12px; color:red;">সর্বনিম্ন উত্তোলন ১০০ টাকা।</p>
            <form method="POST">
                <input type="number" name="amount" class="input-field" placeholder="টাকার পরিমাণ" required>
                <select name="method" class="input-field">
                    <option>Bkash</option>
                    <option>Nagad</option>
                </select>
                <input type="tel" name="number" class="input-field" placeholder="আপনার নম্বর" required>
                <button type="submit" class="btn-primary">Request Withdraw</button>
            </form>
        </div>
    </div>

{% elif page == 'profile' %}
    <div class="header"><div class="logo">Profile</div></div>
    <div class="container">
        <div class="card" style="text-align:center;">
            <div style="width:70px; height:70px; background:#eee; border-radius:50%; margin:auto; display:flex; align-items:center; justify-content:center;"><i class="fas fa-user fa-2x"></i></div>
            <h3>{{ user[1] }} {{ user[2] }}</h3>
            <p style="font-size:13px; color:#666; margin-top:-10px;">ID: {{ user[0] + 1000 }} | Level: {{ user[12] }}</p>
            <div style="text-align:left; font-size:14px; margin-top:20px;">
                <p><b>Email:</b> {{ user[3] }}</p>
                <p><b>Phone:</b> {{ user[4] }}</p>
                <p><b>Refer Link:</b> <br><small style="color:var(--blue);">applex.com/signup?ref={{ user[0] }}</small></p>
            </div>
            <a href="/logout" style="text-decoration:none;"><button class="btn-primary" style="background:red; margin-top:15px;">Logout Account</button></a>
        </div>
    </div>
{% endif %}

<div class="bottom-nav">
    <a href="/dashboard" class="nav-item"><i class="fas fa-home"></i><br>Home</a>
    <a href="#" class="nav-item"><i class="fas fa-tasks"></i><br>Job/Task</a>
    <a href="/withdraw" class="nav-item"><i class="fas fa-wallet"></i><br>Withdraw</a>
    <a href="/profile" class="nav-item"><i class="fas fa-user"></i><br>Profile</a>
</div>

</body>
</html>
"""

# --- ROUTES ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('signup'))
    conn = sqlite3.connect('applex_v4.db')
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user_id' not in session: return redirect(url_for('signup'))
    if request.method == 'POST':
        amount, method, trxid = request.form['amount'], request.form['method'], request.form['trxid']
        conn = sqlite3.connect('applex_v4.db')
        conn.execute("INSERT INTO deposits (user_id, amount, method, trxid, status) VALUES (?,?,?,?,?)",
                     (session['user_id'], amount, method, trxid, 'Pending'))
        conn.commit()
        conn.close()
        return "<script>alert('Deposit Request Sent!'); window.location='/dashboard';</script>"
    return render_template_string(MASTER_HTML, page='deposit')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user_id' not in session: return redirect(url_for('signup'))
    if request.method == 'POST':
        amount, method, number = request.form['amount'], request.form['method'], request.form['number']
        conn = sqlite3.connect('applex_v4.db')
        conn.execute("INSERT INTO withdraws (user_id, amount, method, number, status) VALUES (?,?,?,?,?)",
                     (session['user_id'], amount, method, number, 'Pending'))
        conn.commit()
        conn.close()
        return "<script>alert('Withdraw Request Sent!'); window.location='/dashboard';</script>"
    return render_template_string(MASTER_HTML, page='withdraw')

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('signup'))
    conn = sqlite3.connect('applex_v4.db')
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(MASTER_HTML, page='profile', user=user)

# Signup/Login/Logout একই থাকবে...
# ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
