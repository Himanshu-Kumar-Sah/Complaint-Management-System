# Functions and logic related to a Admin 
import mysql.connector
import config
from datetime import datetime
from db_setup import create_tables  
from tabulate import tabulate
import hashlib
data = None

def admin_login():
    if not data:
        print("No database connection available.")
        return None

    admin_username = input("Enter Admin Username: ").strip()
    admin_password = input("Enter Admin Password: ").strip()

    if not admin_username or not admin_password:
        print("Both username and password are required.")
        return None
    
    hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()


    try:
        my_cursor = data.cursor()
        query = """
            SELECT admin_username 
            FROM admin_details 
            WHERE admin_username = %s AND admin_password = %s
        """
        my_cursor.execute(query, (admin_username, hashed_password)) 
        result = my_cursor.fetchone()
        my_cursor.close()

        if result:
            print(f"Welcome, Admin {admin_username}!")
            return admin_username
        else:
            print("Incorrect admin username or password.")
            return None

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None


def view_all_complaints():
    if not data:
        print("Database not connected.")
        return

    def fetch_and_display(query, values=()):
        try:
            cursor = data.cursor()
            cursor.execute(query, values)
            result = cursor.fetchall()
            cursor.close()

            if result:
                headers = ["Complaint ID", "Phone No.", "Type", "Description", "Priority",
                           "Date & Time", "Status", "Scope", "Location", "Assigned To"]
                print("\n--- Complaints ---\n")
                print(tabulate(result, headers=headers, tablefmt="fancy_grid"))
            else:
                print("No complaints found for the applied filter(s).")

        except mysql.connector.Error as err:
            print("Database error while fetching complaints:", err)

    
    base_query = """
        SELECT complaint_id, user_phone_no, complaint_type, complaint_desc, 
               complaint_priority, complaint_datetime, status, complaint_scope, 
               location, assigned_to  
        FROM user_complaints_details
        ORDER BY complaint_datetime DESC
    """
    fetch_and_display(base_query)

    
    while True:
        print("\nDo you want to apply filters?")
        print("1. Yes")
        print("2. No (Back to Admin Dashboard)")
        choice = input("Choose an option (1-2): ").strip()

        if choice == '1':
            while True:
                print("\n--- Apply Complaint Filters ---")
                print("1. Filter by Priority (Urgent/Normal)")
                print("2. Filter by Status (Pending/In Progress/Resolved)")
                print("3. Filter by Scope (Personal/Community)")
                print("4. Filter by Assigned To (Worker Name or 'Not Assigned')")
                print("5. Clear All Filters")
                print("6. Back to All Complaints View")
                print("7. Exit to Admin Dashboard")

                filter_priority = ""
                filter_status = ""
                filter_scope = ""
                filter_assigned_to = ""

                inner_choice = input("Choose an option (1-7): ").strip()

                if inner_choice == '1':
                    filter_priority = input("Enter Priority (Urgent/Normal): ").strip().capitalize()
                elif inner_choice == '2':
                    filter_status = input("Enter Status (Pending/In Progress/Resolved): ").strip().capitalize()
                elif inner_choice == '3':
                    filter_scope = input("Enter Scope (Personal/Community): ").strip().capitalize()
                elif inner_choice == '4':
                    filter_assigned_to = input("Enter Assigned To (worker or 'Not Assigned'): ").strip()
                elif inner_choice == '5':
                    filter_priority = filter_status = filter_scope = filter_assigned_to = ""
                    print("Filters cleared.")
                    continue
                elif inner_choice == '6':
                    fetch_and_display(base_query)
                    continue
                elif inner_choice == '7':
                    print("Returning to Admin Dashboard...\n")
                    return
                else:
                    print("Invalid option. Try again.")
                    continue

                filters = []
                values = []

                if filter_priority in ['Urgent', 'Normal']:
                    filters.append("complaint_priority = %s")
                    values.append(filter_priority)
                if filter_status in ['Pending', 'In progress', 'Resolved']:
                    filters.append("status = %s")
                    values.append(filter_status)
                if filter_scope in ['Personal', 'Community']:
                    filters.append("complaint_scope = %s")
                    values.append(filter_scope)
                if filter_assigned_to:
                    filters.append("assigned_to = %s")
                    values.append(filter_assigned_to)

                query = base_query
                if filters:
                    query = query.replace("ORDER BY", "WHERE " + " AND ".join(filters) + " ORDER BY")

                fetch_and_display(query, tuple(values))

        elif choice == '2':
            print("Returning to Admin Dashboard...\n")
            break
        else:
            print("Invalid input. Please enter 1 or 2.")



