import customtkinter as ctk
from PIL import Image, ImageTk
import io
import base64
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from views.component_editor.component_editor import ComponentEditor

class ComponentsManager(ctk.CTkFrame):
    def __init__(self, parent, component_controller, template_controller):
        super().__init__(parent)
        self.component_controller = component_controller
        self.template_controller = template_controller
        
        # Get project_id from global variable
        from views.project_view import project_id
        self.project_id = project_id
        
        # Pagination variables
        self.page = 1
        self.items_per_page = 10
        self.total_pages = 1
        
        self._create_ui()
        self._load_components()
    
    def _create_ui(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Components Manager",
            font=("Helvetica", 20, "bold")
        )
        title.pack(side="left", padx=10, pady=5)
        
        # Components list frame
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Pagination frame
        pagination_frame = ctk.CTkFrame(self)
        pagination_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        pagination_frame.grid_columnconfigure((0,1,2,3,4), weight=1)  # Even distribution
        
        # Items per page selector
        items_frame = ctk.CTkFrame(pagination_frame)
        items_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(items_frame, text="Items per page:").pack(side="left", padx=5)
        self.items_per_page_var = ctk.StringVar(value="10")
        items_dropdown = ctk.CTkOptionMenu(
            items_frame,
            values=["5", "10", "20", "50"],
            variable=self.items_per_page_var,
            command=self._on_items_per_page_change
        )
        items_dropdown.pack(side="left", padx=5)
        
        # Pagination controls
        controls_frame = ctk.CTkFrame(pagination_frame)
        controls_frame.pack(side="right", padx=10)
        
        self.first_btn = ctk.CTkButton(
            controls_frame,
            text="<<",
            width=30,
            command=self._first_page
        )
        self.first_btn.pack(side="left", padx=2)
        
        self.prev_btn = ctk.CTkButton(
            controls_frame,
            text="<",
            width=30,
            command=self._prev_page
        )
        self.prev_btn.pack(side="left", padx=2)
        
        self.page_var = ctk.StringVar(value="1")
        self.page_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.page_var,
            width=50,
            justify="center"
        )
        self.page_entry.pack(side="left", padx=5)
        self.page_entry.bind('<Return>', self._on_page_entry)
        
        self.total_pages_label = ctk.CTkLabel(
            controls_frame,
            text="of 1"
        )
        self.total_pages_label.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            controls_frame,
            text=">",
            width=30,
            command=self._next_page
        )
        self.next_btn.pack(side="left", padx=2)
        
        self.last_btn = ctk.CTkButton(
            controls_frame,
            text=">>",
            width=30,
            command=self._last_page
        )
        self.last_btn.pack(side="left", padx=2)
    
    def _load_components(self):
        """Load and display components for current page"""
        try:
            # Clear existing components
            for widget in self.list_frame.winfo_children():
                widget.destroy()
            
            # Get all components for the current project
            self.all_components = self.component_controller.get_project_components(self.project_id)
            
            # Calculate total pages
            total_components = len(self.all_components)
            items_per_page = int(self.items_per_page_var.get())
            self.total_pages = max(1, (total_components + items_per_page - 1) // items_per_page)
            
            # Ensure current page is valid
            self.page = min(max(1, self.page), self.total_pages)
            
            # Update UI
            self.page_var.set(str(self.page))
            self.total_pages_label.configure(text=f"of {self.total_pages}")
            
            # Update button states
            self._update_pagination_controls()
            
            # Calculate slice indices
            start_idx = (self.page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            
            # Get components for current page
            page_components = self.all_components[start_idx:end_idx]
            
            # Create component cards
            for component in page_components:
                self._create_component_card(component)
                
            # Show no components message if needed
            if not page_components:
                no_components_label = ctk.CTkLabel(
                    self.list_frame,
                    text="No components found",
                    font=("Helvetica", 14)
                )
                no_components_label.pack(pady=20)
                
        except Exception as e:
            print(f"Error loading components: {e}")
            self.show_message("Error", f"Failed to load components: {str(e)}")
    
    def _update_pagination_controls(self):
        """Update pagination controls state"""
        # Update button states
        self.first_btn.configure(state="normal" if self.page > 1 else "disabled")
        self.prev_btn.configure(state="normal" if self.page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.page < self.total_pages else "disabled")
        self.last_btn.configure(state="normal" if self.page < self.total_pages else "disabled")
    
    def _on_items_per_page_change(self, value):
        """Handle items per page change"""
        self.page = 1  # Reset to first page
        self._load_components()
    
    def _on_page_entry(self, event):
        """Handle manual page number entry"""
        try:
            new_page = int(self.page_var.get())
            if 1 <= new_page <= self.total_pages:
                self.page = new_page
                self._load_components()
            else:
                self.page_var.set(str(self.page))  # Reset to current page
        except ValueError:
            self.page_var.set(str(self.page))  # Reset to current page
    
    def _first_page(self):
        """Go to first page"""
        if self.page != 1:
            self.page = 1
            self._load_components()
    
    def _prev_page(self):
        """Go to previous page"""
        if self.page > 1:
            self.page -= 1
            self._load_components()
    
    def _next_page(self):
        """Go to next page"""
        if self.page < self.total_pages:
            self.page += 1
            self._load_components()
    
    def _last_page(self):
        """Go to last page"""
        if self.page != self.total_pages:
            self.page = self.total_pages
            self._load_components()
    
    def _create_component_card(self, component):
        # Card frame
        card = ctk.CTkFrame(self.list_frame)
        card.pack(fill="x", padx=5, pady=5)
        
        # Info frame (middle)
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Component name
        name_label = ctk.CTkLabel(
            info_frame,
            text=component.name,  # Use component.name instead of dict access
            font=("Helvetica", 16, "bold")
        )
        name_label.pack(anchor="w", pady=5)
        
        # Component type
        type_label = ctk.CTkLabel(
            info_frame,
            text=f"Type: {component.type}"  # Add component type
        )
        type_label.pack(anchor="w", pady=2)
        
        # Actions frame (right side)
        actions_frame = ctk.CTkFrame(card)
        actions_frame.pack(side="right", padx=10, pady=10)
        
        # Action buttons
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=lambda: self._edit_component(component)
        )
        edit_btn.pack(pady=2)
        
        # export_btn = ctk.CTkButton(
        #     actions_frame,
        #     text="Export",
        #     command=lambda: self._export_component(component)
        # )
        # export_btn.pack(pady=2)
        
        template_btn = ctk.CTkButton(
            actions_frame,
            text="Make Template",
            command=lambda: self._make_template(component)
        )
        template_btn.pack(pady=2)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            fg_color="red",
            command=lambda: self._delete_component(component)
        )
        delete_btn.pack(pady=2)
    
    def _edit_component(self, component):
        """Handle editing a component"""
        try:
            # Switch to component editor view
            self.master.master.show_view("component")
            
            # Get the current component editor instance
            component_editor = self.master.master.current_view
            
            # Load component data from database
            component_data = self.component_controller.get_component_by_id(component.component_id)
            if component_data:
                print(f"Loading component data: {component_data}")  # Debug print
                
                # Create data dictionary for component editor
                editor_data = {
                    'id': component_data.component_id,
                    'name': component_data.name,
                    'type': component_data.type,
                    'properties': component_data.properties
                }
                
                # Load the component into the editor
                component_editor.load_component(editor_data)  # Using the existing load_data method
            else:
                messagebox.showerror("Error", "Failed to load component data")
                
        except Exception as e:
            print(f"Error editing component: {e}")
            messagebox.showerror("Error", f"Failed to edit component: {str(e)}")
    
    def _export_component(self, component):
        # Show file dialog and export component
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.component_controller.export_component(component.component_id, filename)  # Use component_id attribute
    
    def _make_template(self, component):
        # Create template from component
        self.template_controller.create_from_component(component.component_id)  # Use component_id attribute
        self.show_message("Success", "Template created successfully!")
    
    def _delete_component(self, component):
        # Show confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("300x150")
        
        # Warning message
        ctk.CTkLabel(
            dialog,
            text="Are you sure you want to delete this component?",
            wraplength=250
        ).pack(pady=20)
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def confirm_delete():
            self.component_controller.delete_component(component.component_id)
            self._load_components()
            dialog.destroy()
        
        # Yes button
        ctk.CTkButton(
            btn_frame,
            text="Yes",
            command=confirm_delete,
            fg_color="red",
            hover_color="#8B0000"
        ).pack(side="left", padx=5)
        
        # No button
        ctk.CTkButton(
            btn_frame,
            text="No",
            command=dialog.destroy
        ).pack(side="right", padx=5)
    
    def show_message(self, title, message):
        """Show message dialog"""
        if title.lower() == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)