# JobPortal — Flask Web Application

A full-featured, mobile-responsive job portal built with Python Flask, SQLite, and Bootstrap 5.

## Features

### Three User Roles
| Role | Capabilities |
|------|-------------|
| **Admin** | Dashboard with daily/weekly/monthly/yearly stats; manage all jobs, employers & jobseekers |
| **Employer** | Register/login, post jobs, view applications per listing |
| **Job Seeker** | Register/login, browse & search jobs, apply with cover letter, view application history, manage profile |

### UI Highlights
- Dark-themed, modern design with indigo/pink accent palette
- Collapsible sidebar — icons only when collapsed, full labels on hover
- Fully responsive across desktop, tablet, and mobile
- Period-based stats (Daily / Weekly / Monthly / Yearly) on Admin dashboard
- Apply-to-job modal with cover letter field
- Role-based navigation — each user type sees only their relevant pages

---

## Tech Stack
- **Backend**: Python 3 + Flask
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **Frontend**: Bootstrap 5.3 + Font Awesome 6 + Google Fonts
- **Auth**: Session-based with SHA-256 hashed passwords

---

## Setup & Run

### 1. Clone / Extract
```bash
unzip jobportal.zip
cd jobportal
```

### 2. Create a Virtual Environment (recommended)
```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

Then open your browser to: **http://127.0.0.1:5000**

---

## Default Admin Credentials
| Field | Value |
|-------|-------|
| Email | admin@jobportal.com |
| Password | admin123 |

---

## Project Structure
```
jobportal/
├── app.py              # Main Flask application & all routes
├── database.py         # DB init, schema, seeding
├── requirements.txt
├── jobportal.db        # Auto-created on first run
└── templates/
    ├── base.html           # Shared layout (sidebar, header, footer)
    ├── login.html
    ├── register.html
    ├── admin/
    │   ├── dashboard.html
    │   ├── jobs.html
    │   ├── employers.html
    │   └── jobseekers.html
    ├── employer/
    │   ├── dashboard.html
    │   ├── post_job.html
    │   └── applications.html
    └── jobseeker/
        ├── dashboard.html
        ├── browse_jobs.html
        ├── my_applications.html
        └── profile.html
```

---

## User Flows

### Employer
1. Register → Select "Employer" role
2. Log in → See dashboard with your job listings
3. Click **Post a Job** → Fill in details
4. Click application count on any job → View applicants with their profiles & cover letters

### Job Seeker
1. Register → Select "Job Seeker" role  
2. Log in → See latest job openings
3. **Browse Jobs** → Search/filter, click "Apply Now", add optional cover letter
4. **My Applications** → View your application history & statuses
5. **My Profile** → Add phone, skills, experience, resume summary

### Admin
1. Log in with admin credentials
2. **Dashboard** → Toggle between Daily / Weekly / Monthly / Yearly stats
3. **Jobs** → View all postings, toggle active/inactive, delete
4. **Employers** → View all employers, delete accounts
5. **Job Seekers** → View all seekers, delete accounts
