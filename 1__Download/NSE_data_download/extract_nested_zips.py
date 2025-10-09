import os
import zipfile
from pathlib import Path


def extract_nested_zip_files(root_directory):
    """
    Recursively extracts all zip files including nested zips inside folders.
    Each zip is extracted to a folder with the same name in its parent directory.

    Args:
        root_directory: Root path to start searching for zip files
    """
    root_dir = Path(root_directory)

    if not root_dir.exists():
        print(f"Error: Directory '{root_directory}' does not exist")
        return

    extracted_count = 0
    failed_count = 0
    skipped_count = 0

    # Keep extracting until no more zips are found
    while True:
        # Find all zip files recursively
        zip_files = list(root_dir.rglob('*.zip'))

        if not zip_files:
            break

        print(f"\nFound {len(zip_files)} zip files to extract")

        for zip_file in zip_files:
            # Create folder name from zip file name (without .zip extension)
            folder_name = zip_file.stem
            extract_path = zip_file.parent / folder_name

            # Skip if already extracted
            if extract_path.exists() and any(extract_path.iterdir()):
                print(f"Skipped (already exists): {zip_file.relative_to(root_dir)}")
                skipped_count += 1
                continue

            try:
                # Create extraction folder
                extract_path.mkdir(parents=True, exist_ok=True)

                # Extract zip file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

                print(f"Extracted: {zip_file.relative_to(root_dir)} -> {folder_name}/")
                extracted_count += 1

            except Exception as e:
                print(f"Failed: {zip_file.relative_to(root_dir)} - {str(e)}")
                failed_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Extracted: {extracted_count} files")
    print(f"  Skipped:   {skipped_count} files")
    print(f"  Failed:    {failed_count} files")
    print(f"{'='*60}")


def extract_specific_folder_zips(parent_directory):
    """
    Extracts all zip files that are inside subdirectories.
    Each zip is extracted to a folder with the same name in its parent directory.

    Args:
        parent_directory: Path to parent directory containing folders with zip files
    """
    parent_dir = Path(parent_directory)

    if not parent_dir.exists():
        print(f"Error: Directory '{parent_directory}' does not exist")
        return

    extracted_count = 0
    failed_count = 0
    skipped_count = 0

    # Iterate through all subdirectories
    for subfolder in parent_dir.iterdir():
        if not subfolder.is_dir():
            continue

        print(f"\nProcessing folder: {subfolder.name}")

        # Find zip files in this subfolder
        zip_files = list(subfolder.glob('*.zip'))

        for zip_file in zip_files:
            # Create folder name from zip file name (without .zip extension)
            folder_name = zip_file.stem
            extract_path = zip_file.parent / folder_name

            # Skip if already extracted
            if extract_path.exists() and any(extract_path.iterdir()):
                print(f"  Skipped (already exists): {zip_file.name}")
                skipped_count += 1
                continue

            try:
                # Create extraction folder
                extract_path.mkdir(parents=True, exist_ok=True)

                # Extract zip file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

                print(f"  Extracted: {zip_file.name} -> {folder_name}/")
                extracted_count += 1

            except Exception as e:
                print(f"  Failed: {zip_file.name} - {str(e)}")
                failed_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Extracted: {extracted_count} files")
    print(f"  Skipped:   {skipped_count} files")
    print(f"  Failed:    {failed_count} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Directory containing zip files
    nse_dir = r"D:\Programming\NSE_Data\nse_downloads"

    print("Choose extraction mode:")
    print("1. Extract nested zips recursively (extracts zips inside zips)")
    print("2. Extract zips inside subdirectories only")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        print(f"\nExtracting nested zip files from: {nse_dir}\n")
        extract_nested_zip_files(nse_dir)
    elif choice == "2":
        print(f"\nExtracting zip files from subdirectories in: {nse_dir}\n")
        extract_specific_folder_zips(nse_dir)
    else:
        print("Invalid choice!")

    print("\nDone!")