import pandas as pd
from typing import List, Dict
import json
import os

class SpreadsheetHandler:
    def __init__(self):
        self.supported_formats = ['.xlsx', '.csv', '.xls']
    
    def import_spreadsheet(self, file_path: str) -> List[Dict]:
        """Import data from a spreadsheet file"""
        _, ext = os.path.splitext(file_path)
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}")
        
        try:
            # Read spreadsheet
            if ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Convert to list of dictionaries
            return df.to_dict('records')
        
        except Exception as e:
            raise Exception(f"Error importing spreadsheet: {str(e)}")
    
    def export_to_spreadsheet(self, data: List[Dict], output_path: str, format: str = 'xlsx'):
        """Export data to a spreadsheet file"""
        try:
            df = pd.DataFrame(data)
            
            if format == 'csv':
                df.to_csv(output_path, index=False)
            else:
                df.to_excel(output_path, index=False)
            
            return output_path
        
        except Exception as e:
            raise Exception(f"Error exporting to spreadsheet: {str(e)}")
    
    def validate_spreadsheet_format(self, data: List[Dict], required_fields: List[str]) -> bool:
        """Validate if spreadsheet data contains required fields"""
        if not data:
            return False
        
        sample_row = data[0]
        return all(field in sample_row for field in required_fields) 