from flask import Flask, render_template, request, redirect, session,flash
import json
from pathlib import Path
import sys


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


# ============================================================
# IMPORT USERS
# ============================================================

from auth import users


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "it-help-desk-secret-key"


# ============================================================
# LOAD TICKETS
# ============================================================

def load_tickets():

    tickets_file = BASE_DIR / "tickets.json"

    with open(tickets_file, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# SAVE TICKETS
# ============================================================

def save_tickets(tickets):

    tickets_file = BASE_DIR / "tickets.json"

    with open(tickets_file, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def home():

    # User must be logged in
    if "username" not in session:
        return redirect("/login")


    # Load all tickets
    all_tickets = load_tickets()


    # --------------------------------------------------------
    # ROLE-BASED TICKET VISIBILITY
    # --------------------------------------------------------

    if session["role"] == "admin":

        # Admin can see every ticket
        tickets = all_tickets.copy()

    elif session["role"] =="support":

         # Support can see tickets assigned to them
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("assigned_to") == session["username"]
        ]
    else:
        # Normal users see only tickets they created
        tickets = [
            ticket
            for ticket in all_tickets
            if ticket.get("created_by")==session["username"]
        ]


    # --------------------------------------------------------
    # SEARCH AND FILTER VALUES
    # --------------------------------------------------------

    search = request.args.get("search", "").strip().lower()
    status = request.args.get("status", "").strip().lower()
    priority = request.args.get("priority", "").strip().lower()
    category = request.args.get("category", "").strip().lower()


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        tickets = [
            ticket
            for ticket in tickets
            if search in str(ticket.get("id", "")).lower()
            or search in ticket.get("title", "").lower()
            or search in ticket.get("description", "").lower()
            or search in ticket.get("category", "").lower()
        ]


    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    if status:

        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("status", "").strip().lower() == status
        ]


    # --------------------------------------------------------
    # PRIORITY FILTER
    # --------------------------------------------------------

    if priority:

        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("priority", "").strip().lower() == priority
        ]


    # --------------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------------

    if category:

        tickets = [
            ticket
            for ticket in tickets
            if ticket.get("category", "").strip().lower() == category
        ]


    # --------------------------------------------------------
    # DASHBOARD STATISTICS
    # --------------------------------------------------------

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
        if ticket.get("status","").strip().lower()=="in progress"
    )


    


    # --------------------------------------------------------
    # SEND DATA TO TEMPLATE
    # --------------------------------------------------------

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets,
        in_progress_tickets=in_progress_tickets,
        search=search,
        status=status,
        priority=priority,
        category=category,
        username=session.get("username"),
        role=session.get("role")
    )


# ============================================================
# CREATE TICKET
# ============================================================

@app.route("/create-ticket", methods=["GET", "POST"])
def create_ticket():

    # User must be logged in
    if "username" not in session:
        return redirect("/login")


    # --------------------------------------------------------
    # FORM SUBMISSION
    # --------------------------------------------------------

    if request.method == "POST":

        title = request.form.get("title","").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "").strip()

        # Allowed ticket values

        allowed_categories = [
           "hardware",
           "software",
           "network",
           "account",
           "other"
        ]

        # Validate category
        if category not in allowed_categories:
            flash("Invalid ticket category.", "error")
            return redirect("/create-ticket")

        # Validate priority
        if priority not in allowed_priorities:
            flash("Invalid ticket priority.",  "error")
            return redirect("/create-ticket")


        # Validate required fields

        if not title:
            flash("Ticket title is required.", "error")
            return redirect("/create-ticket")
        if not description:
            flash("Ticket description is required.", "error")
            return redirect("/create-ticket")
        if not category:
            flash("Please select a ticket category.", "error")
            return redirect("/create-ticket")
        if not priority:
            flash("Please select a ticket priority.", "error")
            return redirect("/create-ticket")

        # Load existing tickets
        tickets = load_tickets()


        # ----------------------------------------------------
        # CREATE NEW ID
        # ----------------------------------------------------

        if tickets:

            new_id = max(
                ticket["id"]
                for ticket in tickets
            ) + 1

        else:

            new_id = 1


        # ----------------------------------------------------
        # CREATE TICKET
        # ----------------------------------------------------

        new_ticket = {

            "id": new_id,

            "title": title,

            "description": description,

            "category": category,

            "priority": priority,

            "status": "Open",

            "created_by": session["username"],

            "assigned_to": None
        }


        # Add ticket
        tickets.append(new_ticket)


        # Save ticket
        save_tickets(tickets)


        # Return to dashboard
        return redirect("/")


    # Show form
    return render_template("create_ticket.html")


