from flask import Flask, render_template, request, redirect, session, flash
import os

from dotenv import load_dotenv
from werkzeug.security import check_password_hash

from database import get_db_connection


load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def get_support_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT username
            FROM users
            WHERE role = %s
            ORDER BY username
            """,
            ("support",)
        )

        return [row[0] for row in cursor.fetchall()]

    finally:
        cursor.close()
        connection.close()


def get_user_id(username):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        result = cursor.fetchone()

        if not result:
            return None

        return result[0]

    finally:
        cursor.close()
        connection.close()


def get_tickets():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                t.id,
                t.title,
                t.description,
                t.category,
                t.priority,
                t.status,
                t.created_at,
                creator.username AS created_by,
                assigned.username AS assigned_to
            FROM tickets t
            JOIN users creator
                ON t.created_by = creator.id
            LEFT JOIN users assigned
                ON t.assigned_to = assigned.id
            ORDER BY t.id DESC
            """
        )

        rows = cursor.fetchall()

        tickets = []

        for row in rows:
            tickets.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "category": row[3],
                    "priority": row[4],
                    "status": row[5],
                    "created_at": row[6],
                    "created_by": row[7],
                    "assigned_to": row[8],
                }
            )

        return tickets

    finally:
        cursor.close()
        connection.close()


def get_ticket_by_id(ticket_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                t.id,
                t.title,
                t.description,
                t.category,
                t.priority,
                t.status,
                t.created_at,
                creator.username AS created_by,
                assigned.username AS assigned_to
            FROM tickets t
            JOIN users creator
                ON t.created_by = creator.id
            LEFT JOIN users assigned
                ON t.assigned_to = assigned.id
            WHERE t.id = %s
            """,
            (ticket_id,)
        )

        row = cursor.fetchone()

        if not row:
            return None

        ticket = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "category": row[3],
            "priority": row[4],
            "status": row[5],
            "created_at": row[6],
            "created_by": row[7],
            "assigned_to": row[8],
            "remarks": []
        }

        cursor.execute(
            """
            SELECT
                r.remark,
                u.username,
                r.created_at
            FROM remarks r
            JOIN users u
                ON r.created_by = u.id
            WHERE r.ticket_id = %s
            ORDER BY r.created_at ASC
            """,
            (ticket_id,)
        )

        for remark in cursor.fetchall():
            ticket["remarks"].append(
                {
                    "text": remark[0],
                    "created_by": remark[1],
                    "created_at": remark[2]
                }
            )

        return ticket

    finally:
        cursor.close()
        connection.close()


@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    tickets = get_tickets()

    username = session.get("username")
    role = session.get("role")

    if role == "support":
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("assigned_to") == username
        ]

    elif role == "user":
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("created_by") == username
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
        tickets=tickets[:5],
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
        username=username,
        role=role
    )


@app.route("/tickets")
def tickets_page():
    if "username" not in session:
        return redirect("/login")

    tickets = get_tickets()

    username = session.get("username")
    role = session.get("role")

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    category = request.args.get("category", "").strip()
    selected_date = request.args.get("date", "").strip()

    if role == "support":
        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("assigned_to") == username
        ]

    elif role == "user":
        tickets = [
            ticket
            for ticket in tickets
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
            or search_lower in ticket.get("created_by", "").lower()
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
    created_by = get_user_id(session["username"])
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

        user_id = session.get("user_id")

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO tickets (
                    title,
                    description,
                    category,
                    priority,
                    status,
                    created_by,
                    assigned_to
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    title,
                    description,
                    category,
                    priority,
                    "Open",
                    user_id,
                    None
                )
            )
            ticket_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO ticket_history (
                  ticket_id,
                  user_id,
                  action,
                  details
                )
                VALUES (%s, %s, %s, %s) 
                 """,
                (
                   ticket_id,
                   created_by,
                   "Ticket Created",
                "Ticket was created"
                ) 
            )

            connection.commit()

        except Exception as error:
            connection.rollback()
            print("CREATE TICKET ERROR:", repr(error))
            raise
            return redirect("/create-ticket")

        finally:
            cursor.close()
            connection.close()

        return redirect("/")

    return render_template("create_ticket.html")


