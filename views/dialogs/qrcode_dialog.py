import customtkinter as ctk
import qrcode
from PIL import Image
from typing import Callable, Dict, Any

class QRCodeDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save: Callable[[Dict[str, Any]], None]):
        super().__init__(parent)
        self.title("Create QR Code")
        self.on_save = on_save
        
        # Center dialog
        self.geometry("500x400")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # QR Code content
        ctk.CTkLabel(
            self.main_frame,
            text="QR Code Content:",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.content_text = ctk.CTkTextbox(
            self.main_frame,
            height=150,
            width=400
        )
        self.content_text.pack(pady=(0, 20))
        
        # QR Code size
        size_frame = ctk.CTkFrame(self.main_frame)
        size_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            size_frame,
            text="Size (pixels):",
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.size_var = ctk.StringVar(value="120")
        size_entry = ctk.CTkEntry(
            size_frame,
            textvariable=self.size_var,
            width=100
        )
        size_entry.pack(side="left")
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Create button
        ctk.CTkButton(
            button_frame,
            text="Create",
            command=self._create_qrcode
        ).pack(side="left", padx=5)
        
        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="right", padx=5)
    
    
    def _create_qrcode(self):
        """Create QR code and save properties"""
        try:
            content = self.content_text.get("1.0", "end-1c")
            if not content.strip():
                self._show_error("Please enter content for the QR code")
                return
            
            size = int(self.size_var.get())
            if size < 50 or size > 1000:
                self._show_error("Size must be between 50 and 1000 pixels")
                return
            
            # Create properties dictionary
            properties = {
                'type': 'qrcode',
                'content': content,
                'width': size,
                'height': size,
                'fill': 'black',
                'background': None
            }
            
            # Call save callback
            self.on_save(properties)
            self.destroy()
            
        except ValueError:
            self._show_error("Invalid size value")
        except Exception as e:
            self._show_error(f"Error creating QR code: {str(e)}")
    
    def _show_error(self, message: str):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("300x150")
        
        # Center error dialog
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() - 300) // 2
        y = (error_dialog.winfo_screenheight() - 150) // 2
        error_dialog.geometry(f"+{x}+{y}")
        
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        ctk.CTkLabel(
            error_dialog,
            text=message,
            wraplength=250
        ).pack(pady=20)
        
        ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy
        ).pack(pady=10) 