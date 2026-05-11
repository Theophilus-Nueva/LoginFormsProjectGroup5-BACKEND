import os
import mysql.connector
from dotenv import load_dotenv

# Load Railway environment variables
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the Railway MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=os.getenv("MYSQL_PORT"),
        database=os.getenv("MYSQL_DATABASE")
    )