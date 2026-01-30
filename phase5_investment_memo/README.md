# Phase 5: Investment Analysis & Memo

**Objective**: Analyze integrated grid data to compare regions and generate professional investment memo.

## Folder Structure

```
phase5_investment_memo/
├── business_gap_analysis/          POI/Business gap analysis
│   ├── business_gap_analysis.ipynb     Notebook for POI analysis
│   └── outputs/
│       └── business_gap_analysis.png   4-panel service gap chart
│
├── scripts/                        Visualization generators
│   ├── generate_grid_maps.py          Land use, population, night lights maps
│   └── generate_business_gap.py       Business gap analysis (standalone)
│
├── latex/                          Investment memo LaTeX source
│   ├── oku_investment_memo.tex        Main LaTeX source (2-column, 2-page)
│   ├── oku_investment_memo.pdf        ⭐ FINAL DELIVERABLE
│   ├── README.md                      LaTeX compilation guide
│   └── cache/                         Archived old memo versions
│
├── outputs/maps/                   Generated visualizations
│   ├── grid_land_use.png              Land use comparison
│   ├── grid_population_density.png    Population density maps
│   ├── grid_nightlights.png           Night lights (economic activity)
│   └── [5 other maps]
│
├── cache_unused/                   Archived unused files
│   ├── comprehensive_investment_analysis.ipynb  (old 37-cell notebook)
│   ├── phase5_investment_analysis.ipynb
│   ├── identify_hidden_gems.py
│   └── [7 unused PNG files]
│
└── README.md                       This file
```

## Analysis Components

### 1. Business Gap Analysis
**Location**: `business_gap_analysis/`

**Notebook**: `business_gap_analysis.ipynb` (focused POI analysis only)
**Script**: `scripts/generate_business_gap.py` (standalone generator)

Analyzes POI distribution to identify service gaps:
- Top 10 business categories in each region
- Service gap ratio (log scale) - e.g., 48x clinic gap, 106x cafe gap
- Investment needs (conservative estimate)
- 4-panel visualization chart

**Key Finding**: OKU has **15.3x fewer businesses per capita** than Tangsel

**Output**: `business_gap_analysis/outputs/business_gap_analysis.png`

### 2. Grid Visualization Maps
**Script**: `scripts/generate_grid_maps.py`

Generates 3 comparison maps used in final memo:
- `grid_land_use.png` - Land use classification (Page 1)
- `grid_population_density.png` - Population density (Page 1)
- `grid_nightlights.png` - Economic activity (Page 1)

**Note**: Also generates 3 additional maps (not used in final memo, archived to cache_unused):
- `grid_hazard_risk.png`
- `tangsel_overview.png` (4-panel overview)
- `oku_overview.png` (4-panel overview)

### 3. RTRW Validation Analysis
**Location**: `../../phase1_data_hunt/rtrw/rtrw_validation/comparison_pola_ruang.ipynb`

Validates official zoning (RTRW) against satellite reality:
- **Violations**: Protected→Built (33% in Tangsel - regulatory risk)
- **Opportunities**: Residential→Undeveloped (3.4% in OKU - land banking zones)
- Compliance rate calculation (66.4% Tangsel, 93.4% OKU)
- Discrepancy visualization map

**Output**: `../../output/maps/rtrw_compliance_oku_only.png` (used in memo Page 2)

### 4. Investment Memo Generation
**Location**: `latex/`

**Source**: `oku_investment_memo.tex` (2-column, 2-page format)
**Output**: `oku_investment_memo.pdf` ⭐ **FINAL DELIVERABLE**

Professional 2-page LaTeX document (12pt font minimum):

**Page 1: Regional Comparison**
- Land use comparison (left column)
- Population density + night lights (left column)
- Business gap analysis chart (right column)
- Key metrics table (right column)

**Page 2: Investment Decision**
- RTRW compliance map - OKU only (left column)
- Compliance explanation (left column)
- Investment thesis box (right column)
- 3-tier strategy: SHORT/MID/LONG term (right column)
- Top kecamatan rankings (right column)
- Action items (full width at bottom)

**Compilation**:
```bash
cd latex/
pdflatex oku_investment_memo.tex
```

See `latex/README.md` for detailed compilation guide.

## Outputs

### Active Files (Used in Final Memo)

**Visualizations** (`outputs/maps/`):
- `grid_land_use.png` - Land use comparison (used in memo Page 1)
- `grid_population_density.png` - Population density (used in memo Page 1)
- `grid_nightlights.png` - Night lights (used in memo Page 1)

**Business Analysis** (`business_gap_analysis/outputs/`):
- `business_gap_analysis.png` - 4-panel POI gap chart (used in memo Page 1)

