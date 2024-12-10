from PIL import Image, ImageDraw
import os

def create_app_icon():
    # Create a 256x256 image with transparent background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Colors
    primary_color = (52, 131, 235)  # Blue
    secondary_color = (235, 89, 52)  # Red
    accent_color = (52, 235, 131)   # Green
    
    # Draw main circle (game board)
    margin = size * 0.1
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill=primary_color)
    
    # Draw game pieces
    # Piece 1 (triangle)
    piece_size = size * 0.2
    triangle_points = [
        (size * 0.3, size * 0.4),
        (size * 0.5, size * 0.2),
        (size * 0.7, size * 0.4)
    ]
    draw.polygon(triangle_points, fill=secondary_color)
    
    # Piece 2 (square)
    square_size = size * 0.15
    square_pos = [
        size * 0.4, size * 0.5,
        size * 0.4 + square_size, size * 0.5 + square_size
    ]
    draw.rectangle(square_pos, fill=accent_color)
    
    # Create directories if they don't exist
    icon_dir = os.path.join("assets_static", "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # Save as PNG
    png_path = os.path.join(icon_dir, "app_icon.png")
    image.save(png_path, "PNG")
    
    # Save as ICO
    ico_path = os.path.join(icon_dir, "app_icon.ico")
    # Create multiple sizes for ICO file
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    for size in sizes:
        resized_image = image.resize(size, Image.Resampling.LANCZOS)
        images.append(resized_image)
    
    # Save ICO with multiple sizes
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    
    print(f"Icons created successfully:")
    print(f"PNG: {png_path}")
    print(f"ICO: {ico_path}")

if __name__ == "__main__":
    create_app_icon() 