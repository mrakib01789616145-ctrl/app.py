@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    # ইউজার আইডি অনুযায়ী ডাটাবেজ থেকে সব তথ্য আনা হচ্ছে
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    if user:
        # এখানে 'dashboard' পেজ এবং ইউজারের তথ্য পাঠানো হচ্ছে
        return render_template_string(MASTER_HTML, page='dashboard', user=user)
    else:
        return redirect(url_for('logout'))
        
