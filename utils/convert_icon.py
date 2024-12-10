from PIL import Image
import os

# Convert PNG to ICO
png_path = "assets_static/icons/app_icon.png"
ico_path = "assets_static/icons/app_icon.ico"

if os.path.exists(png_path):
    img = Image.open(png_path)
    img.save(ico_path, format='ICO')
    print(f"PNG to ICO conversion successful: {ico_path}")
else:
    print(f"PNG file not found: {png_path}")