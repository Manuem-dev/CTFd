# 🚩 Secx

A modern, fast, and self-hosted Capture The Flag (CTF) platform built with Django, Tailwind CSS, and HTMX. Designed for seamless event management, instant flag validation, and real-time scoreboard tracking.

---

##  Features

- **Dynamic Scoreboard:** Real-time team rankings computed instantly upon flag submission.
- **Team Management:** Create teams, invite members (with a strict 4-member limit), and manage roles (Captains/Members).
- **Flag Validation & Solves:** Secure flag submission and validation supporting standard flag formats.
- **Event Organization:** Host multiple public/private CTF events with customizable start/end timelines.
- **Reactive Frontend:** Driven by **HTMX** and **Alpine.js** for single-page app responsiveness without complex JavaScript frameworks.
- **Admin Suite:** Built-in Django Admin integration to manage challenges, categories, events, and submissions.

---

## Tech Stack

- **Backend:** Python 3.12, Django 6.0
- **Frontend:** HTML5, Tailwind CSS, Alpine.js, HTMX
- **Database:** PostgreSQL (Supabase)
- **Production Server:** Gunicorn & WhiteNoise (static file optimization)

---

## Local Development Setup

Follow these steps to set up the project on your local machine:

### 1. Clone the repository & enter directory
```bash
git clone <repository-url>
cd secx
```

### 2. Configure Virtual Environment
Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Migrations
Run the initial migrations to construct the database schema:
```bash
python manage.py migrate
```

### 5. Create a Superuser
Create an administrative account to access the backend panel:
```bash
python manage.py createsuperuser
```

### 6. Start the Servers

You can run the project in two different modes:

#### Option A: Native Django (Recommended for standard tests)
```bash
python manage.py runserver
```
Go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

#### Option B: Vite Dev Server (With proxy HMR support)
If you wish to run the Vite helper alongside the backend:
```bash
# In one terminal, keep the Django server active:
python manage.py runserver

# In another terminal, run Vite dev proxy:
npm install
npm run dev
```
Go to [http://localhost:5173/](http://localhost:5173/).

---

## Deployment Guide (Render & Supabase)

This project is fully configured for zero-configuration deployments on **Render** using **Supabase** (or any Postgres instance) as the production database.

### 1. Database Setup (Supabase)
1. Create a free project on [Supabase](https://supabase.com/).
2. Retrieve your **URI connection string** from Database settings (Transaction mode, port 6543 or Session mode).

### 2. Environment Variables Configuration
Set the following environment variables on your Render Dashboard:

| Variable | Description | Example / Recommended Value |
| :--- | :--- | :--- |
| `DEBUG` | Disables debug panel in production | `False` |
| `DJANGO_SECRET_KEY` | Production encryption key | *Generate a random hash string* |
| `DATABASE_URL` / `SUPABASE_DB_URL` | Postgres Connection URI | `postgresql://postgres:...` |
| `DJANGO_SUPERUSER_USERNAME` | Automated admin username | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | Automated admin password | `MySecureAdminPassword123` |
| `DJANGO_SUPERUSER_EMAIL` | Admin contact email | `admin@example.com` |

### 3. Render Web Service Parameters
Deploy your code as a **Web Service** on Render with the following configurations:

- **Runtime:** `Python`
- **Build Command:** `./build.sh` (Automatically installs dependencies, compiles static assets, runs migrations, and creates the superuser).
- **Start Command:** `gunicorn ctfplatform.wsgi:application`

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
