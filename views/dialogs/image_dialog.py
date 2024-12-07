import customtkinter as ctk
from views.asset_manager import AssetManager

class ImageDialog:
    def __init__(self, parent, element, asset_controller, on_save):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Edit Image")
        self.dialog.geometry("650x500")
        self.element = element
        self.asset_controller = asset_controller
        self.on_save = on_save
        
        self._create_ui()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def _create_ui(self):
        # Asset manager
        asset_frame = ctk.CTkFrame(self.dialog)
        asset_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.asset_manager = AssetManager(asset_frame, self.asset_controller)
        self.asset_manager.pack(fill="both", expand=True)
        
        # Size inputs
        size_frame = ctk.CTkFrame(self.dialog)
        size_frame.pack(fill="x", padx=20, pady=10)
        
        # Width
        width_frame = ctk.CTkFrame(size_frame)
        width_frame.pack(side="left", padx=5)
        ctk.CTkLabel(width_frame, text="Width:").pack(side="left")
        self.width_var = ctk.StringVar(value=str(self.element.get('properties', {}).get('width', 100)))
        width_entry = ctk.CTkEntry(width_frame, textvariable=self.width_var, width=60)
        width_entry.pack(side="left", padx=2)
        
        # Height
        height_frame = ctk.CTkFrame(size_frame)
        height_frame.pack(side="left", padx=5)
        ctk.CTkLabel(height_frame, text="Height:").pack(side="left")
        self.height_var = ctk.StringVar(value=str(self.element.get('properties', {}).get('height', 100)))
        height_entry = ctk.CTkEntry(height_frame, textvariable=self.height_var, width=60)
        height_entry.pack(side="left", padx=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.dialog)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self._save_and_close
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side="right", padx=5)
    
    def _save_and_close(self):
        try:
            selected_assets = self.asset_manager.selected_assets
            if selected_assets:
                asset_id = list(selected_assets)[0]
                asset = self.asset_controller.get_asset_by_id(asset_id)
                
                if asset:
                    print(f"Saving image with path: {asset.file_path}")  # Debug log
                    properties = {
                        'path': asset.file_path,
                        'width': int(self.width_var.get()),
                        'height': int(self.height_var.get()),
                        'asset_id': asset_id  # Store asset ID for reference
                    }
                    self.on_save(properties)
                    self.dialog.destroy()
                else:
                    print("No asset found")
            else:
                print("No asset selected")
        except ValueError as e:
            print(f"Error saving image: {e}") 