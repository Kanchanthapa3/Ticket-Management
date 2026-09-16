
from auth import login

from tickets import (
    load_tickets,
    create_ticket,
    view_tickets,
    view_assigned_tickets,
    search_ticket,
    update_ticket,
    delete_ticket,
    assign_ticket
)


# ==============================
# COLORS
# ==============================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


# ==============================
# ROLE MENU
# ==============================

def show_role_menu(current_user):

    role = current_user["role"]

    # ==========================
    # USER MENU
    # ==========================

    if role == "user":

        while True:

            print("\n====== USER MENU ======")
            print("1. Create Ticket")
            print("2. View My Tickets")
            print("3. Search My Ticket")
            print("4. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                create_ticket(current_user)

            elif choice == "2":
                view_tickets(current_user)

            elif choice == "3":
                search_ticket(current_user)

            elif choice == "4":
                print("\nLogging out....")
                break

            else:
                print("Invalid choice, Please try again.")


    # ==========================
    # SUPPORT MENU
    # ==========================

    elif role == "support":

        while True:

            print("\n====== IT SUPPORT MENU ======")
            print("1. View All Tickets")
            print("2. My assigned Tickets")
            print("3. Search Ticket")
            print("4. Assign Ticket")
            print("5. Update Ticket")
            print("6. Delete Ticket")
            print("7. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                view_tickets()

            if choice == "2":
                view_assigned_tickets(current_user)

            elif choice == "3":
                search_ticket()

            elif choice == "4":
                assign_ticket()

            elif choice == "5":
                update_ticket(current_user)

            elif choice == "6":
                delete_ticket(current_user)

            elif choice == "7":
                print("\nLogging out....")
                break

            else:
                print("Invalid choice, Please try again.")


    # ==========================
    # ADMIN MENU
    # ==========================

    elif role == "admin":

        while True:

            print("\n====== ADMIN MENU ======")
            print("1. Create Ticket")
            print("2. View All Tickets")
            print("3. Search Ticket")
            print("4. Update Ticket")
            print("5. Delete Ticket")
            print("6. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                create_ticket(current_user)

            elif choice == "2":
                view_tickets()

            elif choice == "3":
                search_ticket()

            elif choice == "4":
                update_ticket(current_user)

            elif choice == "5":
                delete_ticket(current_user)

            elif choice == "6":
                print("\nLogging out....")
                break

            else:
                print("Invalid choice, Please try again.")


# ==============================
# MAIN PROGRAM
# ==============================

load_tickets()

current_user = login()

if current_user:
    print("\nWelcome,", current_user["username"])
    print("Role:", current_user["role"])

    show_role_menu(current_user)

