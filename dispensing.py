# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkcalendar import DateEntry
# from datetime import datetime
# from mysql_connection import Database  # Ensure you have a Database class for MySQL connection

# class DispensingForm(tk.Toplevel):
#     def __init__(self, master=None):
#         super().__init__(master)
#         self.title("Dispensing")

#         # Initialize the Database instance
#         self.db = Database(host='localhost', user='nenp', password='password', database='enpdatabase')
#         if self.db.connect():  # Connect to the database
#             print("Database connected successfully.")
#         else:
#             print("Failed to connect to the database.")

#         # Fetch available final colors from BOMHeading table
#         self.final_colors = self.fetch_final_colors()

#         self.create_widgets()

#     def create_widgets(self):
#         # Labels
#         self.final_color_label = tk.Label(self, text="Final Color")
#         self.final_color_label.grid(row=0, column=0, padx=5, pady=5)

#         self.batch_no_label = tk.Label(self, text="Batch No")
#         self.batch_no_label.grid(row=1, column=0, padx=5, pady=5)

#         self.date_label = tk.Label(self, text="Date")
#         self.date_label.grid(row=2, column=0, padx=5, pady=5)

#         self.quantity_label = tk.Label(self, text="Quantity")
#         self.quantity_label.grid(row=3, column=0, padx=5, pady=5)

#         # Combobox for selecting final color (from BOMHeading)
#         self.final_color_combobox = ttk.Combobox(self, values=self.final_colors)
#         self.final_color_combobox.grid(row=0, column=1, padx=5, pady=5)

#         # Entry for batch number
#         self.batch_no_entry = tk.Entry(self)
#         self.batch_no_entry.grid(row=1, column=1, padx=5, pady=5)

#         # DateEntry for date input
#         self.date_entry = DateEntry(self, date_pattern='yyyy-mm-dd')
#         self.date_entry.grid(row=2, column=1, padx=5, pady=5)

#         # Entry for quantity
#         self.quantity_entry = tk.Entry(self)
#         self.quantity_entry.grid(row=3, column=1, padx=5, pady=5)

#         # Buttons
#         self.dispense_button = ttk.Button(self, text="Dispense", command=self.dispense)
#         self.dispense_button.grid(row=4, column=0, padx=5, pady=10)

#         self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
#         self.cancel_button.grid(row=4, column=1, padx=5, pady=10)

#     def fetch_final_colors(self):
#         """Fetch available final colors from BOMHeading table."""
#         try:
#             cursor = self.db.connection.cursor()
#             cursor.execute("SELECT DISTINCT FinalColor FROM BOMHeading")
#             final_colors = [row[0] for row in cursor.fetchall()]  # Get all distinct final colors
#             return final_colors
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to fetch final colors: {e}")
#             return []
#         finally:
#             cursor.close()

#     def fetch_base_color_percentage(self, final_color):
#         """Fetch BaseColor and Percentage from BOMDetail for the selected FinalColor."""
#         try:
#             cursor = self.db.connection.cursor()
#             query = "SELECT BaseColor, Percentage FROM BOMDetail WHERE FinalColor = %s"
#             cursor.execute(query, (final_color,))
#             base_color_details = cursor.fetchall()  # Fetch all BaseColor and Percentage for the final color
#             return base_color_details
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to fetch base color details: {e}")
#             return []
#         finally:
#             cursor.close()

#     def fetch_available_stock(self, base_colors):
#         """Fetch available stock for the given base colors."""
#         stock_availability = {}
#         try:
#             cursor = self.db.connection.cursor()
#             for base_color in base_colors:
#                 query = "SELECT Stock FROM ColorTable WHERE BaseColor = %s"
#                 cursor.execute(query, (base_color,))
#                 stock = cursor.fetchone()
#                 if stock:
#                     stock_availability[base_color] = stock[0]  # Store available stock
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to fetch stock: {e}")
#         finally:
#             cursor.close()
#         return stock_availability

#     def dispense(self):
#         # Get data from entry fields
#         final_color = self.final_color_combobox.get()
#         batch_no = self.batch_no_entry.get()
#         date = self.date_entry.get()
#         quantity = self.quantity_entry.get()

#         # Validation
#         if not (final_color and batch_no and date and quantity):
#             messagebox.showerror("Error", "All fields are required!")
#             return

