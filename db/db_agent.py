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
    """Custom serializer for datetime and date objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # Converts date to ISO 8601 format
    raise TypeError(f"Type {type(obj)} not serializable")

class DBAgent:
    """Class to handle all database interactions."""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def _connect(self):
        """Establishes a connection to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"]
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error while connecting to database: {e}")

    def _close(self):
        """Closes the database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")

    def execute_query(self, query, params=None):
        """
        Executes a query and returns the results.

        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters to pass to the query (optional).

        Returns:
            list: A list of results from the query.
        """
        results = []
        try:
            self._connect()
            if self.connection:
                self.cursor.execute(query, params or ())
                results = self.cursor.fetchall()
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            self._close()
        return results

    def execute_update(self, query, params):
        """
        Executes an update query (INSERT, UPDATE, DELETE).

        Args:
            query (str): The SQL update query to execute.
            params (tuple): The parameters to pass to the query.
        """
        try:
            self._connect()
            if self.connection:
                self.cursor.execute(query, params)
                self.connection.commit()
                print("Transaction committed successfully!")
        except Error as e:
            print(f"Error executing update: {e}")
        finally:
            self._close()

# Usage example
if __name__ == "__main__":
    db_agent = DBAgent()

    # Example of reading data
    result = db_agent.execute_query("SELECT DISTINCT attendance_date FROM attendance")

    # Convert the result into a list of strings (attendance dates)
    attendance_dates = [str(row[0]) for row in result]

    # Print the list of attendance dates
    print(attendance_dates)

