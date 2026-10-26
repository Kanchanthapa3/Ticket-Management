
from flask import Flask, render_template, request, redirect, session, flash
import json
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
from werkzeug.security import check_password_hash

from database import get_db_connection


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def load_tickets():
    tickets_file = BASE_DIR / "tickets.json"

    with open(tickets_file, "r", encoding="utf-8") as file:
        return json.load(file)


def save_tickets(tickets):
    tickets_file = BASE_DIR / "tickets.json"

    with open(tickets_file, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)


def get_support_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT username
        FROM users
        WHERE role = %s
        ORDER BY username
        """,
        ("support",)
    )

    support_users = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return support_users


@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    all_tickets = load_tickets()

    if session["role"] == "admin":
        tickets = all_tickets.copy()

    elif session["role"] == "support":
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("assigned_to") == session["username"]
        ]

    else:
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("created_by") == session["username"]
        ]

    search = request.args.get("search", "").strip().lower()
    status = request.args.get("status", "").strip().lower()
    priority = request.args.get("priority", "").strip().lower()
    category = request.args.get("category", "").strip().lower()

    if search:
        tickets = [
            ticket
            for ticket in tickets
            if search in str(ticket.get("id", "")).lower()
            or search in ticket.get("title", "").lower()
            or search in ticket.get("description", "").lower()
            or search in ticket.get("category", "").lower()
        ]

    if status:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("status", "").strip().lower() == status
        ]

    if priority:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("priority", "").strip().lower() == priority
        ]

    if category:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("category", "").strip().lower() == category
        ]

    total_tickets = len(tickets)

    open_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("status", "").strip().lower() == "open"
    )

    closed_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("status", "").strip().lower() == "closed"
    )

    in_progress_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("status", "").strip().lower() == "in progress"
    )

    high_priority_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("priority", "").strip().lower() == "high"
    )

    hardware_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "hardware"
    )

    software_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "software"
    )

    network_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "network"
    )

    account_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "account"
    )

    other_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "other"
    )

    if total_tickets:
        open_percentage = (open_tickets / total_tickets) * 100
        in_progress_percentage = (
            in_progress_tickets / total_tickets
        ) * 100
        closed_percentage = (
            closed_tickets / total_tickets
        ) * 100

        software_percentage = (
            software_tickets / total_tickets
        ) * 100

        hardware_percentage = (
            hardware_tickets / total_tickets
        ) * 100

        network_percentage = (
            network_tickets / total_tickets
        ) * 100

        account_percentage = (
            account_tickets / total_tickets
        ) * 100

        other_percentage = (
            other_tickets / total_tickets
        ) * 100

    else:
        open_percentage = 0
        in_progress_percentage = 0
        closed_percentage = 0

        software_percentage = 0
        hardware_percentage = 0
        network_percentage = 0
        account_percentage = 0
        other_percentage = 0

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets,
        in_progress_tickets=in_progress_tickets,
        high_priority_tickets=high_priority_tickets,
        open_percentage=open_percentage,
        in_progress_percentage=in_progress_percentage,
        closed_percentage=closed_percentage,
        hardware_tickets=hardware_tickets,
        software_tickets=software_tickets,
        network_tickets=network_tickets,
        account_tickets=account_tickets,
        other_tickets=other_tickets,
        software_percentage=software_percentage,
        hardware_percentage=hardware_percentage,
        network_percentage=network_percentage,
        account_percentage=account_percentage,
        other_percentage=other_percentage,
        search=search,
        status=status,
        priority=priority,
        category=category,
        username=session.get("username"),
        role=session.get("role")
    )


@app.route("/tickets")
def tickets_page():

    if "username" not in session:
        return redirect("/login")

    all_tickets = load_tickets()

    username = session.get("username")
    role = session.get("role")

    # Get filter values
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    category = request.args.get("category", "").strip()
    selected_date = request.args.get("date", "").strip()

    # Role-based ticket access
    if role == "admin":

        tickets = all_tickets

    elif role == "support":

        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("assigned_to") == username
        ]

    else:

        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("created_by") == username
        ]

    # Search
    if search:

        search_lower = search.lower()

        tickets = [
            ticket
            for ticket in tickets
            if (
                search_lower in str(ticket.get("id", "")).lower()
                or search_lower in ticket.get("title", "").lower()
                or search_lower in ticket.get("description", "").lower()
                or search_lower in ticket.get("category", "").lower()
                or search_lower in ticket.get("created_by", "").lower()
            )
        ]

    # Status
    if status:

        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("status", "").lower() == status.lower()
        ]

    # Priority
    if priority:

        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("priority", "").lower() == priority.lower()
        ]

    # Category
    if category:

        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("category", "").lower() == category.lower()
        ]

    # Date
    if selected_date:

        tickets = [
            ticket
            for ticket in tickets
            if str(ticket.get("created_at", ""))[:10] == selected_date
        ]

    return render_template(
        "tickets.html",
        tickets=tickets,
        username=username,
        role=role,
        search=search,
        status=status,
        priority=priority,
        category=category,
        selected_date=selected_date
    )


@app.route("/create-ticket", methods=["GET", "POST"])
def create_ticket():
    if "username" not in session:
        return redirect("/login")

    if session.get("role") == "support":
        return "Access denied", 403

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "").strip()

        allowed_categories = [
            "hardware",
            "software",
            "network",
            "account",
            "other"
        ]

        allowed_priorities = [
            "Low",
            "Medium",
            "High"
        ]

        if category not in allowed_categories:
            flash("Invalid ticket category.", "error")
            return redirect("/create-ticket")

        if priority not in allowed_priorities:
            flash("Invalid ticket priority.", "error")
            return redirect("/create-ticket")

        if not title:
            flash("Ticket title is required.", "error")
            return redirect("/create-ticket")

        if not description:
            flash("Ticket description is required.", "error")
            return redirect("/create-ticket")

        if len(title) > 100:
            flash(
                "Ticket title must be 100 characters or less.",
                "error"
            )
            return redirect("/create-ticket")

        if len(description) > 500:
            flash(
                "Ticket description must be 500 characters or less.",
                "error"
            )
            return redirect("/create-ticket")

        tickets = load_tickets()

        if tickets:
            new_id = max(ticket["id"] for ticket in tickets) + 1
        else:
            new_id = 1

        new_ticket = {
            "id": new_id,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": "Open",
            "created_by": session["username"],
            "assigned_to": None,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }

        tickets.append(new_ticket)

        save_tickets(tickets)

        return redirect("/")

    return render_template("create_ticket.html")


@app.route("/ticket/<int:ticket_id>")
def ticket_details(ticket_id):
    if "username" not in session:
        return redirect("/login")

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            role = session.get("role")
            username = session.get("username")

            if role == "admin":
                pass

            elif role == "support":
                if ticket.get("assigned_to") != username:
                    return "Access denied", 403

            elif role == "user":
                if ticket.get("created_by") != username:
                    return "Access denied", 403

            return render_template(
                "ticket_details.html",
                ticket=ticket,
                username=username,
                role=role
            )

    return "Ticket not found", 404


@app.route("/ticket/<int:ticket_id>/remark", methods=["POST"])
def add_remark(ticket_id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "support":
        return "Access denied", 403

    remark_text = request.form.get("remark", "").strip()

    if not remark_text:
        flash("Remark cannot be empty.", "error")
        return redirect(f"/ticket/{ticket_id}")

    if len(remark_text) > 1000:
        flash(
            "Remark must be 1000 characters or less.",
            "error"
        )
        return redirect(f"/ticket/{ticket_id}")

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            if ticket.get("assigned_to") != session["username"]:
                return "Access denied", 403

            if "remarks" not in ticket:
                ticket["remarks"] = []

            new_remark = {
                "text": remark_text,
                "created_by": session["username"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            ticket["remarks"].append(new_remark)

            save_tickets(tickets)

            flash("Remark added successfully.", "success")

            return redirect(f"/ticket/{ticket_id}")

    return "Ticket not found", 404


@app.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket(ticket_id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access denied", 403

    assigned_to = request.form.get("assigned_to", "").strip()

    support_users = get_support_users()

    if assigned_to == "":
        assigned_to = None

    elif assigned_to not in support_users:
        return "Invalid support user", 400

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            ticket["assigned_to"] = assigned_to

            save_tickets(tickets)

            return redirect(f"/ticket/{ticket_id}")

    return "Ticket not found", 404


@app.route("/ticket/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):
    if "username" not in session:
        return redirect("/login")

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            role = session.get("role")

            if role == "admin":
                pass

            elif role == "support":
                if ticket.get("assigned_to") != session["username"]:
                    return "Access denied", 403

            else:
                return "Access denied", 403

            status = request.form.get("status")
            priority = request.form.get("priority")

            allowed_statuses = [
                "Open",
                "In Progress",
                "Closed"
            ]

            allowed_priorities = [
                "Low",
                "Medium",
                "High"
            ]

            if status not in allowed_statuses:
                return "Invalid status", 400

            if priority not in allowed_priorities:
                return "Invalid priority", 400

            ticket["status"] = status
            ticket["priority"] = priority

            save_tickets(tickets)

            return redirect(f"/ticket/{ticket_id}")

    return "Ticket not found", 404


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, username, password_hash, role
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

        except Exception:
            flash("Unable to connect to the database.", "error")
            return render_template("login.html")

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

        if user and check_password_hash(user[2], password):

            session.clear()

            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]

            return redirect("/")

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    print("\n========== FLASK ROUTES ==========")

    for rule in app.url_map.iter_rules():
        print(rule)

    print("==================================\n")

    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session, flash
import json
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
from werkzeug.security import check_password_hash

from database import get_db_connection


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def load_tickets():
    tickets_file = BASE_DIR / "tickets.json"

    with open(tickets_file, "r", encoding="utf-8") as file:
        return json.load(file)


def save_tickets(tickets):
    tickets_file = BASE_DIR / "tickets.json"

    with open(tickets_file, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)


def get_support_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT username
        FROM users
        WHERE role = %s
        ORDER BY username
        """,
        ("support",)
    )

    support_users = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return support_users


