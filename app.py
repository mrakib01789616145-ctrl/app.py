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

# ডিজাইনসহ মাস্টার এইচটিএমএল
MASTER_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head><meta charset="UTF-8"><title>APPLEX</title></head>
<body style="font-family:sans-serif; text-align:center; padding:20px; background:#f4f4f4;">
    <div style="background:white; padding:20px; border-radius:10px; max-width:400px; margin:auto;">
        <h2>APPLEX</h2>
        {% if page == 'dashboard' %}
            <h3>স্বাগতম, {{ user['name'] }}</h3>
            <p>আপনার ব্যালেন্স: ৳ {{ user['balance'] }}</p>
            <div style="margin:20px 0;">
                <a href="/complete_task/youtube" style="display:block; padding:12px; background:red; color:white; text-decoration:none; border-radius:5px; margin-bottom:10px;">YouTube সাবস্ক্রাইব (৳2)</a>
                <a href="/complete_task/telegram" style="display:block; padding:12px; background:blue; color:white; text-decoration:none; border-radius:5px;">Telegram জয়েন (৳2)</a>
            </div>
            <a href="/logout" style="color:red;">Logout</a>
        {% elif page == 'go_to_link' %}
            <h3>ধাপ ১: সাবস্ক্রাইব করুন</h3>
            <p>আগে লিঙ্কে গিয়ে কাজটি সম্পন্ন করুন</p>
            <a href="{{ link }}" target="_blank" style="padding:12px 20px; background:green; color:white; text-decoration:none; border-radius:5px;">লিঙ্কে যান (YouTube/Telegram)</a>
            <br><br>
            <a href="/verify_step/{{ task_type }}" style="padding:12px 20px; background:orange; color:white; text-decoration:none; border-radius:5px;">কাজ শেষ? এখানে ক্লিক করুন</a>
        {% elif page == 'verify_final' %}
            <h3>ধাপ ২: কনফার্ম করুন</h3>
            <p>আপনি কি কাজটি সম্পন্ন করেছেন?</p>
            <a href="/verify_task/{{ task_type }}" style="padding:15px; background:blue; color:white; text-decoration:none; border-radius:5px;">হ্যাঁ, আমি সাবস্ক্রাইব করেছি (টাকা নিন)</a>
        {% elif page == 'login' %}
            <form method="POST" action="/login">
                <input type="text" name="phone" placeholder="Phone" required style="padding:10px; width:80%; margin:5px;"><br>
                <input type="password" name="pass" placeholder="Password" required style="padding:10px; width:80%; margin:5px;"><br>
                <button type="submit" style="padding:10px 20px;">Login</button>
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
        user = db.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (request.form['phone'], request.form['pass'])).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return "ভুল ফোন বা পাসওয়ার্ড!"
    return render_template_string(MASTER_HTML, page='login')

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
    link = "https://youtube.com/@rakibteachofficial?si=0RAIeEgd1GNwKtAJ" if task_type == 'youtube' else "https://t.me/applex_income"
    return render_template_string(MASTER_HTML, page='go_to_link', link=link, task_type=task_type)

@app.route('/verify_step/<task_type>')
def verify_step(task_type):
    return render_template_string(MASTER_HTML, page='verify_final', task_type=task_type)

@app.route('/verify_task/<task_type>')
def verify_task(task_type):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    db.execute("UPDATE users SET balance = balance + 2 WHERE id = ?", (session['user_id'],))
    db.commit()
    db.close()
    return "টাস্ক সফল হয়েছে! <a href='/dashboard'>ড্যাশবোর্ডে ফিরে যান</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
