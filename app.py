from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "applex_final_fixed_2026"

# ১. ডাটাবেজ ফাংশন (স্থায়ী এবং নিরাপদ)
DB_PATH = 'applex_main.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # ইউজার টেবিল - ফোন নম্বর দিয়ে লগইন করার জন্য phone কলামটি UNIQUE
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      first_name TEXT, last_name TEXT, email TEXT UNIQUE, 
                      phone TEXT UNIQUE, password TEXT, 
                      refer_bal REAL DEFAULT 0.0, salary_bal REAL DEFAULT 0.0,
                      job_bal REAL DEFAULT 0.0, total_earn REAL DEFAULT 0.0,
                      total_withdraw REAL DEFAULT 0.0, free_earn REAL DEFAULT 0.0,
                      level TEXT DEFAULT 'Free')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, trxid TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS withdraws (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, method TEXT, number TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ২. মাস্টার ডিজাইন (লগইন এবং সাইন আপ সুইচ করার সুবিধাসহ)
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Login/Signup</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; padding: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: white; width: 100%; max-width: 400px; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; margin: 15px; }
        .logo { font-size: 32px; font-weight: 900; color: #000; margin-bottom: 10px; }
        .logo i { color: var(--primary); }
        .input-field { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; outline: none; font-size: 14px; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 10px; }
        .switch-text { margin-top: 20px; font-size: 14px; color: #666; }
        .switch-text a { color: var(--blue); text-decoration: none; font-weight: bold; }
        .error-msg { background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 15px; }
    </style>
</head>
<body>

<div class="card">
    <div class="logo"><i class="fas fa-apple-alt"></i> APPLEX</div>
    
    {% if page == 'login' %}
        <h3>Welcome Back</h3>
        <p style="color:#888; font-size:14px; margin-top:-10px;">Login with your phone number</p>
        {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
        <form method="POST" action="/login">
            <input type="tel" name="phone" class="input-field" placeholder="Phone Number (e.g. 017...)" required>
            <input type="password" name="pass" class="input-field" placeholder="Password" required>
            <button type="submit" class="btn-primary">Login Now</button>
        </form>
        <div class="switch-text">
            Don't have an account? <a href="/signup">Create Account</a>
        </div>

    {% elif page == 'signup' %}
        <h3>Create Account</h3>
        <p style="color:#888; font-size:14px; margin-top:-10px;">Join APPLEX to start earning</p>
        {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
        <form method="POST" action="/signup">
            <div style="display:flex; gap:10px;">
                <input type="text" name="f_name" class="input-field" placeholder="First Name" required>
                <input type="text" name="l_name" class="input-field" placeholder="Last Name" required>
            </div>
            <input type="email" name="email" class="input-field" placeholder="Email Address" required>
            <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
            <input type="password" name="pass" class="input-field" placeholder="Password" required>
            <button type="submit" class="btn-primary">Sign Up Now</button>
        </form>
        <div class="switch-text">
            Already have an account? <a href="/login">Login Here</a>
        </div>
    {% endif %}
</div>

</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('pass')
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(MASTER_HTML, page='login', error="ফোন নম্বর বা পাসওয়ার্ড ভুল!")
            
    return render_template_string(MASTER_HTML, page='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = generate_password_hash(request.form.get('pass'))

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (first_name, last_name, email, phone, password) VALUES (?, ?, ?, ?, ?)",
                           (f_name, l_name, email, phone, password))
            conn.commit()
            session['user_id'] = cursor.lastrowid
            conn.close()
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            return render_template_string(MASTER_HTML, page='signup', error="এই ফোন নম্বর বা ইমেইল দিয়ে অলরেডি অ্যাকাউন্ট আছে!")
            
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # আপনার ড্যাশবোর্ড কোড এখানে থাকবে...
    return "Dashboard Loaded! (আপনার ড্যাশবোর্ড কোডটি এখানে যুক্ত করুন)"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
