from Connector import get_connection
DB = get_connection()
cursor = DB.cursor()
print("DB Connected successfully ✅")

cursor.execute("DROP TABLE IF EXISTS payment_split")

payment_split_query = """
Create table payment_split(
payment_id INT PRIMARY KEY AUTO_INCREMENT,
sale_id INT,
payment_date DATE,
amount_paid DECIMAL(12,2),
payment_method VARCHAR(50),
FOREIGN KEY (sale_id)
REFERENCES customer_sales(sale_id)
)
"""
cursor.execute(payment_split_query)
DB.commit()

print("payment_split table created successfully ✅")
import os
import pandas as pd
path = os.path.join(os.path.dirname(__file__), "data", "payment_splits.csv")
df = pd.read_csv(path)

payment_split_insert_query = """
INSERT INTO payment_split(sale_id, payment_date, amount_paid, payment_method)
VALUES (%s, %s, %s, %s)
"""

for _, row in df.iterrows():
    cursor.execute(payment_split_insert_query, (
        row["sale_id"],
        row["payment_date"],
        row["amount_paid"],
        row["payment_method"],
    ))

DB.commit()
print("CSV data inserted successfully ✅")

cursor.execute("DROP TRIGGER IF EXISTS after_split_insert")
payment_split_trigger = """
CREATE Trigger after_split_insert
AFTER INSERT on payment_split
FOR EACH ROW
BEGIN
    update customer_sales
    SET received_amount = (
    SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_split
        WHERE sale_id = NEW.sale_id
    )
    WHERE sale_id = NEW.sale_id;

END;
"""
cursor.execute("DROP TRIGGER IF EXISTS after_split_insert")

cursor.execute(payment_split_trigger)
DB.commit()
print("Payment split trigger created successfully ✅")  

# cursor.execute("""
# SELECT sale_id, gross_sales, received_amount, pending_amount, status
# FROM customer_sales
# """)

# for row in cursor.fetchall():
#     print(row)

# payment_query = """
# INSERT INTO payment_split
# (sale_id, payment_date, amount_paid, payment_method)
# VALUES (%s, %s, %s, %s)
# """

# cursor.execute(
#     payment_query,
#     (1, '2026-08-11', 10000, 'UPI')
# )

DB.commit()

print("Payment inserted ✅")


