from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
import json
import os
from PIL import Image
import customtkinter as ctk

@dataclass
class Asset:
    asset_id: Optional[int]
    name: str
    file_path: str
    file_type: str
    metadata: Dict
    uploaded_at: datetime
    _preview_image: Optional[ctk.CTkImage] = None
    
    @property
    def id(self) -> Optional[int]:
        """Alias for asset_id to maintain compatibility"""
        return self.asset_id
    
    @classmethod
    def from_db_row(cls, row):
        try:
            metadata = json.loads(row[4]) if row[4] else {}
        except json.JSONDecodeError:
            metadata = {}
        
        # Fix the file path and type
        name = row[1]
        base_path = 'assets'
        
        # Construct proper file path
        if row[3] and '/' in row[3]:  # If file_type contains a path
            file_path = row[3]
        else:
            # Ensure the path starts with 'assets/'
            file_path = os.path.join(base_path, name)
        
        # Get file type from the file name
        file_type = os.path.splitext(name)[1].lower().replace('.', '')
        if not file_type:  # If no extension in name, try to get it from file_path
            file_type = os.path.splitext(file_path)[1].lower().replace('.', '')
        
        # Debug print
        print(f"\nProcessing asset from DB:")
        print(f"Name: {name}")
        print(f"Constructed path: {file_path}")
        print(f"File type: {file_type}")
        
        uploaded_at = None
        if metadata and 'created' in metadata:
            try:
                uploaded_at = datetime.fromisoformat(metadata['created'])
            except (ValueError, TypeError):
                uploaded_at = datetime.now()
        else:
            uploaded_at = datetime.now()
        
        return cls(
            asset_id=row[0],
            name=name,
            file_path=file_path,
            file_type=file_type,
            metadata=metadata,
            uploaded_at=uploaded_at
        )
    
    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'metadata': self.metadata,
            'uploaded_at': self.uploaded_at.isoformat()
        }
    
    @property
    def preview_image(self) -> Optional[ctk.CTkImage]:
        if self._preview_image is None:
            try:
                # Ensure the file path is correct
                if not os.path.exists(self.file_path):
                    # Try different path combinations
                    possible_paths = [
                        self.file_path,
                        os.path.join('assets', self.name),
                        os.path.join('assets', f"{self.name}.{self.file_type}"),
                        os.path.join('assets', self.file_path)
                    ]
                    
                    print(f"\nLooking for image file:")
                    print(f"Original path: {self.file_path}")
                    
                    for path in possible_paths:
                        print(f"Trying: {path}")
                        if os.path.exists(path):
                            self.file_path = path
                            print(f"Found file at: {path}")
                            break
                    else:
                        print("Could not find image file in any expected location")
                        return None
                
                # Load and process the image
                print(f"Loading image from: {self.file_path}")
                pil_image = Image.open(self.file_path)
                original_size = pil_image.size
                print(f"Original size: {original_size}")
                
                # Create thumbnail
                pil_image.thumbnail((100, 100))
                print(f"Thumbnail size: {pil_image.size}")
                
                self._preview_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=pil_image.size
                )
                print("Successfully created preview image")
                
            except Exception as e:
                print(f"Error creating preview for {self.name}: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
        return self._preview_image
    
    def get_full_image(self) -> Optional[ctk.CTkImage]:
        """Get full-size image"""
        if os.path.exists(self.file_path):
            try:
                pil_image = Image.open(self.file_path)
                return ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=pil_image.size
                )
            except Exception as e:
                print(f"Error loading full image for {self.name}: {str(e)}")
        return None