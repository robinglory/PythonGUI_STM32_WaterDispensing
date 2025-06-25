import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import csv
import pandas as pd
from tkinter import filedialog

class BomEntryForm(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("BOM Management System")
        self.geometry("900x600")
        self.resizable(True, True)
        self.configure(bg='#f0f0f0')

        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TCombobox', font=('Arial', 10))
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))

        # Status bar - create this BEFORE tabs and data loading!
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Database connection
        self.db = self.connect_to_database()
        self.available_colors = self.fetch_available_colors() if self.db else []

        # Variables
        self.table_data = []
        self.used_colors = []
        self.selected_bh_id = None

        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabbed interface (which calls load_all_boms)
        self.create_tabbed_interface()

# Adding the CSV and Excel import/export methods
    def export_bom_to_csv(self):
        try:
            rows = [self.boms_tree.item(item)['values'] for item in self.boms_tree.get_children()]
            if not rows:
                messagebox.showinfo("Export", "No BOM data to export.")
                return
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv")])
            if not file_path:
                return
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['BOM ID', 'Final Color', 'Date'])
                writer.writerows(rows)
            messagebox.showinfo("Export", f"BOM list exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def export_bom_to_excel(self):
        try:
            rows = [self.boms_tree.item(item)['values'] for item in self.boms_tree.get_children()]
            if not rows:
                messagebox.showinfo("Export", "No BOM data to export.")
                return
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                    filetypes=[("Excel files", "*.xlsx")])
            if not file_path:
                return
            df = pd.DataFrame(rows, columns=['BOM ID', 'Final Color', 'Date'])
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export", f"BOM list exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    # Adding the delete_bom method to handle BOM deletion
    # This method will prompt for confirmation and delete the BOM from both BOMDetail and BOMHeading tables.
    def delete_bom(self, bh_id):
        if not bh_id:
            messagebox.showwarning("Missing ID", "No BOM ID provided to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete BOM '{bh_id}'?")
        if not confirm:
            return

        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM BOMDetail WHERE BH_ID=%s", (bh_id,))
            cursor.execute("DELETE FROM BOMHeading WHERE BH_ID=%s", (bh_id,))
            self.db.commit()
            messagebox.showinfo("Deleted", f"BOM '{bh_id}' deleted successfully.")
            self.load_all_boms()
            self.clear_edit_tab()
        except Error as e:
            self.db.rollback()
            messagebox.showerror("Database Error", f"Failed to delete BOM: {e}")
        finally:
            if cursor:
                cursor.close()


