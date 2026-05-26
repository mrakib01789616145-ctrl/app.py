from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_pro_stable_v15"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- প্রফেশনাল HTML ইন্টারফেস ---
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Earn Money</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f4f7f6; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .header { background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 1000; }
        .logo { font-size: 22px; font-weight: 800; color: #333; display: flex; align-items: center; gap: 8px; }
        .container { max-width: 500px; margin: auto; padding: 20px; padding-bottom: 100px; }
        
        .balance-card { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .box { background: #fff; padding: 15px; border-radius: 12px; border: 1px solid #eee; text-align: center; transition: 0.3s; }
        .box b { font-size: 16px; color: var(--blue); display: block; }
        .box span { font-size: 12px; color: #666; }

        .upgrade-section { background: linear-gradient(135deg, #6e8efb, #a777e3); color: white; padding: 20px; border-radius: 15px; margin-top: 20px; }
        .btn-main { background: white; color: #6e8efb; border: none; padding: 10px 25px; border-radius: 25px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; }
        
        .nav-bar { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #eee; max-width: 500px; left: 50%; transform: translateX(-50%); box-shadow: 0 -2px 10px rgba(0,0,0,0.05); }
        .nav-btn { text-align: center; color: #888; text-decoration: none; font-size: 12px; flex: 1; cursor: pointer; border: none; background: none; }
        .nav-btn i { font-size: 20px; margin-bottom: 4px; }
        .nav-btn.active { color: var(--blue); }

        .modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); }
        .modal-body { background: white; margin: 30% auto; padding: 30px; border-radius: 20px; width: 85%; max-width: 380px; text-align: center; }
        .num-box { background: #f8f9fa; padding: 15px; border-radius: 12px; font-size: 20px; font-weight: bold; color: var(--blue); border: 2px dashed var(--blue); margin: 15px 0; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
        <div><i class="fas fa-user-circle" style="font-size:24px; color:#555;"></i></div>
    </div>

    <div class="container">
        <div class="balance-card">
            <h4 style="margin:0 0 15px 0;">Welcome, {{ user['first_name'] }}</h4>
            <div class="grid">
                <div class="box"><b>৳{{ user['total_earn'] }}</b><span>Total Earn</span></div>
                <div class="box"><b>৳{{ user['job_bal'] }}</b><span>Work Balance</span></div>
                <div class="box"><b>৳{{ user['refer_bal'] }}</b><span>Refer Bonus</span></div>
                <div class="box"><b>৳{{ user['total_withdraw'] }}</b><span>Withdraw</span></div>
            </div>
        </div>

        <div class="upgrade-section">
            <h3 style="margin:0;">Premium Membership</h3>
            <p style="font-size:13px; opacity:0.9;">Unlock daily tasks and double your earnings today!</p>
            <button class="btn-main" onclick="showPop()">Upgrade Now</button>
        </div>
    </div>

    <div id="payModal" class="modal">
        <div class="modal-body">
            <h3 style="margin:0;">Deposit Now</h3>
            <p style="font-size:14px; color:#666;">নিচের নম্বরে <b>Send Money</b> করুন:</p>
            <div class="num-box">01601616145</div>
            <p style="font-size:12px; color:red;">BKash / Nagad / Rocket (Personal)</p>
            <button onclick="hidePop()" style="width:100%; padding:12px; border-radius:10px; border:none; background:#eee; font-weight:bold;">Close</button>
        </div>
    </div>

    <div class="nav-bar">
        <a href="/dashboard" class="nav-btn active"><i class="fas fa-home"></i><br>Home</a>
        <div class="nav-btn" onclick="alert('Task system loading...')"><i class="fas fa-tasks"></i><br>Task</div>
        <div class="nav-btn" onclick="showPop()"><i class="fas fa-wallet"></i><br>Deposit</div>
        <a href="/logout" class="nav-btn"><i class="fas fa-sign-out-alt"></i><br>Logout</a>
    </div>

    <script>
        function showPop() { document.getElementById('payModal').style.display='block'; }
        function hidePop() { document.getElementById('payModal').style.display='none'; }
    </script>

{% elif page == 'login' %}
    <div style="max-width:400px; margin: 80px auto; padding:30px; background:white; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
        <h2 class="logo" style="justify-content:center;"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</h2>
        <p style="color:#666;">Sign in to your account</p>
        <form method="POST">
            <input type="tel" name="phone" placeholder="Phone Number" style="width:100%; padding:12px; margin:10px 0; border-radius:10px; border:1px solid #ddd; box-sizing:border-box;" required>
            <input type="password" name="pass" placeholder="Password" style="width:100%; padding:12px; margin:10px 0; border-radius:10px; border:1px solid #ddd; box-sizing:border-box;" required>
            <button type="submit" style="width:100%; padding:14px; background:var(--blue); color:white; border:none; border-radius:10px; font-weight:bold; margin-top:10px;">Login</button>
        </form>
    </div>
{% endif %}
</body>
</html>
"""

# --- সার্ভার লজিক ---
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

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
