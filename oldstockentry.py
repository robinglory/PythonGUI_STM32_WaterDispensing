# Preparing code for redesigned stockentry.py with dark theme, clean layout, date filters and export features.
# This version will work with the new StockRecord table and export logs to the defined folder.

code_path = "/mnt/data/stockentry.py"
stock_entry_code = '''
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime, date
import mysql.connector
import pandas as pd
import os

EXPORT_PATH = r"C:\\Users\\ASUS\\Documents\\MinKhantTun(Project)\\PythonGUI\\PythonGUI\\Stock Entry Log"

class StockEntryForm(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("📦 Stock Entry")
        self.geometry("800x600")
        self.configure(bg="#1e1e2f")
        self.db = self.connect_db()
        self.colors = self.fetch_colors()
        self.create_widgets()

    def connect_db(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="minkhanttun",
                password="your_password",  # UPDATE YOUR PASSWORD
                database="mkt"
            )
            print("Database connected successfully.")
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error while connecting to MySQL: {err}")
            return None

    def fetch_colors(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT ColorID, BaseColor FROM ColorTable")
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching colors:", e)
            return []

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e2f", foreground="white", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#3e3e50", foreground="white")
        style.configure("TCombobox", fieldbackground="#1e1e2f", background="#1e1e2f", foreground="white")
        style.configure("Treeview", background="#252636", fieldbackground="#252636", foreground="white", rowheight=25)
        style.map("TButton", background=[("active", "#5c5c77")])

        input_frame = ttk.LabelFrame(self, text="Stock Entry")
        input_frame.pack(padx=20, pady=10, fill="x")

        ttk.Label(input_frame, text="Base Color:").grid(row=0, column=0, padx=5, pady=5)
        self.base_color_cb = ttk.Combobox(input_frame, state='readonly')
        self.base_color_cb.grid(row=0, column=1, padx=5, pady=5)
        self.base_color_cb['values'] = [color[1] for color in self.colors]

        ttk.Label(input_frame, text="Batch No:").grid(row=1, column=0, padx=5, pady=5)
        self.batch_entry = ttk.Entry(input_frame)
        self.batch_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Come Quantity:").grid(row=2, column=0, padx=5, pady=5)
        self.come_entry = ttk.Entry(input_frame)
        self.come_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Date:").grid(row=3, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Submit", command=self.submit_data).grid(row=4, column=0, columnspan=2, pady=10)

        # Filter + Table
        filter_frame = ttk.LabelFrame(self, text="Filter Stock History by Date")
        filter_frame.pack(padx=20, pady=10, fill="x")

        ttk.Label(filter_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Search", command=self.load_stock_history).grid(row=0, column=4, padx=10)

        table_frame = ttk.LabelFrame(self, text="Stock History Log")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("RecordID", "ColorID", "BatchNumber", "Come", "Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)

        export_btn = ttk.Button(self, text="Export to CSV/Excel", command=self.export_data)
        export_btn.pack(pady=10)

    def submit_data(self):
        base_color = self.base_color_cb.get()
        batch = self.batch_entry.get()
        come = self.come_entry.get()
        date_val = self.date_entry.get()

        if not (base_color and batch and come):
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return

        color_id = next((c[0] for c in self.colors if c[1] == base_color), None)
        try:
            cursor = self.db.cursor()
            cursor.execute("INSERT INTO StockRecord (ColorID, BatchNumber, Come, Date) VALUES (%s, %s, %s, %s)",
                           (color_id, batch, int(come), date_val))
            self.db.commit()
            messagebox.showinfo("Success", "Stock entry submitted successfully.")
            self.batch_entry.delete(0, tk.END)
            self.come_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit stock: {e}")

    def load_stock_history(self):
        from_date = self.start_date.get_date()
        to_date = self.end_date.get_date()
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM StockRecord WHERE Date BETWEEN %s AND %s ORDER BY Date",
                           (from_date, to_date))
            rows = cursor.fetchall()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock history: {e}")

    def export_data(self):
        data = [self.tree.item(row)["values"] for row in self.tree.get_children()]
        if not data:
            messagebox.showwarning("No Data", "No data to export.")
            return

        df = pd.DataFrame(data, columns=["RecordID", "ColorID", "BatchNumber", "Come", "Date"])
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(EXPORT_PATH, exist_ok=True)
        csv_path = os.path.join(EXPORT_PATH, f"StockLog_{now}.csv")
        excel_path = os.path.join(EXPORT_PATH, f"StockLog_{now}.xlsx")
        df.to_csv(csv_path, index=False)
        df.to_excel(excel_path, index=False)
        messagebox.showinfo("Exported", f"Stock log exported to:\n{csv_path}\n{excel_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = StockEntryForm(root)
    app.mainloop()
'''
with open(code_path, "w", encoding="utf-8") as f:
    f.write(stock_entry_code)

code_path
