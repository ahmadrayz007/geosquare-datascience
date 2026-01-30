"""
Download BNPB Risk Data from Google Drive

Downloads BNPB disaster risk layers (floods, drought, landslide, earthquake, etc.)
from Google Drive if not already present.

Output:
- inarisk/ folder with all risk TIF files
"""

import requests
from pathlib import Path
import zipfile

# Optional import
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
GDRIVE_FILE_ID = "1SAT-Jn33KRfB9v0fbChIrtaHAIuOcvbJ"
GDRIVE_URL = f"https://drive.usercontent.google.com/download?id={GDRIVE_FILE_ID}&export=download&confirm=t"
OUTPUT_DIR = SCRIPT_DIR / "inarisk"
ZIP_FILE = SCRIPT_DIR / "bnpb_risk_data.zip"

EXPECTED_FILES = [
    "inarisk_hazard_floods.tif",
    "inarisk_hazard_drought.tif",
    "inarisk_hazard_landslide.tif",
    "inarisk_hazard_earthquake.tif",
    "inarisk_hazard_extreme_weather.tif",
    "inarisk_hazard_land_forest_fire.tif"
]

print("="*70)
print("BNPB Risk Data Download")
print("="*70)
print()


def download_bnpb_data():
    """Download BNPB risk data from Google Drive"""

    # Check if data already exists
    if OUTPUT_DIR.exists() and list(OUTPUT_DIR.glob("*.tif")):
        tif_count = len(list(OUTPUT_DIR.glob("*.tif")))
        print(f"✓ BNPB risk data already exists: {tif_count} TIF files in {OUTPUT_DIR.name}/")
        return True

    print(f"Downloading BNPB risk data from Google Drive...")
    print(f"Source: Google Drive (File ID: {GDRIVE_FILE_ID})")
    print(f"Target: {ZIP_FILE}")
    print()

    try:
        # Download with progress bar
        response = requests.get(GDRIVE_URL, stream=True, allow_redirects=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        print(f"Downloading ({total_size / (1024*1024):.1f} MB)...")

        if HAS_TQDM:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                with open(ZIP_FILE, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        else:
            # tqdm not available - simple progress
            downloaded = 0
            with open(ZIP_FILE, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (10 * 1024 * 1024) == 0:
                            print(f"  Downloaded: {downloaded / (1024*1024):.1f} MB")

        print(f"✓ Download complete")

        # Extract ZIP file
        print(f"\nExtracting files...")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(OUTPUT_DIR)

        # Handle nested folders (if ZIP contains inarisk/inarisk/)
        nested_dir = OUTPUT_DIR / "inarisk"
        if nested_dir.exists() and nested_dir.is_dir():
            import shutil
            for item in nested_dir.iterdir():
                shutil.move(str(item), str(OUTPUT_DIR / item.name))
            nested_dir.rmdir()
            print(f"✓ Moved files from nested folder")

        # Count extracted files
        tif_files = list(OUTPUT_DIR.glob("*.tif"))
        print(f"✓ Extracted {len(tif_files)} TIF files to {OUTPUT_DIR.name}/")

        # Clean up ZIP file
        ZIP_FILE.unlink()
        print(f"✓ Cleaned up ZIP file")

        return True

    except Exception as e:
        print(f"✗ Error downloading BNPB data: {e}")
        if ZIP_FILE.exists():
            ZIP_FILE.unlink()
        return False


def main():
    """Main execution"""
    if download_bnpb_data():
        print("\n" + "="*70)
        print("BNPB RISK DATA DOWNLOAD COMPLETE")
        print("="*70)
        print(f"\n📁 Data location: {OUTPUT_DIR}")

        # List available risk layers
        tif_files = sorted(OUTPUT_DIR.glob("*.tif"))
        if tif_files:
            print(f"\nAvailable risk layers ({len(tif_files)}):")
            for tif in tif_files:
                size_mb = tif.stat().st_size / (1024*1024)
                print(f"  ✓ {tif.name} ({size_mb:.1f} MB)")
    else:
        print("\n✗ Download failed")


if __name__ == "__main__":
    main()
