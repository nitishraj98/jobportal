# JobPortal — Flask Web Application

A full-featured, mobile-responsive Job Portal web application built as part of a technical assignment. The application supports three user roles — Admin, Employer, and Job Seeker — each with their own dashboard and set of functionalities.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 + Flask |
| Database | SQLite (via Python's built-in `sqlite3`) |
| Frontend | Bootstrap 5.3 + Font Awesome 6 |
| Fonts | Google Fonts (Plus Jakarta Sans, Space Mono) |
| Auth | Session-based with SHA-256 hashed passwords |

---

## Features Implemented

### Authentication & Access Control
- User registration with role selection (Employer / Job Seeker)
- Secure login with SHA-256 password hashing
- Session-based authentication
- Role-based access control — each role can only access their own pages
- Unauthorized access redirects to login

### Admin
- Centralized dashboard with platform-wide statistics
- Stats segmented by **Daily / Weekly / Monthly / Yearly** periods
- View total jobs posted, registered employers, job seekers, and applications
- Manage all job listings — toggle active/inactive, delete jobs
- Manage all employers — view their job count, delete accounts
- Manage all job seekers — view their application count, delete accounts

### Employer
- Register and log in as an employer
- Post new job listings with title, company, location, type, salary, description, and requirements
- Dashboard showing all posted jobs with application counts
- View applications submitted for each job listing
- See applicant details including name, email, phone, skills, experience, resume summary, and cover letter

### Job Seeker
- Register and log in as a job seeker
- Browse all active job listings
- Search and filter jobs by keyword, location, and job type
- Apply for jobs with an optional cover letter (via modal)
- View application history with status (Pending / Accepted / Rejected)
- Manage profile — update name, phone, skills, experience, and resume summary

### UI & Layout
- Dark-themed modern design with a professional look
- **Collapsible vertical sidebar** — shows only icons when collapsed, expands with labels on hover
- Fully **mobile responsive** — hamburger menu with slide-out overlay on small screens
- Sticky header with page title and logout button
- Footer on every page
- Flash messages for all user actions (success, error, warning)
- Empty state illustrations for pages with no data

---

## Project Structure

```
jobportal/
├── app.py                   # Main Flask app — all routes and logic
├── database.py              # DB schema, initialization, and seeding
├── requirements.txt         # Python dependencies
├── README.md
└── templates/
    ├── base.html                # Shared layout (sidebar, header, footer)
    ├── login.html
    ├── register.html
    ├── admin/
    │   ├── dashboard.html       # Stats with period toggle
    │   ├── jobs.html            # Manage all jobs
    │   ├── employers.html       # Manage all employers
    │   └── jobseekers.html      # Manage all job seekers
    ├── employer/
    │   ├── dashboard.html       # My jobs + application counts
    │   ├── post_job.html        # Post a new job form
    │   └── applications.html    # View applicants for a job
    └── jobseeker/
        ├── dashboard.html       # Latest job openings
        ├── browse_jobs.html     # Search & filter jobs
        ├── my_applications.html # Application history
        └── profile.html         # Edit profile
```

---

## Setup & Run

### 1. Clone the Repository
```
git clone https://github.com/nitishraj98/jobportal.git
cd jobportal
```

### 2. Create a Virtual Environment
```
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Run the Application
```
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

> The database is created automatically on first run. No manual setup needed.

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@jobportal.com | admin123 |
| Employer | Register via /register | — |
| Job Seeker | Register via /register | — |

---

## Developer

**Nitish Raj**  
Assignment submission for pre-interview technical evaluation.