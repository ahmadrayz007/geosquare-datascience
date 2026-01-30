# Phase 1: Data Hunt

**Objective**: Collect all raw data sources needed for the analysis.

## Data Sources

### 1. Population Data (`population/`)
- **Tangerang Selatan**: Disdukcapil population data by kelurahan
- **Ogan Komering Ulu**: Disdukcapil population data by kecamatan
- **Format**: CSV with population counts
- **Scripts** (located in `population/` folder):
  - `tablue-scraper.py` - Scrape Tangsel from Tableau dashboard (Playwright)
  - `vision_ocr.py` - Extract OKU from screenshot using AI vision OCR (OpenRouter)

### 2. RTRW - Official Zoning Maps (`rtrw/`)
- **Tangerang Selatan**: RTRW_KOTA_TANGERANG_SELATAN.geojson (25 features)
- **Ogan Komering Ulu**: RTRW_OGAN_KOMERING_ULU.geojson (21 features)
- **Purpose**: Official spatial planning/zoning for validation against satellite data
- **Script** (located in `rtrw/` folder):
  - `download_rtrw.py` - Download RTRW from BIG SatuPeta API
- **Outputs**:
  - `RTRW_KOTA_TANGERANG_SELATAN.geojson`
  - `RTRW_OGAN_KOMERING_ULU.geojson`

#### RTRW Validation Results (`rtrw/rtrw_validation/comparison_pola_ruang.ipynb`)

**Analysis**: Spatial join of 1.5M grid cells with RTRW zoning to detect discrepancies between official plans vs satellite reality.

**Tangerang Selatan (66.4% Compliance)**:
- **Total Grids Analyzed**: 66,769 grids
- **Compliant**: 44,313 grids (66.4%)
- **Discrepancies**: 22,456 grids (33.6%)
  - **Protected→Built**: 22,052 grids (33.03%) - **CRITICAL VIOLATION**
  - Industrial→Undeveloped: 297 grids (0.44%)
  - Residential→Undeveloped: 107 grids (0.16%)
- **Interpretation**: High discrepancy - Protected/Green zones show actual built development (regulatory risk, but strong market demand signal)

**Ogan Komering Ulu (93.4% Compliance)**:
- **Total Grids Analyzed**: 1,492,186 grids
- **Compliant**: 1,394,413 grids (93.4%)
- **Discrepancies**: 97,773 grids (6.6%)
  - **Residential→Undeveloped**: 50,928 grids (3.41%) - **LAND BANKING OPPORTUNITY**
  - Forest→Developed: 28,631 grids (1.92%)
  - Agriculture→Built: 7,420 grids (0.50%)
  - Protected→Built: 6,272 grids (0.42%)
  - Industrial→Undeveloped: 4,522 grids (0.30%)
- **Interpretation**: Low discrepancy - High zoning integrity with pre-approved residential zones awaiting development (first-mover opportunity)

**Visualization Outputs**:
- `output/maps/rtrw_vs_satellite_discrepancy.png` - Dual map comparison (Tangsel + OKU)
- `output/maps/rtrw_compliance_oku_only.png` - OKU-only detailed compliance map

**Investment Implications**:
- **Tangsel**: High regulatory risk (33% violations in protected zones) but proven market demand
- **OKU**: Predictable market with 3.4% pre-approved undeveloped residential zones = land banking targets at rural pricing before urbanization premiums

### 3. Administrative Boundaries (`boundaries/`)
- **Source**: BIG (Badan Informasi Geospasial)
- **Dataset**: RBI10K_ADMINISTRASI_DESA_20230928.gdb (September 2023)
- **Files**: Kelurahan/Desa boundary GeoJSON for both regions
- **Purpose**: Spatial aggregation and administrative context
- **Script** (located in `boundaries/` folder):
  - `extract_boundaries_from_gdb.py` - Extract boundaries from BIG Geodatabase
- **Outputs**:
  - `tangerang_selatan_kelurahan_RBI.geojson` (kelurahan level)
  - `oku_kecamatan_RBI.geojson` (kecamatan or desa level)