@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    all_tickets = load_tickets()

    if session["role"] == "admin":
        tickets = all_tickets.copy()

    elif session["role"] == "support":
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("assigned_to") == session["username"]
        ]

    else:
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("created_by") == session["username"]
        ]

    search = request.args.get("search", "").strip().lower()
    status = request.args.get("status", "").strip().lower()
    priority = request.args.get("priority", "").strip().lower()
    category = request.args.get("category", "").strip().lower()

    if search:
        tickets = [
            ticket
            for ticket in tickets
            if search in str(ticket.get("id", "")).lower()
            or search in ticket.get("title", "").lower()
            or search in ticket.get("description", "").lower()
            or search in ticket.get("category", "").lower()
        ]

    if status:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("status", "").strip().lower() == status
        ]

    if priority:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("priority", "").strip().lower() == priority
        ]

    if category:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("category", "").strip().lower() == category
        ]

    total_tickets = len(tickets)

    open_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("status", "").strip().lower() == "open"
    )

    closed_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("status", "").strip().lower() == "closed"
    )

    in_progress_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("status", "").strip().lower() == "in progress"
    )

    high_priority_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("priority", "").strip().lower() == "high"
    )

    hardware_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "hardware"
    )

    software_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "software"
    )

    network_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "network"
    )

    account_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "account"
    )

    other_tickets = sum(
        1
        for ticket in tickets
        if ticket.get("category", "").strip().lower() == "other"
    )

    if total_tickets:
        open_percentage = (open_tickets / total_tickets) * 100
        in_progress_percentage = (
            in_progress_tickets / total_tickets
        ) * 100
        closed_percentage = (
            closed_tickets / total_tickets
        ) * 100

        software_percentage = (
            software_tickets / total_tickets
        ) * 100

        hardware_percentage = (
            hardware_tickets / total_tickets
        ) * 100

        network_percentage = (
            network_tickets / total_tickets
        ) * 100

        account_percentage = (
            account_tickets / total_tickets
        ) * 100

        other_percentage = (
            other_tickets / total_tickets
        ) * 100

    else:
        open_percentage = 0
        in_progress_percentage = 0
        closed_percentage = 0

        software_percentage = 0
        hardware_percentage = 0
        network_percentage = 0
        account_percentage = 0
        other_percentage = 0

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets,
        in_progress_tickets=in_progress_tickets,
        high_priority_tickets=high_priority_tickets,
        open_percentage=open_percentage,
        in_progress_percentage=in_progress_percentage,
        closed_percentage=closed_percentage,
        hardware_tickets=hardware_tickets,
        software_tickets=software_tickets,
        network_tickets=network_tickets,
        account_tickets=account_tickets,
        other_tickets=other_tickets,
        software_percentage=software_percentage,
        hardware_percentage=hardware_percentage,
        network_percentage=network_percentage,
        account_percentage=account_percentage,
        other_percentage=other_percentage,
        search=search,
        status=status,
        priority=priority,
        category=category,
        username=session.get("username"),
        role=session.get("role")
    )


