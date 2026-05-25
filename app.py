from flask import Flask, render_template_string, request, session, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "my_secret_key_123" # আপনার সিকিউরিটি কি

# ১. ডাটাবেজ সেটআপ
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      name TEXT, 
                      email TEXT UNIQUE, 
                      password TEXT, 
                      balance REAL DEFAULT 0.0)''')
    conn.commit()
    conn.close()

init_db()

# ২. ডিজাইন (HTML Templates)
BASE_STYLE = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
    .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
    input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
    .btn { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
    .btn-task { background: #28a745; margin-top: 10px; display: block; text-decoration: none; }
    .nav { display: flex; justify-content: space-between; margin-bottom: 20px; font-size: 14px; }
    .error { color: red; margin-bottom: 10px; }
</style>
"""

LOGIN_HTML = BASE_STYLE + """
<div class="card">
    <h2>Login</h2>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <form method="POST">
        <input type="email" name="email" placeholder="আপনার জিমেইল" required>
        <input type="password" name="password" placeholder="পাসওয়ার্ড" required>
        <button type="submit" class="btn">লগইন করুন</button>
    </form>
    <p>অ্যাকাউন্ট নেই? <a href="/signup">এখানে তৈরি করুন</a></p>
</div>
"""

SIGNUP_HTML = BASE_STYLE + """
<div class="card">
    <h2>Create Account</h2>
    <form method="POST">
        <input type="text" name="name" placeholder="আপনার নাম" required>
        <input type="email" name="email" placeholder="জিমেইল আইডি" required>
        <input type="password" name="password" placeholder="নতুন পাসওয়ার্ড" required>
        <button type="submit" class="btn" style="background: #34a853;">সাইনআপ করুন</button>
    </form>
    <p>অলরেডি অ্যাকাউন্ট আছে? <a href="/">লগইন করুন</a></p>
</div>
"""

DASHBOARD_HTML = BASE_STYLE + """
<div class="card">
    <div class="nav">
        <span>স্বাগতম, <b>{{ name }}</b></span>
        <a href="/logout" style="color: red; text-decoration: none;">লগআউট</a>
    </div>
    <div style="background: #e8f0fe; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <p style="margin: 0; color: #555;">আপনার বর্তমান ব্যালেন্স</p>
        <h1 style="margin: 5px 0; color: #1a73e8;">৳ {{ balance }}</h1>
    </div>
    
    <h3>আজকের কাজ (Tasks)</h3>
    <div style="text-align: left; border: 1px solid #eee; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
        <strong>Task #1: ইউটিউব ভিডিও দেখুন</strong>
        <p style="font-size: 13px; color: #666;">পুরস্কার: ৳ ২.০০</p>
        <a href="https://shrinkme.click/2NfYmRso" target="_blank" class="btn btn-task">কাজ শুরু করুন</a>
    </div>
    
    <div style="text-align: left; border: 1px solid #eee; padding: 15px; border-radius: 10px;">
        <strong>Task #2: CPA অফার পূরণ করুন</strong>
        <p style="font-size: 13px; color: #666;">পুরস্কার: ৳ ৫.০০</p>
        <a href="https://singingfiles.com/show.php?l=0&u=2529780&id=36521" target="_blank" class="btn btn-task">কাজ শুরু করুন</a>
    </div>
</div>
"""

# ৩. রাউটস (Logic)
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            error = "ভুল জিমেইল বা পাসওয়ার্ড!"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "এই জিমেইল দিয়ে অলরেডি অ্যাকাউন্ট খোলা হয়েছে!"
    return render_template_string(SIGNUP_HTML)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(DASHBOARD_HTML, name=user[1], balance=user[4])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
