# Boundary GDB Data - Manual Download Instructions

The boundary geodatabase files are hosted on OneDrive and require manual download.

## 📥 Download Steps:

1. **Click this link:** https://1drv.ms/u/c/2951954661ea6560/IQA7B9p2MbFsRrhe0kxuZEsMAahnHgUJoLImWkOyTIpIZVI?e=dYzz81

2. **Download the file:**
   - Click the "Download" button on the OneDrive page
   - Save the ZIP file to this directory: `phase1_data_hunt/boundaries/`

3. **Extract the files:**
   - Unzip the downloaded file to this folder: `phase1_data_hunt/boundaries/`
   - Run: `unzip boundaries_gdb.zip -d .`
   - Note: The validation script will automatically fix nested folders if needed

4. **Verify the download:**
   ```bash
   python download_gdb.py
   ```

## ✅ Expected Files:

The `boundaries/` folder should contain `.gdb` folders with boundary data (e.g., Tangerang Selatan, OKU, etc.)

## 🔄 Alternative: GeoJSON Files

If you prefer using GeoJSON files instead of GDB format, the repository includes pre-converted GeoJSON files:
- `tangerang_selatan_kelurahan_RBI.geojson`
- `oku_kecamatan_RBI.geojson`

These are sufficient for most analyses and don't require the GDB download.