# ============================================================
# TICKET DETAILS
# ============================================================

@app.route("/ticket/<int:ticket_id>")
def ticket_details(ticket_id):

    # User must be logged in
    if "username" not in session:
        return redirect("/login")


    # Load tickets
    tickets = load_tickets()


    # Find ticket
    for ticket in tickets:

        if ticket["id"] == ticket_id:

            return render_template(
                "ticket_details.html",
                ticket=ticket,
                role=session.get("role"),
                username=session.get("username")
            )


    # IMPORTANT:
    # This must be OUTSIDE the for loop.
    return "Ticket not found", 404


# ============================================================
# ASSIGN TICKET
# ============================================================

@app.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket(ticket_id):

    # --------------------------------------------------------
    # LOGIN CHECK
    # --------------------------------------------------------

    if "username" not in session:
        return redirect("/login")


    # --------------------------------------------------------
    # ADMIN CHECK
    # --------------------------------------------------------

    if session.get("role") != "admin":

        return "Access denied", 403


    # --------------------------------------------------------
    # GET SELECTED SUPPORT USER
    # --------------------------------------------------------

    assigned_to = request.form["assigned_to"]


    # Load tickets
    tickets = load_tickets()


    # --------------------------------------------------------
    # FIND TICKET
    # --------------------------------------------------------

    for ticket in tickets:

        if ticket["id"] == ticket_id:

            ticket["assigned_to"] = assigned_to

            # Save changes
            save_tickets(tickets)

            # Return to ticket page
            return redirect(f"/ticket/{ticket_id}")


    # Ticket doesn't exist
    return "Ticket not found", 404

@app.route("/ticket/<int:ticket_id>/update", methods=["POST"])
def update_ticket(ticket_id):

    # User must be logged in
    if "username" not in session:
        return redirect("/login")

    # Only admin and support can update tickets
    if session.get("role") not in ["admin", "support"]:
        return "Access denied", 403

    # Get values from the form
    status = request.form["status"]
    priority = request.form["priority"]

    # Load tickets
    tickets = load_tickets()

    # Find the ticket
    for ticket in tickets:

        if ticket["id"] == ticket_id:

            # Update ticket information
            ticket["status"] = status
            ticket["priority"] = priority

            # Save changes
            save_tickets(tickets)

            # Return to ticket details
            return redirect(f"/ticket/{ticket_id}")

    # Ticket doesn't exist
    return "Ticket not found", 404


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # Already logged in?
    if "username" in session:
        return redirect("/")


    # --------------------------------------------------------
    # LOGIN FORM
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]


        # ----------------------------------------------------
        # CHECK USERS
        # ----------------------------------------------------

        for user in users:

            if (
                user["username"] == username
                and user["password"] == password
            ):

                # Save login information
                session["username"] = user["username"]

                session["role"] = user["role"]


                # Go to dashboard
                return redirect("/")


        # Invalid credentials
        return "Invalid username or password", 401


    # Show login page
    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    # Remove session data
    session.clear()


    # Return to login
    return redirect("/login")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print("\n========== FLASK ROUTES ==========")

    for rule in app.url_map.iter_rules():
        print(rule)

    print("==================================\n")

    app.run(debug=True)