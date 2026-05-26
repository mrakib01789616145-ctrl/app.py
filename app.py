from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_final_fixed_secure_v9"

# ১. ডাটাবেজ কানেকশন এবং টেবিল সেটআপ
def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # এখানে আমরা নিশ্চিত করছি যে টেবিল এবং কলামগুলো ঠিক আছে
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      first_name TEXT, phone TEXT UNIQUE, password TEXT, 
                      refer_bal REAL DEFAULT 0.0, salary_bal REAL DEFAULT 0.0,
                      job_bal REAL DEFAULT 0.0, total_earn REAL DEFAULT 0.0,
                      total_withdraw REAL DEFAULT 0.0, free_earn REAL DEFAULT 0.0,
                      level TEXT DEFAULT 'Free')''')
    conn.commit()
    conn.close()

init_db()

# ২. ড্যাশবোর্ড ও লগইন ইন্টারফেস ডিজাইন
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APPLEX</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #d93025; --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg); margin: 0; padding: 0; }
        .container { max-width: 480px; margin: auto; padding: 15px; }
        .card { background: white; border-radius: 15px; padding: 25px; margin-top: 50px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; }
        .input-field { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .logo { font-size: 32px; font-weight: 900; margin-bottom: 10px; }
        .logo i { color: var(--primary); }
        .balance-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 15px; }
        .bal-box { background: white; padding: 15px 5px; border-radius: 12px; text-align: center; border: 1px solid #eee; }
        .bal-box p { margin: 5px 0 0; color: var(--blue); font-weight: bold; font-size: 11px; }
    </style>
</head>
<body>

{% if page == 'login' %}
    <div class="container">
        <div class="card">
            <div class="logo"><i class="fas fa-apple-alt"></i> APPLEX</div>
            <h3>Login Account</h3>
            {% if error %}<p style="color:red; font-size:13px;">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
                <input type="password" name="pass" class="input-field" placeholder="Password" required>
                <button type="submit" class="btn-primary">Login Now</button>
            </form>
            <p style="font-size:13px; margin-top:15px;">New member? <a href="/signup">Create Account</a></p>
        </div>
    </div>

{% elif page == 'signup' %}
    <div class="container">
        <div class="card">
            <div class="logo"><i class="fas fa-apple-alt"></i> APPLEX</div>
            <h3>Sign Up</h3>
            {% if error %}<p style="color:red; font-size:13px;">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="text" name="f_name" class="input-field" placeholder="Your Name" required>
                <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
                <input type="password" name="pass" class="input-field" placeholder="Password" required>
                <button type="submit" class="btn-primary">Create Account</button>
            </form>
            <p style="font-size:13px; margin-top:15px;">Already have account? <a href="/login">Login</a></p>
        </div>
    </div>

{% elif page == 'dashboard' %}
    <div class="container">
        <div style="background:white; padding:15px; border-radius:15px; margin-top:20px;">
            <h4>Welcome, {{ user['first_name'] }}</h4>
            <div class="balance-grid">
                <div class="bal-box"><b>Tk. {{ user['refer_bal'] }}</b><p>Refer</p></div>
                <div class="bal-box"><b>Tk. {{ user['salary_bal'] }}</b><p>Salary</p></div>
                <div class="bal-box"><b>Tk. {{ user['job_bal'] }}</b><p>Job</p></div>
                <div class="bal-box"><b>Tk. {{ user['total_earn'] }}</b><p>Earn</p></div>
                <div class="bal-box"><b>Tk. {{ user['total_withdraw'] }}</b><p>Withdraw</p></div>
                <div class="bal-box"><b>Tk. {{ user['free_earn'] }}</b><p>Free</p></div>
            </div>
            <br>
            <a href="/logout" style="color:red; text-decoration:none;">Logout</a>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

# --- রাউটস (Routes) ---

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('f_name')
        phone = request.form.get('phone')
        # পাসওয়ার্ডটি এনক্রিপ্ট করা হচ্ছে যাতে এটি নিরাপদে ডাটাবেজে থাকে
        password = generate_password_hash(request.form.get('pass'))
        
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (first_name, phone, password) VALUES (?, ?, ?)", (name, phone, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return render_template_string(MASTER_HTML, page='signup', error="এই নম্বর দিয়ে আইডি অলরেডি আছে!")
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('pass')
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()
        
        # এখানে পাসওয়ার্ড এবং ফোন নম্বর হুবহু ম্যাচ করানো হচ্ছে
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(MASTER_HTML, page='login', error="ভুল নম্বর বা পাসওয়ার্ড!")
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
