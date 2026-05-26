from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_persistent_v101"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    # টেবিল থাকলে নতুন করে তৈরি করবে না, ডাটা সুরক্ষিত থাকবে
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0, total_withdraw REAL DEFAULT 0)''')
    conn.commit()
    return conn

# ড্যাশবোর্ডসহ আপডেট করা ডিজাইন
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>APPLEX - Dashboard</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 320px; text-align: center; }
        .btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; text-decoration: none; display: inline-block; }
    </style>
</head>
<body>
    <div class="card">
        {% if page == 'dashboard' %}
            <h2 style="color:#d93025;">APPLEX</h2>
            <p>স্বাগতম, <b>{{ user['name'] }}</b></p>
            <h3 style="color:#007bff;">ব্যালেন্স: ৳ {{ user['balance'] }}</h3>
            <a href="/logout" class="btn" style="background:#6c757d;">লগ আউট</a>
        {% else %}
            <h2 style="color:#d93025;">APPLEX</h2>
            <form method="POST" action="{{ '/signup' if page == 'signup' else '/login' }}">
                {% if page == 'signup' %}
                    <input type="text" name="name" placeholder="Full Name" required style="width:100%; padding:10px; margin:5px 0;">
                    <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin:5px 0;">
                {% endif %}
                <input type="tel" name="phone" placeholder="Phone Number" required style="width:100%; padding:10px; margin:5px 0;">
                <input type="password" name="pass" placeholder="Password" required style="width:100%; padding:10px; margin:5px 0;">
                <button type="submit" class="btn">Submit</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

# (সাইন-আপ এবং লগইন রুট একই থাকবে)
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
        except: return "এই নম্বর দিয়ে আগে থেকেই অ্যাকাউন্ট খোলা আছে!"
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
