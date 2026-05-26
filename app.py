from flask import Flask, render_template_string, request, session, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_withdraw_ready_v20"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- প্রোফেশনাল ডিজাইন ---
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --blue: #007bff; --red: #d93025; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; }
        .header { background: white; padding: 15px; display: flex; justify-content: space-between; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 100px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        .box { background: white; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #eee; }
        .box b { color: var(--blue); font-size: 18px; display: block; }
        .card { background: white; padding: 20px; border-radius: 15px; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .btn-withdraw { background: var(--red); color: white; border: none; padding: 12px; border-radius: 10px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 10px; }
        .input-style { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }
        .nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #ddd; max-width: 480px; left: 50%; transform: translateX(-50%); }
        .nav-a { text-align: center; color: #666; text-decoration: none; font-size: 12px; flex:1; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); }
        .m-content { background: white; margin: 30% auto; padding: 25px; border-radius: 20px; width: 80%; max-width: 350px; text-align: center; }
    </style>
</head>
<body>
{% if page == 'dashboard' %}
    <div class="header">
        <div style="font-weight:bold; font-size:20px;"><i class="fas fa-apple-alt" style="color:var(--red);"></i> APPLEX</div>
        <i class="fas fa-bell"></i>
    </div>
    <div class="container">
        <h3>Dashboard</h3>
        <p>Welcome, <b>{{ user['first_name'] }}</b></p>
        
        <div class="grid">
            <div class="box"><b>৳{{ user['total_earn'] }}</b><span>Balance</span></div>
            <div class="box"><b>৳{{ user['total_withdraw'] }}</b><span>Withdrawn</span></div>
        </div>

        <div class="card">
            <h4 style="margin:0 0 10px 0;">Withdraw Funds</h4>
            <form action="/withdraw" method="POST">
                <input type="tel" name="withdraw_number" placeholder="Bkash/Nagad Number" class="input-style" required>
                <input type="number" name="amount" placeholder="Amount (Min. 500)" class="input-style" required>
                <button type="submit" class="btn-withdraw">Withdraw Now</button>
            </form>
        </div>

        <div class="card" style="background: linear-gradient(135deg, #667eea, #764ba2); color:white; text-align:center;">
            <h4 style="margin:0;">Premium Upgrade</h4>
            <button onclick="openDep()" style="background:white; color:#764ba2; border:none; padding:10px 20px; border-radius:20px; font-weight:bold; margin-top:10px; width:100%;">Deposit Now</button>
        </div>
    </div>

    <div id="depM" class="modal">
        <div class="m-content">
            <h4>Deposit Money</h4>
            <p>নিচের নম্বরে সেন্ড মানি করুন:</p>
            <div style="padding:15px; border:2px dashed var(--blue); font-size:20px; font-weight:bold; margin:10px 0;">01601616145</div>
            <p style="color:red; font-size:12px;">Admin Personal Number</p>
            <button onclick="closeDep()" style="width:100%; padding:10px; background:#eee; border:none; border-radius:10px;">Close</button>
        </div>
    </div>

    <div class="nav">
        <a href="/dashboard" class="nav-a" style="color:var(--blue);"><i class="fas fa-home"></i><br>Home</a>
        <a href="#" class="nav-a"><i class="fas fa-tasks"></i><br>Tasks</a>
        <div class="nav-a" onclick="openDep()" style="cursor:pointer;"><i class="fas fa-wallet"></i><br>Deposit</div>
        <a href="/logout" class="nav-a"><i class="fas fa-sign-out-alt"></i><br>Logout</a>
    </div>

    <script>
        function openDep(){ document.getElementById('depM').style.display='block'; }
        function closeDep(){ document.getElementById('depM').style.display='none'; }
    </script>

{% elif page == 'login' %}
    <div style="max-width:350px; margin:100px auto; padding:25px; background:white; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1); text-align:center;">
        <h2 style="color:var(--red);"><i class="fas fa-apple-alt"></i> APPLEX</h2>
        <form method="POST">
            <input type="tel" name="phone" placeholder="Phone Number" class="input-style" required>
            <input type="password" name="pass" placeholder="Password" class="input-style" required>
            <button type="submit" style="width:100%; padding:14px; background:var(--blue); color:white; border:none; border-radius:10px; font-weight:bold; margin-top:10px;">Login Now</button>
        </form>
    </div>
{% endif %}
</body>
</html>
"""

# --- সার্ভার লজিক ---
@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone, pwd = request.form['phone'], request.form['pass']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], pwd):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
    return render_template_string(MASTER_HTML, page='login')

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    number = request.form.get('withdraw_number')
    amount = float(request.form.get('amount'))
    user_id = session['user_id']
    
    db = get_db()
    user = db.execute("SELECT total_earn FROM users WHERE id=?", (user_id,)).fetchone()
    
    if user and user['total_earn'] >= amount:
        # ব্যালেন্স কমানো এবং উইথড্র আপডেট করা
        db.execute("UPDATE users SET total_earn = total_earn - ?, total_withdraw = total_withdraw + ? WHERE id=?", (amount, amount, user_id))
        db.commit()
        # এখানে আপনি চাইলে একটি 'withdraw_requests' টেবিলে ডাটা সেভ করতে পারেন
    db.close()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    db.close()
    if not user: return redirect(url_for('login'))
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
