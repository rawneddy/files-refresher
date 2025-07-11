# Icon Design - File Retention Refresher

## Icon Concept
The icon should convey:
1. File refresh/renewal
2. Time/date modification
3. Document preservation
4. Retro computing aesthetic (matching the UI)

## Design Description

### Primary Design: "Refresh Clock Document"
- **Base**: Folder or document icon
- **Overlay**: Circular refresh arrows (⟳) 
- **Accent**: Small clock or calendar in corner
- **Color Scheme**: 
  - Primary: Green (#33FF33) matching retro UI
  - Secondary: White/light gray for contrast
  - Background: Dark gray or black

### Visual Elements
```
┌─────────────┐
│ ┌─┐         │
│ │📄│    ⟳   │
│ └─┘         │
│      🕐     │
└─────────────┘
```

## Icon Sizes Required
Windows .ico files should contain multiple resolutions:
- 16x16 (small icons)
- 32x32 (desktop)
- 48x48 (large view)
- 64x64 (extra large)
- 256x256 (Windows 10/11)

## Creating the Icon

### Method 1: Using Python (Pillow)
Create `create_icon.py`:
```python
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
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
    doc_width = 120
    doc_height = 150
    doc_x = (size - doc_width) // 2
    doc_y = 40
    
    # Draw document
    draw.rectangle(
        [(doc_x, doc_y), (doc_x + doc_width, doc_y + doc_height)],
        fill=(255, 255, 255, 255),
        outline=(51, 255, 51, 255),
        width=3
    )
    
    # Document fold corner
    fold_size = 25
    draw.polygon([
        (doc_x + doc_width - fold_size, doc_y),
        (doc_x + doc_width, doc_y + fold_size),
        (doc_x + doc_width - fold_size, doc_y + fold_size)
    ], fill=(200, 200, 200, 255))
    
    # Draw refresh arrows (circular arrows)
    center_x = doc_x + doc_width + 40
    center_y = doc_y + doc_height // 2
    radius = 35
    
    # Arrow arc
    draw.arc(
        [(center_x - radius, center_y - radius), 
         (center_x + radius, center_y + radius)],
        start=30, end=330, 
        fill=(51, 255, 51, 255), 
        width=8
    )
    
    # Arrow head
    arrow_size = 15
    draw.polygon([
        (center_x + radius - 5, center_y - 10),
        (center_x + radius + 10, center_y),
        (center_x + radius - 5, center_y + 10)
    ], fill=(51, 255, 51, 255))
    
    # Clock icon in bottom
    clock_x = doc_x + doc_width // 2
    clock_y = doc_y + doc_height + 20
    clock_radius = 20
    
    # Clock circle
    draw.ellipse(
        [(clock_x - clock_radius, clock_y - clock_radius),
         (clock_x + clock_radius, clock_y + clock_radius)],
        fill=(255, 255, 255, 255),
        outline=(51, 255, 51, 255),
        width=2
    )
    
    # Clock hands
    draw.line([(clock_x, clock_y), (clock_x, clock_y - 12)], 
              fill=(51, 255, 51, 255), width=2)
    draw.line([(clock_x, clock_y), (clock_x + 8, clock_y + 5)], 
              fill=(51, 255, 51, 255), width=2)
    
    # Save multiple sizes
    sizes = [16, 32, 48, 64, 128, 256]
    icons = []
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Save as ICO
    icons[5].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("Icon created successfully: icon.ico")

if __name__ == "__main__":
    create_icon()
```

### Method 2: Using Online Tools
1. Use tools like:
   - https://www.favicon-generator.org/
   - https://convertico.com/
   - https://icoconvert.com/

2. Upload a PNG design (create in any graphics editor)
3. Generate ICO with multiple sizes

### Method 3: Using Graphics Software
1. **Free Options**:
   - GIMP (Export as .ico)
   - Inkscape (Vector, export to ICO)
   - Paint.NET with ICO plugin

2. **Design Steps**:
   - Create 256x256 canvas
   - Design with vector shapes for scalability
   - Export with all required sizes

## Alternative ASCII Design for Documentation
```
╔═══════════════╗
║   📁 ⟳ 🕐    ║
║               ║
║  REFRESHER    ║
╚═══════════════╝
```

## Icon Usage in Build
Update `build_windows.bat`:
```batch
pyinstaller --onefile ^
    --name file_refresher ^
    --icon=icon.ico ^
    --add-data "config.yaml;." ^
    file_refresher.py
```

## Design Rationale
- **Folder/Document**: Represents files being processed
- **Refresh Arrows**: Indicates updating/refreshing action
- **Clock**: Shows time/date modification aspect
- **Green Color**: Matches retro terminal aesthetic
- **Simple Design**: Clear at small sizes