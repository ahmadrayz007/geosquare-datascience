# Phase 2: Satellite Data Processing

**Objective**: Process satellite imagery using supervised classification and extract land use/land cover (LULC) and night lights data.

## Data Sources

### 1. Sentinel-2 LULC Classification (`data/lulc/`)
- **Source**: Sentinel-2 Surface Reflectance (Google Earth Engine)
- **Method**: Random Forest supervised classification with manual training points
- **Resolution**: 10m × 10m
- **Classes**: 7 land cover classes
  - Water, Trees, Flooded Vegetation, Crops, Built Area, Bare Ground, Rangeland
- **Oil Palm**: Separate layer from BIOPAMA (merged with LULC)
- **Export Format**: GeoTIFF
- **Files**:
  - `lulc_tangsel_2025.tif` (213KB)
  - `lulc_oku_2025.tif` (4.9MB)
  - `oku_oilpalm_biopama.tif` (766KB)

### 2. VIIRS Night Lights (`data/nightlights/`)
- **Source**: Google Earth Engine (NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG)
- **Years**: 2020, 2025
- **Purpose**: Economic activity proxy
- **Export Format**: GeoTIFF (10 files - monthly composites)

## Scripts (`scripts/`)

### Google Earth Engine Scripts
- **`gee_lulc_random_forest.js`** - Random Forest LULC classification using Sentinel-2
  - Uses manual training points for both regions
  - 7 land cover classes
  - Cloud masking and median composite

- **`gee_lulc_split_export.js`** - Export LULC for Tangsel and OKU separately
  - Handles large regions with split export
  - Same Random Forest classification

- **`gee_oilpalm_clip.js`** - Clip BIOPAMA oil palm layer to OKU extent
  - Source: BIOPAMA oil palm plantation dataset
  - Merged with main LULC to add oil palm class

- **`gee_viirs_nightlights.js`** - Export VIIRS night lights time series
  - Monthly composites for 2020 and 2025
  - Median reducer to reduce noise

### Processing Scripts
- **`lulc_metadata.py`** - Assign metadata to LULC rasters
  - Add CRS, band names, descriptions
  - Prepare for grid integration

- **`merge_oilpalm_lulc.py`** - Merge oil palm layer with main LULC
  - Adds oil palm as class 12
  - Only for OKU region

- **`assign_raster_metadata.py`** - General raster metadata assignment

### RTRW Validation
**NOTE**: RTRW validation analysis has been moved to **Phase 1** for better organization.

**Location**: `../phase1_data_hunt/rtrw/rtrw_validation/comparison_pola_ruang.ipynb`

This notebook compares official RTRW zoning against satellite LULC to identify:
- **Violations**: Protected→Built (regulatory risk)
- **Opportunities**: Residential→Undeveloped (land banking zones)
- Compliance rate calculation
- Discrepancy visualization maps

## Outputs

### LULC Data (`data/lulc/`)
- Classified land use/land cover rasters (10m resolution)
- 7 base classes + oil palm (OKU only)

### Night Lights (`data/nightlights/`)
- Monthly VIIRS composites (2020, 2025)
- Economic activity indicators

### RTRW Validation
See `../phase1_data_hunt/rtrw/rtrw_validation/` for:
- RTRW vs satellite compliance analysis
- Discrepancy visualization maps
- Investment implications (violations vs opportunities)

## Methodology

### LULC Classification
1. **Training Data Collection**: Manual digitization of training points in GEE
2. **Sentinel-2 Composite**: Cloud-masked median composite (2025)
3. **Random Forest**: Supervised classification with 10 trees
4. **Oil Palm Merge**: Separate oil palm layer from BIOPAMA merged for OKU
5. **Export**: GeoTIFF format for grid integration

### RTRW Validation (See Phase 1)
RTRW validation analysis located in `../phase1_data_hunt/rtrw/rtrw_validation/`

**Methodology**:
1. Spatial Join: Match grid centroids with RTRW polygons
2. Category Mapping: Map RTRW zones to expected LULC classes
3. Discrepancy Detection: Identify mismatches (violations vs opportunities)
4. Compliance Rate: Calculate percentage of compliant grids

**Key Findings**:
- **Tangsel**: 66.4% compliance (33% Protected→Built violations)
- **OKU**: 93.4% compliance (3.4% Residential→Undeveloped opportunities)

**Outputs**:
- `../../output/maps/rtrw_vs_satellite_discrepancy.png` - Dual map comparison
- `../../output/maps/rtrw_compliance_oku_only.png` - OKU-only compliance map

## Notes

- Random Forest classification trained on manually collected points
- Oil palm class only available for OKU (from BIOPAMA dataset)
- LULC classes aligned with analysis needs (agriculture-focused for OKU)
- RTRW validation distinguishes regulatory violations from investment opportunities
- All outputs prepared for Phase 4 grid integration
