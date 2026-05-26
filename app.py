from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "applex_step_2_stable"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    # টেবিল আপডেট করা (যদি কলাম না থাকে তবে এরর হবে না)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN total_withdraw REAL DEFAULT 0")
    except: pass
    return conn

# --- প্রফেশনাল ইউজার ইন্টারফেস ---
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX - Home</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --blue: #007bff; --red: #d93025; --bg: #f8f9fa; }
        body { font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .header { background: white; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        
        .balance-card { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
        .balance-card h2 { margin: 10px 0; font-size: 32px; }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .menu-item { background: white; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; color: #333; border: 1px solid #eee; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
        .menu-item i { font-size: 24px; margin-bottom: 8px; display: block; }
        
        .nav-bar { position: fixed; bottom: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #ddd; max-width: 480px; left: 50%; transform: translateX(-50%); }
        .nav-link { color: #666; text-decoration: none; font-size: 11px; text-align: center; }
        .nav-link.active { color: var(--blue); }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <h3 style="margin:0; color:var(--red);"><i class="fas fa-apple-alt"></i> APPLEX</h3>
    </div>
    <div class="container">
        <div class="balance-card">
            <span style="opacity:0.8;">My Balance</span>
            <h2>৳ {{ user['balance'] }}</h2>
            <p style="font-size:12px; margin:0;">Welcome, {{ user['name'] }}</p>
        </div>

        <h4 style="margin-bottom:10px;">Earn Daily Reward</h4>
        <div class="grid">
            <a href="/task/youtube" class="menu-item"><i class="fab fa-youtube" style="color:red;"></i>YouTube Sub</a>
            <a href="/task/telegram" class="menu-item"><i class="fab fa-telegram" style="color:#0088cc;"></i>Telegram Join</a>
            <a href="/withdraw_page" class="menu-item"><i class="fas fa-wallet" style="color:green;"></i>Withdraw</a>
            <a href="#" class="menu-item" onclick="alert('Refer Code: REF{{ user['phone'][-4:] }}')"><i class="fas fa-users" style="color:orange;"></i>Refer Earn</a>
        </div>
    </div>

    <div class="nav-bar">
        <a href="/dashboard" class="nav-link active"><i class="fas fa-home"></i><br>Home</a>
        <a href="/withdraw_page" class="nav-link"><i class="fas fa-wallet"></i><br>Withdraw</a>
        <a href="/logout" class="nav-link"><i class="fas fa-sign-out-alt"></i><br>Logout</a>
    </div>

{% elif page == 'login' or page == 'signup' %}
    <div style="max-width:350px; margin: 80px auto; padding:30px; background:white; border-radius:20px; text-align:center; box-shadow:0 10px 25px rgba(0,0,0,0.05);">
        <h2 style="color:var(--red);"><i class="fas fa-apple-alt"></i> APPLEX</h2>
        <form method="POST" action="/{{ page }}">
            {% if page == 'signup' %}
                <input type="text" name="name" placeholder="Full Name" style="width:100%; padding:12px; margin:8px 0; border-radius:8px; border:1px solid #ddd; box-sizing:border-box;" required>
            {% endif %}
            <input type="text" name="phone" placeholder="Phone Number" style="width:100%; padding:12px; margin:8px 0; border-radius:8px; border:1px solid #ddd; box-sizing:border-box;" required>
            <input type="password" name="pass" placeholder="Password" style="width:100%; padding:12px; margin:8px 0; border-radius:8px; border:1px solid #ddd; box-sizing:border-box;" required>
            <button type="submit" style="width:100%; padding:12px; background:var(--blue); color:white; border:none; border-radius:8px; font-weight:bold; margin-top:10px;">{{ 'Create Account' if page == 'signup' else 'Login Now' }}</button>
        </form>
        <p style="font-size:14px; margin-top:15px;"><a href="/{{ 'login' if page == 'signup' else 'signup' }}" style="color:#666;">{{ 'Already have account? Login' if page == 'signup' else 'New here? Create Account' }}</a></p>
    </div>
{% endif %}

</body>
</html>
"""

# --- সার্ভার রুটস ---

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, phone, password, balance) VALUES (?, ?, ?, ?)", 
                       (request.form['name'], request.form['phone'], request.form['pass'], 0))
            db.commit()
            return redirect(url_for('login'))
        except: return "Number already exists!"
        finally: db.close()
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE phone = ? AND password = ?", 
                          (request.form['phone'], request.form['pass'])).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return "ভুল ফোন বা পাসওয়ার্ড! <a href='/login'>আবার চেষ্টা করুন</a>"
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/task/<type>')
def complete_task(type):
    if 'user_id' not in session: return redirect(url_for('login'))
    reward = 5.0  # প্রতি টাস্কে ৫ টাকা
    db = get_db()
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (reward, session['user_id']))
    db.commit()
    db.close()
    # এখানে আপনার ইউটিউব বা টেলিগ্রাম লিঙ্ক দিন
    url = "https://youtube.com/@YourChannel" if type == 'youtube' else "https://t.me/YourGroup"
    return redirect(url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
