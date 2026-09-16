from flask import Flask, render_template, request, redirect
import json
from pathlib import Path

app = Flask(__name__)


def load_tickets():
    base_dir = Path(__file__).resolve().parent.parent
    tickets_file = base_dir / "tickets.json"

    with open(tickets_file, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():

    tickets = load_tickets()

    total_tickets = len(tickets)

    open_tickets = sum(
        1 for ticket in tickets
        if ticket.get("status", "").strip().lower() == "open"
    )

    closed_tickets = sum(
        1 for ticket in tickets
        if ticket.get("status", "").strip().lower() == "closed"
    )
    high_priority_tickets = sum(
        1 for ticket in tickets
        if ticket.get("priority","").strip().lower()=="high"
    )

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets,
        high_priority_tickets = high_priority_tickets
    ) 

    return render_template("index.html", tickets=tickets, total_tickets=total_tickets)
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

if __name__ == "__main__":
    app.run(debug=True)