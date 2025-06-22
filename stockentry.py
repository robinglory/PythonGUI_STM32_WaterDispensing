
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from mysql_connection import Database
from datetime import datetime, date
import csv
import os

EXPORT_PATH = r"C:\Users\ASUS\Documents\MinKhantTun(Project)\PythonGUI\PythonGUI\Stock Entry Log"

class StockEntryForm(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("📦 Stock Entry")
        self.geometry("1200x800")
        self.configure(bg="white")
        self.resizable(False, False)

        self.db = Database(host='localhost', user='minkhanttun', password='29112000', database='mkt')
        if self.db.connect():
            print("Database connected successfully.")
        else:
            print("Failed to connect to the database.")

        self.colors = self.fetch_colors()
        self.create_widgets()
        self.populate_color_combobox()
        self.load_stock_history()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabelFrame", background="white", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("TLabel", background="white", font=("Segoe UI", 10))

        input_frame = ttk.LabelFrame(self, text="Stock Entry")
        input_frame.pack(pady=15, padx=20, fill="x")

        form_inner = tk.Frame(input_frame, bg="white")
        form_inner.pack(anchor="center", pady=10)

        tk.Label(form_inner, text="Base Color:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.base_color_combobox = ttk.Combobox(form_inner, state='readonly', width=20)
        self.base_color_combobox.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form_inner, text="Batch No:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.batch_no_entry = tk.Entry(form_inner, width=22)
        self.batch_no_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(form_inner, text="Come (Qty):", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.come_entry = tk.Entry(form_inner, width=22)
        self.come_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(form_inner, text="Date:", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = DateEntry(form_inner, date_pattern='yyyy-mm-dd', width=19)
        self.date_entry.grid(row=3, column=1, padx=10, pady=10)

        self.submit_button = ttk.Button(input_frame, text="Submit", command=self.submit_data)
        self.submit_button.pack(pady=10)

        filter_frame = ttk.LabelFrame(self, text="Filter Stock History by Date")
        filter_frame.pack(pady=15, padx=20, fill="x")

        filter_inner = tk.Frame(filter_frame, bg="white")
        filter_inner.pack(anchor="center", pady=10)

        tk.Label(filter_inner, text="From:", bg="white").grid(row=0, column=0, padx=10)
        self.from_date = DateEntry(filter_inner, date_pattern='yyyy-mm-dd')
        self.from_date.grid(row=0, column=1, padx=10)

        tk.Label(filter_inner, text="To:", bg="white").grid(row=0, column=2, padx=10)
        self.to_date = DateEntry(filter_inner, date_pattern='yyyy-mm-dd')
        self.to_date.grid(row=0, column=3, padx=10)

        self.filter_button = ttk.Button(filter_inner, text="Filter", command=self.filter_history)
        self.filter_button.grid(row=0, column=4, padx=10)

        table_frame = ttk.LabelFrame(self, text="Stock History Log")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ColorID", "BatchNumber", "Come", "Date"), show="headings")
        self.tree.heading("ColorID", text="Color ID")
        self.tree.heading("BatchNumber", text="Batch No")
        self.tree.heading("Come", text="Quantity")
        self.tree.heading("Date", text="Date")
        self.tree.pack(fill="both", expand=True)

        export_button = ttk.Button(self, text="📁 Export Log", command=self.export_log)
        export_button.pack(pady=10)

    def fetch_colors(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT ColorID, BaseColor FROM ColorTable")
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching colors:", e)
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

        if not (batch_no and come and date_input):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            come = int(come)
            if come <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Come must be a positive integer.")
            return

        new_color_id = next((color[0] for color in self.colors if color[1] == base_color), None)
        if new_color_id:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("UPDATE ColorTable SET Stock = Stock + %s, Date = %s WHERE ColorID = %s", (come, date_input, new_color_id))
                cursor.execute("INSERT INTO StockRecord (ColorID, BatchNumber, Come, Date) VALUES (%s, %s, %s, %s)", (new_color_id, batch_no, come, date_input))
                self.db.connection.commit()
                messagebox.showinfo("Success", "Stock entry added successfully.")
                self.load_stock_history()
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}")
        else:
            messagebox.showerror("Error", "Base color not found in the database.")

    def load_stock_history(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT ColorID, BatchNumber, Come, Date FROM StockRecord ORDER BY Date DESC")
            rows = cursor.fetchall()
            self.update_treeview(rows)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock history: {e}")

    def filter_history(self):
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        try:
            cursor = self.db.connection.cursor()
            query = "SELECT ColorID, BatchNumber, Come, Date FROM StockRecord WHERE Date BETWEEN %s AND %s ORDER BY Date DESC"
            cursor.execute(query, (from_date, to_date))
            rows = cursor.fetchall()
            self.update_treeview(rows)
        except Exception as e:
            messagebox.showerror("Error", f"Filtering failed: {e}")

    def update_treeview(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def export_log(self):
        if not os.path.exists(EXPORT_PATH):
            os.makedirs(EXPORT_PATH)
        filename = f"stock_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(EXPORT_PATH, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ColorID", "BatchNumber", "Come", "Date"])
            for row in self.tree.get_children():
                writer.writerow(self.tree.item(row)['values'])
        messagebox.showinfo("Export", f"Log exported to: {filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = StockEntryForm(master=root)
    app.mainloop()
