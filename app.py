from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_permanent_v1"

# ১. স্থায়ী ডাটাবেজ কানেকশন (একই ফাইলে সব ডেটা থাকবে)
def get_db():
    conn = sqlite3.connect('applex_main.db') # ফাইল নেম সবসময় একই থাকবে
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # ইউজার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      first_name TEXT, last_name TEXT, email TEXT UNIQUE, 
                      phone TEXT UNIQUE, password TEXT, 
                      refer_bal REAL DEFAULT 0.0, salary_bal REAL DEFAULT 0.0,
                      job_bal REAL DEFAULT 0.0, total_earn REAL DEFAULT 0.0,
                      total_withdraw REAL DEFAULT 0.0, free_earn REAL DEFAULT 0.0,
                      level TEXT DEFAULT 'Free')''')
    # পেমেন্ট ও উইথড্র টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, trxid TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS withdraws (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, number TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ২. মাস্টার ডিজাইন (লগইন, ড্যাশবোর্ড, উইথড্র, প্রোফাইল)
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Premium</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .header { background: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 24px; font-weight: bold; }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        .card { background: white; border-radius: 15px; padding: 20px; margin-top: 15px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .input-field { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; outline: none; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #ddd; z-index: 100; }
        .nav-item { text-align: center; color: #666; text-decoration: none; font-size: 11px; flex: 1; }
        .nav-item i { font-size: 20px; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header"><div class="logo"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div></div>
    <div class="container">
        <p style="font-size:13px;">Welcome, <b>{{ user[1] }}</b> | Level: <span style="color:green;">{{ user[12] }}</span></p>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px;">
            <div style="background:white; padding:12px 5px; border-radius:12px; text-align:center; border:1px solid #ddd;"><b>Tk. {{ user[6] }}</b><p style="font-size:10px; color:var(--blue);">Refer</p></div>
            <div style="background:white; padding:12px 5px; border-radius:12px; text-align:center; border:1px solid #ddd;"><b>Tk. {{ user[7] }}</b><p style="font-size:10px; color:var(--blue);">Salary</p></div>
            <div style="background:white; padding:12px 5px; border-radius:12px; text-align:center; border:1px solid #ddd;"><b>Tk. {{ user[8] }}</b><p style="font-size:10px; color:var(--blue);">Job</p></div>
            <div style="background:white; padding:12px 5px; border-radius:12px; text-align:center; border:1px solid #ddd;"><b>Tk. {{ user[9] }}</b><p style="font-size:10px; color:var(--blue);">Total Earn</p></div>
            <div style="background:white; padding:12px 5px; border-radius:12px; text-align:center; border:1px solid #ddd;"><b>Tk. {{ user[10] }}</b><p style="font-size:10px; color:var(--blue);">Withdraw</p></div>
            <div style="background:white; padding:12px 5px; border-radius:12px; text-align:center; border:1px solid #ddd;"><b>Tk. {{ user[11] }}</b><p style="font-size:10px; color:var(--blue);">Free Earn</p></div>
        </div>
        <div class="card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
            <h4>True Level (৳ ১০০)</h4>
            <a href="/deposit" style="text-decoration:none;"><button style="background:white; color:#764ba2; border:none; padding:8px 15px; border-radius:20px; font-weight:bold;">Upgrade</button></a>
        </div>
    </div>

{% elif page == 'login' %}
    <div class="container">
        <div class="card" style="text-align:center; margin-top:50px;">
            <div class="logo" style="font-size:30px;"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
            <h3>Login Account</h3>
            {% if error %}<p style="color:red; font-size:12px;">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
                <input type="password" name="pass" class="input-field" placeholder="Password" required>
                <button type="submit" class="btn-primary">Login Now</button>
            </form>
            <p style="font-size:13px; margin-top:15px;">New member? <a href="/signup">Sign up</a></p>
        </div>
    </div>

{% elif page == 'deposit' %}
    <div class="header"><div class="logo">Deposit</div><a href="/dashboard" style="color:black;"><i class="fas fa-times"></i></a></div>
    <div class="container">
        <div class="card" style="text-align:center;">
            <p>Send Money (Personal): <b style="color:var(--primary);">01601616145</b></p>
            <form method="POST">
                <input type="number" name="amount" class="input-field" placeholder="Amount (100/300)" required>
                <select name="method" class="input-field"><option>Bkash</option><option>Nagad</option></select>
                <input type="text" name="trxid" class="input-field" placeholder="TrxID" required>
                <button type="submit" class="btn-primary">Submit</button>
            </form>
        </div>
    </div>
{% endif %}

{% if page != 'login' and page != 'signup' %}
<div class="bottom-nav">
    <a href="/dashboard" class="nav-item"><i class="fas fa-home"></i><br>Home</a>
    <a href="#" class="nav-item"><i class="fas fa-tasks"></i><br>Job</a>
    <a href="/withdraw" class="nav-item"><i class="fas fa-wallet"></i><br>Withdraw</a>
    <a href="/profile" class="nav-item"><i class="fas fa-user"></i><br>Profile</a>
</div>
{% endif %}

</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone, password = request.form['phone'], request.form['pass']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        conn.close()
        if user and check_password_hash(user[5], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        return render_template_string(MASTER_HTML, page='login', error="ভুল তথ্য!")
    return render_template_string(MASTER_HTML, page='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        f_name, l_name, email = request.form['f_name'], request.form['l_name'], request.form['email']
        phone, password = request.form['phone'], generate_password_hash(request.form['pass'])
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (first_name, last_name, email, phone, password) VALUES (?,?,?,?,?)",
                           (f_name, l_name, email, phone, password))
            conn.commit()
            session['user_id'] = cursor.lastrowid
            conn.close()
            return redirect(url_for('dashboard'))
        except: return "এই নম্বর দিয়ে অলরেডি অ্যাকাউন্ট আছে!"
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        amount, method, trxid = request.form['amount'], request.form['method'], request.form['trxid']
        conn = get_db()
        conn.execute("INSERT INTO deposits (user_id, amount, method, trxid, status) VALUES (?,?,?,?,?)",
                     (session['user_id'], amount, method, trxid, 'Pending'))
        conn.commit()
        conn.close()
        return "<script>alert('Submitted!'); window.location='/dashboard';</script>"
    return render_template_string(MASTER_HTML, page='deposit')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
