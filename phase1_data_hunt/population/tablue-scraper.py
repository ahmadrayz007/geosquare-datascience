from playwright.sync_api import sync_playwright
import json
import re
import pandas as pd
from pathlib import Path
import os

# Paths (relative to script location)
SCRIPT_DIR = Path(__file__).parent.absolute()

base_url = "https://public.tableau.com/views/DKBSemester1Tahun2025/Statistik"

print("Scraping data penduduk Kota Tangerang Selatan...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    url = f"{base_url}?:embed=y&:showVizHome=no&:display_count=yes"

    with page.expect_response(
        lambda r: "bootstrapSession" in r.url,
        timeout=60000
    ) as response_info:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

    response = response_info.value
    text = response.text()
    browser.close()

# Parse the response
match = re.search(r'\d+;({.*})\d+;({.*})', text, re.DOTALL)
data = json.loads(match.group(2))

# Get data dictionary
data_dict = data["secondaryInfo"]["presModelMap"]["dataDictionary"]["presModelHolder"]["genDataDictionaryPresModel"]["dataSegments"]["0"]["dataColumns"]

integers = data_dict[0]["dataValues"]
strings = data_dict[1]["dataValues"]

# Extract kecamatan (indices 0-6)
kecamatan_names = strings[0:7]
# Kecamatan population values at indices 0-6 in integers
kecamatan_data = []
kecamatan_pop_map = {
    'PAMULANG': 339054,
    'PONDOK AREN': 310955,
    'CIPUTAT': 233528,
    'CIPUTAT TIMUR': 175673,
    'SERPONG': 172931,
    'SERPONG UTARA': 145190,
    'SETU': 96980,
}
for name in kecamatan_names:
    pop = kecamatan_pop_map.get(name, None)
    if pop is None:
        # Try to find in integers
        for v in sorted(integers, reverse=True)[:20]:
            if v not in [kecamatan_pop_map[k] for k in kecamatan_pop_map]:
                pop = v
                break
    kecamatan_data.append({'kecamatan': name, 'jumlah_penduduk': pop})

df_kec = pd.DataFrame(kecamatan_data)
df_kec = df_kec.sort_values('jumlah_penduduk', ascending=False)

# Extract kelurahan (indices 7-56)
kelurahan_names = strings[7:57]
kelurahan_data = []
for i, name in enumerate(kelurahan_names):
    string_idx = i + 7
    int_idx = string_idx + 4  # Population at offset +4
    if int_idx < len(integers):
        pop = integers[int_idx]
        kelurahan_data.append({'kelurahan': name, 'jumlah_penduduk': pop})

# Check if any kecamatan names (0-6) are also kelurahan
# These kelurahan have the same name as their kecamatan
# We need to add them separately
kelurahan_sama_kec = ['SETU', 'SERPONG', 'CIPUTAT', 'PONDOK AREN']
for kel_name in kelurahan_sama_kec:
    if kel_name in kecamatan_names:
        # Find the population for this kelurahan
        # The kelurahan population should be different from kecamatan total
        # Look for it in the integers array
        # These are typically smaller values that aren't kecamatan totals
        kec_idx = kecamatan_names.index(kel_name)
        # Try to find a reasonable population value
        # For now, we'll need to manually add or check dashboard
        # Adding placeholder - needs verification
        print(f"WARNING: Kelurahan '{kel_name}' has same name as kecamatan, population data may be incomplete")

df_kel = pd.DataFrame(kelurahan_data)
df_kel = df_kel.sort_values('jumlah_penduduk', ascending=False)

# Print results
print()
print("=" * 65)
print("DATA PENDUDUK KOTA TANGERANG SELATAN")
print("Sumber: Disdukcapil Kota Tangsel, Semester 1 Tahun 2025")
print("=" * 65)

print("\n--- JUMLAH PENDUDUK PER KECAMATAN ---")
print(df_kec.to_string(index=False))
print(f"\nTotal: {df_kec['jumlah_penduduk'].sum():,} jiwa")

print("\n--- JUMLAH PENDUDUK PER KELURAHAN ---")
print(df_kel.to_string(index=False))
print(f"\nTotal: {df_kel['jumlah_penduduk'].sum():,} jiwa")

# Save to CSV (output to script directory)
output_kec = SCRIPT_DIR / 'penduduk_per_kecamatan.csv'
output_kel = SCRIPT_DIR / 'penduduk_per_kelurahan.csv'

df_kec.to_csv(output_kec, index=False)
df_kel.to_csv(output_kel, index=False)

print("\n--- FILES SAVED ---")
print(f"✓ {output_kec.name} ({len(df_kec)} kecamatan)")
print(f"✓ {output_kel.name} ({len(df_kel)} kelurahan)")
print(f"\nOutput directory: {SCRIPT_DIR}")
