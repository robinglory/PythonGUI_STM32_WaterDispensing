# edithandler.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from mysql_connection import Database  # Ensure you have a Database class for MySQL connection

class EditHandler:
    def __init__(self, master, db: Database, table_name: str, fields: dict, id_field: str = 'id'):
        """
        Initialize the EditHandler.

        Parameters:
        - master: The root or parent widget for the edit handler.
        - db: An instance of the Database class for connecting to the MySQL database.
        - table_name: The name of the table to be edited.
        - fields: A dictionary with keys as field names and values as tkinter entry widgets.
        - id_field: The name of the ID field for the table (default is 'id').
        """
        self.master = master
        self.db = db
        self.table_name = table_name
        self.fields = fields  # Dict with field names as keys and entry widgets as values
        self.record_id = None  # Store record ID being edited
        self.id_field = id_field  # Allow for different ID field names

        # Button placeholders (for toggling edit/update mode)
        self.edit_button = None
        self.update_button = None

    def load_record(self, record_id):
        """Load a record from the database into entry fields for editing."""
        try:
            self.record_id = record_id
            cursor = self.db.connection.cursor()
            query = f"SELECT {', '.join(self.fields.keys())} FROM {self.table_name} WHERE {self.id_field} = %s"
            cursor.execute(query, (record_id,))
            result = cursor.fetchone()
            
            if result:
                for index, field in enumerate(self.fields.keys()):
                    self.fields[field].delete(0, tk.END)
                    self.fields[field].insert(0, result[index])

            cursor.close()
            self.toggle_edit_mode(True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load record: {e}")

    def toggle_edit_mode(self, editing=True):
        """Toggle between edit and update modes."""
        if editing:
            if self.edit_button:
                self.edit_button.grid_remove()
            if not self.update_button:
                self.update_button = ttk.Button(self.master, text="Update", command=self.update_record)
                self.update_button.grid(row=len(self.fields), column=1, padx=5, pady=5)
        else:
            if self.update_button:
                self.update_button.grid_remove()
            if self.edit_button:
                self.edit_button.grid()

    def update_record(self):
        """Update the current record with new values from entry fields."""
        try:
            # Validate fields
            field_values = {field: self.fields[field].get() for field in self.fields}
            if any(not value for value in field_values.values()):
                messagebox.showwarning("Warning", "All fields must be filled out.")
                return
            
            # Prepare update query
            query = f"UPDATE {self.table_name} SET " + ", ".join(f"{field} = %s" for field in field_values.keys())
            query += f" WHERE {self.id_field} = %s"
            
            # Execute the update query
            cursor = self.db.connection.cursor()
            cursor.execute(query, tuple(field_values.values()) + (self.record_id,))
            self.db.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "Record updated successfully.")
            self.clear_fields()  # Clear fields after update
            self.toggle_edit_mode(False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")

    def clear_fields(self):
        """Clear all entry fields."""
        for field in self.fields.values():
            field.delete(0, tk.END)

    def bind_edit_button(self, button):
        """Bind the edit button to enable edit mode."""
        self.edit_button = button
        self.edit_button.config(command=lambda: self.load_record(self.record_id))