#         # Format the date using the custom format_date function
#         formatted_date = self.format_date(date)

#         if formatted_date is None:  # If date is invalid, stop the execution
#             return

#         # Fetch BaseColor and Percentage for the selected FinalColor from BOMDetail
#         base_color_details = self.fetch_base_color_percentage(final_color)
#         if not base_color_details:
#             messagebox.showerror("Error", f"No base color data found for {final_color}")
#             return

#         # Calculate total volume to dispense based on percentage
#         total_quantity = float(quantity)  # Convert quantity to float
#         actual_values = []  # To store actual values for each base color

#         # Check stock availability
#         base_colors = [base_color for base_color, _ in base_color_details]
#         stock_availability = self.fetch_available_stock(base_colors)

#         for base_color, percentage in base_color_details:
#             # Convert percentage to float before calculating
#             percentage = float(percentage)  # Ensure percentage is a float
#             # Calculate actual volume based on percentage
#             actual_volume = (total_quantity * percentage) / 100

#             # Check if sufficient stock is available
#             if base_color in stock_availability and stock_availability[base_color] < actual_volume:
#                 messagebox.showerror("Error", f"Insufficient stock for {base_color}. Available: {stock_availability[base_color]}, Required: {actual_volume}")
#                 return

#             actual_values.append((base_color, percentage, actual_volume))  # Store details for later insertion

#         # Insert into DispensingHeading
#         try:
#             cursor = self.db.connection.cursor()
#             heading_query = """INSERT INTO DispensingHeading (FinalColor, BatchNo, Quantity, Date)
#                                VALUES (%s, %s, %s, %s)"""
#             cursor.execute(heading_query, (final_color, batch_no, total_quantity, formatted_date))
#             heading_srno = cursor.lastrowid  # Get the auto-incremented SrNo for the heading entry
#             self.db.connection.commit()

#             # Insert into DispensingDetail
#             detail_query = """INSERT INTO DispensingDetail (FinalColor, BatchNo, BaseColor, Percentage, Actual, Date, DispensingHeadingID)
#                               VALUES (%s, %s, %s, %s, %s, %s, %s)"""

#             for base_color, percentage, actual in actual_values:
#                 cursor.execute(detail_query, (final_color, batch_no, base_color, percentage, actual, formatted_date, heading_srno))

#             self.db.connection.commit()

#             # Deduct stock from ColorTable
#             self.deduct_stock(actual_values)

#             messagebox.showinfo("Success", "Data inserted and stock updated successfully.")
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to insert data: {e}")
#             print("Failed to insert data:", e)
#         finally:
#             cursor.close()

#         self.clear_entries()  # Clear entry fields after submission

#     def deduct_stock(self, actual_values):
#         """Deduct stock from ColorTable based on the actual volumes dispensed."""
#         try:
#             cursor = self.db.connection.cursor()
#             for base_color, _, actual in actual_values:
#                 update_query = "UPDATE ColorTable SET Stock = Stock - %s WHERE BaseColor = %s"
#                 cursor.execute(update_query, (actual, base_color))
#             self.db.connection.commit()  # Commit the stock deduction
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to update stock: {e}")
#         finally:
#             cursor.close()

#     def format_date(self, date_string):
#         """Custom function to format the date into 'DD Month YYYY' format."""
#         try:
#             # Parse the date string assuming the input is 'yyyy-mm-dd'
#             date_object = datetime.strptime(date_string, "%Y-%m-%d")
#             # Format the date as 'DD Month YYYY'
#             formatted_date = date_object.strftime("%d %B %Y")
#             return formatted_date
#         except ValueError:
#             # Handle the case where the date format is not as expected
#             messagebox.showerror("Error", "Invalid date format")
#             return None

#     def clear_entries(self):
#         self.final_color_combobox.set('')  # Clear combobox selection
#         self.batch_no_entry.delete(0, tk.END)
#         self.quantity_entry.delete(0, tk.END)
#         self.date_entry.set_date(datetime.today())

#     def cancel(self):
#         self.destroy()

#     def on_closing(self):
#         self.db.disconnect()
#         self.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.withdraw()  # Hide the main root window
#     app = DispensingForm(root)

#     # Ensure proper disconnection on close
#     app.protocol("WM_DELETE_WINDOW", app.on_closing)
#     app.mainloop()





