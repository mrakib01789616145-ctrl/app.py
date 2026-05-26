from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "premium_fixed_key_123"

# ১. ডাটাবেজ সেটআপ
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      name TEXT, email TEXT UNIQUE, password TEXT, 
                      balance REAL DEFAULT 0.0)''')
    conn.commit()
    conn.close()

init_db()

# ২. সম্পূর্ণ ডিজাইন (Dashboard, Login, Signup, Edit Profile)
FULL_DESIGN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoinStack - Earn</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #1a73e8; --secondary: #34a853; --dark: #202124; }
        body { font-family: 'Poppins', sans-serif; background: #f0f4f8; margin: 0; padding: 0; }
        .header { background: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .container { max-width: 450px; margin: auto; padding: 20px; }
        .wallet-card { background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
        .task-card { background: white; border-radius: 15px; padding: 15px; margin-bottom: 12px; display: flex; align-items: center; gap: 15px; border: 1px solid #eee; }
        .go-btn { background: var(--secondary); color: white; border: none; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; }
        .auth-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center; width: 100%; max-width: 350px; }
        .auth-input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .auth-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div style="color:var(--primary); font-weight:bold;"><i class="fas fa-coins"></i> CoinStack</div>
        <a href="/logout" style="color:red; text-decoration:none; font-size:12px; border:1px solid red; padding:4px 10px; border-radius:15px;">লগআউট</a>
    </div>
    <div class="container">
        <div style="background:white; padding:15px; border-radius:15px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
            <div><p style="margin:0; font-size:12px;">স্বাগতম,</p><h3 style="margin:0;">{{ name }}</h3></div>
            <a href="/edit-profile" style="font-size:12px; text-decoration:none; color:var(--primary); font-weight:bold;"><i class="fas fa-edit"></i> এডিট</a>
        </div>
        <div class="wallet-card"><h1>৳ {{ balance }}</h1><p>Digital Wallet Balance</p></div>
        <h4><i class="fas fa-bolt" style="color:#fbbc04;"></i> কাজগুলো সম্পন্ন করুন</h4>
        <div class="task-card">
            <i class="fab fa-youtube" style="font-size:25px; color:#d93025;"></i>
            <div style="flex-grow:1;"><b>ভিডিও দেখুন</b><br><small>পুরস্কার: ৳ ২.০০</small></div>
            <a href="#" class="go-btn">শুরু</a>
        </div>
    </div>

{% elif page == 'login' or page == 'signup' %}
    <div style="height:100vh; display:flex; align-items:center; justify-content:center; padding:20px;">
        <div class="auth-card">
            <h2>{{ 'Login' if page == 'login' else 'Sign Up' }}</h2>
            {% if error %}<p style="color:red; font-size:13px;">{{ error }}</p>{% endif %}
            <form method="POST">
                {% if page == 'signup' %}<input type="text" name="name" class="auth-input" placeholder="আপনার নাম" required>{% endif %}
                <input type="email" name="email" class="auth-input" placeholder="জিমেইল" required>
                <input type="password" name="password" class="auth-input" placeholder="পাসওয়ার্ড" required>
                <button type="submit" class="auth-btn">{{ 'লগইন' if page == 'login' else 'অ্যাকাউন্ট খুলুন' }}</button>
            </form>
            <p style="font-size:14px; margin-top:15px;">
                {{ 'অ্যাকাউন্ট নেই?' if page == 'login' else 'অ্যাকাউন্ট আছে?' }} 
                <a href="{{ '/signup' if page == 'login' else '/' }}">{{ 'সাইনআপ' if page == 'login' else 'লগইন' }}</a>
            </p>
        </div>
    </div>

{% elif page == 'edit_profile' %}
    <div style="height:100vh; display:flex; align-items:center; justify-content:center; padding:20px;">
        <div class="auth-card">
            <h3>নাম পরিবর্তন করুন</h3>
            <form method="POST">
                <input type="text" name="new_name" class="auth-input" value="{{ name }}" required>
                <button type="submit" class="auth-btn">আপডেট</button>
            </form>
            <a href="/dashboard" style="display:block; margin-top:15px; font-size:14px; color:#666;">ফিরে যান</a>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        conn = sqlite3.connect('users.db')
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        error = "ভুল জিমেইল বা পাসওয়ার্ড!"
    return render_template_string(FULL_DESIGN, page='login', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, email, password = request.form['name'], request.form['email'], request.form['password']
        try:
            conn = sqlite3.connect('users.db')
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except: return "এই জিমেইলটি ইতিমধ্যে ব্যবহৃত হয়েছে!"
    return render_template_string(FULL_DESIGN, page='signup')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(FULL_DESIGN, page='dashboard', name=user[1], balance=user[4])

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    if request.method == 'POST':
        new_name = request.form['new_name']
        conn.execute("UPDATE users SET name=? WHERE id=?", (new_name, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(FULL_DESIGN, page='edit_profile', name=user[1])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
