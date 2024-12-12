# utils/scripts/generate_asset_ai.py
import uuid
from utils.scripts.base_script import BaseScript, ConfigWidget
import asyncio
import perchance
import pandas as pd
from PIL import Image
import os
import time
import random
import customtkinter as ctk
from tkinter import filedialog

class AssetAIGenerator(BaseScript):
    def __init__(self):
        super().__init__()
        self.csv_columns = []
        
    def get_title(self):
        return "Generate AI Assets"
    
    def _browse_csv_file(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            self.csv_entry.delete(0, "end")
            self.csv_entry.insert(0, filename)
            # Explicitly show the columns frame and update columns
            self.csv_columns_frame.pack(fill="x", padx=5, pady=1)
            self._update_csv_columns(filename)
    
    def _update_csv_columns(self, csv_path):
        try:
            df = pd.read_csv(csv_path)
            self.csv_columns = df.columns.tolist()
            # Update combobox values
            self.prompt_column.configure(values=self.csv_columns)
            self.name_column.configure(values=self.csv_columns)
            
            # Set default selection to first column
            if self.csv_columns:
                self.prompt_column.set(self.csv_columns[0])
                self.name_column.set(self.csv_columns[0])
        except Exception as e:
            self.output.insert("end", f"Error loading CSV columns: {str(e)}\n")

    def get_config_widgets(self, parent):
        # Output Directory Selection
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill="x", padx=5, pady=2)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="Select output directory..."
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
        
        ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self._browse_output_path,
            width=60
        ).pack(side="right", padx=(2, 5))

        # Create tabview
        self.tabview = ctk.CTkTabview(parent, height=100)
        self.tabview.pack(fill="x", padx=5, pady=2)
        
        # Create tabs
        custom_tab = self.tabview.add("Custom Prompts")
        csv_tab = self.tabview.add("CSV Prompts")
        
        # Custom Prompts Tab Content
        prompt_frame = ctk.CTkFrame(custom_tab)
        prompt_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        ctk.CTkLabel(prompt_frame, text="Enter Prompts:").pack(side="top", anchor="w", padx=5, pady=(5,0))
        self.prompt_text = ctk.CTkTextbox(
            prompt_frame,
            height=70,
            width=500,
            wrap="word"
        )
        self.prompt_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(
            prompt_frame,
            text="Enter one prompt per line. Each line will generate a separate image.",
            font=("Helvetica", 10),
            text_color="gray"
        ).pack(side="bottom", anchor="w", padx=5)
        
        # CSV Tab Content
        file_frame = ctk.CTkFrame(csv_tab)
        file_frame.pack(fill="x", padx=5, pady=(2,1))
        
        self.csv_entry = ctk.CTkEntry(
            file_frame,
            placeholder_text="Select CSV file..."
        )
        self.csv_entry.pack(side="left", fill="x", expand=True, padx=(5, 2))
        
        browse_csv_btn = ctk.CTkButton(
            file_frame,
            text="Browse",
            command=self._browse_csv_file,
            width=60
        )
        browse_csv_btn.pack(side="right", padx=(2, 5))
        
        # CSV Column Selection Frame
        self.csv_columns_frame = ctk.CTkFrame(csv_tab)
        self.csv_columns_frame.pack_forget()
        
        column_left = ctk.CTkFrame(self.csv_columns_frame)
        column_left.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(column_left, text="Prompt Column:").pack(side="left", padx=5)
        self.prompt_column = ctk.CTkComboBox(
            column_left,
            values=self.csv_columns,
            width=150
        )
        self.prompt_column.pack(side="left", padx=5)
        
        column_right = ctk.CTkFrame(self.csv_columns_frame)
        column_right.pack(side="right", fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(column_right, text="Name Column:").pack(side="left", padx=5)
        self.name_column = ctk.CTkComboBox(
            column_right,
            values=self.csv_columns,
            width=150
        )
        self.name_column.pack(side="left", padx=5)

        # Resolution, Style, and Guidance Scale
        params_frame = ctk.CTkFrame(parent)
        params_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(params_frame, text="Resolution:").pack(side="left", padx=5)
        self.resolution_entry = ctk.CTkEntry(params_frame, placeholder_text="512x768", width=100)
        self.resolution_entry.pack(side="left", padx=5)
        
        # Add Style selector
        ctk.CTkLabel(params_frame, text="Style:").pack(side="left", padx=5)
        styles = [
                    "Painted Anime",
                    "Casual Photo",
                    "Cinematic",
                    "Digital Painting",
                    "Concept Art",
                    "𝗡𝗼 𝘀𝘁𝘆𝗹𝗲",
                    "3D Disney Character",
                    "2D Disney Character",
                    "Disney Sketch",
                    "Concept Sketch",
                    "Painterly",
                    "Oil Painting",
                    "Oil Painting - Realism",
                    "Oil Painting - Old",
                    "Professional Photo",
                    "Anime",
                    "Drawn Anime",
                    "Cute Anime",
                    "Soft Anime",
                    "Fantasy Painting",
                    "Fantasy Landscape",
                    "Fantasy Portrait",
                    "Studio Ghibli",
                    "50s Enamel Sign",
                    "Vintage Comic",
                    "Franco-Belgian Comic",
                    "Tintin Comic",
                    "Medieval",
                    "Pixel Art",
                    "Furry - Oil",
                    "Furry - Cinematic",
                    "Furry - Painted",
                    "Furry - Drawn",
                    "Cute Figurine",
                    "3D Emoji",
                    "Illustration",
                    "Flat Illustration",
                    "Watercolor",
                    "1990s Photo",
                    "1980s Photo",
                    "1970s Photo",
                    "1960s Photo",
                    "1950s Photo",
                    "1940s Photo",
                    "1930s Photo",
                    "1920s Photo",
                    "Vintage Pulp Art",
                    "50s Infomercial Anime",
                    "3D Pokemon",
                    "Painted Pokemon",
                    "2D Pokemon",
                    "Vintage Anime",
                    "Neon Vintage Anime",
                    "Manga",
                    "Fantasy World Map",
                    "Fantasy City Map",
                    "Old World Map",
                    "3D Isometric Icon",
                    "Flat Style Icon",
                    "Flat Style Logo",
                    "Game Art Icon",
                    "Digital Painting Icon",
                    "Concept Art Icon",
                    "Cute 3D Icon",
                    "Cute 3D Icon 𝗦𝗲𝘁",
                    "Crayon Drawing",
                    "Pencil",
                    "Tattoo Design",
                    "Waifu",
                    "YuGiOh Art",
                    "Traditional Japanese",
                    "Nihonga Painting",
                    "Claymation",
                    "Cartoon",
                    "Cursed Photo",
                    "MTG Card"
                ]

        self.style_combo = ctk.CTkComboBox(params_frame, values=styles, width=150)
        self.style_combo.pack(side="left", padx=5)
        self.style_combo.set("Painted Anime")  # Set default style
        
        ctk.CTkLabel(params_frame, text="Guidance Scale:").pack(side="left", padx=5)
        self.guidance_entry = ctk.CTkEntry(params_frame, placeholder_text="7.0", width=60)
        self.guidance_entry.pack(side="left", padx=5)

        # Negative Prompt
        neg_frame = ctk.CTkFrame(parent)
        neg_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(neg_frame, text="Negative Prompt:").pack(side="left", padx=5)
        self.negative_prompt = ctk.CTkTextbox(neg_frame, height=60, wrap="word")
        self.negative_prompt.pack(side="left", fill="x", expand=True, padx=5)
        
        # Set default negative prompt
        default_negative = (
            "glitched, deep fried, jpeg artifacts, out of focus, gradient, soft focus, "
            "low quality, poorly drawn, blur, grainy fabric texture, text, bad art, "
            "boring colors, blurry platformer screenshot"
        )
        self.negative_prompt.insert("1.0", default_negative)
        
        # Bind CSV entry changes to toggle columns frame
        self.csv_entry.bind('<KeyRelease>', self._toggle_columns_frame)
        
        return [
            ConfigWidget(parent, "output_path", "Output Directory:",
                widget_type=lambda p, **k: self.output_entry),
            ConfigWidget(parent, "csv_path", "CSV File:",
                widget_type=lambda p, **k: self.csv_entry),
            ConfigWidget(parent, "prompt_column", "Prompt Column:",
                widget_type=lambda p, **k: self.prompt_column,
                visible=False),
            ConfigWidget(parent, "name_column", "Name Column:",
                widget_type=lambda p, **k: self.name_column,
                visible=False),
            ConfigWidget(parent, "custom_prompts", "Custom Prompts:",
                widget_type=lambda p, **k: self.prompt_text),
            ConfigWidget(parent, "negative_prompt", "Negative Prompt:",
                widget_type=lambda p, **k: self.negative_prompt),
            ConfigWidget(parent, "resolution", "Resolution:",
                widget_type=lambda p, **k: self.resolution_entry),
            ConfigWidget(parent, "guidance_scale", "Guidance Scale:",
                widget_type=lambda p, **k: self.guidance_entry),
            ConfigWidget(parent, "style", "Style:",
                widget_type=lambda p, **k: self.style_combo,
                visible=False)
        ]

    def _browse_output_path(self):
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            mustexist=False  # Allow selecting non-existing directories
        )
        if directory:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, directory)

    @staticmethod
    def resolution_to_shape(resolution):
        width, height = map(int, resolution.split('x'))
        if width > height:
            return 'landscape'
        elif width < height:
            return 'portrait'
        else:
            return 'square'

    @staticmethod
    def sanitize_filename(word):
        return "".join(c for c in word if c.isalnum() or c in (' ', '_')).rstrip()

    def get_prompts(self, config):
        prompts = []
        
        # Get prompts from CSV if file is provided
        csv_path = config["csv_path"].strip()
        if csv_path and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            prompt_col = config["prompt_column"].strip()
            name_col = config["name_column"].strip()
            
            if prompt_col in df.columns and name_col in df.columns:
                for _, row in df.iterrows():
                    prompts.append({
                        'prompt': row[prompt_col],
                        'name': row[name_col]
                    })
        
        # Get prompts from text area
        custom_prompts = config["custom_prompts"].strip()
        if custom_prompts:
            for i, line in enumerate(custom_prompts.split('\n')):
                if line.strip():
                    prompts.append({
                        'prompt': line.strip(),
                        'name': f'generated_image_{str(uuid.uuid4())}'
                    })
        
        return prompts

    async def generate_and_save_images(self, prompts, output_folder, resolution, guidance_scale, negative_prompt):
        gen = perchance.ImageGenerator()

        for idx, prompt_data in enumerate(prompts):
            name = prompt_data.get('name', f'generated_image_{str(uuid.uuid4())}')
            filename = f"{output_folder}/{self.sanitize_filename(name)}.png"

            # Add style to prompt if not "𝗡𝗼 𝘀𝘁𝘆𝗹𝗲"
            style = self.style_combo.get()
            if style and style != "𝗡𝗼 𝘀𝘁𝘆𝗹𝗲":
                full_prompt = f"({style}) {prompt_data['prompt']}"
            else:
                full_prompt = prompt_data['prompt']

            self.output.insert("end", f"Processing {idx + 1}/{len(prompts)}: {full_prompt}\n")
            
            try:
                async with await gen.image(
                    full_prompt,
                    negative_prompt=negative_prompt,
                    seed=-1,
                    shape=self.resolution_to_shape(resolution),
                    guidance_scale=guidance_scale,
                ) as result:
                    print("result", result)
                    binary = await result.download()
                    image = Image.open(binary)
                    image.save(filename)
                    self.output.insert("end", f"Saved image to {filename}\n")

                sleep_time = random.uniform(2, 5)
                self.output.insert("end", f"Waiting {sleep_time:.2f} seconds...\n")
                time.sleep(sleep_time)

            except Exception as e:
                print("error", e)
                self.output.insert("end", f"Error generating image: {str(e)}\n")
    
    def run_script(self, config):
        try:
            output_dir = config["output_path"].strip()
            if not output_dir:
                self.output.insert("end", "Error: Please select an output directory first!\n")
                return
                
            resolution = config["resolution"].strip() or "512x768"
            guidance_scale = float(config["guidance_scale"] or 7.0)
            negative_prompt = config["negative_prompt"].strip()
            
            prompts = self.get_prompts(config)
            if not prompts:
                raise ValueError("No prompts found! Please provide either a CSV file or custom prompts.")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Run the async generation
            asyncio.run(self.generate_and_save_images(
                prompts, output_dir, resolution, guidance_scale, negative_prompt
            ))
            
            self.output.insert("end", "Asset generation completed!\n")
            
        except Exception as e:
            self.output.insert("end", f"Error: {str(e)}\n")

    def _toggle_columns_frame(self, event=None):
        """Toggle visibility of CSV columns frame based on CSV entry content"""
        if self.csv_entry.get():
            self.csv_columns_frame.pack(fill="x", padx=5, pady=1)
            # Update columns if file exists
            if os.path.exists(self.csv_entry.get()):
                self._update_csv_columns(self.csv_entry.get())
        else:
            self.csv_columns_frame.pack_forget()

def main():
    return AssetAIGenerator()