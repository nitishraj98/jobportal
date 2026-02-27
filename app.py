from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import init_db, get_db
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import os

app = Flask(__name__)
app.secret_key = '652344ghfr87y34879thfggvbhgu8hrtgrbyfbgjyhj'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        role = request.form['role']
        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'danger')
        else:
            db.execute('INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)', (name, email, password, role))
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    db = get_db()
    if role == 'admin':
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        year_ago = (now - timedelta(days=365)).strftime('%Y-%m-%d')
        stats = {
            'total_jobs': db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0],
            'total_employers': db.execute("SELECT COUNT(*) FROM users WHERE role='employer'").fetchone()[0],
            'total_jobseekers': db.execute("SELECT COUNT(*) FROM users WHERE role='jobseeker'").fetchone()[0],
            'total_applications': db.execute('SELECT COUNT(*) FROM applications').fetchone()[0],
            'daily_jobs': db.execute('SELECT COUNT(*) FROM jobs WHERE DATE(created_at)=?', (today,)).fetchone()[0],
            'weekly_jobs': db.execute('SELECT COUNT(*) FROM jobs WHERE DATE(created_at)>=?', (week_ago,)).fetchone()[0],
            'monthly_jobs': db.execute('SELECT COUNT(*) FROM jobs WHERE DATE(created_at)>=?', (month_ago,)).fetchone()[0],
            'yearly_jobs': db.execute('SELECT COUNT(*) FROM jobs WHERE DATE(created_at)>=?', (year_ago,)).fetchone()[0],
            'daily_employers': db.execute("SELECT COUNT(*) FROM users WHERE role='employer' AND DATE(created_at)=?", (today,)).fetchone()[0],
            'weekly_employers': db.execute("SELECT COUNT(*) FROM users WHERE role='employer' AND DATE(created_at)>=?", (week_ago,)).fetchone()[0],
            'monthly_employers': db.execute("SELECT COUNT(*) FROM users WHERE role='employer' AND DATE(created_at)>=?", (month_ago,)).fetchone()[0],
            'yearly_employers': db.execute("SELECT COUNT(*) FROM users WHERE role='employer' AND DATE(created_at)>=?", (year_ago,)).fetchone()[0],
            'daily_seekers': db.execute("SELECT COUNT(*) FROM users WHERE role='jobseeker' AND DATE(created_at)=?", (today,)).fetchone()[0],
            'weekly_seekers': db.execute("SELECT COUNT(*) FROM users WHERE role='jobseeker' AND DATE(created_at)>=?", (week_ago,)).fetchone()[0],
            'monthly_seekers': db.execute("SELECT COUNT(*) FROM users WHERE role='jobseeker' AND DATE(created_at)>=?", (month_ago,)).fetchone()[0],
            'yearly_seekers': db.execute("SELECT COUNT(*) FROM users WHERE role='jobseeker' AND DATE(created_at)>=?", (year_ago,)).fetchone()[0],
        }
        recent_jobs = db.execute('SELECT j.*, u.name as employer_name FROM jobs j JOIN users u ON j.employer_id=u.id ORDER BY j.created_at DESC LIMIT 5').fetchall()
        return render_template('admin/dashboard.html', stats=stats, recent_jobs=recent_jobs)
    elif role == 'employer':
        jobs = db.execute('SELECT j.*, COUNT(a.id) as app_count FROM jobs j LEFT JOIN applications a ON j.id=a.job_id WHERE j.employer_id=? GROUP BY j.id ORDER BY j.created_at DESC', (session['user_id'],)).fetchall()
        total_apps = db.execute('SELECT COUNT(*) FROM applications a JOIN jobs j ON a.job_id=j.id WHERE j.employer_id=?', (session['user_id'],)).fetchone()[0]
        return render_template('employer/dashboard.html', jobs=jobs, total_apps=total_apps)
    else:  # jobseeker
        available_jobs = db.execute('SELECT j.*, u.name as employer_name FROM jobs j JOIN users u ON j.employer_id=u.id WHERE j.is_active=1 ORDER BY j.created_at DESC LIMIT 6').fetchall()
        applied_ids = [r['job_id'] for r in db.execute('SELECT job_id FROM applications WHERE user_id=?', (session['user_id'],)).fetchall()]
        return render_template('jobseeker/dashboard.html', available_jobs=available_jobs, applied_ids=applied_ids)

