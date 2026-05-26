from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_final_master_secure"

# ১. ডাটাবেজ কানেকশন (স্থায়ী)
def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# ডাটাবেজ টেবিল তৈরি
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      first_name TEXT, last_name TEXT, email TEXT UNIQUE, 
                      phone TEXT UNIQUE, password TEXT, 
                      refer_bal REAL DEFAULT 0.0, salary_bal REAL DEFAULT 0.0,
                      job_bal REAL DEFAULT 0.0, total_earn REAL DEFAULT 0.0,
                      total_withdraw REAL DEFAULT 0.0, free_earn REAL DEFAULT 0.0,
                      level TEXT DEFAULT 'Free')''')
    conn.commit()
    conn.close()

init_db()

# ২. ড্যাশবোর্ড, লগইন এবং প্রোফাইল ডিজাইন
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
        .logo { font-size: 24px; font-weight: bold; }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        .card { background: white; border-radius: 15px; padding: 20px; margin-top: 15px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .balance-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px; }
        .bal-box { background: white; padding: 12px 5px; border-radius: 12px; text-align: center; border: 1px solid #ddd; }
        .bal-box b { font-size: 13px; color: #333; }
        .bal-box p { margin: 5px 0 0; color: var(--blue); font-weight: bold; font-size: 10px; }
        .input-field { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; outline: none; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #ddd; }
        .nav-item { text-align: center; color: #666; text-decoration: none; font-size: 11px; flex: 1; }
        .nav-item i { font-size: 20px; margin-bottom: 3px; }
        .nav-item.active { color: var(--blue); }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
        <div><i class="fas fa-search"></i> &nbsp; <i class="fas fa-bell"></i></div>
    </div>
    <div class="container">
        <p style="font-size:13px;">Welcome, <b>{{ user['first_name'] }}</b> | Level: <span style="color:green;">{{ user['level'] }}</span></p>
        <div class="balance-grid">
            <div class="bal-box"><b>Tk. {{ user['refer_bal'] }}</b><p>Refer</p></div>
            <div class="bal-box"><b>Tk. {{ user['salary_bal'] }}</b><p>Salary</p></div>
            <div class="bal-box"><b>Tk. {{ user['job_bal'] }}</b><p>Job</p></div>
            <div class="bal-box"><b>Tk. {{ user['total_earn'] }}</b><p>Total Earning</p></div>
            <div class="bal-box"><b>Tk. {{ user['total_withdraw'] }}</b><p>Withdraw</p></div>
            <div class="bal-box"><b>Tk. {{ user['free_earn'] }}</b><p>Free Earn</p></div>
        </div>
        <div class="card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; margin-top:20px;">
            <h4>True Level (৳ ১০০)</h4>
            <p style="font-size:12px;">প্রতিদিন ৫টি টাস্ক এবং মাসিক ইনকাম সুবিধা পান।</p>
            <button style="background:white; color:#764ba2; border:none; padding:10px 20px; border-radius:20px; font-weight:bold;">Upgrade Now</button>
        </div>
    </div>

{% elif page == 'login' %}
    <div class="container" style="text-align:center; margin-top:50px;">
        <div class="card">
            <div class="logo" style="font-size:30px;"><i class="fas fa-apple-alt" style="color:var(--primary);"></i> APPLEX</div>
            <h3>Login Account</h3>
            {% if error %}<p style="color:red; font-size:13px;">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
                <input type="password" name="pass" class="input-field" placeholder="Password" required>
                <button type="submit" class="btn-primary">Login Now</button>
            </form>
            <p style="font-size:13px; margin-top:15px;">New member? <a href="/signup">Create Account</a></p>
        </div>
    </div>
{% endif %}

{% if page != 'login' and page != 'signup' %}
<div class="bottom-nav">
    <a href="/dashboard" class="nav-item active"><i class="fas fa-home"></i><br>Home</a>
    <a href="#" class="nav-item"><i class="fas fa-tasks"></i><br>Job/Task</a>
    <a href="/profile" class="nav-item"><i class="fas fa-user"></i><br>Profile</a>
    <a href="/logout" class="nav-item"><i class="fas fa-sign-out-alt"></i><br>Logout</a>
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
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template_string(MASTER_HTML, page='login', error="ভুল নম্বর বা পাসওয়ার্ড!")
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
