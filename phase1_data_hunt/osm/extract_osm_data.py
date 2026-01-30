"""
Extract OSM Data from PBF - Tangerang Selatan & OKU

Automatically downloads and extracts buildings, roads, and POI from OpenStreetMap
PBF files for both regions. Downloads Indonesia PBF from Geofabrik if not cached,
then uses osmium to create regional PBF extracts, and pyrosm for data extraction.

Input:
- Downloads from: https://download.geofabrik.de/asia/indonesia-latest.osm.pbf
- phase1_data_hunt/boundaries/*.geojson (region boundaries)

Output:
- osm_business_tangsel.geojson/csv (POI with names)
- osm_business_oku.geojson/csv
- osm_buildings_tangsel.geojson (building footprints)
- osm_buildings_oku.geojson
- osm_roads_tangsel.geojson (road network)
- osm_roads_oku.geojson
- tangsel.osm.pbf (regional extract)
- oku.osm.pbf (regional extract)
- osm_business_comparison.png (visualization)

Dependencies:
- pyrosm (OSM PBF reader)
- osmium-tool (PBF extraction)
- geopandas, pandas, matplotlib
- requests (HTTP downloads)
- tqdm (progress bars, optional)
"""

import os
import subprocess
from pathlib import Path
import geopandas as gpd
import pandas as pd
from pyrosm import OSM
import matplotlib.pyplot as plt
import requests
from tqdm import tqdm

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
BOUNDARIES_DIR = SCRIPT_DIR.parent / "boundaries"
INDONESIA_PBF_URL = "https://download.geofabrik.de/asia/indonesia-latest.osm.pbf"
OUTPUT_DIR = SCRIPT_DIR

# Global variable to store the Indonesia PBF path (determined at runtime)
INDONESIA_PBF = None

print("="*70)
print("OSM Data Extraction - Tangerang Selatan & OKU")
print("Using regional PBF extraction for fast processing")
print("="*70)
print()


# ============================================================================
# STEP 1: DOWNLOAD & SETUP
# ============================================================================

