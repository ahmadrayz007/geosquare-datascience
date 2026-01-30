"""
Export Integrated Grids to Multiple Formats
- CSV (for analysis in pandas/Excel)
- GeoJSON (standard spatial format)
- GeoParquet (efficient spatial format)
"""

import geopandas as gpd
import pandas as pd
import os
from pathlib import Path
from shapely.geometry import box
import warnings
warnings.filterwarnings('ignore')

# Paths (relative to script location)
SCRIPT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = SCRIPT_DIR / 'outputs'

print("=" * 70)
print("EXPORTING INTEGRATED GRIDS TO MULTIPLE FORMATS")
print("=" * 70)
print()

# Load integrated grids
print("Loading integrated grids...")
tangsel = pd.read_csv(OUTPUT_DIR / 'grid_tangsel_integrated.csv')
oku = pd.read_csv(OUTPUT_DIR / 'grid_oku_integrated.csv')

print(f"✓ Tangsel: {len(tangsel):,} grids")
print(f"✓ OKU:     {len(oku):,} grids")
print()

# Grid size (50m x 50m)
GRID_SIZE = 50  # meters

def create_grid_geometry(df):
    """
    Create polygon geometries for each grid cell
    Grid = 50m x 50m square centered at (lon, lat)
    """
    # Calculate half grid size in degrees (approximate)
    # At equator: 1 degree ≈ 111km
    # 25m ≈ 0.000225 degrees
    half_size_deg = 25 / 111000  # ~0.000225 degrees

    geometries = []
    for _, row in df.iterrows():
        lon, lat = row['lon'], row['lat']
        # Create box: (minx, miny, maxx, maxy)
        geom = box(
            lon - half_size_deg,
            lat - half_size_deg,
            lon + half_size_deg,
            lat + half_size_deg
        )
        geometries.append(geom)

    return geometries

# Convert to GeoDataFrame with grid geometries
print("Creating grid geometries...")
print("  (Grid = 50m x 50m squares)")

tangsel_geoms = create_grid_geometry(tangsel)
oku_geoms = create_grid_geometry(oku)

tangsel_gdf = gpd.GeoDataFrame(tangsel, geometry=tangsel_geoms, crs='EPSG:4326')
oku_gdf = gpd.GeoDataFrame(oku, geometry=oku_geoms, crs='EPSG:4326')

print(f"✓ Tangsel geometries created")
print(f"✓ OKU geometries created")
print()

# Export to multiple formats
OUTPUT_DIR.mkdir(exist_ok=True)

print("Exporting files...")
print()

# ========== 1. CSV (already exists, but re-export for consistency) ==========
print("1. CSV (Comma-Separated Values)")
tangsel.to_csv(OUTPUT_DIR / 'grid_tangsel_integrated.csv', index=False)
oku.to_csv(OUTPUT_DIR / 'grid_oku_integrated.csv', index=False)
print(f"   ✓ grid_tangsel_integrated.csv")
print(f"   ✓ grid_oku_integrated.csv")
print(f"   Format: CSV (no geometry)")
print(f"   Use: Pandas, Excel, data analysis")
print()

# ========== 2. GeoJSON ==========
print("2. GeoJSON (Geographic JSON)")
print("   Exporting Tangsel... (this may take a moment)")
tangsel_gdf.to_file(OUTPUT_DIR / 'grid_tangsel_integrated.geojson', driver='GeoJSON')
print(f"   ✓ grid_tangsel_integrated.geojson")

print("   Exporting OKU... (this will take longer, 1.5M features)")
oku_gdf.to_file(OUTPUT_DIR / 'grid_oku_integrated.geojson', driver='GeoJSON')
print(f"   ✓ grid_oku_integrated.geojson")
print(f"   Format: GeoJSON (with grid polygon geometries)")
print(f"   Use: QGIS, web maps, GeoJSON.io")
print()

# ========== 3. GeoParquet ==========
print("3. GeoParquet (Columnar Spatial Format)")
tangsel_gdf.to_parquet(OUTPUT_DIR / 'grid_tangsel_integrated.parquet')
print(f"   ✓ grid_tangsel_integrated.parquet")

oku_gdf.to_parquet(OUTPUT_DIR / 'grid_oku_integrated.parquet')
print(f"   ✓ grid_oku_integrated.parquet")
print(f"   Format: GeoParquet (efficient, with geometry)")
print(f"   Use: GeoPandas, DuckDB, modern GIS tools")
print()

# ========== File Size Comparison ==========
print("=" * 70)
print("FILE SIZE COMPARISON")
print("=" * 70)

def get_file_size_mb(filepath):
    return os.path.getsize(filepath) / (1024 * 1024)

formats = ['csv', 'geojson', 'parquet']
regions = ['tangsel', 'oku']

for region in regions:
    print(f"\n{region.upper()}:")
    for fmt in formats:
        if fmt == 'csv':
            filepath = OUTPUT_DIR / f'grid_{region}_integrated.csv'
        elif fmt == 'geojson':
            filepath = OUTPUT_DIR / f'grid_{region}_integrated.geojson'
        else:
            filepath = OUTPUT_DIR / f'grid_{region}_integrated.parquet'

        if filepath.exists():
            size_mb = get_file_size_mb(filepath)
            print(f"  {fmt.upper():<10} {size_mb:>8.2f} MB")

print()
print("=" * 70)
print("EXPORT COMPLETE")
print("=" * 70)
print()
print(f"Output directory: {OUTPUT_DIR}")
print()
print("Format Recommendations:")
print("  • CSV       → Analysis in Excel, Pandas (no geometry)")
print("  • GeoJSON   → Visualization in QGIS, web maps (human-readable)")
print("  • Parquet   → Fastest loading, smallest size (binary, efficient)")
print()
print("All formats contain the same 24 columns:")
print("  - grid_id, lat, lon")
print("  - Population (3 cols)")
print("  - LULC (2 cols)")
print("  - Night Lights (3 cols)")
print("  - Hazards (7 cols)")
print("  - RTRW (2 cols)")
print("  - OSM (3 cols)")
print("  - geometry (polygon, except CSV)")
print()
print("=" * 70)
