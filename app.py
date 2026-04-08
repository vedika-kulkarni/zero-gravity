from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'zerogravity_secret_key_2024'

# Use Render Persistent Disk path if provided, otherwise default to local
DATABASE = os.environ.get('DB_PATH', 'database.db')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = 'kulkarnivedika471@gmail.com'  
MAIL_PASSWORD = 'ikcm vgvf wtia aqwl'     

# ─────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL DEFAULT '',
        phone TEXT,
        city TEXT DEFAULT 'Nagpur',
        age_group TEXT,
        availability TEXT,
        skills TEXT,
        interests TEXT,
        bio TEXT,
        join_date TEXT DEFAULT CURRENT_DATE
    )''')

    # Migrate old DB: add password column if missing
    try:
        c.execute("ALTER TABLE volunteers ADD COLUMN password TEXT NOT NULL DEFAULT ''")
        conn.commit()
    except Exception:
        pass

    try:
        c.execute("ALTER TABLE volunteers ADD COLUMN reset_code TEXT")
        c.execute("ALTER TABLE volunteers ADD COLUMN reset_expiry REAL")
        conn.commit()
    except Exception:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT,
        schedule TEXT,
        duration TEXT,
        slots INTEGER DEFAULT 10,
        registered INTEGER DEFAULT 0,
        skills_required TEXT,
        description TEXT,
        contact_person TEXT,
        posted_date TEXT DEFAULT CURRENT_DATE,
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER,
        opportunity_id INTEGER,
        volunteer_name TEXT,
        volunteer_email TEXT,
        opp_title TEXT,
        opp_category TEXT,
        reason TEXT,
        experience TEXT,
        status TEXT DEFAULT 'pending',
        applied_date TEXT DEFAULT CURRENT_DATE,
        FOREIGN KEY(volunteer_id) REFERENCES volunteers(id),
        FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        subject TEXT,
        message TEXT,
        received_date TEXT DEFAULT CURRENT_DATE
    )''')

    # Default admin
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES ('admin', ?)", (generate_password_hash('zerogravity2024'),))

    # Sample opportunities
    existing_opps = c.execute("SELECT COUNT(*) as c FROM opportunities").fetchone()['c']
    if existing_opps == 0:
        sample_opps = [
            ("Digital Literacy for Senior Citizens", "Education", "Nagpur Central",
             "Every Saturday", "Weekly", 10, 3,
             "Teaching,Communication,Patience",
             "Help senior citizens learn basic smartphone and internet skills. Sessions held every Saturday morning at the Bharat Nagar community centre.",
             "Priya Joshi"),
            ("Free Health Camp - Slum Areas", "Health", "Dharampeth, Nagpur",
             "15 Jan 2025", "One-time", 20, 8,
             "Medical,First Aid,Communication",
             "Join our team of medical professionals to run a free health camp covering basic screenings, blood pressure, eye check-ups and nutrition counselling.",
             "Dr. Anand Kulkarni"),
            ("Tree Plantation Drive - Ambazari Lake", "Environment", "Ambazari, Nagpur",
             "20 Jan 2025", "One-time", 50, 22,
             "Teamwork,Physical Fitness,Leadership",
             "Help us plant 500 saplings around the Ambazari Lake area to restore greenery. Tools and saplings provided. Suitable for all ages.",
             "Ravi Tiwari"),
            ("Art & Creativity Workshop for Kids", "Arts & Culture", "Manish Nagar, Nagpur",
             "Every Sunday", "Weekly", 15, 6,
             "Arts,Teaching,Creativity,Photography",
             "Teach drawing, painting and creative arts to children aged 6-14 from underprivileged backgrounds. Materials provided.",
             "Sneha Mandal"),
            ("Website & Social Media Support", "Technology", "Remote / Nagpur Office",
             "Ongoing", "Ongoing", 5, 1,
             "Programming,Design,Social Media,Communication",
             "Help Zero Gravity manage its online presence, create content, and maintain the volunteer platform. Flexible timing.",
             "Kunal Mehta"),
            ("Rural Women's Skill Development", "Community", "Hingna Rural, Nagpur",
             "Bi-weekly", "Monthly", 8, 3,
             "Leadership,Teaching,Communication,Business",
             "Empower rural women through skill-building workshops in stitching, food processing, and micro-enterprise. Transport arranged.",
             "Meena Sharma"),
        ]
        c.executemany('''INSERT INTO opportunities
            (title,category,location,schedule,duration,slots,registered,skills_required,description,contact_person)
            VALUES (?,?,?,?,?,?,?,?,?,?)''', sample_opps)

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# EMAIL HELPER
# ─────────────────────────────────────────
def send_verification_email(to_email, code):
    if MAIL_USERNAME == 'your_gmail@gmail.com':
        print(f"Skipped email to {to_email}. Please configure MAIL_USERNAME.")
        return False
        
    msg = MIMEText(f"Hello Volunteer,\n\nYour Verification Code is: {code}\n\nThis code will expire in 1 hour.\n\nThank you,\nZero Gravity Team")
    msg['Subject'] = 'Zero Gravity - Password Reset Code'
    msg['From'] = f"Zero Gravity <{MAIL_USERNAME}>"
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed to send: {e}")
        return False

