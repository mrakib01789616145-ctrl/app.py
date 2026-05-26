from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_step_by_step_v2"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0, total_withdraw REAL DEFAULT 0)''')
    conn.commit()
    return conn

# নতুন ড্যাশবোর্ড ডিজাইন এবং লগইন পেজ
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Home</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; margin: 0; }
        .header { background: white; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-weight: bold; color: #d93025; font-size: 24px; }
        .container { max-width: 400px; margin: 20px auto; padding: 15px; }
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); text-align: center; margin-bottom: 15px; }
        .balance-title { font-size: 14px; color: #666; margin: 0; }
        .balance-amount { font-size: 32px; font-weight: bold; color: #007bff; margin: 10px 0; }
        .user-info { font-size: 16px; color: #333; margin-top: 10px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; }
        .logout-btn { background: #6c757d; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">APPLEX</div>
    <div class="container">
        
        {% if page == 'dashboard' %}
            <div class="card">
                <div class="user-info">স্বাগতম, <b>{{ user['name'] }}</b></div>
                <hr style="border: 0.5px solid #eee; margin: 15px 0;">
                <p class="balance-title">আপনার বর্তমান ব্যালেন্স</p>
                <div class="balance-amount">৳ {{ user['balance'] }}</div>
            </div>
            
            <div class="card">
                <p style="color: #888; font-size: 14px;">টাস্ক এবং উইথড্র অপশন পরবর্তী ধাপে আসবে।</p>
                <a href="/logout" class="btn logout-btn">লগ আউট</a>
            </div>

        {% elif page == 'login' or page == 'signup' %}
            <div class="card">
                <h2>{{ 'অ্যাকাউন্ট খুলুন' if page == 'signup' else 'লগইন করুন' }}</h2>
                <form method="POST" action="{{ '/signup' if page == 'signup' else '/login' }}">
                    {% if page == 'signup' %}
                        <input type="text" name="name" placeholder="আপনার নাম" required>
                        <input type="email" name="email" placeholder="ইমেইল" required>
                    {% endif %}
                    <input type="tel" name="phone" placeholder="ফোন নম্বর" required>
                    <input type="password" name="pass" placeholder="পাসওয়ার্ড" required>
                    <button type="submit" class="btn">{{ 'নিবন্ধন করুন' if page == 'signup' else 'প্রবেশ করুন' }}</button>
                </form>
                <a href="{{ '/login' if page == 'signup' else '/signup' }}" style="font-size: 13px; color: #666; text-decoration: none; margin-top: 15px; display: block;">
                    {{ 'আগে থেকে অ্যাকাউন্ট আছে? লগইন করুন' if page == 'signup' else 'নতুন ইউজার? অ্যাকাউন্ট খুলুন' }}
                </a>
            </div>
        {% endif %}

    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
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
        except: return "এই ফোন নম্বরটি ইতিমধ্যে ব্যবহৃত হয়েছে!"
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
        return "ভুল ফোন নম্বর বা পাসওয়ার্ড!"
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
