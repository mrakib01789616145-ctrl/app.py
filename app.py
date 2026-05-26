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

# ২. প্রোফাইল এডিট সহ নতুন ডিজাইন
DESIGN_WITH_PROFILE = """
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
        
        .header { background: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .logo { font-size: 20px; font-weight: bold; color: var(--primary); display: flex; align-items: center; gap: 8px; }
        .logout-btn { text-decoration: none; color: #d93025; font-weight: 600; border: 1px solid #d93025; padding: 5px 12px; border-radius: 20px; font-size: 12px; }

        .container { max-width: 450px; margin: auto; padding: 20px; }

        /* Wallet Card */
        .wallet-card { 
            background: linear-gradient(135deg, #1a73e8, #0d47a1); 
            color: white; padding: 25px; border-radius: 20px; 
            text-align: center; box-shadow: 0 10px 20px rgba(26, 115, 232, 0.3);
            margin-bottom: 25px;
        }
        .wallet-card h1 { font-size: 36px; margin: 10px 0; }

        /* Profile Section */
        .profile-sec { background: white; padding: 15px; border-radius: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; border: 1px solid #eee; }
        .edit-link { font-size: 13px; color: var(--primary); text-decoration: none; font-weight: 600; }

        /* Task Card */
        .task-card { 
            background: white; border-radius: 15px; padding: 15px; 
            margin-bottom: 12px; display: flex; align-items: center; gap: 15px;
            border: 1px solid #eee;
        }
        .task-icon { width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .task-info { flex-grow: 1; }
        .go-btn { background: var(--secondary); color: white; border: none; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; }

        /* Form Styling */
        .auth-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center; }
        .auth-input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; outline: none; }
        .auth-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div class="header">
        <div class="logo"><i class="fas fa-coins"></i> CoinStack</div>
        <a href="/logout" class="logout-btn">লগআউট <i class="fas fa-sign-out-alt"></i></a>
    </div>

    <div class="container">
        <div class="profile-sec">
            <div>
                <p style="margin:0; font-size: 12px; color: #666;">স্বাগতম,</p>
                <h3 style="margin:0;">{{ name }}</h3>
            </div>
            <a href="/edit-profile" class="edit-link"><i class="fas fa-user-edit"></i> প্রোফাইল এডিট</a>
        </div>

        <div class="wallet-card">
            <p style="margin:0; font-size: 13px; opacity: 0.9;">Digital Wallet Balance</p>
            <h1>৳ {{ balance }}</h1>
            <span style="background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:10px; font-size:12px;">Available Coins: 0</span>
        </div>

        <h4 style="margin: 20px 0 10px;"><i class="fas fa-bolt" style="color: #fbbc04;"></i> আজকের কাজ</h4>
        
        <div class="task-card">
            <div class="task-icon" style="background:#feebeb; color:#d93025;"><i class="fab fa-youtube"></i></div>
            <div class="task-info">
                <h4 style="margin:0; font-size:14px;">ইউটিউব ভিডিও দেখুন</h4>
                <p style="margin:0; font-size:12px; color:var(--secondary);">পুরস্কার: ৳ ২.০০</p>
            </div>
            <a href="#" class="go-btn">শুরু করুন</a>
        </div>

        <div class="task-card">
            <div class="task-icon" style="background:#e6f4ea; color:#1e8e3e;"><i class="fas fa-mobile-alt"></i></div>
            <div class="task-info">
                <h4 style="margin:0; font-size:14px;">CPA অফার পূরণ করুন</h4>
                <p style="margin:0; font-size:12px; color:var(--secondary);">পুরস্কার: ৳ ৫.০০</p>
            </div>
            <a href="#" class="go-btn">শুরু করুন</a>
        </div>
    </div>

{% elif page == 'edit_profile' %}
    <div style="height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div class="auth-card" style="width: 100%; max-width: 350px;">
            <h3>প্রোফাইল আপডেট</h3>
            <form method="POST">
                <label style="display:block; text-align:left; font-size:13px; color:#666;">আপনার নাম পরিবর্তন করুন:</label>
                <input type="text" name="new_name" class="auth-input" value="{{ name }}" required>
                <button type="submit" class="auth-btn">আপডেট করুন</button>
            </form>
            <br>
            <a href="/dashboard" style="text-decoration:none; color:#666; font-size:14px;">ফিরে যান</a>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

# ৩. রাউটস (লজিক)
@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('signup')) # সরাসরি সাইনআপ পেজে পাঠাবে

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # সাইনআপ লজিক (আগের মতোই)
    if request.method == 'POST':
        name, email, password = request.form['name'], request.form['email'], request.form['password']
        try:
            conn = sqlite3.connect('users.db')
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        except: return "Error: Email already exists."
    return render_template_string(DESIGN_WITH_PROFILE, page='signup')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: 
        # ডেমো ইউজার যদি না থাকে (আপনার সুবিধার জন্য)
        session['user_id'] = 1 
        session['user_name'] = "Rakib"
    
    conn = sqlite3.connect('users.db')
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(DESIGN_WITH_PROFILE, page='dashboard', name=user[1], balance=user[4])

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    if request.method == 'POST':
        new_name = request.form['new_name']
        conn.execute("UPDATE users SET name=? WHERE id=?", (new_name, session['user_id']))
        conn.commit()
        session['user_name'] = new_name
        conn.close()
        return redirect(url_for('dashboard'))
    
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(DESIGN_WITH_PROFILE, page='edit_profile', name=user[1])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
