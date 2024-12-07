import customtkinter as ctk
from tkinter import colorchooser, messagebox

class ShapeDialog:
    def __init__(self, parent, element, on_save):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Edit Shape")
        self.element = element
        self.on_save = on_save
        
        # Initialize properties with defaults
        self.properties = element.get('properties', {})
        
        self._create_ui()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def _create_ui(self):
        # Color pickers frame
        colors_frame = ctk.CTkFrame(self.dialog)
        colors_frame.pack(padx=20, pady=10, fill="x")
        
        # Fill color
        fill_frame = ctk.CTkFrame(colors_frame)
        fill_frame.pack(side="left", padx=5)
        ctk.CTkLabel(fill_frame, text="Fill:").pack(side="left")
        self.fill_preview = ctk.CTkButton(
            fill_frame, 
            text="",
            width=30,
            command=lambda: self._pick_color('fill')
        )
        self.fill_preview.pack(side="left", padx=5)
        self.fill_preview.configure(fg_color=self.properties.get('fill', '#3498db'))
        
        # Border color
        border_frame = ctk.CTkFrame(colors_frame)
        border_frame.pack(side="left", padx=5)
        ctk.CTkLabel(border_frame, text="Border:").pack(side="left")
        self.border_preview = ctk.CTkButton(
            border_frame,
            text="",
            width=30,
            command=lambda: self._pick_color('outline')
        )
        self.border_preview.pack(side="left", padx=5)
        self.border_preview.configure(fg_color=self.properties.get('outline', 'black'))
        
        # Size inputs
        size_frame = ctk.CTkFrame(self.dialog)
        size_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(size_frame, text="Width:").pack(side="left")
        self.width_var = ctk.StringVar(value=str(self.properties.get('width', 50)))
        width_entry = ctk.CTkEntry(size_frame, textvariable=self.width_var, width=50)
        width_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_frame, text="Height:").pack(side="left")
        self.height_var = ctk.StringVar(value=str(self.properties.get('height', 50)))
        height_entry = ctk.CTkEntry(size_frame, textvariable=self.height_var, width=50)
        height_entry.pack(side="left", padx=5)
        
        # Border properties
        border_props_frame = ctk.CTkFrame(self.dialog)
        border_props_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(border_props_frame, text="Border Width:").pack(side="left")
        self.border_width_var = ctk.StringVar(value=str(self.properties.get('outline_width', 1)))
        border_width_entry = ctk.CTkEntry(border_props_frame, textvariable=self.border_width_var, width=50)
        border_width_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(border_props_frame, text="Style:").pack(side="left", padx=5)
        # Convert existing dash pattern to style name
        current_dash = self.properties.get('dash', '')
        current_style = "Solid"
        if current_dash == (5, 2):
            current_style = "Dash"
        elif current_dash == (2, 2):
            current_style = "Dot"
        
        self.border_style_var = ctk.StringVar(value=current_style)
        border_style = ctk.CTkOptionMenu(
            border_props_frame,
            values=["Solid", "Dash", "Dot"],
            variable=self.border_style_var
        )
        border_style.pack(side="left", padx=5)
        
        # Corner radius
        radius_frame = ctk.CTkFrame(self.dialog)
        radius_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(radius_frame, text="Corner Radius:").pack(side="left")
        self.radius_var = ctk.StringVar(value=str(self.properties.get('radius', 0)))
        radius_entry = ctk.CTkEntry(radius_frame, textvariable=self.radius_var, width=50)
        radius_entry.pack(side="left", padx=5)
        
        # Opacity slider frame
        opacity_frame = ctk.CTkFrame(self.dialog)
        opacity_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(opacity_frame, text="Opacity:").pack(side="left")
        self.opacity_var = ctk.DoubleVar(value=self.properties.get('opacity', 1.0))
        opacity_slider = ctk.CTkSlider(
            opacity_frame,
            from_=0.0,
            to=1.0,
            variable=self.opacity_var,
            width=150
        )
        opacity_slider.pack(side="left", padx=5)
        
        # Opacity value label
        self.opacity_label = ctk.CTkLabel(opacity_frame, text="100%")
        self.opacity_label.pack(side="left", padx=5)
        
        # Update opacity label when slider changes
        self.opacity_var.trace_add("write", self._update_opacity_label)
        
        # Save button
        ctk.CTkButton(
            self.dialog,
            text="Save",
            command=self._save_and_close
        ).pack(pady=10)
    
    def _pick_color(self, property_name):
        color = colorchooser.askcolor(
            color=self.properties.get(property_name, '#3498db' if property_name == 'fill' else 'black'),
            title=f"Choose {property_name.title()} Color"
        )[1]
        if color:
            self.properties[property_name] = color
            if property_name == 'fill':
                self.fill_preview.configure(fg_color=color)
            else:
                self.border_preview.configure(fg_color=color)
    
    def _update_opacity_label(self, *args):
        """Update the opacity label when the slider value changes"""
        opacity_percentage = int(self.opacity_var.get() * 100)
        self.opacity_label.configure(text=f"{opacity_percentage}%")
    
    def _save_and_close(self):
        try:
            # Convert dash style to actual dash pattern
            dash_style = self.border_style_var.get()
            dash_pattern = {
                'Solid': None,  # Changed from empty string to None
                'Dash': (5, 2),
                'Dot': (2, 2)
            }.get(dash_style, None)  # Default to None instead of empty string
            
            properties = {
                'width': int(self.width_var.get()),
                'height': int(self.height_var.get()),
                'fill': self.properties.get('fill', '#3498db'),
                'outline': self.properties.get('outline', 'black'),
                'outline_width': int(self.border_width_var.get()),
                'dash': dash_pattern,
                'radius': int(self.radius_var.get()),
                'opacity': float(self.opacity_var.get())
            }
            
            # Update the element's properties
            self.element['properties'] = properties
            
            self.on_save(properties)
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for size, border width, and radius.")