@app.route("/tickets")
def tickets_page():
    if "username" not in session:
        return redirect("/login")

    all_tickets = load_tickets()

    username = session.get("username")
    role = session.get("role")

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    category = request.args.get("category", "").strip()
    selected_date = request.args.get("date", "").strip()

    if role == "admin":
        tickets = all_tickets

    elif role == "support":
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("assigned_to") == username
        ]

    else:
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("created_by") == username
        ]

    if search:
        search_lower = search.lower()

        tickets = [
            ticket
            for ticket in tickets
            if search_lower in str(ticket.get("id", "")).lower()
            or search_lower in ticket.get("title", "").lower()
            or search_lower in ticket.get("description", "").lower()
            or search_lower in ticket.get("category", "").lower()
        ]

    if status:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("status", "").lower() == status.lower()
        ]

    if priority:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("priority", "").lower() == priority.lower()
        ]

    if category:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("category", "").lower() == category.lower()
        ]

    if selected_date:
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("created_at") == selected_date
        ]

    return render_template(
        "tickets.html",
        tickets=tickets,
        username=username,
        role=role,
        search=search,
        status=status,
        priority=priority,
        category=category,
        selected_date=selected_date
    )


@app.route("/create-ticket", methods=["GET", "POST"])
def create_ticket():
    if "username" not in session:
        return redirect("/login")

    if session.get("role") == "support":
        return "Access denied", 403

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "").strip()

        allowed_categories = [
            "hardware",
            "software",
            "network",
            "account",
            "other"
        ]

        allowed_priorities = [
            "Low",
            "Medium",
            "High"
        ]

        if category not in allowed_categories:
            flash("Invalid ticket category.", "error")
            return redirect("/create-ticket")

        if priority not in allowed_priorities:
            flash("Invalid ticket priority.", "error")
            return redirect("/create-ticket")

        if not title:
            flash("Ticket title is required.", "error")
            return redirect("/create-ticket")

        if not description:
            flash("Ticket description is required.", "error")
            return redirect("/create-ticket")

        if len(title) > 100:
            flash(
                "Ticket title must be 100 characters or less.",
                "error"
            )
            return redirect("/create-ticket")

        if len(description) > 500:
            flash(
                "Ticket description must be 500 characters or less.",
                "error"
            )
            return redirect("/create-ticket")

        tickets = load_tickets()

        if tickets:
            new_id = max(ticket["id"] for ticket in tickets) + 1
        else:
            new_id = 1

        new_ticket = {
            "id": new_id,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": "Open",
            "created_by": session["username"],
            "assigned_to": None,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }

        tickets.append(new_ticket)

        save_tickets(tickets)

        return redirect("/")

    return render_template("create_ticket.html")


