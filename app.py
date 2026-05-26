from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_final_master_v50"

# ডাটাবেজ অটো-সেটআপ
def init_db():
    conn = sqlite3.connect('applex_main.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0, total_withdraw REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- একীভূত ডিজাইন (লগইন, সাইনআপ, ড্যাশবোর্ড) ---
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Earn & Task</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --success: #28a745; --bg: #f4f7f6; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; }
        .header { background: white; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        
        /* কার্ড ডিজাইন */
        .card { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; }
        .balance-box { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; text-align: center; }
        
        /* টাস্ক গ্রিড */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .task-item { background: white; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; color: #333; border: 1px solid #eee; }
        .task-item i { font-size: 25px; margin-bottom: 8px; display: block; }

        /* ফরম ও বাটন */
        input { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; color: white; }
        .btn-blue { background: var(--blue); }
        .btn-red { background: var(--primary); }

        /* বটম ন্যাভ */
        .nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #ddd; max-width: 480px; left: 50%; transform: translateX(-50%); }
        .nav-item { text-align: center; color: #666; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header"><h3 style="margin:0; color:var(--primary);">APPLEX</h3></div>
    <div class="container">
        <div class="card balance-box">
            <p style="margin:0; opacity:0.8;">My Balance</p>
            <h2 style="margin:5px 0;">৳ {{ user['balance'] }}</h2>
            <small>Withdrawn: ৳{{ user['total_withdraw'] }}</small>
        </div>

        <h4>Daily Tasks</h4>
        <div class="grid">
            <a href="/do_task/youtube" class="task-item"><i class="fab fa-youtube" style="color:red;"></i>YouTube Sub</a>
            <a href="/do_task/telegram" class="task-item"><i class="fab fa-telegram" style="color:#0088cc;"></i>Telegram Join</a>
            <a href="/withdraw" class="task-item"><i class="fas fa-money-bill-wave" style="color:green;"></i>Withdraw</a>
            <a href="#" class="task-item" onclick="alert('Refer Code: REF'+'{{ user['phone'][-4:] }}')"><i class="fas fa-users" style="color:orange;"></i>Refer Earn</a>
        </div>
    </div>

{% elif page == 'withdraw' %}
    <div class="header"><h3>Withdraw Money</h3></div>
    <div class="container">
        <div class="card">
            <p style="font-size:14px; color:#666;">মিনিমাম উইথড্র ৳৫০</p>
            <form action="/request_withdraw" method="POST">
                <input type="number" name="amount" placeholder="Amount (Min 50)" min="50" required>
                <input type="tel" name="phone" placeholder="Bkash/Nagad Number" required>
                <button type="submit" class="btn btn-red">Withdraw Now</button>
            </form>
            <a href="/dashboard" style="display:block; text-align:center; margin-top:15px; color:var(--blue);">Back to Home</a>
        </div>
    </div>

{% elif page == 'login' or page == 'signup' %}
    <div class="container" style="text-align:center; margin-top:50px;">
        <div class="card">
            <h2 style="color:var(--primary);">APPLEX</h2>
            <form method="POST" action="{{ '/signup' if page == 'signup' else '/login' }}">
                {% if page == 'signup' %}
                    <input type="text" name="name" placeholder="Full Name" required>
                    <input type="email" name="email" placeholder="Email" required>
                {% endif %}
                <input type="tel" name="phone" placeholder="Phone Number" required>
                <input type="password" name="pass" placeholder="Password" required>
                <button type="submit" class="btn btn-blue">{{ 'Create Account' if page == 'signup' else 'Login' }}</button>
            </form>
            {% if page == 'login' %}
                <p>New? <a href="/signup">Sign Up</a></p>
            {% else %}
                <p>Have account? <a href="/login">Login</a></p>
            {% endif %}
        </div>
    </div>
{% endif %}

{% if page != 'login' and page != 'signup' %}
<div class="nav">
    <a href="/dashboard" class="nav-item"><i class="fas fa-home"></i><br>Home</a>
    <a href="/withdraw" class="nav-item"><i class="fas fa-wallet"></i><br>Withdraw</a>
    <a href="/logout" class="nav-item"><i class="fas fa-sign-out-alt"></i><br>Logout</a>
</div>
{% endif %}

</body>
</html>
"""

# --- সার্ভার লজিক ---

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, email, phone, pwd = request.form['name'], request.form['email'], request.form['phone'], request.form['pass']
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)", 
                       (name, email, phone, generate_password_hash(pwd)))
            db.commit()
            return redirect(url_for('login'))
        except: return "Phone Number Exists!"
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

@app.route('/do_task/<type>')
def do_task(type):
    if 'user_id' not in session: return redirect(url_for('login'))
    reward = 2.0 # প্রতি কাজের জন্য ২ টাকা
    db = get_db()
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (reward, session['user_id']))
    db.commit()
    db.close()
    # এখানে আপনার আসল লিঙ্ক দিতে পারেন
    url = "https://youtube.com" if type == 'youtube' else "https://t.me"
    return redirect(url)

@app.route('/withdraw')
def withdraw():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='withdraw', user=user)

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
