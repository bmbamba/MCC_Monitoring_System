from PIL import Image, ImageDraw

# Create a 256x256 icon
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw motor body
draw.rounded_rectangle([40, 40, size-40, size-40], radius=30, fill='#3b82f6')

# Draw center circle
center = size//2
draw.ellipse([center-35, center-35, center+35, center+35], fill='white')

# Draw 'M' letter
draw.text((center-20, center-20), "M", fill='#3b82f6', font=None)

# Save as ICO
img.save('app_icon.ico', format='ICO')
print("Icon created: app_icon.ico")