### 4. OpenStreetMap Data (`osm/`)
- **Roads**: Road network for infrastructure analysis
- **POI**: Points of Interest (amenities, services, facilities)
- **Buildings**: Building footprints for dasymetric mapping
- **Format**: GeoJSON extracted from OSM PBF
- **Script** (located in `osm/` folder):
  - `extract_osm_data.py` - Extract buildings, roads, and POI from PBF files
- **Outputs**:
  - `osm_business_tangsel.geojson/csv` (1,999 POI)
  - `osm_business_oku.geojson/csv` (131 POI)
  - `osm_buildings_tangsel.geojson` (135k buildings)
  - `osm_buildings_oku.geojson` (70k buildings)
  - `osm_roads_tangsel.geojson` (44k road segments)
  - `osm_roads_oku.geojson` (6.6k road segments)

### 5. BNPB Disaster Hazards (`bnpb/`)
- **Source**: BNPB InaRISK disaster hazard portal
- **Data**: 6 hazard types (floods, drought, landslide, earthquake, extreme weather, fire)
- **Format**: GeoTIFF rasters
- **Script** (located in `bnpb/` folder):
  - `risk_bnpb.py` - Automated download and processing of BNPB hazard rasters
- **Outputs**: `inarisk/` (raster files), `cache/` (cached data)

## Data Collection Methods

All scripts are located in their respective data folders for self-contained organization:

### Automated Scripts
1. **`population/tablue-scraper.py`**
   - Scrapes Tangsel population from Disdukcapil Tableau dashboard
   - Source: https://public.tableau.com/views/DKBSemester1Tahun2025/Statistik
   - Method: Playwright headless browser + JSON parsing
   - Outputs: `penduduk_per_kecamatan.csv`, `penduduk_per_kelurahan.csv`

2. **`population/vision_ocr.py`**
   - Extracts OKU population from screenshot using AI vision
   - Method: OpenRouter API with GLM-4.6V vision model for OCR
   - Input: `disdukcapil_oku.jpeg` (government screenshot)
   - Outputs: `penduduk_oku_vision.csv` (15 kecamatan data)

3. **`rtrw/download_rtrw.py`**
   - Downloads RTRW from BIG SatuPeta REST API
   - Source: BIG PUBLIK/PERENCANAAN_RUANG endpoint
   - Method: HTTP GET requests with region filtering
   - Outputs:
     - `RTRW_KOTA_TANGERANG_SELATAN.geojson` (25 RTRW zones)
     - `RTRW_OGAN_KOMERING_ULU.geojson` (21 RTRW zones)

4. **`boundaries/extract_boundaries_from_gdb.py`**
   - Extracts boundaries from BIG RBI10K Geodatabase
   - Source: `cache/RBI10K_ADMINISTRASI_DESA_20230928.gdb`
   - Method: Fiona/geopandas to read GDB and filter by region keywords
   - Outputs:
     - `tangerang_selatan_kelurahan_RBI.geojson` (kelurahan boundaries)
     - `oku_kecamatan_RBI.geojson` (kecamatan/desa boundaries)

5. **`osm/extract_osm_data.py`**
   - Extracts buildings, roads, and POI from OpenStreetMap PBF files
   - Source: `cache/indonesia-260115.osm.pbf`
   - Method: osmium for regional extraction + pyrosm for data parsing
   - Outputs:
     - Business POI (geojson/csv), buildings, roads for both regions
     - Regional PBF files (tangsel.osm.pbf, oku.osm.pbf)

6. **`bnpb/risk_bnpb.py`**
   - Downloads BNPB InaRISK hazard rasters
   - Method: Automated download from BNPB portal with rasterio processing
   - Outputs: 6 hazard rasters + composite index

### Manual Downloads
- **OSM PBF**: Downloaded indonesia-260115.osm.pbf to `cache/` folder (required for OSM extraction script)
- **RBI GDB**: Downloaded RBI10K_ADMINISTRASI_DESA_20230928.gdb
## Notes

- All raw data should remain in original format
- Document data sources and collection dates
- Keep metadata files for provenance tracking
