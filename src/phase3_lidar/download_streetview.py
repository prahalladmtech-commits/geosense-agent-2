import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

MAPILLARY_TOKEN = os.getenv("MAPILLARY_TOKEN")

if not MAPILLARY_TOKEN:
    raise RuntimeError(
        "MAPILLARY_TOKEN not found in .env. "
        "Please add your Mapillary access token."
    )


IMAGE_DIR = Path("data/streetview/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def find_images_in_bbox(min_lon, min_lat, max_lon, max_lat, limit=20):
    """Find Mapillary images inside a bounding box."""

    url = "https://graph.mapillary.com/images"

    params = {
        "access_token": MAPILLARY_TOKEN,
        "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "limit": limit,
        "fields": "id,thumb_2048_url,geometry,compass_angle,captured_at",
    }

    response = requests.get(url, params=params, timeout=30)

    if response.status_code != 200:
        print("Mapillary API error:")
        print(response.status_code)
        print(response.text)
        response.raise_for_status()

    return response.json().get("data", [])


def download_image(image_meta, save_dir):
    """Download one Mapillary image."""

    image_id = image_meta["id"]
    image_url = image_meta.get("thumb_2048_url")

    if not image_url:
        print(f"No image URL for {image_id}")
        return None

    output_file = Path(save_dir) / f"{image_id}.jpg"

    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    output_file.write_bytes(response.content)

    print(f"Saved: {output_file}")

    return output_file


if __name__ == "__main__":

    # Small test area from the Phase 3 laboratory manual
    min_lon = 80.24
    min_lat = 13.05
    max_lon = 80.25
    max_lat = 13.06

    images = find_images_in_bbox(
        min_lon,
        min_lat,
        max_lon,
        max_lat,
        limit=20,
    )

    print(f"Found {len(images)} images")

    for image in images:
        download_image(image, IMAGE_DIR)

    print("Street imagery download completed.")