from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_final_master_v12"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# ১. আপনার আসল ডিজাইন এবং নতুন ডিপোজিট সিস্টেমের HTML
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .header { background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 24px; font-weight: bold; display: flex; align-items: center; gap: 8px; }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        
        .balance-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px; }
        .bal-box { background: white; padding: 15px 5px; border-radius: 12px; text-align: center; border: 1px solid #eee; }
        .bal-box b { font-size: 13px; color: #333; display: block; }
        .bal-box p { margin: 5px 0 0; color: var(--blue); font-weight: bold; font-size: 10px; }

        .upgrade-card { border-radius: 15px; padding: 20px; margin-top: 15px; color: white; position: relative; }
        .btn-upgrade { background: white; color: #764ba2; border: none; padding: 8px 20px; border-radius: 20px; font-weight: bold; margin-top: 10px; cursor: pointer; }
        
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #ddd; max-width: 480px; left: 50%; transform: translateX(-50%); }
        .nav-item { text-align: center; color: #666; text-decoration: none; font-size: 11px; flex: 1; border:none; background:none; cursor:pointer; }
        .nav-item i { font-size: 20px; margin-bottom: 3px; }
        .nav-item.active { color: var(--blue); }

        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); }
        .modal-content { background: white; margin: 25% auto; padding: 25px; border-radius: 20px; width: 80%; max-width: 350px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .copy-box { background: #f1f1f1; padding: 15px; border-radius: 10px; font-size: 18px; font-weight: bold; color: var(--blue); border: 2px dashed #007bff; margin: 10px 0; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
        <div><i class="fas fa-search"></i> &nbsp; <i class="fas fa-bell"></i></div>
    </div>
    <div class="container">
        <h3 style="margin-bottom: 5px;">Dashboard</h3>
        <p style="font-size:13px; margin:0;">Welcome, <b>{{ user['first_name'] }}</b> | Level: <span style="color:green;">{{ user['level'] }}</span></p>
        
        <div class="balance-grid">
            <div class="bal-box"><b>Tk. {{ user['refer_bal'] }}</b><p>Refer</p></div>
            <div class="bal-box"><b>Tk. {{ user['salary_bal'] }}</b><p>Salary</p></div>
            <div class="bal-box"><b>Tk. {{ user['job_bal'] }}</b><p>Job</p></div>
            <div class="bal-box"><b>Tk. {{ user['total_earn'] }}</b><p>Total Earning</p></div>
            <div class="bal-box"><b>Tk. {{ user['total_withdraw'] }}</b><p>Withdraw</p></div>
            <div class="bal-box"><b>Tk. {{ user['free_earn'] }}</b><p>Free Earn</p></div>
        </div>

        <div class="upgrade-card" style="background: linear-gradient(135deg, #667eea, #764ba2);">
            <h4 style="margin:0;">True Level (৳ ১০০)</h4>
            <button class="btn-upgrade" onclick="openDeposit()">Upgrade Now</button>
        </div>

        <div class="upgrade-card" style="background: linear-gradient(135deg, #ff9a9e, #fad0c4); color: #333;">
            <h4 style="margin:0;">Master Level (৳ ৩০০)</h4>
            <button class="btn-upgrade" style="color: #d93025;" onclick="openDeposit()">Unlock Master</button>
        </div>
    </div>

    <div id="depositModal" class="modal">
        <div class="modal-content">
            <h4 style="margin:0;">Deposit Money</h4>
            <p style="font-size:13px; color:#666;">নিচের নম্বরে <b>Send Money</b> করুন</p>
            <div class="copy-box">01601616145</div>
            <p style="font-size:12px; color:red;">বিকাশ / নগদ / রকেট (Personal)</p>
            <button onclick="closeDeposit()" style="margin-top:15px; width:100%; padding:12px; border:none; border-radius:10px; background:var(--blue); color:white; font-weight:bold;">বন্ধ করুন</button>
        </div>
    </div>

    <div class="bottom-nav">
        <a href="/dashboard" class="nav-item active"><i class="fas fa-home"></i><br>Home</a>
        <a href="#" class="nav-item"><i class="fas fa-list-ul"></i><br>Job/Task</a>
        <div class="nav-item" onclick="openDeposit()"><i class="fas fa-wallet"></i><br>Deposit</div>
        <a href="#" class="nav-item"><i class="fas fa-user"></i><br>Profile</a>
    </div>

    <script>
        function openDeposit() { document.getElementById('depositModal').style.display = 'block'; }
        function closeDeposit() { document.getElementById('depositModal').style.display = 'none'; }
        window.onclick = function(event) {
            if (event.target == document.getElementById('depositModal')) { closeDeposit(); }
        }
    </script>

{% elif page == 'login' %}
    <div class="container" style="text-align:center; margin-top:50px;">
        <div style="background:white; padding:30px; border-radius:20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
            <div class="logo" style="justify-content:center;"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
            <h3>Login Account</h3>
            <form method="POST">
                <input type="tel" name="phone" placeholder="Phone Number" style="width:100%; padding:12px; margin:10px 0; border-radius:10px; border:1px solid #ddd; box-sizing: border-box;" required>
                <input type="password" name="pass" placeholder="Password" style="width:100%; padding:12px; margin:10px 0; border-radius:10px; border:1px solid #ddd; box-sizing: border-box;" required>
                <button type="submit" style="width:100%; padding:14px; background:var(--blue); color:white; border:none; border-radius:10px; font-weight:bold;">Login Now</button>
            </form>
        </div>
    </div>
{% endif %}
</body>
</html>
"""

# ২. রুটস (Routes)
@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone, password = request.form['phone'], request.form['pass']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template_string(MASTER_HTML, page='login', error="Invalid Login")
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    if not user: return redirect(url_for('login'))
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