def add_worker():
    if not data:
        print("No database connection available.")
        return

    worker_name = input("Enter Worker Name: ").strip()
    worker_phone_no = input("Enter Worker Phone No.: ").strip()
    worker_password = input("Enter Worker Password (min 6 chars): ").strip()
    specialization = input("Worker Specialization: ").strip()

    if not all([worker_name, worker_phone_no, worker_password, specialization]):
        print("All fields are required.")
        return

    if not worker_phone_no.isdigit() or len(worker_phone_no) != 10:
        print("Invalid phone number. Must be 10 digits.")
        return

    if len(worker_password) < 6:
        print("Password must be at least 6 characters long.")
        return

    hashed_password = hashlib.sha256(worker_password.encode()).hexdigest()

    try:
        my_cursor = data.cursor()

        my_cursor.execute("SELECT * FROM workers_details WHERE worker_phone_no = %s", (worker_phone_no,))
        if my_cursor.fetchone():
            print("Worker with this phone number already exists.")
            my_cursor.close()
            return

        query = """
            INSERT INTO workers_details (worker_name, worker_phone_no, worker_password, specialization)
            VALUES (%s, %s, %s, %s)
        """
        my_cursor.execute(query, (worker_name, worker_phone_no, hashed_password, specialization))
        data.commit()
        my_cursor.close()
        print("Worker added successfully.")

    except mysql.connector.Error as err:
        print("Database error:", err)

def assign_complaint():
    if not data:
        print("Database not connected.")
        return

    try:
        my_cursor = data.cursor()

        my_cursor.execute("""
            SELECT complaint_id, complaint_type, complaint_scope, location 
            FROM user_complaints_details 
            WHERE assigned_to = 'Not Assigned'
        """)
        complaints = my_cursor.fetchall()

        if not complaints:
            print("No unassigned complaints available.")
            return

        print("\n--- Unassigned Complaints ---")
        print(tabulate(complaints, headers=["ID", "Type", "Scope", "Location"], tablefmt="fancy_grid"))

        complaint_id_input = input("Enter Complaint ID to assign: ").strip()
        if not complaint_id_input.isdigit():
            print("Invalid Complaint ID.")
            return
        complaint_id = int(complaint_id_input)

        my_cursor.execute("""
            SELECT complaint_id 
            FROM user_complaints_details 
            WHERE complaint_id = %s AND assigned_to = 'Not Assigned'
        """, (complaint_id,))
        if not my_cursor.fetchone():
            print("Complaint ID is invalid or already assigned.")
            return

        my_cursor.execute("SELECT worker_id, worker_name, specialization FROM workers_details")
        workers = my_cursor.fetchall()

        if not workers:
            print("No workers available in the system.")
            return

        print("\n--- Available Workers ---")
        print(tabulate(workers, headers=["Worker ID", "Name", "Specialization"], tablefmt="fancy_grid"))

        worker_id_input = input("Enter Worker ID to assign this complaint to: ").strip()
        if not worker_id_input.isdigit():
            print("Invalid Worker ID.")
            return
        worker_id = int(worker_id_input)

        my_cursor.execute("SELECT worker_name, worker_phone_no FROM workers_details WHERE worker_id = %s", (worker_id,))
        result = my_cursor.fetchone()

        if not result:
            print("Worker ID does not exist.")
            return

        worker_name, worker_phone_no = result

        update_query = """
            UPDATE user_complaints_details 
            SET assigned_to = %s, worker_phone_no = %s, status = 'In Progress' 
            WHERE complaint_id = %s
        """
        my_cursor.execute(update_query, (worker_name, worker_phone_no, complaint_id))
        data.commit()
        print(f"Complaint ID {complaint_id} assigned to {worker_name}.")

    except mysql.connector.Error as err:
        print("Database error:", err)

    finally:
        my_cursor.close()


