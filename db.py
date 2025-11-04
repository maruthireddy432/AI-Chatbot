import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")  
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))    
MYSQL_USER = os.getenv("MYSQL_USER")               
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")       
MYSQL_DB = os.getenv("MYSQL_DB")

def get_connection():
    """Create and return a MySQL database connection using TCP/IP"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset='utf8mb4'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Test connection
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        conn.close()
