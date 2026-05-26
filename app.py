from flask import Flask, render_template_string, request, session, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_mega_pro_v30"

# ডাটাবেজ সেটআপ
def init_db():
    conn = sqlite3.connect('applex_main.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0, total_withdraw REAL DEFAULT 0, 
                  refer_code TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- প্রোফেশনাল ইউজার ইন্টারফেস (HTML) ---
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Earn Real Money</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #2ecc71; --secondary: #3498db; --danger: #e74c3c; --dark: #2c3e50; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f6; margin: 0; }
        .header { background: white; padding: 15px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .container { max-width: 480px; margin: auto; padding: 20px; padding-bottom: 100px; }
        
        /* ব্যালেন্স কার্ড */
        .balance-card { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
        .balance-card h2 { margin: 10px 0; font-size: 35px; }

        /* টাস্ক ও অপশন গ্রিড */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .menu-item { background: white; padding: 20px; border-radius: 15px; text-align: center; text-decoration: none; color: var(--dark); box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
        .menu-item i { font-size: 30px; margin-bottom: 10px; display: block; }
        .yt { color: #ff0000; } .tg { color: #0088cc; } .ref { color: #f39c12; } .wd { color: #27ae60; }

        /* ফরম স্টাইল */
        .card { background: white; padding: 20px; border-radius: 15px; margin-top: 15px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; color: white; }
        .btn-primary { background: var(--secondary); }
        .btn-withdraw { background: var(--danger); }

        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #eee; max-width: 480px; left: 50%; transform: translateX(-50%); }
        .nav-link { color: #7f8c8d; text-decoration: none; font-size: 12px; text-align: center; }
        .nav-link.active { color: var(--secondary); }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <h3 style="margin:0; color:var(--danger);"><i class="fas fa-apple-alt"></i> APPLEX</h3>
    </div>
    <div class="container">
        <div class="balance-card">
            <span style="opacity: 0.8;">Available Balance</span>
            <h2>৳ {{ user['balance'] }}</h2>
            <p style="font-size: 12px;">Total Withdrawn: ৳{{ user['total_withdraw'] }}</p>
        </div>

        <h4 style="margin-bottom:10px;">Daily Tasks</h4>
        <div class="grid">
            <a href="/complete_task/youtube" class="menu-item"><i class="fab fa-youtube yt"></i>Youtube Subscribe</a>
            <a href="/complete_task/telegram" class="menu-item"><i class="fab fa-telegram tg"></i>Telegram Join</a>
            <a href="/refer" class="menu-item"><i class="fas fa-users ref"></i>Refer & Earn</a>
            <a href="/withdraw" class="menu-item"><i class="fas fa-wallet wd"></i>Withdraw</a>
        </div>
    </div>

    <div class="bottom-nav">
        <a href="/dashboard" class="nav-link active"><i class="fas fa-home"></i><br>Home</a>
        <a href="/withdraw" class="nav-link"><i class="fas fa-money-check-alt"></i><br>Withdraw</a>
        <a href="/profile" class="nav-link"><i class="fas fa-user"></i><br>Profile</a>
    </div>

{% elif page == 'login' or page == 'signup' %}
    <div style="max-width:350px; margin: 80px auto; padding:30px; background:white; border-radius:20px; text-align:center; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
        <h2><i class="fas fa-apple-alt" style="color:var(--danger);"></i> APPLEX</h2>
        <p>{{ 'Create New Account' if page == 'signup' else 'Login to Your Account' }}</p>
        
        <form method="POST" action="{{ '/signup' if page == 'signup' else '/login' }}">
            {% if page == 'signup' %}
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="email" name="email" placeholder="Email Address" required>
            {% endif %}
            <input type="tel" name="phone" placeholder="Phone Number" required>
            <input type="password" name="pass" placeholder="Password" required>
            <button type="submit" class="btn btn-primary">{{ 'Sign Up Now' if page == 'signup' else 'Login Now' }}</button>
        </form>
        
        {% if page == 'login' %}
            <p style="font-size:14px; margin-top:15px;">New here? <a href="/signup">Create Account</a></p>
        {% else %}
            <p style="font-size:14px; margin-top:15px;">Already have an account? <a href="/login">Login</a></p>
        {% endif %}
    </div>

{% elif page == 'withdraw' %}
    <div class="header"><h3>Withdraw Funds</h3></div>
    <div class="container">
        <div class="card">
            <p style="color:#666;">Minimum Withdraw: <b>৳ ৫০</b></p>
            <form method="POST" action="/request_withdraw">
                <input type="number" name="amount" placeholder="Enter Amount" min="50" required>
                <input type="tel" name="phone" placeholder="Bkash/Nagad Number" required>
                <button type="submit" class="btn btn-withdraw">Withdraw Now</button>
            </form>
            <a href="/dashboard" style="display:block; text-align:center; margin-top:15px; color:#666;">Back to Home</a>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

# --- ব্যাকএন্ড লজিক ---

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, email, phone, pwd = request.form['name'], request.form['email'], request.form['phone'], request.form['pass']
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, phone, password, refer_code) VALUES (?, ?, ?, ?, ?)", 
                       (name, email, phone, generate_password_hash(pwd), "REF"+phone[-4:]))
            db.commit()
            return redirect(url_for('login'))
        except:
            return "Phone number already exists!"
        finally: db.close()
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone, pwd = request.form['phone'], request.form['pass']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], pwd):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/complete_task/<type>')
def complete_task(type):
    if 'user_id' not in session: return redirect(url_for('login'))
    reward = 5.0 # প্রতি টাস্কে ৫ টাকা
    db = get_db()
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (reward, session['user_id']))
    db.commit()
    db.close()
    return redirect(url_for('dashboard'))

@app.route('/withdraw')
def withdraw_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template_string(MASTER_HTML, page='withdraw')

@app.route('/request_withdraw', methods=['POST'])
def request_withdraw():
    amount = float(request.form['amount'])
    db = get_db()
    user = db.execute("SELECT balance FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if user['balance'] >= amount:
        db.execute("UPDATE users SET balance = balance - ?, total_withdraw = total_withdraw + ? WHERE id = ?", 
                   (amount, amount, session['user_id']))
        db.commit()
    db.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
