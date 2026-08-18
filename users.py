import os
import pandas as pd
from Connector import get_connection
from security import hash_password

DB = get_connection()
cursor = DB.cursor()
print("DB Connected successfully ✅")

# =========================
# TABLE SETUP
# =========================

user_drop_query = """
DROP TABLE IF EXISTS users
"""
cursor.execute(user_drop_query)

users_query = """
CREATE TABLE users(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    branch_id INT,
    role ENUM('Super Admin', 'Admin'),
    email VARCHAR(255) NOT NULL,
    FOREIGN KEY (branch_id)
    REFERENCES branch(branch_id)
)
"""
cursor.execute(users_query)
print("users table created ✅")

# =========================
# TRIGGERS (created BEFORE data load, so they're enforced from the first insert)
# =========================

drop_insert_trigger = "DROP TRIGGER IF EXISTS before_user_insert"
cursor.execute(drop_insert_trigger)

insert_trigger = """
CREATE TRIGGER before_user_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'Super Admin'
    AND EXISTS (
        SELECT 1
        FROM users
        WHERE role = 'Super Admin'
    )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only one Super Admin is allowed';
    END IF;
END
"""

try:
    cursor.execute(insert_trigger)
    print("INSERT trigger created ✅")
except Exception as e:
    print("INSERT trigger failed ❌")
    print(e)

drop_update_trigger = "DROP TRIGGER IF EXISTS before_user_update"
cursor.execute(drop_update_trigger)

update_trigger = """
CREATE TRIGGER before_user_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'Super Admin'
    AND OLD.role <> 'Super Admin'
    AND EXISTS (
        SELECT 1
        FROM users
        WHERE role = 'Super Admin'
        AND user_id <> OLD.user_id
    )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only one Super Admin is allowed';
    END IF;
END
"""

try:
    cursor.execute(update_trigger)
    print("UPDATE trigger created ✅")
except Exception as e:
    print("UPDATE trigger failed ❌")
    print(e)

DB.commit()

# =========================
# DATA LOAD (now protected by the triggers above)
# =========================

path = os.path.join(os.path.dirname(__file__), "data", "users.csv")
path = os.path.abspath(r"c:\Users\poorn\Downloads\users.csv")
df = pd.read_csv(path)

# Optional: normalize role casing/whitespace before insert so the ENUM
# and the trigger's string comparison ('Super Admin') match reliably.
# df["role"] = df["role"].str.strip()

user_insert_query = """
INSERT INTO users
(username, password, branch_id, role, email)
VALUES (%s, %s, %s, %s, %s)
"""

for _, rows in df.iterrows():
    # Handle missing branch_id
    if pd.isna(rows["branch_id"]):
        branch_id = None
    else:
        branch_id = int(rows["branch_id"])

    values = (
        rows["username"],
        hash_password(str(rows["password"])),
        branch_id,
        rows["role"],
        rows["email"]
    )

    cursor.execute(user_insert_query, values)

DB.commit()
print("users data inserted ✅")

cursor.close()
DB.close()

print("Finished ✅")

