# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkcalendar import DateEntry
# from mysql_connection import Database
# from datetime import datetime


# class ColorEntryForm(tk.Toplevel):
#     def __init__(self, master):
#         super().__init__(master)
#         self.title("Color Entry")
#         self.geometry("450x350")
#         self.resizable(False, False)
#         self.style = ttk.Style(self)
#         self.style.theme_use("clam")
#         self.configure_gui()
#         self.create_widgets()
#         self.connect_database()

#     def configure_gui(self):
#         self.columnconfigure(0, weight=1)
#         self.style.configure("TLabel", padding=5)
#         self.style.configure("TEntry", padding=5)
#         self.style.configure("TButton", padding=5)
#         self.style.configure("TNotebook.Tab", padding=[10, 5])

#     def connect_database(self):
#         self.db = Database('localhost', 'minkhanttun', '29112000', 'mkt')
#         if self.db.connect():
#             self.conn = self.db.connection
#             self.cursor = self.conn.cursor()
#             self.cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS ColorTable (
#                     ColorID VARCHAR(255) PRIMARY KEY,
#                     BaseColor VARCHAR(255) NOT NULL,
#                     Stock INT NOT NULL,
#                     Date VARCHAR(20) NOT NULL
#                 )
#             ''')
#             self.conn.commit()
#         else:
#             messagebox.showerror("Database Error", "Connection failed.")

#     def create_widgets(self):
#         notebook = ttk.Notebook(self)
#         notebook.pack(expand=True, fill="both", padx=10, pady=10)

#         self.insert_tab = ttk.Frame(notebook)
#         self.edit_tab = ttk.Frame(notebook)
#         notebook.add(self.insert_tab, text="Insert")
#         notebook.add(self.edit_tab, text="Edit")

#         self.create_insert_widgets()
#         self.create_edit_widgets()

#     def create_insert_widgets(self):
#         fields = [("Base Color:", "base_color_entry"),
#                   ("Stock:", "stock_entry"),
#                   ("Date:", "date_entry")]
#         for i, (label_text, attr_name) in enumerate(fields):
#             ttk.Label(self.insert_tab, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)
#             if "date" in attr_name:
#                 widget = DateEntry(self.insert_tab, date_pattern="yyyy-mm-dd")
#             else:
#                 widget = ttk.Entry(self.insert_tab)
#             widget.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
#             setattr(self, attr_name, widget)

#         self.stock_entry.insert(0, "0")
#         self.insert_tab.columnconfigure(1, weight=1)

#         ttk.Button(self.insert_tab, text="Insert", command=self.submit_data).grid(
#             row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

#     def create_edit_widgets(self):
#         fields = [("Color ID:", "edit_color_id_entry"),
#                   ("Base Color:", "edit_base_color_entry"),
#                   ("Stock:", "edit_stock_entry"),
#                   ("Date:", "edit_date_entry")]

#         for i, (label_text, attr_name) in enumerate(fields):
#             ttk.Label(self.edit_tab, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)
#             if "date" in attr_name:
#                 widget = DateEntry(self.edit_tab, date_pattern="yyyy-mm-dd")
#             else:
#                 widget = ttk.Entry(self.edit_tab)
#             widget.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
#             setattr(self, attr_name, widget)

#         self.edit_tab.columnconfigure(1, weight=1)

#         button_frame = ttk.Frame(self.edit_tab)
#         button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

#         ttk.Button(button_frame, text="Load", command=self.load_data).pack(side="left", expand=True, fill="x", padx=5)
#         ttk.Button(button_frame, text="Update", command=self.update_data).pack(side="left", expand=True, fill="x", padx=5)
#         ttk.Button(button_frame, text="Remove", command=self.remove_data).pack(side="left", expand=True, fill="x", padx=5)

#     def get_next_color_id(self):
#         self.cursor.execute("SELECT MAX(ColorID) FROM ColorTable")
#         result = self.cursor.fetchone()
#         if result[0] is None:
#             return "C000"
#         return f"C{int(result[0][1:]) + 1:03}"