# ---- ADMIN ROUTES ----
@app.route('/admin/jobs')
@role_required('admin')
def admin_jobs():
    db = get_db()
    jobs = db.execute('SELECT j.*, u.name as employer_name, COUNT(a.id) as app_count FROM jobs j JOIN users u ON j.employer_id=u.id LEFT JOIN applications a ON j.id=a.job_id GROUP BY j.id ORDER BY j.created_at DESC').fetchall()
    return render_template('admin/jobs.html', jobs=jobs)

@app.route('/admin/jobs/delete/<int:job_id>', methods=['POST'])
@role_required('admin')
def admin_delete_job(job_id):
    db = get_db()
    db.execute('DELETE FROM applications WHERE job_id=?', (job_id,))
    db.execute('DELETE FROM jobs WHERE id=?', (job_id,))
    db.commit()
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/toggle/<int:job_id>', methods=['POST'])
@role_required('admin')
def admin_toggle_job(job_id):
    db = get_db()
    job = db.execute('SELECT is_active FROM jobs WHERE id=?', (job_id,)).fetchone()
    db.execute('UPDATE jobs SET is_active=? WHERE id=?', (0 if job['is_active'] else 1, job_id))
    db.commit()
    flash('Job status updated.', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/employers')
@role_required('admin')
def admin_employers():
    db = get_db()
    employers = db.execute("SELECT u.*, COUNT(j.id) as job_count FROM users u LEFT JOIN jobs j ON u.id=j.employer_id WHERE u.role='employer' GROUP BY u.id ORDER BY u.created_at DESC").fetchall()
    return render_template('admin/employers.html', employers=employers)

@app.route('/admin/employers/delete/<int:uid>', methods=['POST'])
@role_required('admin')
def admin_delete_employer(uid):
    db = get_db()
    db.execute('DELETE FROM applications WHERE job_id IN (SELECT id FROM jobs WHERE employer_id=?)', (uid,))
    db.execute('DELETE FROM jobs WHERE employer_id=?', (uid,))
    db.execute('DELETE FROM users WHERE id=?', (uid,))
    db.commit()
    flash('Employer deleted.', 'success')
    return redirect(url_for('admin_employers'))

@app.route('/admin/jobseekers')
@role_required('admin')
def admin_jobseekers():
    db = get_db()
    seekers = db.execute("SELECT u.*, COUNT(a.id) as app_count FROM users u LEFT JOIN applications a ON u.id=a.user_id WHERE u.role='jobseeker' GROUP BY u.id ORDER BY u.created_at DESC").fetchall()
    return render_template('admin/jobseekers.html', seekers=seekers)

@app.route('/admin/jobseekers/delete/<int:uid>', methods=['POST'])
@role_required('admin')
def admin_delete_jobseeker(uid):
    db = get_db()
    db.execute('DELETE FROM applications WHERE user_id=?', (uid,))
    db.execute('DELETE FROM users WHERE id=?', (uid,))
    db.commit()
    flash('Jobseeker deleted.', 'success')
    return redirect(url_for('admin_jobseekers'))

# ---- EMPLOYER ROUTES ----
@app.route('/employer/post-job', methods=['GET', 'POST'])
@role_required('employer')
def post_job():
    if request.method == 'POST':
        db = get_db()
        db.execute('''INSERT INTO jobs (employer_id, title, company, location, job_type, salary, description, requirements)
                      VALUES (?,?,?,?,?,?,?,?)''',
                   (session['user_id'], request.form['title'], request.form['company'],
                    request.form['location'], request.form['job_type'], request.form['salary'],
                    request.form['description'], request.form['requirements']))
        db.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('employer/post_job.html')

@app.route('/employer/applications/<int:job_id>')
@role_required('employer')
def job_applications(job_id):
    db = get_db()
    job = db.execute('SELECT * FROM jobs WHERE id=? AND employer_id=?', (job_id, session['user_id'])).fetchone()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('dashboard'))
    applications = db.execute('''SELECT a.*, u.name, u.email, p.phone, p.skills, p.experience, p.resume_text
                                  FROM applications a JOIN users u ON a.user_id=u.id
                                  LEFT JOIN profiles p ON u.id=p.user_id
                                  WHERE a.job_id=? ORDER BY a.applied_at DESC''', (job_id,)).fetchall()
    return render_template('employer/applications.html', job=job, applications=applications)