# old code before Jan6
# import serial
# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkcalendar import DateEntry
# from datetime import datetime
# from mysql_connection import Database  # Ensure you have a Database class for MySQL connection

# class DispensingForm(tk.Toplevel):
#     def __init__(self, master=None):
#         super().__init__(master)
#         self.title("Dispensing")
#         self.arduino_port = "COM3"  # Replace with your Arduino's COM port
#         self.baud_rate = 9600       # Match with Arduino's baud rate
#         self.arduino = None         # Placeholder for serial connection

#         # Initialize the Database instance
#         self.db = Database(host='localhost', user='nenp', password='password', database='enpdatabase')
#         if self.db.connect():  # Connect to the database
#             print("Database connected successfully.")
#         else:
#             print("Failed to connect to the database.")

#         self.initialize_serial()


#         # Fetch available final colors from BOMHeading table
#         self.final_colors = self.fetch_final_colors()

#         self.create_widgets()

#     def initialize_serial(self):
#         """Initialize serial communication with Arduino."""
#         try:
#             self.arduino = serial.Serial(self.arduino_port, self.baud_rate, timeout=2)
#             time.sleep(2)  # Wait for Arduino to reset
#             print("Serial connection established with Arduino.")
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to connect to Arduino: {e}")
#             self.arduino = None

#     def send_to_arduino(self, data):
#         """Send data to Arduino via serial."""
#         try:
#             if self.arduino:
#                 self.arduino.write(data.encode())  # Send data as bytes
#                 time.sleep(0.5)  # Small delay for Arduino to process
#                 response = self.arduino.readline().decode().strip()  # Read Arduino's response
#                 print(f"Arduino response: {response}")
#                 return response
#             else:
#                 messagebox.showerror("Error", "Arduino is not connected.")
#                 return None
#         except Exception as e:
#             messagebox.showerror("Error", f"Error communicating with Arduino: {e}")
#             return None

#     def create_widgets(self):
#         # Labels
#         self.final_color_label = tk.Label(self, text="Final Color")
#         self.final_color_label.grid(row=0, column=0, padx=5, pady=5)

#         self.batch_no_label = tk.Label(self, text="Batch No")
#         self.batch_no_label.grid(row=1, column=0, padx=5, pady=5)

#         self.date_label = tk.Label(self, text="Date")
#         self.date_label.grid(row=2, column=0, padx=5, pady=5)

#         self.quantity_label = tk.Label(self, text="Quantity")
#         self.quantity_label.grid(row=3, column=0, padx=5, pady=5)

#         # Combobox for selecting final color (from BOMHeading)
#         self.final_color_combobox = ttk.Combobox(self, values=self.final_colors)
#         self.final_color_combobox.grid(row=0, column=1, padx=5, pady=5)

#         # Entry for batch number
#         self.batch_no_entry = tk.Entry(self)
#         self.batch_no_entry.grid(row=1, column=1, padx=5, pady=5)

#         # DateEntry for date input
#         self.date_entry = DateEntry(self, date_pattern='yyyy-mm-dd')
#         self.date_entry.grid(row=2, column=1, padx=5, pady=5)

#         # Entry for quantity
#         self.quantity_entry = tk.Entry(self)
#         self.quantity_entry.grid(row=3, column=1, padx=5, pady=5)

#         # Buttons
#         self.dispense_button = ttk.Button(self, text="Dispense", command=self.dispense)
#         self.dispense_button.grid(row=4, column=0, padx=5, pady=10)

#         self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
#         self.cancel_button.grid(row=4, column=1, padx=5, pady=10)

#     def fetch_final_colors(self):
#         """Fetch available final colors from BOMHeading table."""
#         try:
#             cursor = self.db.connection.cursor()
#             cursor.execute("SELECT DISTINCT FinalColor FROM BOMHeading")
#             final_colors = [row[0] for row in cursor.fetchall()]  # Get all distinct final colors
#             return final_colors
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to fetch final colors: {e}")
#             return []
#         finally:
#             cursor.close()

#     def fetch_base_color_percentage(self, final_color):
#         """Fetch BaseColor and Percentage from BOMDetail for the selected FinalColor."""
#         try:
#             cursor = self.db.connection.cursor()
#             query = "SELECT BaseColor, Percentage FROM BOMDetail WHERE FinalColor = %s"
#             cursor.execute(query, (final_color,))
#             base_color_details = cursor.fetchall()  # Fetch all BaseColor and Percentage for the final color
#             return base_color_details
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to fetch base color details: {e}")
#             return []
#         finally:
#             cursor.close()

