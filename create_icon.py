#!/usr/bin/env python3
"""
Create icon.ico for File Retention Refresher
Generates a retro-style icon with file refresh theme
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create retro-style icon for the application"""
    # Create base image (256x256 for highest quality)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background - dark square with rounded corners
    draw.rounded_rectangle(
        [(10, 10), (size-10, size-10)], 
        radius=20, 
        fill=(40, 40, 40, 255),
        outline=(51, 255, 51, 255),
        width=4
    )
    
    # Document shape
    doc_width = 100
    doc_height = 130
    doc_x = (size - doc_width) // 2 - 20
    doc_y = 50
    
    # Draw document
    draw.rectangle(
        [(doc_x, doc_y), (doc_x + doc_width, doc_y + doc_height)],
        fill=(255, 255, 255, 255),
        outline=(51, 255, 51, 255),
        width=3
    )
    
    # Document fold corner
    fold_size = 20
    draw.polygon([
        (doc_x + doc_width - fold_size, doc_y),
        (doc_x + doc_width, doc_y + fold_size),
        (doc_x + doc_width - fold_size, doc_y + fold_size)
    ], fill=(200, 200, 200, 255))
    
    # Draw text lines on document
    for i in range(6):
        y = doc_y + 25 + (i * 15)
        draw.rectangle(
            [(doc_x + 15, y), (doc_x + doc_width - 25, y + 3)],
            fill=(51, 255, 51, 255)
        )
    
    # Draw refresh arrows (circular arrows)
    center_x = doc_x + doc_width + 35
    center_y = doc_y + doc_height // 2
    radius = 30
    
    # Arrow arc
    draw.arc(
        [(center_x - radius, center_y - radius), 
         (center_x + radius, center_y + radius)],
        start=30, end=330, 
        fill=(51, 255, 51, 255), 
        width=6
    )
    
    # Arrow head
    arrow_size = 12
    draw.polygon([
        (center_x + radius - 3, center_y - 8),
        (center_x + radius + 8, center_y),
        (center_x + radius - 3, center_y + 8)
    ], fill=(51, 255, 51, 255))
    
    # Clock icon in bottom
    clock_x = doc_x + doc_width // 2
    clock_y = doc_y + doc_height + 25
    clock_radius = 18
    
    # Clock circle
    draw.ellipse(
        [(clock_x - clock_radius, clock_y - clock_radius),
         (clock_x + clock_radius, clock_y + clock_radius)],
        fill=(255, 255, 255, 255),
        outline=(51, 255, 51, 255),
        width=3
    )
    
    # Clock hands
    draw.line([(clock_x, clock_y), (clock_x, clock_y - 10)], 
              fill=(51, 255, 51, 255), width=3)
    draw.line([(clock_x, clock_y), (clock_x + 6, clock_y + 4)], 
              fill=(51, 255, 51, 255), width=2)
    
    # Center dot
    draw.ellipse(
        [(clock_x - 2, clock_y - 2), (clock_x + 2, clock_y + 2)],
        fill=(51, 255, 51, 255)
    )
    
    # Save multiple sizes for ICO format
    sizes = [16, 32, 48, 64, 128, 256]
    icons = []
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Save as ICO
    icons[5].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("Icon created successfully: icon.ico")
    
    # Also save as PNG for reference
    img.save('icon.png', format='PNG')
    print("Reference PNG created: icon.png")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("Error: Pillow library not found. Install with: pip install Pillow")
    except Exception as e:
        print(f"Error creating icon: {e}")