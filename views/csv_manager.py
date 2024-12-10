import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class CSVManager(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_csv = None
        self.data = None
        
        self._create_ui()
        self._load_csv_list()
    
    def _create_ui(self):
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Changed to 2 for two toolbar rows
        
        # Upper toolbar
        self.upper_toolbar = ctk.CTkFrame(self)
        self.upper_toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))
        
        # Import button
        ctk.CTkButton(
            self.upper_toolbar,
            text="Import CSV",
            command=self._import_csv
        ).pack(side="left", padx=5)
        
        # Delete CSV button
        ctk.CTkButton(
            self.upper_toolbar,
            text="Delete CSV",
            command=self._delete_csv_file,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=5)
        
        # CSV selection dropdown (moved to upper toolbar)
        self.dropdown_frame = ctk.CTkFrame(self.upper_toolbar)
        self.dropdown_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(
            self.dropdown_frame,
            text="Select CSV:"
        ).pack(side="left", padx=5)
        
        # Lower toolbar
        self.lower_toolbar = ctk.CTkFrame(self)
        self.lower_toolbar.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 5))
        
        # Add Row button
        ctk.CTkButton(
            self.lower_toolbar,
            text="Add Row",
            command=self._add_row
        ).pack(side="left", padx=5)
        
        # Add Column button
        ctk.CTkButton(
            self.lower_toolbar,
            text="Add Column",
            command=self._add_column
        ).pack(side="left", padx=5)
        
        # Delete Row button
        ctk.CTkButton(
            self.lower_toolbar,
            text="Delete Row",
            command=self._delete_selected_rows,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=5)
        
        # Save button
        ctk.CTkButton(
            self.lower_toolbar,
            text="Save Changes",
            command=self._save_changes
        ).pack(side="left", padx=5)
        
        # Records count label
        self.records_label = ctk.CTkLabel(
            self.lower_toolbar,
            text="Total Records: 0"
        )
        self.records_label.pack(side="right", padx=5)
        
        # Table frame (update row number)
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create scrollbars first
        x_scroll = ctk.CTkScrollbar(self.table_frame, orientation="horizontal")
        y_scroll = ctk.CTkScrollbar(self.table_frame, orientation="vertical")
        
        # Create table with new bindings
        self.table = tk.ttk.Treeview(self.table_frame)
        self.table.bind('<Double-1>', self._on_double_click)
        
        # Create entry widget for editing (initially hidden)
        self.edit_entry = ctk.CTkEntry(self.table_frame, width=100, height=25)
        self.edit_entry.bind('<Return>', self._on_entry_return)
        self.edit_entry.bind('<Escape>', lambda e: self._cancel_edit())
        
        # Configure scrollbar commands
        x_scroll.configure(command=self.table.xview)
        y_scroll.configure(command=self.table.yview)
        self.table.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        
        # Grid layout instead of pack for better control
        self.table.grid(row=0, column=0, sticky="nsew")
        x_scroll.grid(row=1, column=0, sticky="ew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights for table_frame
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._edit_selected)
        self.context_menu.add_command(label="Delete", command=self._delete_selected_rows)
        
        # Bind right-click
        self.table.bind("<Button-3>", self._show_context_menu)
    
    def _import_csv(self):
        """Import CSV file"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                # Create data directory if it doesn't exist
                data_dir = "./assets_static/data"
                os.makedirs(data_dir, exist_ok=True)
                
                # Copy file to data directory
                filename = os.path.basename(file_path)
                destination = os.path.join(data_dir, filename)
                shutil.copy2(file_path, destination)
                
                # Load the CSV
                self._load_csv(destination)
                
                # Refresh the CSV list and select the new file
                self._load_csv_list()
                
                # Update the dropdown to show the new file
                for widget in self.dropdown_frame.winfo_children():
                    if isinstance(widget, ctk.CTkOptionMenu):
                        widget.set(filename)
                
                messagebox.showinfo("Success", "CSV imported successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
    
    def _load_csv(self, file_path):
        """Load CSV data into table"""
        try:
            self.data = pd.read_csv(file_path)
            self.current_csv = file_path
            
            # Clear existing table
            self.table.delete(*self.table.get_children())
            
            # Set columns with No. as first column
            columns = ["No."] + list(self.data.columns)
            self.table["columns"] = columns
            self.table["show"] = "headings"
            
            # Configure columns
            self.table.heading("No.", text="No.")
            self.table.column("No.", width=50, anchor="center")
            
            for column in self.data.columns:
                self.table.heading(column, text=column)
                self.table.column(column, width=100)
            
            # Add data with row numbers
            for idx, row in self.data.iterrows():
                self.table.insert("", "end", values=[idx + 1] + list(row))
            
            # Update records count
            self._update_records_count()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def _update_records_count(self):
        """Update the records count label"""
        count = len(self.table.get_children())
        self.records_label.configure(text=f"Total Records: {count}")

    def _delete_selected_rows(self):
        """Delete selected rows from table"""
        if not self.table.selection():
            messagebox.showwarning("Warning", "Please select rows to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected rows?"):
            # Delete selected items
            for item in self.table.selection():
                self.table.delete(item)
            
            # Renumber remaining rows
            self._renumber_rows()
            
            # Update records count
            self._update_records_count()

    def _renumber_rows(self):
        """Renumber all rows after deletion"""
        items = self.table.get_children()
        for idx, item in enumerate(items, 1):
            values = list(self.table.item(item)["values"])
            values[0] = idx  # Update row number
            self.table.item(item, values=values)

    def _add_row(self):
        """Add new row to table"""
        if self.data is None:
            messagebox.showwarning("Warning", "Please load a CSV file first")
            return
            
        # Create empty row with row number
        new_row = [len(self.table.get_children()) + 1] + [""] * len(self.data.columns)
        item = self.table.insert("", "end", values=new_row)
        self._update_records_count()
        
        # Optional: Start editing the first cell of the new row
        self.table.selection_set(item)
        self.table.focus(item)
    
    def _add_column(self):
        """Add new column to table"""
        if self.data is None:
            messagebox.showwarning("Warning", "Please load a CSV file first")
            return
            
        # Show dialog for column name
        dialog = ctk.CTkInputDialog(
            text="Enter column name:",
            title="Add Column"
        )
        column_name = dialog.get_input()
        
        if column_name:
            # Add column to table
            self.table["columns"] = list(self.table["columns"]) + [column_name]
            self.table.heading(column_name, text=column_name)
            self.table.column(column_name, width=100)
            
            # Update all rows with empty value for new column
            for item in self.table.get_children():
                values = list(self.table.item(item)["values"])
                values.append("")
                self.table.item(item, values=values)
    
    def _save_changes(self):
        """Save changes to CSV file"""
        if not self.current_csv:
            messagebox.showwarning("Warning", "No CSV file loaded")
            return
            
        try:
            # Get data from table
            data = []
            columns = list(self.table["columns"])
            columns.remove("No.")  # Remove No. column before saving
            
            for item in self.table.get_children():
                values = list(self.table.item(item)["values"])
                values.pop(0)  # Remove the No. column value
                data.append(values)
            
            # Create DataFrame and save
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(self.current_csv, index=False)
            
            messagebox.showinfo("Success", "Changes saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
    def _load_csv_list(self):
        """Load list of CSV files and display in dropdown"""
        try:
            # Get list of CSV files from controller
            csv_files = self.controller.get_csv_list()
            
            # Clear existing dropdown if it exists
            for widget in self.dropdown_frame.winfo_children():
                if isinstance(widget, ctk.CTkOptionMenu):
                    widget.destroy()
            
            # Create dropdown
            if csv_files:
                self.csv_var = ctk.StringVar(value=csv_files[0])
                dropdown = ctk.CTkOptionMenu(
                    self.dropdown_frame,
                    values=csv_files,
                    variable=self.csv_var,
                    command=self._on_csv_selected
                )
                dropdown.pack(side="left", padx=5)
                
                # Load first CSV file if no file is currently loaded
                if not self.current_csv and csv_files:
                    self._load_csv(os.path.join("./assets_static/data", csv_files[0]))
            else:
                # Show message if no CSV files
                ctk.CTkLabel(
                    self.dropdown_frame,
                    text="No CSV files found"
                ).pack(side="left", padx=5)
                
        except Exception as e:
            print(f"Error loading CSV list: {e}")
            messagebox.showerror("Error", f"Failed to load CSV list: {str(e)}")

    def _on_csv_selected(self, choice):
        """Handle CSV selection from dropdown"""
        try:
            file_path = os.path.join("./assets_static/data", choice)
            self._load_csv(file_path)
        except Exception as e:
            print(f"Error selecting CSV: {e}")
            messagebox.showerror("Error", f"Failed to load selected CSV: {str(e)}")

    def _on_double_click(self, event):
        """Handle double click on table cell"""
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        # Get column and item
        column = self.table.identify_column(event.x)
        item = self.table.identify_row(event.y)
        
        if not item or not column:
            return
            
        # Don't allow editing the No. column
        if column == "#1":  # No. column
            return
            
        # Get column name and current value
        column_id = self.table["columns"][int(column.replace("#", "")) - 1]
        current_value = self.table.item(item)["values"][int(column.replace("#", "")) - 1]
        
        # Get cell bbox
        x, y, w, h = self.table.bbox(item, column)
        
        # Position entry widget (without setting width/height)
        self.edit_entry.place(x=x, y=y)
        self.edit_entry.configure(width=w)  # Update width if needed
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # Store current editing info
        self._editing = {
            "item": item,
            "column": column,
            "column_id": column_id
        }

    def _on_entry_return(self, event):
        """Handle entry widget return key"""
        if not hasattr(self, '_editing'):
            return
            
        # Get new value
        new_value = self.edit_entry.get()
        
        # Update table
        item = self._editing["item"]
        column_idx = int(self._editing["column"].replace("#", "")) - 1
        
        # Get current values and update the specific column
        values = list(self.table.item(item)["values"])
        values[column_idx] = new_value
        
        # Update the table
        self.table.item(item, values=values)
        
        # Clean up
        self._cancel_edit()

    def _cancel_edit(self):
        """Cancel editing and hide entry widget"""
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.place_forget()
        if hasattr(self, '_editing'):
            del self._editing
        self.table.focus()

    def _show_context_menu(self, event):
        """Show context menu on right click"""
        item = self.table.identify_row(event.y)
        if item:
            self.table.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _edit_selected(self):
        """Start editing the selected cell"""
        selected = self.table.selection()
        if not selected:
            return
        
        item = selected[0]
        column = "#2"  # Start with first editable column
        
        # Simulate double click on the cell
        bbox = self.table.bbox(item, column)
        if bbox:
            x = bbox[0] + 5
            y = bbox[1] + 5
            self._on_double_click(type('Event', (), {'x': x, 'y': y})())

    def _delete_csv_file(self):
        """Delete the currently selected CSV file"""
        if not self.current_csv:
            messagebox.showwarning("Warning", "No CSV file selected")
            return
        
        filename = os.path.basename(self.current_csv)
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?\nThis action cannot be undone."):
            try:
                # Delete the file
                os.remove(self.current_csv)
                
                # Clear the table
                self.table.delete(*self.table.get_children())
                self.current_csv = None
                self.data = None
                
                # Update the CSV list
                self._load_csv_list()
                
                # Update records count
                self._update_records_count()
                
                messagebox.showinfo("Success", f"CSV file '{filename}' deleted successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete CSV file: {str(e)}")