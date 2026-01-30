# Setup Guide

## Prerequisites

- Python 3.10 or higher
- Git
- osmium-tool (for OSM data processing)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "Geosquare Data Science Challenge"
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install osmium-tool
```

#### macOS:
```bash
brew install osmium-tool
```

#### Windows:
Download from: https://osmcode.org/osmium-tool/

## Running the Project

The project is organized into 5 phases. **Run them in order**:

| Phase | Where to Run | Type |
|-------|--------------|------|
| Phase 1 | Local Python scripts | Data download & preparation |
| Phase 2 | **Google Earth Engine** + Local notebook | Satellite processing |
| Phase 3 | Local Jupyter notebook | Dasymetric mapping |
| Phase 4 | Local Jupyter notebook | Grid integration |
| Phase 5 | Local Python scripts + LaTeX | Visualizations & memo |

---

### Phase 1: Data Hunt (Download & Prepare Data)

**Step 1: Download BNPB Risk Data** (Required)
```bash
cd phase1_data_hunt/bnpb
python download_risk_bnpb.py
cd ../..
```
Downloads 6 disaster hazard TIF files (~540 MB) from Google Drive.

**Step 2: Validate Boundaries** (Required)
```bash
cd phase1_data_hunt/boundaries
python download_gdb.py
cd ../..
```
Validates boundary files. GeoJSON files are already included, so no download needed.

**Step 3: Extract OpenStreetMap Data** (Required)
```bash
cd phase1_data_hunt/osm
python extract_osm_data.py
cd ../..
```
Auto-detects existing `indonesia-*.osm.pbf` or downloads from Geofabrik (~1.6 GB).
Extracts POI, buildings, and roads for Tangerang Selatan & OKU.

**Step 4: Download RTRW Zoning** (Optional - data already included)
```bash
cd phase1_data_hunt/rtrw
python download_rtrw.py
cd ../..
```

---

### Phase 2: Satellite Data (⚠️ Runs in Google Earth Engine)

**IMPORTANT**: Phase 2 satellite processing runs entirely in **Google Earth Engine Code Editor**, not locally.

**Step 1: Export Satellite Data in GEE**
1. Open [Google Earth Engine Code Editor](https://code.earthengine.google.com/)
2. Create a new script and copy-paste from:
   - `phase2_satellite/scripts/gee_lulc_random_forest.js` (LULC classification)
   - `phase2_satellite/scripts/gee_viirs_nightlights.js` (Night lights)
3. Run each script and export to Google Drive
4. Download exported TIF files to:
   - `phase2_satellite/data/lulc/` (LULC files)
   - `phase2_satellite/data/nightlights/` (night lights files)

**Step 2: RTRW Validation** (Local Jupyter Notebook)
```bash
cd phase2_satellite/rtrw_validation
jupyter notebook comparison_pola_ruang.ipynb
# Run all cells
cd ../..
```

---

### Phase 3: Dasymetric Mapping (Population Distribution)

```bash
cd phase3_dasymetric
jupyter notebook dasymetric_mapping.ipynb
# Run all cells to disaggregate census data to 50m × 50m grids
cd ..
```

**Outputs**: Population grids saved to `phase3_dasymetric/outputs/`

---

### Phase 4: Grid Integration (Merge All Data Layers)

```bash
cd phase4_grid_integration
jupyter notebook grid_data_integration.ipynb
# Run all cells to integrate 8 data layers into geosquare grid
cd ..
```

**Outputs**:
- `outputs/grid_tangsel_integrated.parquet` (67K grids)
- `outputs/grid_oku_integrated.parquet` (1.5M grids)

---

### Phase 5: Investment Analysis (Visualizations & Memo)

**Step 1: Generate Maps**
```bash
cd phase5_investment_memo
python scripts/generate_grid_maps.py          # 8 visualization maps
python scripts/generate_business_gap.py       # Business gap chart
```

**Step 2: Compile Investment Memo**
```bash
cd latex
pdflatex oku_investment_memo.tex              # Generates 2-page PDF
cd ../..
```

**Final Output**: `phase5_investment_memo/latex/oku_investment_memo.pdf` ⭐

## Project Structure

```
Geosquare Data Science Challenge/
├── phase1_data_hunt/        # Data collection and preparation
│   ├── boundaries/          # Administrative boundaries
│   ├── osm/                 # OpenStreetMap data
│   ├── population/          # Population census data
│   ├── bnpb/                # Disaster risk data
│   └── rtrw/                # Spatial planning zones
├── phase2_satellite/        # Satellite imagery analysis
├── phase3_dasymetric/       # Population mapping
├── phase4_grid_integration/ # Data layer integration
├── phase5_investment_memo/  # Final analysis
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # Project overview
```

## Data Storage

Large data files (.pbf, .tif, .geojson) are stored locally and excluded from Git.

The project uses relative paths throughout, so it will work regardless of where you clone it.

## Troubleshooting

### Import Error: "No module named 'geosquare_grid'"

Install the geosquare-grid library:
```bash
pip install geosquare-grid
```

### BNPB Download Fails

If `download_risk_bnpb.py` fails:
1. Check your internet connection
2. Follow manual download instructions in `phase1_data_hunt/bnpb/README_DOWNLOAD.md`
3. Download from OneDrive link and extract to `phase1_data_hunt/bnpb/inarisk/`

The script automatically handles nested folder issues during extraction.

### GDB Boundary Files Missing

If `download_gdb.py` reports missing files:
1. **Recommended**: Use existing GeoJSON files (already included in repository)
2. **Optional**: Download GDB files manually from OneDrive (see `phase1_data_hunt/boundaries/README_DOWNLOAD_GDB.md`)

The script automatically fixes nested folder extraction if you download manually.

### OSM Download Fails

If `extract_osm_data.py` fails to download:
1. Check your internet connection
2. Manually download from: https://download.geofabrik.de/asia/indonesia-latest.osm.pbf
3. Place it in: `phase1_data_hunt/osm/indonesia-latest.osm.pbf`
4. Run the script again (it will auto-detect the existing file)

### "osmium not found" Error

Install osmium-tool using your system package manager:
- **Ubuntu/Debian**: `sudo apt-get install osmium-tool`
- **macOS**: `brew install osmium-tool`
- **Windows**: Download from https://osmcode.org/osmium-tool/

### Google Earth Engine Access Required

Phase 2 requires a Google Earth Engine account:
1. Sign up at: https://earthengine.google.com/
2. Wait for approval (usually instant for research/education)
3. Access Code Editor at: https://code.earthengine.google.com/

### Missing tqdm Module

If you see `ModuleNotFoundError: No module named 'tqdm'`:
```bash
pip install tqdm
```

The download scripts will still work without tqdm (just without progress bars).

## Contributing

Feel free to submit issues or pull requests!

## License

[Add your license here]
