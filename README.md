# Zero Gravity NGO — Volunteer Management & Engagement Platform

A full-stack Flask-based volunteer management platform designed to streamline volunteer engagement, opportunity management, application workflows, and operational reporting for NGOs and social impact organizations.

The platform enables volunteers to discover opportunities, apply seamlessly, and track participation while providing administrators with centralized tools for workflow management, analytics, and engagement monitoring.

---

# Live Demo

🔗 https://zerogravity-2k5r.onrender.com/

---

# Problem Statement

NGOs often face challenges in:
- Managing volunteer applications efficiently
- Tracking opportunities and engagement
- Organizing operational workflows
- Monitoring participation analytics
- Centralizing communication and reporting

This platform was developed to digitize and automate volunteer management operations through a centralized web-based system.

---

# Key Features

## Volunteer Portal
- Volunteer registration & authentication
- Personalized volunteer dashboard
- Browse opportunities with advanced filtering
- Skill-based opportunity recommendations
- Application tracking & participation history
- Profile management

---

## Opportunity Management
- Create and manage volunteer opportunities
- Category, duration, and skill-based filtering
- Search-driven opportunity discovery
- Dynamic opportunity status management

---

## Admin Dashboard
- Centralized admin control panel
- Volunteer directory management
- Application review workflows
- Opportunity moderation
- Contact message management
- Operational reporting dashboard

---

## Analytics & Reporting
- Volunteer participation statistics
- Opportunity category distribution
- Skill analysis dashboards
- Application trend monitoring
- Operational summary reporting

---

# System Architecture

```text
Frontend (HTML/CSS/Bootstrap)
        │
        ▼
Flask Application Layer
        │
 ┌───────────────────┐
 │ Business Logic    │
 │ Authentication    │
 │ Workflow Handling │
 │ Reporting Engine  │
 └───────────────────┘
        │
        ▼
SQLite Database
```

---

# Project Architecture

```text
zerogravity/
│
├── app.py
├── requirements.txt
├── database.db
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── admin.css
│   │
│   └── js/
│       └── main.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── opportunities.html
│   ├── gallery.html
│   ├── contact.html
│   ├── register.html
│   ├── login.html
│   ├── profile.html
│   ├── apply.html
│   │
│   ├── partials/
│   │   └── opp_card.html
│   │
│   └── admin/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── opportunities.html
│       ├── applications.html
│       ├── volunteers.html
│       ├── messages.html
│       ├── reports.html
│       └── settings.html
```

---

# Tech Stack

## Backend
- Python
- Flask

## Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Database
- SQLite

## Tools & Libraries
- Font Awesome
- Google Fonts

---

# Core Functionalities

## Authentication & Access Control
- Volunteer login/signup
- Secure session handling
- Admin authentication workflows

---

## Workflow Management
- Volunteer application lifecycle tracking
- Opportunity moderation workflows
- Admin approval/review system

---

## Recommendation System
- Skill-based volunteer recommendations
- Personalized opportunity matching

---

## Reporting & Insights
- Dashboard-based operational analytics
- Participation tracking
- Volunteer engagement reporting

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/zerogravity.git
cd zerogravity
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate virtual environment:

### Windows
```bash
venv\Scripts\activate
```

### Mac/Linux
```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Application

```bash
python app.py
```

---

## 5. Open in Browser

```text
http://127.0.0.1:5000/
```

---

# Screenshots

## Home Dashboard
[Add Screenshot Here]

---

## Volunteer Opportunity Management
[Add Screenshot Here]

---

## Admin Analytics Dashboard
[Add Screenshot Here]

---

## Reports & Insights
[Add Screenshot Here]

---

# Future Improvements

- REST API integration
- Cloud database migration
- Email notifications
- Role-based access control
- Docker deployment
- Real-time updates
- Mobile responsiveness enhancements

---

# Learning Outcomes

- Full-stack application development
- Flask backend architecture
- Database design & management
- Authentication systems
- Workflow automation concepts
- Dashboard & reporting systems
- Operational analytics implementation

---

# Deployment

The application can be deployed using:
- Render
- Railway
- Heroku
- PythonAnywhere

---
