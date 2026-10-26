import json
from database import get_db_connection


def load_tickets():
    with open("../tickets.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_user_id(cursor, username):
    cursor.execute(
        "SELECT id FROM users WHERE username = %s",
        (username,)
    )

    result = cursor.fetchone()

    if not result:
        raise ValueError(f"User '{username}' not found in PostgreSQL.")

    return result[0]


tickets = load_tickets()

connection = get_db_connection()
cursor = connection.cursor()

default_creator = "pratiksha"

try:
    for ticket in tickets:
        ticket_id = ticket["id"]

        created_by_username = ticket.get("created_by")

        if not created_by_username or created_by_username == "web_user":
            created_by_username = default_creator

        created_by = get_user_id(
            cursor,
            created_by_username
        )

        assigned_to = get_user_id(
            cursor,
            ticket["assigned_to"]
        ) if ticket.get("assigned_to") else None

        cursor.execute(
            """
            INSERT INTO tickets (
                id,
                title,
                description,
                category,
                priority,
                status,
                created_by,
                assigned_to
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ticket["id"],
                ticket["title"],
                ticket["description"],
                ticket["category"],
                ticket["priority"],
                ticket["status"],
                created_by,
                assigned_to
            )
        )

        for remark in ticket.get("remarks", []):
            remark_created_by = get_user_id(
                cursor,
                remark["created_by"]
            )

            cursor.execute(
                """
                INSERT INTO remarks (
                    ticket_id,
                    created_by,
                    remark,
                    created_at
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    remark_created_by,
                    remark["text"],
                    remark["created_at"]
                )
            )

        print(f"Ticket {ticket_id} migrated successfully.")

    cursor.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('tickets', 'id'),
            COALESCE((SELECT MAX(id) FROM tickets), 1)
        )
        """
    )

    connection.commit()

    print("\nMigration completed successfully.")

except Exception as error:
    connection.rollback()
    print("\nMigration failed.")
    print("Error:", error)

finally:
    cursor.close()
    connection.close()