#     def fetch_available_stock(self, base_colors):
#         """Fetch available stock for the given base colors."""
#         stock_availability = {}
#         try:
#             cursor = self.db.connection.cursor()
#             for base_color in base_colors:
#                 query = "SELECT Stock FROM ColorTable WHERE BaseColor = %s"
#                 cursor.execute(query, (base_color,))
#                 stock = cursor.fetchone()
#                 if stock:
#                     stock_availability[base_color] = stock[0]  # Store available stock
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to fetch stock: {e}")
#         finally:
#             cursor.close()
#         return stock_availability

#     def dispense(self):
#         # Get data from entry fields
#         final_color = self.final_color_combobox.get()
#         batch_no = self.batch_no_entry.get()
#         date = self.date_entry.get()
#         quantity = self.quantity_entry.get()

#         # Validation
#         if not (final_color and batch_no and date and quantity):
#             messagebox.showerror("Error", "All fields are required!")
#             return

#         # Format the date using the custom format_date function
#         formatted_date = self.format_date(date)

#         if formatted_date is None:  # If date is invalid, stop the execution
#             return

#         # Fetch BaseColor and Percentage for the selected FinalColor from BOMDetail
#         base_color_details = self.fetch_base_color_percentage(final_color)
#         if not base_color_details:
#             messagebox.showerror("Error", f"No base color data found for {final_color}")
#             return

#         # Calculate total volume to dispense based on percentage
#         total_quantity = float(quantity)  # Convert quantity to float
#         actual_values = []  # To store actual values for each base color

#         # Check stock availability
#         base_colors = [base_color for base_color, _ in base_color_details]
#         stock_availability = self.fetch_available_stock(base_colors)

#         for base_color, percentage in base_color_details:
#             # Convert percentage to float before calculating
#             percentage = float(percentage)  # Ensure percentage is a float
#             # Calculate actual volume based on percentage
#             actual_volume = (total_quantity * percentage) / 100

#             # Check if sufficient stock is available
#             if base_color in stock_availability and stock_availability[base_color] < actual_volume:
#                 messagebox.showerror("Error", f"Insufficient stock for {base_color}. Available: {stock_availability[base_color]}, Required: {actual_volume}")
#                 return

#             actual_values.append((base_color, percentage, actual_volume))  # Store details for later insertion
#         # Send data to Arduino
#         try:
#             for base_color, percentage, actual_volume in actual_values:
#                 arduino_command = f"{base_color}:{actual_volume}\n"  # Format: BaseColor:Volume
#                 response = self.send_to_arduino(arduino_command)
#                 if response != "OK":  # Expect "OK" as Arduino acknowledgment
#                     messagebox.showerror("Error", f"Arduino failed for {base_color}.")
#                     return
#         except Exception as e:
#             messagebox.showerror("Error", f"Error sending data to Arduino: {e}")
#             return

#         # Insert into DispensingHeading
#         try:
#             cursor = self.db.connection.cursor()
#             heading_query = """INSERT INTO DispensingHeading (FinalColor, BatchNo, Quantity, Date)
#                                VALUES (%s, %s, %s, %s)"""
#             cursor.execute(heading_query, (final_color, batch_no, total_quantity, formatted_date))
#             heading_srno = cursor.lastrowid  # Get the auto-incremented SrNo for the heading entry
#             self.db.connection.commit()

#             # Insert into DispensingDetail
#             detail_query = """INSERT INTO DispensingDetail (FinalColor, BatchNo, BaseColor, Percentage, Actual, Date, DispensingHeadingID)
#                               VALUES (%s, %s, %s, %s, %s, %s, %s)"""

#             for base_color, percentage, actual in actual_values:
#                 cursor.execute(detail_query, (final_color, batch_no, base_color, percentage, actual, formatted_date, heading_srno))

#             self.db.connection.commit()

#             # Deduct stock from ColorTable
#             self.deduct_stock(actual_values)

#             messagebox.showinfo("Success", "Data inserted and stock updated successfully.")
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to insert data: {e}")
#             print("Failed to insert data:", e)
#         finally:
#             cursor.close()

