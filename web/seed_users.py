from database import get_db_connection
from werkzeug.security import generate_password_hash


users = [
    ("pratiksha", "1234", "user"),
    ("support", "5678", "support"),
    ("kanchan", "5534", "admin")
]

connection = get_db_connection()
cursor = connection.cursor()

for username, password, role in users:
    password_hash = generate_password_hash(password)

    cursor.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, %s)
        """,
        (username, password_hash, role)
    )

connection.commit()

cursor.close()
connection.close()

print("Users created.")