def download_indonesia_pbf():
    """Find existing Indonesia PBF or download from Geofabrik if not found"""
    global INDONESIA_PBF

    # Look for any existing indonesia-*.osm.pbf file
    existing_pbfs = list(SCRIPT_DIR.glob("indonesia-*.osm.pbf"))

    if existing_pbfs:
        # Use the most recent one (by modification time)
        INDONESIA_PBF = max(existing_pbfs, key=lambda p: p.stat().st_mtime)
        size_mb = INDONESIA_PBF.stat().st_size / (1024*1024)
        print(f"✓ Found existing Indonesia PBF: {INDONESIA_PBF.name} ({size_mb:.1f} MB)")
        return True

    # No existing file found - download it
    INDONESIA_PBF = SCRIPT_DIR / "indonesia-latest.osm.pbf"

    print(f"\n{'='*70}")
    print("DOWNLOADING INDONESIA OSM DATA")
    print(f"{'='*70}")
    print(f"Source: {INDONESIA_PBF_URL}")
    print(f"Target: {INDONESIA_PBF}")
    print("This is a large file (~1.6 GB) and may take several minutes...")
    print()

    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(INDONESIA_PBF_URL, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        # Use tqdm if available, otherwise simple progress
        try:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                with open(INDONESIA_PBF, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        except NameError:
            # tqdm not available, use simple progress
            downloaded = 0
            with open(INDONESIA_PBF, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (10 * 1024 * 1024) == 0:  # Every 10 MB
                            print(f"  Downloaded: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB")

        size_mb = INDONESIA_PBF.stat().st_size / (1024*1024)
        print(f"\n✓ Download complete: {INDONESIA_PBF.name} ({size_mb:.1f} MB)")
        return True

    except Exception as e:
        print(f"✗ Error downloading Indonesia PBF: {e}")
        if INDONESIA_PBF.exists():
            INDONESIA_PBF.unlink()  # Remove partial download
        return False


def load_boundaries():
    """Load region boundaries from GeoJSON"""
    print("Loading region boundaries...")

    tangsel_path = BOUNDARIES_DIR / "tangerang_selatan_kelurahan_RBI.geojson"
    oku_path = BOUNDARIES_DIR / "oku_kecamatan_RBI.geojson"

    if not tangsel_path.exists():
        raise FileNotFoundError(f"Tangsel boundary not found: {tangsel_path}")
    if not oku_path.exists():
        raise FileNotFoundError(f"OKU boundary not found: {oku_path}")

    tangsel_boundary = gpd.read_file(tangsel_path)
    oku_boundary = gpd.read_file(oku_path)

    # Dissolve to single polygon
    tangsel_dissolved = tangsel_boundary.dissolve()
    oku_dissolved = oku_boundary.dissolve()

    print(f"✓ Tangsel: {len(tangsel_boundary)} kelurahan")
    print(f"✓ OKU: {len(oku_boundary)} kecamatan")

    return tangsel_dissolved, oku_dissolved


def get_bbox_string(gdf, buffer=0.01):
    """Get bbox string for osmium with buffer"""
    bbox = gdf.total_bounds  # [minx, miny, maxx, maxy]
    return f"{bbox[0]-buffer},{bbox[1]-buffer},{bbox[2]+buffer},{bbox[3]+buffer}"


# ============================================================================
# STEP 2: REGIONAL PBF EXTRACTION
# ============================================================================

def extract_regional_pbf(region_name, bbox_string, output_pbf):
    """Extract regional PBF from Indonesia PBF using osmium"""
    if output_pbf.exists():
        print(f"✓ {output_pbf.name} already exists")
        return True

    if not INDONESIA_PBF.exists():
        print(f"Error: Indonesia PBF not found: {INDONESIA_PBF}")
        return False

    print(f"Extracting {region_name} region from Indonesia PBF...")
    cmd = f'osmium extract -b {bbox_string} "{INDONESIA_PBF}" -o "{output_pbf}" --overwrite'

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        size_mb = output_pbf.stat().st_size / (1024*1024)
        print(f"✓ {output_pbf.name} created ({size_mb:.1f} MB)")
        return True
    else:
        print(f"Error extracting {region_name}: {result.stderr}")
        return False


# ============================================================================
# STEP 3: DATA EXTRACTION
# ============================================================================

def extract_pois(osm_obj, region_gdf, region_name):
    """Extract POIs from regional PBF and clip to boundaries"""
    print(f"\n--- Extracting {region_name} POIs ---")

    pois_raw = osm_obj.get_pois()
    print(f"POIs in bbox: {len(pois_raw):,}")

    # Ensure same CRS
    if pois_raw.crs != region_gdf.crs:
        pois_raw = pois_raw.to_crs(region_gdf.crs)

    # Clip to precise boundary
    pois = gpd.sjoin(pois_raw, region_gdf[['geometry']], how='inner', predicate='within')
    pois = pois.drop(columns=['index_right'], errors='ignore')

    print(f"✓ POIs within boundary: {len(pois):,}")
    return pois


def extract_business_data(gdf, region_name):
    """Extract business POIs with names and categorize"""
    print(f"\n--- Extracting business data for {region_name} ---")

    # Filter POIs with names
    biz = gdf[gdf['name'].notna()].copy()
    print(f"POIs with name: {len(biz):,}")

    # Select relevant columns
    cols_to_keep = ['name', 'amenity', 'shop', 'office', 'brand', 'operator',
                    'addr:street', 'addr:city', 'addr:postcode', 'phone',
                    'website', 'opening_hours', 'geometry']
    cols_exist = [c for c in cols_to_keep if c in biz.columns]
    biz = biz[cols_exist]

    # Add category
    def get_category(row):
        if pd.notna(row.get('shop')):
            return f"shop:{row['shop']}"
        elif pd.notna(row.get('amenity')):
            return f"amenity:{row['amenity']}"
        elif pd.notna(row.get('office')):
            return f"office:{row['office']}"
        return 'other'

    biz['category'] = biz.apply(get_category, axis=1)

    # Add lat/lon (convert to projected CRS first to avoid warning)
    biz_proj = biz.to_crs('EPSG:32748')  # UTM Zone 48S
    biz['lon'] = biz_proj.geometry.centroid.to_crs(biz.crs).x
    biz['lat'] = biz_proj.geometry.centroid.to_crs(biz.crs).y

    print(f"✓ Business POIs: {len(biz):,}")
    print(f"\nTop categories:")
    print(biz['category'].value_counts().head(10))

    return biz


def extract_buildings(osm_obj, region_gdf, region_name):
    """Extract building footprints"""
    print(f"\n--- Extracting {region_name} Buildings ---")

    buildings_raw = osm_obj.get_buildings()
    print(f"Buildings in bbox: {len(buildings_raw):,}")

    # Ensure same CRS
    if buildings_raw.crs != region_gdf.crs:
        buildings_raw = buildings_raw.to_crs(region_gdf.crs)

    # Clip to precise boundary
    buildings = gpd.sjoin(buildings_raw, region_gdf[['geometry']], how='inner', predicate='within')
    buildings = buildings.drop(columns=['index_right'], errors='ignore')

    # Calculate area
    buildings['area_m2'] = buildings.to_crs('EPSG:32748').geometry.area

    print(f"✓ Buildings: {len(buildings):,}")
    print(f"  Total area: {buildings['area_m2'].sum()/1e6:.2f} km²")
    print(f"  Mean size: {buildings['area_m2'].mean():.1f} m²")

    return buildings


def extract_roads(osm_obj, region_gdf, region_name):
    """Extract road network"""
    print(f"\n--- Extracting {region_name} Roads ---")

    roads_raw = osm_obj.get_network(network_type="driving")

    if roads_raw is None or len(roads_raw) == 0:
        print("⚠ No roads found")
        return gpd.GeoDataFrame()

    print(f"Roads in bbox: {len(roads_raw):,}")

    # Ensure same CRS and clip
    if roads_raw.crs != region_gdf.crs:
        roads_raw = roads_raw.to_crs(region_gdf.crs)

    roads = gpd.clip(roads_raw, region_gdf)

    # Calculate length
    roads['length_m'] = roads.to_crs('EPSG:32748').geometry.length

    print(f"✓ Roads: {len(roads):,}")
    print(f"  Total length: {roads['length_m'].sum()/1000:.1f} km")

    if 'highway' in roads.columns:
        print(f"\nTop road types:")
        print(roads['highway'].value_counts().head(5))

    return roads


# ============================================================================
# STEP 4: OUTPUT & VISUALIZATION
# ============================================================================

def save_data(biz_tangsel, biz_oku, buildings_tangsel, buildings_oku, roads_tangsel, roads_oku):
    """Save all extracted data"""
    print("\n" + "="*70)
    print("SAVING DATA")
    print("="*70)

    # Business POIs
    biz_tangsel.to_file(OUTPUT_DIR / 'osm_business_tangsel.geojson', driver='GeoJSON')
    csv_cols = [c for c in biz_tangsel.columns if c != 'geometry']
    biz_tangsel[csv_cols].to_csv(OUTPUT_DIR / 'osm_business_tangsel.csv', index=False)
    print(f"✓ osm_business_tangsel.geojson/csv ({len(biz_tangsel):,} records)")

    biz_oku.to_file(OUTPUT_DIR / 'osm_business_oku.geojson', driver='GeoJSON')
    csv_cols = [c for c in biz_oku.columns if c != 'geometry']
    biz_oku[csv_cols].to_csv(OUTPUT_DIR / 'osm_business_oku.csv', index=False)
    print(f"✓ osm_business_oku.geojson/csv ({len(biz_oku):,} records)")

    # Buildings
    building_cols = ['name', 'building', 'amenity', 'area_m2', 'geometry']
    cols_tangsel = [c for c in building_cols if c in buildings_tangsel.columns]
    cols_oku = [c for c in building_cols if c in buildings_oku.columns]

    buildings_tangsel[cols_tangsel].to_file(OUTPUT_DIR / 'osm_buildings_tangsel.geojson', driver='GeoJSON')
    print(f"✓ osm_buildings_tangsel.geojson ({len(buildings_tangsel):,} buildings)")

    buildings_oku[cols_oku].to_file(OUTPUT_DIR / 'osm_buildings_oku.geojson', driver='GeoJSON')
    print(f"✓ osm_buildings_oku.geojson ({len(buildings_oku):,} buildings)")

    # Roads
    if len(roads_tangsel) > 0:
        road_cols = ['name', 'highway', 'length_m', 'geometry']
        cols_exist = [c for c in road_cols if c in roads_tangsel.columns]
        roads_tangsel[cols_exist].to_file(OUTPUT_DIR / 'osm_roads_tangsel.geojson', driver='GeoJSON')
        print(f"✓ osm_roads_tangsel.geojson ({len(roads_tangsel):,} roads)")

    if len(roads_oku) > 0:
        cols_exist = [c for c in road_cols if c in roads_oku.columns]
        roads_oku[cols_exist].to_file(OUTPUT_DIR / 'osm_roads_oku.geojson', driver='GeoJSON')
        print(f"✓ osm_roads_oku.geojson ({len(roads_oku):,} roads)")


def create_visualization(biz_tangsel, biz_oku, tangsel_dissolved, oku_dissolved):
    """Create comparison visualization"""
    print("\nCreating visualization...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Tangsel - Categories
    ax1 = axes[0, 0]
    top_cats = biz_tangsel['category'].value_counts().head(12)
    ax1.barh(range(len(top_cats)), top_cats.values, color='#3498db')
    ax1.set_yticks(range(len(top_cats)))
    ax1.set_yticklabels(top_cats.index)
    ax1.invert_yaxis()
    ax1.set_xlabel('Count')
    ax1.set_title(f'Top Business Categories - Tangerang Selatan\n({len(biz_tangsel):,} total)')

    # Tangsel - Map
    ax2 = axes[0, 1]
    tangsel_dissolved.boundary.plot(ax=ax2, color='blue', linewidth=1.5)
    biz_tangsel.plot(ax=ax2, markersize=2, alpha=0.5, color='#e74c3c')
    ax2.set_title('Business Locations - Tangerang Selatan')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')

    # OKU - Categories
    ax3 = axes[1, 0]
    top_cats = biz_oku['category'].value_counts().head(12)
    ax3.barh(range(len(top_cats)), top_cats.values, color='#27ae60')
    ax3.set_yticks(range(len(top_cats)))
    ax3.set_yticklabels(top_cats.index)
    ax3.invert_yaxis()
    ax3.set_xlabel('Count')
    ax3.set_title(f'Top Business Categories - Ogan Komering Ulu\n({len(biz_oku):,} total)')

    # OKU - Map
    ax4 = axes[1, 1]
    oku_dissolved.boundary.plot(ax=ax4, color='orange', linewidth=1.5)
    biz_oku.plot(ax=ax4, markersize=2, alpha=0.5, color='#9b59b6')
    ax4.set_title('Business Locations - Ogan Komering Ulu')
    ax4.set_xlabel('Longitude')
    ax4.set_ylabel('Latitude')

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'osm_business_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✓ osm_business_comparison.png")


def print_summary(pois_tangsel, pois_oku, biz_tangsel, biz_oku,
                  buildings_tangsel, buildings_oku, roads_tangsel, roads_oku):
    """Print final summary"""
    print("\n" + "="*70)
    print("OSM DATA EXTRACTION - FINAL SUMMARY")
    print("="*70)

    print(f"\n{'Category':<25} {'Tangsel':>15} {'OKU':>15} {'Ratio':>10}")
    print("-"*70)

    # POIs
    print(f"{'Total POIs':<25} {len(pois_tangsel):>15,} {len(pois_oku):>15,} {len(pois_tangsel)/max(len(pois_oku),1):>10.1f}x")
    print(f"{'Business POIs':<25} {len(biz_tangsel):>15,} {len(biz_oku):>15,} {len(biz_tangsel)/max(len(biz_oku),1):>10.1f}x")

    # Buildings
    print(f"{'Buildings':<25} {len(buildings_tangsel):>15,} {len(buildings_oku):>15,} {len(buildings_tangsel)/max(len(buildings_oku),1):>10.1f}x")
    tangsel_area = buildings_tangsel['area_m2'].sum()/1e6
    oku_area = buildings_oku['area_m2'].sum()/1e6
    print(f"{'Building Area (km²)':<25} {tangsel_area:>15.2f} {oku_area:>15.2f} {tangsel_area/max(oku_area,0.01):>10.1f}x")

    # Roads
    if len(roads_tangsel) > 0 and len(roads_oku) > 0:
        print(f"{'Road Segments':<25} {len(roads_tangsel):>15,} {len(roads_oku):>15,} {len(roads_tangsel)/max(len(roads_oku),1):>10.1f}x")
        tangsel_road_km = roads_tangsel['length_m'].sum()/1000
        oku_road_km = roads_oku['length_m'].sum()/1000
        print(f"{'Road Length (km)':<25} {tangsel_road_km:>15.1f} {oku_road_km:>15.1f} {tangsel_road_km/max(oku_road_km,0.1):>10.1f}x")

    print("-"*70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("="*70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution pipeline"""

    # Step 1: Download Indonesia PBF
    if not download_indonesia_pbf():
        print("Failed to obtain Indonesia PBF file. Exiting.")
        return

    # Step 2: Load boundaries and get bounding boxes
    tangsel_dissolved, oku_dissolved = load_boundaries()
    tangsel_bbox_str = get_bbox_string(tangsel_dissolved)
    oku_bbox_str = get_bbox_string(oku_dissolved)

    print(f"\nTangsel bbox: {tangsel_bbox_str}")
    print(f"OKU bbox: {oku_bbox_str}")
    print()

    # Step 3: Extract regional PBFs
    tangsel_pbf = OUTPUT_DIR / 'tangsel.osm.pbf'
    oku_pbf = OUTPUT_DIR / 'oku.osm.pbf'

    if not extract_regional_pbf("Tangsel", tangsel_bbox_str, tangsel_pbf):
        return
    if not extract_regional_pbf("OKU", oku_bbox_str, oku_pbf):
        return

    print()

    # Step 4: Load regional PBFs
    print("Loading regional PBF files...")
    osm_tangsel = OSM(str(tangsel_pbf))
    osm_oku = OSM(str(oku_pbf))
    print("✓ Regional PBF files loaded")

    # Step 5: Extract all data layers
    pois_tangsel = extract_pois(osm_tangsel, tangsel_dissolved, "Tangsel")
    pois_oku = extract_pois(osm_oku, oku_dissolved, "OKU")

    biz_tangsel = extract_business_data(pois_tangsel, "Tangerang Selatan")
    biz_oku = extract_business_data(pois_oku, "Ogan Komering Ulu")

    buildings_tangsel = extract_buildings(osm_tangsel, tangsel_dissolved, "Tangsel")
    buildings_oku = extract_buildings(osm_oku, oku_dissolved, "OKU")

    roads_tangsel = extract_roads(osm_tangsel, tangsel_dissolved, "Tangsel")
    roads_oku = extract_roads(osm_oku, oku_dissolved, "OKU")

    # Step 6: Save, visualize, and summarize
    save_data(biz_tangsel, biz_oku, buildings_tangsel, buildings_oku, roads_tangsel, roads_oku)
    create_visualization(biz_tangsel, biz_oku, tangsel_dissolved, oku_dissolved)
    print_summary(pois_tangsel, pois_oku, biz_tangsel, biz_oku,
                  buildings_tangsel, buildings_oku, roads_tangsel, roads_oku)


if __name__ == "__main__":
    main()
