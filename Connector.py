import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    DB = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD","Poorni@S21"),
        database=os.getenv("DB_NAME", "Sales_Management"),
    )
    return DB