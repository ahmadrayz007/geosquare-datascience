"""
Assign Metadata to All Rasters
- Night Lights (VIIRS)
- BNPB Hazards (InaRISK)
"""

import rasterio
import numpy as np
import os

# ============================================================
# NIGHT LIGHTS METADATA
# ============================================================

NIGHTLIGHTS_METADATA = {
    'description': 'VIIRS Day/Night Band - Nighttime Radiance',
    'source': 'NASA VIIRS DNB',
    'resolution': '500m (resampled to 10m)',
    'unit': 'nanoWatts/cm²/sr',
    'date_range_2020': '2020-01-01 to 2020-12-31',
    'date_range_2025': '2025-01-01 to 2025-12-31',
    'processing': 'Cloud-free median composite',
    'interpretation': '0=rural/dark, 10=residential, 30=urban, 60+=dense urban/industrial'
}

def assign_nightlights_metadata(input_tif, year, region):
    """
    Assign metadata to night lights raster
    """
    print(f"Processing: {os.path.basename(input_tif)}")

    with rasterio.open(input_tif, 'r+') as src:
        # Update tags
        src.update_tags(
            description=f'{NIGHTLIGHTS_METADATA["description"]} - {year}',
            source=NIGHTLIGHTS_METADATA['source'],
            year=str(year),
            region=region,
            resolution=NIGHTLIGHTS_METADATA['resolution'],
            unit=NIGHTLIGHTS_METADATA['unit'],
            date_range=NIGHTLIGHTS_METADATA[f'date_range_{year}'],
            processing=NIGHTLIGHTS_METADATA['processing'],
            interpretation=NIGHTLIGHTS_METADATA['interpretation']
        )

        # Set band description
        src.set_band_description(1, f'Night Lights {year}')

        # Get stats
        data = src.read(1)
        valid_data = data[data > 0]

        if len(valid_data) > 0:
            print(f"  ✓ Stats: min={valid_data.min():.2f}, max={valid_data.max():.2f}, mean={valid_data.mean():.2f}")
        else:
            print(f"  ⚠ No valid data found")

    print(f"  ✓ Metadata assigned\n")


# ============================================================
# BNPB HAZARDS METADATA
# ============================================================

HAZARD_METADATA = {
    'inarisk_hazard_floods': {
        'name': 'Flood Risk',
        'name_id': 'Risiko Banjir',
        'description': 'Multi-hazard flood risk index combining historical flood events, topography, and precipitation'
    },
    'inarisk_hazard_drought': {
        'name': 'Drought Risk',
        'name_id': 'Risiko Kekeringan',
        'description': 'Drought risk index based on precipitation patterns, water availability, and historical drought events'
    },
    'inarisk_hazard_landslide': {
        'name': 'Landslide Risk',
        'name_id': 'Risiko Tanah Longsor',
        'description': 'Landslide susceptibility based on slope, soil type, precipitation, and historical landslide events'
    },
    'inarisk_hazard_earthquake': {
        'name': 'Earthquake Risk',
        'name_id': 'Risiko Gempa Bumi',
        'description': 'Earthquake hazard index based on seismic activity, fault lines, and soil amplification'
    },
    'inarisk_hazard_extreme_weather': {
        'name': 'Extreme Weather Risk',
        'name_id': 'Risiko Cuaca Ekstrem',
        'description': 'Extreme weather risk including storms, high winds, and extreme precipitation events'
    },
    'inarisk_hazard_land_forest_fire': {
        'name': 'Forest Fire Risk',
        'name_id': 'Risiko Kebakaran Hutan/Lahan',
        'description': 'Fire risk index based on vegetation type, climate, and historical fire events'
    }
}

# Risk classification
RISK_CLASSIFICATION = {
    'low': '0.0 - 0.3 (Low/Rendah)',
    'moderate': '0.3 - 0.6 (Moderate/Sedang)',
    'high': '0.6 - 1.0 (High/Tinggi)'
}

