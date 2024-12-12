from .base_dialog import BaseDialog
import customtkinter as ctk
from tkinter import colorchooser, font

class TextDialog(BaseDialog):
    FONT_STYLES = ["normal", "bold", "italic", "bold italic"]
    ALIGNMENTS = ["left", "center", "right"]
    
    def __init__(self, parent, element, on_save):
        self.on_save = on_save
        super().__init__(parent, element, "Edit Text")
        self.dialog.geometry("400x450")
    
    def _create_ui(self):
        # Text content
        text_frame = ctk.CTkFrame(self.dialog)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.text_area = ctk.CTkTextbox(text_frame, height=100)
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_area.insert("1.0", self.properties.get('text', ''))
        
        # Font settings
        font_frame = ctk.CTkFrame(self.dialog)
        font_frame.pack(fill="x", padx=20, pady=10)
        
        # Font family
        self.font_var = ctk.StringVar(value=self.properties.get('font', 'Arial'))
        font_menu = ctk.CTkOptionMenu(
            font_frame,
            values=sorted(font.families()),
            variable=self.font_var
        )
        font_menu.pack(side="left", padx=5)
        
        # Font size
        self.size_var = ctk.StringVar(value=str(self.properties.get('fontSize', 12)))
        size_entry = ctk.CTkEntry(font_frame, textvariable=self.size_var, width=50)
        size_entry.pack(side="left", padx=5)
        
        # Style (bold, italic)
        style = "normal"
        if self.properties.get('bold') and self.properties.get('italic'):
            style = "bold italic"
        elif self.properties.get('bold'):
            style = "bold"
        elif self.properties.get('italic'):
            style = "italic"
        
        self.style_var = ctk.StringVar(value=style)
        style_menu = ctk.CTkOptionMenu(
            font_frame,
            values=self.FONT_STYLES,
            variable=self.style_var
        )
        style_menu.pack(side="left", padx=5)
        
        # Color picker
        color_frame = ctk.CTkFrame(self.dialog)
        color_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(color_frame, text="Color:").pack(side="left")
        self.color_var = ctk.StringVar(value=self.properties.get('fill', 'black'))
        self.color_preview = ctk.CTkButton(
            color_frame,
            text="",
            width=30,
            command=self._pick_color
        )
        self.color_preview.pack(side="left", padx=5)
        self.color_preview.configure(fg_color=self.color_var.get())
        
        # Alignment
        align_frame = ctk.CTkFrame(self.dialog)
        align_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(align_frame, text="Alignment:").pack(side="left")
        self.align_var = ctk.StringVar(value=self.properties.get('align', 'left'))
        align_menu = ctk.CTkOptionMenu(
            align_frame,
            values=self.ALIGNMENTS,
            variable=self.align_var
        )
        align_menu.pack(side="left", padx=5)
        
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
    
    def _pick_color(self):
        color = colorchooser.askcolor(color=self.color_var.get())[1]
        if color:
            self.color_var.set(color)
            self.color_preview.configure(fg_color=color)
    
    def _save_and_close(self):
        try:
            # Parse font style
            style = self.style_var.get()
            bold = "bold" in style
            italic = "italic" in style
            
            properties = {
                'text': self.text_area.get("1.0", "end-1c"),
                'font': self.font_var.get(),
                'fontSize': int(self.size_var.get()),
                'fill': self.color_var.get(),
                'bold': bold,
                'italic': italic,
                'align': self.align_var.get()
            }
            self.on_save(properties)
            self.dialog.destroy()
        except ValueError as e:
            print(f"Error saving text: {e}")