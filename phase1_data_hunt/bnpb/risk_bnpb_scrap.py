"""
BNPB Hazard Layer Downloader
Script untuk download hazard layers dari BNPB InaRISK Portal

Sumber: https://gis.bnpb.go.id/server/rest/services/inarisk/

Available Hazard Layers:
1. inarisk_hazard_floods - Banjir
2. inarisk_hazard_drought - Kekeringan
3. inarisk_hazard_landslide - Tanah Longsor
4. inarisk_hazard_earthquake - Gempa Bumi
5. inarisk_hazard_extreme_weather - Cuaca Ekstrem
6. inarisk_hazard_land_forest_fire - Kebakaran Hutan/Lahan

Note: API ini sering down. Saya sudah download sebelumnya.
"""

import requests
import os
import time

# Daftar layer yang akan didownload (hazard layers)
HAZARD_LAYERS = [
    "inarisk_hazard_floods",           # Banjir
    "inarisk_hazard_drought",          # Kekeringan
    "inarisk_hazard_landslide",        # Tanah Longsor
    "inarisk_hazard_earthquake",       # Gempa Bumi
    "inarisk_hazard_extreme_weather",  # Cuaca Ekstrem
    "inarisk_hazard_land_forest_fire", # Kebakaran Hutan/Lahan
]

# Bounding box Indonesia (WGS84)
# Format: "xmin,ymin,xmax,ymax"
BBOX_INDONESIA = "95,-11,141,6"

# Base URL BNPB InaRISK
BASE_URL = "https://gis.bnpb.go.id/server/rest/services/inarisk"


def download_layer(layer_name, output_dir, format="tiff", size="4096,2048"):
    """
    Download satu layer dari BNPB ImageServer

    Parameters:
    - layer_name: Nama layer (e.g., "inarisk_hazard_floods")
    - output_dir: Folder output
    - format: Format output (tiff, png, jpg)
    - size: Ukuran gambar "width,height"

    Returns:
    - True jika berhasil, False jika gagal
    """
    url = f"{BASE_URL}/{layer_name}/ImageServer/exportImage"

    params = {
        "bbox": BBOX_INDONESIA,
        "bboxSR": "4326",        # Input CRS (WGS84)
        "imageSR": "4326",       # Output CRS (WGS84)
        "size": size,            # Image dimensions
        "format": format,
        "pixelType": "UNKNOWN",
        "noData": "",
        "noDataInterpretation": "esriNoDataMatchAny",
        "interpolation": "RSP_NearestNeighbor",
        "compression": "LZ77",
        "f": "image"
    }

    ext = "tif" if format == "tiff" else format
    filename = f"{layer_name}.{ext}"
    filepath = os.path.join(output_dir, filename)

    # Skip jika file sudah ada
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"  ⊙ Already exists: {filename} ({file_size / 1024 / 1024:.2f} MB)")
        return True

    print(f"  Downloading: {layer_name}")
    print(f"  URL: {url}")

    try:
        response = requests.get(url, params=params, stream=True, timeout=180)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')

        if 'image' in content_type or 'tiff' in content_type or 'octet' in content_type:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(filepath)
            print(f"  ✓ Success: {filename} ({file_size / 1024 / 1024:.2f} MB)")
            return True
        else:
            print(f"  ✗ Error: Server returned non-image response")
            print(f"    Content-Type: {content_type}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error: {e}")
        return False


def generate_download_urls():
    """
    Generate URL untuk download manual di browser
    Berguna jika API down atau untuk download lewat browser
    """
    print("=" * 70)
    print("MANUAL DOWNLOAD URLs (Copy-paste to browser)")
    print("=" * 70)

    for layer in HAZARD_LAYERS:
        url = (f"{BASE_URL}/{layer}/ImageServer/exportImage?"
               f"bbox={BBOX_INDONESIA}&bboxSR=4326&imageSR=4326&"
               f"size=4096,2048&format=tiff&f=image")
        print(f"\n{layer}:")
        print(url)

    print("\n" + "=" * 70)


def check_existing_files(output_dir):
    """
    Check file apa saja yang sudah ada
    """
    if not os.path.exists(output_dir):
        return []

    existing = []
    for layer in HAZARD_LAYERS:
        filepath = os.path.join(output_dir, f"{layer}.tif")
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            existing.append((layer, size_mb))

    return existing


def main():
    print("=" * 70)
    print("BNPB InaRISK Hazard Layer Downloader")
    print("Download Hazard Layers - Seluruh Indonesia")
    print("=" * 70)
    print()

    # Buat folder output (relative to script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "inarisk")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output folder: {output_dir}")
    print(f"Layers to download: {len(HAZARD_LAYERS)}")
    print(f"Bounding Box: {BBOX_INDONESIA} (Indonesia)")
    print()

    # Check existing files
    existing = check_existing_files(output_dir)
    if existing:
        print("Existing files:")
        for layer, size_mb in existing:
            print(f"  ✓ {layer}.tif ({size_mb:.2f} MB)")
        print()

    # Generate URL untuk download manual
    generate_download_urls()
    print()

    # Download semua layer
    print("DOWNLOADING...")
    print("-" * 70)

    success = 0
    failed = 0
    skipped = 0

    for i, layer in enumerate(HAZARD_LAYERS, 1):
        print(f"\n[{i}/{len(HAZARD_LAYERS)}] {layer}")

        filepath = os.path.join(output_dir, f"{layer}.tif")
        if os.path.exists(filepath):
            skipped += 1
            file_size = os.path.getsize(filepath)
            print(f"  ⊙ Skipped (already exists): {file_size / 1024 / 1024:.2f} MB")
        elif download_layer(layer, output_dir):
            success += 1
        else:
            failed += 1

        # Delay antar request untuk menghindari rate limiting
        if i < len(HAZARD_LAYERS):
            time.sleep(2)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Output: {output_dir}/")
    print("=" * 70)
    print()
    print("Hazard Layers:")
    for layer in HAZARD_LAYERS:
        filepath = os.path.join(output_dir, f"{layer}.tif")
        status = "✓" if os.path.exists(filepath) else "✗"
        print(f"  {status} {layer}")
    print()


if __name__ == "__main__":
    main()
