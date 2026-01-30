"""
Generate Grid Visualization Maps for Investment Memo
- Tangsel vs OKU side-by-side comparison
- Multiple thematic maps: Population, LULC, Night Lights, Hazards
- Output: PNG images for LaTeX inclusion
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("GENERATING GRID VISUALIZATION MAPS")
print("=" * 70)
print()

# Load integrated grids
print("Loading grid data...")
tangsel = gpd.read_parquet('output/grid_integration/grid_tangsel_integrated.parquet')
oku = gpd.read_parquet('output/grid_integration/grid_oku_integrated.parquet')

print(f"✓ Tangsel: {len(tangsel):,} grids")
print(f"✓ OKU: {len(oku):,} grids")
print()

# Create output directory
import os
os.makedirs('output/maps', exist_ok=True)

# LULC color mapping function
# CRITICAL FIX: The grid integration has WRONG class numbers!
# Actual mapping in data:
#   Built Area = 7 (should be 5)
#   Crops = 5 (should be 4)
#   Flooded Veg = 4 (should be 3)
#   Trees = 2 (should be 1)
#   Water = 1 (should be 0)
#   Bare = 8 (correct)
#   Rangeland = 11 (should be 10)
# Solution: Map by ACTUAL class numbers in the data!

LULC_COLORS_ACTUAL = {
    0: '#cccccc',  # No Data (actual)
    1: '#419bdf',  # Water (actual)
    2: '#397d49',  # Trees (actual, dark green)
    4: '#e49635',  # Flooded veg (actual, orange)
    5: '#dfc35a',  # Crops (actual, yellow)
    7: '#c4281b',  # Built - RED (actual!)
    8: '#a59b8f',  # Bare (actual, beige)
    11: '#e7e7e7', # Rangeland (actual, light gray)
    12: '#d67dff', # Oil Palm (actual, PURPLE - important for OKU!)
}

def get_lulc_colors(gdf):
    """Map LULC class to colors for each grid (using ACTUAL class numbers in data)"""
    return gdf['lulc_class'].map(LULC_COLORS_ACTUAL).fillna('#cccccc')

# ========== 1. POPULATION DENSITY MAP ==========
print("1. Generating Population Density Maps...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Use log scale for better visualization (Tangsel is 100x denser than OKU!)
import matplotlib.colors as colors

# Tangsel
tangsel_nonzero = tangsel[tangsel['pop_density_km2'] > 0]
tangsel.plot(column='pop_density_km2',
             ax=ax1,
             cmap='YlOrRd',
             legend=True,
             edgecolor='none',
             norm=colors.LogNorm(vmin=max(0.1, tangsel['pop_density_km2'].min()),
                                 vmax=tangsel['pop_density_km2'].max()),
             legend_kwds={'label': 'Pop Density (per km², log scale)', 'shrink': 0.8})
ax1.set_title('Tangerang Selatan\nPopulation Density (Log Scale)', fontsize=14, fontweight='bold')
ax1.axis('off')

# OKU
oku_nonzero = oku[oku['pop_density_km2'] > 0]
oku.plot(column='pop_density_km2',
         ax=ax2,
         cmap='YlOrRd',
         legend=True,
         edgecolor='none',
         norm=colors.LogNorm(vmin=max(0.1, oku['pop_density_km2'].min()),
                             vmax=oku['pop_density_km2'].max()),
         legend_kwds={'label': 'Pop Density (per km², log scale)', 'shrink': 0.8})
ax2.set_title('Ogan Komering Ulu\nPopulation Density (Log Scale)', fontsize=14, fontweight='bold')
ax2.axis('off')

plt.tight_layout()
plt.savefig('output/maps/grid_population_density.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: grid_population_density.png")
plt.close()

# ========== 2. LAND USE (LULC) MAP ==========
print("2. Generating Land Use Classification Maps...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Tangsel
tangsel.plot(ax=ax1, color=get_lulc_colors(tangsel), edgecolor='none')
ax1.set_title('Tangerang Selatan\nLand Use Classification', fontsize=14, fontweight='bold')
ax1.axis('off')

# OKU
oku.plot(ax=ax2, color=get_lulc_colors(oku), edgecolor='none')
ax2.set_title('Ogan Komering Ulu\nLand Use Classification', fontsize=14, fontweight='bold')
ax2.axis('off')

# Create legend (use ACTUAL class numbers from data!)
legend_labels = {
    7: 'Built Area',    # Actual class in data
    2: 'Trees',         # Actual class
    5: 'Crops',         # Actual class
    12: 'Oil Palm',     # Actual class (OKU only!)
    11: 'Rangeland',    # Actual class
    1: 'Water'          # Actual class
}
patches = [mpatches.Patch(color=LULC_COLORS_ACTUAL[k], label=v) for k, v in legend_labels.items()]
fig.legend(handles=patches, loc='lower center', ncol=6, frameon=False)

plt.tight_layout()
plt.savefig('output/maps/grid_land_use.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: grid_land_use.png")
plt.close()

# ========== 3. NIGHT LIGHTS (ECONOMIC ACTIVITY) ==========
print("3. Generating Night Lights Maps...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Tangsel
tangsel.plot(column='nightlight_2025',
             ax=ax1,
             cmap='inferno',
             legend=True,
             edgecolor='none',
             legend_kwds={'label': 'Radiance 2025', 'shrink': 0.8})
ax1.set_title('Tangerang Selatan\nNight Lights (Economic Activity)', fontsize=14, fontweight='bold')
ax1.axis('off')

# OKU
oku.plot(column='nightlight_2025',
         ax=ax2,
         cmap='inferno',
         legend=True,
         edgecolor='none',
         legend_kwds={'label': 'Radiance 2025', 'shrink': 0.8})
ax2.set_title('Ogan Komering Ulu\nNight Lights (Economic Activity)', fontsize=14, fontweight='bold')
ax2.axis('off')

plt.tight_layout()
plt.savefig('output/maps/grid_nightlights.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: grid_nightlights.png")
plt.close()

# ========== 4. HAZARD RISK MAP ==========
print("4. Generating Hazard Risk Maps...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# FIXED: Use full 0-1 scale for both regions to show true risk levels
# Green (0-0.3) = Low risk, Yellow (0.3-0.5) = Medium, Red (0.5-1.0) = High

# Tangsel
tangsel.plot(column='hazard_composite',
             ax=ax1,
             cmap='RdYlGn_r',  # Red = high risk, Green = low risk
             legend=True,
             edgecolor='none',
             vmin=0, vmax=1,  # FIXED SCALE 0-1
             legend_kwds={'label': 'Hazard Index (0=Safe, 1=Danger)', 'shrink': 0.8})
ax1.set_title('Tangerang Selatan\nDisaster Risk (BNPB)', fontsize=14, fontweight='bold')
ax1.axis('off')

# Add risk level annotations
ax1.text(0.02, 0.98, f'Avg: {tangsel["hazard_composite"].mean():.3f} (Low-Med)',
         transform=ax1.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# OKU
oku.plot(column='hazard_composite',
         ax=ax2,
         cmap='RdYlGn_r',
         legend=True,
         edgecolor='none',
         vmin=0, vmax=1,  # FIXED SCALE 0-1
         legend_kwds={'label': 'Hazard Index (0=Safe, 1=Danger)', 'shrink': 0.8})
ax2.set_title('Ogan Komering Ulu\nDisaster Risk (BNPB)', fontsize=14, fontweight='bold')
ax2.axis('off')

# Add risk level annotations
ax2.text(0.02, 0.98, f'Avg: {oku["hazard_composite"].mean():.3f} (Low)',
         transform=ax2.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.tight_layout()
plt.savefig('output/maps/grid_hazard_risk.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: grid_hazard_risk.png")
plt.close()

# ========== 5. COMPOSITE OVERVIEW (4-panel for each region) ==========
print("5. Generating Composite Overview Maps...")

# Tangsel 4-panel
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Tangerang Selatan - Grid Analysis Overview', fontsize=16, fontweight='bold')

# Population (log scale)
tangsel.plot(column='pop_density_km2', ax=axes[0,0], cmap='YlOrRd',
             edgecolor='none', legend=True,
             norm=colors.LogNorm(vmin=max(0.1, tangsel['pop_density_km2'].min()),
                                 vmax=tangsel['pop_density_km2'].max()),
             legend_kwds={'shrink': 0.6})
axes[0,0].set_title('Population Density (Log)')
axes[0,0].axis('off')

# LULC
tangsel.plot(ax=axes[0,1], color=get_lulc_colors(tangsel), edgecolor='none')
axes[0,1].set_title('Land Use')
axes[0,1].axis('off')

# Night Lights
tangsel.plot(column='nightlight_2025', ax=axes[1,0], cmap='inferno',
             edgecolor='none', legend=True, legend_kwds={'shrink': 0.6})
axes[1,0].set_title('Night Lights (Economic Activity)')
axes[1,0].axis('off')

# Hazards (fixed scale 0-1)
tangsel.plot(column='hazard_composite', ax=axes[1,1], cmap='RdYlGn_r',
             edgecolor='none', legend=True, vmin=0, vmax=1, legend_kwds={'shrink': 0.6})
axes[1,1].set_title('Disaster Risk (0=Safe, 1=Danger)')
axes[1,1].axis('off')

plt.tight_layout()
plt.savefig('output/maps/tangsel_overview.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: tangsel_overview.png")
plt.close()

# OKU 4-panel
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Ogan Komering Ulu - Grid Analysis Overview', fontsize=16, fontweight='bold')

# Population (log scale)
oku.plot(column='pop_density_km2', ax=axes[0,0], cmap='YlOrRd',
         edgecolor='none', legend=True,
         norm=colors.LogNorm(vmin=max(0.1, oku['pop_density_km2'].min()),
                             vmax=oku['pop_density_km2'].max()),
         legend_kwds={'shrink': 0.6})
axes[0,0].set_title('Population Density (Log)')
axes[0,0].axis('off')

# LULC
oku.plot(ax=axes[0,1], color=get_lulc_colors(oku), edgecolor='none')
axes[0,1].set_title('Land Use')
axes[0,1].axis('off')

# Night Lights
oku.plot(column='nightlight_2025', ax=axes[1,0], cmap='inferno',
         edgecolor='none', legend=True, legend_kwds={'shrink': 0.6})
axes[1,0].set_title('Night Lights (Economic Activity)')
axes[1,0].axis('off')

# Hazards (fixed scale 0-1)
oku.plot(column='hazard_composite', ax=axes[1,1], cmap='RdYlGn_r',
         edgecolor='none', legend=True, vmin=0, vmax=1, legend_kwds={'shrink': 0.6})
axes[1,1].set_title('Disaster Risk (0=Safe, 1=Danger)')
axes[1,1].axis('off')

plt.tight_layout()
plt.savefig('output/maps/oku_overview.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: oku_overview.png")
plt.close()

print()
print("=" * 70)
print("MAP GENERATION COMPLETE")
print("=" * 70)
print()
print("Generated Maps:")
print("  1. grid_population_density.png  - Population density comparison")
print("  2. grid_land_use.png            - Land use classification")
print("  3. grid_nightlights.png         - Economic activity (night lights)")
print("  4. grid_hazard_risk.png         - Disaster risk zones")
print("  5. tangsel_overview.png         - Tangsel 4-panel overview")
print("  6. oku_overview.png             - OKU 4-panel overview")
print()
print("All maps saved to: output/maps/")
print("Ready for LaTeX inclusion!")
print()
