from pathlib import Path

p = Path("src/main.js")
s = p.read_text(encoding="utf-8")

marker = "document\n  .querySelector('#load-drone')"

insert = """document.querySelector('#toggle-drone').addEventListener('click', () => {
  if (!droneTileset) return;
  droneTileset.show = !droneTileset.show;
  const visible = droneTileset.show;
  document.querySelector('#toggle-drone').textContent =
    visible ? 'Hide point cloud' : 'Show point cloud';
  document.querySelector('#visibility-status').textContent =
    visible ? 'Point cloud is visible.' : 'Point cloud is hidden.';
});

"""

if marker not in s:
    raise SystemExit("Insertion point not found. No changes made.")

if "querySelector('#toggle-drone').addEventListener" in s:
    raise SystemExit("Toggle logic already exists. No changes made.")

p.write_text(s.replace(marker, insert + marker, 1), encoding="utf-8")
print("Visibility toggle logic added successfully.")