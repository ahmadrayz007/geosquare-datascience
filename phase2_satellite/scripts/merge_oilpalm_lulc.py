"""
Merge Oil Palm layer into LULC OKU
Overlays oil palm plantations onto LULC classification
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np

# LULC Classes (updated with Oil Palm)
LULC_CLASSES = {
    1: 'Water',
    2: 'Trees',
    4: 'Flooded Vegetation',
    5: 'Crops',
    7: 'Built Area',
    8: 'Bare Ground',
    11: 'Rangeland',
    12: 'Oil Palm'  # NEW CLASS
}

# Color palette (hex to RGB)
LULC_COLORS = {
    1: (65, 155, 223),      # Water - #419bdf
    2: (57, 125, 73),       # Trees - #397d49
    4: (122, 135, 198),     # Flooded Vegetation - #7a87c6
    5: (228, 150, 53),      # Crops - #e49635
    7: (196, 40, 27),       # Built Area - #c4281b
    8: (165, 155, 143),     # Bare Ground - #a59b8f
    11: (227, 226, 195),    # Rangeland - #e3e2c3
    12: (139, 69, 19)       # Oil Palm - #8B4513 (brown)
}

def merge_oilpalm_to_lulc():
    """
    Merge oil palm layer into LULC OKU
    - Class 1 or 2 in oil palm raster → becomes class 12 (Oil Palm) in LULC
    - Class 3 in oil palm raster → ignored (keep original LULC)
    """

    lulc_path = 'data/satellite/lulc_oku_2025.tif'
    oilpalm_path = 'data/satellite/oku_oilpalm_biopama.tif'
    output_path = 'data/satellite/lulc_oku_2025.tif'

    print("=" * 60)
    print("MERGING OIL PALM INTO LULC OKU")
    print("=" * 60)

    # Open LULC raster
    with rasterio.open(lulc_path, 'r') as lulc_src:
        lulc_data = lulc_src.read(1)
        lulc_meta = lulc_src.meta.copy()
        lulc_transform = lulc_src.transform
        lulc_crs = lulc_src.crs
        lulc_shape = lulc_data.shape

        print(f"LULC shape: {lulc_shape}")
        print(f"LULC CRS: {lulc_crs}")
        print(f"LULC unique values: {np.unique(lulc_data)}")

        # Open Oil Palm raster
        with rasterio.open(oilpalm_path, 'r') as oilpalm_src:
            print(f"\nOil Palm shape: {oilpalm_src.shape}")
            print(f"Oil Palm CRS: {oilpalm_src.crs}")

            # Reproject oil palm to match LULC
            oilpalm_data = np.zeros(lulc_shape, dtype=np.uint8)

            reproject(
                source=rasterio.band(oilpalm_src, 1),
                destination=oilpalm_data,
                src_transform=oilpalm_src.transform,
                src_crs=oilpalm_src.crs,
                dst_transform=lulc_transform,
                dst_crs=lulc_crs,
                resampling=Resampling.nearest
            )

            print(f"Oil Palm unique values after reproject: {np.unique(oilpalm_data)}")

            # Create mask for oil palm (class 1 or 2)
            oilpalm_mask = (oilpalm_data == 1) | (oilpalm_data == 2)

            # Count pixels that will be replaced
            n_replaced = np.sum(oilpalm_mask)
            print(f"\nPixels to be replaced with Oil Palm: {n_replaced:,}")

            if n_replaced > 0:
                # Show what LULC classes will be replaced
                replaced_classes, replaced_counts = np.unique(lulc_data[oilpalm_mask], return_counts=True)
                print("\nLULC classes being replaced:")
                for cls, cnt in zip(replaced_classes, replaced_counts):
                    cls_name = LULC_CLASSES.get(int(cls), f'Unknown ({cls})')
                    print(f"  Class {cls} ({cls_name}): {cnt:,} pixels")

                # Replace LULC values with Oil Palm (class 12)
                lulc_data[oilpalm_mask] = 12

                print(f"\nFinal LULC unique values: {np.unique(lulc_data)}")
            else:
                print("\nWARNING: No oil palm pixels found to merge!")

        # Update metadata
        lulc_meta.update({
            'dtype': 'uint8',
            'compress': 'lzw',
            'tiled': True,
            'blockxsize': 512,
            'blockysize': 512,
            'nodata': 0
        })

        # Write output
        with rasterio.open(output_path, 'w', **lulc_meta) as dst:
            dst.write(lulc_data, 1)

            # Set band description
            dst.set_band_description(1, 'LULC Classification with Oil Palm')

            # Add color interpretation
            dst.write_colormap(1, LULC_COLORS)

            # Set category names
            dst.update_tags(1, **{
                'class_names': ','.join([f"{k}:{v}" for k, v in LULC_CLASSES.items()]),
                'description': 'Land Use Land Cover Classification 2025 (with Oil Palm overlay)',
                'method': 'Random Forest - Sentinel-2 + Oil Palm overlay from BIOPAMA',
                'bands_used': 'B2,B3,B4,B5,B6,B7,B8,B8A,B11,B12,NDVI,NDWI,NDBI,SAVI,EVI,BSI',
                'date_range': '2025-01-01 to 2025-12-31',
                'source': 'Sentinel-2 SR Harmonized + BIOPAMA Oil Palm',
                'resolution': '10m',
                'oil_palm_source': 'BIOPAMA Closed-canopy Oil Palm (Industrial + Smallholder)'
            })

            dst.update_tags(**{
                'AREA_OR_POINT': 'Area',
                'TIFFTAG_SOFTWARE': 'Google Earth Engine + rasterio'
            })

    print("\n" + "=" * 60)
    print("MERGE COMPLETE")
    print("=" * 60)
    print(f"Output saved to: {output_path}")
    print(f"\nFinal LULC Classes:")
    for class_id, class_name in LULC_CLASSES.items():
        print(f"  {class_id}: {class_name}")

if __name__ == '__main__':
    merge_oilpalm_to_lulc()
