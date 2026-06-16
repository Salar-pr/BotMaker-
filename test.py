import os

current_dir = os.getcwd()

jpg_files = [f for f in os.listdir(current_dir)
             if os.path.isfile(os.path.join(current_dir, f)) and f.lower().endswith('.jpg')]
for i, filename in enumerate(jpg_files):
    temp_name = f"temp_rename_{i}.tmp"
    os.rename(os.path.join(current_dir, filename), os.path.join(current_dir, temp_name))
temp_files = [f for f in os.listdir(current_dir) if f.startswith("temp_rename_")]
for i, temp_file in enumerate(temp_files, start=1):
    new_name = f"{i}.jpg"
    os.rename(os.path.join(current_dir, temp_file), os.path.join(current_dir, new_name))


