from flask import Flask, render_template, request, redirect, session
import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from auth import users

print(users)


app = Flask(__name__)
app.secret_key = "it-help-desk-secret-key"


def load_tickets():
    base_dir = Path(__file__).resolve().parent.parent
    tickets_file = base_dir / "tickets.json"

    with open(tickets_file, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():

    all_tickets = load_tickets()
    tickets= all_tickets.copy()

    # Get search and filter values
    search = request.args.get("search", "").strip().lower()
    status = request.args.get("status", "").strip().lower()
    priority = request.args.get("priority", "").strip().lower()
    category = request.args.get("category", "").strip().lower()


    # Search tickets
    if search:
        tickets = [
            ticket for ticket in tickets
            if search in str(ticket.get("id", "")).lower()
            or search in ticket.get("title", "").lower()
            or search in ticket.get("description", "").lower()
            or search in ticket.get("category", "").lower()
        ]


    # Filter by status
    if status:
        tickets = [
            ticket for ticket in tickets
            if ticket.get("status", "").strip().lower() == status
        ]


    # Filter by priority
    if priority:
        tickets = [
            ticket for ticket in tickets
            if ticket.get("priority", "").strip().lower() == priority
        ]

    #Filter by category
    if category:
        tickets=[
            ticket for ticket in tickets
            if ticket.get("category","").strip().lower() == category
        ]


    # Dashboard statistics
    total_tickets = len(tickets)

    open_tickets = sum(
        1 for ticket in all_tickets
        if ticket.get("status", "").strip().lower() == "open"
    )

    closed_tickets = sum(
        1 for ticket in all_tickets
        if ticket.get("status", "").strip().lower() == "closed"
    )

    high_priority_tickets = sum(
        1 for ticket in all_tickets
        if ticket.get("priority", "").strip().lower() == "high"
    )

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets,
        high_priority_tickets=high_priority_tickets,
        search=search,
        status=status,
        priority=priority,
        category=category
    )
@app.route("/create-ticket", methods=["GET", "POST"])
def create_ticket():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]

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
            "created_by": "web_user",
            "assigned_to": None
        }

        tickets.append(new_ticket)

        base_dir = Path(__file__).resolve().parent.parent
        tickets_file = base_dir / "tickets.json"

        with open(tickets_file, "w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4)

        return redirect("/")

    return render_template("create_ticket.html")
@app.route("/ticket/<int:ticket_id>")
def ticket_details(ticket_id):

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return render_template(
                "ticket_details.html",
                ticket=ticket
            )
        return "Ticket not found",404

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        print("USERNAME:", repr(username))
        print("PASSWORD:", repr(password))

        for user in users:

            if (
                user["username"] == username
                and user["password"] == password
            ):
                session["username"] = user["username"]
                session["role"] = user["role"]

                return redirect("/")

                

        return "Invalid username or password", 401

    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)