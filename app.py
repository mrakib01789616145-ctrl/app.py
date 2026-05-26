from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "applex_final_2026_pro"

# ... (get_db ফাংশন আগের মতোই থাকবে) ...

MASTER_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head><meta charset="UTF-8"><title>APPLEX Earning</title></head>
<body style="font-family:sans-serif; text-align:center; padding:20px; background:#f4f4f4;">
    <div style="background:white; padding:20px; border-radius:15px; max-width:400px; margin:auto;">
        <h2>APPLEX Tasks</h2>
        {% if page == 'dashboard' %}
            <p>ব্যালেন্স: ৳ {{ user['balance'] }}</p>
            <div style="margin:20px 0;">
                <a href="/task/video" style="display:block; padding:12px; background:red; color:white; text-decoration:none; border-radius:8px; margin-bottom:10px;">ভিডিও দেখুন (৳10)</a>
                <a href="/task/app" style="display:block; padding:12px; background:green; color:white; text-decoration:none; border-radius:8px;">অ্যাপ ইন্সটল (৳5)</a>
            </div>
            <a href="/logout">Logout</a>
        {% elif page == 'task_instruction' %}
            <h3>{{ title }}</h3>
            <p>{{ instruction }}</p>
            <a href="{{ link }}" target="_blank" style="padding:10px; background:blue; color:white; text-decoration:none; border-radius:5px;">লিঙ্কে যান</a>
            <br><br>
            <a href="/verify/{{ task_type }}" style="padding:10px; background:orange; color:white; text-decoration:none; border-radius:5px;">আমি কাজটি সম্পন্ন করেছি</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/task/<task_type>')
def task(task_type):
    if 'user_id' not in session: return redirect(url_for('login'))
    if task_type == 'video':
        return render_template_string(MASTER_HTML, page='task_instruction', title="৫ মিনিট ভিডিও দেখুন", 
                                      instruction="ভিডিওটি সম্পূর্ণ ৫ মিনিট দেখুন, অন্যথায় ব্যালেন্স যোগ হবে না।", 
                                      link="https://youtube.com/@rakibteachofficial", task_type='video')
    else:
        return render_template_string(MASTER_HTML, page='task_instruction', title="অ্যাপ ডাউনলোড করুন", 
                                      instruction="CPAGrip লিঙ্ক থেকে অ্যাপটি ডাউনলোড করে ওপেন করুন।", 
                                      link="YOUR_CPAGRIP_LINK_HERE", task_type='app')

@app.route('/verify/<task_type>')
def verify(task_type):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    amount = 10 if task_type == 'video' else 5
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, session['user_id']))
    db.commit()
    db.close()
    return f"টাস্ক সম্পন্ন! ৳{amount} যোগ করা হয়েছে। <a href='/dashboard'>ড্যাশবোর্ডে ফিরে যান</a>"

# ... (অন্যান্য রুট আগের মতোই থাকবে) ...