#         self.clear_entries()  # Clear entry fields after submission

#     def deduct_stock(self, actual_values):
#         """Deduct stock from ColorTable based on the actual volumes dispensed."""
#         try:
#             cursor = self.db.connection.cursor()
#             for base_color, _, actual in actual_values:
#                 update_query = "UPDATE ColorTable SET Stock = Stock - %s WHERE BaseColor = %s"
#                 cursor.execute(update_query, (actual, base_color))
#             self.db.connection.commit()  # Commit the stock deduction
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to update stock: {e}")
#         finally:
#             cursor.close()

#     def format_date(self, date_string):
#         """Custom function to format the date into 'DD Month YYYY' format."""
#         try:
#             # Parse the date string assuming the input is 'yyyy-mm-dd'
#             date_object = datetime.strptime(date_string, "%Y-%m-%d")
#             # Format the date as 'DD Month YYYY'
#             formatted_date = date_object.strftime("%d %B %Y")
#             return formatted_date
#         except ValueError:
#             # Handle the case where the date format is not as expected
#             messagebox.showerror("Error", "Invalid date format")
#             return None

#     def clear_entries(self):
#         self.final_color_combobox.set('')  # Clear combobox selection
#         self.batch_no_entry.delete(0, tk.END)
#         self.quantity_entry.delete(0, tk.END)
#         self.date_entry.set_date(datetime.today())

#     def cancel(self):
#         self.destroy()

#     def on_closing(self):
#         self.db.disconnect()
#         self.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.withdraw()  # Hide the main root window
#     app = DispensingForm(root)

#     # Ensure proper disconnection on close
#     app.protocol("WM_DELETE_WINDOW", app.on_closing)
#     app.mainloop()










# version 1 - Jan6 16:47
import serial
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from mysql_connection import Database  # Ensure you have a Database class for MySQL connection
import time

