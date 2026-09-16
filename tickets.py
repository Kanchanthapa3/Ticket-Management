import json
import time
from colors import RED, GREEN, YELLOW, BLUE, CYAN, RESET
from auth import users


tickets = []
ticket_id = 1


# ==============================
# SAVE TICKETS
# ==============================

def save_tickets():
    with open("tickets.json", "w") as file:
        json.dump(tickets, file, indent=4)


# ==============================
# LOAD TICKETS
# ==============================

def load_tickets():
    global tickets
    global ticket_id

    try:
        with open("tickets.json", "r") as file:
            tickets = json.load(file)

        if tickets:
            ticket_id = max(ticket["id"] for ticket in tickets) + 1
        else:
            ticket_id = 1

    except FileNotFoundError:
        tickets = []
        ticket_id = 1


# ==============================
# LOADING ANIMATION
# ==============================

def loading_animation(message):
    print(message)

    for i in range(1, 11):
        bar = "█" * i
        spaces = " " * (10 - i)

        print(
            "\r[" + bar + spaces + "] " + str(i * 10) + "%",
            end="",
            flush=True
        )

        time.sleep(0.1)

    print()


# ==============================
# GET PRIORITY
# ==============================

def get_priority():
    while True:
        priority = input("Enter priority (High/Medium/Low): ")

        if priority.lower() in ["high", "medium", "low"]:
            return priority.capitalize()

        print(
            RED + "Invalid priority! Choose High, Medium, or Low." + RESET
        )


# ==============================
# GET STATUS
# ==============================

def get_status():
    while True:
        status = input("Enter status (Open/In Progress/Closed): ")

        if status.lower() in ["open", "in progress", "closed"]:
            return status.title()

        print(RED + "Invalid status!" + RESET)


# ==============================
# CREATE TICKET
# ==============================

def create_ticket(current_user):
    global ticket_id

    title = input("Enter ticket title: ")
    description = input("Enter ticket description: ")
    category = input("Enter category: ")
    priority = get_priority()

    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "status": "Open",
        "created_by": current_user["username"],
        "assigned_to": None
    }

    tickets.append(ticket)

    ticket_id += 1

    save_tickets()

    loading_animation("Creating ticket")

    print(GREEN + "✓ Ticket created successfully!" + RESET)
    print("Your Ticket ID is:", ticket["id"])


# ==============================
# ASSIGN TICKET
# ==============================

def assign_ticket():
    ticket_id_input = get_ticket_id()

    for ticket in tickets:
        if ticket["id"] == ticket_id_input:
            break
    else:
        print(RED + "\nTicket not found." + RESET)
        return

    assigned_to = input("Enter support username: ")
    support_users = [
        user["username"]
        for user in users
        if user["role"] == "support"
    
    ]
    if assigned_to not in support_users:
        print(RED + "\n✗ Support user not found." + RESET)
        return

    ticket["assigned_to"] = assigned_to

    save_tickets()

    print(GREEN + "\n✓ Ticket assigned successfully!" + RESET)


# ==============================
# PRIORITY COLOR
# ==============================

def priority_color(priority):

    if priority.lower() == "high":
        return RED + priority.upper() + RESET

    elif priority.lower() == "medium":
        return YELLOW + priority.upper() + RESET

    elif priority.lower() == "low":
        return GREEN + priority.upper() + RESET

    else:
        return RESET + priority + RESET


# ==============================
# STATUS COLOR
# ==============================

def status_color(status):

    if status.lower() == "open":
        return GREEN + status.upper() + RESET

    elif status.lower() == "in progress":
        return YELLOW + status.upper() + RESET

    elif status.lower() == "closed":
        return BLUE + status.upper() + RESET

    else:
        return RESET + status + RESET


# ==============================
# DISPLAY TICKET
# ==============================

def display_ticket(ticket):

    print(
        CYAN
        + "\n╔══════════════════════════════════════════╗"
        + RESET
    )

    print(
        CYAN
        + "║"
        + RESET
        + f"              🎫 TICKET #{ticket['id']:<3}"
        + "            "
        + CYAN
        + "║"
        + RESET
    )

    print(
        CYAN
        + "╠══════════════════════════════════════════╣"
        + RESET
    )

    print(f"║ Title       : {ticket['title']}")
    print(f"║ Category    : {ticket['category']}")

    print(
        "║ Priority    : "
        + priority_color(ticket["priority"])
    )

    print(
        "║ Status      : "
        + status_color(ticket["status"])
    )

    print(f"║ Description : {ticket['description']}")

    print(
        f"║ Created By  : {ticket.get('created_by', 'Unknown')}"
    )

    print(
        f"║ Assigned To : {ticket.get('assigned_to', 'Not Assigned')}"
    )

    print(
        CYAN
        + "╚══════════════════════════════════════════╝"
        + RESET
    )


