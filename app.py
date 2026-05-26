from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "premium_key_99"

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

# ২. আধুনিক ডিজাইন (CSS + HTML)
NEW_DESIGN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoinStack - Earn Money</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #1a73e8; --secondary: #34a853; --dark: #202124; --light: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: #f0f4f8; margin: 0; padding: 0; color: var(--dark); }
        
        /* Header */
        .header { background: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); sticky: top; }
        .logo { font-size: 22px; font-weight: bold; color: var(--primary); display: flex; align-items: center; gap: 8px; }
        .logout-btn { text-decoration: none; color: #d93025; font-weight: 600; border: 1px solid #d93025; padding: 5px 15px; border-radius: 20px; font-size: 14px; }

        .container { max-width: 450px; margin: auto; padding: 20px; }

        /* Welcome Section */
        .welcome-sec { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .user-icon { font-size: 40px; color: #bdc1c6; }

        /* Wallet Card */
        .wallet-card { 
            background: linear-gradient(135deg, #1a73e8, #0d47a1); 
            color: white; padding: 25px; border-radius: 20px; 
            text-align: center; box-shadow: 0 10px 20px rgba(26, 115, 232, 0.3);
            position: relative; overflow: hidden;
        }
        .wallet-card::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); }
        .wallet-card p { font-size: 14px; opacity: 0.9; margin: 0; }
        .wallet-card h1 { font-size: 36px; margin: 10px 0; }
        .wallet-card span { font-size: 14px; background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 15px; }

        /* Task Section */
        .section-title { font-size: 18px; font-weight: 700; margin: 25px 0 15px; display: flex; align-items: center; gap: 10px; }
        
        .task-card { 
            background: white; border-radius: 15px; padding: 15px; 
            margin-bottom: 15px; display: flex; align-items: center; gap: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: 0.3s; border: 1px solid #eee;
        }
        .task-card:hover { transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.05); }
        .task-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
        .yt-icon { background: #feebeb; color: #d93025; }
        .cpa-icon { background: #e6f4ea; color: #1e8e3e; }
        
        .task-info { flex-grow: 1; }
        .task-info h4 { margin: 0; font-size: 15px; }
        .task-info p { margin: 3px 0 0; font-size: 13px; color: #5f6368; }
        .task-reward { font-weight: bold; color: var(--secondary); font-size: 14px; }

        .go-btn { background: var(--secondary); color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; text-decoration: none; font-size: 13px; }

        /* Auth Pages */
        .auth-card { background: white; padding: 40px 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center; }
        .auth-input { width: 100%; padding: 14px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; font-size: 16px; outline: none; transition: 0.3s; }
        .auth-input:focus { border-color: var(--primary); }
        .auth-btn { width: 100%; padding: 14px; background: var(--primary); color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-coins"></i> CoinStack</div>
        <a href="/logout" class="logout-btn">লগআউট <i class="fas fa-sign-out-alt"></i></a>
    </div>

    <div class="container">
        <div class="welcome-sec">
            <div>
                <h3 style="margin:0;">স্বাগতম, {{ name }}</h3>
                <p style="margin:0; font-size: 13px; color: #5f6368;">আপনার সম্ভাবনা বৃদ্ধি করুন!</p>
            </div>
            <div class="user-icon"><i class="fas fa-user-circle"></i></div>
        </div>

        <div class="wallet-card">
            <p>Digital Wallet Card</p>
            <h1>৳ {{ balance }}</h1>
            <span>Available Coins: 0</span>
        </div>

        <div class="section-title"><i class="fas fa-tasks" style="color: var(--primary);"></i> Your Earnings Hub</div>

        <div class="task-card">
            <div class="task-icon yt-icon"><i class="fab fa-youtube"></i></div>
            <div class="task-info">
                <h4>ইউটিউব ভিডিও দেখুন</h4>
                <p class="task-reward">পুরস্কার: ৳ ২.০০</p>
            </div>
            <a href="YOUR_YT_LINK" target="_blank" class="go-btn">শুরু করুন</a>
        </div>

        <div class="task-card">
            <div class="task-icon cpa-icon"><i class="fas fa-mobile-alt"></i></div>
            <div class="task-info">
                <h4>CPA অফার পূরণ করুন</h4>
                <p class="task-reward">পুরস্কার: ৳ ৫.০০</p>
            </div>
            <a href="YOUR_CPA_LINK" target="_blank" class="go-btn">শুরু করুন</a>
        </div>
    </div>

{% elif page == 'login' %}
    <div style="height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div class="auth-card" style="width: 100%; max-width: 350px;">
            <h2 style="color: var(--primary);"><i class="fas fa-coins"></i> CoinStack</h2>
            <p>লগইন করে আয় শুরু করুন</p>
            {% if error %}<p style="color: red; font-size: 13px;">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="email" name="email" class="auth-input" placeholder="জিমেইল" required>
                <input type="password" name="password" class="auth-input" placeholder="পাসওয়ার্ড" required>
                <button type="submit" class="auth-btn">লগইন</button>
            </form>
            <p style="font-size: 14px; margin-top: 20px;">অ্যাকাউন্ট নেই? <a href="/signup" style="color: var(--primary); text-decoration: none; font-weight: bold;">সাইনআপ</a></p>
        </div>
    </div>

{% elif page == 'signup' %}
    <div style="height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div class="auth-card" style="width: 100%; max-width: 350px;">
            <h2 style="color: var(--secondary);"><i class="fas fa-user-plus"></i> Join Us</h2>
            <p>সহজে অ্যাকাউন্ট তৈরি করুন</p>
            <form method="POST">
                <input type="text" name="name" class="auth-input" placeholder="পূর্ণ নাম" required>
                <input type="email" name="email" class="auth-input" placeholder="জিমেইল" required>
                <input type="password" name="password" class="auth-input" placeholder="পাসওয়ার্ড" required>
                <button type="submit" class="auth-btn" style="background: var(--secondary);">সাইনআপ</button>
            </form>
            <p style="font-size: 14px; margin-top: 20px;">অ্যাকাউন্ট আছে? <a href="/" style="color: var(--secondary); text-decoration: none; font-weight: bold;">লগইন</a></p>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

# ৩. রাউটস (লজিক আগের মতোই থাকবে)
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
            session['user_id'], session['user_name'] = user[0], user[1]
            return redirect(url_for('dashboard'))
        error = "ভুল তথ্য!"
    return render_template_string(NEW_DESIGN, page='login', error=error)

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
        except: return "জিমেইলটি ইতিমধ্যে ব্যবহৃত!"
    return render_template_string(NEW_DESIGN, page='signup')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(NEW_DESIGN, page='dashboard', name=user[1], balance=user[4])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
