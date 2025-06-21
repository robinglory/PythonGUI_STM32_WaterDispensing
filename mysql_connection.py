import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host, user, password, database):
        """Initialize database connection parameters."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Successfully connected to the database.")
                return True
        except Error as e:
            print("Error while connecting to MySQL:", e)
            return False

    def disconnect(self):
        """Close the connection to the MySQL database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def is_connected(self):
        """Check if the connection is still active."""
        return self.connection is not None and self.connection.is_connected()