def update_complaint_status():
    if not data:
        print("Database not connected.")
        return

    try:
        my_cursor = data.cursor()

        complaint_id_input = input("Enter Complaint ID to update: ").strip()
        if not complaint_id_input.isdigit():
            print("Invalid Complaint ID. It must be a number.")
            return
        complaint_id = int(complaint_id_input)

        my_cursor.execute(
            "SELECT complaint_id, status FROM user_complaints_details WHERE complaint_id = %s",
            (complaint_id,)
        )
        result = my_cursor.fetchone()
        if not result:
            print("Invalid Complaint ID.")
            return

        current_status = result[1]
        print(f"Current status of Complaint ID {complaint_id}: {current_status}")

        new_status = input("Enter new status [Pending / In Progress / Resolved]: ").strip().title()
        valid_statuses = ['Pending', 'In Progress', 'Resolved']

        if new_status not in valid_statuses:
            print("Invalid status. Must be one of:", ", ".join(valid_statuses))
            return

        if current_status == 'Resolved' and new_status != 'Resolved':
            confirm = input("This complaint is already resolved. Do you really want to change it? (y/n): ").strip().lower()
            if confirm != 'y':
                print("No changes made.")
                return

        my_cursor.execute(
            "UPDATE user_complaints_details SET status = %s WHERE complaint_id = %s",
            (new_status, complaint_id)
        )
        data.commit()
        print(f"Complaint ID {complaint_id} status updated to {new_status}.")

    except mysql.connector.Error as err:
        print("Database error:", err)
    finally:
        my_cursor.close()

def delete_worker():
    if not data:
        print("Database not connected.")
        return

    try:
        my_cursor = data.cursor()
        my_cursor.execute("SELECT worker_id, worker_name, specialization FROM workers_details")
        workers = my_cursor.fetchall()

        if not workers:
            print("No workers found in the system.")
            return

        print(tabulate(workers, headers=["Worker ID", "Name", "Specialization"], tablefmt="fancy_grid"))

        worker_id_input = input("Enter Worker ID to delete: ").strip()
        if not worker_id_input.isdigit():
            print("Invalid Worker ID. Must be a number.")
            return
        worker_id = int(worker_id_input)

        my_cursor.execute("SELECT worker_name FROM workers_details WHERE worker_id = %s", (worker_id,))
        result = my_cursor.fetchone()
        if not result:
            print("No such worker found.")
            return

        worker_name = result[0]
        confirm = input(f"Are you sure you want to delete worker '{worker_name}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return

        my_cursor.execute("DELETE FROM workers_details WHERE worker_id = %s", (worker_id,))
        data.commit()
        print(f" Worker '{worker_name}' deleted successfully.")

    except Exception as e:
        print(" Error during deletion:", e)

    finally:
        my_cursor.close()

    

def admin_dashboard(admin_username):
    while True:
        print(f"\n--- Admin Dashboard ({admin_username}) ---")
        print("1. View All Complaints")
        print("2. Assign Complaint to Workers")
        print("3. Update Complaint Status")
        print("4. Add Worker")
        print("5. Delete Worker")
        print("6. Logout")

        choice = input("Choose an option (1-6): ").strip()

        if choice == '1':
            view_all_complaints()
        elif choice == '2':
            assign_complaint()
        elif choice == '3':
            update_complaint_status()
        elif choice == '4':
            add_worker()
        elif choice == '5':
            delete_worker()
        elif choice == '6':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
