"""
Boundary GDB Data Setup & Validation

Checks for geodatabase boundary files and provides download instructions if missing.
Due to OneDrive download restrictions, manual download is required.

Note: GeoJSON files are already available and can be used instead of GDB format.
"""

from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
DOWNLOAD_LINK = "https://1drv.ms/u/c/2951954661ea6560/IQA7B9p2MbFsRrhe0kxuZEsMAahnHgUJoLImWkOyTIpIZVI?e=dYzz81"

print("="*70)
print("Boundary GDB Data Setup & Validation")
print("="*70)
print()


def check_gdb_data():
    """Check if GDB boundary data exists and fix nested folders if needed"""
    # Check for nested extraction (boundaries/boundaries/)
    nested_dir = SCRIPT_DIR / "boundaries"
    if nested_dir.exists() and nested_dir.is_dir():
        import shutil
        print(f"ℹ Detected nested 'boundaries/' folder, moving files up...")
        moved_count = 0
        for item in nested_dir.iterdir():
            target = SCRIPT_DIR / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
                moved_count += 1
        if moved_count > 0:
            try:
                nested_dir.rmdir()
                print(f"✓ Moved {moved_count} items from nested folder")
            except OSError:
                print(f"✓ Moved {moved_count} items (nested folder not empty, keeping it)")
        print()

    gdb_folders = list(SCRIPT_DIR.glob("*.gdb"))
    geojson_files = list(SCRIPT_DIR.glob("*.geojson"))
    return gdb_folders, geojson_files


def print_download_instructions():
    """Print manual download instructions"""
    print("ℹ GDB geodatabase files not found")
    print()
    print("=" * 70)
    print("OPTIONS")
    print("=" * 70)
    print()
    print("Option 1: Use existing GeoJSON files (Recommended)")
    print("  The repository already includes boundary data in GeoJSON format,")
    print("  which works with all scripts and is easier to use.")
    print()
    print("Option 2: Download GDB files manually")
    print("  If you specifically need GDB format:")
    print()
    print("  1. Open this link in your browser:")
    print(f"     {DOWNLOAD_LINK}")
    print()
    print("  2. Click 'Download' and save the ZIP file")
    print()
    print("  3. Extract to this folder:")
    print(f"     {SCRIPT_DIR}")
    print()
    print("  4. Run this script again to validate:")
    print("     python download_gdb.py")
    print()
    print("=" * 70)
    print()
    print("See README_DOWNLOAD_GDB.md for detailed instructions")


def main():
    """Main execution"""
    gdb_folders, geojson_files = check_gdb_data()

    if geojson_files:
        print("✅ GeoJSON BOUNDARY FILES FOUND")
        print("=" * 70)
        print()
        print(f"📁 Location: {SCRIPT_DIR}")
        print(f"📊 Total files: {len(geojson_files)}")
        print()
        print("Available boundary files:")
        for gj in sorted(geojson_files):
            size_mb = gj.stat().st_size / (1024*1024)
            print(f"  ✓ {gj.name} ({size_mb:.2f} MB)")
        print()
        print("These GeoJSON files are ready to use and don't require GDB download.")
        print()

        if gdb_folders:
            print(f"Also found {len(gdb_folders)} GDB folder(s):")
            for gdb in sorted(gdb_folders):
                print(f"  ✓ {gdb.name}")
            print()

        return True

    if gdb_folders:
        print("✅ GDB BOUNDARY FILES FOUND")
        print("=" * 70)
        print()
        print(f"📁 Location: {SCRIPT_DIR}")
        print(f"📊 Total GDB folders: {len(gdb_folders)}")
        print()
        print("Available GDB folders:")
        for gdb in sorted(gdb_folders):
            print(f"  ✓ {gdb.name}")
        print()
        return True

    # No data found
    print_download_instructions()
    return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
