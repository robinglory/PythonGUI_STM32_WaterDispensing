import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from mysql_connection import Database
from datetime import datetime, date

class StockEntryForm(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Stock Entry")
        self.create_widgets()

        # Connect to the database
        self.db = Database(host='localhost', user='minkhanttun', password='your_password', database='mkt')
        if self.db.connect():
            print("Database connected successfully.")
        else:
            print("Failed to connect to the database.")

        self.colors = self.fetch_colors()  # Fetch existing colors for the combobox
        self.populate_color_combobox()

    def create_widgets(self):
        # Labels
        self.base_color_label = tk.Label(self, text="Base Color")
        self.base_color_label.grid(row=0, column=0, padx=5, pady=5)

        self.batch_no_label = tk.Label(self, text="Batch No")
        self.batch_no_label.grid(row=1, column=0, padx=5, pady=5)

        self.come_label = tk.Label(self, text="Come")
        self.come_label.grid(row=2, column=0, padx=5, pady=5)

        self.date_label = tk.Label(self, text="Date")
        self.date_label.grid(row=3, column=0, padx=5, pady=5)

        # Entry Fields
        self.base_color_combobox = ttk.Combobox(self, state='readonly')
        self.base_color_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        self.batch_no_entry = tk.Entry(self)
        self.batch_no_entry.grid(row=1, column=1, padx=5, pady=5)

        self.come_entry = tk.Entry(self)
        self.come_entry.grid(row=2, column=1, padx=5, pady=5)

        self.date_entry = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        # New Color Entry
        self.new_color_entry = tk.Entry(self)
        self.new_color_entry.grid(row=0, column=2, padx=5, pady=5)
        self.new_color_entry.grid_remove()  # Hide new color entry initially

        # Buttons
        self.submit_button = ttk.Button(self, text="Submit", command=self.submit_data)
        self.submit_button.grid(row=4, column=0, padx=5, pady=10)

        self.edit_button = ttk.Button(self, text="Edit", command=self.edit_data)
        self.edit_button.grid(row=4, column=1, padx=5, pady=10)

        # Add new color option
        self.new_color_button = ttk.Button(self, text="Add New Color", command=self.toggle_new_color_entry)
        self.new_color_button.grid(row=0, column=3, padx=5, pady=10)

    def fetch_colors(self):
        """Fetch existing colors from the ColorTable."""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT ColorID, BaseColor FROM ColorTable")
            return cursor.fetchall()  # Fetch all colors
        except Exception as e:
            print("Error fetching colors:", e)
            return []

    def populate_color_combobox(self):
        """Populate the combobox with existing colors."""
        color_names = [color[1] for color in self.colors]  # Extract color names
        self.base_color_combobox['values'] = color_names
        if color_names:
            self.base_color_combobox.current(0)  # Select the first item by default

    def toggle_new_color_entry(self):
        """Toggle the visibility of the new color entry and update combobox state."""
        if self.new_color_entry.winfo_ismapped():
            # Hide new color entry and re-enable combobox
            self.new_color_entry.grid_remove()
            self.base_color_combobox.state(['!disabled'])  # Enable color selection
            self.new_color_button.config(text="Add New Color")
        else:
            # Show new color entry and disable combobox
            self.new_color_entry.grid()
            self.base_color_combobox.state(['disabled'])  # Disable color selection
            self.new_color_entry.focus()  # Focus on the new color entry
            self.new_color_button.config(text="Cancel")

    def submit_data(self):
        # Get data from entry fields
        base_color = self.base_color_combobox.get()
        batch_no = self.batch_no_entry.get()
        come = self.come_entry.get()
        date_input = self.date_entry.get()

        # Validation check
        if not (batch_no and come and date_input):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Determine if a new color is being added
        new_color = self.new_color_entry.get().strip()
        if new_color:  # If there is a new color, we will insert it into the database
            color_id = self.add_new_color(new_color)  # Add new color and get its ID
        else:
            # Find ColorID based on BaseColor
            color_id = next((color[0] for color in self.colors if color[1] == base_color), None)

        if color_id is not None:
            # Check stock availability
            if int(come) > 0:  # Ensure that the 'come' entry is a positive integer
                try:
                    cursor = self.db.connection.cursor()
                    formatted_date = self.format_date(date_input)

                    # Update stock for existing color
                    update_stock_query = """UPDATE ColorTable SET Stock = Stock + %s, Date = %s WHERE ColorID = %s"""
                    cursor.execute(update_stock_query, (come, formatted_date, color_id))
                    self.db.connection.commit()

                    # Insert data into StockRecord
                    insert_query = """INSERT INTO StockRecord (ColorID, BatchNumber, Come, Date) 
                                      VALUES (%s, %s, %s, %s)"""
                    cursor.execute(insert_query, (color_id, batch_no, come, formatted_date))
                    self.db.connection.commit()

                    messagebox.showinfo("Success", "Data inserted successfully.")
                    print("Data inserted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to insert data: {e}")
                    print("Failed to insert data:", e)
                finally:
                    cursor.close()
            else:
                messagebox.showerror("Error", "Quantity to come must be greater than zero.")
        else:
            messagebox.showerror("Error", "Selected color does not exist.")

        self.clear_entries()  # Clear entry fields after submission

    def add_new_color(self, new_color):
        """Add a new color to the ColorTable and return its ID."""
        try:
            cursor = self.db.connection.cursor()
            
            # Generate the new ColorID in the required format (C000, C001, etc.)
            color_id = self.generate_color_id()  # Generate a unique ID.

            insert_color_query = """INSERT INTO ColorTable (ColorID, BaseColor, Stock, Date) 
                                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(insert_color_query, (color_id, new_color, 0, self.format_date(date.today().strftime('%Y-%m-%d'))))
            self.db.connection.commit()

            self.colors.append((color_id, new_color))  # Add to local colors list
            self.populate_color_combobox()  # Refresh the combobox
            messagebox.showinfo("Success", "New color added successfully.")
            print("New color added to ColorTable.")
            return color_id  # Return the new color ID
        except Exception as e:
            print("Failed to add new color:", e)
            messagebox.showerror("Error", "Failed to add new color.")
            return None
        finally:
            cursor.close()

    def generate_color_id(self):
        """Generate the next ColorID in the format C000, C001, etc."""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT ColorID FROM ColorTable ORDER BY ColorID DESC LIMIT 1")  # Get the last ColorID
            last_id = cursor.fetchone()

            if last_id is None:  # If there are no records
                return "C000"
            else:
                # Extract the numeric part, increment it, and format back to C000, C001, etc.
                next_id = int(last_id[0][1:]) + 1  # Strip 'C' and increment
                return f"C{next_id:03d}"  # Format as C000, C001, etc.
        except Exception as e:
            print("Error generating ColorID:", e)
            return None
        finally:
            cursor.close()

    def clear_entries(self):
        # Clear entry fields after submission
        self.batch_no_entry.delete(0, tk.END)
        self.come_entry.delete(0, tk.END)
        self.date_entry.set_date(date.today())  # Reset the date entry
        self.new_color_entry.delete(0, tk.END)  # Clear new color entry

    def format_date(self, date_text):
        """Formats the date from 'yyyy-mm-dd' to 'DD Month YYYY'."""
        try:
            date_obj = datetime.strptime(date_text, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d %B %Y')
            return formatted_date
        except ValueError:
            print("Date format error. Please use 'yyyy-mm-dd'.")
            return None

    def edit_data(self):
        # TODO: Implement data editing functionality
        pass

    def on_closing(self):
        """Override the close event to disconnect from the database."""
        self.db.disconnect()  # Disconnect when closing the window
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    app = StockEntryForm(master=root)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)  # Handle closing event
    app.mainloop()


