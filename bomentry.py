import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import mysql.connector
from mysql.connector import Error

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
        
        # Create tabbed interface
        self.create_tabbed_interface()
        
        # Status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def connect_to_database(self):
        """Establish database connection"""
        try:
            return mysql.connector.connect(
                host='localhost',
                user='minkhanttun',
                password='your_password',
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

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = BomEntryForm(root)
    app.mainloop()