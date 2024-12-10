import os
import pandas as pd
from typing import List, Dict, Optional
import shutil

class CSVController:
    def __init__(self):
        self.data_dir = "./assets_static/data"
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    
    def import_csv(self, file_path: str) -> bool:
        """Import CSV file to data directory"""
        try:
            # Validate file exists and is CSV
            if not os.path.exists(file_path) or not file_path.lower().endswith('.csv'):
                return False
            
            # Copy file to data directory
            filename = os.path.basename(file_path)
            destination = os.path.join(self.data_dir, filename)
            shutil.copy2(file_path, destination)
            
            return True
            
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return False
    
    def get_csv_list(self) -> List[str]:
        """Get list of available CSV files"""
        try:
            return [f for f in os.listdir(self.data_dir) if f.lower().endswith('.csv')]
        except Exception as e:
            print(f"Error getting CSV list: {e}")
            return []
    
    def load_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """Load CSV file and return as DataFrame"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                return pd.read_csv(file_path)
            return None
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
    
    def save_csv(self, filename: str, data: pd.DataFrame) -> bool:
        """Save DataFrame to CSV file"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            data.to_csv(file_path, index=False)
            return True
            
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def get_columns(self, filename: str) -> List[str]:
        """Get column names from CSV file"""
        try:
            df = self.load_csv(filename)
            if df is not None:
                return list(df.columns)
            return []
            
        except Exception as e:
            print(f"Error getting columns: {e}")
            return []
    
    def get_data_preview(self, filename: str, rows: int = 5) -> Optional[pd.DataFrame]:
        """Get preview of CSV data"""
        try:
            df = self.load_csv(filename)
            if df is not None:
                return df.head(rows)
            return None
            
        except Exception as e:
            print(f"Error getting data preview: {e}")
            return None
    
    def delete_csv(self, filename: str) -> bool:
        """Delete CSV file"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting CSV: {e}")
            return False
    
    def validate_csv(self, file_path: str) -> Dict[str, any]:
        """Validate CSV file before import"""
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File does not exist"}
            
            # Check file extension
            if not file_path.lower().endswith('.csv'):
                return {"valid": False, "error": "Not a CSV file"}
            
            # Try to read file
            df = pd.read_csv(file_path)
            
            return {
                "valid": True,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns)
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)} 