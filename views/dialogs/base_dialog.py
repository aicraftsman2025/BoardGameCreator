import customtkinter as ctk

class BaseDialog:
    def __init__(self, parent, element, title="Edit Element"):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.element = element
        self.properties = element.get('properties', {}).copy()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create UI
        self._create_ui()
        
        # Center dialog on parent
        self.center_on_parent(parent)
    
    def center_on_parent(self, parent):
        """Center the dialog on its parent window"""
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """Override this method to create the dialog's UI"""
        raise NotImplementedError
    
    def _save_and_close(self):
        """Override this method to handle saving"""
        raise NotImplementedError 