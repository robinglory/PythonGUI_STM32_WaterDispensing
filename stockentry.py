import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from mysql_connection import Database
from datetime import datetime, date
import pandas as pd
import os

EXPORT_FOLDER = r"C:\Users\ASUS\Documents\MinKhantTun(Project)\PythonGUI\PythonGUI\Stock Entry Log"

class StockEntryForm(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Stock Entry")
        self.configure(bg="#1e1e2f")
        self.geometry("900x600")
        self.resizable(False, False)

        # DB connect
        self.db = Database(host='localhost', user='minkhanttun', password='your_password', database='mkt')
        if self.db.connect():
            print("Database connected successfully.")
        else:
            messagebox.showerror("Error", "Failed to connect to the database.")

        self.colors = self.fetch_colors()  # For combobox
        self.create_widgets()
        self.populate_color_combobox()
        self.load_stock_history()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8, background="#3e3e50", foreground="white")
        style.map("TButton",
                  background=[("active", "#5c5c77")],
                  foreground=[("disabled", "#a0a0a0")])
        style.configure("TLabel", background="#1e1e2f", foreground="white", font=("Segoe UI", 11))
        style.configure("TCombobox", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 11))
        style.configure("Treeview", font=("Segoe UI", 10), background="#2e2e3e", foreground="white",
                        fieldbackground="#2e2e3e")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#3e3e50", foreground="white")

        # Input frame
        input_frame = ttk.LabelFrame(self, text="Stock Entry", style="TLabelFrame")
        input_frame.place(x=20, y=20, width=860, height=140)

        ttk.Label(input_frame, text="Base Color:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.base_color_combobox = ttk.Combobox(input_frame, state='readonly', width=25)
        self.base_color_combobox.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Batch No:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.batch_no_entry = ttk.Entry(input_frame, width=28)
        self.batch_no_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Come (Qty):").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.come_entry = ttk.Entry(input_frame, width=20)
        self.come_entry.grid(row=0, column=3, padx=10, pady=10)

        ttk.Label(input_frame, text="Date:").grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.date_entry = DateEntry(input_frame, date_pattern='yyyy-mm-dd', width=18)
        self.date_entry.grid(row=1, column=3, padx=10, pady=10)

        # Buttons
        self.submit_button = ttk.Button(input_frame, text="Submit", command=self.submit_data)
        self.submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        self.clear_button = ttk.Button(input_frame, text="Clear", command=self.clear_entries)
        self.clear_button.grid(row=2, column=2, columnspan=2, padx=10, pady=15, sticky="ew")

        # Filter frame
        filter_frame = ttk.LabelFrame(self, text="Filter Stock History by Date", style="TLabelFrame")
        filter_frame.place(x=20, y=180, width=860, height=80)

        ttk.Label(filter_frame, text="Start Date:").grid(row=0, column=0, padx=10, pady=20, sticky="e")
        self.start_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd', width=18)
        self.start_date.grid(row=0, column=1, padx=10, pady=20)

        ttk.Label(filter_frame, text="End Date:").grid(row=0, column=2, padx=10, pady=20, sticky="e")
        self.end_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd', width=18)
        self.end_date.grid(row=0, column=3, padx=10, pady=20)

        self.filter_button = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_date_filter)
        self.filter_button.grid(row=0, column=4, padx=10)

        self.reset_filter_button = ttk.Button(filter_frame, text="Reset Filter", command=self.load_stock_history)
        self.reset_filter_button.grid(row=0, column=5, padx=10)

        # Table frame
        table_frame = ttk.LabelFrame(self, text="Stock History Log", style="TLabelFrame")
        table_frame.place(x=20, y=270, width=860, height=300)

        columns = ("SrNo", "BaseColor", "BatchNo", "Come", "Date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading("SrNo", text="SrNo")
        self.tree.heading("BaseColor", text="Base Color")
        self.tree.heading("BatchNo", text="Batch No")
        self.tree.heading("Come", text="Quantity")
        self.tree.heading("Date", text="Date")

        self.tree.column("SrNo", width=50, anchor='center')
        self.tree.column("BaseColor", width=150)
        self.tree.column("BatchNo", width=150)
        self.tree.column("Come", width=100, anchor='center')
        self.tree.column("Date", width=150, anchor='center')

        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Export buttons
        export_frame = ttk.Frame(self)
        export_frame.place(x=20, y=580, width=860, height=40)

        self.export_csv_button = ttk.Button(export_frame, text="Export CSV", command=self.export_csv)
        self.export_csv_button.pack(side='left', padx=20)

        self.export_excel_button = ttk.Button(export_frame, text="Export Excel", command=self.export_excel)
        self.export_excel_button.pack(side='left', padx=20)

    def fetch_colors(self):
        """Fetch existing colors from the ColorTable."""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT ColorID, BaseColor FROM ColorTable")
            colors = cursor.fetchall()
            cursor.close()
            return colors
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching colors: {e}")
            return []

    def populate_color_combobox(self):
        color_names = [color[1] for color in self.colors]
        self.base_color_combobox['values'] = color_names
        if color_names:
            self.base_color_combobox.current(0)

    def submit_data(self):
        base_color = self.base_color_combobox.get()
        batch_no = self.batch_no_entry.get()
        come = self.come_entry.get()
        date_input = self.date_entry.get()

        if not (base_color and batch_no and come and date_input):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            come_val = int(come)
            if come_val <= 0:
                messagebox.showerror("Error", "'Come' quantity must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Error", "'Come' quantity must be a valid number.")
            return

        # Get ColorID for base_color
        color_id = next((c[0] for c in self.colors if c[1] == base_color), None)
        if color_id is None:
            messagebox.showerror("Error", "Selected color not found in database.")
            return

        formatted_date = self.format_date(date_input)
        if not formatted_date:
            return

        try:
            cursor = self.db.connection.cursor()
            # Update stock
            update_stock_query = """UPDATE ColorTable SET Stock = Stock + %s, Date = %s WHERE ColorID = %s"""
            cursor.execute(update_stock_query, (come_val, formatted_date, color_id))
            self.db.connection.commit()

            # Insert into StockRecord
            insert_query = """INSERT INTO StockRecord (ColorID, BatchNumber, Come, Date)
                              VALUES (%s, %s, %s, %s)"""
            cursor.execute(insert_query, (color_id, batch_no, come_val, formatted_date))
            self.db.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "Stock entry added successfully.")
            self.load_stock_history()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert data: {e}")

    def clear_entries(self):
        self.batch_no_entry.delete(0, tk.END)
        self.come_entry.delete(0, tk.END)
        self.date_entry.set_date(date.today())

    def format_date(self, date_text):
        try:
            date_obj = datetime.strptime(date_text, '%Y-%m-%d')
            return date_obj.strftime('%d %B %Y')
        except Exception as e:
            messagebox.showerror("Error", "Date format error. Please use 'yyyy-mm-dd'.")
            return None

    def load_stock_history(self):
        # Clear current rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.db.connection.cursor()
            # Join StockRecord with ColorTable to get BaseColor name
            cursor.execute(
                """SELECT sr.StockRecordID, ct.BaseColor, sr.BatchNumber, sr.Come, sr.Date
                   FROM StockRecord sr
                   JOIN ColorTable ct ON sr.ColorID = ct.ColorID
                   ORDER BY sr.Date DESC, sr.StockRecordID DESC""")
            records = cursor.fetchall()
            cursor.close()

            for i, (srid, base_color, batch_no, come, dt) in enumerate(records, start=1):
                formatted_dt = dt.strftime('%d %b %Y') if isinstance(dt, (datetime, date)) else dt
                self.tree.insert("", "end", values=(i, base_color, batch_no, come, formatted_dt))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock history: {e}")

    def apply_date_filter(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()

        if start > end:
            messagebox.showerror("Error", "Start date cannot be after end date.")
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            cursor = self.db.connection.cursor()
            cursor.execute(
                """SELECT sr.StockRecordID, ct.BaseColor, sr.BatchNumber, sr.Come, sr.Date
                   FROM StockRecord sr
                   JOIN ColorTable ct ON sr.ColorID = ct.ColorID
                   WHERE sr.Date BETWEEN %s AND %s
                   ORDER BY sr.Date DESC, sr.StockRecordID DESC""", (start, end))
            records = cursor.fetchall()
            cursor.close()

            for i, (srid, base_color, batch_no, come, dt) in enumerate(records, start=1):
                formatted_dt = dt.strftime('%d %b %Y') if isinstance(dt, (datetime, date)) else dt
                self.tree.insert("", "end", values=(i, base_color, batch_no, come, formatted_dt))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply date filter: {e}")

    def export_csv(self):
        self.export_data("csv")

    def export_excel(self):
        self.export_data("xlsx")

    def export_data(self, file_type):
        if not os.path.exists(EXPORT_FOLDER):
            os.makedirs(EXPORT_FOLDER)

        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Warning", "No data to export.")
            return

        data = []
        for item in items:
            data.append(self.tree.item(item)['values'])

        df = pd.DataFrame(data, columns=["SrNo", "BaseColor", "BatchNo", "Quantity", "Date"])
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"StockEntryLog_{now_str}.{file_type}"
        filepath = os.path.join(EXPORT_FOLDER, filename)

        try:
            if file_type == "csv":
                df.to_csv(filepath, index=False)
            else:
                df.to_excel(filepath, index=False)

            messagebox.showinfo("Export Successful", f"Data exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")

    def on_closing(self):
        self.db.disconnect()
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = StockEntryForm(root)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
