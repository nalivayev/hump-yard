"""
Plugin template for EXIF data extraction from images.
This is a starter template that will be fully implemented later.
Requires PIL/Pillow library: pip install Pillow
"""
from ..base_plugin import FileProcessorPlugin
from pathlib import Path
from typing import Dict, Any
import json


class ExifPlugin(FileProcessorPlugin):
    """
    Plugin template for extracting EXIF data from images.
    Requires PIL/Pillow library: pip install Pillow
    TODO: Full implementation coming soon.
    """
    
    @property
    def name(self) -> str:
        return "exif"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_handle(self, file_path: str) -> bool:
        """
        Check if the file is an image.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if the file is a supported image format, False otherwise.
        """
        valid_extensions = {'.jpg', '.jpeg', '.tiff', '.tif', '.png'}
        return Path(file_path).suffix.lower() in valid_extensions
    
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        """
        Extract EXIF data from image and save it to a JSON file.
        
        Configuration parameters:
        - output_dir: Directory to save JSON files (optional)
        
        Args:
            file_path: Path to the image file to process.
            config: Plugin configuration.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Try to import PIL
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
            except ImportError:
                self.logger.error("PIL/Pillow not installed. Run: pip install Pillow")
                return False
            
            file_path_obj = Path(file_path)
            
            # Open image
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                
                if not exif_data:
                    self.logger.warning(f"No EXIF data found in {file_path_obj.name}")
                    return True
                
                # Convert EXIF data to readable format
                exif_readable = {
                    TAGS.get(tag, tag): str(value)
                    for tag, value in exif_data.items()
                }
                
                # Determine output path for JSON
                output_dir = config.get('output_dir')
                if output_dir:
                    output_path = Path(output_dir) / f"{file_path_obj.stem}_exif.json"
                else:
                    output_path = file_path_obj.with_suffix('.exif.json')
                
                # Save EXIF data to JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(exif_readable, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"EXIF data saved to {output_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to extract EXIF from {file_path}: {e}")
            return False
