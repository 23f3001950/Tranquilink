# TranquiLink 🌿
### Digital Psychological Intervention System for Students

Flask · Jinja2 · Bootstrap 5 · SQLite3

---

## Quick Start

```bash
cd tranquilink
pip install flask
python run.py
# → http://localhost:5050
```

## Architecture

- Sequence diagrams: [`docs/sequence-diagrams.md`](docs/sequence-diagrams.md)

---

## Roles & Access

| Feature | Student | Counsellor | Admin |
|---|:---:|:---:|:---:|
| AI Support Chat | ✅ | ❌ | ❌ |
| Book Appointment | ✅ | ❌ | ❌ |
| Log Mood | ✅ | ❌ | ❌ |
| Exercises (view) | ✅ | ❌ | ❌ |
| Review Counsellor | ✅ | ❌ | ❌ |
| Peer Forum (post) | ✅ | ❌ | ❌ |
| Peer Forum (reply) | ✅ | ✅ | ❌ |
| Resources | ✅ | ✅ | ✅ |
| Manage Appointments | ❌ | ✅ | ✅ |
| Add Exercises | ❌ | ✅ | ❌ |
| Emergency Appointments | ❌ | ✅ | ❌ |
| View own Reviews | ❌ | ✅ | ❌ |
| Analytics Dashboard | ❌ | ❌ | ✅ |
| Campaigns | ❌ | ❌ | ✅ |
| Approve Counsellors | ❌ | ❌ | ✅ |

---

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@tranquilink.in | admin123 |
| Counsellor | Register at /counsellor/register | — |
| Student | Register at /register | — |

**Counsellor approval flow:** counsellor registers → admin sees pending request in dashboard → clicks Approve → counsellor can now login.

---

## Project Structure

```
tranquilink/
├── app.py                         # Flask app + CounsellorDB class
├── run.py                         # Startup script
├── requirements.txt
└── templates/
    ├── base.html                  # Navbar (role-aware), footer
    ├── index.html                 # Landing page with counsellor list
    ├── login.html                 # Student/Admin + Counsellor login
    ├── register.html              # Student registration
    ├── counsellor_register.html   # Counsellor credential registration
    ├── dashboard.html             # Role-aware dashboard
    ├── chat.html                  # AI TranquilBot chat
    ├── appointments.html          # Book appointment (student)
    ├── exercises.html             # View exercises (student)
    ├── review_counsellor.html     # Leave a star review (student)
    ├── forum.html                 # Peer forum list
    ├── new_post.html              # Create forum post (student only)
    ├── view_post.html             # View post + replies (counsellor badge)
    ├── resources.html             # Filterable resource hub
    ├── counsellor_dashboard.html  # Counsellor overview
    ├── counsellor_appointments.html
    ├── counsellor_emergency.html  # Emergency case management
    ├── counsellor_exercises.html  # Add/manage exercises
    ├── counsellor_reviews.html    # View student reviews + rating
    ├── admin.html                 # Analytics + counsellor approvals
    └── campaigns.html             # Campaign management
```

---

## Database Design

**`users`** — students and admin  
**`counsellors`** — separate table; registered independently, approved by admin  
**`appointments`** — links student ↔ counsellor  
**`emergency_appointments`** — counsellor-created urgent cases  
**`exercises`** — general or student-specific, created by counsellor  
**`counsellor_reviews`** — star rating + text, posted by student after completed session  
**`forum_posts` / `forum_replies`** — peer forum; replies track `is_counsellor` flag  
**`mood_logs`** — private daily mood entry per student  
**`resources`** — multilingual guides, videos, audio  
**`campaigns`** — admin-created wellness interventions

---

## Crisis Helplines (India)
- **iCall:** 9152987821 (Mon–Sat 8am–10pm)  
- **Vandrevala Foundation:** 1860-2662-345 (24/7)  
- **Snehi:** 044-24640050 (24/7)  
- **NIMHANS:** 080-46110007 (24/7)
