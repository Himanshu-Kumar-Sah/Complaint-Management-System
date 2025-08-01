# Complaint Management System 🛠️

A terminal-based Complaint Management System built with Python and MySQL, allowing Users to register and submit complaints, Admins to assign and manage them, and Workers to resolve and update complaint statuses.

## 🔧 Features

- 👥 User registration and login
- 📝 Complaint submission (Personal/Community)
- 👮 Admin dashboard to:
  - View/filter complaints
  - Assign complaints to workers
  - Manage worker accounts
- 👷 Worker dashboard to view & update assigned complaints
- 🗳️ Feedback system after complaint resolution

## 🗃️ Tech Stack

- Python 3
- MySQL
- Tabulate (for CLI tables)

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Himanshu-Kumar-Sah/Complaint-Management-System.git
   cd Complaint-Management-System

2. Create your own config.py file.
config.py Example:

import hashlib
DB_HOST = "localhost"
DB_USER = "your_mysql_username"
DB_PASS = "your_mysql_password"
DB_NAME = "your_user_database"


Admin1_username = "admin_username"
Admin1_password = "password"
hashed_password = hashlib.sha256(Admin1_password.encode()).hexdigest()

3. Run the main script

   python CMS_Main.py
