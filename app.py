from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "applex_debug_v1"

def get_db():
    conn = sqlite3.connect('applex_main.db')
    conn.row_factory = sqlite3.Row
    return conn

MASTER_HTML = """
<!DOCTYPE html>
<html>
<body>
    <h2>APPLEX</h2>
    {% if page == 'login' %}
        <form method="POST" action="/login">
            <input type="text" name="phone" placeholder="Phone" required>
            <input type="password" name="pass" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <a href="/signup">Sign Up</a>
    {% elif page == 'signup' %}
        <form method="POST" action="/signup">
            <input type="text" name="name" placeholder="Name" required>
            <input type="text" name="phone" placeholder="Phone" required>
            <input type="password" name="pass" placeholder="Password" required>
            <button type="submit">Sign Up</button>
        </form>
    {% elif page == 'dashboard' %}
        <h3>Welcome, {{ user['name'] }}</h3>
        <p>Balance: {{ user['balance'] }}</p>
        <a href="/logout">Logout</a>
    {% endif %}
</body>
</html>
"""

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = get_db()
        db.execute("INSERT INTO users (name, phone, password, balance) VALUES (?, ?, ?, ?)", 
                   (request.form['name'], request.form['phone'], request.form['pass'], 0))
        db.commit()
        db.close()
        return redirect(url_for('login'))
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
        return "Login Failed!"
    return render_template_string(MASTER_HTML, page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    db.close()
    return render_template_string(MASTER_HTML, page='dashboard', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