#     def format_date(self, date_text):
#         try:
#             return datetime.strptime(date_text, '%Y-%m-%d').strftime('%d %B %Y')
#         except ValueError:
#             messagebox.showerror("Invalid Date", "Date formatting error.")
#             return None

#     def submit_data(self):
#         base_color = self.base_color_entry.get()
#         stock = self.stock_entry.get()
#         date = self.date_entry.get_date().strftime('%Y-%m-%d')
#         formatted_date = self.format_date(date)

#         if not base_color or not stock or not formatted_date:
#             messagebox.showerror("Error", "All fields must be filled.")
#             return

#         try:
#             stock = int(stock)
#             color_id = self.get_next_color_id()
#             self.cursor.execute(
#                 "INSERT INTO ColorTable (ColorID, BaseColor, Stock, Date) VALUES (%s, %s, %s, %s)",
#                 (color_id, base_color, stock, formatted_date)
#             )
#             self.conn.commit()
#             messagebox.showinfo("Inserted", f"Color added with ID: {color_id}")
#             self.clear_insert_fields()
#         except Exception as e:
#             messagebox.showerror("Database Error", str(e))

#     def load_data(self):
#         color_id = self.edit_color_id_entry.get()
#         if not color_id:
#             messagebox.showerror("Error", "Enter a Color ID.")
#             return

#         try:
#             self.cursor.execute("SELECT * FROM ColorTable WHERE ColorID = %s", (color_id,))
#             record = self.cursor.fetchone()
#             if record:
#                 _, base_color, stock, date = record
#                 self.edit_base_color_entry.delete(0, tk.END)
#                 self.edit_base_color_entry.insert(0, base_color)
#                 self.edit_stock_entry.delete(0, tk.END)
#                 self.edit_stock_entry.insert(0, stock)
#                 self.edit_date_entry.set_date(datetime.strptime(date, '%d %B %Y'))
#             else:
#                 messagebox.showerror("Not Found", f"No record for ID: {color_id}")
#         except Exception as e:
#             messagebox.showerror("Database Error", str(e))

#     def update_data(self):
#         color_id = self.edit_color_id_entry.get()
#         base_color = self.edit_base_color_entry.get()
#         stock = self.edit_stock_entry.get()
#         date = self.edit_date_entry.get_date().strftime('%Y-%m-%d')
#         formatted_date = self.format_date(date)

#         if not all([color_id, base_color, stock, formatted_date]):
#             messagebox.showerror("Error", "All fields must be filled.")
#             return

#         try:
#             stock = int(stock)
#             self.cursor.execute(
#                 "UPDATE ColorTable SET BaseColor = %s, Stock = %s, Date = %s WHERE ColorID = %s",
#                 (base_color, stock, formatted_date, color_id)
#             )
#             self.conn.commit()
#             messagebox.showinfo("Updated", "Color updated successfully.")
#         except Exception as e:
#             messagebox.showerror("Database Error", str(e))

#     def remove_data(self):
#         color_id = self.edit_color_id_entry.get()
#         if not color_id:
#             messagebox.showerror("Error", "Enter a Color ID.")
#             return

#         try:
#             self.cursor.execute("DELETE FROM ColorTable WHERE ColorID = %s", (color_id,))
#             self.conn.commit()
#             messagebox.showinfo("Deleted", "Color removed successfully.")
#             self.clear_edit_fields()
#         except Exception as e:
#             messagebox.showerror("Database Error", str(e))

#     def clear_insert_fields(self):
#         self.base_color_entry.delete(0, tk.END)
#         self.stock_entry.delete(0, tk.END)
#         self.stock_entry.insert(0, "0")
#         self.date_entry.set_date(datetime.today())

