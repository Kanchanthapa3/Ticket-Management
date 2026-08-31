import json

tickets = []
ticket_id = 1


def save_tickets():
    with open("tickets.json", "w") as file:
        json.dump(tickets, file, indent=4)

def load_tickets():
    global tickets

    with open("tickets.json", "r") as file:
        tickets = json.load(file)


# ==============================
# CREATE TICKET
# ==============================

def create_ticket():
    global ticket_id

    title = input("Enter ticket title: ")
    description = input("Enter ticket description: ")
    category = input("Enter category: ")
    priority = input("Mention priority based on your emergency: ")

    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "status": "Open"
    }

    tickets.append(ticket)

    ticket_id += 1
    save_tickets()

    print("\nTicket created successfully!")
    print("Your Ticket ID is:", ticket["id"])


# ==============================
# VIEW ALL TICKETS
# ==============================

def view_tickets():
    print("\n====== ALL TICKETS ======")

    if len(tickets) == 0:
        print("No tickets found.")
        return

    for ticket in tickets:
        print("\nTicket ID:", ticket["id"])
        print("Title:", ticket["title"])
        print("Description:", ticket["description"])
        print("Category:", ticket["category"])
        print("Priority:", ticket["priority"])
        print("Status:", ticket["status"])
        print("--------------------------------")


# ==============================
# SEARCH TICKET
# ==============================

def search_ticket():
    search_id = int(input("Enter ticket ID to search: "))

    for ticket in tickets:
        if ticket["id"] == search_id:
            print("\n====== TICKET FOUND ======")
            print("Ticket ID:", ticket["id"])
            print("Title:", ticket["title"])
            print("Description:", ticket["description"])
            print("Category:", ticket["category"])
            print("Priority:", ticket["priority"])
            print("Status:", ticket["status"])
            return

    print("\nTicket not found.")

def update_ticket():
    update_id = int(input("Enter ticket ID to update: "))

    for ticket in tickets:
        if ticket["id"] == update_id:

            print("\n====== UPDATE TICKET ======")
            print("1. Title")
            print("2. Description")
            print("3. Category")
            print("4. Priority")
            print("5. Status")

            choice = input("What do you want to update? ")

            if choice == "1":
                ticket["title"] = input("Enter new title: ")

            elif choice == "2":
                ticket["description"] = input("Enter new description: ")

            elif choice == "3":
                ticket["category"] = input("Enter new category: ")

            elif choice == "4":
                ticket["priority"] = input("Enter new priority: ")

            elif choice == "5":
                ticket["status"] = input("Enter new status: ")

            else:
                print("Invalid choice.")
                return

            print("\nTicket updated successfully!")
            return

    print("\nTicket not found.")

def delete_ticket():
    delete_id = int(input("Enter ticket ID to delete: "))

    for ticket in tickets:
        if ticket["id"] == delete_id:
            print("\nTicket found.")
            print("Title:", ticket["title"])
            print("Status:", ticket["status"])

            confirmation = input("Are you sure you want to delete this ticket? (yes/no): ")

            if confirmation.lower() == "yes":
                tickets.remove(ticket)
                print("\nTicket deleted successfully!")
            else:
                print("\nTicket was not deleted.")

            return

    print("\nTicket not found.")


# ==============================
# MAIN MENU
# ==============================

def show_menu():
    print("\n========================================")
    print("          IT HELP DESK SYSTEM")
    print("========================================")
    print("1. Create Ticket")
    print("2. View All Tickets")
    print("3. Search Ticket")
    print("4. Update Ticket")
    print("5. Delete Ticket")
    print("6. Exit")


# ==============================
# MAIN PROGRAM
# ==============================
load_tickets()
while True:
    show_menu()

    choice = input("Enter your choice: ")

    if choice == "1":
        create_ticket()

    elif choice == "2":
        view_tickets()

    elif choice == "3":
        search_ticket()

    elif choice == "4":
        update_ticket()

    elif choice == "5":
        delete_ticket()

    elif choice == "6":
        print("\nThank you for using IT Help Desk System.")
        break

    else:
        print("\nInvalid choice. Please try again.")