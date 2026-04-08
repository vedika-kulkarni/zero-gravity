# Zero Gravity NGO — Volunteer Platform

A full Flask web application for the Zero Gravity NGO (Nagpur) volunteer management platform.

---

## Project Structure

```
zerogravity/
├── app.py                    # Main Flask application
├── database.db               # SQLite database (auto-created on first run)
├── requirements.txt
├── static/
│   ├── css/
│   │   ├── style.css         # Public site styles
│   │   └── admin.css         # Admin panel styles
│   └── js/
│       └── main.js
└── templates/
    ├── base.html             # Public site base layout
    ├── index.html            # Home page
    ├── about.html            # About page
    ├── opportunities.html    # Opportunity listing + search/filter
    ├── gallery.html          # Gallery page
    ├── contact.html          # Contact form
    ├── register.html         # Volunteer registration
    ├── login.html            # Volunteer login
    ├── profile.html          # Volunteer dashboard
    ├── apply.html            # Apply for opportunity
    ├── partials/
    │   └── opp_card.html     # Reusable opportunity card
    └── admin/
        ├── base.html         # Admin base layout
        ├── login.html        # Admin login
        ├── dashboard.html    # Admin overview
        ├── opportunities.html# Post & manage opportunities
        ├── applications.html # Review applications
        ├── volunteers.html   # Volunteer directory
        ├── messages.html     # Contact messages
        ├── reports.html      # Analytics & reports
        └── settings.html     # Change password & settings
```

---

## Setup & Run

### 1. Install Python 3.8+

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://127.0.0.1:5000/
```

The `database.db` file is created automatically on first run with sample data.

---

## Admin Access

URL: `http://127.0.0.1:5000/admin/login`

| Username | Password         |
|----------|-----------------|
| admin    | zerogravity2024 |

> You can change the password from the Settings page inside the admin panel.

---

## Features

### Public Site
- Home with hero, how-it-works, featured opportunities, impact stats, testimonials
- About page with mission, vision, work areas, 80G certification
- Opportunities listing with search + 4 filters (keyword, category, skill, duration)
- Skill-based recommendation — logged-in volunteers see matched opportunities first
- Volunteer registration with skills & interests selection
- Apply for opportunities with motivation & experience
- Volunteer profile with application history and recommendations
- Contact form saved to database
- Gallery page

### Admin Panel (restricted)
- Dashboard with live stats and recent applications
- Post new volunteer opportunities
- Manage / toggle / delete opportunities
- Review and approve/reject volunteer applications
- Full volunteer directory
- Contact messages inbox
- Reports: category breakdown, skill distribution, summary stats
- Change admin password

---

## Tech Stack
- **Backend:** Python (Flask)
- **Database:** SQLite (via Python's built-in `sqlite3`)
- **Frontend:** HTML, CSS, Bootstrap 5, Font Awesome
- **Fonts:** Playfair Display + DM Sans (Google Fonts)

---

## Contact
Zero Gravity NGO — Nagpur, Maharashtra
contact@myzerogravity.org | +91 7507011110
