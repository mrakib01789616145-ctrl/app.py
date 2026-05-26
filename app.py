from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "applex_final_2026_pro"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, phone TEXT UNIQUE, password TEXT, 
                  balance REAL DEFAULT 0)''')
    conn.commit()
    return conn

# মাস্টার এইচটিএমএল ডিজাইন
MASTER_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head><meta charset="UTF-8"><title>APPLEX Dashboard</title></head>
<body style="font-family:sans-serif; text-align:center; padding:20px; background:#f4f4f4;">
    <div style="background:white; padding:20px; border-radius:10px; max-width:400px; margin:auto;">
        <h2>APPLEX</h2>
        {% if page == 'dashboard' %}
            <h3 style="color:#333;">স্বাগতম, {{ user['name'] }}</h3>
            <p style="font-size:20px; color:blue;">আপনার ব্যালেন্স: ৳ {{ user['balance'] }}</p>
            
            <div style="margin:20px 0;">
                <p>টাস্ক সম্পন্ন করে আয় করুন:</p>
                <a href="/complete_task/youtube" style="display:block; padding:12px; background:red; color:white; text-decoration:none; border-radius:5px; margin-bottom:10px;">YouTube সাবস্ক্রাইব (৳2)</a>
                <a href="/complete_task/telegram" style="display:block; padding:12px; background:blue; color:white; text-decoration:none; border-radius:5px;">Telegram জয়েন (৳2)</a>
            </div>
            <a href="/logout" style="color:red;">Logout</a>
        {% elif page == 'login' %}
            <form method="POST" action="/login">
                <input type="text" name="phone" placeholder="Phone Number" required style="padding:10px; width:80%; margin:5px;"><br>
                <input type="password" name="pass" placeholder="Password" required style="padding:10px; width:80%; margin:5px;"><br>
                <button type="submit" style="padding:10px 20px;">Login</button>
            </form>
            <p><a href="/signup">নতুন একাউন্ট খুলুন</a></p>
        {% elif page == 'signup' %}
            <form method="POST" action="/signup">
                <input type="text" name="name" placeholder="Name" required style="padding:10px; width:80%; margin:5px;"><br>
                <input type="text" name="phone" placeholder="Phone" required style="padding:10px; width:80%; margin:5px;"><br>
                <input type="password" name="pass" placeholder="Password" required style="padding:10px; width:80%; margin:5px;"><br>
                <button type="submit" style="padding:10px 20px;">Sign Up</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

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
        return "ভুল ফোন বা পাসওয়ার্ড!"
    return render_template_string(MASTER_HTML, page='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            db = get_db()
            db.execute("INSERT INTO users (name, phone, password, balance) VALUES (?, ?, ?, 0)", 
                       (request.form['name'], request.form['phone'], request.form['pass']))
            db.commit()
            db.close()
            return redirect(url_for('login'))
        except: return "এই নম্বরটি ইতিমধ্যে ব্যবহৃত হয়েছে!"
    return render_template_string(MASTER_HTML, page='signup')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/complete_task/<task_type>')
def complete_task(task_type):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    db.execute("UPDATE users SET balance = balance + 2 WHERE id = ?", (session['user_id'],))
    db.commit()
    db.close()
    
    # এখানে আপনার লিঙ্কগুলো বসিয়ে দিন
    if task_type == 'youtube':
        return redirect("https://youtube.com/@rakibteachofficial?si=XKb75CYFD5bOeAdm") 
    else:
        return redirect("https://t.me/applex_income")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
# এটি app.py ফাইলের শেষে যুক্ত করুন

@app.route('/withdraw_page', methods=['GET', 'POST'])
def withdraw_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    message = ""

    if request.method == 'POST':
        amount = float(request.form['amount'])
        if amount >= 50: # মিনিমাম উইথড্র ৫০ টাকা
            if user['balance'] >= amount:
                db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, session['user_id']))
                db.commit()
                message = "সফলভাবে উইথড্র রিকোয়েস্ট পাঠানো হয়েছে!"
            else:
                message = "আপনার পর্যাপ্ত ব্যালেন্স নেই।"
        else:
            message = "মিনিমাম উইথড্র ৫০ টাকা।"
    
    db.close()
    
    # উইথড্র পেজের ডিজাইন
    withdraw_html = f"""
    <div style="text-align:center; padding:20px;">
        <h3>উইথড্র পেজ</h3>
        <p>আপনার ব্যালেন্স: ৳ {user['balance']}</p>
        <p style="color:red;">{message}</p>
        <form method="POST">
            <input type="number" name="amount" placeholder="৳ ৫০ বা তার বেশি" required style="padding:10px;"><br><br>
            <button type="submit" style="padding:10px 20px;">উইথড্র করুন</button>
        </form>
        <br><a href="/dashboard">ড্যাশবোর্ডে ফিরে যান</a>
    </div>
    """
    return render_template_string(MASTER_HTML.replace('{% if page == \'dashboard\' %}', withdraw_html))
    
