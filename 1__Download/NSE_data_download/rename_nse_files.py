import os
import re
from pathlib import Path


def rename_nse_files(directory_path):
    """
    Renames NSE archive files from DDMMYYYY format to YYYYMMDD format for proper chronological sorting.

    Args:
        directory_path: Path to the directory containing the files
    """
    directory = Path(directory_path)

    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist")
        return

    # Pattern to match files like: Reports-Archives-Multiple-DDMMYYYY.zip
    pattern = r'^(Reports-Archives-Multiple-)(\d{2})(\d{2})(\d{4})(\.zip)$'

    renamed_count = 0
    skipped_count = 0

    for file in directory.iterdir():
        if not file.is_file():
            continue

        match = re.match(pattern, file.name)

        if match:
            prefix = match.group(1)  # "Reports-Archives-Multiple-"
            day = match.group(2)      # DD
            month = match.group(3)    # MM
            year = match.group(4)     # YYYY
            extension = match.group(5) # ".zip"

            # New format: YYYYMMDD
            new_name = f"{prefix}{year}{month}{day}{extension}"
            new_path = directory / new_name

            # Check if target file already exists
            if new_path.exists():
                print(f"Skipped (target exists): {file.name}")
                skipped_count += 1
                continue

            # Rename the file
            file.rename(new_path)
            print(f"Renamed: {file.name} -> {new_name}")
            renamed_count += 1

    print(f"\nSummary:")
    print(f"  Renamed: {renamed_count} files")
    print(f"  Skipped: {skipped_count} files")


if __name__ == "__main__":
    # Directory containing the NSE files
    nse_directory = r"D:\Programming\NSE_Data\nse_downloads"

    print(f"Starting file rename in: {nse_directory}\n")
    rename_nse_files(nse_directory)
    print("\nDone!")