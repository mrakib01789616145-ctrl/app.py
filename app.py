from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_super_secure_key_999"

# ১. ডাটাবেজ সেটআপ
def init_db():
    conn = sqlite3.connect('applex_v2.db')
    cursor = conn.cursor()
    # ইউজার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      first_name TEXT, last_name TEXT, email TEXT UNIQUE, 
                      phone TEXT, password TEXT, 
                      refer_bal REAL DEFAULT 0.0, salary_bal REAL DEFAULT 0.0,
                      job_bal REAL DEFAULT 0.0, total_earn REAL DEFAULT 0.0,
                      total_withdraw REAL DEFAULT 0.0, free_earn REAL DEFAULT 0.0,
                      level TEXT DEFAULT 'Free')''')
    # ডিপোজিট টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS deposits 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user_id INTEGER, amount REAL, method TEXT, trxid TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ২. ডিজাইন টেমপ্লেট (ড্যাশবোর্ড, সাইনআপ, ডিপোজিট)
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Premium Earning</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .header { background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); sticky: top; }
        .logo { font-size: 24px; font-weight: bold; color: black; }
        .logo span { color: var(--primary); }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }

        /* Balance Grid (6 Boxes) */
        .balance-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px; }
        .bal-box { background: white; padding: 12px 5px; border-radius: 12px; text-align: center; border: 1px solid #ddd; }
        .bal-box b { font-size: 13px; color: #333; }
        .bal-box p { margin: 5px 0 0; color: var(--blue); font-weight: bold; font-size: 11px; }

        /* Level Cards */
        .card { background: white; border-radius: 15px; padding: 20px; margin-top: 15px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .true-level { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .master-level { background: linear-gradient(135deg, #ff9a9e, #fecfef); color: #333; }
        .btn-upgrade { background: white; color: #764ba2; border: none; padding: 10px 20px; border-radius: 20px; font-weight: bold; margin-top: 10px; cursor: pointer; }

        /* Auth Form */
        .auth-card { background: white; padding: 30px; border-radius: 20px; text-align: center; margin-top: 50px; }
        .input-field { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        
        /* Bottom Nav */
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #ddd; }
        .nav-item { text-align: center; color: #666; text-decoration: none; font-size: 11px; }
        .nav-item i { font-size: 20px; margin-bottom: 3px; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
        <div><i class="fas fa-search"></i> &nbsp; <i class="fas fa-bell"></i></div>
    </div>
    <div class="container">
        <h3>Dashboard</h3>
        <p style="font-size:13px; margin-top:-10px;">Welcome, <b>{{ name }}</b> | Level: <span style="color:green;">{{ level }}</span></p>

        <div class="balance-grid">
            <div class="bal-box"><b>Tk. {{ bal[0] }}</b><p>Refer</p></div>
            <div class="bal-box"><b>Tk. {{ bal[1] }}</b><p>Salary</p></div>
            <div class="bal-box"><b>Tk. {{ bal[2] }}</b><p>Job</p></div>
            <div class="bal-box"><b>Tk. {{ bal[3] }}</b><p>Total Earning</p></div>
            <div class="bal-box"><b>Tk. {{ bal[4] }}</b><p>Withdraw</p></div>
            <div class="bal-box"><b>Tk. {{ bal[5] }}</b><p>Free Earn</p></div>
        </div>

        <div class="card true-level">
            <h4>True Level (৳ ১০০)</h4>
            <p>প্রতিদিন ৫টি টাস্ক এবং মাসিক ইনকাম সুবিধা পান।</p>
            <a href="/deposit" style="text-decoration:none;"><button class="btn-upgrade">Upgrade Now</button></a>
        </div>

        <div class="card master-level">
            <h4>Master Level (৳ ৩০০)</h4>
            <p>আনলিমিটেড টাস্ক এবং ডাবল রেফারেল কমিশন।</p>
            <a href="/deposit" style="text-decoration:none;"><button class="btn-upgrade" style="color:#d93025;">Unlock Master</button></a>
        </div>
    </div>

    <div class="bottom-nav">
        <a href="/dashboard" class="nav-item"><i class="fas fa-home"></i><br>Home</a>
        <a href="#" class="nav-item"><i class="fas fa-tasks"></i><br>Job/Task</a>
        <a href="/deposit" class="nav-item"><i class="fas fa-wallet"></i><br>Deposit</a>
        <a href="/logout" class="nav-item"><i class="fas fa-user"></i><br>Profile</a>
    </div>

{% elif page == 'signup' %}
    <div class="container">
        <div class="auth-card">
            <div class="logo" style="font-size:35px;"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
            <p>Sign up to start earning</p>
            <form method="POST">
                <div style="display:flex; gap:10px;">
                    <input type="text" name="f_name" class="input-field" placeholder="First Name" required>
                    <input type="text" name="l_name" class="input-field" placeholder="Last Name" required>
                </div>
                <input type="email" name="email" class="input-field" placeholder="Email Address" required>
                <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
                <input type="password" name="pass" class="input-field" placeholder="Password" required>
                <button type="submit" class="btn-primary">Create Account</button>
            </form>
            <p style="font-size:13px; margin-top:15px;">Already have account? <a href="/login">Login</a></p>
        </div>
    </div>

{% elif page == 'deposit' %}
    <div class="header">
        <div class="logo">Deposit Money</div>
        <a href="/dashboard" style="text-decoration:none; color:black;"><i class="fas fa-times"></i></a>
    </div>
    <div class="container">
        <div class="card" style="text-align:center;">
            <p>বিকাশ/নগদ (Personal): <b>017XXXXXXXX</b></p>
            <p style="font-size:12px; color:red;">নিচের নম্বরটি কপি করে টাকা পাঠিয়ে দিন।</p>
            <form method="POST">
                <input type="number" name="amount" class="input-field" placeholder="টাকার পরিমাণ (100/300)" required>
                <select name="method" class="input-field">
                    <option>Bkash</option>
                    <option>Nagad</option>
                </select>
                <input type="text" name="trxid" class="input-field" placeholder="Transaction ID (TrxID)" required>
                <button type="submit" class="btn-primary">Submit Payment</button>
            </form>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        f_name, l_name = request.form['f_name'], request.form['l_name']
        email, phone = request.form['email'], request.form['phone']
        password = generate_password_hash(request.form['pass'])
        
        try:
            conn = sqlite3.connect('applex_v2.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (first_name, last_name, email, phone, password) VALUES (?,?,?,?,?)",
                           (f_name, l_name, email, phone, password))
            conn.commit()
            session['user_id'] = cursor.lastrowid
            conn.close()
            return redirect(url_for('dashboard'))
        except: return "Email already exists!"
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email, password = request.form['email'], request.form['pass']
        conn = sqlite3.connect('applex_v2.db')
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user[5], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        return "Invalid Credentials!"
    return render_template_string(MASTER_HTML, page='signup') # Login UI same as signup for demo

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('signup'))
    conn = sqlite3.connect('applex_v2.db')
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    # balances: refer, salary, job, total_earn, withdraw, free
    balances = [user[6], user[7], user[8], user[9], user[10], user[11]]
    return render_template_string(MASTER_HTML, page='dashboard', name=user[1], level=user[12], bal=balances)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user_id' not in session: return redirect(url_for('signup'))
    if request.method == 'POST':
        amount, method = request.form['amount'], request.form['method']
        trxid = request.form['trxid']
        conn = sqlite3.connect('applex_v2.db')
        conn.execute("INSERT INTO deposits (user_id, amount, method, trxid, status) VALUES (?,?,?,?,?)",
                     (session['user_id'], amount, method, trxid, 'Pending'))
        conn.commit()
        conn.close()
        return "<script>alert('Payment Submitted! Admin will verify soon.'); window.location='/dashboard';</script>"
    return render_template_string(MASTER_HTML, page='deposit')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
