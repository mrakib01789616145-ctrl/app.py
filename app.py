from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_persistent_v101"

# ডাটাবেজ কানেকশন এবং টেবিল প্রোটেকশন
def get_db():
    # এই ফাইলটি আপনার সব ডাটা সেভ করে রাখবে
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    # IF NOT EXISTS ব্যবহার করা হয়েছে যাতে ডাটা রিসেট না হয়
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0, total_withdraw REAL DEFAULT 0)''')
    conn.commit()
    return conn

# সাইন-আপ ও লগইন ডিজাইন (বর্ডার এবং শ্যাডোসহ প্রফেশনাল লুক)
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Login/Signup</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 100%; max-width: 350px; text-align: center; }
        .logo { font-size: 28px; font-weight: bold; color: #d93025; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 16px; }
        .btn { width: 100%; padding: 14px; background: #007bff; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }
        .btn:hover { background: #0056b3; }
        .toggle-link { font-size: 14px; margin-top: 20px; display: block; color: #666; text-decoration: none; }
        .error { color: red; font-size: 14px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">APPLEX</div>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        {% if page == 'signup' %}
            <form method="POST" action="/signup">
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="tel" name="phone" placeholder="Phone Number" required>
                <input type="password" name="pass" placeholder="Create Password" required>
                <button type="submit" class="btn">Create Account</button>
            </form>
            <a href="/login" class="toggle-link">Already a member? Login</a>
        {% else %}
            <form method="POST" action="/login">
                <input type="tel" name="phone" placeholder="Phone Number" required>
                <input type="password" name="pass" placeholder="Password" required>
                <button type="submit" class="btn">Login Now</button>
            </form>
            <a href="/signup" class="toggle-link">New member? Create Account</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' in session:
        return "Loging Success! Your data is safe."
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name, email, phone, pwd = request.form['name'], request.form['email'], request.form['phone'], request.form['pass']
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)", 
                       (name, email, phone, generate_password_hash(pwd)))
            db.commit()
            return redirect(url_for('login'))
        except:
            error = "এই ফোন নম্বরটি ইতিমধ্যে ব্যবহৃত হয়েছে!"
        finally:
            db.close()
    return render_template_string(MASTER_HTML, page='signup', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        phone, pwd = request.form['phone'], request.form['pass']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], pwd):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        error = "ভুল ফোন নম্বর বা পাসওয়ার্ড!"
    return render_template_string(MASTER_HTML, page='login', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
