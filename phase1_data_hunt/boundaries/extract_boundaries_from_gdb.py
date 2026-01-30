"""
Extract Administrative Boundaries from RBI GDB

Extracts kelurahan/desa boundaries for Tangerang Selatan and Ogan Komering Ulu
from BIG's RBI10K Geodatabase and exports to GeoJSON format.

Source GDB: cache/RBI10K_ADMINISTRASI_DESA_20230928.gdb
Source: Badan Informasi Geospasial (BIG)
Date: September 2023

Processing:
- Tangerang Selatan: Keeps kelurahan/desa level (as-is)
- Ogan Komering Ulu: Dissolves desa → kecamatan level (aggregated)

Output:
- tangerang_selatan_kelurahan_RBI.geojson (54 kelurahan)
- oku_kecamatan_RBI.geojson (15 kecamatan, dissolved from desa)
"""

import geopandas as gpd
import os
from pathlib import Path

# Paths (relative to script location)
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
GDB_PATH = PROJECT_ROOT / "cache" / "RBI10K_ADMINISTRASI_DESA_20230928.gdb" / "RBI10K_ADMINISTRASI_DESA_20230928.gdb"
OUTPUT_DIR = SCRIPT_DIR  # Output to boundaries/ folder

# Target regions (exact match to avoid catching OKU Timur/Selatan)
TANGSEL_KEYWORDS = ["KOTA TANGERANG SELATAN"]
OKU_KEYWORDS = ["OGAN KOMERING ULU$"]  # $ for end-of-string regex


def list_layers_in_gdb(gdb_path):
    """
    List all layers in the Geodatabase
    """
    import fiona

    print(f"Reading GDB: {gdb_path}")
    layers = fiona.listlayers(str(gdb_path))

    print(f"\nFound {len(layers)} layers:")
    for i, layer in enumerate(layers, 1):
        print(f"  {i}. {layer}")

    return layers


def extract_boundaries(gdb_path, layer_name, region_keywords, output_filename, dissolve_by=None):
    """
    Extract boundaries for specific region from GDB layer

    Parameters:
    - gdb_path: Path to GDB file
    - layer_name: Layer name in GDB
    - region_keywords: List of keywords to match region names
    - output_filename: Output GeoJSON filename
    - dissolve_by: Optional column name to dissolve by (e.g., 'WADMKC' for kecamatan)

    Returns:
    - GeoDataFrame of extracted boundaries
    """
    print(f"\n{'='*70}")
    print(f"Extracting: {output_filename}")
    print(f"{'='*70}")

    # Read layer from GDB
    print(f"Reading layer: {layer_name}")
    gdf = gpd.read_file(gdb_path, layer=layer_name)

    print(f"Total features in layer: {len(gdf):,}")
    print(f"Columns: {list(gdf.columns)}")

    # Find column that contains region names (prioritize WADMKK for kabupaten/kota names)
    if 'WADMKK' in gdf.columns:
        name_col = 'WADMKK'
    else:
        name_cols = [col for col in gdf.columns if any(
            keyword in col.upper() for keyword in ['WADM', 'NAMA', 'KAB', 'KOT']
        ) and 'KD' not in col.upper()]  # Exclude code columns (KDPKAB, KDCBPS, etc.)

        if not name_cols:
            print("Warning: Could not find name column, using first text column")
            name_cols = [gdf.select_dtypes(include=['object']).columns[0]]

        name_col = name_cols[0]

    print(f"Using column for filtering: {name_col}")

    # Filter for target region (using regex for exact matching)
    mask = gdf[name_col].str.upper().str.contains('|'.join(region_keywords), na=False, regex=True)
    filtered = gdf[mask].copy()

    print(f"Filtered features (desa level): {len(filtered):,}")

    if len(filtered) == 0:
        print(f"Warning: No features found for keywords: {region_keywords}")
        print(f"Sample values in {name_col}:")
        print(gdf[name_col].unique()[:10])
        return None

    # Dissolve by kecamatan if requested
    if dissolve_by:
        print(f"\nDissolving by: {dissolve_by}")

        # Find kecamatan column
        kec_cols = [col for col in filtered.columns if dissolve_by.upper() in col.upper()]

        if not kec_cols:
            print(f"Warning: Could not find column matching '{dissolve_by}'")
            print(f"Available columns: {list(filtered.columns)}")
        else:
            kec_col = kec_cols[0]
            print(f"Using column: {kec_col}")

            # Keep important columns before dissolve
            cols_to_keep = [kec_col, 'geometry']

            # Add kabupaten column if exists
            kab_cols = [col for col in filtered.columns if 'WADMKK' in col.upper() or 'KAB' in col.upper()]
            if kab_cols:
                cols_to_keep.insert(0, kab_cols[0])

            # Dissolve
            dissolved = filtered[cols_to_keep].dissolve(by=kec_col, as_index=False)
            filtered = dissolved

            print(f"Dissolved features (kecamatan level): {len(filtered):,}")

    # Ensure CRS is WGS84
    if filtered.crs != 'EPSG:4326':
        print(f"Converting CRS from {filtered.crs} to EPSG:4326")
        filtered = filtered.to_crs('EPSG:4326')

    # Export to GeoJSON
    output_path = OUTPUT_DIR / output_filename
    filtered.to_file(output_path, driver='GeoJSON')

    file_size = output_path.stat().st_size / 1024  # KB
    print(f"✓ Exported: {output_filename} ({file_size:.1f} KB)")
    print(f"  Features: {len(filtered):,}")
    print(f"  Bounds: {filtered.total_bounds}")

    return filtered


