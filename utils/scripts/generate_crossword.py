from utils.scripts.base_script import BaseScript, ConfigWidget
import pandas as pd
import numpy as np
import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from tkinter import filedialog
from config import get_config

class CrosswordGenerator(BaseScript):
    def __init__(self):
        self.config = get_config()
        super().__init__()
        
    def get_title(self):
        return "Generate Crossword"
    
    def get_config_widgets(self, parent):
        # Create container frame for path selection
        path_frame = ctk.CTkFrame(parent)
        path_frame.pack(fill="x", padx=5, pady=2)
        
        # Create path entry and browse button
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Select output directory..."
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._browse_output_path,
            width=60
        )
        browse_btn.pack(side="right", padx=(2, 5))
        
        # Create path widget
        path_widget = ConfigWidget(
            parent, "output_path", "Output Directory:",
            widget_type=lambda p, **k: self.path_entry
        )
        
        # Get existing widgets
        csv_files = self._get_csv_files()
        self.columns = []
        
        # Create CSV file selector
        csv_widget = ConfigWidget(
            parent, "csv_file", "CSV File:",
            ctk.CTkOptionMenu, 
            values=csv_files,
            command=self._on_csv_selected
        )
        
        # Create column selector
        column_widget = ConfigWidget(
            parent, "column", "Word Column:",
            ctk.CTkOptionMenu,
            values=self.columns
        )
        
        # Store widgets for later updates
        self.csv_widget = csv_widget.widget
        self.column_widget = column_widget.widget
        
        # Update columns if a CSV file is selected
        if csv_files:
            self._on_csv_selected(csv_files[0])
        
        return [
            path_widget,
            csv_widget,
            column_widget,
            ConfigWidget(
                parent, "start_row", "Start Row:",
                ctk.CTkEntry, placeholder_text="1"
            ),
            ConfigWidget(
                parent, "end_row", "End Row:",
                ctk.CTkEntry, placeholder_text="20"
            ),
            ConfigWidget(
                parent, "grid_size", "Grid Size:",
                ctk.CTkEntry, placeholder_text="12"
            )
        ]
    
    def _get_csv_files(self):
        """Get list of available CSV files"""
        try:
            data_dir =  self.config.USER_DATA_DIR / "data"
            return [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        except Exception:
            return []
    
    def _get_csv_columns(self, csv_file):
        """Get list of columns from CSV file"""
        try:
            csv_path = self.config.USER_DATA_DIR / "data" / csv_file
            df = pd.read_csv(csv_path, nrows=0)  # Read only header
            return df.columns.tolist()
        except Exception as e:
            self.output.insert("end", f"Error reading CSV columns: {str(e)}\n")
            return []
    
    def _on_csv_selected(self, csv_file):
        """Handle CSV file selection"""
        self.columns = self._get_csv_columns(csv_file)
        self.column_widget.configure(values=self.columns)
        if self.columns:
            self.column_widget.set(self.columns[0])
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", f"Loaded columns from {csv_file}\n")
        else:
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", "No columns found in CSV file\n")
    
    def _browse_output_path(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir="."
        )
        if directory:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, directory)
    
    def run_script(self, config):
        try:
            # Get output directory from config
            output_dir = config["output_path"].strip()
            if not output_dir:
                output_dir = "crossword_output"  # Default if not specified
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Parse other config values
            csv_file = config["csv_file"]
            column = config["column"]
            start_row = int(config["start_row"] or 1)
            end_row = int(config["end_row"] or 20)
            grid_size = int(config["grid_size"] or 12)
            
            # Generate unique filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"crossword_{start_row}_{end_row}_{timestamp}"
            
            # Update paths to use selected directory
            output_path = os.path.join(output_dir, f"{base_filename}.csv")
            words_path = os.path.join(output_dir, f"words_{base_filename}.csv")
            image_path = os.path.join(output_dir, f"{base_filename}.png")
            
            # Load words with column selection
            words = self.load_words_from_csv(csv_file, start_row, end_row, column)
            if not words:
                if hasattr(self, 'dialog') and self.output:
                    self.output.insert("end", "No valid words found in the specified range.\n")
                return
            
            # Generate crossword
            crossword_data = self.generate_crossword_layout(words, grid_size)
            
            # Save grid to CSV
            grid_df = pd.DataFrame(crossword_data['grid'])
            grid_df.to_csv(output_path, index=False, header=False)
            
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", f"Grid saved to {output_path}\n")
            
            # Save word positions
            words_df = pd.DataFrame(crossword_data['placed_words'])
            words_df.to_csv(words_path, index=False)
            
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", f"Word positions saved to {words_path}\n")
            
            # Export image
            self.export_crossword_to_image(
                crossword_data,
                image_path,
                f"Crossword ({start_row}-{end_row})"
            )
            
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", "Crossword generated successfully!\n")
            
        except Exception as e:
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", f"Error: {str(e)}\n")
    
    def load_words_from_csv(self, csv_file, start_row, end_row, column=None):
        """Load words from CSV file within specified row range and column"""
        try:
            # Construct full path to CSV file
            csv_path = self.config.USER_DATA_DIR / "data" / csv_file
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            # Validate column selection
            if column not in df.columns:
                if hasattr(self, 'dialog') and self.output:
                    self.output.insert("end", f"Column '{column}' not found. Using first column.\n")
                column = df.columns[0]
            
            # Adjust row indices to 0-based indexing
            start_idx = start_row - 1
            end_idx = end_row
            
            # Validate row range
            if start_idx < 0:
                start_idx = 0
                if hasattr(self, 'dialog') and self.output:
                    self.output.insert("end", "Start row adjusted to 1\n")
            if end_idx > len(df):
                end_idx = len(df)
                if hasattr(self, 'dialog') and self.output:
                    self.output.insert("end", f"End row adjusted to {end_idx}\n")
            
            # Filter rows and get words from specified column
            words = df.iloc[start_idx:end_idx][column].tolist()
            
            # Clean and validate words
            valid_words = []
            for word in words:
                # Convert to string and clean
                word = str(word).strip().upper()
                # Check if word contains only letters
                if word.isalpha():
                    valid_words.append(word)
                else:
                    if hasattr(self, 'dialog') and self.output:
                        self.output.insert("end", f"Skipping invalid word: {word}\n")
            
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", f"Loaded {len(valid_words)} valid words from column '{column}'\n")
            return valid_words
            
        except Exception as e:
            if hasattr(self, 'dialog') and self.output:
                self.output.insert("end", f"Error loading words: {str(e)}\n")
            return []
    
    def generate_crossword_layout(self, words, grid_size):
        """Generate a crossword layout from the given words"""
        # Sort words by length (longest first)
        words = sorted(words, key=len, reverse=True)
        
        # Initialize grid with numpy for better performance
        grid = np.full((grid_size, grid_size), '', dtype=object)
        placed_words = []
        
        # Place first word in center row
        if words:
            center_row = grid_size // 2
            start_col = (grid_size - len(words[0])) // 2
            if start_col >= 0:
                grid[center_row, start_col:start_col + len(words[0])] = list(words[0].upper())
                placed_words.append({
                    'word': words[0],
                    'x': start_col,
                    'y': center_row,
                    'horizontal': True
                })
        
        def can_place_word(word, row, col, direction):
            """Check if a word can be placed at a given position and direction"""
            word = word.upper()
            word_len = len(word)
            
            # Check bounds
            if direction == "horizontal":
                if col < 0 or col + word_len > grid_size or row < 0 or row >= grid_size:
                    return False
            else:  # vertical
                if row < 0 or row + word_len > grid_size or col < 0 or col >= grid_size:
                    return False
            
            # Check each position
            for i, letter in enumerate(word):
                r, c = (row, col + i) if direction == "horizontal" else (row + i, col)
                curr_cell = grid[r, c]
                
                # Check if cell is empty or matches letter
                if curr_cell != '' and curr_cell != letter:
                    return False
                
                # Check adjacent cells (except intersections)
                if direction == "horizontal":
                    # Check above and below
                    if r > 0 and grid[r-1, c] != '' and curr_cell == '':
                        return False
                    if r < grid_size-1 and grid[r+1, c] != '' and curr_cell == '':
                        return False
                else:
                    # Check left and right
                    if c > 0 and grid[r, c-1] != '' and curr_cell == '':
                        return False
                    if c < grid_size-1 and grid[r, c+1] != '' and curr_cell == '':
                        return False
            
            return True
        
        def place_word(word, row, col, direction):
            """Place a word into the grid"""
            word = word.upper()
            for i, letter in enumerate(word):
                if direction == "horizontal":
                    grid[row, col + i] = letter
                else:
                    grid[row + i, col] = letter
        
        # Place remaining words
        for word in words[1:]:
            if len(word) > grid_size:
                self.output.insert("end", f"Skipping {word}: too long for grid\n")
                continue
                
            placed = False
            # Try to place word at intersections first
            for r in range(grid_size):
                for c in range(grid_size):
                    if placed:
                        break
                        
                    # Try to place at intersections
                    if grid[r, c] != '' and grid[r, c] in word.upper():
                        word_idx = word.upper().index(grid[r, c])
                        
                        # Try horizontal placement
                        if can_place_word(word, r, c - word_idx, "horizontal"):
                            place_word(word, r, c - word_idx, "horizontal")
                            placed_words.append({
                                'word': word,
                                'x': c - word_idx,
                                'y': r,
                                'horizontal': True
                            })
                            placed = True
                            break
                        
                        # Try vertical placement
                        if not placed and can_place_word(word, r - word_idx, c, "vertical"):
                            place_word(word, r - word_idx, c, "vertical")
                            placed_words.append({
                                'word': word,
                                'x': c,
                                'y': r - word_idx,
                                'horizontal': False
                            })
                            placed = True
                            break
            
            if not placed:
                self.output.insert("end", f"Could not place word: {word}\n")
        
        return {
            'grid': grid.tolist(),  # Convert numpy array to list for JSON serialization
            'placed_words': placed_words
        }
    
    def export_crossword_to_image(self, crossword_data, output_path, title):
        """Export the crossword to a PNG image"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            grid = np.array(crossword_data['grid'])  # Convert back to numpy array
            grid_size = len(grid)
            cell_size = 50
            padding = 20
            
            # Create image with extra space for title
            img_width = grid_size * cell_size + 2 * padding
            img_height = grid_size * cell_size + 2 * padding + 40
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
                font_cell = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
            except:
                font_title = ImageFont.load_default()
                font_cell = ImageFont.load_default()
            
            # Draw title
            title_x = img_width // 2
            draw.text((title_x, padding), title, font=font_title, fill="black", anchor="mm")
            
            # Draw grid
            for r in range(grid_size):
                for c in range(grid_size):
                    x1 = c * cell_size + padding
                    y1 = r * cell_size + padding + 40
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    # Draw cell border
                    draw.rectangle([x1, y1, x2, y2], outline="black", width=2)
                    
                    # Draw letter if not empty
                    letter = grid[r, c]
                    if letter != '':
                        draw.text(
                            ((x1 + x2) // 2, (y1 + y2) // 2),
                            letter,
                            font=font_cell,
                            fill="black",
                            anchor="mm"
                        )
            
            # Save image
            img.save(output_path)
            self.output.insert("end", f"Crossword exported to {output_path}\n")
            
        except Exception as e:
            self.output.insert("end", f"Error exporting crossword: {str(e)}\n")

def main():
    return CrosswordGenerator()