class DispensingForm(tk.Toplevel):
    COMMAND_PREFIX = 'C'  # Command prefix for dispensing

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Dispensing")
        self.arduino_port = "/dev/ttyUSB0"  # Replace with your Arduino's COM port
        self.baud_rate = 9600       # Match with Arduino's baud rate
        self.arduino = None         # Placeholder for serial connection

        # Initialize the Database instance
        self.db = Database(host='localhost', user='minkhanttun', password='your_password', database='mkt')
        if self.db.connect():  # Connect to the database
            print("Database connected successfully.")
        else:
            print("Failed to connect to the database.")

        self.initialize_serial()

        # Fetch available final colors from BOMHeading table
        self.final_colors = self.fetch_final_colors()

        self.create_widgets()

    def initialize_serial(self):
        """Initialize serial communication with Arduino."""
        try:
            self.arduino = serial.Serial(self.arduino_port, self.baud_rate, timeout=2)
            time.sleep(2)  # Wait for Arduino to reset
            print("Serial connection established with Arduino.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Arduino: {e}")
            self.arduino = None

    def send_to_arduino(self, data):
        """Send data to Arduino via serial and wait for acknowledgment."""
        try:
            if self.arduino:
                self.arduino.write(data.encode())  # Send data as bytes
                time.sleep(0.5)  # Small delay for Arduino to process
                response = self.arduino.readline().decode().strip()  # Read Arduino's response
                print(f"Arduino response: {response}")
                return response
            else:
                messagebox.showerror("Error", "Arduino is not connected.")
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Error communicating with Arduino: {e}")
            return None

    def create_widgets(self):
        # Labels
        self.final_color_label = tk.Label(self, text="Final Color")
        self.final_color_label.grid(row=0, column=0, padx=5, pady=5)

        self.batch_no_label = tk.Label(self, text="Batch No")
        self.batch_no_label.grid(row=1, column=0, padx=5, pady=5)

        self.date_label = tk.Label(self, text="Date")
        self.date_label.grid(row=2, column=0, padx=5, pady=5)

        self.quantity_label = tk.Label(self, text="Quantity")
        self.quantity_label.grid(row=3, column=0, padx=5, pady=5)

        # Combobox for selecting final color (from BOMHeading)
        self.final_color_combobox = ttk.Combobox(self, values=self.final_colors)
        self.final_color_combobox.grid(row=0, column=1, padx=5, pady=5)

        # Entry for batch number
        self.batch_no_entry = tk.Entry(self)
        self.batch_no_entry.grid(row=1, column=1, padx=5, pady=5)

        # DateEntry for date input
        self.date_entry = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Entry for quantity
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        self.dispense_button = ttk.Button(self, text="Dispense", command=self.dispense)
        self.dispense_button.grid(row=4, column=0, padx=5, pady=10)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=4, column=1, padx=5, pady=10)

    def fetch_final_colors(self):
        """Fetch available final colors from BOMHeading table."""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT DISTINCT FinalColor FROM BOMHeading")
            final_colors = [row[0] for row in cursor.fetchall()]  # Get all distinct final colors
            return final_colors
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch final colors: {e}")
            return []
        finally:
            cursor.close()

    def fetch_base_color_percentage(self, final_color):
        """Fetch BaseColor and Percentage from BOMDetail for the selected FinalColor."""
        try:
            cursor = self.db.connection.cursor()
            query = "SELECT BaseColor, Percentage FROM BOMDetail WHERE FinalColor = %s"
            cursor.execute(query, (final_color,))
            base_color_details = cursor.fetchall()  # Fetch all BaseColor and Percentage for the final color
            return base_color_details
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch base color details: {e}")
            return []
        finally:
            cursor.close()

    def fetch_available_stock(self, base_colors):
        """Fetch available stock for the given base colors."""
        stock_availability = {}
        try:
            cursor = self.db.connection.cursor()
            for base_color in base_colors:
                query = "SELECT Stock FROM ColorTable WHERE BaseColor = %s"
                cursor.execute(query, (base_color,))
                stock = cursor.fetchone()
                if stock:
                    stock_availability[base_color] = stock[0]  # Store available stock
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch stock: {e}")
        finally:
            cursor.close()
        return stock_availability

    def dispense(self):
        # Get data from entry fields
        final_color = self.final_color_combobox.get()
        batch_no = self.batch_no_entry.get()
        date = self.date_entry.get()
        quantity = self.quantity_entry.get()

        # Validation
        if not (final_color and batch_no and date and quantity):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Format the date using the custom format_date function
        formatted_date = self.format_date(date)

        if formatted_date is None:  # If date is invalid, stop the execution
            return

        # Fetch BaseColor and Percentage for the selected FinalColor from BOMDetail
        base_color_details = self.fetch_base_color_percentage(final_color)
        if not base_color_details:
            messagebox.showerror("Error", f"No base color data found for {final_color}")
            return

        # Calculate total volume to dispense based on percentage
        total_quantity = float(quantity)  # Convert quantity to float
        actual_values = []  # To store actual values for each base color

        # Check stock availability
        base_colors = [base_color for base_color, _ in base_color_details]
        stock_availability = self.fetch_available_stock(base_colors)

        for base_color, percentage in base_color_details:
            # Convert percentage to float before calculating
            percentage = float(percentage)  # Ensure percentage is a float
            # Calculate actual volume based on percentage
            actual_volume = (total_quantity * percentage) / 100

            # Check if sufficient stock is available
            if base_color in stock_availability and stock_availability[base_color] < actual_volume:
                messagebox.showerror("Error", f"Insufficient stock for {base_color}. Available: {stock_availability[base_color]}, Required: {actual_volume}")
                return

            actual_values.append((base_color, percentage, actual_volume))  # Store details for later insertion

        # Send data to Arduino
        try:
            for base_color, percentage, actual_volume in actual_values:
                arduino_command = f"{self.COMMAND_PREFIX}:{base_color}:{actual_volume}\n"  # Format: C:BaseColor:Volume
                response = self.send_to_arduino(arduino_command)
                if response != "OK":  # Expect "OK" as Arduino acknowledgment
                    messagebox.showerror("Error", f"Arduino failed for {base_color}.")
                    return
        except Exception as e:
            messagebox.showerror("Error", f"Error sending data to Arduino: {e}")
            return

        # # Insert into DispensingHeading
        try:
            cursor = self.db.connection.cursor()
            heading_query = """INSERT INTO DispensingHeading (FinalColor, BatchNo, Quantity, Date)
                               VALUES (%s, %s, %s, %s)"""
            cursor.execute(heading_query, (final_color, batch_no, total_quantity, formatted_date))
            heading_srno = cursor.lastrowid  # Get the auto-incremented SrNo for the heading entry
            self.db.connection.commit()

            # Insert into DispensingDetail
            detail_query = """INSERT INTO DispensingDetail (FinalColor, BatchNo, BaseColor, Percentage, Actual, Date, DispensingHeadingID)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            for base_color, percentage, actual in actual_values:
                cursor.execute(detail_query, (final_color, batch_no, base_color, percentage, actual, formatted_date, heading_srno))

            self.db.connection.commit()

            # Deduct stock from ColorTable
            self.deduct_stock(actual_values)

            messagebox.showinfo("Success", "Data inserted and stock updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert data: {e}")
            print("Failed to insert data:", e)
        finally:
            cursor.close()

        self.clear_entries()  # Clear entry fields after submission

    def deduct_stock(self, actual_values):
        """Deduct stock from ColorTable based on the actual volumes dispensed."""
        try:
            cursor = self.db.connection.cursor()
            for base_color, _, actual in actual_values:
                update_query = "UPDATE ColorTable SET Stock = Stock - %s WHERE BaseColor = %s"
                cursor.execute(update_query, (actual, base_color))
            self.db.connection.commit()  # Commit the stock deduction
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {e}")
        finally:
            cursor.close()

    def format_date(self, date_string):
        """Custom function to format the date into 'DD Month YYYY' format."""
        try:
            # Parse the date string assuming the input is 'yyyy-mm-dd'
            date_object = datetime.strptime(date_string, "%Y-%m-%d")
            # Format the date as 'DD Month YYYY'
            formatted_date = date_object.strftime("%d %B %Y")
            return formatted_date
        except ValueError:
            # Handle the case where the date format is not as expected
            messagebox.showerror("Error", "Invalid date format")
            return None

    def clear_entries(self):
        self.final_color_combobox.set('')  # Clear combobox selection
        self.batch_no_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.date_entry.set_date(datetime.today())

    def cancel(self):
        self.destroy()

    def on_closing(self):
        self.db.disconnect()
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main root window
    app = DispensingForm(root)

    # Ensure proper disconnection on close
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

# In your dispensing.py (suggested additions)
# import serial
# from serial.tools import list_ports

# class DispensingForm(tk.Toplevel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("Dispensing Control")
#         self.ser = None
        
#         # Add serial connection controls
#         ttk.Label(self, text="Select COM Port:").pack()
#         self.port_combobox = ttk.Combobox(self, values=self.get_serial_ports())
#         self.port_combobox.pack()
        
#         ttk.Button(self, text="Connect", command=self.connect_serial).pack()
        
#         # Add pump control interface
#         self.create_pump_controls()
    
#     def get_serial_ports(self):
#         return [port.device for port in list_ports.comports()]
    
#     def connect_serial(self):
#         port = self.port_combobox.get()
#         try:
#             self.ser = serial.Serial(port, 9600, timeout=1)
#             self.after(100, self.check_serial)
#         except serial.SerialException as e:
#             messagebox.showerror("Connection Error", str(e))
    
#     def create_pump_controls(self):
#         # Create UI elements for each pump
#         for i in range(1, 10):  # For 9 pumps
#             frame = ttk.Frame(self)
#             ttk.Label(frame, text=f"Pump {i}:").pack(side=tk.LEFT)
#             entry = ttk.Entry(frame, width=5)
#             entry.pack(side=tk.LEFT)
#             ttk.Label(frame, text="mL").pack(side=tk.LEFT)
#             ttk.Button(frame, text="Dispense", 
#                        command=lambda i=i, e=entry: self.dispense(i, e.get())).pack(side=tk.LEFT)
#             frame.pack(pady=2)
    
#     def dispense(self, pump_num, volume):
#         if self.ser and self.ser.is_open:
#             try:
#                 volume = float(volume)
#                 if volume > 0:
#                     self.ser.write(f"D{pump_num}:{volume}\n".encode())
#             except ValueError:
#                 messagebox.showerror("Error", "Please enter a valid volume")
    
#     def check_serial(self):
#         if self.ser and self.ser.in_waiting:
#             response = self.ser.readline().decode().strip()
#             self.display_response(response)
#         self.after(100, self.check_serial)
    
#     def display_response(self, message):
#         # Add to a log or status display
#         pass