# Phase 3: Dasymetric Population Mapping

**Objective**: Disaggregate desa-level population counts to 50m × 50m grid using dasymetric mapping with satellite-derived weights.

## Methodology

Dasymetric mapping uses ancillary data (satellite LULC) to intelligently distribute population counts from large administrative units (desa) to fine-resolution grids.

**Formula**:
```
Grid Population = Desa Population × (Grid Weight / Sum of Weights in Desa)

where Grid Weight is based on LULC class:
- Built Area: High weight (people live here)
- Crops/Rangeland: Low weight (some rural population)
- Trees/Water: Zero weight (uninhabited)
```

## Inputs

1. **Population Data** (from Phase 1):
   - Desa-level population counts from Disdukcapil

2. **Administrative Boundaries** (from Phase 1):
   - Desa polygons for spatial join

3. **LULC Data** (from Phase 2):
   - ESA WorldCover 10m for land use classification

4. **Grid System**:
   - 50m × 50m Geosquare Grid (Level 12)
   - Generated using `geosquare` Python library

## Scripts

- `dasymetric_mapping.py` - Main dasymetric population disaggregation script
- `validate_population.py` - Validate that grid totals = desa totals
- `visualize_pop_density.py` - Create population density maps

## Outputs

- `grid_tangsel_population.parquet` - Tangsel grids with estimated population
- `grid_oku_population.parquet` - OKU grids with estimated population
- Population density maps for validation

## Notes

- Dasymetric mapping preserves total population (mass-preserving)
- Grid population is ESTIMATED, not census-accurate at grid level
- Quality depends on LULC accuracy and weight calibration
- Better than uniform distribution (which ignores land use)
