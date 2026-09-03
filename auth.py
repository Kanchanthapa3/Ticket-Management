from colors import RED, GREEN, RESET
users =[
    {
        "username": "pratiksha",
        "password": "1234",
        "role":"user"
    },
    {
        "username": "support",
        "password": "5678",
        "role": "support"

    },
    {
        "username": "kanchan",
        "password": "5534",
        "role": "admin"
    }
]

def login():
    username = input("Username: ")
    password = input("Password: ")

    for user in users:
        if user["username"] == username and user["password"] == password:
            print(GREEN + "\n Login Successful !" + RESET)
            print("Welcome, ", username)

            return user 
    print(RED + "\n Invalid username or password." + RESET)
    return None