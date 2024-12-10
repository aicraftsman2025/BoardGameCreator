import customtkinter as ctk
from typing import Dict
import json

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Create main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_settings_tabs()
        self._create_footer()
        
        # Load settings
        self.load_settings()
    
    def _create_header(self):
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        title = ctk.CTkLabel(
            header,
            text="Settings",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=10)
    
    def _create_settings_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # General Settings Tab
        general_tab = self.tabview.add("General")
        self._create_general_settings(general_tab)
        
        # Export Settings Tab
        export_tab = self.tabview.add("Export")
        self._create_export_settings(export_tab)
        
        # Advanced Settings Tab
        advanced_tab = self.tabview.add("Advanced")
        self._create_advanced_settings(advanced_tab)
    
    def _create_general_settings(self, parent):
        # Default Sizes Frame
        sizes_frame = ctk.CTkFrame(parent)
        sizes_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            sizes_frame,
            text="Default Component Sizes (mm)",
            font=("Helvetica", 14, "bold")
        ).pack(anchor="w", pady=5)
        
        # Card Size
        self._create_size_inputs(sizes_frame, "card", "Cards")
        self._create_size_inputs(sizes_frame, "token", "Tokens")
        self._create_size_inputs(sizes_frame, "board", "Boards")
    
    def _create_export_settings(self, parent):
        export_frame = ctk.CTkFrame(parent)
        export_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            export_frame,
            text="Export Settings",
            font=("Helvetica", 14, "bold")
        ).pack(anchor="w", pady=5)
        
        # Page Size
        self.page_size_var = ctk.StringVar()
        ctk.CTkLabel(
            export_frame,
            text="Default Page Size:"
        ).pack(anchor="w", padx=5)
        
        page_size = ctk.CTkOptionMenu(
            export_frame,
            values=["A4", "A3", "Letter", "Legal"],
            variable=self.page_size_var
        )
        page_size.pack(anchor="w", padx=5, pady=5)
        
        # Export Quality
        self.quality_var = ctk.StringVar()
        ctk.CTkLabel(
            export_frame,
            text="Export Quality:"
        ).pack(anchor="w", padx=5)
        
        quality = ctk.CTkOptionMenu(
            export_frame,
            values=["Draft", "Standard", "High"],
            variable=self.quality_var
        )
        quality.pack(anchor="w", padx=5, pady=5)
    
    def _create_advanced_settings(self, parent):
        advanced_frame = ctk.CTkFrame(parent)
        advanced_frame.pack(fill="x", padx=10, pady=5)
        
        # Autosave Settings
        ctk.CTkLabel(
            advanced_frame,
            text="Autosave",
            font=("Helvetica", 14, "bold")
        ).pack(anchor="w", pady=5)
        
        self.autosave_var = ctk.BooleanVar()
        autosave_switch = ctk.CTkSwitch(
            advanced_frame,
            text="Enable Autosave",
            variable=self.autosave_var,
            command=self._on_autosave_change
        )
        autosave_switch.pack(anchor="w", padx=5, pady=5)
        
        # Autosave Interval
        self.interval_var = ctk.StringVar()
        ctk.CTkLabel(
            advanced_frame,
            text="Autosave Interval (minutes):"
        ).pack(anchor="w", padx=5)
        
        interval_entry = ctk.CTkEntry(
            advanced_frame,
            textvariable=self.interval_var,
            width=100
        )
        interval_entry.pack(anchor="w", padx=5, pady=5)
    
    def _create_footer(self):
        footer = ctk.CTkFrame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Save Button
        save_btn = ctk.CTkButton(
            footer,
            text="Save Changes",
            command=self.save_settings
        )
        save_btn.pack(side="right", padx=5, pady=5)
        
        # Reset Button
        reset_btn = ctk.CTkButton(
            footer,
            text="Reset to Default",
            fg_color="red",
            command=self.reset_settings
        )
        reset_btn.pack(side="right", padx=5, pady=5)
    
    def _create_size_inputs(self, parent, key: str, label: str):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(frame, text=f"{label}:").pack(side="left", padx=5)
        
        setattr(self, f"{key}_width", ctk.CTkEntry(frame, width=50))
        getattr(self, f"{key}_width").pack(side="left", padx=5)
        
        ctk.CTkLabel(frame, text="x").pack(side="left")
        
        setattr(self, f"{key}_height", ctk.CTkEntry(frame, width=50))
        getattr(self, f"{key}_height").pack(side="left", padx=5)
        
        ctk.CTkLabel(frame, text="mm").pack(side="left")
    
    def load_settings(self):
        settings = self.controller.get_settings()
        if settings:
            # Load size settings
            for component in ['card', 'token', 'board']:
                if sizes := settings['default_sizes'].get(component):
                    getattr(self, f"{component}_width").insert(0, str(sizes['width']))
                    getattr(self, f"{component}_height").insert(0, str(sizes['height']))
            
            # Load export settings
            self.page_size_var.set(settings['export']['page_size'])
            self.quality_var.set(settings['export']['quality'].capitalize())
            
            # Load advanced settings
            self.autosave_var.set(settings['autosave']['enabled'])
            self.interval_var.set(str(settings['autosave']['interval']))
    
    def save_settings(self):
        def safe_int(value, default=0):
            try:
                return int(value) if value.strip() else default
            except ValueError:
                return default

        settings = {
            'default_sizes': {
                component: {
                    'width': safe_int(getattr(self, f"{component}_width").get()),
                    'height': safe_int(getattr(self, f"{component}_height").get())
                }
                for component in ['card', 'token', 'board']
            },
            'export': {
                'page_size': self.page_size_var.get(),
                'quality': self.quality_var.get().lower()
            },
            'autosave': {
                'enabled': self.autosave_var.get(),
                'interval': safe_int(self.interval_var.get(), 5)  # default 5 minutes
            }
        }
        
        self.controller.save_settings(settings)
    
    def reset_settings(self):
        if self.show_confirm_dialog():
            settings = self.controller.get_default_settings()
            self.controller.save_settings(settings)
            self.load_settings()
    
    def _on_autosave_change(self):
        # Enable/disable interval entry based on autosave switch
        pass
    
    def _show_color_picker(self):
        # Implement color picker dialog
        pass
    
    def show_confirm_dialog(self) -> bool:
        dialog = ctk.CTkInputDialog(
            text="Type 'RESET' to confirm resetting all settings:",
            title="Confirm Reset"
        )
        return dialog.get_input() == "RESET"