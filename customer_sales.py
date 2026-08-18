import os
from Connector import get_connection
import pandas as pd

DB = get_connection()
cursor = DB.cursor()
print("DB Connected successfully ✅")

Drop_query_2 = """
DROP TABLE IF EXISTS customer_sales
"""
cursor.execute(Drop_query_2)

customer_sales_query = """
create table customer_sales(
sale_id INT PRIMARY KEY AUTO_INCREMENT,
branch_id INT,
date DATE DEFAULT (CURRENT_DATE),
name VARCHAR(100) NOT NULL,
mobile_number VARCHAR(15),
product_name VARCHAR(30),
gross_sales DECIMAL(12,2) NOT NULL,
received_amount Decimal(12,2) DEFAULT 0,
pending_amount Decimal(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
status ENUM('Open','Close') DEFAULT 'Open',
FOREIGN KEY(branch_id) REFERENCES branch(branch_id)
)
"""

cursor.execute(customer_sales_query)
print("customer_sales_table created ✅")

cursor.execute("DROP TRIGGER IF EXISTS before_sale_insert")
cursor.execute("DROP TRIGGER IF EXISTS before_sale_update")



# Trigger 1: fires on INSERT (new sale)
insert_trigger_query = """
CREATE TRIGGER before_sale_insert
BEFORE INSERT ON customer_sales
FOR EACH ROW
BEGIN
    IF NEW.gross_sales - NEW.received_amount <= 0 THEN
        SET NEW.status = 'Close';
    ELSE
        SET NEW.status = 'Open';
    END IF;
END
"""
cursor.execute(insert_trigger_query)
print("Insert trigger created ✅")

# Trigger 2: fires on UPDATE (e.g. partial/final payment comes in later)
update_trigger_query = """
CREATE TRIGGER before_sale_update
BEFORE UPDATE ON customer_sales
FOR EACH ROW
BEGIN
    IF NEW.gross_sales - NEW.received_amount <= 0 THEN
        SET NEW.status = 'Close';
    ELSE
        SET NEW.status = 'Open';
    END IF;
END
"""
cursor.execute(update_trigger_query)
print("Update trigger created ✅")

DB.commit()
print("All objects created successfully ✅")

path = os.path.join(os.path.dirname(__file__), "data", "customer_sales.csv")
df = pd.read_csv(path)

for _, row in df.iterrows():
    csv_query = """
    INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        row['branch_id'],
        row['date'],
        row['name'],
        row['mobile_number'],
        row['product_name'],
        row['gross_sales'],
        row['received_amount'],
        row['status']
    )
    cursor.execute(csv_query, values)

DB.commit()
print("CSV data inserted successfully ✅")

cursor.execute("DESCRIBE customer_sales")

for row in cursor.fetchall():
    print(row)

#checking the trigger here:
cursor.execute("SHOW TRIGGERS LIKE 'customer_sales'")
triggers = cursor.fetchall()
for trigger in triggers:
    print(trigger)

#Branch sales analysis


