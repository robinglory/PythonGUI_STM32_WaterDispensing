import mysql.connector
from mysql.connector import Error

def fetch_all_data(database, user, password, host='localhost'):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='minkhanttun',
            password='29112000',
            database='mkt'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Fetch all table names
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                print(f"Data from table: {table_name}")
                # Fetch all data from the current table
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()

                for row in rows:
                    print(row)
                print()  # New line for better readability

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed")

# Replace with your database credentials
fetch_all_data('enpdatabase', 'nenp', 'password')
