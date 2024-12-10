import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, A4, A5
from reportlab.lib.units import mm
import tkinter as tk
from reportlab.lib.utils import ImageReader
import math
import shutil
import tempfile

class PDFExporter(ctk.CTkFrame):
    def __init__(self, parent, template_controller, csv_controller):
        super().__init__(parent)
        self.template_controller = template_controller
        self.csv_controller = csv_controller
        
        # Initialize variables
        self.selected_template = None
        self.export_path = None
        self.page_size = "A4"
        self.page_sizes = {
            "A3": A3,
            "A4": A4,
            "A5": A5
        }
        
        self._create_ui()
        self._load_templates()
    
    def _create_ui(self):
        """Create the main UI components"""
        # Top Frame: Template Selection and Export Path
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Template Selection
        template_frame = ctk.CTkFrame(top_frame)
        template_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            template_frame,
            text="Select Template:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        self.template_var = ctk.StringVar(value="Select template...")
        self.template_menu = ctk.CTkOptionMenu(
            template_frame,
            variable=self.template_var,
            values=["Loading..."],
            command=self._on_template_selected,
            width=200
        )
        self.template_menu.pack(side="left", padx=5)
        
        # Page Size Selection
        size_frame = ctk.CTkFrame(top_frame)
        size_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            size_frame,
            text="Page Size:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        self.size_var = ctk.StringVar(value="A4")
        for size in ["A3", "A4", "A5"]:
            ctk.CTkRadioButton(
                size_frame,
                text=size,
                variable=self.size_var,
                value=size
            ).pack(side="left", padx=10)
        
        # Export Path Selection
        path_frame = ctk.CTkFrame(top_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            path_frame,
            text="Export Path:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)
        
        self.path_var = ctk.StringVar(value="Choose export path...")
        path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.path_var,
            width=300,
            state="readonly"
        )
        path_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._choose_export_path,
            width=100
        ).pack(side="left", padx=5)
        
        # Middle Frame: Row Range Filter
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            filter_frame,
            text="Row Range Filter",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        range_frame = ctk.CTkFrame(filter_frame)
        range_frame.pack(fill="x", padx=5, pady=5)
        
        # Start Row
        ctk.CTkLabel(
            range_frame,
            text="Start Row:"
        ).pack(side="left", padx=5)
        
        self.start_row_var = ctk.StringVar(value="1")
        start_entry = ctk.CTkEntry(
            range_frame,
            textvariable=self.start_row_var,
            width=80
        )
        start_entry.pack(side="left", padx=5)
        
        # End Row
        ctk.CTkLabel(
            range_frame,
            text="End Row:"
        ).pack(side="left", padx=5)
        
        self.end_row_var = ctk.StringVar(value="")
        end_entry = ctk.CTkEntry(
            range_frame,
            textvariable=self.end_row_var,
            width=80,
            placeholder_text="Last"
        )
        end_entry.pack(side="left", padx=5)
        
        # Bottom Frame: Export Controls and Preview
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left side: Export controls
        control_frame = ctk.CTkFrame(bottom_frame)
        control_frame.pack(side="left", fill="y", padx=5)
        
        # Export button
        ctk.CTkButton(
            control_frame,
            text="Generate PDF",
            command=self._start_export,
            width=120
        ).pack(pady=5)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(control_frame)
        progress_frame.pack(fill="x", pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=2)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready",
            font=("Arial", 10)
        )
        self.progress_label.pack(pady=2)
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(bottom_frame)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(
            self.preview_frame,
            text="Preview",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.preview_container = ctk.CTkFrame(self.preview_frame)
        self.preview_container.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _load_templates(self):
        """Load available templates"""
        templates = self.template_controller.get_all_templates()
        template_names = [t.name for t in templates] if templates else ["No templates"]
        self.template_menu.configure(values=template_names)
    
    def _choose_export_path(self):
        """Open dialog to choose export path"""
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )
        if path:
            self.path_var.set(path)
    
    def _on_template_selected(self, template_name):
        """Handle template selection"""
        templates = self.template_controller.get_all_templates()
        self.selected_template = next(
            (t for t in templates if t.name == template_name),
            None
        )
        if self.selected_template:
            self._update_preview()
    
    def _update_preview(self):
        """Update the preview of card layout on selected page size"""
        # Clear previous preview
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        if not self.selected_template:
            return
        
        # Load template data
        template_data = self.template_controller.load_template(self.selected_template.id)
        if not template_data:
            return
        
        # Get actual dimensions from template data
        dimensions = template_data['dimensions']
        dpi = dimensions.get('dpi', 96)
        unit = dimensions.get('unit', 'mm')
        
        # Convert dimensions to mm if needed
        if unit == 'px':
            actual_width = (dimensions['width'] / dpi) * 25.4
            actual_height = (dimensions['height'] / dpi) * 25.4
        elif unit == 'in':
            actual_width = dimensions['width'] * 25.4
            actual_height = dimensions['height'] * 25.4
        else:  # unit is already mm
            actual_width = dimensions['width']
            actual_height = dimensions['height']
        
        # Calculate layout
        page_size = self.page_sizes[self.size_var.get()]
        layout = self._calculate_layout(actual_width, actual_height, page_size)
        
        # Show template and layout info
        info_text = f"Template: {self.selected_template.name}\n"
        info_text += f"Card Size: {actual_width:.1f}x{actual_height:.1f}mm\n"
        info_text += f"Page Size: {self.size_var.get()}\n\n"
        info_text += f"Layout Details:\n"
        info_text += f"• Cards per page: {layout['cards_per_page']}\n"
        info_text += f"• Cards per row: {layout['cards_per_row']}\n"
        info_text += f"• Cards per column: {layout['cards_per_column']}\n"
        info_text += f"• Horizontal spacing: {layout['h_spacing']:.1f}mm\n"
        info_text += f"• Vertical spacing: {layout['v_spacing']:.1f}mm\n"
        info_text += f"• Page margins: {layout['margin']}mm"
        
        ctk.CTkLabel(
            self.preview_container,
            text=info_text,
            justify="left"
        ).pack(pady=10, padx=10, anchor="w")
    
    def _calculate_layout(self, card_width_mm: float, card_height_mm: float, page_size: tuple) -> dict:
        """Calculate how many cards can fit on a page and their positions"""
        # Convert page size from points to mm (1 point = 0.352778 mm)
        print("page_size", page_size)
        print("card_width_mm", card_width_mm)
        print("card_height_mm", card_height_mm)
        page_width_mm = page_size[0] * 0.352778
        page_height_mm = page_size[1] * 0.352778
        
        # Add margins (10mm on each side)
        margin_mm = 10
        usable_width = max(0.1, page_width_mm - (2 * margin_mm))
        usable_height = max(0.1, page_height_mm - (2 * margin_mm))
        print("usable_width", usable_width)
        print("usable_height", usable_height)
        
        # Ensure card dimensions are positive
        card_width_mm = max(0.1, float(card_width_mm))
        card_height_mm = max(0.1, float(card_height_mm))
        
        # Calculate number of cards that can fit in each direction
        cards_per_row = max(1, math.floor(usable_width / card_width_mm))
        cards_per_column = max(1, math.floor(usable_height / card_height_mm))
        
        # Calculate spacing between cards (distribute extra space evenly)
        extra_width = usable_width - (cards_per_row * card_width_mm)
        extra_height = usable_height - (cards_per_column * card_height_mm)
        
        # Ensure we don't divide by zero by using at least 1 for denominators
        h_spacing = extra_width / max(1, cards_per_row + 1)
        v_spacing = extra_height / max(1, cards_per_column + 1)
        
        return {
            'cards_per_page': cards_per_row * cards_per_column,
            'cards_per_row': cards_per_row,
            'cards_per_column': cards_per_column,
            'h_spacing': h_spacing,
            'v_spacing': v_spacing,
            'margin': margin_mm,
            'card_width': card_width_mm,
            'card_height': card_height_mm
        }

    def _generate_card_image(self, card_data: dict, output_path: str) -> str:
        """Generate a temporary image file for a card"""
        try:
            # Create preview frame for image generation
            preview_frame = ctk.CTkFrame(self)
            
            # Get dimensions and convert to pixels
            dimensions = card_data.get('dimensions', {})
            dpi = dimensions.get('dpi', 96)
            unit = dimensions.get('unit', 'mm')
            
            # Convert dimensions to pixels
            if unit == 'mm':
                width = int((dimensions['width'] * dpi) / 25.4)
                height = int((dimensions['height'] * dpi) / 25.4)
            elif unit == 'in':
                width = int(dimensions['width'] * dpi)
                height = int(dimensions['height'] * dpi)
            else:  # unit is already px
                width = int(dimensions['width'])
                height = int(dimensions['height'])
            
            # Ensure dimensions are positive integers
            width = max(1, width)
            height = max(1, height)
            
            preview_frame.configure(width=width, height=height)
            preview_frame.pack_forget()  # Hide the frame but keep it in memory
            
            try:
                # Generate card image using template controller
                success = self.template_controller.export_template_image(
                    template_data=card_data,
                    output_path=output_path,
                    preview_frame=None
                )
                
                if not success:
                    print(f"Template controller failed with dimensions: {width}x{height}")
                    return None
                
                # Verify the image exists
                if not os.path.exists(output_path):
                    print(f"Output file not found: {output_path}")
                    return None
                
                # Verify and process the image
                with Image.open(output_path) as img:
                    # Save as PNG with white background
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, 'WHITE')
                        background.paste(img, mask=img.split()[-1])
                        background.save(output_path, 'PNG')
                    else:
                        img.convert('RGB').save(output_path, 'PNG')
                
                return output_path
                
            except Exception as e:
                print(f"Error in image generation: {e}")
                import traceback
                traceback.print_exc()
                return None
            
            finally:
                # Clean up preview frame
                preview_frame.destroy()
                
        except Exception as e:
            print(f"Critical error in _generate_card_image: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _start_export(self):
        """Start the PDF export process"""
        if not self._validate_export():
            return
        
        try:
            # Get template data
            template_data = self.template_controller.load_template(self.selected_template.id)
            if not template_data:
                self._show_error("Failed to load template data")
                return
            
            # Get card dimensions and calculate actual size
            dimensions = template_data.get('dimensions', {})
            unit = dimensions.get('unit', 'mm')
            dpi = dimensions.get('dpi', 96)
            
            # Get actual width and height in mm
            card_width_mm = dimensions.get('actual_width', dimensions.get('width', 63))
            card_height_mm = dimensions.get('actual_height', dimensions.get('height', 88))
            
            print("unit", unit)
            print("dpi", dpi)
            # Convert to mm if needed
            if unit == 'px':
                card_width_mm = (card_width_mm / dpi) * 25.4
                card_height_mm = (card_height_mm / dpi) * 25.4
            elif unit == 'in':
                card_width_mm = card_width_mm * 25.4
                card_height_mm = card_height_mm * 25.4
            elif unit == 'mm':
                # Convert from pixels to mm since actual size is always in pixels
                card_width_mm = (card_width_mm / dpi) * 25.4
                card_height_mm = (card_height_mm / dpi) * 25.4
            
            # Load CSV data
            csv_file = template_data.get('data_source', {}).get('file')
            if not csv_file:
                self._show_error("No CSV file configured in template")
                return
            
            csv_path = os.path.join("./assets_static/data", csv_file)
            if not os.path.exists(csv_path):
                self._show_error(f"CSV file not found: {csv_file}")
                return
            
            df = pd.read_csv(csv_path)
            
            # Apply row range filter
            start_row = int(self.start_row_var.get()) - 1
            end_row = int(self.end_row_var.get()) if self.end_row_var.get() else len(df)
            df = df.iloc[start_row:end_row]
            
            if df.empty:
                self._show_error("No records match the filter criteria")
                return
            
            # Get page size and calculate layout
            page_size = self.page_sizes[self.size_var.get()]
            layout = self._calculate_layout(card_width_mm, card_height_mm, page_size)
            
            # Debug print
            print(f"Layout calculation results:")
            print(f"Page size: {page_size}")
            print(f"Card size: {card_width_mm}mm x {card_height_mm}mm")
            print(f"Cards per row: {layout['cards_per_row']}")
            print(f"Cards per column: {layout['cards_per_column']}")
            print(f"Cards per page: {layout['cards_per_page']}")
            print(f"Horizontal spacing: {layout['h_spacing']}mm")
            print(f"Vertical spacing: {layout['v_spacing']}mm")
            
            # Calculate page margins and spacing
            page_width_mm = page_size[0] * 25.4 / 72  # Convert points to mm
            page_height_mm = page_size[1] * 25.4 / 72
            
            # Use layout values for margins and spacing
            margin_h = layout['margin']  # Use margin from layout calculation
            margin_v = layout['margin']
            
            # Use pre-calculated spacing from layout
            h_spacing = layout['h_spacing']
            v_spacing = layout['v_spacing']
            
            # Create temporary directory for card images
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Create PDF
                c = canvas.Canvas(self.path_var.get(), pagesize=page_size)
                
                # Process cards
                total_cards = len(df)
                cards_on_current_page = 0
                cards_per_page = layout['cards_per_page']
                total_pages = math.ceil(total_cards / cards_per_page)
                current_page = 1
                
                for index, row in df.iterrows():
                    # Update progress
                    progress = (index - start_row + 1) / total_cards
                    self.progress_bar.set(progress)
                    self.progress_label.configure(
                        text=f"Processing card {index - start_row + 1} of {total_cards}"
                    )
                    self.update()
                    
                    try:
                        # Generate card image
                        card_data = template_data.copy()
                        self._apply_mappings(card_data, row)
                        
                        # Generate temporary image file
                        temp_image_path = os.path.join(temp_dir, f"card_{index}.png")
                        result_path = self._generate_card_image(card_data, temp_image_path)
                        
                        if not result_path or not os.path.exists(result_path):
                            print(f"Failed to generate image for card {index}")
                            continue
                        
                        # Calculate position on page
                        row_num = (cards_on_current_page // layout['cards_per_row'])
                        col_num = (cards_on_current_page % layout['cards_per_row'])
                        
                        # Calculate x and y positions in points (72 points = 1 inch)
                        x = (layout['margin'] + col_num * (layout['card_width'] + layout['h_spacing'])) * 72 / 25.4
                        y = (page_height_mm - (layout['margin'] + (row_num + 1) * layout['card_height'] + row_num * layout['v_spacing'])) * 72 / 25.4
                        
                        # Add image to PDF
                        try:
                            img = ImageReader(result_path)
                            c.drawImage(
                                img,
                                x, y,
                                width=card_width_mm * 72 / 25.4,
                                height=card_height_mm * 72 / 25.4,
                                preserveAspectRatio=True
                            )
                            
                            cards_on_current_page += 1
                            
                            # Start new page if current page is full
                            if cards_on_current_page >= cards_per_page and index < len(df) - 1:
                                c.showPage()
                                current_page += 1
                                cards_on_current_page = 0
                            
                        except Exception as e:
                            print(f"Error adding image to PDF: {e}")
                            continue
                        
                    except Exception as e:
                        print(f"Error processing card {index}: {e}")
                        continue
                
                # Save the final PDF
                if cards_on_current_page > 0:
                    c.showPage()
                
                c.save()
                self.progress_bar.set(1)
                self.progress_label.configure(text="Export completed!")
                
                if cards_on_current_page > 0:
                    tk.messagebox.showinfo(
                        "Success",
                        f"PDF exported successfully!\n"
                        f"Total pages: {total_pages}\n"
                        f"Total cards: {total_cards}"
                    )
                else:
                    self._show_error("No cards were successfully generated")
                
            finally:
                # Clean up temporary files
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    print(f"Error cleaning up temporary files: {e}")
        
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.progress_bar.set(0)
            self.progress_label.configure(text="Ready")
    
    def _validate_export(self) -> bool:
        """Validate export configuration"""
        if self.template_var.get() == "Select template...":
            self._show_error("Please select a template")
            return False
        
        if not self.path_var.get() or self.path_var.get() == "Choose export path...":
            self._show_error("Please select an export path")
            return False
        
        try:
            if self.start_row_var.get():
                start_row = int(self.start_row_var.get())
                if start_row < 1:
                    self._show_error("Start row must be greater than 0")
                    return False
            
            if self.end_row_var.get():
                end_row = int(self.end_row_var.get())
                if end_row < int(self.start_row_var.get()):
                    self._show_error("End row must be greater than start row")
                    return False
        except ValueError:
            self._show_error("Row numbers must be valid integers")
            return False
        
        return True
    
    def _show_error(self, message: str):
        """Show error message"""
        tk.messagebox.showerror("Error", message)
    
    def _apply_mappings(self, card_data: dict, row: pd.Series):
        """Apply data mappings to card data"""
        try:
            mappings = card_data.get('data_source', {}).get('mappings', {})
            available_columns = row.index.tolist()
            
            for element_id, mapping in mappings.items():
                if mapping['type'] == 'direct':
                    column = mapping['column']
                    if column not in available_columns:
                        print(f"Warning: Column '{column}' not found in data")
                        continue
                    
                    value = str(row[column]) if pd.notna(row[column]) else ""
                    if not value:
                        continue
                    
                    for element in card_data['elements']:
                        if element['id'] == element_id and element['type'] == 'text':
                            element['properties']['text'] = value
                            break
                
                elif mapping['type'] == 'macro':
                    expression = mapping['expression']
                    for column in available_columns:
                        col_value = str(row[column]) if pd.notna(row[column]) else ""
                        expression = expression.replace(f"${{{column}}}", col_value)
                    
                    for element in card_data['elements']:
                        if element['id'] == element_id and element['type'] == 'image':
                            element['properties']['path'] = expression
                            break
        
        except Exception as e:
            print(f"Error applying mappings: {e}") 