**RTRW Validation** (`../../output/maps/`):
- `rtrw_compliance_oku_only.png` - OKU compliance map (used in memo Page 2)

**Final Deliverable** (`latex/`):
- `oku_investment_memo.pdf` ⭐ **MAIN DELIVERABLE** (2-page PDF)

### Archived Files (Not Used in Final Memo)

Moved to `cache_unused/`:
- `comprehensive_investment_analysis.ipynb` - Old 37-cell analysis notebook
- `phase5_investment_analysis.ipynb` - Old EDA notebook
- `identify_hidden_gems.py` - Hidden gems scoring script
- `grid_hazard_risk.png` - Hazard risk map
- `tangsel_overview.png` - 4-panel Tangsel overview
- `oku_overview.png` - 4-panel OKU overview
- `growth_distribution.png` - Growth distribution chart
- `growth_hotspot_maps.png` - Growth hotspot maps
- `kecamatan_radar_chart.png` - Kecamatan radar comparison
- `kecamatan_rankings_heatmap.png` - Kecamatan rankings heatmap
- `poi_density_maps.png` - POI density spatial maps
- `rtrw_zone_distribution.png` - RTRW zone pie charts
- `service_coverage.png` - Service coverage bar chart
- `hazard_comparison_detailed.png` - Detailed hazard comparison

**Note**: Files archived because final memo focuses on concise 2-page format. All analysis still accessible in archived files.

## Key Findings

### Tangerang Selatan
- **Profile**: Mature urban market
- **Strengths**: High economic activity, dense population, excellent infrastructure
- **Weaknesses**: Limited land (82% built), higher disaster risk (0.35)
- **RTRW**: 66.4% compliance - 33% violations (Protected→Built)
- **Investment**: Short-term ROI, retail expansion, high-value property

### Ogan Komering Ulu (THE HIDDEN GEM)
- **Profile**: Emerging agricultural market
- **Strengths**: MASSIVE land availability (98% undeveloped), agricultural powerhouse (68%), lower disaster risk (0.28)
- **Opportunities**: 22.6x larger than Tangsel, first-mover advantage
- **RTRW**: 93.4% compliance - 3.4% underdeveloped residential zones (land banking opportunity)
- **Investment**: Long-term growth, agribusiness, land banking, infrastructure partnerships

### Investment Thesis
**Portfolio Diversification Strategy**:
- 60% capital → Tangsel (short-term ROI, stable returns)
- 40% capital → OKU (long-term growth, exponential upside)

## Scripts Summary

**Active Scripts** (2 files):
1. `scripts/generate_grid_maps.py` - Generates 3 maps for memo (land use, population, night lights)
2. `scripts/generate_business_gap.py` - Generates business gap analysis chart

**Archived Scripts** (moved to `cache_unused/`):
- `generate_hazard_comparison.py` - Hazard comparison chart
- `generate_investment_memo.py` - Old matplotlib-based memo generator
- `generate_latex_pdf.py` - Old matplotlib-based PDF generator

## Data Sources

All data sourced from Phase 1-4:
- **Population**: Disdukcapil Tangsel & OKU (Phase 1)
- **Hazards**: BNPB InaRISK (Phase 1)
- **LULC**: ESA WorldCover satellite (Phase 2)
- **Night Lights**: VIIRS 2020-2025 (Phase 2)
- **Roads/POI**: OpenStreetMap (Phase 1)
- **Zoning**: RTRW official maps (Phase 1)
- **Integrated Grid**: Phase 4 outputs (grid_tangsel_integrated.parquet, grid_oku_integrated.parquet)

**Grid Resolution**: 50m × 50m (Geosquare Level 12)
**Total Grids Analyzed**: 1,559,032 (67,649 Tangsel + 1,491,383 OKU)

## How to Regenerate Deliverable

### Step 1: Generate Visualizations
```bash
# Generate grid comparison maps
python scripts/generate_grid_maps.py

# Generate business gap analysis
python scripts/generate_business_gap.py
```

### Step 2: Generate RTRW Compliance Map
```bash
# Run RTRW validation notebook (if not already done)
cd ../../phase1_data_hunt/rtrw/rtrw_validation/
jupyter notebook comparison_pola_ruang.ipynb
# Run the cell that generates "rtrw_compliance_oku_only.png"
```

### Step 3: Compile Investment Memo
```bash
cd latex/
pdflatex oku_investment_memo.tex
# Output: oku_investment_memo.pdf (2 pages)
```

**Result**: `latex/oku_investment_memo.pdf` ⭐ FINAL DELIVERABLE
