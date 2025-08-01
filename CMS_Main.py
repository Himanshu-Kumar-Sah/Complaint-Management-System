import mysql.connector
import hashlib
from user import registration, user_login, user_dashboard, data as user_data
from admin import admin_login, admin_dashboard, data as admin_data
from worker import worker_login, worker_dashboard, data as worker_data
from db_setup import connection, create_tables
import config


def main_menu():
    while True:
        print("\n--- Welcome to Complaint Management System ---")
        print("1. Register as User")
        print("2. Login as User")
        print("3. Login as Admin")
        print("4. Login as Worker")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()
        if choice == '1':
            registration()
        elif choice == '2':
            phone_no = user_login()
            if phone_no:
                user_dashboard(phone_no)
        elif choice == '3':
            admin_username = admin_login()
            if admin_username:
                admin_dashboard(admin_username)
        elif choice == '4':
            worker_phone_no = worker_login()
            if worker_phone_no:
                worker_dashboard(worker_phone_no)
        elif choice == '5':
            print("Exiting. Thank you!")
            break
        else:
            print("Invalid input. Try again.")


def main():
    db = connection()
    if db:
        # Inject the same DB object into all modules
        import user, admin, worker
        user.data = db
        admin.data = db
        worker.data = db

        create_tables(db)
        main_menu()
    else:
        print("Unable to start the system without DB connection.")

if __name__ == "__main__":
    main()
