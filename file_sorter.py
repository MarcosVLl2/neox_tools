import os
import shutil
from tqdm import tqdm


def organize_files(source_dir, target_dir):
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Count total files for the progress bar
    total_files = sum([len(files) for _, _, files in os.walk(source_dir)])

    # Create a progress bar
    with tqdm(total=total_files, unit='file', desc="Organizing") as pbar:
        for root, _, files in os.walk(source_dir):
            for file in files:
                # Get the full path of the file
                file_path = os.path.join(root, file)

                # Get the file extension (convert to lowercase)
                _, extension = os.path.splitext(file)
                extension = extension.lower()

                if extension:
                    # Remove the dot from the extension
                    extension = extension[1:]
                else:
                    # For files without extension
                    extension = 'no_extension'

                # Create a directory for this extension if it doesn't exist
                extension_dir = os.path.join(target_dir, extension)
                os.makedirs(extension_dir, exist_ok=True)

                # Move the file to the appropriate directory
                target_path = os.path.join(extension_dir, file)

                # If a file with the same name already exists, add a number to the filename
                counter = 1
                while os.path.exists(target_path):
                    name, ext = os.path.splitext(file)
                    target_path = os.path.join(extension_dir, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.move(file_path, target_path)

                # Update the progress bar
                pbar.update(1)


def main():
    source_dir = r"res_normal_pack_42"
    target_dir = r"res_normal_sort"

    print(f"Organizing files from {source_dir} to {target_dir}")
    print("This may take a while depending on the number of files...")

    organize_files(source_dir, target_dir)

    print("\nFile organization complete!")


if __name__ == "__main__":
    main()