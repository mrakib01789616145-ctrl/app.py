from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "applex_final_fixed_v7"

# ১. ডাটাবেজ ফাংশন
def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

# ২. ড্যাশবোর্ড, লগইন এবং সাইন-আপ ডিজাইন (সব পেজ এক সাথে)
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
        .container { max-width: 480px; margin: auto; padding: 15px; padding-bottom: 80px; }
        .card { background: white; border-radius: 15px; padding: 25px; margin-top: 50px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; }
        .input-field { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; outline: none; }
        .btn-primary { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .logo { font-size: 32px; font-weight: 900; margin-bottom: 10px; }
        .logo i { color: var(--primary); }
    </style>
</head>
<body>

{% if page == 'dashboard' %}
    <div style="padding:20px;">
        <h3>Welcome, {{ user['first_name'] }}</h3>
        <p>ব্যালেন্স বক্সগুলো এখানে দেখা যাবে...</p>
        <a href="/logout">Logout</a>
    </div>

{% elif page == 'login' %}
    <div class="container">
        <div class="card">
            <div class="logo"><i class="fas fa-apple-alt"></i> APPLEX</div>
            <h3>Login Account</h3>
            {% if error %}<p style="color:red; font-size:13px;">{{ error }}</p>{% endif %}
            <form method="POST" action="/login">
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
            <h3>Create Account</h3>
            {% if error %}<p style="color:red; font-size:13px;">{{ error }}</p>{% endif %}
            <form method="POST" action="/signup">
                <input type="text" name="f_name" class="input-field" placeholder="First Name" required>
                <input type="tel" name="phone" class="input-field" placeholder="Phone Number" required>
                <input type="password" name="pass" class="input-field" placeholder="Password" required>
                <button type="submit" class="btn-primary">Sign Up</button>
            </form>
            <p style="font-size:13px; margin-top:15px;">Already have account? <a href="/login">Login</a></p>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('pass')
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()
        
        # পাসওয়ার্ড চেক করার সময় আগের সেভ করা পাসওয়ার্ডের সাথে মেলানো হচ্ছে
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template_string(MASTER_HTML, page='login', error="ভুল নম্বর বা পাসওয়ার্ড!")
    return render_template_string(MASTER_HTML, page='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        phone = request.form.get('phone')
        password = generate_password_hash(request.form.get('pass'))
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (first_name, phone, password) VALUES (?,?,?)", (f_name, phone, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return render_template_string(MASTER_HTML, page='signup', error="এই নম্বর দিয়ে অ্যাকাউন্ট আছে!")
    return render_template_string(MASTER_HTML, page='signup')

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