@app.route("/ticket/<int:ticket_id>")
def ticket_details(ticket_id):
    if "username" not in session:
        return redirect("/login")

    ticket = get_ticket_by_id(ticket_id)

    if not ticket:
        return "Ticket not found", 404

    role = session.get("role")
    username = session.get("username")

    if role == "support":
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
        flash("Remark must be 1000 characters or less.", "error")
        return redirect(f"/ticket/{ticket_id}")

    ticket = get_ticket_by_id(ticket_id)

    if not ticket:
        return "Ticket not found", 404

    if ticket.get("assigned_to") != session["username"]:
        return "Access denied", 403

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        user_id = get_user_id(session["username"])

        if user_id is None:
            raise ValueError("Logged-in user was not found.")

        cursor.execute(
            """
            INSERT INTO remarks (
                ticket_id,
                created_by,
                remark
            )
            VALUES (%s, %s, %s)
            """,
            (ticket_id, user_id, remark_text)
        )

        cursor.execute(
            """
            INSERT INTO ticket_history (
                ticket_id,
                user_id,
                action,
                details
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                ticket_id,
                user_id,
                "Remark Added",
                f"Support added a remark: {remark_text}"
            )
        )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("ADD REMARK ERROR:", repr(error))
        flash("Unable to add remark.", "error")
        return redirect(f"/ticket/{ticket_id}")

    finally:
        cursor.close()
        connection.close()

    flash("Remark added successfully.", "success")
    return redirect(f"/ticket/{ticket_id}")



@app.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket(ticket_id):
    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access denied", 403

    assigned_to = request.form.get("assigned_to", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT assigned_to
            FROM tickets
            WHERE id = %s
            """,
            (ticket_id,)
        )
        ticket = cursor.fetchone()

        if not ticket:
            return "Ticket not found", 404

        previous_assignee_id = ticket[0]
        assigned_user_id = None

        if assigned_to:
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE username = %s
                  AND role = %s
                """,
                (assigned_to, "support")
            )

            user = cursor.fetchone()

            if not user:
                return "Invalid support user", 400

            assigned_user_id = user[0]

        if previous_assignee_id != assigned_user_id:
            cursor.execute(
                """
                UPDATE tickets
                SET assigned_to = %s
                WHERE id = %s
                """,
                (assigned_user_id, ticket_id)
            )

            if assigned_user_id is None:
                details = "Ticket assignment removed"
                action = "Ticket Unassigned"
            else:
                details = f"Ticket assigned to {assigned_to}"
                action = "Ticket Assigned"

            cursor.execute(
                """
                INSERT INTO ticket_history (
                    ticket_id,
                    user_id,
                    action,
                    details
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    get_user_id(session["username"]),
                    action,
                    details
                )
            )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("ASSIGN TICKET ERROR:", repr(error))
        return "Unable to assign ticket", 500

    finally:
        cursor.close()
        connection.close()

    return redirect(f"/ticket/{ticket_id}")




@app.route("/ticket/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):
    if "username" not in session:
        return redirect("/login")

    ticket = get_ticket_by_id(ticket_id)

    if not ticket:
        return "Ticket not found", 404

    role = session.get("role")

    if role == "support":
        if ticket.get("assigned_to") != session["username"]:
            return "Access denied", 403
    elif role != "admin":
        return "Access denied", 403

    status = request.form.get("status")
    priority = request.form.get("priority")

    allowed_statuses = ["Open", "In Progress", "Closed"]
    allowed_priorities = ["Low", "Medium", "High"]

    if status not in allowed_statuses:
        return "Invalid status", 400

    if priority not in allowed_priorities:
        return "Invalid priority", 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT status, priority
            FROM tickets
            WHERE id = %s
            """,
            (ticket_id,)
        )
        old_ticket = cursor.fetchone()

        if not old_ticket:
            return "Ticket not found", 404

        old_status, old_priority = old_ticket

        cursor.execute(
            """
            UPDATE tickets
            SET status = %s,
                priority = %s
            WHERE id = %s
            """,
            (status, priority, ticket_id)
        )

        user_id = get_user_id(session["username"])

        if old_status != status:
            cursor.execute(
                """
                INSERT INTO ticket_history
                    (ticket_id, user_id, action, details)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    user_id,
                    "Status Changed",
                    f"Status changed from {old_status} to {status}"
                )
            )

        if old_priority != priority:
            cursor.execute(
                """
                INSERT INTO ticket_history
                    (ticket_id, user_id, action, details)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    user_id,
                    "Priority Changed",
                    f"Priority changed from {old_priority} to {priority}"
                )
            )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("UPDATE TICKET ERROR:", repr(error))
        return "Unable to update ticket", 500

    finally:
        cursor.close()
        connection.close()

    return redirect(f"/ticket/{ticket_id}")



@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash(
                "Username and password are required.",
                "error"
            )
            return render_template("login.html")

        connection = None
        cursor = None
        user = None

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
            flash(
                "Unable to connect to the database.",
                "error"
            )
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

        flash(
            "Invalid username or password.",
            "error"
        )

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