def assign_hazard_metadata(input_tif):
    """
    Assign metadata to BNPB hazard raster
    """
    filename = os.path.basename(input_tif)
    layer_name = filename.replace('.tif', '')

    if layer_name not in HAZARD_METADATA:
        print(f"  ⚠ Unknown layer: {layer_name}")
        return

    metadata = HAZARD_METADATA[layer_name]
    print(f"Processing: {filename}")

    with rasterio.open(input_tif, 'r+') as src:
        # Update tags
        src.update_tags(
            name=metadata['name'],
            name_id=metadata['name_id'],
            description=metadata['description'],
            source='BNPB InaRISK Portal',
            year='2023',
            scale='0-1 normalized (0=low risk, 1=high risk)',
            classification_low=RISK_CLASSIFICATION['low'],
            classification_moderate=RISK_CLASSIFICATION['moderate'],
            classification_high=RISK_CLASSIFICATION['high'],
            interpretation='Higher value = higher risk. Use for investment risk assessment.'
        )

        # Set band description
        src.set_band_description(1, metadata['name'])

        # Get stats
        data = src.read(1)
        valid_data = data[data > 0]

        if len(valid_data) > 0:
            # Classify risk
            low = np.sum((valid_data >= 0) & (valid_data < 0.3))
            moderate = np.sum((valid_data >= 0.3) & (valid_data < 0.6))
            high = np.sum((valid_data >= 0.6) & (valid_data <= 1.0))
            total = len(valid_data)

            print(f"  ✓ Stats: min={valid_data.min():.3f}, max={valid_data.max():.3f}, mean={valid_data.mean():.3f}")
            print(f"  ✓ Risk distribution:")
            print(f"     Low:      {low:,} ({low/total*100:.1f}%)")
            print(f"     Moderate: {moderate:,} ({moderate/total*100:.1f}%)")
            print(f"     High:     {high:,} ({high/total*100:.1f}%)")
        else:
            print(f"  ⚠ No valid data found")

    print(f"  ✓ Metadata assigned\n")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ASSIGN METADATA TO RASTERS")
    print("=" * 70)
    print()

    # ========== NIGHT LIGHTS ==========
    print("=" * 70)
    print("NIGHT LIGHTS (VIIRS)")
    print("=" * 70)
    print()

    nightlights_dir = 'data/nightlights'
    nightlights_files = [
        ('tangsel_nightlights_2020.tif', 2020, 'Tangerang Selatan'),
        ('tangsel_nightlights_2025.tif', 2025, 'Tangerang Selatan'),
        ('oku_nightlights_2020.tif', 2020, 'Ogan Komering Ulu'),
        ('oku_nightlights_2025.tif', 2025, 'Ogan Komering Ulu'),
    ]

    for filename, year, region in nightlights_files:
        filepath = os.path.join(nightlights_dir, filename)
        if os.path.exists(filepath):
            assign_nightlights_metadata(filepath, year, region)
        else:
            print(f"⚠ File not found: {filepath}\n")

    # ========== BNPB HAZARDS ==========
    print("=" * 70)
    print("BNPB HAZARDS (InaRISK)")
    print("=" * 70)
    print()

    hazards_dir = 'bnpb_risiko_indonesia/inarisk'
    hazard_files = [
        'inarisk_hazard_floods.tif',
        'inarisk_hazard_drought.tif',
        'inarisk_hazard_landslide.tif',
        'inarisk_hazard_earthquake.tif',
        'inarisk_hazard_extreme_weather.tif',
        'inarisk_hazard_land_forest_fire.tif',
    ]

    for filename in hazard_files:
        filepath = os.path.join(hazards_dir, filename)
        if os.path.exists(filepath):
            assign_hazard_metadata(filepath)
        else:
            print(f"⚠ File not found: {filepath}\n")

    # ========== SUMMARY ==========
    print("=" * 70)
    print("METADATA ASSIGNMENT COMPLETE")
    print("=" * 70)
    print()
    print("Night Lights: 4 files")
    print("BNPB Hazards: 6 files")
    print()
    print("Use 'gdalinfo' or rasterio to view metadata:")
    print("  gdalinfo data/nightlights/tangsel_nightlights_2025.tif")
    print("  gdalinfo bnpb_risiko_indonesia/inarisk/inarisk_hazard_floods.tif")
    print("=" * 70)


if __name__ == '__main__':
    main()
