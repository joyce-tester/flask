import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

# Configure your database connection
DB_CONFIG = {
    "host": "joycelin53.mysql.pythonanywhere-services.com",       # Replace with your database host (e.g., 'localhost')
    "user": "joycelin53",       # Replace with your database username
    "password": "Dbaccess",  # Replace with your database password
    "database": "joycelin53$default"  # Replace with your database name
}

def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # Converts date to ISO 8601 format
    raise TypeError(f"Type {type(obj)} not serializable")

def get_db_connection():
    """
    Establishes a connection to the database.

    Returns:
        connection: A MySQL database connection object.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to database: {e}")
        return None

# Function to insert a record into the attendance table
def add_to_db(member_id, attendance_date):
    """
    Inserts a record into the attendance table.

    Args:
        member_id (str): The ID of the member.
        attendance_date (str): The date of attendance (format: YYYY-MM-DD).
    """
    connection = None
    try:
        # Get the database connection
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Insert record into the attendance table
            query = "INSERT INTO attendance (Member_id, attendance_date) VALUES (%s, %s)"
            cursor.execute(query, (member_id, attendance_date))

            # Commit the transaction
            connection.commit()
            print("Record inserted successfully!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
def read_table(sql):
    """
    Reads data from the database based on the provided SQL query.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        list: A list of tuples containing the query results.
    """
    connection = None
    try:
        # Get the database connection
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Execute the provided SQL query
            cursor.execute(sql)

            # Fetch all rows from the executed query
            results = cursor.fetchall()
            return results

    except Error as e:
        print(f"Error: {e}")
        return []

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
if __name__ == "__main__":
    read_table("select * from attendance")
