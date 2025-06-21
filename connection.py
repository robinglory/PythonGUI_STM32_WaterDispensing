import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',      # Change if your MySQL server is on a different host
        user='minkhanttun',           # Your MySQL username
        password='your_password',   # Your MySQL password
        database='mkt' # Your database name
    )

    if connection.is_connected():
        print("Connected to MySQL database")

except mysql.connector.Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