def main():
    print("="*70)
    print("RBI10K Administrative Boundaries Extraction")
    print("Source: BIG (Badan Informasi Geospasial)")
    print("="*70)
    print()

    # Check if GDB exists
    if not GDB_PATH.exists():
        print(f"Error: GDB file not found at {GDB_PATH}")
        print(f"Expected location: {GDB_PATH}")
        print("\nPlease ensure RBI10K GDB is downloaded to cache/ folder")
        return

    print(f"GDB Path: {GDB_PATH}")
    print(f"Output Dir: {OUTPUT_DIR}")
    print()

    # List available layers
    layers = list_layers_in_gdb(GDB_PATH)

    # Find the desa/kelurahan layer (usually contains 'DESA' or 'ADM' in name)
    desa_layer = None
    for layer in layers:
        if any(keyword in layer.upper() for keyword in ['DESA', 'KELURAHAN', 'ADM']):
            desa_layer = layer
            break

    if not desa_layer:
        print("\nCould not auto-detect desa/kelurahan layer.")
        print("Please specify the layer name manually.")
        return

    print(f"\nUsing layer: {desa_layer}")
    print()

    # Extract Tangerang Selatan kelurahan (keep desa/kelurahan level)
    tangsel_gdf = extract_boundaries(
        GDB_PATH,
        desa_layer,
        TANGSEL_KEYWORDS,
        "tangerang_selatan_kelurahan_RBI.geojson",
        dissolve_by=None  # Keep original desa/kelurahan level
    )

    # Extract OKU and dissolve to kecamatan level
    oku_gdf = extract_boundaries(
        GDB_PATH,
        desa_layer,
        OKU_KEYWORDS,
        "oku_kecamatan_RBI.geojson",
        dissolve_by="WADMKC"  # Dissolve desa → kecamatan
    )

    # Summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)

    if tangsel_gdf is not None:
        print(f"✓ Tangerang Selatan: {len(tangsel_gdf):,} kelurahan (desa level)")
    else:
        print("✗ Tangerang Selatan: Failed")

    if oku_gdf is not None:
        print(f"✓ Ogan Komering Ulu: {len(oku_gdf):,} kecamatan (dissolved from desa)")
    else:
        print("✗ Ogan Komering Ulu: Failed")

    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("="*70)


if __name__ == "__main__":
    main()
