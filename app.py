from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_secure_v100"

# ডাটাবেজ কানেকশন এবং টেবিল প্রোটেকশন
def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    # IF NOT EXISTS নিশ্চিত করে যে ডাটা মুছবে না
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0, total_withdraw REAL DEFAULT 0)''')
    conn.commit()
    return conn

# সাইন-আপ ও লগইন ডিজাইন
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Access</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); width: 320px; text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .toggle-link { font-size: 14px; margin-top: 15px; display: block; color: #666; text-decoration: none; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color:#d93025;">APPLEX</h2>
        
        {% if page == 'signup' %}
            <form method="POST" action="/signup">
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="tel" name="phone" placeholder="Phone Number" required>
                <input type="password" name="pass" placeholder="Create Password" required>
                <button type="submit" class="btn">Create Account</button>
            </form>
            <a href="/login" class="toggle-link">Already have an account? Login</a>
        {% else %}
            <form method="POST" action="/login">
                <input type="tel" name="phone" placeholder="Phone Number" required>
                <input type="password" name="pass" placeholder="Password" required>
                <button type="submit" class="btn">Login Now</button>
            </form>
            <a href="/signup" class="toggle-link">New user? Create Account</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' in session: return "Success! You are logged in." # পরবর্তীতে ড্যাশবোর্ড এড হবে
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
        except: return "এই ফোন নম্বর দিয়ে আগে থেকেই অ্যাকাউন্ট খোলা আছে!"
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
            return redirect(url_for('index'))
        return "ভুল ফোন নম্বর বা পাসওয়ার্ড!"
    return render_template_string(MASTER_HTML, page='login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
