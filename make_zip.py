import os
import zipfile

src_dir = r"d:\Download\mv-baldal"
zip_path = r"d:\Download\mv-baldal\mv-baldal.zip"

exclude_dirs = {"bin", "obj", ".vs", ".git", ".vscode", "__pycache__"}
exclude_files = {"mv-baldal.zip", "test.html", "test.pdf", "index.html", "download.html", "create_download_page.py", "make_zip.py"}

file_count = 0
total_raw_size = 0

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
    for root, dirs, files in os.walk(src_dir):
        # Exclude specified directories in-place
        dirs[:] = [d for d in dirs if d.lower() not in exclude_dirs]
        
        for file in files:
            if file.lower() in exclude_files:
                continue
            
            full_path = os.path.join(root, file)
            # Calculate archive path starting with mv-baldal/
            rel_path = os.path.relpath(full_path, src_dir)
            arc_name = os.path.join("mv-baldal", rel_path)
            
            zipf.write(full_path, arc_name)
            file_count += 1
            total_raw_size += os.path.getsize(full_path)

zip_size = os.path.getsize(zip_path)
print(f"Files zipped: {file_count}")
print(f"Raw Size: {total_raw_size / (1024*1024):.2f} MB")
print(f"Zip Size: {zip_size / (1024*1024):.2f} MB ({zip_size} bytes)")
