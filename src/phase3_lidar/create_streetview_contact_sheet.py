from pathlib import Path
from PIL import Image, ImageDraw

IMAGE_DIR = Path("data/streetview/images")
OUTPUT_DIR = Path("data/streetview/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

images = sorted(IMAGE_DIR.glob("*.jpg"))

thumb_width = 400
thumb_height = 225
label_height = 30
columns = 3
rows = (len(images) + columns - 1) // columns

sheet_width = columns * thumb_width
sheet_height = rows * (thumb_height + label_height)

sheet = Image.new("RGB", (sheet_width, sheet_height), "white")
draw = ImageDraw.Draw(sheet)

for index, image_path in enumerate(images):
    image = Image.open(image_path).convert("RGB")
    image.thumbnail((thumb_width, thumb_height))

    x = (index % columns) * thumb_width
    y = (index // columns) * (thumb_height + label_height)

    sheet.paste(image, (x, y))

    draw.text(
        (x + 5, y + thumb_height + 5),
        image_path.name,
        fill="black"
    )

output_file = OUTPUT_DIR / "streetview_contact_sheet.jpg"
sheet.save(output_file, quality=95)

print(f"Created contact sheet for {len(images)} images")
print(f"Saved to: {output_file}")