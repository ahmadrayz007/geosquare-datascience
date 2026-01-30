"""
LULC Raster Metadata Assignment
Assigns proper metadata to LULC GeoTIFF files from GEE export
"""

import rasterio
from rasterio.enums import Resampling
import numpy as np

# LULC Class Mapping
LULC_CLASSES = {
    1: 'Water',
    2: 'Trees',
    4: 'Flooded Vegetation',
    5: 'Crops',
    7: 'Built Area',
    8: 'Bare Ground',
    11: 'Rangeland'
}

# Color palette (hex to RGB)
LULC_COLORS = {
    1: (65, 155, 223),      # Water - #419bdf
    2: (57, 125, 73),       # Trees - #397d49
    4: (122, 135, 198),     # Flooded Vegetation - #7a87c6
    5: (228, 150, 53),      # Crops - #e49635
    7: (196, 40, 27),       # Built Area - #c4281b
    8: (165, 155, 143),     # Bare Ground - #a59b8f
    11: (227, 226, 195)     # Rangeland - #e3e2c3
}

def assign_lulc_metadata(input_tif, output_tif=None):
    """
    Assign metadata to LULC raster

    Parameters:
    - input_tif: Path to input LULC GeoTIFF
    - output_tif: Path to output GeoTIFF (if None, overwrites input)
    """
    if output_tif is None:
        output_tif = input_tif

    with rasterio.open(input_tif, 'r') as src:
        # Read data
        data = src.read(1)

        # Get metadata
        meta = src.meta.copy()

        # Update metadata
        meta.update({
            'dtype': 'uint8',
            'compress': 'lzw',
            'tiled': True,
            'blockxsize': 512,
            'blockysize': 512,
            'nodata': 0
        })

        # Convert data to uint8 if needed
        data = data.astype('uint8')

        # Write output with metadata
        with rasterio.open(output_tif, 'w', **meta) as dst:
            dst.write(data, 1)

            # Set band description
            dst.set_band_description(1, 'LULC Classification')

            # Add color interpretation
            dst.write_colormap(1, LULC_COLORS)

            # Set category names
            category_names = [''] * 256
            for class_id, class_name in LULC_CLASSES.items():
                if class_id < 256:
                    category_names[class_id] = class_name

            dst.update_tags(1, **{
                'class_names': ','.join([f"{k}:{v}" for k, v in LULC_CLASSES.items()]),
                'description': 'Land Use Land Cover Classification 2025',
                'method': 'Random Forest - Sentinel-2',
                'bands_used': 'B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12,NDVI,NDWI,NDBI,SAVI,EVI,BSI',
                'date_range': '2025-01-01 to 2025-12-31',
                'source': 'Sentinel-2 SR Harmonized',
                'resolution': '10m'
            })

            # Set CRS metadata
            dst.update_tags(**{
                'AREA_OR_POINT': 'Area',
                'TIFFTAG_SOFTWARE': 'Google Earth Engine + rasterio'
            })

    print(f"Metadata assigned to: {output_tif}")
    print(f"\nLULC Classes:")
    for class_id, class_name in LULC_CLASSES.items():
        print(f"  {class_id}: {class_name}")

    # Print basic stats
    with rasterio.open(output_tif, 'r') as src:
        data = src.read(1)
        unique_values = np.unique(data[data > 0])
        print(f"\nUnique values in raster: {unique_values}")
        print(f"Raster shape: {data.shape}")
        print(f"CRS: {src.crs}")
        print(f"Bounds: {src.bounds}")

if __name__ == '__main__':
    import sys

    # Process Tangsel
    print("=" * 60)
    print("Processing LULC Tangsel 2025")
    print("=" * 60)
    assign_lulc_metadata('data/satellite/lulc_tangsel_2025.tif')

    print("\n")

    # Process OKU
    print("=" * 60)
    print("Processing LULC OKU 2025")
    print("=" * 60)
    assign_lulc_metadata('data/satellite/lulc_oku_2025.tif')

    print("\n" + "=" * 60)
    print("METADATA ASSIGNMENT COMPLETE")
    print("=" * 60)
