from abc import ABC, abstractmethod
import tkinter as tk
import customtkinter as ctk

class ConfigWidget:
    def __init__(self, parent, name, label, widget_type, **kwargs):
        self.name = name
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(
            self.frame,
            text=label
        ).pack(side="left", padx=5)
        
        self.widget = widget_type(self.frame, **kwargs)
        self.widget.pack(side="right", padx=5)
    
    def get(self):
        return self.widget.get()

class BaseScript(ABC):
    def __init__(self):
        self.dialog = None
        self.output = None
    
    @abstractmethod
    def get_config_widgets(self, parent):
        """Return list of configuration widgets specific to this script"""
        pass
    
    @abstractmethod
    def run_script(self, config):
        """Execute the script with the given configuration"""
        pass
    
    def create_dialog(self, parent):
        """Create the configuration dialog"""
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(self.get_title())
        self.dialog.geometry("800x600")
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Config section
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", padx=5, pady=5)
        
        # Get script-specific config widgets
        self.config_widgets = self.get_config_widgets(config_frame)
        
        # Output section
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.output = ctk.CTkTextbox(output_frame)
        self.output.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Generate",
            command=self._run_with_config
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side="right", padx=5)
    
    def _run_with_config(self):
        """Collect config values and run the script"""
        config = {widget.name: widget.get() for widget in self.config_widgets}
        self.run_script(config)
    
    @abstractmethod
    def get_title(self):
        """Return the script title"""
        pass 