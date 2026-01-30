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

The project is organized into 5 phases. Run them in order:

### Phase 1: Data Hunt

Download and prepare all data sources:

```bash
# Download Indonesia OSM data and extract regional data
cd phase1_data_hunt/osm
python3 extract_osm_data.py
```

This will:
- Download Indonesia PBF from Geofabrik (~1.6 GB)
- Extract regional data for Tangerang Selatan & OKU
- Generate building footprints, roads, and POI data

### Phase 2: Satellite Data

Process LULC and nightlights data (if available).

### Phase 3: Dasymetric Mapping

Generate population distribution on Geosquare grid:

```bash
cd phase3_dasymetric
jupyter notebook dasymetric_mapping.ipynb
```

### Phase 4: Grid Integration

Integrate all data layers:

```bash
cd phase4_grid_integration
jupyter notebook grid_data_integration.ipynb
```

### Phase 5: Investment Memo

Generate final analysis and report.

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

### OSM Download Fails

The script automatically downloads Indonesia OSM data from Geofabrik. If the download fails:
1. Check your internet connection
2. Manually download from: https://download.geofabrik.de/asia/indonesia-latest.osm.pbf
3. Place it in: `phase1_data_hunt/osm/indonesia-latest.osm.pbf`

### "osmium not found" Error

Install osmium-tool using your system package manager (see step 4 above).

## Contributing

Feel free to submit issues or pull requests!

## License

[Add your license here]