# ─────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'volunteer_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    featured = db.execute('SELECT * FROM opportunities WHERE is_active=1 LIMIT 3').fetchall()
    vol_count = db.execute('SELECT COUNT(*) as c FROM volunteers').fetchone()['c']
    opp_count = db.execute('SELECT COUNT(*) as c FROM opportunities WHERE is_active=1').fetchone()['c']
    db.close()
    return render_template('index.html',
        featured=featured,
        vol_count=vol_count or 500,
        opp_count=opp_count,
        lives_count=10000,
        current_user=session.get('volunteer_name'))

@app.route('/about')
def about():
    return render_template('about.html', current_user=session.get('volunteer_name'))

@app.route('/opportunities')
def opportunities():
    db = get_db()
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    skill = request.args.get('skill', '')
    duration = request.args.get('duration', '')

    sql = 'SELECT * FROM opportunities WHERE is_active=1'
    params = []
    if q:
        sql += ' AND (title LIKE ? OR description LIKE ? OR skills_required LIKE ?)'
        params += [f'%{q}%', f'%{q}%', f'%{q}%']
    if category:
        sql += ' AND category=?'
        params.append(category)
    if skill:
        sql += ' AND skills_required LIKE ?'
        params.append(f'%{skill}%')
    if duration:
        sql += ' AND duration=?'
        params.append(duration)

    opps = db.execute(sql, params).fetchall()

    # Skill-based sorting for logged-in volunteers
    match_count = 0
    if session.get('volunteer_skills'):
        user_skills = set(s.strip() for s in session['volunteer_skills'].split(',') if s.strip())
        def score(o):
            opp_skills = set(s.strip() for s in (o['skills_required'] or '').split(','))
            return len(user_skills & opp_skills)
        opps = sorted(opps, key=score, reverse=True)
        match_count = sum(1 for o in opps if score(o) > 0)

    db.close()
    return render_template('opportunities.html',
        opportunities=opps,
        q=q, category=category, skill=skill, duration=duration,
        match_count=match_count,
        current_user=session.get('volunteer_name'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', current_user=session.get('volunteer_name'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        db = get_db()
        db.execute('INSERT INTO contact_messages (name,email,subject,message) VALUES (?,?,?,?)',
            (request.form['name'], request.form['email'],
             request.form.get('subject', ''), request.form['message']))
        db.commit()
        db.close()
        flash('Message sent! We will reply within 24 hours.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', current_user=session.get('volunteer_name'))

# ─────────────────────────────────────────
# VOLUNTEER AUTH
# ─────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        confirm  = request.form['confirm_password'].strip()

        if not name or not email or not password:
            flash('Name, email and password are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        skills    = ','.join(request.form.getlist('skills'))
        interests = ','.join(request.form.getlist('interests'))

        db = get_db()
        existing = db.execute('SELECT id FROM volunteers WHERE email=?', (email,)).fetchone()
        if existing:
            flash('This email is already registered. Please log in.', 'danger')
            db.close()
            return redirect(url_for('register'))

        db.execute('''INSERT INTO volunteers
            (name, email, password, phone, city, age_group, availability, skills, interests, bio)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (name, email, generate_password_hash(password),
             request.form.get('phone', ''),
             request.form.get('city', 'Nagpur'),
             request.form.get('age_group', ''),
             request.form.get('availability', ''),
             skills, interests,
             request.form.get('bio', '')))
        db.commit()
        vol = db.execute('SELECT * FROM volunteers WHERE email=?', (email,)).fetchone()
        db.close()

        session['volunteer_id']    = vol['id']
        session['volunteer_name']  = vol['name']
        session['volunteer_email'] = vol['email']
        session['volunteer_skills'] = skills
        flash(f'Welcome, {name}! You are now part of Zero Gravity.', 'success')
        return redirect(url_for('profile'))

    return render_template('register.html', current_user=session.get('volunteer_name'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        db = get_db()
        vol = db.execute('SELECT * FROM volunteers WHERE email=?', (email,)).fetchone()
        
        valid_login = False
        if vol:
            if check_password_hash(vol['password'], password):
                valid_login = True
            elif vol['password'] == password:
                # Graceful migration
                db.execute('UPDATE volunteers SET password=? WHERE id=?', (generate_password_hash(password), vol['id']))
                db.commit()
                valid_login = True

        if valid_login:
            session['volunteer_id']    = vol['id']
            session['volunteer_name']  = vol['name']
            session['volunteer_email'] = vol['email']
            session['volunteer_skills'] = vol['skills'] or ''
            flash(f'Welcome back, {vol["name"]}!', 'success')
            db.close()
            return redirect(url_for('profile'))
        elif vol and vol['password'] == '':
            # Old account without password — let them set one
            flash('Your account was created before passwords were added. Please re-register with a password.', 'warning')
            db.close()
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            db.close()

    return render_template('login.html', current_user=session.get('volunteer_name'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        db = get_db()
        vol = db.execute('SELECT * FROM volunteers WHERE email=?', (email,)).fetchone()
        
        if vol:
            # Generate a 6-digit code and set expiry to 1 hour
            code = str(random.randint(100000, 999999))
            expiry = time.time() + 3600
            db.execute('UPDATE volunteers SET reset_code=?, reset_expiry=? WHERE id=?', 
                      (code, expiry, vol['id']))
            db.commit()
            
            # Send the real email
            send_verification_email(email, code)
            
            db.close()
            return redirect(url_for('reset_password', email=email))
        
        db.close()
        # Security best practice: don't reveal if email exists or not
        flash('If this email is registered, a verification code will be sent.', 'info')
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html', current_user=session.get('volunteer_name'))

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        code = request.form.get('code', '').strip()
        new_pwd = request.form.get('password', '').strip()
        confirm_pwd = request.form.get('confirm_password', '').strip()

        if new_pwd != confirm_pwd:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', email=email))
        
        if len(new_pwd) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('reset_password', email=email))

        db = get_db()
        vol = db.execute('SELECT * FROM volunteers WHERE email=?', (email,)).fetchone()
        
        # Verify the code and its expiration
        if not vol or vol['reset_code'] != code or not vol['reset_expiry'] or time.time() > vol['reset_expiry']:
            flash('Invalid or expired verification code.', 'danger')
            db.close()
            return redirect(url_for('reset_password', email=email))
            
        # Update the password and clear out the reset tokens
        db.execute('UPDATE volunteers SET password=?, reset_code=NULL, reset_expiry=NULL WHERE id=?', 
                  (generate_password_hash(new_pwd), vol['id']))
        db.commit()
        db.close()
        
        flash('Password successfully reset! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html', email=email, current_user=session.get('volunteer_name'))

# ─────────────────────────────────────────
# VOLUNTEER PROFILE & APPLY
# ─────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    db = get_db()
    vol = db.execute('SELECT * FROM volunteers WHERE id=?', (session['volunteer_id'],)).fetchone()
    my_apps = db.execute('''SELECT a.*, o.location, o.schedule
        FROM applications a JOIN opportunities o ON a.opportunity_id=o.id
        WHERE a.volunteer_id=?''', (session['volunteer_id'],)).fetchall()

    # Recommended based on skills
    user_skills = [s.strip() for s in (vol['skills'] or '').split(',') if s.strip()]
    all_opps = db.execute('SELECT * FROM opportunities WHERE is_active=1').fetchall()
    recommended = []
    for o in all_opps:
        opp_skills = set(s.strip() for s in (o['skills_required'] or '').split(','))
        if any(s in opp_skills for s in user_skills):
            recommended.append(o)
    recommended = recommended[:3]
    db.close()
    return render_template('profile.html',
        vol=vol, my_apps=my_apps, recommended=recommended,
        current_user=session.get('volunteer_name'))


@app.route('/apply/<int:opp_id>', methods=['GET', 'POST'])
@login_required
def apply(opp_id):
    db = get_db()
    opp = db.execute('SELECT * FROM opportunities WHERE id=?', (opp_id,)).fetchone()
    if not opp:
        flash('Opportunity not found.', 'danger')
        db.close()
        return redirect(url_for('opportunities'))

    already = db.execute('SELECT id FROM applications WHERE volunteer_id=? AND opportunity_id=?',
        (session['volunteer_id'], opp_id)).fetchone()

    if request.method == 'POST':
        if already:
            flash('You have already applied for this opportunity.', 'warning')
        else:
            db.execute('''INSERT INTO applications
                (volunteer_id, opportunity_id, volunteer_name, volunteer_email,
                 opp_title, opp_category, reason, experience)
                VALUES (?,?,?,?,?,?,?,?)''',
                (session['volunteer_id'], opp_id,
                 session['volunteer_name'], session['volunteer_email'],
                 opp['title'], opp['category'],
                 request.form.get('reason', ''),
                 request.form.get('experience', '')))
            db.execute('UPDATE opportunities SET registered=registered+1 WHERE id=?', (opp_id,))
            db.commit()
            flash('Application submitted! Zero Gravity will contact you soon.', 'success')
        db.close()
        return redirect(url_for('profile'))

    db.close()
    return render_template('apply.html',
        opp=opp, already=already,
        current_user=session.get('volunteer_name'))

# ─────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────
@app.route('/admin')
def admin_redirect():
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        db = get_db()
        admin = db.execute('SELECT * FROM admins WHERE username=?', (u,)).fetchone()
        
        valid_login = False
        if admin:
            if check_password_hash(admin['password'], p):
                valid_login = True
            elif admin['password'] == p:
                # Graceful migration
                db.execute('UPDATE admins SET password=? WHERE id=?', (generate_password_hash(p), admin['id']))
                db.commit()
                valid_login = True
                
        db.close()
        
        if valid_login:
            session['admin_logged_in'] = True
            session['admin_username']  = u
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    stats = {
        'volunteers':    db.execute('SELECT COUNT(*) as c FROM volunteers').fetchone()['c'],
        'opportunities': db.execute('SELECT COUNT(*) as c FROM opportunities WHERE is_active=1').fetchone()['c'],
        'applications':  db.execute('SELECT COUNT(*) as c FROM applications').fetchone()['c'],
        'pending':       db.execute("SELECT COUNT(*) as c FROM applications WHERE status='pending'").fetchone()['c'],
    }
    recent_apps = db.execute('''SELECT a.*, v.city FROM applications a
        JOIN volunteers v ON a.volunteer_id=v.id
        ORDER BY a.id DESC LIMIT 5''').fetchall()
    cat_data = db.execute('SELECT category, COUNT(*) as cnt FROM opportunities GROUP BY category').fetchall()
    db.close()
    return render_template('admin/dashboard.html', stats=stats,
        recent_apps=recent_apps, cat_data=cat_data,
        admin_user=session.get('admin_username'))

@app.route('/admin/opportunities', methods=['GET', 'POST'])
@admin_required
def admin_opportunities():
    db = get_db()
    if request.method == 'POST':
        skills = ','.join([s.strip() for s in request.form.get('skills_required', '').split(',') if s.strip()])
        db.execute('''INSERT INTO opportunities
            (title, category, location, schedule, duration, slots, skills_required, description, contact_person)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (request.form['title'], request.form['category'],
             request.form.get('location', 'Nagpur'),
             request.form.get('schedule', 'TBD'),
             request.form.get('duration', 'One-time'),
             int(request.form.get('slots', 10)),
             skills,
             request.form['description'],
             request.form.get('contact_person', 'Zero Gravity Team')))
        db.commit()
        flash('Opportunity posted successfully!', 'success')
        db.close()
        return redirect(url_for('admin_opportunities'))
    opps = db.execute('SELECT * FROM opportunities ORDER BY id DESC').fetchall()
    db.close()
    return render_template('admin/opportunities.html', opportunities=opps,
        admin_user=session.get('admin_username'))

@app.route('/admin/opportunities/delete/<int:opp_id>')
@admin_required
def admin_delete_opp(opp_id):
    db = get_db()
    db.execute('DELETE FROM opportunities WHERE id=?', (opp_id,))
    db.execute('DELETE FROM applications WHERE opportunity_id=?', (opp_id,))
    db.commit()
    db.close()
    flash('Opportunity deleted.', 'info')
    return redirect(url_for('admin_opportunities'))

@app.route('/admin/opportunities/toggle/<int:opp_id>')
@admin_required
def admin_toggle_opp(opp_id):
    db = get_db()
    opp = db.execute('SELECT is_active FROM opportunities WHERE id=?', (opp_id,)).fetchone()
    db.execute('UPDATE opportunities SET is_active=? WHERE id=?', (1 - opp['is_active'], opp_id))
    db.commit()
    db.close()
    return redirect(url_for('admin_opportunities'))

@app.route('/admin/applications')
@admin_required
def admin_applications():
    db = get_db()
    status_filter = request.args.get('status', 'all')
    sql = 'SELECT * FROM applications'
    if status_filter != 'all':
        sql += f" WHERE status='{status_filter}'"
    sql += ' ORDER BY id DESC'
    apps = db.execute(sql).fetchall()
    counts = {
        'all':      db.execute('SELECT COUNT(*) as c FROM applications').fetchone()['c'],
        'pending':  db.execute("SELECT COUNT(*) as c FROM applications WHERE status='pending'").fetchone()['c'],
        'approved': db.execute("SELECT COUNT(*) as c FROM applications WHERE status='approved'").fetchone()['c'],
        'rejected': db.execute("SELECT COUNT(*) as c FROM applications WHERE status='rejected'").fetchone()['c'],
    }
    db.close()
    return render_template('admin/applications.html', applications=apps,
        status_filter=status_filter, counts=counts,
        admin_user=session.get('admin_username'))

@app.route('/admin/applications/update/<int:app_id>/<status>')
@admin_required
def admin_update_app(app_id, status):
    if status not in ('approved', 'rejected', 'pending'):
        return redirect(url_for('admin_applications'))
    db = get_db()
    db.execute('UPDATE applications SET status=? WHERE id=?', (status, app_id))
    db.commit()
    db.close()
    flash(f'Application marked as {status}.', 'success')
    return redirect(url_for('admin_applications'))

@app.route('/admin/volunteers')
@admin_required
def admin_volunteers():
    db = get_db()
    vols = db.execute('''SELECT v.*, COUNT(a.id) as app_count
        FROM volunteers v LEFT JOIN applications a ON v.id=a.volunteer_id
        GROUP BY v.id ORDER BY v.id DESC''').fetchall()
    db.close()
    return render_template('admin/volunteers.html', volunteers=vols,
        admin_user=session.get('admin_username'))

@app.route('/admin/messages')
@admin_required
def admin_messages():
    db = get_db()
    msgs = db.execute('SELECT * FROM contact_messages ORDER BY id DESC').fetchall()
    db.close()
    return render_template('admin/messages.html', messages=msgs,
        admin_user=session.get('admin_username'))

@app.route('/admin/reports')
@admin_required
def admin_reports():
    db = get_db()
    cat_data   = db.execute('SELECT category, COUNT(*) as cnt FROM opportunities GROUP BY category').fetchall()
    # FIX: correct column name is 'skills' in volunteers table
    skill_data = db.execute('SELECT skills FROM volunteers WHERE skills IS NOT NULL AND skills != ""').fetchall()
    skill_counts = {}
    for row in skill_data:
        for s in (row['skills'] or '').split(','):
            s = s.strip()
            if s:
                skill_counts[s] = skill_counts.get(s, 0) + 1
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    summary = {
        'total_volunteers':    db.execute('SELECT COUNT(*) as c FROM volunteers').fetchone()['c'],
        'total_opportunities': db.execute('SELECT COUNT(*) as c FROM opportunities').fetchone()['c'],
        'total_applications':  db.execute('SELECT COUNT(*) as c FROM applications').fetchone()['c'],
        'approved':            db.execute("SELECT COUNT(*) as c FROM applications WHERE status='approved'").fetchone()['c'],
        'pending':             db.execute("SELECT COUNT(*) as c FROM applications WHERE status='pending'").fetchone()['c'],
    }
    db.close()
    return render_template('admin/reports.html',
        cat_data=cat_data, top_skills=top_skills, summary=summary,
        admin_user=session.get('admin_username'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        cur  = request.form['current_password']
        new  = request.form['new_password']
        conf = request.form['confirm_password']
        db = get_db()
        admin = db.execute('SELECT * FROM admins WHERE username=?', (session['admin_username'],)).fetchone()
        
        if not admin:
            flash('Admin not found.', 'danger')
        else:
            valid_cur = False
            if check_password_hash(admin['password'], cur):
                valid_cur = True
            elif admin['password'] == cur:
                valid_cur = True
                
            if not valid_cur:
                flash('Current password is incorrect.', 'danger')
            elif new != conf:
                flash('New passwords do not match.', 'danger')
            elif len(new) < 6:
                flash('Password must be at least 6 characters.', 'danger')
            else:
                db.execute('UPDATE admins SET password=? WHERE username=?', (generate_password_hash(new), session['admin_username']))
                db.commit()
                flash('Password updated successfully!', 'success')
        db.close()
    return render_template('admin/settings.html', admin_user=session.get('admin_username'))

# ─────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run()
