import customtkinter as ctk
from tkinter import filedialog
import json
import webbrowser

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
        
        # Export Settings Tab (Paths)
        export_tab = self.tabview.add("Export")
        self._create_export_settings(export_tab)
        
        # About Tab
        about_tab = self.tabview.add("About")
        self._create_about_tab(about_tab)
    
    def _create_export_settings(self, parent):
        paths_frame = ctk.CTkFrame(parent)
        paths_frame.pack(fill="x", padx=10, pady=5)
        
        # Assets Directory
        ctk.CTkLabel(
            paths_frame,
            text="Assets Directory",
            font=("Helvetica", 14, "bold")
        ).pack(anchor="w", pady=5)
        
        path_container = ctk.CTkFrame(paths_frame)
        path_container.pack(fill="x", pady=5)
        
        self.assets_path = ctk.CTkEntry(
            path_container,
            placeholder_text="Select assets directory...",
            width=300
        )
        self.assets_path.pack(side="left", padx=5)
        
        ctk.CTkButton(
            path_container,
            text="Browse",
            command=self._choose_assets_path,
            width=100
        ).pack(side="left", padx=5)
    
    def _create_about_tab(self, parent):
        about_frame = ctk.CTkFrame(parent)
        about_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # App Title
        ctk.CTkLabel(
            about_frame,
            text="Board Game Creator",
            font=("Helvetica", 20, "bold")
        ).pack(pady=10)
        
        # Version
        ctk.CTkLabel(
            about_frame,
            text="Version 1.0.0",
            font=("Helvetica", 12)
        ).pack(pady=5)
        
        # Description
        description = (
            "A powerful tool for designing and creating board game components.\n"
            "Create cards, tokens, boards, and export them to PDF format.\n\n"
            "Special thanks to:\n"
            "• ChatGPT - For the initial concept and design ideas\n"
            "• Claude AI - For implementation guidance and code optimization"
        )
        ctk.CTkLabel(
            about_frame,
            text=description,
            font=("Helvetica", 12),
            wraplength=400
        ).pack(pady=20)
        
        # GitHub Link
        github_button = ctk.CTkButton(
            about_frame,
            text="View on GitHub",
            command=lambda: webbrowser.open("https://github.com/haruthuc/boardgamedesigner")
        )
        github_button.pack(pady=10)
        
        # Copyright
        ctk.CTkLabel(
            about_frame,
            text="© 2024 chatGPT & Claude AI and Thuc Huynh. All rights reserved.",
            font=("Helvetica", 10)
        ).pack(pady=20)
    
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
    
    def _choose_assets_path(self):
        path = filedialog.askdirectory(
            title="Select Assets Directory"
        )
        if path:
            self.assets_path.delete(0, 'end')
            self.assets_path.insert(0, path)
    
    def load_settings(self):
        settings = self.controller.get_settings()
        if settings:
            # Load Paths only
            self.assets_path.delete(0, 'end')
            self.assets_path.insert(0, settings.get('paths', {}).get('assets', 'assets'))
    
    def save_settings(self):
        settings = {
            'paths': {
                'assets': self.assets_path.get() or 'assets'
            }
        }
        
        success = self.controller.save_settings(settings)
        if success:
            # Update asset controller path
            self.controller.update_asset_path(settings['paths']['assets'])