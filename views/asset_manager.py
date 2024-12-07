import customtkinter as ctk
from tkinter import filedialog
import os
from PIL import Image
from typing import List, Optional

class AssetManager(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_assets = set()
        self.current_folder = None
        self.items_per_page = 12
        self.current_page = 1
        self.thumbnail_cache = {}
        
        self._create_toolbar()
        self._create_folder_tree()
        self._create_asset_grid()
        
        # Debounce resize event
        self._resize_timer = None
        self.bind('<Configure>', self._debounced_resize)
        
        # Load initial assets
        self.load_assets()
    
    def _create_toolbar(self):
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        
        # Import Button
        self.import_btn = ctk.CTkButton(
            self.toolbar,
            text="Import Assets",
            command=self.import_assets
        )
        self.import_btn.pack(side="left", padx=5)
        
        # New Folder Button
        self.new_folder_btn = ctk.CTkButton(
            self.toolbar,
            text="New Folder",
            command=self.create_folder
        )
        self.new_folder_btn.pack(side="left", padx=5)
        
        # Delete Selected Button
        self.delete_selected_btn = ctk.CTkButton(
            self.toolbar,
            text="Delete Selected",
            fg_color="red",
            command=self.delete_selected
        )
        self.delete_selected_btn.pack(side="left", padx=5)
        
        # Search Entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_assets())
        self.search_entry = ctk.CTkEntry(
            self.toolbar,
            placeholder_text="Search assets...",
            textvariable=self.search_var,
            width=200
        )
        self.search_entry.pack(side="right", padx=5)
    
    def _create_folder_tree(self):
        # Create folder navigation panel
        self.folder_frame = ctk.CTkFrame(self, width=200)
        self.folder_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Folder Tree
        self.folder_tree = ctk.CTkScrollableFrame(self.folder_frame)
        self.folder_tree.pack(fill="both", expand=True)
        
        # Root folder
        self.root_folder = ctk.CTkButton(
            self.folder_tree,
            text="All Assets",
            command=lambda: self.select_folder(None)
        )
        self.root_folder.pack(fill="x", padx=2, pady=2)
        
        self.load_folders()
    
    def _create_asset_grid(self):
        # Main grid container
        self.grid_container = ctk.CTkFrame(self)
        self.grid_container.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Asset grid
        self.grid_frame = ctk.CTkScrollableFrame(self.grid_container)
        self.grid_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid weights for flexibility
        self.grid_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Pagination at the bottom of grid container
        self._create_pagination()
        
        # Cache for thumbnails
        self.thumbnail_cache = {}
    
    def _create_pagination(self):
        self.pagination_frame = ctk.CTkFrame(self.grid_container)
        self.pagination_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # Previous page button
        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text="←",
            width=30,
            command=self.previous_page
        )
        self.prev_btn.pack(side="left", padx=5)
        
        # Page indicator
        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Page 1"
        )
        self.page_label.pack(side="left", padx=5)
        
        # Next page button
        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="→",
            width=30,
            command=self.next_page
        )
        self.next_btn.pack(side="left", padx=5)
    
    def create_folder(self):
        dialog = ctk.CTkInputDialog(
            text="Enter folder name:",
            title="New Folder"
        )
        folder_name = dialog.get_input()
        if folder_name:
            try:
                self.controller.create_asset_folder(folder_name, parent_id=self.current_folder)
                self.load_folders()
                self.show_message("Success", f"Folder '{folder_name}' created successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to create folder: {str(e)}")
    
    def load_folders(self):
        # Clear existing folders
        for widget in self.folder_tree.winfo_children():
            if widget != self.root_folder:
                widget.destroy()
        
        # Configure root folder
        self.root_folder.configure(
            fg_color=("gray75", "gray25") if self.current_folder is None else "transparent",
            text_color="black" if self.current_folder is None else "white",
            hover_color=("gray65", "gray35")
        )
        
        # Load folders from controller
        folders = self.controller.get_asset_folders()
        for folder_name in folders:
            folder_frame = ctk.CTkFrame(self.folder_tree)
            folder_frame.pack(fill="x", padx=2, pady=2)
            
            # Folder button
            folder_btn = ctk.CTkButton(
                folder_frame,
                text=folder_name,
                command=lambda fname=folder_name: self.select_folder(fname),
                fg_color="transparent" if folder_name != self.current_folder else ("gray75", "gray25"),
                text_color="white" if folder_name != self.current_folder else "black",
                hover_color=("gray65", "gray35")
            )
            folder_btn.pack(side="left", fill="x", expand=True)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                folder_frame,
                text="×",
                width=30,
                fg_color="red",
                hover_color="#AA0000",
                command=lambda fname=folder_name: self.delete_folder(fname)
            )
            delete_btn.pack(side="right", padx=2)
    
    def select_folder(self, folder_name: Optional[str]):
        """Select a folder and load its assets"""
        self.current_folder = folder_name
        self.current_page = 1
        self.selected_assets.clear()
        self.clear_thumbnail_cache()
        
        self._update_folder_selection()
        self.load_assets()
    
    def _update_folder_selection(self):
        """Update the visual appearance of selected folder"""
        # Reset root folder appearance
        self.root_folder.configure(
            fg_color=("gray75", "gray25") if self.current_folder is None else "transparent",
            text_color="black" if self.current_folder is None else "white"
        )
        
        # Update other folders
        for widget in self.folder_tree.winfo_children():
            if isinstance(widget, ctk.CTkFrame):  # For folder frames
                folder_btn = widget.winfo_children()[0]  # Get the folder button
                is_selected = folder_btn.cget("text") == str(self.current_folder)
                folder_btn.configure(
                    fg_color=("gray75", "gray25") if is_selected else "transparent",
                    text_color="yellow" if is_selected else "white"
                )
    
    def load_assets(self):
        # Clear existing assets
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Load assets from controller with pagination and folder filtering
        start_idx = (self.current_page - 1) * self.items_per_page
        assets = self.controller.get_all_assets(self.current_folder)
        
        if not assets:
            label = ctk.CTkLabel(
                self.grid_frame,
                text="No assets found in this folder",
                font=("Arial", 14)
            )
            label.pack(pady=20)
            return
        
        # Fixed number of columns for better performance
        num_columns = 3
        
        # Create asset thumbnails
        assets_to_show = assets[start_idx:start_idx + self.items_per_page]
        for i, asset in enumerate(assets_to_show):
            row = i // num_columns
            col = i % num_columns
            self.create_asset_thumbnail(asset, row, col)
        
        # Update pagination
        total_assets = len(assets)
        total_pages = max(1, (total_assets + self.items_per_page - 1) // self.items_per_page)
        
        self.page_label.configure(text=f"Page {self.current_page} of {total_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")
    
    def create_asset_thumbnail(self, asset, row, col):
        # Add more detailed debug prints
        print(f"\nAsset Details:")
        print(f"- Name: {asset.name}")
        print(f"- File Path: {asset.file_path}")
        print(f"- File Type: {asset.file_type}")
        print(f"- File Exists: {os.path.exists(asset.file_path)}")
        
        # Add debug print
        print(f"Creating thumbnail for asset: {asset.name}")
        print(f"Preview image available: {asset.preview_image is not None}")
        
        # Create a frame for the asset with flexible width
        frame = ctk.CTkFrame(self.grid_frame)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        
        # Selection checkbox at the top
        checkbox = ctk.CTkCheckBox(
            frame,
            text="",
            command=lambda a=asset: self.toggle_asset_selection(a)
        )
        checkbox.grid(row=0, column=0, sticky="nw", padx=5, pady=2)
        
        # Thumbnail image
        if asset.id in self.thumbnail_cache:
            preview_image = self.thumbnail_cache[asset.id]
        else:
            preview_image = asset.preview_image
            if preview_image:
                self.thumbnail_cache[asset.id] = preview_image
        
        if preview_image:
            print(f"Thumbnail dimensions: {preview_image._size}")
            thumbnail = ctk.CTkLabel(
                frame,
                text="",
                image=preview_image
            )
        else:
            print(f"No preview image for {asset.name}, using text fallback")
            thumbnail = ctk.CTkLabel(
                frame,
                text=asset.file_type.upper(),
                width=100,
                height=100
            )
        thumbnail.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        
        # Asset name label
        name_label = ctk.CTkLabel(
            frame,
            text=asset.name,
            wraplength=150
        )
        name_label.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
    
    def toggle_asset_selection(self, asset):
        if asset.id in self.selected_assets:
            self.selected_assets.remove(asset.id)
        else:
            self.selected_assets.add(asset.id)
        
        # Update delete button state
        self.delete_selected_btn.configure(
            state="normal" if self.selected_assets else "disabled"
        )
    
    def delete_selected(self):
        if not self.selected_assets:
            return
        
        # Confirm deletion
        dialog = ctk.CTkInputDialog(
            text=f"Delete {len(self.selected_assets)} items? Type 'DELETE' to confirm:",
            title="Confirm Deletion"
        )
        if dialog.get_input() == "DELETE":
            deleted_count = 0
            
            # Delete selected items
            for item_id in self.selected_assets:
                try:
                    if isinstance(item_id, str):  # It's a folder
                        if self.controller.delete_folder(item_id):
                            deleted_count += 1
                    else:  # It's an asset
                        if self.controller.delete_asset(item_id):
                            deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete item {item_id}: {e}")
            
            self.selected_assets.clear()
            self.load_folders()  # Refresh folder list
            self.load_assets()   # Refresh asset grid
            
            if deleted_count > 0:
                self.show_message("Success", f"Successfully deleted {deleted_count} items.")
    
    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_assets()
    
    def next_page(self):
        total_assets = self.controller.get_assets_count()
        total_pages = (total_assets + self.items_per_page - 1) // self.items_per_page
        
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_assets()
    
    def import_assets(self):
        files = filedialog.askopenfilenames(
            title="Select Assets",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            imported_count = 0
            for file in files:
                try:
                    self.controller.import_asset(file, self.current_folder)
                    imported_count += 1
                except Exception as e:
                    print(f"Failed to import {file}: {e}")
            
            self.load_assets()
            if imported_count > 0:
                self.show_message("Success", f"Successfully imported {imported_count} assets.")
    
    def filter_assets(self):
        # Filter assets based on search text
        pass 

    def delete_folder(self, folder_name: str):
        """Delete a folder after confirmation"""
        dialog = ctk.CTkInputDialog(
            text=f"Delete folder '{folder_name}'? Type 'DELETE' to confirm:",
            title="Confirm Folder Deletion"
        )
        if dialog.get_input() == "DELETE":
            if self.controller.delete_folder(folder_name):
                if self.current_folder == folder_name:
                    self.select_folder(None)  # Reset to root if current folder is deleted
                self.load_folders()
                self.show_message("Success", f"Folder '{folder_name}' deleted successfully!")
    
    def show_message(self, title: str, message: str):
        """Show a simple message dialog without input field"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self)  # Set to be on top of the main window
        
        # Center the dialog
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - 300) // 2
        y = (screen_height - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Message label
        label = ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=250
        )
        label.pack(pady=20, padx=20, expand=True)
        
        # OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100
        )
        ok_button.pack(pady=(0, 20))
        
        # Make dialog modal
        dialog.grab_set()
        self.wait_window(dialog)
    
    def _debounced_resize(self, event):
        """Debounce the resize event to prevent excessive reloading"""
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(250, lambda: self.load_assets())
    
    def clear_thumbnail_cache(self):
        """Clear the thumbnail cache"""
        self.thumbnail_cache.clear()
    