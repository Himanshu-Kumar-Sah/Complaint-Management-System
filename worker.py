import mysql.connector
import config
from datetime import datetime
from db_setup import create_tables  
from tabulate import tabulate
import hashlib
data = None

def worker_login():
    if not data:
        print("No database connection available.")
        return None

    worker_phone_no = input("Enter Worker Phone No.: ").strip()
    worker_password = input("Enter Worker Password: ").strip()

    if not worker_phone_no or not worker_password:
        print("Both phone number and password are required.")
        return None

    hashed_password = hashlib.sha256(worker_password.encode()).hexdigest()


    try:
        my_cursor = data.cursor()
        query = """
            SELECT worker_phone_no
            FROM workers_details
            WHERE worker_phone_no = %s AND worker_password = %s;
        """
        my_cursor.execute(query, (worker_phone_no, hashed_password))
        result = my_cursor.fetchone()
        my_cursor.close()

        if result:
            print(f"Welcome, worker {worker_phone_no}!")
            return worker_phone_no
        else:
            print("Incorrect phone number or password.")
            return None

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None


def view_assigned_complaints(worker_phone_no):
    if not data:
        print("Database not connected.")
        return

    my_cursor = data.cursor()
    query = """
        SELECT complaint_id, user_phone_no, complaint_type, complaint_desc, 
               complaint_priority, complaint_scope, location 
        FROM user_complaints_details 
        WHERE worker_phone_no = %s
    """
    my_cursor.execute(query, (worker_phone_no,))
    complaints = my_cursor.fetchall()

    if not complaints:
        print("No complaints assigned.")
        my_cursor.close()
        return

    print("\n--- Assigned Complaints ---\n")
    for complaint in complaints:
        complaint_id, phone_no, type_, desc, priority, scope, location = complaint
        print(f"Complaint ID   : {complaint_id}")
        print(f"Phone Number   : {phone_no}")
        print(f"Type           : {type_}")
        print(f"Description    : {desc}")
        print(f"Priority       : {priority}")
        print(f"Scope          : {scope}")

        if scope == 'Community':
            print(f"Location       : {location if location else 'N/A'}")
        elif scope == 'Personal':
            addr_query = """
                SELECT user_house_no, user_tower_no, user_floor_no, 
                       user_locality, user_area, user_city, user_state, user_pincode
                FROM user_address_details
                WHERE user_phone_no = %s
            """
            my_cursor.execute(addr_query, (phone_no,))
            addr = my_cursor.fetchone()
            if addr:
                house_no, tower, floor, locality, area, city, state, pincode = addr
                print(f"Address        : House {house_no}, Tower {tower}, Floor {floor},")
                print(f"                 {locality}, {area}, {city}, {state} - {pincode}")
            else:
                print("Address        : [Not Available]")

        print("-" * 40)

    my_cursor.close()



def update_assigned_complaint_status(worker_phone_no):
    if not data:
        print("Database not connected.")
        return

    my_cursor = data.cursor()

    try:
        my_cursor.execute("""
            SELECT complaint_id, complaint_type, complaint_scope 
            FROM user_complaints_details 
            WHERE worker_phone_no = %s
        """, (worker_phone_no,))
        complaints = my_cursor.fetchall()

        if not complaints:
            print("No assigned complaints available.")
            return

        print("\n--- Assigned Complaints ---\n")
        print(tabulate(complaints, headers=["ID", "Type", "Scope"], tablefmt="fancy_grid"))

        complaint_id = input("Enter Complaint ID to update: ").strip()
        if not complaint_id.isdigit():
            print("Invalid Complaint ID.")
            return
        complaint_id = int(complaint_id)

        my_cursor.execute("""
            SELECT complaint_id, status 
            FROM user_complaints_details 
            WHERE complaint_id = %s AND worker_phone_no = %s
        """, (complaint_id, worker_phone_no))
        result = my_cursor.fetchone()

        if not result:
            print("Invalid Complaint ID or not assigned to you.")
            return

        current_status = result[1]
        print(f"Current Status of Complaint {complaint_id}: {current_status}")

        new_status = input("Enter new status [Pending/In Progress/Resolved]: ").strip().title()
        if new_status not in ['Pending', 'In Progress', 'Resolved']:
            print("Invalid status. Must be one of: Pending, In Progress, Resolved.")
            return

        update_query = "UPDATE user_complaints_details SET status = %s WHERE complaint_id = %s"
        my_cursor.execute(update_query, (new_status, complaint_id))
        data.commit()
        print(f"Complaint ID {complaint_id} status updated to '{new_status}'.")

    except mysql.connector.Error as err:
        print("Database error:", err)

    finally:
        my_cursor.close()


def worker_dashboard(worker_phone_no):
    while True:
        print(f"\n--- Worker Dashboard ({worker_phone_no}) ---")
        print("1. View Assigned Complaints")
        print("2. Update Complaint Status")
        print("3. Logout")

        choice = input("Choose an option (1-3): ").strip()

        if choice == '1':
            view_assigned_complaints(worker_phone_no)
        elif choice == '2':
            update_assigned_complaint_status(worker_phone_no)
        elif choice == '3':
            print("Logging out...\n")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")