#     def clear_edit_fields(self):
#         self.edit_color_id_entry.delete(0, tk.END)
#         self.edit_base_color_entry.delete(0, tk.END)
#         self.edit_stock_entry.delete(0, tk.END)
#         self.edit_date_entry.set_date(datetime.today())


# if __name__ == "__main__":
#     root = tk.Tk()
#     root.withdraw()
#     ColorEntryForm(root).mainloop()


## This is my Code 
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from mysql_connection import Database
from datetime import datetime, date


class ColorEntryForm(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Color Entry")
        self.geometry("450x400")
        self.resizable(False, False)
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure_gui()
        self.create_widgets()
        self.connect_database()

    def configure_gui(self):
        self.columnconfigure(0, weight=1)
        self.style.configure("TLabel", padding=5)
        self.style.configure("TEntry", padding=5)
        self.style.configure("TButton", padding=5)
        self.style.configure("TNotebook.Tab", padding=[10, 5])

    def connect_database(self):
        self.db = Database('localhost', 'minkhanttun', '29112000', 'mkt')
        if self.db.connect():
            self.conn = self.db.connection
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ColorTable (
                    ColorID VARCHAR(255) PRIMARY KEY,
                    BaseColor VARCHAR(255) NOT NULL,
                    PumpNumber INT NOT NULL,
                    Stock INT NOT NULL,
                    Date DATE NOT NULL
                )
            ''')
            self.conn.commit()
        else:
            messagebox.showerror("Database Error", "Connection failed.")

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.insert_tab = ttk.Frame(notebook)
        self.edit_tab = ttk.Frame(notebook)
        notebook.add(self.insert_tab, text="Insert")
        notebook.add(self.edit_tab, text="Edit")

        self.create_insert_widgets()
        self.create_edit_widgets()

    def create_insert_widgets(self):
        fields = [("Base Color:", "base_color_entry"),
                  ("Pump Number:", "pump_number_entry"),
                  ("Stock:", "stock_entry"),
                  ("Date:", "date_entry")]
        for i, (label_text, attr_name) in enumerate(fields):
            ttk.Label(self.insert_tab, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if "date" in attr_name:
                widget = DateEntry(self.insert_tab, date_pattern="yyyy-mm-dd")
            elif "pump_number" in attr_name:
                widget = ttk.Spinbox(self.insert_tab, from_=1, to=9, width=5)
            else:
                widget = ttk.Entry(self.insert_tab)
            widget.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            setattr(self, attr_name, widget)

        self.stock_entry.insert(0, "0")
        self.insert_tab.columnconfigure(1, weight=1)

        ttk.Button(self.insert_tab, text="Insert", command=self.submit_data).grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    def create_edit_widgets(self):
        fields = [("Color ID:", "edit_color_id_entry"),
                  ("Base Color:", "edit_base_color_entry"),
                  ("Pump Number:", "edit_pump_number_entry"),
                  ("Stock:", "edit_stock_entry"),
                  ("Date:", "edit_date_entry")]

        for i, (label_text, attr_name) in enumerate(fields):
            ttk.Label(self.edit_tab, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if "date" in attr_name:
                widget = DateEntry(self.edit_tab, date_pattern="yyyy-mm-dd")
            elif "pump_number" in attr_name:
                widget = ttk.Spinbox(self.edit_tab, from_=1, to=9, width=5)
            else:
                widget = ttk.Entry(self.edit_tab)
            widget.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            setattr(self, attr_name, widget)

        self.edit_tab.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(self.edit_tab)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Button(button_frame, text="Load", command=self.load_data).pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_data).pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_data).pack(side="left", expand=True, fill="x", padx=5)

    def get_next_color_id(self):
        self.cursor.execute("SELECT MAX(ColorID) FROM ColorTable")
        result = self.cursor.fetchone()
        if result[0] is None:
            return "C000"
        return f"C{int(result[0][1:]) + 1:03}"

    def submit_data(self):
        base_color = self.base_color_entry.get()
        pump_number = self.pump_number_entry.get()
        stock = self.stock_entry.get()
        date = self.date_entry.get_date().strftime('%Y-%m-%d')

        if not base_color or not pump_number or not stock or not date:
            messagebox.showerror("Error", "All fields must be filled.")
            return

        try:
            pump_number = int(pump_number)
            stock = int(stock)
            color_id = self.get_next_color_id()
            self.cursor.execute(
                "INSERT INTO ColorTable (ColorID, BaseColor, PumpNumber, Stock, Date) VALUES (%s, %s, %s, %s, %s)",
                (color_id, base_color, pump_number, stock, date)
            )
            self.conn.commit()
            messagebox.showinfo("Inserted", f"Color added with ID: {color_id}")
            self.clear_insert_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def load_data(self):
        color_id = self.edit_color_id_entry.get()
        if not color_id:
            messagebox.showerror("Error", "Enter a Color ID.")
            return

        try:
            self.cursor.execute("SELECT * FROM ColorTable WHERE ColorID = %s", (color_id,))
            record = self.cursor.fetchone()
            if record:
                _, base_color, pump_number, stock, date_value = record
                self.edit_base_color_entry.delete(0, tk.END)
                self.edit_base_color_entry.insert(0, base_color)
                self.edit_pump_number_entry.delete(0, tk.END)
                self.edit_pump_number_entry.insert(0, pump_number)
                self.edit_stock_entry.delete(0, tk.END)
                self.edit_stock_entry.insert(0, stock)
                if isinstance(date_value, str):
                    print("DATE VALUE:", repr(date_value))
                    parsed_date = datetime.strptime(date_value.strip(), '%Y-%m-%d').date()
                elif isinstance(date_value, datetime):
                    parsed_date = date_value.date()
                elif isinstance(date_value, date):
                    parsed_date = date_value
                else:
                    raise ValueError("Unsupported date format")
                self.edit_date_entry.set_date(parsed_date)
            else:
                messagebox.showerror("Not Found", f"No record for ID: {color_id}")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def update_data(self):
        color_id = self.edit_color_id_entry.get()
        base_color = self.edit_base_color_entry.get()
        # pump_number = self.edit_pump_number_entry.get()
        # stock = self.edit_stock_entry.get()
        # date = self.edit_date_entry.get_date().strftime('%Y-%m-%d')
        pump_number = self.edit_pump_number_entry.get()
        stock = self.edit_stock_entry.get()
        date = self.edit_date_entry.get_date().strftime('%Y-%m-%d')


        if not all([color_id, base_color, pump_number, stock, date]):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        try:
            pump_number = int(pump_number)
            stock = int(stock)
            self.cursor.execute(
                "UPDATE ColorTable SET BaseColor = %s, PumpNumber = %s, Stock = %s, Date = %s WHERE ColorID = %s",
                (base_color, pump_number, stock, date, color_id)
            )
            self.conn.commit()
            messagebox.showinfo("Updated", "Color updated successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def remove_data(self):
        color_id = self.edit_color_id_entry.get()
        if not color_id:
            messagebox.showerror("Error", "Enter a Color ID.")
            return

        try:
            self.cursor.execute("DELETE FROM ColorTable WHERE ColorID = %s", (color_id,))
            self.conn.commit()
            messagebox.showinfo("Deleted", "Color removed successfully.")
            self.clear_edit_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def clear_insert_fields(self):
        self.base_color_entry.delete(0, tk.END)
        self.pump_number_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, "0")
        self.date_entry.set_date(datetime.today())

    def clear_edit_fields(self):
        self.edit_color_id_entry.delete(0, tk.END)
        self.edit_base_color_entry.delete(0, tk.END)
        self.edit_pump_number_entry.delete(0, tk.END)
        self.edit_stock_entry.delete(0, tk.END)
        self.edit_date_entry.set_date(datetime.today())


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ColorEntryForm(root).mainloop()
