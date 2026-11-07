import laspy
from pathlib import Path

src = Path(r"D:\Drone_Image_Processing\Align_77_image\output\point_cloud.laz")
dst = Path(r"C:\GeoSense_Agent\data\satellite\point_cloud_full.las")

dst.parent.mkdir(parents=True, exist_ok=True)

with laspy.open(src) as reader:
    with laspy.open(dst, mode="w", header=reader.header) as writer:
        total = 0
        for chunk in reader.chunk_iterator(250000):
            writer.write_points(chunk)
            total += len(chunk)
            print(f"Written: {total:,} points")

print("LAS created:", dst)
print(f"File size: {dst.stat().st_size / 1024**3:.2f} GB")