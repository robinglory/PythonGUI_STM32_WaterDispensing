import tkinter as tk
import sqlite3
from tkinter import ttk, messagebox

class SQLiteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite GUI")

        # Create a connection to the SQLite database
        self.conn = sqlite3.connect("mydatabase.db")
        self.cursor = self.conn.cursor()

        # Create GUI elements
        self.create_widgets()

    def display_data(self):
        # Clear any existing data in the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch data from the database
        self.cursor.execute("SELECT * FROM StockRecord")
        rows = self.cursor.fetchall()

        # Insert data into the treeview
        for row in rows:
            self.tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteGUI(root)
    root.mainloop()