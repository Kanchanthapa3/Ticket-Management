# 🛠️ IT Help Desk & Ticket Management System

A Python-based IT Help Desk and Ticket Management System designed to manage technical support requests, assign tickets to support staff, track ticket status, and provide role-based access.

The project started as a command-line application and was later extended into a Flask-based web application with a responsive dashboard.

---

## ✨ Features

### 🎫 Ticket Management

* Create support tickets
* View tickets
* Search tickets
* Filter tickets by status, priority, and category
* View detailed ticket information
* Update ticket status and priority
* Delete tickets
* Assign tickets to support staff

### 👥 Role-Based Access

The system supports three user roles:

**Admin**

* View all tickets
* Create tickets
* Assign tickets
* Update tickets
* Delete tickets

**Support**

* View tickets assigned to them
* Update assigned tickets
* Manage ticket status and priority

**User**

* Create tickets
* View tickets they created
* Track their submitted requests

### 📊 Dashboard

* Total ticket count
* Open tickets
* In-progress tickets
* Closed tickets
* High-priority tickets
* Ticket status visualization

### 🎨 User Interface

* Responsive web interface
* Sidebar navigation
* Mobile-friendly layout
* Ticket cards
* Status and priority badges
* Hover animations
* Empty-state messages
* Responsive mobile navigation

### 🔐 Validation & Access Control

* Login authentication
* Role-based authorization
* Ticket ownership restrictions
* Assignment validation
* Category validation
* Priority validation
* Ticket title and description length validation

---

## 🧰 Technologies Used

* **Python**
* **Flask**
* **HTML5**
* **CSS3**
* **Jinja2**
* **JSON**
* **Git & GitHub**

---

## 📁 Project Structure

```text
TicketMgmt/
│
├── main.py
├── auth.py
├── tickets.py
├── colors.py
├── tickets.json
├── requirements.txt
├── README.md
│
└── web/
    ├── app.py
    │
    ├── templates/
    │   ├── index.html
    │   ├── tickets.html
    │   ├── create_ticket.html
    │   ├── ticket_details.html
    │   └── login.html
    │
    └── static/
        └── style.css
```

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Kanchanthapa3/Ticket-Management.git
```

### 2. Open the project

```bash
cd Ticket-Management
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Start the Flask application

```bash
python web/app.py
```

### 7. Open the application

Open the local Flask address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

---

## 👤 Demo Roles

The current development version contains demo accounts for testing different roles.

| Username    | Role    |
| ----------- | ------- |
| `kanchan`   | Admin   |
| `support`   | Support |
| `pratiksha` | User    |

> Demo credentials are currently stored in `auth.py` for development purposes. They should be replaced with secure password handling before production deployment.

---

## 🔄 Current Data Storage

The current version uses a JSON file for ticket persistence:

```text
tickets.json
```

This keeps the project simple during development while the application features are being built.

A database-backed version is planned as a later development stage.

---

## 🎯 Project Goals

This project was created to practice and demonstrate practical software development concepts including:

* Python programming
* Flask web development
* CRUD operations
* Authentication
* Role-based authorization
* Data validation
* File-based persistence
* Web application design
* Responsive UI development
* Git and GitHub workflow

---

## 🔮 Future Improvements

Planned improvements include:

* SQLite/database integration
* SQLAlchemy ORM
* Secure password hashing
* Better authentication management
* Ticket activity/history
* Notifications
* Improved reporting
* Production deployment
* Additional dashboard analytics

---

## 📌 Project Status

**Development status:** Active development

The core ticket management, authentication, role-based access, assignment, dashboard, filtering, and responsive interface features have been implemented.

The database migration and final production/security improvements are planned for the final development stage.