# Adding the add_base_color method to handle adding base colors
# Adding insert data method to handle inserting BOM data
# Adding clear_entries method to clear form fields

    def add_base_color(self):
        """Add a base color and its percentage to the table in Insert tab"""
        base_color = self.base_color_combobox.get().strip()
        percentage_str = self.percentage_entry.get().strip()

        # Clear previous error message
        self.error_label.config(text="")

        if not base_color:
            self.error_label.config(text="Please select a base color.")
            return
        if not percentage_str.isdigit():
            self.error_label.config(text="Percentage must be a positive integer.")
            return

        percentage = int(percentage_str)
        if percentage <= 0 or percentage > 100:
            self.error_label.config(text="Percentage must be between 1 and 100.")
            return

        # Check if this base color is already added
        for child in self.base_tree.get_children():
            existing_color = self.base_tree.item(child)['values'][0]
            if existing_color == base_color:
                self.error_label.config(text=f"Base color '{base_color}' is already added.")
                return

        # Calculate total percentage if added
        current_total = 0
        for child in self.base_tree.get_children():
            current_total += int(self.base_tree.item(child)['values'][1])
        new_total = current_total + percentage

        if new_total > 100:
            self.error_label.config(text=f"Total percentage cannot exceed 100%. Current total is {current_total}%.")
            return

        # Add to treeview
        self.base_tree.insert('', tk.END, values=(base_color, percentage))

        # Update total percentage label
        self.total_percentage.config(text=f"Total: {new_total}%")

        # Clear inputs
        self.base_color_combobox.set('')
        self.percentage_entry.delete(0, tk.END)

    def insert_data(self):
        """Insert new BOM into the database with its details"""
        final_color = self.final_color_entry.get().strip()
        date_value = self.date_entry.get_date()
        base_colors = []

        # Clear error label
        self.error_label.config(text="")

        if not final_color:
            self.error_label.config(text="Final color cannot be empty.")
            return

        # Collect base colors and percentages from the treeview
        for child in self.base_tree.get_children():
            color, percent = self.base_tree.item(child)['values']
            base_colors.append((color, int(percent)))

        if not base_colors:
            self.error_label.config(text="Add at least one base color.")
            return

        # Check total percentage must be exactly 100%
        total_percentage = sum(p for _, p in base_colors)
        if total_percentage != 100:
            self.error_label.config(text=f"Total percentage must be exactly 100%. Current total: {total_percentage}%.")
            return

        try:
            cursor = self.db.cursor()

            # Generate new BH_ID like B000, B001, etc.
            cursor.execute("SELECT MAX(BH_ID) FROM BOMHeading")
            result = cursor.fetchone()
            if result[0] is None:
                new_bh_id = "B000"
            else:
                max_id = result[0]
                max_num = int(max_id[1:])  # Remove leading letter
                new_bh_id = f"B{max_num + 1:03d}"

            # Insert BOM heading
            cursor.execute(
                "INSERT INTO BOMHeading (BH_ID, FinalColor, Date) VALUES (%s, %s, %s)",
                (new_bh_id, final_color, date_value)
            )

            # Insert BOM details
            for color, percent in base_colors:
                cursor.execute(
                    "INSERT INTO BOMDetail (BH_ID, BaseColor, Percentage) VALUES (%s, %s, %s)",
                    (new_bh_id, color, percent)
                )

            self.db.commit()
            messagebox.showinfo("Success", f"BOM '{final_color}' inserted successfully with ID {new_bh_id}.")

            # Clear form and treeview
            self.clear_entries()
            self.load_all_boms()  # Refresh BOM list view
        except Error as e:
            self.db.rollback()
            messagebox.showerror("Database Error", f"Failed to insert BOM: {e}")
        finally:
            if cursor:
                cursor.close()

    def clear_entries(self):
        """Clear all input fields and treeview in Insert tab"""
        self.final_color_entry.delete(0, tk.END)
        self.date_entry.set_date(datetime.today())
        self.base_color_combobox.set('')
        self.percentage_entry.delete(0, tk.END)
        for item in self.base_tree.get_children():
            self.base_tree.delete(item)
        self.total_percentage.config(text="Total: 0%")
        self.error_label.config(text="")




    def connect_to_database(self):
        """Establish database connection"""
        try:
            return mysql.connector.connect(
                host='localhost',
                user='minkhanttun',
                password='29112000',
                database='mkt'
            )
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            return None
    
    def create_tabbed_interface(self):
        """Create the tabbed interface"""
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Create tabs
        self.insert_tab = ttk.Frame(self.notebook)
        self.edit_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.insert_tab, text="Add New BOM")
        self.notebook.add(self.edit_tab, text="Edit BOM")
        self.notebook.add(self.view_tab, text="View BOMs")
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Setup each tab
        self.setup_insert_tab()
        self.setup_edit_tab()
        self.setup_view_tab()
    
    def setup_insert_tab(self):
        """Setup the insert tab"""
        # Header
        header = ttk.Label(self.insert_tab, text="Add New Bill of Materials", font=('Arial', 12, 'bold'))
        header.pack(pady=(5, 15))
        
        # Form frame
        form_frame = ttk.Frame(self.insert_tab)
        form_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Final Color
        ttk.Label(form_frame, text="Final Color:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.final_color_entry = ttk.Entry(form_frame, width=30)
        self.final_color_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Date
        ttk.Label(form_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = DateEntry(form_frame, width=27, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Base Colors Section
        base_frame = ttk.LabelFrame(self.insert_tab, text="Base Colors", padding=10)
        base_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Base Color Input
        input_frame = ttk.Frame(base_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Base Color:").pack(side=tk.LEFT, padx=5)
        self.base_color_combobox = ttk.Combobox(input_frame, values=self.available_colors, width=25)
        self.base_color_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(input_frame, text="Percentage:").pack(side=tk.LEFT, padx=5)
        self.percentage_entry = ttk.Entry(input_frame, width=10)
        self.percentage_entry.pack(side=tk.LEFT, padx=5)
        
        self.add_button = ttk.Button(input_frame, text="Add", command=self.add_base_color)
        self.add_button.pack(side=tk.LEFT, padx=10)
        
        # Base Colors Table
        self.table_frame = ttk.Frame(base_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for base colors
        self.base_tree = ttk.Treeview(self.table_frame, columns=('color', 'percentage'), show='headings', height=5)
        self.base_tree.heading('color', text='Base Color')
        self.base_tree.heading('percentage', text='Percentage')
        self.base_tree.column('color', width=200)
        self.base_tree.column('percentage', width=100)
        self.base_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.base_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.base_tree.configure(yscrollcommand=scrollbar.set)
        
        # Total Percentage
        self.total_percentage = ttk.Label(base_frame, text="Total: 0%", font=('Arial', 10, 'bold'))
        self.total_percentage.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Error Label
        self.error_label = ttk.Label(base_frame, text="", foreground='red')
        self.error_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Submit Button
        button_frame = ttk.Frame(self.insert_tab)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_entries)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.insert_button = ttk.Button(button_frame, text="Submit BOM", style='Accent.TButton', command=self.insert_data)
        self.insert_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure accent button style
        self.style.configure('Accent.TButton', foreground='white', background='#0078d7')
   
    def setup_edit_tab(self):
        """Setup the edit tab"""
        # Header
        header = ttk.Label(self.edit_tab, text="Edit Existing BOM", font=('Arial', 12, 'bold'))
        header.pack(pady=(5, 15))
        
        # Search frame
        search_frame = ttk.Frame(self.edit_tab)
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(search_frame, text="Enter BH_ID:").pack(side=tk.LEFT, padx=5)
        self.id_entry = ttk.Entry(search_frame, width=15)
        self.id_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_button = ttk.Button(search_frame, text="Search", command=self.load_data_for_edit)
        self.search_button.pack(side=tk.LEFT, padx=10)
        
        # Form frame
        self.edit_form_frame = ttk.Frame(self.edit_tab)
        self.edit_form_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Final Color
        ttk.Label(self.edit_form_frame, text="Final Color:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.edit_final_color_entry = ttk.Entry(self.edit_form_frame, width=30)
        self.edit_final_color_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Date
        ttk.Label(self.edit_form_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.edit_date_entry = DateEntry(self.edit_form_frame, width=27, date_pattern='yyyy-mm-dd')
        self.edit_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Base Colors Section
        self.edit_base_frame = ttk.LabelFrame(self.edit_tab, text="Base Colors", padding=10)
        self.edit_base_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Base Colors Treeview
        self.edit_base_tree = ttk.Treeview(self.edit_base_frame, columns=('color', 'percentage'), show='headings', height=5)
        self.edit_base_tree.heading('color', text='Base Color')
        self.edit_base_tree.heading('percentage', text='Percentage')
        self.edit_base_tree.column('color', width=200)
        self.edit_base_tree.column('percentage', width=100)
        self.edit_base_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.edit_base_frame, orient=tk.VERTICAL, command=self.edit_base_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.edit_base_tree.configure(yscrollcommand=scrollbar.set)
        
        # Edit Total Percentage
        self.edit_total_percentage = ttk.Label(self.edit_base_frame, text="Total: 0%", font=('Arial', 10, 'bold'))
        self.edit_total_percentage.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Button Frame
        button_frame = ttk.Frame(self.edit_tab)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.update_button = ttk.Button(button_frame, text="Update BOM", style='Accent.TButton', command=self.update_data)
        self.update_button.pack(side=tk.RIGHT, padx=5)
    
    def setup_view_tab(self):
        """Setup the view tab to display all BOMs"""
        # Header
        header = ttk.Label(self.view_tab, text="View All BOMs", font=('Arial', 12, 'bold'))
        header.pack(pady=(5, 15))
        
        # Search and filter frame
        filter_frame = ttk.Frame(self.view_tab)
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(filter_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_button = ttk.Button(filter_frame, text="Search", command=self.search_boms)
        self.search_button.pack(side=tk.LEFT, padx=10)
        
        self.refresh_button = ttk.Button(filter_frame, text="Refresh", command=self.load_all_boms)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)

        # Add Export Buttons Frame under filter_frame or elsewhere
        export_frame = ttk.Frame(self.view_tab)
        export_frame.pack(fill=tk.X, padx=20, pady=5)

        export_csv_btn = ttk.Button(export_frame, text="Export CSV", command=self.export_bom_to_csv)
        export_csv_btn.pack(side=tk.LEFT, padx=5)

        export_excel_btn = ttk.Button(export_frame, text="Export Excel", command=self.export_bom_to_excel)
        export_excel_btn.pack(side=tk.LEFT, padx=5)

        ## Adding Delete Button
        # Delete button for view tab
        delete_btn = ttk.Button(self.view_tab, text="Delete Selected BOM", command=self.delete_selected_bom)
        delete_btn.pack(pady=5)

        # BOMs Treeview
        tree_frame = ttk.Frame(self.view_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.boms_tree = ttk.Treeview(tree_frame, columns=('id', 'final_color', 'date'), show='headings')
        self.boms_tree.heading('id', text='BOM ID')
        self.boms_tree.heading('final_color', text='Final Color')
        self.boms_tree.heading('date', text='Date')
        self.boms_tree.column('id', width=80)
        self.boms_tree.column('final_color', width=200)
        self.boms_tree.column('date', width=150)
        self.boms_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.boms_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.boms_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load all BOMs initially
        self.load_all_boms()
        
        # Double click to edit
        self.boms_tree.bind('<Double-1>', self.edit_selected_bom)
    
    # [Rest of your methods (add_base_color, insert_data, etc.) would follow here]
    # They would need to be updated to work with the new UI elements
    
    def fetch_available_colors(self):
        """Fetch available base colors from database"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT BaseColor FROM ColorTable")
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch colors: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def load_all_boms(self):
        """Load all BOMs into the view tab"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT BH_ID, FinalColor, Date FROM BOMHeading ORDER BY Date DESC")
            
            # Clear existing items
            for item in self.boms_tree.get_children():
                self.boms_tree.delete(item)
            
            # Add new items
            for row in cursor.fetchall():
                self.boms_tree.insert('', tk.END, values=row)
                
            self.status_bar.config(text=f"Loaded {self.boms_tree.get_children().__len__()} BOMs")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load BOMs: {e}")
        finally:
            if cursor:
                cursor.close()

    def load_data_for_edit(self):
        bh_id = self.id_entry.get().strip()
        if not bh_id:
            messagebox.showwarning("Input Error", "Please enter a BOM ID to search.")
            return

        try:
            cursor = self.db.cursor()
            # Fetch BOM heading info
            cursor.execute("SELECT FinalColor, Date FROM BOMHeading WHERE BH_ID = %s", (bh_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showinfo("Not Found", f"No BOM found with ID {bh_id}.")
                return
            
            final_color, date_value = result
            self.edit_final_color_entry.delete(0, tk.END)
            self.edit_final_color_entry.insert(0, final_color)
            self.edit_date_entry.set_date(date_value)

            # Fetch BOM details (base colors)
            cursor.execute("SELECT BaseColor, Percentage FROM BOMDetail WHERE BH_ID = %s", (bh_id,))
            rows = cursor.fetchall()

            # Clear old items in edit tree
            for item in self.edit_base_tree.get_children():
                self.edit_base_tree.delete(item)

            total_percentage = 0
            for base_color, percent in rows:
                self.edit_base_tree.insert('', tk.END, values=(base_color, percent))
                total_percentage += percent

            self.edit_total_percentage.config(text=f"Total: {total_percentage}%")
            self.selected_bh_id = bh_id
            self.status_bar.config(text=f"Loaded BOM {bh_id} for editing.")

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load BOM data: {e}")
        finally:
            if cursor:
                cursor.close()


    def update_data(self):
        if not self.selected_bh_id:
            messagebox.showerror("Error", "No BOM selected for update.")
            return

        final_color = self.edit_final_color_entry.get().strip()
        date_value = self.edit_date_entry.get_date()
        base_colors = []

        # Validate inputs
        if not final_color:
            messagebox.showerror("Validation Error", "Final color cannot be empty.")
            return

        for child in self.edit_base_tree.get_children():
            color, percent = self.edit_base_tree.item(child)['values']
            base_colors.append((color, int(percent)))

        if not base_colors:
            messagebox.showerror("Validation Error", "Add at least one base color.")
            return

        total_percentage = sum(p for _, p in base_colors)
        if total_percentage != 100:
            messagebox.showerror("Validation Error", f"Total percentage must be exactly 100%. Current total: {total_percentage}%.")
            return

        try:
            cursor = self.db.cursor()
            # Update BOMHeading
            cursor.execute(
                "UPDATE BOMHeading SET FinalColor=%s, Date=%s WHERE BH_ID=%s",
                (final_color, date_value, self.selected_bh_id)
            )

            # Delete existing details
            cursor.execute(
                "DELETE FROM BOMDetail WHERE BH_ID=%s",
                (self.selected_bh_id,)
            )

            # Insert new details
            for color, percent in base_colors:
                cursor.execute(
                    "INSERT INTO BOMDetail (BH_ID, BaseColor, Percentage) VALUES (%s, %s, %s)",
                    (self.selected_bh_id, color, percent)
                )

            self.db.commit()
            messagebox.showinfo("Success", f"BOM '{self.selected_bh_id}' updated successfully.")
            self.load_all_boms()
            self.clear_edit_tab()
        except Error as e:
            self.db.rollback()
            messagebox.showerror("Database Error", f"Failed to update BOM: {e}")
        finally:
            if cursor:
                cursor.close()

    def clear_edit_tab(self):
        self.selected_bh_id = None
        self.id_entry.delete(0, tk.END)
        self.edit_final_color_entry.delete(0, tk.END)
        self.edit_date_entry.set_date(datetime.today())
        for item in self.edit_base_tree.get_children():
            self.edit_base_tree.delete(item)
        self.edit_total_percentage.config(text="Total: 0%")


    def search_boms(self):
        search_term = self.search_entry.get().strip()
        try:
            cursor = self.db.cursor()
            query = """
                SELECT BH_ID, FinalColor, Date 
                FROM BOMHeading 
                WHERE BH_ID LIKE %s OR FinalColor LIKE %s
                ORDER BY Date DESC
            """
            like_term = f"%{search_term}%"
            cursor.execute(query, (like_term, like_term))

            # Clear existing items
            for item in self.boms_tree.get_children():
                self.boms_tree.delete(item)

            # Add filtered results
            for row in cursor.fetchall():
                self.boms_tree.insert('', tk.END, values=row)

            self.status_bar.config(text=f"Search results: {len(self.boms_tree.get_children())} BOM(s) found")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to search BOMs: {e}")
        finally:
            if cursor:
                cursor.close()

##    # Adding the edit_selected_bom method to handle double-clicking a BOM in the view tab
#    # This method will load the selected BOM's data into the edit tab for modification.
    def edit_selected_bom(self, event):
        selected_item = self.boms_tree.selection()
        if not selected_item:
            return
        item = self.boms_tree.item(selected_item)
        bh_id = item['values'][0]  # Assuming BH_ID is the first column
        self.notebook.select(self.edit_tab)  # Switch to edit tab
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, bh_id)
        self.load_data_for_edit()

    # 🔽 ADD THIS RIGHT AFTER
    def delete_selected_bom(self):
        selected_item = self.boms_tree.selection()
        if not selected_item:
            messagebox.showwarning("Select BOM", "Please select a BOM to delete.")
            return

        bh_id = self.boms_tree.item(selected_item)['values'][0]
        self.delete_bom(bh_id)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = BomEntryForm(root)
    app.mainloop()