@app.route("/ticket/<int:ticket_id>")
def ticket_details(ticket_id):
    if "username" not in session:
        return redirect("/login")

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            role = session.get("role")
            username = session.get("username")

            if role == "admin":
                pass

            elif role == "support":
                if ticket.get("assigned_to") != username:
                    return "Access denied", 403

            elif role == "user":
                if ticket.get("created_by") != username:
                    return "Access denied", 403

            return render_template(
                "ticket_details.html",
                ticket=ticket,
                username=username,
                role=role
            )

    return "Ticket not found", 404


@app.route("/ticket/<int:ticket_id>/remark", methods=["POST"])
def add_remark(ticket_id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "support":
        return "Access denied", 403

    remark_text = request.form.get("remark", "").strip()

    if not remark_text:
        flash("Remark cannot be empty.", "error")
        return redirect(f"/ticket/{ticket_id}")

    if len(remark_text) > 1000:
        flash(
            "Remark must be 1000 characters or less.",
            "error"
        )
        return redirect(f"/ticket/{ticket_id}")

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            if ticket.get("assigned_to") != session["username"]:
                return "Access denied", 403

            if "remarks" not in ticket:
                ticket["remarks"] = []

            new_remark = {
                "text": remark_text,
                "created_by": session["username"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            ticket["remarks"].append(new_remark)

            save_tickets(tickets)

            flash("Remark added successfully.", "success")

            return redirect(f"/ticket/{ticket_id}")

    return "Ticket not found", 404


@app.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket(ticket_id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access denied", 403

    assigned_to = request.form.get("assigned_to", "").strip()

    support_users = get_support_users()

    if assigned_to == "":
        assigned_to = None

    elif assigned_to not in support_users:
        return "Invalid support user", 400

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            ticket["assigned_to"] = assigned_to

            save_tickets(tickets)

            return redirect(f"/ticket/{ticket_id}")

    return "Ticket not found", 404


@app.route("/ticket/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):
    if "username" not in session:
        return redirect("/login")

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:

            role = session.get("role")

            if role == "admin":
                pass

            elif role == "support":
                if ticket.get("assigned_to") != session["username"]:
                    return "Access denied", 403

            else:
                return "Access denied", 403

            status = request.form.get("status")
            priority = request.form.get("priority")

            allowed_statuses = [
                "Open",
                "In Progress",
                "Closed"
            ]

            allowed_priorities = [
                "Low",
                "Medium",
                "High"
            ]

            if status not in allowed_statuses:
                return "Invalid status", 400

            if priority not in allowed_priorities:
                return "Invalid priority", 400

            ticket["status"] = status
            ticket["priority"] = priority

            save_tickets(tickets)

            return redirect(f"/ticket/{ticket_id}")

    return "Ticket not found", 404


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, username, password_hash, role
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

        except Exception:
            flash("Unable to connect to the database.", "error")
            return render_template("login.html")

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

        if user and check_password_hash(user[2], password):

            session.clear()

            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]

            return redirect("/")

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    print("\n========== FLASK ROUTES ==========")

    for rule in app.url_map.iter_rules():
        print(rule)

    print("==================================\n")

    app.run(debug=True)
