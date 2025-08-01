# Functions and logic related to a USER 
import mysql.connector
import config
from datetime import datetime
from db_setup import create_tables  
from tabulate import tabulate
import hashlib
import re
data = None

def registration():
    if not data:
        print("No database connection available.")
        return
    
    user_first_name = input("Enter Your First Name: ").strip()
    user_last_name = input("Enter Your Last Name: ").strip()
    user_email_id = input("Enter Your E-mail ID: ").strip()
    user_phone_no = input("Enter Your Phone Number: ").strip()
    user_gender = input("Enter Your Gender (M/F/O): ").strip().upper()
    user_password = input("Enter Your Password (min 6 chars): ").strip()

    # Input Validations
    if not all([user_first_name, user_email_id, user_phone_no, user_gender, user_password]):
        print("All fields are required.")
        return

    if user_gender not in ['M', 'F', 'O']:
        print("Gender must be M, F, or O.")
        return

    if len(user_password) < 6:
        print("Password must be at least 6 characters long.")
        return

    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email_id):
        print("Invalid email format.")
        return

    # Secure the password using SHA-256 hashing
    hashed_password = hashlib.sha256(user_password.encode()).hexdigest()

    # Proceed with database operations
    if data:
        try:
            my_cursor = data.cursor()
            my_cursor.execute(
                "SELECT * FROM user_registeration_details WHERE user_phone_no = %s",
                (user_phone_no,))
            if my_cursor.fetchone():
                print("User with this phone number already exists.")
                my_cursor.close()
                return

            insert_query = """
                INSERT INTO user_registeration_details 
                (user_first_name, user_last_name, user_email_id, user_phone_no, user_gender, user_password) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            my_cursor.execute(
                insert_query,
                (user_first_name, user_last_name, user_email_id, user_phone_no, user_gender, hashed_password)
            )
            data.commit()
            my_cursor.close()
            print("Registration successful.")

        except mysql.connector.Error as err:
            print("Database error:", err)
    else:
        print("No database connection available.")




def user_login():
    if not data:
        print("No database connection available.")
        return None
    
    user_phone_no = input("Enter Your Phone No.: ").strip()
    user_password = input("Enter Your Password: ").strip()

    if not user_phone_no or not user_password:
        print("Both phone number and password are required.")
        return None

    hashed_password = hashlib.sha256(user_password.encode()).hexdigest()
    
    try:
        my_cursor = data.cursor()
        query = """
            SELECT user_phone_no
            FROM user_registeration_details
            WHERE user_phone_no = %s AND user_password = %s;
        """
        my_cursor.execute(query, (user_phone_no, hashed_password)) 
        result = my_cursor.fetchone()
        my_cursor.close()
        
        if result:
            print(f"Welcome, user {user_phone_no}!")
            return user_phone_no
        else:
            print("Incorrect phone number or password.")
            return None
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None



def add_your_address(user_phone_no):
    if not data:
        print("No database connection available.")
        return
    my_cursor = data.cursor()
    my_cursor.execute("SELECT * FROM user_address_details WHERE user_phone_no = %s", (user_phone_no,))
    if my_cursor.fetchone():
        print("Address already added.")
        my_cursor.close()
        return

    try:
        # Input with validation and cleaning
        house_no = input("Your House No.: ").strip()
        tower = input("Your Tower No.: ").strip()
        floor = input("Your Floor No.: ").strip()
        locality = input("Locality: ").strip()
        area = input("Area: ").strip()
        city = input("City: ").strip()
        state = input("State: ").strip()
        pincode = input("Pincode: ").strip()

        # Basic Validation
        if not all([house_no, tower, floor, locality, state, pincode]):
            print("All address fields are required.")
            return
        if not house_no.isdigit() or not floor.isdigit() or not pincode.isdigit():
            print("House No., Floor, and Pincode must be numeric.")
            return

        # Convert numeric values
        house_no = int(house_no)
        floor = int(floor)
        pincode = int(pincode)

        my_cursor = data.cursor()
        insert_query = """
            INSERT INTO user_address_details (
                user_phone_no, user_house_no, user_tower_no, user_floor_no,
                user_locality, user_area, user_city, user_state, user_pincode
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        my_cursor.execute(insert_query, (
            user_phone_no, house_no, tower, floor, locality, area, city, state, pincode
        ))
        data.commit()
        my_cursor.close()
        print("Address added successfully.")

    except ValueError:
        print("Invalid input. Numeric values expected for House No., Floor, and Pincode.")
    except mysql.connector.Error as err:
        print("Database error:", err)



def add_complain(user_phone_no):
    complain = input("Personal [P] or Community [C]: ").strip().upper()
    
    if complain not in ["P", "C"]:
        print("Invalid input. Please enter 'P' for Personal or 'C' for Community.")
        return

    if complain == "P":
        if data:
            my_cursor = data.cursor()
            query = "SELECT user_phone_no FROM user_address_details WHERE user_phone_no = %s"
            my_cursor.execute(query, (user_phone_no,))
            result = my_cursor.fetchone()
            my_cursor.close()
            if not result:
                print("Please add your address before submitting a personal complaint.")
                add_your_address(user_phone_no)
                my_cursor = data.cursor()
                my_cursor.execute(query, (user_phone_no,))
                result = my_cursor.fetchone()
                my_cursor.close()
                if not result:
                    print("Address not added. Complaint aborted.")
                    return

    complain_type = input("Enter Complaint Type (e.g., Plumbing, Electric): ").strip()
    complain_description = input("Enter Complaint Description: ").strip()
    
    complain_priority = input("Priority (Urgent/Normal): ").strip().capitalize()
    if complain_priority not in ["Urgent", "Normal"]:
        print("Invalid priority. Please enter 'Urgent' or 'Normal'.")
        return

    location = input("Enter Location: ").strip() if complain == "C" else None
    complaint_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complain_status = "Pending"

    if data:
        try:
            my_cursor = data.cursor()
            insert_query = """
                INSERT INTO user_complaints_details (
                    user_phone_no, complaint_type, complaint_desc, complaint_priority, complaint_datetime,
                    status, complaint_scope, location, assigned_to
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            my_cursor.execute(insert_query, (
                user_phone_no, complain_type, complain_description, complain_priority, complaint_datetime,
                complain_status, 'Personal' if complain == 'P' else 'Community', location, 'Not Assigned'
            ))
            data.commit()
            my_cursor.close()
            print("Complaint added successfully.")
        except mysql.connector.Error as err:
            print("Database error:", err)
    else:
        print("No database connection available.")


def view_complain(user_phone_no):
    if not data:
        print("No database connection.")
        return

    try:
        my_cursor = data.cursor()
        query = """
            SELECT complaint_id, user_phone_no, complaint_type, complaint_desc, 
                   complaint_priority, complaint_datetime, status, complaint_scope, 
                   location, assigned_to, worker_phone_no
            FROM user_complaints_details
            WHERE user_phone_no = %s
            ORDER BY complaint_datetime DESC
        """
        my_cursor.execute(query, (user_phone_no,))
        results = my_cursor.fetchall()

        if not results:
            print("No complaints found.")
            return

        print("\n--- Your Complaints ---\n")
        for row in results:
            print(f"Complaint ID      : {row[0]}")
            print(f"Phone Number      : {row[1]}")
            print(f"Type              : {row[2]}")
            print(f"Description       : {row[3]}")
            print(f"Priority          : {row[4]}")
            print(f"Date & Time       : {row[5]}")
            print(f"Status            : {row[6]}")
            print(f"Scope             : {row[7]}")
            if row[7] == 'Community':
                print(f"Location          : {row[8] if row[8] else 'N/A'}")
            print(f"Assigned To       : {row[9] if row[9] else 'Not Assigned'}")
            print(f"Worker Phone No.  : {row[10] if row[10] else 'N/A'}")
            print("-" * 50)

    except mysql.connector.Error as err:
        print("Database error while fetching complaints:", err)
    finally:
        my_cursor.close()

def delete_complaint(user_phone_no):
    if not data:
        print("Database not connected.")
        return
    view_complain(user_phone_no)
    complaint_id = input("Enter Complaint ID to delete: ").strip()
    if not complaint_id.isdigit():
        print("Invalid Complaint ID.")
        return
    try:
        my_cursor = data.cursor()
        query = """DELETE FROM user_complaints_details 
                   WHERE complaint_id = %s AND user_phone_no = %s AND status = 'Pending'"""
        my_cursor.execute(query, (int(complaint_id), user_phone_no))
        if my_cursor.rowcount == 0:
            print("Complaint not found or already processed.")
        else:
            data.commit()
            print("Complaint deleted successfully.")
        my_cursor.close()
        
    except Exception as e:
        print(" Error:", e)
    finally:
        my_cursor.close()


def give_feedback(user_phone_no):
    if not data:
        print("Database not connected.")
        return

    try:
        my_cursor = data.cursor()
        query = """
            SELECT complaint_id, complaint_desc, complaint_datetime, complaint_priority
            FROM user_complaints_details
            WHERE user_phone_no = %s AND status = 'Resolved' AND feedback_rating IS NULL
        """
        my_cursor.execute(query, (user_phone_no,))
        results = my_cursor.fetchall()

        if not results:
            print("No resolved complaints available for feedback.")
            return

        print("\n--- Resolved Complaints Pending Feedback ---\n")
        for row in results:
            print(f"Complaint ID      : {row[0]}")
            print(f"Description       : {row[1]}")
            print(f"Resolved On       : {row[2]}")
            print(f"Priority          : {row[3]}")
            print("-" * 40)

        complaint_id = input("Enter Complaint ID for feedback: ").strip()
        if not complaint_id.isdigit():
            print("Invalid Complaint ID.")
            return
        complaint_id = int(complaint_id)

        feedback_rating = input("Enter the Feedback Rating (1-5): ").strip()
        if not feedback_rating.isdigit() or int(feedback_rating) not in [1, 2, 3, 4, 5]:
            print("Invalid rating. Please enter a number between 1 and 5.")
            return
        feedback_rating = int(feedback_rating)

        feedback_text = input("Enter feedback on your complaint: ").strip()

        update_query = """
            UPDATE user_complaints_details
            SET feedback_rating = %s, feedback_text = %s
            WHERE complaint_id = %s AND user_phone_no = %s
        """
        my_cursor.execute(update_query, (feedback_rating, feedback_text, complaint_id, user_phone_no))
        data.commit()
        print("Thank you for your feedback.")

    except mysql.connector.Error as err:
        print("Database error:", err)
    finally:
        my_cursor.close()

def user_dashboard(user_phone_no):
    while True:
        print(f"\n--- User Dashboard ({user_phone_no}) ---")
        print("1. Add Address")
        print("2. Add Complaint")
        print("3. View Complaint Status")
        print("4. Delete Complaint")
        print("5. Give Feedback")
        print("6. Logout")

        choice = input("Choose an option (1-6): ").strip()

        if choice == '1':
            add_your_address(user_phone_no)
        elif choice == '2':
            add_complain(user_phone_no)
        elif choice == '3':
            view_complain(user_phone_no)
        elif choice == '4':
            delete_complaint(user_phone_no)
        elif choice == '5':
            give_feedback(user_phone_no)
        elif choice == '6':
            print("Logging out...\n")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")