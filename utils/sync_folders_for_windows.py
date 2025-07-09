import hashlib
import os
import shutil
import yaml

# === Hardcoded Paths ===
SOURCE_DIR = r"C:\Path\To\Source"
DEST_DIR = r"C:\Path\To\Destination"
SOURCE_MD5_FILE = "source_md5.yaml"
DEST_MD5_FILE = "dest_md5.yaml"

# === Utility Functions ===
def compute_md5(filepath, chunk_size=8192):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def get_all_files(base_path):
    """Return a dict of relative_path → md5"""
    file_dict = {}
    for root, _, files in os.walk(base_path):
        for name in files:
            abs_path = os.path.join(root, name)
            rel_path = os.path.relpath(abs_path, base_path)
            md5 = compute_md5(abs_path)
            if md5:
                file_dict[rel_path.replace("\\", "/")] = md5
    return file_dict

def save_md5_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def load_md5_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def sync_files(source_dir, dest_dir, source_md5, dest_md5):
    for rel_path, md5 in source_md5.items():
        dest_file_path = os.path.join(dest_dir, rel_path)
        source_file_path = os.path.join(source_dir, rel_path)
        needs_copy = (
            rel_path not in dest_md5 or
            dest_md5[rel_path] != md5 or
            not os.path.exists(dest_file_path)
        )
        if needs_copy:
            print(f"Copying: {rel_path}")
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
            shutil.copy2(source_file_path, dest_file_path)
        else:
            print(f"Skipping (up to date): {rel_path}")

def sync_progress(source_md5, dest_md5, dest_dir):
    updated_dest_md5 = dest_md5.copy()
    files_still_need_sync = 0

    for rel_path, source_hash in source_md5.items():
        dest_file_path = os.path.join(dest_dir, rel_path)

        if not os.path.exists(dest_file_path):
            files_still_need_sync += 1
            continue

        # If already known and matched, skip
        if rel_path in dest_md5 and dest_md5[rel_path] == source_hash:
            continue

        # Recompute hash and compare
        new_dest_hash = compute_md5(dest_file_path)
        if new_dest_hash == source_hash:
            updated_dest_md5[rel_path] = new_dest_hash
        else:
            files_still_need_sync += 1

    save_md5_file(updated_dest_md5, DEST_MD5_FILE)
    print(f"{files_still_need_sync} file(s) still need syncing.")


# === Main Menu ===
def main():
    print("Select a task:")
    print("1. Generate MD5 list for source")
    print("2. Generate MD5 list for destination")
    print("3. Sync files from source to destination")
    print("4. Sync progress (check only unsynced files)")

    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        print("Generating MD5 list for source...")
        source_files = get_all_files(SOURCE_DIR)
        save_md5_file(source_files, SOURCE_MD5_FILE)
        print(f"Source file list saved to {SOURCE_MD5_FILE}")

    elif choice == "2":
        print("Generating MD5 list for destination...")
        dest_files = get_all_files(DEST_DIR)
        save_md5_file(dest_files, DEST_MD5_FILE)
        print(f"Destination file list saved to {DEST_MD5_FILE}")

    elif choice == "3":
        print("Syncing files...")
        source_files = load_md5_file(SOURCE_MD5_FILE)
        dest_files = load_md5_file(DEST_MD5_FILE)
        sync_files(SOURCE_DIR, DEST_DIR, source_files, dest_files)
        print("Sync complete.")

    elif choice == "4":
        print("Checking sync progress...")
        source_files = load_md5_file(SOURCE_MD5_FILE)
        dest_files = load_md5_file(DEST_MD5_FILE)
        sync_progress(source_files, dest_files, DEST_DIR)

    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()

