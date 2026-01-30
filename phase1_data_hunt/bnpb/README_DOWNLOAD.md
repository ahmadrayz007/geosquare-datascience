# BNPB Risk Data - Manual Download Instructions

The BNPB disaster risk data is hosted on OneDrive and requires manual download due to automated download restrictions.

## 📥 Download Steps:

1. **Click this link:** https://1drv.ms/u/c/2951954661ea6560/IQARgVvtwrt7QYzfDz4poLpYAUK9Yjgj27pTBqMrthLh8r8?e=ignE5b

2. **Download the file:**
   - Click the "Download" button on the OneDrive page
   - Save the ZIP file to this directory: `phase1_data_hunt/bnpb/`

3. **Extract the files:**
   - Unzip the downloaded file to this folder: `phase1_data_hunt/bnpb/`
   - Run: `unzip bnpb_risk_data.zip`
   - Note: The download script automatically handles nested folders

4. **Verify the download:**
   ```bash
   python download_risk_bnpb.py
   ```

## ✅ Expected Files:

The `inarisk/` folder should contain:
- `inarisk_hazard_floods.tif`
- `inarisk_hazard_drought.tif`
- `inarisk_hazard_landslide.tif`
- `inarisk_hazard_earthquake.tif`
- `inarisk_hazard_extreme_weather.tif`
- `inarisk_hazard_land_forest_fire.tif`

## 🔄 Alternative: Use Existing Data

If you already have BNPB risk data from another source, simply place the TIF files in the `inarisk/` folder and the scripts will detect them automatically.