# ==============================
# VIEW ALL TICKETS
# ==============================

def view_tickets(current_user=None):

    if current_user and current_user["role"] == "user":

        user_tickets = [
            ticket
            for ticket in tickets
            if ticket.get("created_by") == current_user["username"]
        ]

    else:
        user_tickets = tickets

    print("\n====== ALL TICKETS ======")

    if len(user_tickets) == 0:
        print("No tickets found.")
        return

    for ticket in user_tickets:
        display_ticket(ticket)


# ==============================
# SEARCH TICKET
# ==============================

def search_ticket(current_user=None):

    if current_user and current_user["role"] == "user":

        searchable_tickets = [
            ticket
            for ticket in tickets
            if ticket.get("created_by") == current_user["username"]
        ]

    else:
        searchable_tickets = tickets

    search_id = get_ticket_id()

    for ticket in searchable_tickets:

        if ticket["id"] == search_id:

            print("\n====== TICKET FOUND ======")

            print("Ticket ID:", ticket["id"])
            print("Title:", ticket["title"])
            print("Description:", ticket["description"])
            print("Category:", ticket["category"])
            print("Priority:", ticket["priority"])
            print("Status:", ticket["status"])
            print(
                "Created By:",
                ticket.get("created_by", "Unknown")
            )
            print(
                "Assigned To:",
                ticket.get("assigned_to", "Not Assigned")
            )

            return

    print("\nTicket not found.")


# ==============================
# UPDATE TICKET
# ==============================

def update_ticket(current_user=None):

    update_id = get_ticket_id()

    for ticket in tickets:
        if ticket["id"] == update_id:
            break
    else:
        print(RED + "\nTicket not found." + RESET)
        return

    # Check support user's permission
    if current_user and current_user["role"] == "support":

        if ticket.get("assigned_to") != current_user["username"]:

            print(
                RED
                + "\n✗ You cannot update this ticket."
                + RESET
            )

            print(
                "This ticket is assigned to:",
                ticket.get("assigned_to", "Not Assigned")
            )

            return

    print("\n====== UPDATE TICKET ======")

    print("1. Title")
    print("2. Description")
    print("3. Category")
    print("4. Priority")
    print("5. Status")

    choice = input("What do you want to update? ")

    if choice == "1":

        ticket["title"] = input(
            "Enter new title: "
        )

    elif choice == "2":

        ticket["description"] = input(
            "Enter new description: "
        )

    elif choice == "3":

        ticket["category"] = input(
            "Enter new category: "
        )

    elif choice == "4":

        ticket["priority"] = get_priority()

    elif choice == "5":

        ticket["status"] = get_status()

    else:

        print("Invalid choice.")
        return

    save_tickets()

    print(
        GREEN
        + "\n✓ Ticket updated successfully!"
        + RESET
    )


# ==============================
# GET TICKET ID
# ==============================

def get_ticket_id():

    while True:

        try:

            ticket_id_input = int(
                input("Enter ticket ID: ")
            )

            if ticket_id_input > 0:
                return ticket_id_input

            print(
                RED
                + "Ticket ID must be greater than 0."
                + RESET
            )

        except ValueError:

            print(
                RED
                + "Please enter a valid number."
                + RESET
            )


# ==============================
# DELETE TICKET
# ==============================

def delete_ticket(current_user=None):

    delete_id = get_ticket_id()

    for ticket in tickets:

    

        if ticket["id"] == delete_id:

            print("\nTicket found.")
            print("Title:", ticket["title"])
            print("Status:", ticket["status"])

            if current_user and current_user['role']=='support':

                if ticket.get("assigned_to")!= current_user["username"]:
                    print(
                        RED + "\n✗ You cannot delete this ticket." + RESET
                    )
                    print("This ticket is assigned to: ", ticket.get("assignet_to", "Not Assigned"))
                    return

            confirmation = input(
                "Are you sure you want to delete this ticket? (yes/no): "
            )

            if confirmation.lower() == "yes":

                tickets.remove(ticket)

                save_tickets()

                print(
                    GREEN
                    + "\n✓ Ticket deleted successfully!"
                    + RESET
                )

            else:

                print(
                    "\nTicket was not deleted."
                )

            return

    print("\nTicket not found.")

def view_assigned_tickets(current_user):
    assigned_tickets = [
        ticket for ticket in tickets
        if ticket.get("assigned_to") == current_user
        ["username"]

    ]
    if len(assigned_tickets) == 0:
        print(YELLOW +"\nNo tickets are assigned to you." + RESET)
        return

    print(CYAN + "\nn====== MY ASSIGNED TICKETS ======" + RESET)

    for ticket in assigned_tickets:
        display_ticket(ticket)