# ---- JOBSEEKER ROUTES ----
@app.route('/jobs')
@role_required('jobseeker')
def browse_jobs():
    db = get_db()
    q = request.args.get('q', '')
    loc = request.args.get('location', '')
    jtype = request.args.get('type', '')
    query = 'SELECT j.*, u.name as employer_name FROM jobs j JOIN users u ON j.employer_id=u.id WHERE j.is_active=1'
    params = []
    if q:
        query += ' AND (j.title LIKE ? OR j.description LIKE ?)'
        params += [f'%{q}%', f'%{q}%']
    if loc:
        query += ' AND j.location LIKE ?'
        params.append(f'%{loc}%')
    if jtype:
        query += ' AND j.job_type=?'
        params.append(jtype)
    query += ' ORDER BY j.created_at DESC'
    jobs = db.execute(query, params).fetchall()
    applied_ids = [r['job_id'] for r in db.execute('SELECT job_id FROM applications WHERE user_id=?', (session['user_id'],)).fetchall()]
    return render_template('jobseeker/browse_jobs.html', jobs=jobs, applied_ids=applied_ids, q=q, loc=loc, jtype=jtype)

@app.route('/jobs/apply/<int:job_id>', methods=['POST'])
@role_required('jobseeker')
def apply_job(job_id):
    db = get_db()
    existing = db.execute('SELECT id FROM applications WHERE user_id=? AND job_id=?', (session['user_id'], job_id)).fetchone()
    if existing:
        flash('You have already applied for this job.', 'warning')
    else:
        cover_letter = request.form.get('cover_letter', '')
        db.execute('INSERT INTO applications (user_id, job_id, cover_letter) VALUES (?,?,?)',
                   (session['user_id'], job_id, cover_letter))
        db.commit()
        flash('Application submitted successfully!', 'success')
    return redirect(url_for('browse_jobs'))

@app.route('/my-applications')
@role_required('jobseeker')
def my_applications():
    db = get_db()
    apps = db.execute('''SELECT a.*, j.title, j.company, j.location, j.job_type, j.salary, u.name as employer_name
                          FROM applications a JOIN jobs j ON a.job_id=j.id JOIN users u ON j.employer_id=u.id
                          WHERE a.user_id=? ORDER BY a.applied_at DESC''', (session['user_id'],)).fetchall()
    return render_template('jobseeker/my_applications.html', apps=apps)

@app.route('/profile', methods=['GET', 'POST'])
@role_required('jobseeker')
def profile():
    db = get_db()
    if request.method == 'POST':
        phone = request.form.get('phone', '')
        skills = request.form.get('skills', '')
        experience = request.form.get('experience', '')
        resume_text = request.form.get('resume_text', '')
        existing = db.execute('SELECT id FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
        if existing:
            db.execute('UPDATE profiles SET phone=?, skills=?, experience=?, resume_text=? WHERE user_id=?',
                       (phone, skills, experience, resume_text, session['user_id']))
        else:
            db.execute('INSERT INTO profiles (user_id, phone, skills, experience, resume_text) VALUES (?,?,?,?,?)',
                       (session['user_id'], phone, skills, experience, resume_text))
        # Update name
        new_name = request.form.get('name', session['name'])
        db.execute('UPDATE users SET name=? WHERE id=?', (new_name, session['user_id']))
        session['name'] = new_name
        db.commit()
        flash('Profile updated!', 'success')
    user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    profile_data = db.execute('SELECT * FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    return render_template('jobseeker/profile.html', user=user, profile=profile_data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
