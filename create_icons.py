#!/usr/bin/env python3
"""
Simple script to create basic PWA icons
"""

def create_svg_icon(size, filename):
    """Create a simple SVG icon for PWA"""
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="{size}" height="{size}" fill="#007bff" rx="{size//8}"/>
    
    <!-- Wallet icon -->
    <g transform="translate({size//4}, {size//4})">
        <!-- Wallet base -->
        <rect width="{size//2}" height="{size//2.5}" fill="white" rx="{size//20}" stroke="none"/>
        
        <!-- Wallet detail -->
        <rect x="{size//20}" y="{size//10}" width="{size//2.5}" height="{size//8}" fill="#007bff" rx="{size//40}"/>
        
        <!-- Money symbol -->
        <text x="{size//4}" y="{size//3.5}" font-family="Arial, sans-serif" 
              font-size="{size//8}" font-weight="bold" text-anchor="middle" fill="#28a745">₹</text>
    </g>
</svg>"""
    
    with open(filename, 'w') as f:
        f.write(svg_content)
    print(f"Created {filename}")

if __name__ == "__main__":
    import os
    
    # Create icons directory if it doesn't exist
    os.makedirs('/Users/arunteja.mididoddy/Documents/arun/expense-calculator/static/icons', exist_ok=True)
    
    # Create different sized icons
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        filename = f'/Users/arunteja.mididoddy/Documents/arun/expense-calculator/static/icons/icon-{size}x{size}.svg'
        create_svg_icon(size, filename)
    
    print("All PWA icons created successfully!")
    print("Note: For production, convert these SVG files to PNG format using:")
    print("  - Online converters like convertio.co")
    print("  - ImageMagick: convert icon.svg icon.png")
    print("  - Inkscape: inkscape icon.svg --export-png=icon.png")
