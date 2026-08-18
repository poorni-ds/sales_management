from Connector import get_connection
DB = get_connection()
print("DB Connected successfully ✅")

cursor = DB.cursor()

Drop_query = """
DROP TABLE IF EXISTS branch
"""
cursor.execute(Drop_query)

branch_query = """ 
create table branch(
branch_id INT PRIMARY KEY AUTO_INCREMENT,
branch_name VARCHAR(100) NOT NULL,
branch_admin_name VARCHAR(100) NOT NULL)
"""
cursor.execute(branch_query)

DB.commit()

insert_query = """
INSERT INTO branch(branch_name, branch_admin_name)
VALUES
    ('Chennai', 'Arun Kumar'),
    ('Bangalore', 'Ravi Shankar'),
    ('Hyderabad', 'Suresh Reddy'),
    ('Delhi', 'Neha Sharma'),
    ('Mumbai', 'Rahul Mehta'),
    ('Pune', 'Amit Patil'),
    ('Kolkata', 'Subham Ghosh'),
    ('Ahmedabad', 'Raj Patel')
"""

cursor.execute(insert_query)
DB.commit()

cursor.execute("select *from branch")
rows = cursor.fetchall()
for row in rows:
    print(row)
DB.commit()