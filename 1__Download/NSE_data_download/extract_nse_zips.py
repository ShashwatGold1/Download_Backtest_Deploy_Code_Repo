import os
import zipfile
from pathlib import Path


def extract_all_zip_files(source_directory, extract_to_directory=None):
    """
    Extracts all zip files in a directory to folders with the same name as the zip file.

    Args:
        source_directory: Path to directory containing zip files
        extract_to_directory: Path where extracted folders will be created (default: same as source)
    """
    source_dir = Path(source_directory)

    if not source_dir.exists():
        print(f"Error: Source directory '{source_directory}' does not exist")
        return

    # Use source directory if extract_to not specified
    if extract_to_directory is None:
        extract_to_directory = source_dir
    else:
        extract_to_directory = Path(extract_to_directory)
        extract_to_directory.mkdir(parents=True, exist_ok=True)

    # Find all zip files
    zip_files = list(source_dir.glob('*.zip'))

    if not zip_files:
        print(f"No zip files found in {source_directory}")
        return

    print(f"Found {len(zip_files)} zip files to extract\n")

    extracted_count = 0
    failed_count = 0
    skipped_count = 0

    for zip_file in zip_files:
        # Create folder name from zip file name (without .zip extension)
        folder_name = zip_file.stem
        extract_path = extract_to_directory / folder_name

        # Skip if already extracted
        if extract_path.exists() and any(extract_path.iterdir()):
            print(f"Skipped (already exists): {folder_name}")
            skipped_count += 1
            continue

        try:
            # Create extraction folder
            extract_path.mkdir(parents=True, exist_ok=True)

            # Extract zip file
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            print(f"Extracted: {zip_file.name} -> {folder_name}/")
            extracted_count += 1

        except Exception as e:
            print(f"Failed: {zip_file.name} - {str(e)}")
            failed_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Extracted: {extracted_count} files")
    print(f"  Skipped:   {skipped_count} files")
    print(f"  Failed:    {failed_count} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Source directory containing zip files
    source_dir = r"D:\Programming\NSE_Data\nse_downloads"

    # Optional: specify different extraction directory
    # extract_dir = r"D:\Programming\NSE_Data\nse_extracted"
    extract_dir = None  # Will extract to same directory as zip files

    print(f"Extracting zip files from: {source_dir}\n")
    extract_all_zip_files(source_dir, extract_dir)
    print("\nDone!")